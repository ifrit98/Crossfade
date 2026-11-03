# CrossFade

Conventions are in `HANDOFF.md`, "Conventions to keep". The gate uses the `.venv` in the main checkout and runs from it or from any worktree:

```
V="$(git rev-parse --path-format=absolute --git-common-dir)/../.venv/bin"
$V/ruff check crossfade packs tests && $V/ruff format --check crossfade packs tests && $V/python -m pytest -q
```

## Code Review Rules
- Flag behavior the change adds that no test exercises.
- Flag a change to a contract (the shape of a record, task, run or result, or a CF rule) that isn't recorded in `build_pack/01_contracts.md` or the slice's PRD.
- Flag any invented dataset, threshold or result. This repo marks unknown values open instead.
