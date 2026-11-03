"""W0 increment 7: the CLI and the end-to-end demo. PRD-W0 AT-20 (runs offline; no network code
exists in the package, which test_no_network_imports asserts)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from conftest import profile_dataset

from crossfade.cli import main

ROOT = Path(__file__).resolve().parents[1]


def _write_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    profile_dataset([0.0, 2.0], [1.0, 1.0], "ms").to_zarr(
        tmp_path / "golden.zarr", consolidated=False
    )
    (tmp_path / "golden.yaml").write_text(
        yaml.safe_dump(
            {
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
        )
    )
    (tmp_path / "summary.json").write_text(
        json.dumps(
            {"assertions": [{"name": "range", "value": 12.5, "units": "km", "confidence": 0.7}]}
        )
    )
    (tmp_path / "summary.yaml").write_text(
        yaml.safe_dump(
            {
                "kind": "summary",
                "source_system": "legacy",
                "capability_label": "C0",
                "capabilities": ["upstream_asserted"],
            }
        )
    )
    (tmp_path / "params.yaml").write_text("reference_time: 2.0\nreference_time_units: ms\n")
    return (
        tmp_path / "golden.zarr",
        tmp_path / "golden.yaml",
        tmp_path / "summary.json",
        tmp_path / "summary.yaml",
    )


def test_w0_at20_demo_sequence(tmp_path, capsys):
    zarr, gman, sjson, sman = _write_inputs(tmp_path)
    store = str(tmp_path / "store")
    cfg = str(ROOT / "crossfade.toml")
    task = str(ROOT / "tasks" / "profile.weighted_rms_width.v0.1.yaml")
    stask = str(ROOT / "tasks" / "summary.compare.v0.1.yaml")

    assert main(["--store", store, "ingest", str(zarr), "--manifest", str(gman)]) == 0
    rec_id = json.loads(capsys.readouterr().out)["id"]
    assert main(["--store", store, "ingest", str(sjson), "--manifest", str(sman)]) == 0
    sum_id = json.loads(capsys.readouterr().out)["id"]

    assert (
        main(
            [
                "--store",
                store,
                "--config",
                cfg,
                "assess",
                task,
                rec_id,
                "--op",
                "profile.weighted_rms_width",
                "--params",
                str(tmp_path / "params.yaml"),
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["status"] == "supported"

    assert (
        main(
            [
                "--store",
                store,
                "--config",
                cfg,
                "run",
                task,
                rec_id,
                "--op",
                "profile.weighted_rms_width",
                "--params",
                str(tmp_path / "params.yaml"),
            ]
        )
        == 0
    )
    run = json.loads(capsys.readouterr().out)
    assert run["status"] == "succeeded"
    assert run["result"]["quantities"]["normalized_width"]["value"] == 0.5

    assert main(["--store", store, "--config", cfg, "replay", run["run_id"]]) == 0
    assert json.loads(capsys.readouterr().out)["attempt_of"] == run["run_id"]

    assert main(["--store", store, "inspect", rec_id]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["record"]["id"] == rec_id and len(shown["runs"]) == 2

    # the refusal: a summary record asked for a channel task
    rc = main(
        [
            "--store",
            store,
            "--config",
            cfg,
            "assess",
            task,
            sum_id,
            "--op",
            "profile.weighted_rms_width",
        ]
    )
    out = json.loads(capsys.readouterr().out)
    assert rc == 1 and out["status"] == "unsupported"

    assert (
        main(["--store", store, "--config", cfg, "run", stask, sum_id, "--op", "summary.import"])
        == 0
    )
    srun = json.loads(capsys.readouterr().out)
    assert srun["result"]["quantities"]["range"]["origin"] == "upstream_asserted"

    assert main(["--store", store, "verify"]) == 0
    v = json.loads(capsys.readouterr().out)
    assert v == {"mismatches": [], "orphans": [], "orphan_outputs": []}

    assert main(["--store", store, "export", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "store.tar").exists()


def test_no_network_imports():
    src = "".join(p.read_text() for p in (ROOT / "crossfade").glob("*.py"))
    for mod in ("requests", "urllib", "http.client", "socket", "httpx"):
        assert f"import {mod}" not in src and f"from {mod}" not in src
