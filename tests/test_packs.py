"""W0 increment 3: Operation protocol, registry, assess. PRD-W0 AT-04 (structural part), AT-05,
AT-14, AT-15, AT-17, AT-18, AT-21."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import profile_dataset, profile_manifest
from pydantic import BaseModel

from crossfade.packs import Assessment, Operation, RegistryError, assess, registry
from crossfade.tasks import load

ROOT = Path(__file__).resolve().parents[1]
T0 = load(ROOT / "tasks" / "profile.weighted_rms_width.v0.1.yaml")


class _NeedsPhase:
    """Test-only operation with preconditions, to exercise the machinery."""

    op_id = "test.needs_phase"
    version = "0.1"
    preconditions = ["has_phase", "has_source_reference"]
    transform_class = "none"
    determinism = "exact"
    tolerance = None
    is_model = False

    class params_model(BaseModel):
        pass

    def assess(self, task, record, params):
        return Assessment(status="supported", reasons=[], missing=[])

    def run(self, task, record, params, ctx):  # pragma: no cover
        raise NotImplementedError


def test_registry_loads_fixture_packs():
    reg = registry(ROOT / "crossfade.toml")
    assert "profile.weighted_rms_width" in reg
    assert "summary.import" in reg
    assert all(isinstance(op, Operation) for op in reg.values())


def test_w0_at17_core_api_version_mismatch_fails_whole(tmp_path, monkeypatch):
    pkg = tmp_path / "badpack"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("CORE_API_VERSION = 2\nOPERATIONS = []\n")
    cfg = tmp_path / "crossfade.toml"
    cfg.write_text('[packs]\nlist = ["packs.profile_fixture", "badpack"]\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(RegistryError, match="badpack"):
        registry(cfg)


def test_w0_at05_negative_reference_time_is_unsupported(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    op = registry(ROOT / "crossfade.toml")["profile.weighted_rms_width"]
    a = assess(op, T0, rec, {"reference_time": -2.0, "reference_time_units": "ms"})
    assert a.status == "unsupported" and any("reference_time" in r for r in a.reasons)


def test_w0_at18_unknown_param_is_unsupported(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    op = registry(ROOT / "crossfade.toml")["profile.weighted_rms_width"]
    a = assess(op, T0, rec, {"bogus": 1})
    assert a.status == "unsupported" and "bogus" in a.missing + a.reasons


def test_quarantined_record_is_unsupported(store):
    ds = profile_dataset([0.0, 2.0], [1.0, 1.0], "ms")
    del ds["weight"].attrs["units"]
    rec = store.put(ds, profile_manifest())
    op = registry(ROOT / "crossfade.toml")["profile.weighted_rms_width"]
    a = assess(op, T0, rec, {})
    assert a.status == "unsupported" and any(r.startswith("quarantined:") for r in a.reasons)


def test_wrong_profile_convention_is_unsupported(store, golden_ms):
    m = profile_manifest()
    m["processing_history"][0]["params"]["profile_convention"] = "bin_integrated"
    rec = store.put(golden_ms, m)
    op = registry(ROOT / "crossfade.toml")["profile.weighted_rms_width"]
    a = assess(op, T0, rec, {})
    assert a.status == "unsupported" and any("convention" in r for r in a.reasons)


def test_w0_at14_summary_record_lacks_phase(store):
    rec = store.put(
        {"assertions": []},
        {
            "kind": "summary",
            "source_system": "legacy",
            "capability_label": "C0",
            "capabilities": ["upstream_asserted"],
        },
    )
    a = assess(_NeedsPhase(), T0, rec, {})
    assert a.status == "unsupported" and "has_phase" in a.missing


def test_w0_at15_c3_label_does_not_authorize(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest(capability_label="C3", capabilities=["has_phase"]))
    a = assess(_NeedsPhase(), T0, rec, {})
    assert a.status == "unsupported" and a.missing == ["has_source_reference"]


@pytest.mark.parametrize("op_id", sorted(registry(ROOT / "crossfade.toml")))
def test_w0_at21_conformance_every_precondition_refused_when_absent(store, golden_ms, op_id):
    op = registry(ROOT / "crossfade.toml")[op_id]
    for cap in op.preconditions:
        others = [c for c in op.preconditions if c != cap]
        rec = store.put(golden_ms, profile_manifest(capabilities=others))
        a = assess(op, T0, rec, {})
        assert a.status == "unsupported" and cap in a.missing
