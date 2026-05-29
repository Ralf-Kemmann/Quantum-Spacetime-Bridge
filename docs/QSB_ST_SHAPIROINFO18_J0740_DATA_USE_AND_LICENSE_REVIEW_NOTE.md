# QSB-ST-SHAPIROINFO18 -- J0740+6620 Data-Use and License Review Note

## Current anchor

`4ecaee9 Update QSB-ST ShapiroInfo J0740 manifest after source review`

## Purpose

SHAPIROINFO18 prueft, ob die Nutzungs-, Zitier- und Policy-Lage fuer einen
spaeteren kontrollierten Download-Schritt ausreichend dokumentierbar erscheint.
Es ist kein Download-Block.

Dieser Block dokumentiert eine vorsichtige Data-Use-/License-/Citation-Pruefung
fuer den Kandidaten J0740+6620. Er prueft nur oeffentliche
Nutzungs-/Zitierhinweise auf Review-Ebene. Er laedt keine Daten, inspiziert
keine Dateien und oeffnet kein Download-Gate.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO12_PUBLIC_SOURCE_AND_CITATION_CHECKLIST.md`
- `docs/QSB_ST_SHAPIROINFO13_CANDIDATE_SOURCE_REVIEW_J0740_6620.md`
- `docs/QSB_ST_SHAPIROINFO15_J0740_DOWNLOAD_MANIFEST_DRAFT_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO16_J0740_MANUAL_SOURCE_REVIEW_RESULT.md`
- `docs/QSB_ST_SHAPIROINFO17_J0740_DOWNLOAD_MANIFEST_UPDATE_AFTER_SOURCE_REVIEW.md`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`

## Scope

- data-use / license review note only
- no download
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Reviewed Public Context

Quelle 1:

NANOGrav Data page

URL:

`https://nanograv.org/science/data`

Observed:

- lists "Timing Data for the Binary Parameters of J0740+6620"
- describes the release as TEMPO/TEMPO2-compatible timing data for Cromartie et
  al. 2020
- supports data/public-release context and file-format expectation only

Quelle 2:

NANOGrav J0740+6620 source page

URL:

`https://nanograv.org/science/data/timing-data-binary-parameters-j07406620`

Observed:

- source page is public
- lists J0740+6620 timing data
- lists J0740+6620 parameter file
- references Cromartie et al. 2020

Quelle 3:

NANOGrav Publication Policy

URL:

`https://nanograv.org/resources/members/publication-policy`

Observed:

- policy text refers to NANOGrav publications
- includes publications involving or motivated by NANOGrav data,
  pre-publication NANOGrav research/results, member discussions, NANOGrav
  science, or NANOGrav-developed tools
- this is relevant as cautionary publication/use context
- this does not by itself authorize download or reuse
- exact data-use/license conditions for the J0740 public release remain
  manual-review material

Quelle 4:

Cromartie et al. 2020 citation

Title:

Relativistic Shapiro delay measurements of an extremely massive millisecond
pulsar

Journal:

Nature Astronomy 4, 72-76 (2020)

DOI:

10.1038/s41550-019-0880-2

Use:

citation identity and scientific context only, not project evidence

## Data-Use Review Table

| review_item | status | evidence | remaining_blocker | gate_effect | notes |
|---|---|---|---|---|---|
| `public_release_page_visible` | `reviewed_known_documented` | NANOGrav J0740 source page and NANOGrav data page | none for public visibility | supports source review only | Public visibility is not reuse permission. |
| `citation_path_visible` | `reviewed_known_documented` | Cromartie et al. 2020 cited by source page; DOI known | none for paper citation identity | citation identity can remain pass | Citation path is visible and separable from data-use terms. |
| `publication_policy_context_visible` | `reviewed_known_documented` | NANOGrav Publication Policy page exists and describes scope for NANOGrav publications / data-related work | determine whether/how it applies to this project's later use | manual review still required before download | Policy context is cautionary, not a download authorization. |
| `data_use_or_license_note` | `manual_review_required` | no dataset-specific license/reuse statement confirmed in this block | dataset-specific use/license note must be captured before download | download remains blocked | Public release context is not enough by itself. |
| `required_acknowledgement_or_citation` | `manual_review_required` | source cites Cromartie et al. 2020; additional acknowledgements may exist | acknowledgement/citation wording not finalized | download remains blocked | Later note must preserve exact required wording if found. |
| `download_terms` | `manual_review_required` | no download performed; linked files not opened | download page/link terms not reviewed at file level | download remains blocked | File-level terms remain unknown. |
| `repository_publication_risk` | `needs_manual_review` | future repo may document derived workflow; exact NANOGrav policy relation should be respected | clarify citation/acknowledgement and avoid redistribution if not clearly permitted | raw data storage/public tracking remains blocked | Keep raw data out of tracked history unless explicitly allowed and approved. |
| `redistribution_policy` | `unknown` | no explicit redistribution permission captured | do not commit raw downloaded files unless explicit permission and project decision | raw data tracking remains blocked | Unknown redistribution state is a blocker. |

## Gate Decision

`data_use_review_status = DATA_USE_REVIEW_PARTIAL`

`citation_policy_context_status = CITATION_POLICY_CONTEXT_IDENTIFIED`

`download_gate_status = BLOCKED_BEFORE_DOWNLOAD`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

Reason:

Public source, citation path, and policy context are visible. However,
dataset-specific license/reuse terms, acknowledgement wording, file-level
download terms, and redistribution/commit policy remain unresolved.

## Recommendation For Manifest Update

Recommend later update to:

`data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`

Possible later fields:

- `data_use_review_status: DATA_USE_REVIEW_PARTIAL`
- `citation_policy_context_status: CITATION_POLICY_CONTEXT_IDENTIFIED`
- `data_use_or_license_note: manual_review_required; dataset-specific license/reuse note not yet resolved`
- `raw_data_tracking_status: BLOCKED_RAW_DATA_TRACKING`
- `download_allowed: false`
- `sidecar_population_allowed: false`
- `dry_run_preview_allowed: false`

But:

Do not update the manifest in SHAPIROINFO18 unless explicitly requested.
SHAPIROINFO18 is a note only.

## What Is Still Not Allowed

- no file download
- no opening linked data files
- no local raw data directory population
- no raw data commit
- no `.par` / `.tim` inspection
- no checksum calculation from files
- no correction-state sidecar population
- no adapter dry-run
- no residual preview

## Relation To SHAPIROINFO17

SHAPIROINFO17 updated the J0740 manifest with source/citation facts.
SHAPIROINFO18 reviews data-use and policy context but does not change the
manifest.

## Relation To SHAPIROINFO15

SHAPIROINFO15 created the blocked candidate-specific manifest draft.
SHAPIROINFO18 keeps download blocked.

## Befund

J0740+6620 has visible public source and citation context. A NANOGrav
publication-policy context is visible. Dataset-specific license/reuse and
acknowledgement details remain unresolved.

## Interpretation

The candidate remains suitable for cautious planning, but not yet for download
or raw-data handling.

## Hypothese

Separating citation identity from data-use/license review reduces the risk of
treating public visibility as automatic reuse permission.

## Offene Luecke

- no dataset-specific license/reuse statement resolved
- no acknowledgement wording finalized
- no file-level download terms inspected
- no data downloaded
- no raw data storage decision
- no checksum
- no `.par` parsed
- no `.tim` parsed
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
- no candidate residual claim from data-use review
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO19 J0740 Manifest Update After Data-Use Review
- SHAPIROINFO20 README / Release-Note Inspection Plan
- SHAPIROINFO21 Local Storage and Raw Data Policy Note
- SHAPIROINFO22 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO23 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- enthaelt DATA_USE_REVIEW_PARTIAL
- enthaelt CITATION_POLICY_CONTEXT_IDENTIFIED
- enthaelt BLOCKED_BEFORE_DOWNLOAD
- enthaelt BLOCKED_RAW_DATA_TRACKING
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DRY_RUN
- enthaelt NANOGrav Publication Policy
- enthaelt 10.1038/s41550-019-0880-2
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
