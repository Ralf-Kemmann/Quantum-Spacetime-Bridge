# QSB-ST-SHAPIROINFO29 -- File-Link Metadata Review Result

## Current Anchor

`21d34b6 Add QSB-ST ShapiroInfo file-link metadata review plan`

## Purpose

SHAPIROINFO29 dokumentiert eine begrenzte File-Link-Metadatenpruefung fuer
J0740+6620. Dieser Block prueft nur Link-/Header-/Dateimetadaten und keine
Dateiinhalte.

File-link metadata is not data ingestion.
Header metadata is not .par/.tim parsing.
Visible link labels are not file inspection.

## Scope

- file-link metadata review result only
- public source page review only
- link-label and href metadata only
- header-only checks only
- no download
- no GET body download
- no file body retrieval
- no file bodies saved
- no linked timing-data file opened as data
- no linked parameter file opened as data
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Created Files

| path | role |
|---|---|
| `data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml` | machine-readable metadata review record |
| `docs/QSB_ST_SHAPIROINFO29_FILE_LINK_METADATA_REVIEW_RESULT.md` | human-readable result note |

No existing file is modified by SHAPIROINFO29.

## Source Page Reviewed

Source page:

`https://nanograv.org/science/data/timing-data-binary-parameters-j07406620`

Observed at public page level:

- title: `Timing Data for the Binary Parameters of J0740+6620`
- visible link label: `J0740+6620 timing data`
- visible link label: `J0740+6620 parameter file`
- reference context: H.T. Cromartie et al., Nature Astronomy 4, 72 (2020)

The source-page HTML was inspected only to identify visible link targets. No
timing-data or parameter-file body was opened or saved.

## Header-Only Commands Used

Source-page href inspection:

```bash
curl --silent --show-error --location --max-time 20 https://nanograv.org/science/data/timing-data-binary-parameters-j07406620 | rg -n "J0740|href|Downloads|data\\.nanograv"
```

Timing-data link metadata:

```bash
curl --head --location --max-time 20 https://data.nanograv.org/static/data/J0740+6620.cfr+19.tim
```

Parameter-file link metadata:

```bash
curl --head --location --max-time 20 https://data.nanograv.org/static/data/J0740+6620.par
```

These commands did not save file bodies and did not parse `.par` / `.tim`
contents.

## Metadata Result Table

| link_label | link_target_url | http_status_code | content_type | content_length_bytes | last_modified | etag | redirect_chain | result |
|---|---|---|---|---|---|---|---|---|
| `J0740+6620 timing data` | `https://data.nanograv.org/static/data/J0740+6620.cfr+19.tim` | `200` | `application/octet-stream` | `3660990` | `Wed, 15 Apr 2020 14:11:38 GMT` | `"5e97161a-37dcbe"` | no redirect hop visible | metadata recorded |
| `J0740+6620 parameter file` | `https://data.nanograv.org/static/data/J0740+6620.par` | `200` | `application/octet-stream` | `14306` | `Wed, 15 Apr 2020 14:11:38 GMT` | `"5e97161a-37e2"` | no redirect hop visible | metadata recorded |

## Gate Statuses After SHAPIROINFO29

`file_link_metadata_review_status = FILE_LINK_METADATA_REVIEW_PARTIAL`

`download_gate_status = BLOCKED_BEFORE_DOWNLOAD`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

`download_allowed_after_metadata_review = false`

## Result Interpretation

The metadata review confirms that the public source page exposes two visible
file links and that both link targets respond to header-only checks. This does
not open a download gate.

The result is metadata only. It does not inspect timing data, parameter values,
TOAs, residuals, clock state, ephemeris state, DM/ISM state, backend state, or
noise model state.

## Relation To SHAPIROINFO28

SHAPIROINFO28 planned a bounded file-link metadata review. SHAPIROINFO29
executes only that bounded metadata layer: source-page link labels, visible
hrefs, and HEAD/header metadata.

## Relation To Gate Checker

The Gate-Checker remains relevant before any future data contact. SHAPIROINFO29
does not change the manifest gates and does not bypass the `BLOCKED_EXPECTED`
control path.

## Befund

The J0740+6620 source page exposes two visible file-link targets. Header-only
metadata was recorded for the timing-data link and the parameter-file link.

## Interpretation

The candidate is more reproducible at link-metadata level, but still blocked
before download, raw-data tracking, sidecar population, dry-run adapter use, or
residual calculation.

## Hypothese

Recording link and header metadata before download may reduce later provenance
drift without crossing into data ingestion.

## Offene Luecke

- no file downloaded
- no file body opened
- no file body saved
- no `.par` parsed
- no `.tim` parsed
- no checksum from downloaded file
- no source-provided checksum observed
- no sidecar populated
- no adapter run
- no residual calculation
- no physical interpretation

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from metadata review
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO30 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO31 Targeted Binary Pulsar Dry-Run Adapter Spec
- SHAPIROINFO32 Controlled Download Gate Decision
- SHAPIROINFO33 File-Link Metadata Manifest Update

## Acceptance Checks

- Datei `j0740_6620_file_link_metadata_review.yaml` existiert
- Datei `QSB_ST_SHAPIROINFO29_FILE_LINK_METADATA_REVIEW_RESULT.md` existiert
- enthaelt File-link metadata is not data ingestion
- enthaelt Header metadata is not .par/.tim parsing
- enthaelt Visible link labels are not file inspection
- enthaelt `J0740+6620 timing data`
- enthaelt `J0740+6620 parameter file`
- enthaelt `http_status_code`
- enthaelt `content_type`
- enthaelt `content_length_bytes`
- enthaelt `last_modified`
- enthaelt `etag`
- enthaelt `download_allowed_after_metadata_review = false`
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
