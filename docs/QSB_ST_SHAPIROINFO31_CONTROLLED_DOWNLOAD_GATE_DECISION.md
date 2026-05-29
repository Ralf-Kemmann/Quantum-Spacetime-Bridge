# QSB-ST-SHAPIROINFO31 -- Controlled Download Gate Decision

## Current Anchor

`9f3ddbd Update QSB-ST ShapiroInfo manifest after file-link metadata review`

## Purpose

SHAPIROINFO31 trifft eine kontrollierte Gate-Entscheidung nach Source-,
Policy-, Manifest-, README-/Release-, Gate-Checker- und
File-Link-Metadata-Review.

Der Block entscheidet noch keinen Datenanalysezugang. Er entscheidet nur, ob
ein spaeterer minimaler Quarantaene-Download vorbereitet werden darf.

SHAPIROINFO31 selbst laedt nichts herunter.

## Scope

- controlled download gate decision only
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

## Decision

`controlled_download_gate_decision = LIMITED_GO_FOR_QUARANTINE_DOWNLOAD_PREP`

Meaning:

Ein spaeterer Download-Block darf vorbereitet werden, aber nur unter
Quarantaenebedingungen:

- keine automatische Analyse
- keine `.par` / `.tim`-Ingestion
- keine Sidecar-Population aus Dateiinhalten
- keine Adapterausfuehrung
- keine Residuen
- keine Rohdaten-Commits
- nur lokale Quarantaeneablage
- nur mit Manifest, Checksum, Source-URL, Retrieval-Log und Gate-Checker-Recheck

## Inputs Considered

| input | path | decision role |
|---|---|---|
| manifest update after metadata review | `docs/QSB_ST_SHAPIROINFO30_MANIFEST_UPDATE_AFTER_FILE_LINK_METADATA_REVIEW.md` | confirms metadata transfer without opening gates |
| file-link metadata result | `docs/QSB_ST_SHAPIROINFO29_FILE_LINK_METADATA_REVIEW_RESULT.md` | records link/header metadata only |
| machine-readable metadata review | `data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml` | records URL/header fields and blocked gate status |
| J0740 manifest draft | `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml` | remains blocked for analysis and sidecar use |
| negative test result | `docs/QSB_ST_SHAPIROINFO27_GATE_CHECKER_NEGATIVE_TEST_RESULT_NOTE.md` | shows fail-closed behavior for unsafe fixture states |
| gate checker | `scripts/run_qsb_st_shapiroinfo24b_gate_checker.py` | must be re-run before any later data-contact step |

## Gate Meaning

This is not a general download approval.
This is not an analysis approval.
This is not a sidecar-population approval.

It is a narrow permission to prepare a later, separate quarantine-download
block, provided the next block keeps all data-use and raw-data boundaries
visible.

## Mandatory Conditions For Any Later Quarantine Download Block

Any later block must:

- keep raw files local-only by default
- create or update a manifest entry before and after retrieval
- record source URL
- record retrieval command or browser action note
- record UTC retrieval timestamp
- record downloaded filename
- record local quarantine path
- compute and record checksum after download
- record file size
- avoid overwrite unless explicitly reviewed
- re-run the Gate-Checker after manifest update
- keep download outputs out of Git unless a later explicit raw-data policy pass says otherwise
- keep `sidecar_population_allowed: false`
- keep `dry_run_preview_allowed: false`

## Still Blocked

- automatic analysis
- `.par` / `.tim` ingestion
- parsing timing model parameters
- parsing TOAs
- sidecar population from file contents
- adapter execution
- residual calculation
- raw-data commit
- physical interpretation

## Gate Statuses After SHAPIROINFO31

`controlled_download_gate_decision = LIMITED_GO_FOR_QUARANTINE_DOWNLOAD_PREP`

`download_preparation_status = ALLOWED_FOR_NEXT_BLOCK_ONLY`

`download_execution_status = BLOCKED_IN_THIS_BLOCK`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

`analysis_gate_status = BLOCKED_BEFORE_ANALYSIS`

## Relation To SHAPIROINFO30

SHAPIROINFO30 updated the manifest with File-Link-Metadata review fields.
SHAPIROINFO31 uses that manifest state to permit only preparation of a later
quarantine-download block.

## Relation To SHAPIROINFO29

SHAPIROINFO29 recorded package-label and header metadata. SHAPIROINFO31 keeps
the same boundary: package metadata can support preparation, but package
content remains closed.

## Relation To Gate Checker

The Gate-Checker positive and negative tests remain part of the safety path. A
later quarantine-download block must re-run the checker after any manifest
change and must fail closed if gates or claim flags are unexpectedly open.

## Befund

The project has enough public source, citation, policy-context, manifest,
README/release-page, gate-checker, negative-test, and file-link-metadata
context to prepare a later minimal quarantine-download block.

## Interpretation

The decision is deliberately narrow. It moves the workflow from indefinite
planning toward a bounded technical next step, while preserving the boundary
between metadata review and data ingestion.

## Hypothese

A limited quarantine-download preparation gate can reduce provenance drift
while preventing raw data from being treated as analysis-ready input.

## Offene Luecke

- no download in SHAPIROINFO31
- no linked file opened
- no file body inspected
- no `.par` parsed
- no `.tim` parsed
- no checksum from downloaded file
- no quarantine directory created
- no raw data tracking
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
- no candidate residual claim from gate decision
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO32 Minimal Quarantine Download Plan
- SHAPIROINFO33 Controlled Quarantine Download Execution
- SHAPIROINFO34 Gate-Checker Recheck After Quarantine Manifest Update
- SHAPIROINFO35 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO36 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- enthaelt LIMITED_GO_FOR_QUARANTINE_DOWNLOAD_PREP
- enthaelt controlled_download_gate_decision
- enthaelt BLOCKED_IN_THIS_BLOCK
- enthaelt BLOCKED_RAW_DATA_TRACKING
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DRY_RUN
- enthaelt BLOCKED_BEFORE_ANALYSIS
- enthaelt Quarantaene
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
