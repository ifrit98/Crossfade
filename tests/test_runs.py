"""W0 increments 4-6: execute, replay, T0 and summary runs, the subprocess worker.
PRD-W0 AT-01, 02, 03, 04, 05, 06, 10, 11, 12, 13, 19, 22, 23, 24.

AT-04 and AT-05 value checks happen at run time (answer=unsupported), because assess never
opens the payload (contract 01 section 3). Parameter checks (negative reference) are at assess.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest
from conftest import profile_dataset, profile_manifest
from pydantic import BaseModel, ValidationError

from crossfade import runs as runs_mod
from crossfade.packs import Assessment, RegistryError, registry
from crossfade.records import ureg
from crossfade.runs import Run, WorkerLimits, execute, replay
from crossfade.tasks import load

ROOT = Path(__file__).resolve().parents[1]
REG = registry(ROOT / "crossfade.toml")
T0 = load(ROOT / "tasks" / "profile.weighted_rms_width.v0.1.yaml")
SUMMARY = load(ROOT / "tasks" / "summary.compare.v0.1.yaml")
GOLDEN = json.loads((ROOT / "fixtures" / "t0_golden.json").read_text())
T0_OP = REG["profile.weighted_rms_width"]
REF = {"reference_time": 2.0, "reference_time_units": "ms"}
MEM = 2**31  # a test value only; the limit values are open (PRD-W0)

# A pack whose operations misbehave in the worker. The worker imports it by name, so it lives in
# a directory on sys.path rather than in this module.
MISBEHAVING_PACK = """
import atexit, os, signal, time
from pydantic import BaseModel, ConfigDict
from crossfade.packs import Assessment
from crossfade.runs import Result

class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nbytes: int = 0

def raises(params, ctx):
    raise RuntimeError("worker exploded")

def hangs(params, ctx):
    time.sleep(3600)

def publishes_then_dies(params, ctx):
    manifest = {"kind": "summary", "source_system": "test", "capability_label": "C0"}
    ctx.put({"run": ctx.run_id}, manifest)
    os.kill(os.getpid(), signal.SIGKILL)

def exits(params, ctx):
    os._exit(3)

def allocates(params, ctx):
    bytes(params.nbytes)

def dies_after_replying(params, ctx):
    atexit.register(os.kill, os.getpid(), signal.SIGKILL)  # runs after the reply is written
    return Result(answer="partial")

class Op:
    version = "0.1"
    preconditions = []
    params_model = Params
    transform_class = "none"
    determinism = "exact"
    tolerance = None
    is_model = False

    def __init__(self, fn):
        self.op_id, self.fn = f"test.{fn.__name__}", fn

    def assess(self, task, record, params):
        return Assessment(status="supported")

    def run(self, task, record, params, ctx):
        return self.fn(params, ctx)

CORE_API_VERSION = 1
OPERATIONS = [
    Op(f) for f in (raises, hangs, publishes_then_dies, exits, allocates, dies_after_replying)
]
"""


@pytest.fixture(scope="module")
def bad(tmp_path_factory):
    root = tmp_path_factory.mktemp("packs")
    (root / "misbehaving_pack").mkdir()
    (root / "misbehaving_pack" / "__init__.py").write_text(MISBEHAVING_PACK)
    (root / "crossfade.toml").write_text('[packs]\nlist = ["misbehaving_pack"]\n')
    with pytest.MonkeyPatch.context() as mp:
        mp.syspath_prepend(str(root))
        yield registry(root / "crossfade.toml")


def _rlimit_as_probe(nbytes: int) -> str:
    """Whether a child process can cap its address space at nbytes, and is refused past it."""
    code = (
        "import resource, sys; n = int(sys.argv[1]); "
        "resource.setrlimit(resource.RLIMIT_AS, (n, resource.getrlimit(resource.RLIMIT_AS)[1])); "
        "print('set', flush=True); bytes(4 * n)"
    )
    p = subprocess.run([sys.executable, "-c", code, str(nbytes)], capture_output=True, text=True)
    if "set" not in p.stdout:
        return "unsettable"
    return "enforced" if "MemoryError" in p.stderr else "not enforced"


RLIMIT_AS = _rlimit_as_probe(MEM)


def _q(run: Run, name: str) -> float:
    return run.result.quantities[name].value


def test_w0_at01_golden_profile(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    run = execute(store, T0, T0_OP, rec, REF)
    assert run.status == "succeeded" and run.result.answer == "complete"
    for k, v in GOLDEN["expected"].items():
        assert _q(run, k) == pytest.approx(v, rel=GOLDEN["tolerance_rel"])
    assert run.result.quantities["mean_delay"].units == "ms"
    assert run.result.quantities["mean_delay"].origin == "computed"
    assert run.result.uncertainty.kind == "not_applicable"
    assert run.result.forward_check.status == "not_applicable"
    assert run.path == "reference"


def test_w0_at02_seconds_and_milliseconds_agree(store, golden_ms, golden_s):
    a = execute(store, T0, T0_OP, store.put(golden_ms, profile_manifest()), REF)
    b = execute(
        store,
        T0,
        T0_OP,
        store.put(golden_s, profile_manifest()),
        {"reference_time": 0.002, "reference_time_units": "s"},
    )
    u = ureg()
    b_ms = (_q(b, "mean_delay") * u(b.result.quantities["mean_delay"].units)).to("ms").magnitude
    assert b_ms == pytest.approx(_q(a, "mean_delay"))
    assert _q(a, "normalized_width") == pytest.approx(_q(b, "normalized_width"))
    assert store.get(a.inputs[0]).coords["delay"].units == "ms"
    assert store.get(b.inputs[0]).coords["delay"].units == "s"


def test_w0_at03_masked_invalid_entry_is_excluded_and_counted(store):
    ds = profile_dataset([0.0, 2.0, 5.0], [1.0, 1.0, np.nan], "ms", valid=[True, True, False])
    run = execute(store, T0, T0_OP, store.put(ds, profile_manifest()), REF)
    assert run.result.answer == "complete"
    assert _q(run, "n_used") == 2 and _q(run, "n_excluded") == 1
    assert _q(run, "rms_width") == pytest.approx(1.0)


def test_w0_at04_unmasked_invalid_entry_is_refused(store):
    ds = profile_dataset([0.0, 2.0, 5.0], [1.0, 1.0, np.nan], "ms")
    run = execute(store, T0, T0_OP, store.put(ds, profile_manifest()), REF)
    assert run.status == "succeeded" and run.result.answer == "unsupported"
    assert any("nonfinite" in r and "2" in r for r in run.result.diagnostics["reasons"])


def test_w0_at05_zero_total_weight_and_negative_weight_refused(store):
    zero_rec = store.put(profile_dataset([0.0, 2.0], [0.0, 0.0], "ms"), profile_manifest())
    neg_rec = store.put(profile_dataset([0.0, 2.0], [1.0, -1.0], "ms"), profile_manifest())
    zero = execute(store, T0, T0_OP, zero_rec, REF)
    neg = execute(store, T0, T0_OP, neg_rec, REF)
    assert zero.result.answer == "unsupported"
    assert any("zero_total_weight" in r for r in zero.result.diagnostics["reasons"])
    assert neg.result.answer == "unsupported"
    assert any("negative_weight" in r for r in neg.result.diagnostics["reasons"])


def test_w0_at06_missing_reference_time_gives_partial(store, golden_ms):
    run = execute(store, T0, T0_OP, store.put(golden_ms, profile_manifest()), {})
    assert run.result.answer == "partial"
    assert "normalized_width" not in run.result.quantities
    assert _q(run, "rms_width") == pytest.approx(1.0)


def test_execute_refuses_when_assess_is_not_supported(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    with pytest.raises(runs_mod.NotSupported, match="reference_time"):
        execute(store, T0, T0_OP, rec, {"reference_time": -1.0, "reference_time_units": "ms"})


def test_w0_at10_worker_failure_is_persisted_without_result(store, golden_ms, bad):
    rec = store.put(golden_ms, profile_manifest())
    op = bad["test.raises"]
    run = execute(store, T0, op, rec, {})
    assert run.status == "failed" and run.result is None and "exploded" in run.error
    assert "Traceback" in run.error
    assert (store.root / "runs" / f"{run.run_id}.json").exists()
    retry = execute(store, T0, op, rec, {}, attempt_of=run.run_id)
    assert retry.attempt_of == run.run_id and retry.run_id != run.run_id


def test_w0_at22_wall_clock_limit_kills_hung_worker(store, golden_ms, bad, monkeypatch):
    workers, popen = [], subprocess.Popen

    def spy(args, *a, **k):  # keeps the worker's handle; other subprocesses pass through
        proc = popen(args, *a, **k)
        if args[-1:] == [runs_mod._BOOT]:
            workers.append(proc)
        return proc

    monkeypatch.setattr(subprocess, "Popen", spy)
    rec = store.put(golden_ms, profile_manifest())
    t0 = time.monotonic()
    run = execute(store, T0, bad["test.hangs"], rec, {}, limits=WorkerLimits(wall_seconds=1))
    assert time.monotonic() - t0 < 10
    assert run.status == "failed" and run.result is None
    assert "wall-clock limit" in run.error and "wall_seconds=1.0" in run.error
    [worker] = workers
    assert worker.returncode is not None  # reaped, so the pid is free
    with pytest.raises(ProcessLookupError):
        os.kill(worker.pid, 0)


def test_w0_at23_worker_killed_by_signal_leaves_orphan_output(store, golden_ms, bad):
    rec = store.put(golden_ms, profile_manifest())
    run = execute(store, T0, bad["test.publishes_then_dies"], rec, {})
    assert run.status == "failed" and run.result is None
    assert "SIGKILL" in run.error
    orphans = store.verify()["orphan_outputs"]
    assert len(orphans) == 1 and store.get(orphans[0]).produced_by_run == run.run_id


def test_worker_exit_without_result_names_exit_code(store, golden_ms, bad):
    rec = store.put(golden_ms, profile_manifest())
    run = execute(store, T0, bad["test.exits"], rec, {})
    assert run.status == "failed" and run.result is None and "exit code 3" in run.error


def test_worker_death_after_its_reply_fails_the_run(store, golden_ms, bad):
    rec = store.put(golden_ms, profile_manifest())
    run = execute(store, T0, bad["test.dies_after_replying"], rec, {})
    assert run.status == "failed" and run.result is None
    assert "after writing its result" in run.error and "SIGKILL" in run.error


def test_op_within_wall_clock_limit_succeeds(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    run = execute(store, T0, T0_OP, rec, REF, limits=WorkerLimits(wall_seconds=60))
    assert run.status == "succeeded" and _q(run, "rms_width") == pytest.approx(1.0)


@pytest.mark.skipif(RLIMIT_AS == "unsettable", reason=f"RLIMIT_AS at {MEM} bytes is {RLIMIT_AS}")
def test_op_within_memory_limit_succeeds(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    limits = WorkerLimits(memory_bytes=8 * MEM)  # roomy: this checks a limit doesn't fail the run
    run = execute(store, T0, T0_OP, rec, REF, limits=limits)
    assert run.status == "succeeded" and _q(run, "rms_width") == pytest.approx(1.0)


@pytest.mark.skipif(RLIMIT_AS != "enforced", reason=f"RLIMIT_AS at {MEM} bytes is {RLIMIT_AS}")
def test_w0_at24_memory_limit_fails_runaway_worker(store, golden_ms, bad):
    rec = store.put(golden_ms, profile_manifest())
    limits = WorkerLimits(memory_bytes=MEM)
    run = execute(store, T0, bad["test.allocates"], rec, {"nbytes": 4 * MEM}, limits=limits)
    assert run.status == "failed" and run.result is None
    assert f"memory_bytes={MEM}" in run.error or "signal" in run.error


def test_memory_error_under_a_memory_limit_names_the_limit(store, golden_ms, bad, monkeypatch):
    """AT-24's MemoryError path, run in-process so it is covered where RLIMIT_AS can't be set."""
    monkeypatch.setattr(runs_mod, "_limit_memory", lambda nbytes: None)
    rec = store.put(golden_ms, profile_manifest())
    scratch = store.root / "tmp" / "run_inprocess"
    scratch.mkdir()
    job = {
        "store": str(store.root),
        "pack": "misbehaving_pack",
        "op_id": "test.allocates",
        "task": T0.model_dump(mode="json"),
        "record": rec.model_dump(mode="json"),
        "params": {"nbytes": 2**62},  # no allocator grants this, limit or not
        "seed": None,
        "run_id": "run_inprocess",
        "scratch": str(scratch),
        "memory_bytes": MEM,
    }
    runs_mod._worker(job)
    error = json.loads((scratch / "result.json").read_text())["error"]
    assert error.startswith(f"under memory limit memory_bytes={MEM}: MemoryError")


@pytest.mark.skipif(RLIMIT_AS != "unsettable", reason=f"RLIMIT_AS at {MEM} bytes is {RLIMIT_AS}")
def test_memory_limit_that_cannot_be_set_fails_the_run(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    run = execute(store, T0, T0_OP, rec, REF, limits=WorkerLimits(memory_bytes=MEM))
    assert run.status == "failed" and run.result is None
    assert f"memory limit memory_bytes={MEM} could not be set" in run.error


def test_limits_must_be_positive():
    with pytest.raises(ValidationError):
        WorkerLimits(wall_seconds=0)
    with pytest.raises(ValidationError):
        WorkerLimits(memory_bytes=-1)


def test_execute_refuses_op_not_listed_by_a_pack(store, golden_ms):
    class Unlisted:
        op_id = "test.unlisted"
        version = "0.1"
        preconditions: list[str] = []
        transform_class = "none"
        determinism = "exact"
        tolerance = None
        is_model = False

        class params_model(BaseModel):
            pass

        def assess(self, task, record, params):
            return Assessment(status="supported")

        def run(self, task, record, params, ctx):  # pragma: no cover
            raise NotImplementedError

    rec = store.put(golden_ms, profile_manifest())
    with pytest.raises(RegistryError, match="test.unlisted"):
        execute(store, T0, Unlisted(), rec, {})
    assert not list((store.root / "runs").glob("*.json"))


def test_w0_at11_interrupted_publication_leaves_orphan_not_run(store, golden_ms, monkeypatch):
    rec = store.put(golden_ms, profile_manifest())

    def die(*a, **k):
        raise KeyboardInterrupt

    monkeypatch.setattr(runs_mod, "_persist_run", die)
    with pytest.raises(KeyboardInterrupt):
        execute(store, T0, T0_OP, rec, REF)
    assert not list((store.root / "runs").glob("*.json"))
    assert store.db.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 0
    assert store.verify()["orphan_outputs"]


def test_w0_at12_replay_reproduces_outputs(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    first = execute(store, T0, T0_OP, rec, REF)
    again = replay(store, first.run_id, REG)
    assert again.attempt_of == first.run_id and again.run_id != first.run_id
    assert [store.get(o).byte_hash for o in again.result.outputs] == [
        store.get(o).byte_hash for o in first.result.outputs
    ]
    assert again.result.quantities == first.result.quantities


def test_w0_at19_output_is_descriptors_only_anchor(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    run = execute(store, T0, T0_OP, rec, REF)
    out = store.get(run.result.outputs[0])
    assert out.kind == "anchor_estimate" and out.anchor.anchor_kind == "descriptors_only"
    assert out.payload_kind == "structured" and out.parents == [rec.id]
    assert out.produced_by_run == run.run_id
    assert set(out.anchor.descriptors) >= {"mean_delay", "rms_width"}


def test_w0_at13_summary_import_keeps_upstream_semantics(store):
    payload = {"assertions": [{"name": "range", "value": 12.5, "units": "km", "confidence": 0.7}]}
    rec = store.put(
        payload,
        {
            "kind": "summary",
            "source_system": "legacy",
            "capability_label": "C0",
            "capabilities": ["upstream_asserted"],
        },
    )
    run = execute(store, SUMMARY, REG["summary.import"], rec, {})
    assert run.path == "output_only"
    q = run.result.quantities["range"]
    assert q.origin == "upstream_asserted" and q.value == 12.5 and q.units == "km"
    assert run.result.uncertainty.kind == "not_applicable"
    assert run.result.diagnostics["upstream_confidence"] == {"range": 0.7}


def test_run_json_rejects_unknown_fields(store, golden_ms):
    run = execute(store, T0, T0_OP, store.put(golden_ms, profile_manifest()), REF)
    data = json.loads((store.root / "runs" / f"{run.run_id}.json").read_text())
    data["surprise"] = 1
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Run.model_validate(data)
