# CrossFade

Conventions are in `HANDOFF.md`, "Conventions to keep". The gate is `ruff check crossfade packs tests && ruff format --check crossfade packs tests && pytest -q`.

## Code Review Rules
- Flag behavior the change adds that no test exercises.
- Flag a change to a contract (the shape of a record, task, run or result, or a CF rule) that isn't recorded in `build_pack/01_contracts.md` or the slice's PRD.
- Flag any invented dataset, threshold or result. This repo marks unknown values open instead.
