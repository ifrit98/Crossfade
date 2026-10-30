"""summary.import: return upstream assertions as upstream_asserted quantities."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from crossfade.packs import Assessment
from crossfade.runs import ForwardCheck, Quantity, Result, Uncertainty


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ImportSummary:
    op_id = "summary.import"
    version = "0.1"
    preconditions = ["upstream_asserted"]
    params_model = Params
    transform_class = "none"
    determinism = "exact"
    tolerance = None
    is_model = False

    def assess(self, task, record, params) -> Assessment:
        if record.kind != "summary" or record.payload_kind != "structured":
            return Assessment(status="unsupported", reasons=["kind:not a structured summary"])
        return Assessment(status="supported")

    def run(self, task, record, params, ctx) -> Result:
        payload = ctx.store.load_payload(record)
        q, conf = {}, {}
        for a in payload.get("assertions", []):
            q[a["name"]] = Quantity(
                value=float(a["value"]), units=str(a.get("units", "1")), origin="upstream_asserted"
            )
            if "confidence" in a:
                conf[a["name"]] = a["confidence"]
        return Result(
            quantities=q,
            answer="complete" if q else "partial",
            uncertainty=Uncertainty(kind="not_applicable"),
            forward_check=ForwardCheck(status="not_applicable"),
            diagnostics={"upstream_confidence": conf},
        )
