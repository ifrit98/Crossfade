# Simulator independence statement

Required for every cross-domain claim from simulation (section 03 §6). Stored as a `Record` of kind `summary` and referenced by the report.

- **Generators:** A and B, with versions and code locations.
- **Physics kernels:** what each solves; confirmation that no propagation code is shared.
- **Scene distributions:** how scenes are sampled in each; whether any sampling code or distribution is shared.
- **Approximation families:** the modeling assumptions of each; every assumption shared by both, stated plainly. For the v0.3 in-house generators this includes "discrete paths with per-path delay and gain," which is also the anchor assumption.
- **Truth construction:** how truth is derived in each; whether the two derivations share a rule (for example the arrival-merging rule for `arrival_count`).
- **Shared infrastructure that is acceptable:** array libraries, schemas, readers, the bootstrap code.
- **Consequence:** which claims this independence supports and which require measured-data validation.
