"""W0 increments 4-6: execute, replay, T0 and summary runs.
PRD-W0 AT-01, 02, 03, 04, 05, 06, 10, 11, 12, 13, 19.

AT-04 and AT-05 value checks happen at run time (answer=unsupported), because assess never
opens the payload (contract 01 section 3). Parameter checks (negative reference) are at assess.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from conftest import profile_dataset, profile_manifest

from crossfade import runs as runs_mod
from crossfade.packs import registry
from crossfade.records import ureg
from crossfade.runs import Run, execute, replay
from crossfade.tasks import load

ROOT = Path(__file__).resolve().parents[1]
REG = registry(ROOT / "crossfade.toml")
T0 = load(ROOT / "tasks" / "profile.weighted_rms_width.v0.1.yaml")
SUMMARY = load(ROOT / "tasks" / "summary.compare.v0.1.yaml")
GOLDEN = json.loads((ROOT / "fixtures" / "t0_golden.json").read_text())
T0_OP = REG["profile.weighted_rms_width"]
REF = {"reference_time": 2.0, "reference_time_units": "ms"}


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


def test_w0_at10_worker_failure_is_persisted_without_result(store, golden_ms, monkeypatch):
    rec = store.put(golden_ms, profile_manifest())

    def boom(self, task, record, params, ctx):
        raise RuntimeError("worker exploded")

    monkeypatch.setattr(type(T0_OP), "run", boom)
    run = execute(store, T0, T0_OP, rec, REF)
    assert run.status == "failed" and run.result is None and "exploded" in run.error
    assert (store.root / "runs" / f"{run.run_id}.json").exists()
    retry = execute(store, T0, T0_OP, rec, REF, attempt_of=run.run_id)
    assert retry.attempt_of == run.run_id and retry.run_id != run.run_id


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
