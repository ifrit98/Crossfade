"""Run: one execution attempt and its typed result. execute() and replay().

Invariants: CF-08/09 (uncertainty and forward-check are typed states, never defaulted to a pass),
CF-10 (every run resolves to inputs, op version, code rev, env lock), CF-11 (failures persisted,
retries linked), CF-12 (outputs published before the run that references them), CF-13 (origin).
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import traceback
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from crossfade.packs import Operation, RunContext, assess
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


def execute(
    store: Store,
    task: TaskSpec,
    op: Operation,
    record: Record,
    params: dict[str, Any],
    seed: int | None = None,
    attempt_of: str | None = None,
) -> Run:
    """Assess, then run in-process, then publish. A failed op is a persisted failed run."""
    a = assess(op, task, record, params)
    if a.status != "supported":
        raise NotSupported(f"{op.op_id} on {record.id}: {a.status}: {a.reasons} {a.missing}")
    parsed = op.params_model.model_validate(params)
    run_id = "run_" + uuid.uuid4().hex
    scratch = store.root / "tmp" / run_id
    scratch.mkdir(parents=True, exist_ok=True)
    ctx = RunContext(store, seed, scratch, run_id)
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
    try:
        result: Result = op.run(task, record, parsed, ctx)
        result = result.model_copy(update={"outputs": ctx.outputs})
        run = Run(**base, status="succeeded", finished_at=datetime.now(UTC), result=result)
    except Exception as e:  # noqa: BLE001 - any op failure is a failed run, persisted
        run = Run(
            **base,
            status="failed",
            finished_at=datetime.now(UTC),
            error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}",
        )
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
