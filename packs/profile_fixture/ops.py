"""T0: weighted mean delay, RMS width, normalized width on a point-weight profile."""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from crossfade.packs import Assessment, RunContext
from crossfade.records import Record, ureg
from crossfade.runs import ForwardCheck, Quantity, Result, Uncertainty
from crossfade.tasks import TaskSpec


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reference_time: float | None = Field(default=None, gt=0)
    reference_time_units: str | None = None


class WeightedRmsWidth:
    op_id = "profile.weighted_rms_width"
    version = "0.1"
    preconditions: list[str] = []
    params_model = Params
    transform_class = "exact"
    determinism = "exact"
    tolerance = None
    is_model = False

    def assess(self, task: TaskSpec, record: Record, params: Params) -> Assessment:
        reasons: list[str] = []
        if "delay" not in record.coords:
            reasons.append("missing_coord:delay")
        if "weight" not in record.units:
            reasons.append("missing_var:weight")
        conv = next(
            (
                s.params.get("profile_convention")
                for s in record.processing_history
                if "profile_convention" in s.params
            ),
            None,
        )
        if conv != "point_weights":
            reasons.append(f"profile_convention:{conv!r} is not point_weights")
        if params.reference_time is not None and not params.reference_time_units:
            reasons.append("params:reference_time given without reference_time_units")
        if reasons:
            return Assessment(status="unsupported", reasons=reasons)
        return Assessment(status="supported")

    def run(self, task: TaskSpec, record: Record, params: Params, ctx: RunContext) -> Result:
        ds = ctx.store.load_payload(record)
        delay = ds["delay"].values.astype(float)
        weight = ds["weight"].values.astype(float)
        valid = ds["valid"].values.astype(bool) if "valid" in ds else np.ones_like(weight, bool)
        d_units = record.coords["delay"].units
        na = Uncertainty(kind="not_applicable")
        fc = ForwardCheck(status="not_applicable")

        reasons: list[str] = []
        bad = np.where(valid & ~np.isfinite(weight))[0]
        if bad.size:
            reasons += [f"nonfinite:weight[{i}]" for i in bad]
        if np.any(valid & (weight < 0)):
            reasons.append("negative_weight")
        if not reasons and weight[valid].sum() <= 0:
            reasons.append("zero_total_weight")
        if reasons:
            return Result(
                answer="unsupported",
                uncertainty=na,
                forward_check=fc,
                diagnostics={"reasons": reasons},
            )

        w = weight[valid] / weight[valid].sum()
        d = delay[valid]
        mean = float(np.sum(w * d))
        rms = float(np.sqrt(np.sum(w * (d - mean) ** 2)))
        q = {
            "mean_delay": Quantity(value=mean, units=d_units, origin="computed"),
            "rms_width": Quantity(value=rms, units=d_units, origin="computed"),
            "n_used": Quantity(value=float(valid.sum()), units="1", origin="computed"),
            "n_excluded": Quantity(value=float((~valid).sum()), units="1", origin="computed"),
        }
        answer = "partial"
        if params.reference_time is not None:
            u = ureg()
            ref = (params.reference_time * u(params.reference_time_units)).to(d_units).magnitude
            q["normalized_width"] = Quantity(value=rms / ref, units="1", origin="computed")
            answer = "complete"

        descriptors = {
            k: {
                "value": v.value,
                "units": v.units,
                "definition": task.quantities[k].definition,
                "canonical_kind": task.quantities[k].canonical_kind,
            }
            for k, v in q.items()
            if task.quantities[k].canonical_kind != "not_channel"
        }
        ctx.put(
            {"descriptors": {k: v["value"] for k, v in descriptors.items()}},
            {
                "kind": "anchor_estimate",
                "source_system": record.source_system,
                "capability_label": record.capability_label,
                "capabilities": [],
                "parents": [record.id],
                "processing_history": [
                    {
                        "op_id": self.op_id,
                        "op_version": self.version,
                        "params": params.model_dump(),
                        "transform_class": "exact",
                    }
                ],
                "anchor": {
                    "anchor_kind": "descriptors_only",
                    "descriptors": descriptors,
                    "statistical_semantics": "estimate",
                    "assumptions": ["profile_convention=point_weights"],
                    "identifiable": list(descriptors),
                    "ambiguous": [],
                },
            },
        )
        return Result(
            quantities=q, answer=answer, applicability="in_scope", uncertainty=na, forward_check=fc
        )
