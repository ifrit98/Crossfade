"""Shared fixtures. Test-only helpers live here, never in the package."""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr


def profile_dataset(delay, weight, delay_units="ms", valid=None) -> xr.Dataset:
    """A delay-power profile as the T0 task expects it: point weights on a delay coordinate."""
    ds = xr.Dataset(
        {"weight": ("delay", np.asarray(weight, dtype=float), {"units": "1"})},
        coords={"delay": ("delay", np.asarray(delay, dtype=float), {"units": delay_units})},
    )
    if valid is not None:
        ds["valid"] = ("delay", np.asarray(valid, dtype=bool))
    return ds


def profile_manifest(**over) -> dict:
    m = {
        "kind": "representation",
        "source_system": "fixture",
        "capability_label": "C1",
        "capabilities": [],
        "masks": ["valid"],
        "processing_history": [
            {
                "op_id": "fixture.profile",
                "op_version": "0.1",
                "params": {"profile_convention": "point_weights"},
                "transform_class": "exact",
            }
        ],
    }
    m.update(over)
    return m


@pytest.fixture
def store(tmp_path):
    from crossfade.records import Store

    return Store(tmp_path / "store")


@pytest.fixture
def golden_ms():
    return profile_dataset([0.0, 2.0], [1.0, 1.0], "ms")


@pytest.fixture
def golden_s():
    return profile_dataset([0.0, 0.002], [1.0, 1.0], "s")
