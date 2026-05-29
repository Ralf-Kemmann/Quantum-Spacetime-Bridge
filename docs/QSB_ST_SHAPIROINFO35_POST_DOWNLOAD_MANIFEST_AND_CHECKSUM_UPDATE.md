# QSB-ST-SHAPIROINFO35 -- Post-Download Manifest and Checksum Update

## Current Anchor

`729d15b Add QSB-ST ShapiroInfo controlled quarantine download execution note`

## Purpose

SHAPIROINFO35 aktualisiert das bestehende J0740-Manifest mit den lokalen
Quarantaene-Download- und Integritaetsinformationen aus SHAPIROINFO34.

Der Block dokumentiert Dateigroesse, sha256 und lokale Quarantaenepfade, ohne
Raw-Dateien zu committen oder Inhalte zu inspizieren.

## Scope

- post-download manifest and checksum update only
- no new downloads
- no new scripts
- no new runs
- no PINT / tempo2 installation
- no PINT / tempo2 execution
- no real pulsar evaluation
- no `.par` / `.tim` ingestion
- no File-Body-Inspektion
- no raw file display
- no sidecar population from file contents
- no adapter execution
- no residual calculation
- no raw-data commit
- no Bridge claim
- no Shapiro modification claim

## Files Created Or Modified

| path | action | status |
|---|---|---|
| `docs/QSB_ST_SHAPIROINFO35_POST_DOWNLOAD_MANIFEST_AND_CHECKSUM_UPDATE.md` | created | manifest/checksum update note |
| `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml` | modified | local quarantine paths, sizes, sha256 values recorded |

No other existing project file is modified by this block.

Raw files and local quarantine artifacts under
`data/QSB-ST-SHAPIROINFO/public_sources/` remain untracked and are not committed.

## Local Files Verified

Allowed checks only: `test -f`, `stat`, `sha256sum`, and `find` for paths.

| file | local_path | size_bytes | sha256 |
|---|---|---|---|
| `J0740+6620.cfr+19.tim` | `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim` | `3660990` | `9ba8945092273d388558e7f61f01d050ce7701eb9658c4522315fd8c98157f78` |
| `J0740+6620.par` | `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par` | `14306` | `79360c122325ada7bcccda77db65bf2041b5458430841f7b0399f0c10c055015` |

## Manifest Fields Updated

| manifest_area | field_or_status | value_after_update | boundary |
|---|---|---|---|
| `candidate_context` | `quarantine_download_status` | `QUARANTINE_DOWNLOAD_COMPLETED_LOCAL_ONLY` | Local quarantine only. |
| `candidate_context` | `local_integrity_status` | `LOCAL_CHECKSUM_RECORDED` | Integrity only. |
| `file_expectations.expected_timing_observation_file` | `local_quarantine_path` | raw `.tim` quarantine path | No parsing. |
| `file_expectations.expected_timing_observation_file` | `local_file_size_bytes` | `3660990` | Size metadata only. |
| `file_expectations.expected_timing_observation_file` | `local_sha256` | `9ba8945092273d388558e7f61f01d050ce7701eb9658c4522315fd8c98157f78` | Integrity only. |
| `file_expectations.expected_timing_model_file` | `local_quarantine_path` | raw `.par` quarantine path | No parsing. |
| `file_expectations.expected_timing_model_file` | `local_file_size_bytes` | `14306` | Size metadata only. |
| `file_expectations.expected_timing_model_file` | `local_sha256` | `79360c122325ada7bcccda77db65bf2041b5458430841f7b0399f0c10c055015` | Integrity only. |
| `download_plan` | `post_download_manifest_update_status` | `LOCAL_INTEGRITY_RECORDED` | Analysis still blocked. |
| `local_storage_plan` | `local_storage_status` | `LOCAL_QUARANTINE_CREATED` | Raw files stay local. |
| `integrity_plan` | `integrity_gate_status` | `LOCAL_INTEGRITY_RECORDED_ANALYSIS_BLOCKED` | No analysis gate. |

## Gate State After Update

The manifest update does not open any analysis or parsing gate:

- `download_allowed` remains `false`
- `sidecar_population_allowed` remains `false`
- `dry_run_preview_allowed` remains `false`
- `downloaded_files` remains `[]`
- raw files remain untracked
- raw-data commit remains blocked
- `.par` / `.tim` ingestion remains blocked
- sidecar population from file contents remains blocked
- adapter execution remains blocked
- residual calculation remains blocked

## What Was Not Done

- no new download
- no raw file opened, displayed, grepped, sed-read, head-read, or tail-read
- no `.par` parsed
- no `.tim` parsed
- no timing model parameter read
- no TOA read
- no sidecar populated from file contents
- no adapter execution
- no residual calculation
- no physical interpretation

## Relation To SHAPIROINFO34

SHAPIROINFO34 performed the controlled local quarantine download and recorded
the initial local file sizes and sha256 values. SHAPIROINFO35 transfers those
integrity values into the existing blocked J0740 manifest.

## Relation To SHAPIROINFO32

SHAPIROINFO32 specified that any download must remain quarantine-only and must
document source URL, local path, size, checksum, and retrieval boundary.
SHAPIROINFO35 completes the manifest side of that bookkeeping.

## Befund

The J0740 manifest now records local quarantine paths, file sizes, sha256
checksums, and local integrity status for the two quarantined files.

## Interpretation

This improves auditability of the local quarantine state without turning raw
files into tracked data, parsed inputs, sidecar sources, adapter inputs, or
scientific evidence.

## Hypothese

Recording checksums in the manifest may reduce later provenance drift while
keeping a hard boundary between quarantine storage and analysis.

## Offene Luecke

- no post-download Gate-Checker run in this block
- no `.par` parsed
- no `.tim` parsed
- no file body inspected
- no sidecar populated
- no adapter run
- no residual calculation
- no physical interpretation
- raw files remain untracked

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from manifest update
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO36 Gate-Checker Recheck After Post-Download Manifest Update
- SHAPIROINFO37 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO38 Targeted Binary Pulsar Dry-Run Adapter Spec
- SHAPIROINFO39 Raw-Data Tracking Policy Decision

## Acceptance Checks

- Datei existiert
- Manifest enthaelt `QUARANTINE_DOWNLOAD_COMPLETED_LOCAL_ONLY`
- Manifest enthaelt `LOCAL_CHECKSUM_RECORDED`
- Manifest enthaelt `LOCAL_INTEGRITY_RECORDED_ANALYSIS_BLOCKED`
- Manifest enthaelt `sha256`
- Manifest enthaelt `3660990`
- Manifest enthaelt `14306`
- Manifest enthaelt `raw_data_commit_allowed: false`
- Manifest enthaelt `file_body_inspected_after_download: false`
- Spec enthaelt no new download
- Spec enthaelt no `.par` parsed
- Spec enthaelt no `.tim` parsed
- Spec enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
