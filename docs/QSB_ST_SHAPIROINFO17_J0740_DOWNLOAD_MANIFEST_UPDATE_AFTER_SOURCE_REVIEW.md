# QSB-ST-SHAPIROINFO17 -- J0740+6620 Download Manifest Update After Source Review

## Current anchor

`c754770 Add QSB-ST ShapiroInfo J0740 manual source review result`

## Purpose

SHAPIROINFO17 uebertraegt nur die in SHAPIROINFO16 geprueften
Source-/Citation-Felder in den bestehenden J0740-Download-Manifest-Draft.

Dieser Block ist kein Download-Block. Er aktualisiert den Manifest-Draft nur
auf Source-/Citation-Review-Ebene und laesst alle operativen Gates geschlossen.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO15_J0740_DOWNLOAD_MANIFEST_DRAFT_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO16_J0740_MANUAL_SOURCE_REVIEW_RESULT.md`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`
- `docs/QSB_ST_SHAPIROINFO14_PUBLIC_SOURCE_DOWNLOAD_MANIFEST_TEMPLATE_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO12_PUBLIC_SOURCE_AND_CITATION_CHECKLIST.md`

## Scope

- manifest update note only
- source/citation field transfer only
- no download
- no dataset ingestion
- no `.par` / `.tim` parsing
- no `.par` / `.tim` inspection
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Files Created Or Modified

| path | action | status |
|---|---|---|
| `docs/QSB_ST_SHAPIROINFO17_J0740_DOWNLOAD_MANIFEST_UPDATE_AFTER_SOURCE_REVIEW.md` | created | result note for the manifest update |
| `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml` | modified | Source-/Citation fields updated only |

No other files are created or modified by this block.

## Transferred Fields

| manifest_area | field_or_status | value_after_update | source_in_SHAPIROINFO16 | boundary |
|---|---|---|---|---|
| `candidate_context` | `manual_source_review_result_reference` | `docs/QSB_ST_SHAPIROINFO16_J0740_MANUAL_SOURCE_REVIEW_RESULT.md` | SHAPIROINFO16 result note | Reference pointer only. |
| `candidate_context` | `public_source_review_status` | `SOURCE_REVIEW_PARTIAL_PASS` | Gate decision in SHAPIROINFO16 | Source review only; not a download pass. |
| `candidate_context` | `citation_gate_status` | `CITATION_IDENTITY_PASS` | Gate decision in SHAPIROINFO16 | Citation identity only. |
| `public_source_gate` | `source_page_url_status` | `reviewed_known_documented` | NANOGrav J0740 source page review | URL review does not inspect linked files. |
| `public_source_gate` | `dataset_or_release_name_status` | `reviewed_known_documented` | Timing Data for the Binary Parameters of J0740+6620 | Release/file metadata still unresolved. |
| `public_source_gate` | `citation_reference` | Cromartie et al. 2020, Nature Astronomy 4, 72-76; DOI 10.1038/s41550-019-0880-2 | Nature Astronomy citation review | Paper citation only, not dataset evidence. |
| `public_source_gate` | `citation_reference_status` | `reviewed_known_documented` | SHAPIROINFO16 citation gate | Citation pass only. |
| `public_source_gate` | `doi_or_stable_identifier` | paper DOI plus dataset-specific identifier still manual-review-required | DOI review in SHAPIROINFO16 | Paper DOI is not a dataset checksum or dataset-specific identifier. |
| `public_source_gate` | `data_access_method_status` | `reviewed_known_documented` | NANOGrav page lists download entries | Access method observed, not used. |
| `file_expectations` | `expected_timing_model_file.observed_status` | `reviewed_known_documented` | J0740+6620 parameter file listed | Expected file only; not downloaded or inspected. |
| `file_expectations` | `expected_timing_observation_file.observed_status` | `reviewed_known_documented` | J0740+6620 timing data listed | Expected file only; not downloaded or inspected. |

## Manifest Gate State After Update

The update does not open any operational gate:

- `manifest_gate_status` remains `BLOCKED_MANUAL_REVIEW_REQUIRED`
- `download_allowed` remains `false`
- `sidecar_population_allowed` remains `false`
- `dry_run_preview_allowed` remains `false`
- `download_plan.download_gate_status` remains `BLOCKED_MANUAL_REVIEW_REQUIRED`
- `downstream_gate.sidecar_gate_status` remains `BLOCKED_BEFORE_SIDECAR_DRAFT`
- `downstream_gate.adapter_gate_status` remains `BLOCKED_BEFORE_ADAPTER`

## Fields Not Updated

These remain unresolved or blocked:

- data-use/license note
- exact release metadata
- dataset-specific DOI or stable identifier
- README/release-note availability
- clock/ephemeris context
- noise/correction context
- local storage path
- checksum/integrity plan
- provenance manifest population
- Correction-State sidecar population
- window-definition sidecar population

## What Is Still Not Allowed

- no file download
- no local raw data directory population
- no `.par` / `.tim` inspection
- no `.par` / `.tim` ingestion
- no checksum calculation from files
- no correction-state sidecar population
- no adapter dry-run
- no residual preview

## Relation To SHAPIROINFO16

SHAPIROINFO16 produced the manual source review result. SHAPIROINFO17 applies
only the reviewed Source-/Citation-field updates recommended there. It does not
extend the review to data-use, file content, correction-state, local storage,
or checksum fields.

## Relation To SHAPIROINFO15

SHAPIROINFO15 created the candidate-specific download manifest draft.
SHAPIROINFO17 updates that same draft while preserving its blocked posture:
download, sidecar population, and dry-run preview remain disallowed.

## Relation To SHAPIROINFO14/12

SHAPIROINFO14 defined the generic public source download manifest template.
SHAPIROINFO12 defined the source/citation checklist. SHAPIROINFO17 keeps the
same gate discipline: source/citation identity can improve without permitting
data contact.

## Befund

The J0740 manifest draft now records the SHAPIROINFO16 source-review partial
pass, citation identity pass, paper DOI context, and reviewed expected timing
data / parameter-file status.

## Interpretation

The candidate is better documented at source/citation level, but it remains
blocked before download, before sidecar population, and before any dry-run
adapter path.

## Hypothese

Keeping source/citation updates separate from download permission may reduce
later audit ambiguity, because a candidate can become better documented without
quietly crossing into data contact.

## Offene Luecke

- no data-use/license note reviewed
- no README/release notes inspected
- no file downloaded
- no file metadata recorded
- no checksums computed
- no `.par` parsed
- no `.tim` parsed
- no `.par` / `.tim` ingestion
- no clock/ephemeris state inspected
- no noise/correction context inspected
- no sidecar populated
- no adapter run
- no residual calculation

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

- SHAPIROINFO18 Data-Use and License Review Note
- SHAPIROINFO19 J0740 Download Manifest Update After Data-Use Review
- SHAPIROINFO20 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO21 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- Manifest enthaelt `SOURCE_REVIEW_PARTIAL_PASS`
- Manifest enthaelt `CITATION_IDENTITY_PASS`
- Manifest enthaelt `reviewed_known_documented`
- Manifest enthaelt DOI `10.1038/s41550-019-0880-2`
- Manifest enthaelt `download_allowed: false`
- Manifest enthaelt `sidecar_population_allowed: false`
- Manifest enthaelt `dry_run_preview_allowed: false`
- Manifest enthaelt `downloaded_files: []`
- Manifest claim flags remain false
- Spec enthaelt no download
- Spec enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
