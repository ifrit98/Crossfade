"""W0 increment 2: TaskSpec loading. PRD-W0 AT-16."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from crossfade.tasks import TaskSpec, load

TASKS = Path(__file__).resolve().parents[1] / "tasks"


def test_loads_t0_task():
    t = load(TASKS / "profile.weighted_rms_width.v0.1.yaml")
    assert t.task_id == "profile.weighted_rms_width" and t.task_kind == "transform"
    assert t.quantities["mean_delay"].canonical_kind == "power_statistic"
    assert t.quantities["n_used"].canonical_kind == "not_channel"
    assert t.params["reference_time"].required is False


def test_w0_at16_unknown_field_rejected(tmp_path):
    data = yaml.safe_load((TASKS / "profile.weighted_rms_width.v0.1.yaml").read_text())
    data["surprise"] = 1
    with pytest.raises(ValidationError, match="surprise"):
        TaskSpec.model_validate(data)


def test_w0_at16_quantity_without_canonical_kind_rejected():
    data = yaml.safe_load((TASKS / "profile.weighted_rms_width.v0.1.yaml").read_text())
    del data["quantities"]["mean_delay"]["canonical_kind"]
    with pytest.raises(ValidationError, match="canonical_kind"):
        TaskSpec.model_validate(data)


def test_deploy_fields_exclude_oracle_classes():
    data = yaml.safe_load((TASKS / "profile.weighted_rms_width.v0.1.yaml").read_text())
    data["allowed_inputs"].append({"name": "truth", "availability": "evaluation_only"})
    data["allowed_inputs"].append({"name": "sim", "availability": "training_only"})
    t = TaskSpec.model_validate(data)
    assert set(t.deploy_fields()) == {"delay", "weight", "valid"}
    assert set(t.oracle_fields()) == {"truth", "sim"}
