"""Record: anything observed or derived. Store: content-hashed files plus a SQLite index.

Invariants enforced here: CF-01 (write-once blobs), CF-02 (identity covers bytes and manifest,
rechecked on read), CF-03 (validated units or quarantine), CF-25 (unknown fields rejected).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pint
import xarray as xr
from pydantic import BaseModel, ConfigDict

UREG = pint.UnitRegistry()


class IntegrityError(RuntimeError):
    """A stored payload or record no longer matches its recorded hashes or id."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CoordSpec(_Strict):
    units: str
    dtype: str
    length: int
    attrs: dict[str, str] = {}


class ProcessingStep(_Strict):
    op_id: str
    op_version: str
    params: dict[str, Any] = {}
    transform_class: Literal["exact", "coordinate", "lossy", "physical"]


class RegimeCoord(_Strict):
    value: float | None
    units: str = "1"
    provenance: Literal["metadata", "estimated", "oracle"]
    availability: Literal["inference", "supervision", "evaluation_only"]
    uncertainty: float | None = None


class Descriptor(_Strict):
    value: float
    units: str
    definition: str
    canonical_kind: str


class AnchorFields(_Strict):
    anchor_kind: Literal[
        "impulse_response", "delay_doppler", "delay_scale", "power_statistic", "descriptors_only"
    ]
    descriptors: dict[str, Descriptor] = {}
    statistical_semantics: Literal[
        "realization", "expectation", "estimate", "posterior_samples", "pseudo_label"
    ]
    normalization: dict[str, str | float] = {}
    assumptions: list[str] = []
    identifiable: list[str] = []
    ambiguous: list[str] = []
    uncertainty_ref: str | None = None


class Record(_Strict):
    schema_version: int = 1
    id: str
    kind: Literal["observation", "representation", "anchor_estimate", "summary"]
    payload_kind: Literal["array", "structured"]
    payload_ref: str
    byte_hash: str
    manifest_hash: str

    source_system: str
    acquired_at: datetime | None = None
    ingested_at: datetime
    data_use: str | None = None

    capability_label: Literal["C0", "C1", "C2", "C3"]
    capabilities: list[str] = []

    coords: dict[str, CoordSpec] = {}
    units: dict[str, str] = {}
    masks: list[str] = []
    group_ids: dict[str, str] = {}

    processing_history: list[ProcessingStep] = []
    parents: list[str] = []
    produced_by_run: str | None = None
    validation_state: Literal["eligible", "quarantined"]
    validation_notes: list[str] = []

    regime: dict[str, RegimeCoord] | None = None
    anchor: AnchorFields | None = None


_IDENTITY_EXCLUDED = {
    "id",
    "byte_hash",
    "manifest_hash",
    "ingested_at",
    "payload_ref",
    "produced_by_run",
}


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_tree(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(q for q in root.rglob("*") if q.is_file()):
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def _manifest_hash(rec: Record) -> str:
    """sha256 of the record's stored JSON less the fields identity excludes, so it can be
    recomputed from the record alone."""
    return _sha256(_canonical(json.loads(rec.model_dump_json(exclude=_IDENTITY_EXCLUDED))))


def _record_id(byte_hash: str, manifest_hash: str) -> str:
    return "rec_" + _sha256((byte_hash + manifest_hash).encode())[:16]


def _validate_units(ds: xr.Dataset, manifest: dict[str, Any]) -> tuple[dict, dict, list[str]]:
    """Return (units, coords, notes) as the record keeps them. Any note but nonfinite:<var> means
    quarantine.

    The kept units are the payload's `units` attributes, overlaid name by name by those the
    manifest supplies in `units` or `coords`. Every kept unit must parse, a manifest unit must
    equal the payload's attribute where both exist, and a payload variable without the attribute
    is missing its units whatever the manifest says (CF-03). For a payload coordinate the
    manifest gives only the units; dtype, length and attrs describe the payload.
    """
    masks = list(manifest.get("masks", []))
    given_units = dict(manifest.get("units", {}))
    given_coords = {k: CoordSpec.model_validate(v) for k, v in manifest.get("coords", {}).items()}
    notes: list[str] = []
    units: dict[str, str] = {}
    coords: dict[str, CoordSpec] = {}

    def parse(name: str, u: str) -> None:
        try:
            UREG.parse_units(u)
        except Exception:  # pint raises several types
            notes.append(f"unparseable_units:{name}:{u}")

    def keep(name: str, attrs: dict, given: str | None) -> str | None:
        u = attrs.get("units")
        if u is None:
            notes.append(f"missing_units:{name}")
        else:
            parse(name, u)
        if given is not None and given != u:
            if u is not None:
                notes.append(f"units_conflict:{name}")
            parse(name, given)
        return given if given is not None else u

    for name, var in ds.data_vars.items():
        if name in masks:
            continue
        u = keep(str(name), var.attrs, given_units.pop(str(name), None))
        if u is not None:
            units[str(name)] = u
        if np.issubdtype(var.dtype, np.number) and not np.all(np.isfinite(var.values)):
            notes.append(f"nonfinite:{name}")
    for name, c in ds.coords.items():
        given = given_coords.pop(str(name), None)
        u = keep(str(name), c.attrs, given.units if given else None)
        coords[str(name)] = CoordSpec(
            units=u or "?",
            dtype=str(c.dtype),
            length=int(c.size),
            attrs={k: str(v) for k, v in c.attrs.items() if k != "units"},
        )
    for name, u in given_units.items():  # masks, and names the payload has no variable for
        parse(name, u)
        units[name] = u
    for name, spec in given_coords.items():
        parse(name, spec.units)
        coords[name] = spec
    return units, coords, notes


class Store:
    """Write-once blobs under blobs/<hash>, record JSON under records/, SQLite index."""

    def __init__(self, root: Path):
        self.root = Path(root)
        for d in ("blobs", "records", "runs", "reports", "tmp"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        from crossfade.db import connect

        self.db = connect(self.root / "index.sqlite")

    # ---- payloads -------------------------------------------------------

    def _put_blob(self, payload: Any) -> tuple[str, str, str]:
        """Write payload write-once. Returns (payload_kind, byte_hash, payload_ref)."""
        tmp = self.root / "tmp" / f"put-{os.getpid()}-{datetime.now(UTC).timestamp()}"
        if isinstance(payload, xr.Dataset):
            payload.to_zarr(tmp, mode="w", consolidated=False)
            digest = _hash_tree(tmp)
            final = self.root / "blobs" / digest
            if final.exists():
                shutil.rmtree(tmp)
            else:
                os.replace(tmp, final)
            return "array", digest, f"blobs/{digest}"
        data = _canonical(payload)
        digest = _sha256(data)
        final = self.root / "blobs" / f"{digest}.json"
        if not final.exists():
            tmp.write_bytes(data)
            os.replace(tmp, final)
        return "structured", digest, f"blobs/{digest}.json"

    def _blob_hash(self, payload_ref: str) -> str:
        p = self.root / payload_ref
        return _hash_tree(p) if p.is_dir() else _sha256(p.read_bytes())

    def load_payload(self, rec: Record) -> Any:
        p = self.root / rec.payload_ref
        if rec.payload_kind == "array":
            return xr.open_zarr(p, consolidated=False).load()
        return json.loads(p.read_text())

    # ---- records --------------------------------------------------------

    def put(self, payload: Any, manifest: dict[str, Any]) -> Record:
        manifest = dict(manifest)
        notes: list[str] = []
        if isinstance(payload, xr.Dataset):
            units, coords, notes = _validate_units(payload, manifest)
            manifest["units"] = units
            manifest["coords"] = {k: v.model_dump() for k, v in coords.items()}
        payload_kind, byte_hash, payload_ref = self._put_blob(payload)
        fatal = [n for n in notes if not n.startswith("nonfinite:")]
        manifest["validation_state"] = "quarantined" if fatal else "eligible"
        manifest["validation_notes"] = notes
        manifest["payload_kind"] = payload_kind
        body = {
            k: v
            for k, v in manifest.items()
            if k not in {"id", "byte_hash", "manifest_hash", "ingested_at", "payload_ref"}
        }
        rec = Record(
            id="",
            byte_hash=byte_hash,
            manifest_hash="",
            payload_ref=payload_ref,
            ingested_at=datetime.now(UTC),
            **body,
        )
        manifest_hash = _manifest_hash(rec)
        rec = rec.model_copy(
            update={"manifest_hash": manifest_hash, "id": _record_id(byte_hash, manifest_hash)}
        )
        path = self.root / "records" / f"{rec.id}.json"
        if not path.exists():
            tmp = self.root / "tmp" / f"{rec.id}.json"
            tmp.write_text(rec.model_dump_json(indent=1))
            os.replace(tmp, path)
            self.db.execute(
                "INSERT OR IGNORE INTO records VALUES (?,?,?,?,?,?)",
                (rec.id, rec.kind, byte_hash, manifest_hash, rec.validation_state, str(path)),
            )
            self.db.commit()
        return Record.model_validate_json(path.read_text())

    def _integrity(self, rec: Record, record_id: str) -> str | None:
        """Why the record stored as `record_id` fails its hashes or id, or None (CF-01, CF-02)."""
        if self._blob_hash(rec.payload_ref) != rec.byte_hash:
            return "payload hash mismatch"
        if _manifest_hash(rec) != rec.manifest_hash:
            return "manifest hash mismatch"
        if not rec.id == record_id == _record_id(rec.byte_hash, rec.manifest_hash):
            return "id mismatch"
        return None

    def get(self, record_id: str) -> Record:
        rec = Record.model_validate_json((self.root / "records" / f"{record_id}.json").read_text())
        if why := self._integrity(rec, record_id):
            raise IntegrityError(f"{record_id}: {why}")
        return rec

    def verify(self) -> dict[str, list[str]]:
        """Recompute every hash and id. Report mismatches, orphan blobs (no record references
        them), and orphan outputs (run outputs no published run references, as when the run was
        never published or failed after publishing them: CF-12)."""
        referenced: set[str] = set()
        mismatches: list[str] = []
        orphan_outputs: list[str] = []
        run_outputs: set[str] = set()
        for p in (self.root / "runs").glob("*.json"):
            run_outputs.update((json.loads(p.read_text()).get("result") or {}).get("outputs", []))
        for p in (self.root / "records").glob("*.json"):
            rec = Record.model_validate_json(p.read_text())
            referenced.add(rec.payload_ref)
            if self._integrity(rec, p.stem):
                mismatches.append(p.stem)
            if rec.produced_by_run and rec.id not in run_outputs:
                orphan_outputs.append(rec.id)
        orphans = [
            f"blobs/{p.name}"
            for p in (self.root / "blobs").iterdir()
            if f"blobs/{p.name}" not in referenced
        ]
        return {"mismatches": mismatches, "orphans": orphans, "orphan_outputs": orphan_outputs}


def ureg() -> pint.UnitRegistry:
    return UREG
