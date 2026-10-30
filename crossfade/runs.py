"""Run: one execution attempt and its typed result. execute() and replay().

Invariants: CF-08/09 (uncertainty and forward-check are typed states, never defaulted to a pass),
CF-10 (every run resolves to inputs, op version, code rev, env lock), CF-11 (failures persisted,
retries linked), CF-12 (outputs published before the run that references them), CF-13 (origin).

The operation runs in a child process under optional limits. Installed packs are a trust boundary,
not a sandbox: the child limits time and memory, not what the pack may touch.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import signal
import subprocess
import sys
import traceback
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from crossfade.packs import Operation, RegistryError, RunContext, assess
from crossfade.records import Record, Store
from crossfade.tasks import TaskSpec


class NotSupported(RuntimeError):
    """execute() refused to start because assess was not `supported`."""


class ReplayMismatch(RuntimeError):
    pass


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Quantity(_Strict):
    value: float
    units: str
    origin: Literal["upstream_asserted", "computed", "inferred"]


class ForwardCheck(_Strict):
    status: Literal["passed", "failed", "unavailable", "not_applicable"]
    residual: float | None = None
    threshold: float | None = None
    in_sample: bool | None = None


class Uncertainty(_Strict):
    kind: Literal[
        "posterior",
        "confidence_interval",
        "predictive_interval",
        "ensemble_summary",
        "unavailable",
        "not_applicable",
    ]
    estimand: str | None = None
    method: str | None = None
    version: str | None = None
    validated_on: list[dict[str, Any]] = []
    conditional_on_plugin: str | None = None
    payload_ref: str | None = None


class Result(_Strict):
    quantities: dict[str, Quantity] = {}
    outputs: list[str] = []
    answer: Literal["complete", "partial", "abstained", "unsupported"]
    applicability: Literal["in_scope", "out_of_scope", "unknown"] = "unknown"
    forward_check: ForwardCheck = ForwardCheck(status="unavailable")
    uncertainty: Uncertainty = Uncertainty(kind="unavailable")
    alternatives: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}


class Run(_Strict):
    schema_version: int = 1
    run_id: str
    task_id: str
    task_version: str
    op_id: str
    op_version: str
    inputs: list[str]
    params: dict[str, Any]
    assumptions_used: list[str] = []
    code_rev: str
    env_lock_hash: str
    seed: int | None = None
    path: Literal["reference", "learned", "output_only", "diagnostic"]
    started_at: datetime
    finished_at: datetime | None = None
    status: Literal["succeeded", "failed", "cancelled"]
    attempt_of: str | None = None
    error: str | None = None
    result: Result | None = None


class WorkerLimits(_Strict):
    """Limits on the worker process; None means no limit. The values are open (PRD-W0)."""

    wall_seconds: float | None = Field(default=None, gt=0)  # the child's whole life, imports too
    memory_bytes: int | None = Field(default=None, gt=0)  # address space, as RLIMIT_AS


def _code_rev() -> str:
    try:
        rev = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        ).stdout.strip()
        return f"dirty:{rev}" if dirty else rev
    except Exception:
        return "unknown"


def _env_lock_hash() -> str:
    try:
        frozen = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True
        ).stdout
    except Exception:
        frozen = sys.version
    return hashlib.sha256(frozen.encode()).hexdigest()


def _path_for(op: Operation, record: Record, task: TaskSpec) -> str:
    if record.kind == "summary":
        return "output_only"
    return "learned" if op.is_model else "reference"


def _persist_run(store: Store, run: Run) -> None:
    """Write the run JSON via temp file and atomic rename, then the index row. Outputs were
    already published by the run context, so a crash before this leaves orphan outputs, never a
    run referencing missing outputs (CF-12)."""
    path = store.root / "runs" / f"{run.run_id}.json"
    tmp = store.root / "tmp" / f"{run.run_id}.json"
    tmp.write_text(run.model_dump_json(indent=1))
    os.replace(tmp, path)
    store.db.execute(
        "INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?)",
        (run.run_id, run.task_id, run.op_id, run.status, str(path)),
    )
    store.db.commit()


def _pack_of(op: Operation) -> str:
    """The imported pack module whose OPERATIONS holds this op, for the worker to import."""
    for name, mod in list(sys.modules.items()):
        ops = getattr(mod, "__dict__", {}).get("OPERATIONS")
        if isinstance(ops, list | tuple) and any(o is op for o in ops):
            return name
    raise RegistryError(f"{op.op_id}: not listed in any imported pack's OPERATIONS")


# The child takes the parent's sys.path first, so it imports the same code as the parent.
_BOOT = (
    "import json, sys; job = json.load(sys.stdin); sys.path[:] = job['sys_path']; "
    "from crossfade.runs import _worker; _worker(job)"
)


def _limit_memory(nbytes: int) -> None:
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (nbytes, resource.getrlimit(resource.RLIMIT_AS)[1]))
    except (ImportError, ValueError, OSError) as e:  # never run unlimited instead
        raise RuntimeError(f"memory limit memory_bytes={nbytes} could not be set: {e}") from e


def _worker(job: dict[str, Any]) -> None:
    """Child process: apply the memory limit, import the op from its pack as registry() does,
    run it, and write {"result": ...} or {"error": ...} to result.json in the scratch dir."""
    scratch, mem = Path(job["scratch"]), job["memory_bytes"]
    try:
        if mem is not None:
            _limit_memory(mem)
        op = next(
            o for o in importlib.import_module(job["pack"]).OPERATIONS if o.op_id == job["op_id"]
        )
        ctx = RunContext(Store(Path(job["store"])), job["seed"], scratch, job["run_id"])
        task, record = TaskSpec.model_validate(job["task"]), Record.model_validate(job["record"])
        result = op.run(task, record, op.params_model.model_validate(job["params"]), ctx)
        result = Result.model_validate(result.model_dump() | {"outputs": ctx.outputs})
        out = {"result": result.model_dump(mode="json")}
    except Exception as e:  # noqa: BLE001 - any op failure is a failed run, persisted
        limited = isinstance(e, MemoryError) and mem is not None
        note = f"under memory limit memory_bytes={mem}: " if limited else ""
        out = {"error": f"{note}{type(e).__name__}: {e}\n{traceback.format_exc()}"}
    tmp = scratch / "result.json.tmp"
    tmp.write_text(json.dumps(out))
    os.replace(tmp, scratch / "result.json")


def _work(job: dict[str, Any], wall_seconds: float | None) -> tuple[Result | None, str | None]:
    """Run the worker in a child process. Returns (result, None) or (None, why it failed)."""
    proc = subprocess.Popen([sys.executable, "-c", _BOOT], stdin=subprocess.PIPE)
    try:
        proc.communicate(json.dumps(job).encode(), timeout=wall_seconds)
    except subprocess.TimeoutExpired:
        return None, f"wall-clock limit wall_seconds={wall_seconds} exceeded; worker killed"
    finally:
        if proc.poll() is None:  # timed out, or the parent was interrupted
            proc.kill()
            proc.wait()
    reply = Path(job["scratch"]) / "result.json"
    if not reply.exists():
        rc = proc.returncode
        how = f"exit code {rc}"
        if rc < 0:
            how = "signal " + next((s.name for s in signal.Signals if s == -rc), str(-rc))
        return None, f"worker exited without a result: {how}"
    out = json.loads(reply.read_text())
    if "error" in out:
        return None, out["error"]
    return Result.model_validate(out["result"]), None


def execute(
    store: Store,
    task: TaskSpec,
    op: Operation,
    record: Record,
    params: dict[str, Any],
    seed: int | None = None,
    attempt_of: str | None = None,
    limits: WorkerLimits | None = None,
) -> Run:
    """Assess, then run the op in a child process under `limits`, then publish. Every worker
    failure (an exception, the wall-clock limit, the child's death) is a persisted failed run."""
    a = assess(op, task, record, params)
    if a.status != "supported":
        raise NotSupported(f"{op.op_id} on {record.id}: {a.status}: {a.reasons} {a.missing}")
    limits = limits or WorkerLimits()
    pack = _pack_of(op)
    run_id = "run_" + uuid.uuid4().hex
    scratch = store.root / "tmp" / run_id
    scratch.mkdir(parents=True, exist_ok=True)
    base = dict(
        run_id=run_id,
        task_id=task.task_id,
        task_version=task.version,
        op_id=op.op_id,
        op_version=op.version,
        inputs=[record.id],
        params=params,
        seed=seed,
        code_rev=_code_rev(),
        env_lock_hash=_env_lock_hash(),
        path=_path_for(op, record, task),
        started_at=datetime.now(UTC),
        attempt_of=attempt_of,
        assumptions_used=[k for k, v in task.params.items() if v.is_assumption and k in params],
    )
    job = {
        "sys_path": sys.path,
        "store": str(store.root),
        "pack": pack,
        "op_id": op.op_id,
        "task": task.model_dump(mode="json"),
        "record": record.model_dump(mode="json"),
        "params": params,
        "seed": seed,
        "run_id": run_id,
        "scratch": str(scratch),
        "memory_bytes": limits.memory_bytes,
    }
    result, error = _work(job, limits.wall_seconds)
    if error is None:
        run = Run(**base, status="succeeded", finished_at=datetime.now(UTC), result=result)
    else:
        run = Run(**base, status="failed", finished_at=datetime.now(UTC), error=error)
    _persist_run(store, run)
    return run


def load_run(store: Store, run_id: str) -> Run:
    return Run.model_validate_json((store.root / "runs" / f"{run_id}.json").read_text())


def replay(store: Store, run_id: str, reg: dict[str, Operation]) -> Run:
    """Re-execute with the same inputs, params and seed; compare outputs by the op's contract."""
    prior = load_run(store, run_id)
    op = reg[prior.op_id]
    if op.version != prior.op_version:
        raise ReplayMismatch(f"{prior.op_id}: version {op.version} != recorded {prior.op_version}")
    from crossfade.tasks import load as load_task  # local import keeps runs.py free of paths

    task = load_task(_task_path(prior.task_id, prior.task_version))
    record = store.get(prior.inputs[0])
    new = execute(store, task, op, record, prior.params, seed=prior.seed, attempt_of=run_id)
    if prior.status == "succeeded" and new.status == "succeeded":
        old_h = [store.get(o).byte_hash for o in prior.result.outputs]
        new_h = [store.get(o).byte_hash for o in new.result.outputs]
        if op.determinism == "exact" and old_h != new_h:
            raise ReplayMismatch(f"{run_id}: outputs differ under exact determinism")
    return new


def _task_path(task_id: str, version: str) -> str:
    from pathlib import Path

    here = Path(__file__).resolve().parents[1] / "tasks"
    return str(here / f"{task_id}.v{version}.yaml")
