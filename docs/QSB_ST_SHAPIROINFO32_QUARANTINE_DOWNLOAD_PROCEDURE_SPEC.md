# QSB-ST-SHAPIROINFO32 -- Quarantine Download Procedure Spec

## Current Anchor

`998c1ec Add QSB-ST ShapiroInfo controlled download gate decision`

## Purpose

SHAPIROINFO32 legt die konkrete Prozedur fuer einen moeglichen spaeteren
kontrollierten Quarantaene-Download der J0740+6620-Dateien fest.

Dieser Block ist noch kein Download-Block. Er oeffnet kein Analyse-, Parsing-,
Sidecar- oder Dry-run-Gate.

Die Schleuse wird beschrieben, nicht geoeffnet.

## Scope

- quarantine download procedure specification only
- no download
- no linked timing-data file opened
- no linked parameter file opened
- no file body inspection
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO31_CONTROLLED_DOWNLOAD_GATE_DECISION.md`
- `docs/QSB_ST_SHAPIROINFO30_MANIFEST_UPDATE_AFTER_FILE_LINK_METADATA_REVIEW.md`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml`
- `scripts/run_qsb_st_shapiroinfo24b_gate_checker.py`

## Procedure Decision Boundary

SHAPIROINFO31 permitted only preparation of a later quarantine-download block:

`controlled_download_gate_decision = LIMITED_GO_FOR_QUARANTINE_DOWNLOAD_PREP`

SHAPIROINFO32 turns that decision into a procedure. It still does not execute
the procedure.

## Planned Quarantine Layout

Planned only, not created in this block:

- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/checksums/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/notes/`

No directory is created by SHAPIROINFO32.

## Candidate Files For Later Quarantine Download

| role | source_url | planned_local_path | boundary |
|---|---|---|---|
| timing-data file | `https://data.nanograv.org/static/data/J0740+6620.cfr+19.tim` | `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim` | local quarantine only; no parsing |
| parameter file | `https://data.nanograv.org/static/data/J0740+6620.par` | `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par` | local quarantine only; no parsing |

## Required Pre-Download Checks For A Later Block

Before any later download execution, a later block must confirm:

- manifest still says `download_allowed_after_metadata_review: false`
- SHAPIROINFO31 decision is present
- data-use/license blockers are explicitly acknowledged
- raw files are local-only by default
- no raw-data commit is planned
- local quarantine paths are explicit
- overwrite policy is explicit
- retrieval command is shown before execution
- Gate-Checker is run before download
- Gate-Checker result is documented
- claim flags remain false

## Later Execution Procedure

If a later block explicitly performs quarantine download, it must:

1. Report `git status --short`.
2. Create only the planned quarantine directories.
3. Show exact source URLs and local target paths.
4. Refuse overwrite unless explicitly approved in that later block.
5. Retrieve raw files only into `raw/`.
6. Record retrieval timestamp UTC.
7. Record source URL.
8. Record retrieval command or browser action note.
9. Record downloaded filename.
10. Record local path.
11. Record file size.
12. Compute sha256 checksum after download.
13. Write a retrieval log under `notes/` or `manifest/`.
14. Write checksum material under `checksums/`.
15. Update the manifest in a later explicit manifest-update block.
16. Re-run the Gate-Checker after manifest update.

This procedure does not authorize parsing or analysis.

## Mandatory Post-Download Quarantine Rules

After any later quarantine download:

- raw files remain local-only by default
- raw files are not committed
- `.par` is not parsed
- `.tim` is not parsed
- file contents are not used to populate Correction-State
- no adapter run occurs
- no residual preview occurs
- no physical interpretation occurs
- checksums and retrieval logs may be reviewed for tracking

## Forbidden In SHAPIROINFO32

- no download
- no GET body download
- no opening linked timing-data file
- no opening linked parameter file
- no file body inspection
- no checksum from downloaded file
- no quarantine directory creation
- no raw data tracking
- no sidecar population
- no adapter dry-run
- no residual calculation

## Gate Statuses After SHAPIROINFO32

`quarantine_download_procedure_status = QUARANTINE_DOWNLOAD_PROCEDURE_DEFINED`

`download_execution_status = BLOCKED_IN_THIS_BLOCK`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`raw_data_commit_status = BLOCKED_RAW_DATA_COMMIT`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

`analysis_gate_status = BLOCKED_BEFORE_ANALYSIS`

## Relation To SHAPIROINFO31

SHAPIROINFO31 made the narrow decision:
`LIMITED_GO_FOR_QUARANTINE_DOWNLOAD_PREP`. SHAPIROINFO32 specifies how a later
quarantine download would have to be done if explicitly requested.

## Relation To SHAPIROINFO30/29

SHAPIROINFO29 recorded file-link metadata. SHAPIROINFO30 transferred those
metadata into the manifest. SHAPIROINFO32 uses those metadata only to define
source URLs and planned quarantine paths.

## Relation To Gate Checker

The Gate-Checker must be run before and after any later download-related
manifest update. Any unexpected open gate or true claim flag must stop the
workflow.

## Befund

The project now has a concrete procedure for a possible later quarantine
download without performing that download.

## Interpretation

The procedure makes the next technical step auditable while keeping raw files
out of analysis, sidecar population, adapter execution, and Git tracking.

## Hypothese

A written quarantine procedure can reduce the risk that a future raw-file
contact becomes silent ingestion or uncontrolled provenance drift.

## Offene Luecke

- no download in SHAPIROINFO32
- no quarantine directories created
- no file body inspected
- no `.par` parsed
- no `.tim` parsed
- no checksum from downloaded file
- no retrieval log created
- no manifest update from downloaded files
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
- no candidate residual claim from procedure planning
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO33 Controlled Quarantine Download Execution
- SHAPIROINFO34 Gate-Checker Recheck After Quarantine Manifest Update
- SHAPIROINFO35 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO36 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- enthaelt QUARANTINE_DOWNLOAD_PROCEDURE_DEFINED
- enthaelt BLOCKED_IN_THIS_BLOCK
- enthaelt BLOCKED_RAW_DATA_TRACKING
- enthaelt BLOCKED_RAW_DATA_COMMIT
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DRY_RUN
- enthaelt BLOCKED_BEFORE_ANALYSIS
- enthaelt sha256
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
