# QSB-ST-SHAPIROINFO16 -- J0740+6620 Manual Source Review Result

## Current anchor

`b46a8a2 Add QSB-ST ShapiroInfo J0740 download manifest draft`

## Purpose

SHAPIROINFO16 prueft, ob der J0740+6620-Kandidat fuer einen spaeteren
Download-Manifest-Update grundsaetzlich quellen- und zitierfaehig genug ist.
Es ist kein Download-Block.

Dieser Block dokumentiert das Ergebnis einer manuellen Quellenpruefung fuer
den Kandidaten J0740+6620. Er bewertet nur oeffentliche Quellen-, Zitier- und
Dateierwartungsinformationen. Er laedt keine Daten und inspiziert keine
Dateien.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO13_CANDIDATE_SOURCE_REVIEW_J0740_6620.md`
- `docs/QSB_ST_SHAPIROINFO15_J0740_DOWNLOAD_MANIFEST_DRAFT_SPEC.md`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`
- `docs/QSB_ST_SHAPIROINFO12_PUBLIC_SOURCE_AND_CITATION_CHECKLIST.md`
- `docs/QSB_ST_SHAPIROINFO14_PUBLIC_SOURCE_DOWNLOAD_MANIFEST_TEMPLATE_SPEC.md`

## Scope

- manual source review result only
- no download
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Reviewed Sources

Quelle 1:

NANOGrav Data page

URL:

`https://nanograv.org/science/data`

Observed:

- lists "Timing Data for the Binary Parameters of J0740+6620"
- describes it as TEMPO/TEMPO2-compatible timing data for Cromartie et al. 2020
- supports file-format expectation only

Quelle 2:

NANOGrav J0740+6620 source page

URL:

`https://nanograv.org/science/data/timing-data-binary-parameters-j07406620`

Observed from SHAPIROINFO13:

- source page identified
- lists J0740+6620 timing data
- lists J0740+6620 parameter file
- references Cromartie et al. 2020

Quelle 3:

Nature Astronomy paper page

Title:

Relativistic Shapiro delay measurements of an extremely massive millisecond
pulsar

Authors:

H. T. Cromartie et al.

Journal:

Nature Astronomy 4, 72-76 (2020)

DOI:

10.1038/s41550-019-0880-2

Observed:

- publication exists
- article title and DOI identified
- content context: Shapiro-delay-based mass measurement for MSP J0740+6620
- used here only as citation/source context, not as project evidence

Optional supporting source:

arXiv 1904.06759

Title:

Relativistic Shapiro delay measurements of an extremely massive millisecond
pulsar

Use:

bibliographic/context support only, not dataset ingestion.

## Manual Review Result Table

| review_item | status | evidence | remaining_blocker | gate_effect | notes |
|---|---|---|---|---|---|
| `source_page_url` | `reviewed_known_documented` | NANOGrav J0740 source page URL | none for source identification | source gate can pass | Public page identity is reviewable. |
| `dataset_or_release_name` | `reviewed_known_documented` | Timing Data for the Binary Parameters of J0740+6620 | exact downloadable file metadata still not inspected | source review pass only | Dataset/page name is visible; file contents are not inspected. |
| `citation_reference` | `reviewed_known_documented` | Cromartie et al. 2020, Nature Astronomy 4, 72-76 | none for citation identity | citation gate can pass | Citation identity is sufficient for source review. |
| `doi_or_stable_identifier` | `reviewed_known_documented` | DOI 10.1038/s41550-019-0880-2 | dataset-specific DOI/identifier still unknown | paper DOI pass; dataset identifier still manual | Paper DOI is not a dataset checksum or release identifier. |
| `data_access_method` | `reviewed_known_documented` | NANOGrav page lists downloadable timing data and parameter file | file links not downloaded or inspected | access method pass for review only | Access entries were observed only as page facts. |
| `data_use_or_license_note` | `manual_review_required` | not reviewed | data-use/license/citation terms need explicit review before download | download remains blocked | Must be resolved before any file contact. |
| `expected_timing_model_file` | `reviewed_known_documented` | J0740+6620 parameter file listed | file not downloaded or inspected | expected file gate pass only | Expected `.par`-like file remains uninspected. |
| `expected_timing_observation_file` | `reviewed_known_documented` | J0740+6620 timing data listed | file not downloaded or inspected | expected file gate pass only | Expected `.tim`-like file remains uninspected. |
| `expected_readme_or_release_notes` | `manual_review_required` | not inspected | release notes/README availability not checked | sidecar remains blocked | Documentation context remains unresolved. |
| `expected_clock_or_ephemeris_context` | `unknown` | not inspected | required before correction-state sidecar | sidecar remains blocked | Clock/ephemeris state is still opaque. |
| `expected_noise_or_correction_context` | `unknown` | not inspected | required before correction-state sidecar | sidecar remains blocked | Noise/correction state is still opaque. |
| `local_storage_plan` | `planned_not_executed` | SHAPIROINFO15 manifest draft planned local path placeholders | no real directory populated, no download decision | download remains blocked | No concrete local storage path is populated. |
| `checksum_or_integrity_plan` | `planned_not_executed` | SHAPIROINFO15 manifest draft requires sha256/integrity planning | no file downloaded, no checksum possible | download remains blocked | Checksum plan exists only as future requirement. |
| `manual_review_required_before_download` | `still_required` | SHAPIROINFO12/15 gate | data-use, release notes, integrity, and correction context unresolved | BLOCKED_BEFORE_DOWNLOAD | Manual review remains active. |

## Gate Decision

`source_review_result = SOURCE_REVIEW_PARTIAL_PASS`

`citation_gate_status = CITATION_IDENTITY_PASS`

`download_gate_status = BLOCKED_BEFORE_DOWNLOAD`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

Reason:

Public source, candidate identity, expected timing data, expected parameter
file, and paper citation are identifiable. However, data-use/licensing note,
README/release-note content, clock/ephemeris context, noise/correction context,
actual file metadata, local retrieval, checksum, and sidecar population remain
unresolved.

## Update Recommendation For SHAPIROINFO15 Manifest

Recommend later manifest update, but not in this block:

- `source_page_url` can move from `manual_review_required` to
  `reviewed_known_documented`
- `citation_reference` can move to `reviewed_known_documented`
- `doi_or_stable_identifier` can include paper DOI
- `expected_timing_model_file` can remain expected yes, not downloaded
- `expected_timing_observation_file` can remain expected yes, not downloaded
- `download_allowed` remains false
- `sidecar_population_allowed` remains false
- `dry_run_preview_allowed` remains false

## What Is Still Not Allowed

- no file download
- no local raw data directory population
- no `.par` / `.tim` inspection
- no checksum calculation from files
- no correction-state sidecar population
- no adapter dry-run
- no residual preview

## Relation To SHAPIROINFO15

SHAPIROINFO15 created the candidate-specific download manifest draft.
SHAPIROINFO16 reviews source/citation identity and recommends which fields may
later be updated, but does not update the manifest itself.

## Relation To SHAPIROINFO13

SHAPIROINFO13 identified the candidate source page. SHAPIROINFO16 adds
manual-review result status and paper DOI context.

## Relation To SHAPIROINFO12

SHAPIROINFO12 defined the source/citation checklist. SHAPIROINFO16 applies
that checklist to the J0740 candidate at manual-review-result level.

## Befund

The candidate has a public NANOGrav source context and a clear bibliographic
paper citation. It remains blocked before download and before sidecar
population.

## Interpretation

J0740+6620 remains a suitable first candidate for a later targeted binary
pulsar dry-run path, but not yet for data ingestion.

## Hypothese

After a later data-use/license review and README/file-link inspection, the
manifest could be updated for a controlled download step while keeping sidecar
and dry-run gates closed.

## Offene Luecke

- no data-use/license note reviewed
- no README/release notes inspected
- no file downloaded
- no file metadata recorded
- no checksums computed
- no `.par` parsed
- no `.tim` parsed
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
- no candidate residual claim from source review
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO17 J0740 Download Manifest Update After Source Review
- SHAPIROINFO18 Data-Use and License Review Note
- SHAPIROINFO19 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO20 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- enthaelt SOURCE_REVIEW_PARTIAL_PASS
- enthaelt CITATION_IDENTITY_PASS
- enthaelt BLOCKED_BEFORE_DOWNLOAD
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DRY_RUN
- enthaelt DOI 10.1038/s41550-019-0880-2
- enthaelt Timing Data for the Binary Parameters of J0740+6620
- enthaelt J0740+6620 timing data
- enthaelt J0740+6620 parameter file
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
