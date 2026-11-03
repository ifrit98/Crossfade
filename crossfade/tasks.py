"""TaskSpec: what a run may see and must return. Loaded from YAML; unknown fields rejected.

Invariants: CF-06 (deploy handle excludes oracle classes), CF-23 (every quantity names a
canonical kind or not_channel), CF-25 (unknown fields rejected).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, field_validator

Availability = Literal[
    "prediction_metadata",
    "prediction_evidence",
    "prediction_estimate",
    "training_only",
    "evaluation_only",
]
DEPLOY_CLASSES = {"prediction_metadata", "prediction_evidence", "prediction_estimate"}


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FieldRef(_Strict):
    name: str
    availability: Availability


class ParamSpec(_Strict):
    type: str
    units: str | None = None
    required: bool = True
    is_assumption: bool = False
    description: str = ""


class QuantitySpec(_Strict):
    definition: str
    units: str
    canonical_kind: str
    ambiguity_allowed: bool = False

    @field_validator("canonical_kind")
    @classmethod
    def _nonempty(cls, v: str) -> str:
        if not v:
            raise ValueError("canonical_kind must name a channel representation or 'not_channel'")
        return v


class TruthSpec(_Strict):
    kind: Literal["exact", "simulated", "measured", "none"]
    description: str
    error_model: str


class NormSpec(_Strict):
    rule: str
    reversible: bool
    fit_scope: Literal["train", "train_dev"]


class RegimeRef(_Strict):
    name: str
    availability: Literal["inference", "supervision", "evaluation_only"]


class MetricSpec(_Strict):
    name: str
    direction: str
    units: str
    independent_unit: str


class SplitPolicy(_Strict):
    unit: str
    held_out_groups: list[str] = []
    pretraining_exposure: str = "none"


class UncReq(_Strict):
    kinds_accepted: list[str]
    may_be_unavailable: bool


class TaskSpec(_Strict):
    schema_version: int = 1
    task_id: str
    version: str
    task_kind: Literal["transform", "estimation", "comparison"]
    question: str
    allowed_inputs: list[FieldRef]
    required_capabilities: list[str] = []
    params: dict[str, ParamSpec] = {}
    quantities: dict[str, QuantitySpec]
    truth_source: TruthSpec
    normalization: NormSpec
    regime_coords: list[RegimeRef] = []
    baselines: list[str] = []
    metrics: list[MetricSpec] = []
    split_policy: SplitPolicy
    uncertainty_requirement: UncReq
    completion_rule: str
    promotion_rule: str

    def deploy_fields(self) -> list[str]:
        """The only fields a deployment-path operation may read (CF-06)."""
        return [f.name for f in self.allowed_inputs if f.availability in DEPLOY_CLASSES]

    def oracle_fields(self) -> list[str]:
        """Training-only and evaluation-only fields; a run that reads them is diagnostic."""
        return [f.name for f in self.allowed_inputs if f.availability not in DEPLOY_CLASSES]


def load(path: Path | str) -> TaskSpec:
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text())
    return TaskSpec.model_validate(data)
