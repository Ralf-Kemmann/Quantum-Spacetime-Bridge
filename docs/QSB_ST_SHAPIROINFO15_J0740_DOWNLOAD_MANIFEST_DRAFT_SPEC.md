# QSB-ST-SHAPIROINFO15 -- J0740+6620 Download Manifest Draft Spec

## Current anchor

`0f24462 Add QSB-ST ShapiroInfo public source download manifest template`

## Purpose

SHAPIROINFO15 erzeugt einen J0740+6620-spezifischen
Download-Manifest-Draft for Manual Review.

Dieser Draft erlaubt noch nichts. Er dokumentiert nur die aus SHAPIROINFO13
uebernommene oeffentliche Quellseite, den Kandidatenkontext und die weiterhin
blockierenden Review-Gates vor jedem Download, jeder lokalen Ablage, jeder
Sidecar-Population und jeder Dry-Run-Preview.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO13_CANDIDATE_SOURCE_REVIEW_J0740_6620.md`
- `docs/QSB_ST_SHAPIROINFO14_PUBLIC_SOURCE_DOWNLOAD_MANIFEST_TEMPLATE_SPEC.md`
- `data/QSB-ST-SHAPIROINFO/public_source_download_manifest_template.yaml`

## Scope

- manual-review manifest draft only
- no download
- no data analysis
- no run output
- no script creation
- no `.par` / `.tim` parsing
- no `.par` / `.tim` ingestion
- no PINT/tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Created Files

| path | role | status |
|---|---|---|
| `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml` | J0740+6620-specific download manifest draft for manual review. | created; blocked |
| `docs/QSB_ST_SHAPIROINFO15_J0740_DOWNLOAD_MANIFEST_DRAFT_SPEC.md` | Human-readable spec for the manual-review draft. | created; spec only |

No other files are created by this block.

## Candidate Context

Candidate:

- NANOGrav J0740+6620

Source page:

- `https://nanograv.org/science/data/timing-data-binary-parameters-j07406620`

Source-page title:

- Timing Data for the Binary Parameters of J0740+6620

Citation path:

- Cromartie et al. 2020, Nature Astronomy, as referenced by the NANOGrav source
  page

Expected source-page items:

- J0740+6620 timing data
- J0740+6620 parameter file

Manual-review boundary:

- no files downloaded in SHAPIROINFO15
- no file content inspected
- no `.par` parsed
- no `.tim` parsed
- no sidecar populated

## Manifest Decision

Required draft values:

- `manifest_record_id = J0740_6620_MANUAL_REVIEW_DRAFT_NO_DOWNLOAD`
- `manifest_gate_status = BLOCKED_MANUAL_REVIEW_REQUIRED`
- `download_allowed = false`
- `sidecar_population_allowed = false`
- `dry_run_preview_allowed = false`

Interpretation:

The J0740+6620 source page is specific enough for a manual-review draft, but
the draft does not clear download, sidecar population, adapter dry-run, or
residual preview.

Remaining blockers:

- data-use/license note remains unresolved
- exact release metadata remains unresolved
- DOI or stable identifier remains unresolved
- local storage plan remains unresolved
- checksum/integrity plan remains unresolved
- provenance manifest remains unpopulated
- clock/ephemeris context remains uninspected
- noise/correction context remains uninspected

## Relation To SHAPIROINFO13

SHAPIROINFO13 reviewed the public NANOGrav source page for J0740+6620 at
source-review level only. It found that the source page exists and lists
J0740+6620 timing data plus a J0740+6620 parameter file, while keeping download
and sidecar gates blocked.

SHAPIROINFO15 carries those source-review facts into a manual-review manifest
draft without downloading or inspecting files.

## Relation To SHAPIROINFO14

SHAPIROINFO14 created the generic public source download manifest template.
SHAPIROINFO15 creates a candidate-specific draft from that template, with the
same blocker posture and with J0740+6620-specific source context filled at
manual-review level.

## Relation To SHAPIROINFO11

SHAPIROINFO11 created the Correction-State sidecar template. SHAPIROINFO15 does
not populate that sidecar and does not authorize sidecar population. The
download manifest draft remains upstream of any dataset-specific
Correction-State sidecar.

## Befund

A J0740+6620-specific manifest draft now records the NANOGrav source page, the
source-page title, the Cromartie et al. 2020 Nature Astronomy citation path,
and the expected source-page entries for timing data and parameter file.

## Interpretation

The candidate remains in manual-review state. The manifest draft improves
auditability, but it does not create a local dataset, does not inspect timing
files, and does not permit a Sidecar- or Adapter-Schritt.

## Hypothese

A blocked, candidate-specific manifest draft may make the next manual review
more auditable by separating source identity from download permission and by
keeping unresolved provenance, storage, integrity, and correction-state fields
visible.

## Offene Luecke

- no download
- no files downloaded in SHAPIROINFO15
- no local data files
- no checksum recorded
- no file size recorded
- no `.par` parsed
- no `.tim` parsed
- no `.par` / `.tim` ingestion
- no data-use/license note resolved
- no exact release metadata resolved
- no DOI or stable identifier resolved
- no clock state inspected
- no ephemeris state inspected
- no noise/correction context inspected
- no Correction-State sidecar populated
- no adapter run
- no residual calculation
- no empirical result

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from manifest drafting
- no derivation of c
- no explanation of the numerical value of c+

## Next Possible Blocks

- SHAPIROINFO15A J0740+6620 Manual Source Review Checklist
- SHAPIROINFO16 J0740+6620 Provenance Manifest Draft for Manual Review Only
- SHAPIROINFO17 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO18 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`
  existiert
- Datei `docs/QSB_ST_SHAPIROINFO15_J0740_DOWNLOAD_MANIFEST_DRAFT_SPEC.md`
  existiert
- YAML enthaelt `manifest_record_id: "J0740_6620_MANUAL_REVIEW_DRAFT_NO_DOWNLOAD"`
- YAML enthaelt `manifest_gate_status: "BLOCKED_MANUAL_REVIEW_REQUIRED"`
- YAML enthaelt `download_allowed: false`
- YAML enthaelt `sidecar_population_allowed: false`
- YAML enthaelt `dry_run_preview_allowed: false`
- YAML enthaelt NANOGrav J0740+6620
- YAML enthaelt Timing Data for the Binary Parameters of J0740+6620
- YAML enthaelt Cromartie et al. 2020, Nature Astronomy
- YAML enthaelt J0740+6620 timing data
- YAML enthaelt J0740+6620 parameter file
- YAML enthaelt no files downloaded in SHAPIROINFO15
- YAML claim flags are all false
- Spec enthaelt Current anchor `0f24462`
- Spec enthaelt Manifest decision
- Spec enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
