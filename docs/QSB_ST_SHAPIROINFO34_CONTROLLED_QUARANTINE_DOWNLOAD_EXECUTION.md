# QSB-ST-SHAPIROINFO34 -- Controlled Quarantine Download Execution

## Current Anchor

`b2f87da Add QSB-ST ShapiroInfo gate checker pre-download recheck`

## Purpose

SHAPIROINFO34 fuehrt den ersten kontrollierten Quarantaene-Download der
J0740+6620-Dateien aus.

Der Download dient ausschliesslich der lokalen Quarantaeneablage und
Integritaetsdokumentation. Der Block fuehrt keine Analyse, kein Parsing und
keine Interpretation durch.

## Scope

- controlled quarantine download execution only
- local quarantine storage only
- no PINT / tempo2 installation
- no PINT / tempo2 execution
- no real pulsar evaluation
- no `.par` / `.tim` ingestion
- no File-Body-Inspektion nach dem Download
- no file content reading for science or parsing
- no sidecar population from file contents
- no adapter execution
- no residual calculation
- no raw-data commit
- no Bridge claim
- no Shapiro modification claim

## Pre-Download Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO33_GATE_CHECKER_PRE_DOWNLOAD_RECHECK.md`
- `docs/QSB_ST_SHAPIROINFO32_QUARANTINE_DOWNLOAD_PROCEDURE_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO31_CONTROLLED_DOWNLOAD_GATE_DECISION.md`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`
- `scripts/run_qsb_st_shapiroinfo24b_gate_checker.py`

Pre-download recheck from SHAPIROINFO33:

- `gate_decision: BLOCKED_EXPECTED`
- `failed_checks: 0`
- `exit_code: 0`

## Created Quarantine Layout

The following local quarantine directories were created:

- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/checksums/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/logs/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/notes/`

These are local quarantine artifacts, not analysis inputs.

## Retrieval Commands

Timing-data file:

```bash
curl --fail --location --show-error --silent --output data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim https://data.nanograv.org/static/data/J0740+6620.cfr+19.tim
```

Parameter file:

```bash
curl --fail --location --show-error --silent --output data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par https://data.nanograv.org/static/data/J0740+6620.par
```

Retrieval timestamp recorded:

`2026-05-29T22:22:41Z`

## Download Result Table

| label | source_url | local_path | file_size_bytes | sha256 | status |
|---|---|---|---|---|---|
| `J0740+6620 timing data` | `https://data.nanograv.org/static/data/J0740+6620.cfr+19.tim` | `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim` | `3660990` | `9ba8945092273d388558e7f61f01d050ce7701eb9658c4522315fd8c98157f78` | downloaded to local quarantine |
| `J0740+6620 parameter file` | `https://data.nanograv.org/static/data/J0740+6620.par` | `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par` | `14306` | `79360c122325ada7bcccda77db65bf2041b5458430841f7b0399f0c10c055015` | downloaded to local quarantine |

## Local Quarantine Artifacts

Raw files:

- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par`

Checksum files:

- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/checksums/J0740+6620.cfr+19.tim.sha256`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/checksums/J0740+6620.par.sha256`

Local manifest and notes:

- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/j0740_6620_quarantine_download_manifest_2026_05_29.yaml`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/logs/j0740_6620_quarantine_download_retrieval_log_2026_05_29.md`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/notes/QUARANTINE_BOUNDARY_NOTE.md`

These artifacts are not committed in this block unless Ralf later explicitly
decides otherwise.

## Boundary Controls

- raw files are local-only by default
- raw files are not committed
- checksum and retrieval artifacts are local quarantine support material
- no file body was opened after download
- no `.par` was parsed
- no `.tim` was parsed
- no TOAs were read
- no timing model parameters were read
- no Correction-State sidecar was populated from file contents
- no adapter was executed
- no residual was calculated

## Gate Statuses After SHAPIROINFO34

`quarantine_download_execution_status = QUARANTINE_DOWNLOAD_COMPLETED_LOCAL_ONLY`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`raw_data_commit_status = BLOCKED_RAW_DATA_COMMIT`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

`analysis_gate_status = BLOCKED_BEFORE_ANALYSIS`

## Relation To SHAPIROINFO33

SHAPIROINFO33 performed the pre-download Gate-Checker recheck and returned
`BLOCKED_EXPECTED` with `failed_checks: 0`. SHAPIROINFO34 uses that state as
the immediate control context for local quarantine download.

## Relation To SHAPIROINFO32

SHAPIROINFO32 specified the quarantine download procedure. SHAPIROINFO34
executes only the download and integrity-documentation part of that procedure.

## Befund

Two J0740+6620 files were downloaded into the local quarantine `raw/` directory.
File sizes and sha256 checksums were recorded. No file body was inspected after
download.

## Interpretation

This is a controlled local quarantine event, not a data-analysis step. The
files are now local artifacts whose integrity is documented, but they remain
outside parsing, sidecar population, adapter execution, residual calculation,
and Git tracking.

## Hypothese

Separating local quarantine retrieval from parsing and analysis reduces the
risk that public files enter the project as uncontrolled or overinterpreted
data.

## Offene Luecke

- no `.par` parsed
- no `.tim` parsed
- no file body inspected after download
- no TOAs read
- no timing model parameters read
- no Correction-State sidecar populated
- no adapter run
- no residual calculation
- no physical interpretation
- no raw-data commit

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from quarantine download
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO35 Gate-Checker Recheck After Quarantine Download
- SHAPIROINFO36 Manifest Update After Quarantine Download
- SHAPIROINFO37 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO38 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- raw files exist locally under quarantine path
- checksum files exist
- local quarantine manifest exists
- retrieval log exists
- contains QUARANTINE_DOWNLOAD_COMPLETED_LOCAL_ONLY
- contains BLOCKED_RAW_DATA_TRACKING
- contains BLOCKED_RAW_DATA_COMMIT
- contains BLOCKED_BEFORE_SIDECAR_DRAFT
- contains BLOCKED_BEFORE_DRY_RUN
- contains BLOCKED_BEFORE_ANALYSIS
- contains sha256
- contains no `.par` parsed
- contains no `.tim` parsed
- contains no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
