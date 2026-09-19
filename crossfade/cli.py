"""Eight thin subcommands, each one module function. No logic lives here."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
from pathlib import Path
from typing import Any

import xarray as xr
import yaml

from crossfade.packs import assess as _assess
from crossfade.packs import registry
from crossfade.records import Store
from crossfade.runs import execute, load_run, replay
from crossfade.tasks import load as load_task


def _out(obj: Any) -> None:
    print(json.dumps(obj, indent=1, default=str))


def _load_payload(path: Path) -> Any:
    if path.suffix == ".zarr" or path.is_dir():
        return xr.open_zarr(path, consolidated=False).load()
    return json.loads(path.read_text())


def _params(path: str | None) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text()) or {} if path else {}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="crossfade")
    p.add_argument("--store", default="store")
    p.add_argument("--config", default="crossfade.toml")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ingest")
    s.add_argument("payload")
    s.add_argument("--manifest", required=True)
    s = sub.add_parser("inspect")
    s.add_argument("id")
    for name in ("assess", "run"):
        s = sub.add_parser(name)
        s.add_argument("task")
        s.add_argument("record")
        s.add_argument("--op", required=True)
        s.add_argument("--params")
        s.add_argument("--seed", type=int)
    s = sub.add_parser("replay")
    s.add_argument("run_id")
    sub.add_parser("verify")
    s = sub.add_parser("export")
    s.add_argument("out_dir")
    a = p.parse_args(argv)

    store = Store(Path(a.store))
    if a.cmd == "ingest":
        manifest = yaml.safe_load(Path(a.manifest).read_text())
        rec = store.put(_load_payload(Path(a.payload)), manifest)
        _out(rec.model_dump(mode="json"))
        return 0
    if a.cmd == "inspect":
        if a.id.startswith("run_"):
            _out(load_run(store, a.id).model_dump(mode="json"))
            return 0
        rec = store.get(a.id)
        rows = store.db.execute("SELECT path FROM runs").fetchall()
        runs = [load_run(store, Path(r[0]).stem) for r in rows]
        _out(
            {
                "record": rec.model_dump(mode="json"),
                "runs": [r.model_dump(mode="json") for r in runs if a.id in r.inputs],
            }
        )
        return 0
    if a.cmd == "verify":
        _out(store.verify())
        return 0
    if a.cmd == "export":
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        with tarfile.open(out / "store.tar", "w") as tar:
            tar.add(store.root, arcname="store")
        _out({"exported": str(out / "store.tar")})
        return 0

    reg = registry(a.config)
    if a.cmd == "replay":
        _out(replay(store, a.run_id, reg).model_dump(mode="json"))
        return 0
    task, rec, op = load_task(a.task), store.get(a.record), reg[a.op]
    if a.cmd == "assess":
        res = _assess(op, task, rec, _params(a.params))
        _out(res.model_dump())
        return 0 if res.status == "supported" else 1
    run = execute(store, task, op, rec, _params(a.params), seed=a.seed)
    _out(run.model_dump(mode="json"))
    return 0 if run.status == "succeeded" else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
