# QSB-ST-SHAPIROINFO13 -- Candidate Source Review for J0740+6620

## Current anchor

`dd2f8af Add QSB-ST ShapiroInfo public source and citation checklist`

## Purpose

SHAPIROINFO13 prueft, ob J0740+6620 als Kandidat die
Quellen-/Zitier-Gate-Anforderungen aus SHAPIROINFO12 grundsaetzlich erfuellen
koennte.

Dies ist eine erste Quellenpruefung fuer den bevorzugten
Targeted-Binary-Pulsar-Kandidaten J0740+6620. Dieser Block prueft nur
oeffentliche Quelle, Zitierpfad, Dateierwartung und Gate-Status. Er laedt keine
Daten und wertet nichts aus.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO09_TARGETED_BINARY_PULSAR_PILOT_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO10_CORRECTION_STATE_FIELD_SCHEMA.md`
- `docs/QSB_ST_SHAPIROINFO11_CORRECTION_STATE_SIDECAR_TEMPLATE_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO12_PUBLIC_SOURCE_AND_CITATION_CHECKLIST.md`

## Scope

- source review only
- no download
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Reviewed Public Source

Quelle:

NANOGrav page:
Timing Data for the Binary Parameters of J0740+6620

Source URL:

`https://nanograv.org/science/data/timing-data-binary-parameters-j07406620`

Source status:

public source page identified

Observed source claims from page:

- public release page exists
- downloads are listed for:
  - J0740+6620 timing data
  - J0740+6620 parameter file
- reference listed:
  H. T. Cromartie et al.,
  "Relativistic Shapiro delay measurements of an extremely massive millisecond
  pulsar",
  Nature Astronomy 4, 72 (2020)

Important:

- Do not download the linked files in this block.
- Do not mark file contents as inspected.

## Supporting NANOGrav Data Index Note

Quelle:

NANOGrav Data page:

`https://nanograv.org/science/data`

Observed:

The J0740+6620 release is described as TEMPO/TEMPO2-compatible timing data for
Cromartie et al. 2020.

Important:

- This supports file-format expectation only.
- It does not prove local compatibility.
- It does not replace actual future file inspection.

## Candidate Checklist Status Table

| checklist_item | observed_status | evidence | gate_status | blocking_if_not_resolved | notes |
|---|---|---|---|---|---|
| `source_page_url` | `known_documented` | NANOGrav public release page | `pass_for_source_review` | yes | Source URL is identified; no file links were downloaded. |
| `dataset_or_release_name` | `known_documented` | Timing Data for the Binary Parameters of J0740+6620 | `pass_for_source_review` | yes | Release/page name is visible. |
| `release_version_or_date` | `known_but_needs_review` | Page references Cromartie et al. 2020; exact dataset release metadata still needs manual review | `needs_manual_review` | yes | Date/version must be recorded before sidecar draft. |
| `citation_reference` | `known_documented` | Cromartie et al. 2020 Nature Astronomy reference listed on source page | `pass_for_source_review` | yes | Citation path exists at source-review level. |
| `doi_or_stable_identifier` | `manual_review_required` | no DOI confirmed locally in this block | `needs_manual_review` | yes if required by future manifest | No DOI is asserted here. |
| `data_access_method` | `known_documented` | NANOGrav page lists download entries | `pass_for_source_review` | yes | Access entries exist; they were not used. |
| `data_use_or_license_note` | `manual_review_required` | not reviewed in this block | `blocking_before_download` | yes | Data-use and citation-use notes must be checked first. |
| `expected_timing_model_file` | `known_documented` | Page lists J0740+6620 parameter file | `pass_for_source_review` | yes | File content was not inspected. |
| `expected_timing_observation_file` | `known_documented` | Page lists J0740+6620 timing data | `pass_for_source_review` | yes | File content was not inspected. |
| `expected_readme_or_release_notes` | `manual_review_required` | not inspected | `needs_manual_review` | yes | README/release-note context remains open. |
| `expected_clock_or_ephemeris_context` | `unknown` | not inspected | `blocking_before_sidecar` | yes | Clock and ephemeris state remain unresolved. |
| `expected_noise_or_correction_context` | `unknown` | not inspected | `blocking_before_sidecar` | yes | Noise, DM/ISM, backend, and correction context remain unresolved. |
| `file_format_expectation` | `known_but_needs_review` | NANOGrav data index describes TEMPO/TEMPO2-compatible timing data | `needs_manual_review` | yes | Supports expectation only; local compatibility is not checked. |
| `local_storage_plan` | `manual_review_required` | not defined in this block | `blocking_before_download` | yes | No local data path is created or approved. |
| `checksum_or_integrity_plan` | `manual_review_required` | not defined in this block | `blocking_before_download` | yes | Integrity plan must precede download. |
| `provenance_manifest_required` | `known_documented` | SHAPIROINFO12 rule | `required` | yes | Manifest is required before tracked data use. |
| `correction_state_sidecar_required` | `known_documented` | SHAPIROINFO10/11 rule | `required` | yes | Sidecar is mandatory before adapter use. |
| `window_definition_sidecar_required` | `known_documented` | SHAPIROINFO09/12 rule | `required` | yes | A/B/control windows must be specified later. |
| `manual_review_required_before_download` | `known_documented` | SHAPIROINFO12 rule | `required` | yes | Manual gate remains active. |
| `no_download_until_gate_passed` | `known_documented` | SHAPIROINFO12 rule | `required` | yes | Download remains blocked. |

## Gate Decision

`candidate_source_review_status = PASS_FOR_SOURCE_REVIEW_ONLY`

But:

- `download_gate_status = BLOCKED_BEFORE_DOWNLOAD`
- `sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

Reason:

The public source and expected timing/parameter files are identifiable, but
data-use note, release details, clock/ephemeris/correction context, local
storage plan, checksum plan, and provenance manifest are not yet populated.

## What Is Allowed Next

Allowed next block:

- SHAPIROINFO14 Public Source Download Manifest Template

or:

- SHAPIROINFO14A J0740+6620 Manual Source Review Checklist

Not yet allowed:

- file download
- `.par` / `.tim` inspection
- sidecar population as dataset-specific
- adapter dry-run
- residual preview

## Relation To SHAPIROINFO12

SHAPIROINFO12 defined the public source and citation gate. SHAPIROINFO13
applies that gate to the J0740+6620 candidate at source-review level only.

## Relation To SHAPIROINFO11

SHAPIROINFO11 created the correction-state sidecar template. SHAPIROINFO13
does not populate that template yet because required source/correction fields
remain unresolved.

## Befund

A public NANOGrav source page for J0740+6620 exists and lists timing data plus
a parameter file. The release is associated with Cromartie et al. 2020 and
TEMPO/TEMPO2-compatible timing data according to NANOGrav's data pages.

## Interpretation

J0740+6620 remains a suitable first candidate for the targeted binary pulsar
pilot path, but only at source-review level. The candidate is not yet cleared
for download or sidecar population.

## Hypothese

A narrowly controlled J0740+6620 pilot may become feasible after data-use
notes, provenance manifest, release details, correction-state context, and
local storage/checksum plan are explicitly defined.

## Offene Luecke

- no download
- no file inspection
- no `.par` parsed
- no `.tim` parsed
- no clock state inspected
- no ephemeris state inspected
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

- SHAPIROINFO14 Public Source Download Manifest Template
- SHAPIROINFO14A J0740+6620 Manual Source Review Checklist
- SHAPIROINFO15 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO16 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- enthaelt NANOGrav J0740+6620
- enthaelt Timing Data for the Binary Parameters of J0740+6620
- enthaelt Cromartie et al. 2020
- enthaelt J0740+6620 timing data
- enthaelt J0740+6620 parameter file
- enthaelt PASS_FOR_SOURCE_REVIEW_ONLY
- enthaelt BLOCKED_BEFORE_DOWNLOAD
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
