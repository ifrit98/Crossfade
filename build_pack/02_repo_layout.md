# 02. Repository layout

## Tree

```
crossfade/
├── pyproject.toml            # package metadata; deps below; pytest and ruff config
├── crossfade.toml            # explicit pack list, store path, worker limits
├── crossfade/
│   ├── __init__.py
│   ├── records.py            # Record model; store put/get/verify; hashing; pint validation; zarr and JSON io
│   ├── tasks.py              # TaskSpec model; YAML loader; field availability classes
│   ├── packs.py              # Operation protocol; Assessment; registry from crossfade.toml; conformance helpers
│   ├── runs.py               # Run and Result models; execute(); replay(); subprocess worker
│   ├── bench.py              # ExperimentSpec; SplitManifest; leakage checker; feature firewall; aggregation; Report; claim index
│   ├── db.py                 # SQLite schema: records, runs, reports; open/migrate; ~80 lines
│   └── cli.py                # ingest, inspect, assess, run, replay, bench, report, export; argparse
├── packs/
│   ├── profile_fixture/      # W0: T0 weighted RMS width; descriptors_only anchor
│   ├── summary_fixture/      # W0: C0 structured summary; import_summary only
│   ├── sonar_sim/            # W1: image-source waveguide simulator; PDP estimators; beamform-STFT transform
│   └── hf_sim/               # W2: multimode skywave simulator; delay-Doppler estimators
├── tasks/                    # TaskSpec YAML files, versioned by filename
│   ├── profile.weighted_rms_width.v0.1.yaml
│   ├── summary.compare.v0.1.yaml
│   ├── pdp.rms_delay_spread.v0.1.yaml
│   └── pdp.arrival_count.v0.1.yaml
├── experiments/              # ExperimentSpec YAML files for the bench
├── fixtures/                 # golden inputs and reference answers, stored independently of implementations
├── tests/
│   ├── test_records.py
│   ├── test_tasks.py
│   ├── test_packs_conformance.py   # parametrized over every registered pack
│   ├── test_runs.py
│   ├── test_bench.py
│   └── test_w0_demo.py             # the end-to-end W0 acceptance run
└── store/                    # created at runtime; gitignored
    ├── blobs/<sha256>        # payloads: zarr directories or JSON files
    ├── records/<id>.json
    ├── runs/<id>.json
    ├── reports/<id>.json
    └── index.sqlite
```

## Module responsibilities

| Module | Owns | Does not own | Budget |
|---|---|---|---|
| `records.py` | `Record` model; `put(payload, manifest) -> Record`; `get(id)`; `verify(id)`; byte and manifest hashing; pint check at `put`; zarr write and read for arrays; JSON for structured | Any interpretation of what the record means | 350 |
| `tasks.py` | `TaskSpec` model; `load(path)`; the five field availability classes; `allowed_fields(task, phase)` | Any estimator | 150 |
| `packs.py` | `Operation` protocol; `Assessment`; `registry()` reading `crossfade.toml`; `conformance(pack)` helpers used by the parametrized test | Any operation implementation | 200 |
| `runs.py` | `Run`, `Result`, the five state enums; `execute(task, op, record, params) -> Run`; `replay(run_id) -> Run`; subprocess worker with resource limit; atomic publication of outputs then run | Metrics, comparisons | 350 |
| `bench.py` | `ExperimentSpec`; `SplitManifest`; `check_leakage()`; `firewall(task, phase)`; `aggregate()`; `Report`, `Claim`, `Mapping`; `claim_index()` | Training loops (those live in `packs/*/models.py`) | 500 by end of W1 |
| `db.py` | Three tables; open; migrate; row helpers | Anything semantic | 80 |
| `cli.py` | Eight subcommands mapping one-to-one to module functions | Logic | 150 |

## Dependencies

| Package | Role | Tag |
|---|---|---|
| `pydantic>=2` | All record types | [P] |
| `numpy`, `scipy` | Estimators, simulators | [P] |
| `xarray`, `zarr` | Labeled arrays and their storage | [P] |
| `pint` | Unit validation at ingest | [P] |
| `pyyaml` | TaskSpec and ExperimentSpec files | [P] |
| `pytest` | Tests | [P] |
| `ruff` | Lint and format | [P] |
| `torch` | W2 models only; not a core dependency | [P], W2 |
| `sbi` | W2 uncertainty where a forward model exists; optional | [P], W2 |

Nothing else in W0 to W3. A proposed dependency is reviewed against the one-sentence rule.

## CLI

Eight subcommands. Each is a thin wrapper over one module function; no logic lives in `cli.py`.

```
crossfade ingest   <payload> --manifest <yaml> [--kind observation|representation|anchor_estimate|summary]
crossfade inspect  <record_id | run_id | report_id>
crossfade assess   <task_yaml> <record_id> [--op <op_id>]
crossfade run      <task_yaml> <record_id> --op <op_id> [--params <yaml>] [--seed N]
crossfade replay   <run_id>
crossfade bench    <experiment_yaml>
crossfade report   <report_id> [--claims]
crossfade export   <out_dir>
```

`inspect` prints the record, its parents, and every run that consumed it. `export` tars the store and dumps the SQLite tables. There is no `serve`.

## Pack layout

```
packs/sonar_sim/
├── __init__.py       # CORE_API_VERSION = 1; OPERATIONS = [...]; REGIME = {...}; TRANSFORMS = [...]
├── manifest.toml     # name, version, fixtures, data_use defaults
├── sim.py            # the image-source waveguide generator (W1)
├── ops.py            # Operation implementations
├── models.py         # W2 only: encoders, heads
├── fixtures/         # golden inputs and answers for this pack
└── tests/            # pack-specific tests beyond conformance
```

Registration is one line in `crossfade.toml`:

```toml
[packs]
list = ["packs.profile_fixture", "packs.summary_fixture", "packs.sonar_sim"]
```

## Testing layout

Acceptance tests in each PRD have ids like `W0-AT-03`. The pytest function is named `test_w0_at03_<slug>` so a reviewer can grep from PRD to test. `test_packs_conformance.py` is parametrized over `registry()` and asserts, for every operation: `assess` refuses a record missing each declared precondition; `run` on the pack's golden fixture reproduces its stored answer within the op's declared tolerance; a run with an undeclared parameter is refused.

## Development workflow

`ruff check && ruff format --check && pytest -q` is the whole gate. It runs offline. There is no CI configuration in W0; a GitHub Actions file running that one line is added when a second contributor exists.
