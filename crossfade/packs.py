"""Operation protocol, assessment, and the explicit pack registry.

Invariants: CF-04 (labels never authorize; explicit capabilities do), CF-05 (unknown is never
coerced to supported). ADR-09: packs are an explicit import-path list; one integer API version.
"""

from __future__ import annotations

import importlib
import tomllib
from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, ValidationError

from crossfade.records import Record, Store
from crossfade.tasks import TaskSpec

CORE_API_VERSION = 1


class RegistryError(RuntimeError):
    pass


class Assessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["supported", "unsupported", "unknown"]
    reasons: list[str] = []
    missing: list[str] = []


class RunContext:
    """What an operation's run() receives: the store, a seed, and a scratch directory."""

    def __init__(self, store: Store, seed: int | None, scratch: Path, run_id: str):
        self.store, self.seed, self.scratch, self.run_id = store, seed, scratch, run_id
        self.outputs: list[str] = []

    def put(self, payload: Any, manifest: dict[str, Any]) -> Record:
        rec = self.store.put(payload, {**manifest, "produced_by_run": self.run_id})
        self.outputs.append(rec.id)
        return rec


@runtime_checkable
class Operation(Protocol):
    op_id: str
    version: str
    preconditions: list[str]
    params_model: type[BaseModel]
    transform_class: Literal["exact", "coordinate", "lossy", "physical", "none"]
    determinism: Literal["exact", "tolerance"]
    tolerance: float | None
    is_model: bool

    def assess(self, task: TaskSpec, record: Record, params: BaseModel) -> Assessment: ...
    def run(self, task: TaskSpec, record: Record, params: BaseModel, ctx: RunContext) -> Any: ...


def assess(op: Operation, task: TaskSpec, record: Record, params: dict[str, Any]) -> Assessment:
    """Structural preflight: params, quarantine, explicit capabilities, then the op's own check.

    Never opens the payload. A capability label (C0..C3) is ignored here on purpose (CF-04).
    """
    try:
        parsed = op.params_model.model_validate(params)
    except ValidationError as e:
        names = sorted({str(err["loc"][0]) for err in e.errors() if err.get("loc")})
        return Assessment(
            status="unsupported",
            reasons=[
                f"params:{'.'.join(map(str, err.get('loc', ())))}:{err['msg']}"
                for err in e.errors()
            ],
            missing=names,
        )
    if record.validation_state != "eligible":
        return Assessment(
            status="unsupported",
            reasons=[f"quarantined:{n}" for n in record.validation_notes]
            or ["quarantined:unknown"],
        )
    missing = [
        c for c in [*task.required_capabilities, *op.preconditions] if c not in record.capabilities
    ]
    if missing:
        return Assessment(
            status="unsupported",
            reasons=[f"missing_capability:{c}" for c in missing],
            missing=missing,
        )
    return op.assess(task, record, parsed)


def registry(config_path: Path | str) -> dict[str, Operation]:
    """Import every listed pack, check its API version, collect its operations. Fails whole."""
    cfg = tomllib.loads(Path(config_path).read_text())
    ops: dict[str, Operation] = {}
    for modname in cfg.get("packs", {}).get("list", []):
        try:
            mod = importlib.import_module(modname)
        except Exception as e:  # any import failure fails the whole registry
            raise RegistryError(f"{modname}: import failed: {e}") from e
        if getattr(mod, "CORE_API_VERSION", None) != CORE_API_VERSION:
            raise RegistryError(
                f"{modname}: CORE_API_VERSION {getattr(mod, 'CORE_API_VERSION', None)!r} "
                f"!= core {CORE_API_VERSION}"
            )
        for op in getattr(mod, "OPERATIONS", []):
            if not isinstance(op, Operation):
                raise RegistryError(f"{modname}: {op!r} does not satisfy Operation")
            if op.op_id in ops:
                raise RegistryError(f"{modname}: duplicate op_id {op.op_id}")
            ops[op.op_id] = op
    return ops
