"""W0 increment 1: immutable, hashed, unit-validated records. PRD-W0 AT-07, AT-08, AT-09, AT-25,
AT-26."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from conftest import profile_dataset, profile_manifest
from pydantic import ValidationError

from crossfade import records as records_mod
from crossfade.packs import assess, registry
from crossfade.records import IntegrityError, Record
from crossfade.tasks import load

ROOT = Path(__file__).resolve().parents[1]
T0 = load(ROOT / "tasks" / "profile.weighted_rms_width.v0.1.yaml")
T0_OP = registry(ROOT / "crossfade.toml")["profile.weighted_rms_width"]


def test_w0_at08_same_bytes_different_units_are_different_records(store, golden_ms):
    a = store.put(golden_ms, profile_manifest())
    b = store.put(profile_dataset([0.0, 2.0], [1.0, 1.0], "s"), profile_manifest())
    assert a.byte_hash != b.byte_hash or a.manifest_hash != b.manifest_hash
    assert a.id != b.id
    assert a.units == {"weight": "1"} and a.coords["delay"].units == "ms"
    assert b.coords["delay"].units == "s"


def test_put_is_deterministic_for_identical_input(store, golden_ms):
    a = store.put(golden_ms, profile_manifest())
    b = store.put(golden_ms, profile_manifest())
    assert a.id == b.id and a.byte_hash == b.byte_hash


def test_w0_at07_missing_units_quarantines_record(store):
    ds = profile_dataset([0.0, 2.0], [1.0, 1.0], "ms")
    del ds["weight"].attrs["units"]
    rec = store.put(ds, profile_manifest())
    assert rec.validation_state == "quarantined"
    assert any("weight" in n for n in rec.validation_notes)


def test_unparseable_units_quarantines_record(store):
    ds = profile_dataset([0.0, 2.0], [1.0, 1.0], "furlongs_per_bogon")
    rec = store.put(ds, profile_manifest())
    assert rec.validation_state == "quarantined"


def test_w0_at09_tampered_blob_is_detected(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    blob_dir = store.root / rec.payload_ref
    target = next(p for p in sorted(blob_dir.rglob("*")) if p.is_file() and p.stat().st_size > 0)
    target.write_bytes(b"\x00" * target.stat().st_size)
    from crossfade.records import IntegrityError

    with pytest.raises(IntegrityError):
        store.get(rec.id)


def test_get_round_trips_payload_and_manifest(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    again = store.get(rec.id)
    assert again == rec
    ds = store.load_payload(again)
    np.testing.assert_allclose(ds["weight"].values, [1.0, 1.0])
    assert ds["delay"].attrs["units"] == "ms"


def test_structured_payload_round_trips(store):
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
    assert rec.payload_kind == "structured" and rec.validation_state == "eligible"
    assert store.load_payload(rec) == payload
    assert rec.byte_hash == store.get(rec.id).byte_hash


def test_metadata_correction_creates_successor_not_edit(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    fixed = store.put(golden_ms, profile_manifest(source_system="fixture-v2", parents=[rec.id]))
    assert fixed.parents == [rec.id] and fixed.id != rec.id
    assert store.get(rec.id).source_system == "fixture"
    assert not hasattr(store, "update")


def test_record_json_rejects_unknown_fields(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    path = store.root / "records" / f"{rec.id}.json"
    data = json.loads(path.read_text())
    data["surprise"] = 1
    from pydantic import ValidationError

    from crossfade.records import Record

    with pytest.raises(ValidationError):
        Record.model_validate(data)


def test_verify_reports_orphan_blob(store, golden_ms):
    rec = store.put(golden_ms, profile_manifest())
    (store.root / "records" / f"{rec.id}.json").unlink()
    report = store.verify()
    assert rec.payload_ref in report["orphans"]


def _coord(units: str, **over) -> dict:
    return {"units": units, "dtype": "float64", "length": 2} | over


@pytest.mark.parametrize(
    "given, name",
    [
        ({"coords": {"delay": _coord("s")}}, "delay"),
        ({"units": {"weight": "m"}}, "weight"),
        ({"coords": {"delay": _coord("millisecond")}}, "delay"),  # units compare as strings
    ],
)
def test_w0_at25_manifest_unit_conflicting_with_payload_quarantines(store, golden_ms, given, name):
    rec = store.put(golden_ms, profile_manifest(**given))
    assert rec.validation_state == "quarantined"
    assert f"units_conflict:{name}" in rec.validation_notes
    a = assess(T0_OP, T0, rec, {})
    assert a.status == "unsupported" and f"quarantined:units_conflict:{name}" in a.reasons


@pytest.mark.parametrize(
    "given, name",
    [
        ({"units": {"weight": "furlongs_per_bogon"}}, "weight"),
        ({"units": {"extra": "furlongs_per_bogon"}}, "extra"),
        ({"coords": {"extra": _coord("furlongs_per_bogon")}}, "extra"),
    ],
)
def test_w0_at25_unparseable_manifest_unit_quarantines(store, golden_ms, given, name):
    rec = store.put(golden_ms, profile_manifest(**given))
    assert rec.validation_state == "quarantined"
    assert f"unparseable_units:{name}:furlongs_per_bogon" in rec.validation_notes


def test_w0_at25_manifest_repeating_payload_units_is_the_same_record(store, golden_ms):
    bare = store.put(golden_ms, profile_manifest())
    same = profile_manifest(units={"weight": "1"}, coords={"delay": _coord("ms")})
    assert store.put(golden_ms, same).id == bare.id and bare.validation_state == "eligible"
    # A manifest coordinate gives only its units; dtype, length and attrs describe the payload.
    other = profile_manifest(coords={"delay": _coord("ms", dtype="int8", length=9)})
    assert store.put(golden_ms, other).id == bare.id


def test_manifest_unit_does_not_cure_missing_payload_units(store):
    ds = profile_dataset([0.0, 2.0], [1.0, 1.0], "ms")
    del ds["weight"].attrs["units"]
    rec = store.put(ds, profile_manifest(units={"weight": "1"}))
    assert rec.validation_state == "quarantined" and "missing_units:weight" in rec.validation_notes


def test_manifest_coord_must_be_a_full_coord_spec(store, golden_ms):
    with pytest.raises(ValidationError):
        store.put(golden_ms, profile_manifest(coords={"delay": {"units": "ms"}}))


@pytest.mark.parametrize("rehash", ["none", "manifest_hash", "id"])
def test_w0_at26_edited_record_json_fails_integrity(store, golden_ms, rehash):
    rec = store.put(golden_ms, profile_manifest())
    assert store.put(golden_ms, profile_manifest()).id == rec.id
    assert len(list((store.root / "records").glob("*.json"))) == 1
    path = store.root / "records" / f"{rec.id}.json"
    data = json.loads(path.read_text())
    data["coords"]["delay"]["units"] = "s"
    if rehash != "none":  # an editor who also recomputes the hashes is caught by the next check
        data["manifest_hash"] = records_mod._manifest_hash(Record.model_validate(data))
    if rehash == "id":
        data["id"] = records_mod._record_id(data["byte_hash"], data["manifest_hash"])
    path.write_text(json.dumps(data))
    with pytest.raises(IntegrityError):
        store.get(rec.id)
    assert store.verify()["mismatches"] == [rec.id]
