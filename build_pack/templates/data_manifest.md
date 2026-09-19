# Data manifest

One per dataset, simulated or measured, stored as a `Record` of kind `summary` before any run consumes the data.

- **name, version**
- **source:** generator and version, or provider and access date
- **license or clearance:** and the `data_use` label to stamp on every record
- **capability_label** and explicit **capabilities**
- **group id scheme:** which fields give session, instrument, environment, source_recording, scene
- **truth:** kind (exact, simulated, measured, none), how constructed, error model
- **regime coverage:** list of cells per governing group, from metadata; not a bounding box
- **known gaps:** missing metadata, excluded records, and why
- **independence:** for a simulator, the reference to its independence statement
