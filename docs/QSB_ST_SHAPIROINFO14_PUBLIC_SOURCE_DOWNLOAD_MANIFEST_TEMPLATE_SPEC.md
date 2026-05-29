# QSB-ST-SHAPIROINFO14 -- Public Source Download Manifest Template

## Current anchor

`1110646 Add QSB-ST ShapiroInfo J0740 source review`

## Purpose

SHAPIROINFO14 erzeugt ein YAML-Template fuer ein spaeteres oeffentliches
Quellen-/Download-Manifest.

Dieses Manifest ist Pflicht, bevor irgendein oeffentlicher Kandidatendatensatz
heruntergeladen, lokal abgelegt oder in einen Sidecar-Draft uebernommen wird.

Wichtig:

- Dieses Template ist kein Download-Manifest fuer einen echten Datensatz.
- Es enthaelt keine geprueften URLs, keine lokalen Dateien und keine
  Checksummen.
- Es ist standardmaessig blockierend.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO12_PUBLIC_SOURCE_AND_CITATION_CHECKLIST.md`
- `docs/QSB_ST_SHAPIROINFO13_CANDIDATE_SOURCE_REVIEW_J0740_6620.md`
- `docs/QSB_ST_SHAPIROINFO11_CORRECTION_STATE_SIDECAR_TEMPLATE_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO10_CORRECTION_STATE_FIELD_SCHEMA.md`

## Scope

- manifest template only
- no download
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Files Created By This Block

| path | role | status |
|---|---|---|
| `data/QSB-ST-SHAPIROINFO/public_source_download_manifest_template.yaml` | Empty public source/download manifest template. | created as template only |
| `docs/QSB_ST_SHAPIROINFO14_PUBLIC_SOURCE_DOWNLOAD_MANIFEST_TEMPLATE_SPEC.md` | Human-readable manifest-template specification. | created as spec only |

No run output, script, downloaded file, parsed timing file, checksum result, or
empirical result is created by SHAPIROINFO14.

## Manifest Rule

The manifest template is a blocker, not an authorization. It may be copied into
a dataset-specific manifest only after a future block explicitly authorizes
manual source review and local storage planning.

The template must not contain:

- checked source URLs
- real download URLs
- local data files
- checksums
- file sizes
- inspected `.par` content
- inspected `.tim` content
- populated dataset-specific sidecar fields

## Default Gate State

The template starts blocked:

- `manifest_status: template_blocked`
- `public_source_gate.gate_status: BLOCKED_BEFORE_DOWNLOAD`
- `download_plan.download_gate_status: BLOCKED_BEFORE_DOWNLOAD`
- `integrity_plan.integrity_gate_status: BLOCKED_BEFORE_DOWNLOAD`
- `downstream_gate.sidecar_gate_status: BLOCKED_BEFORE_SIDECAR_DRAFT`
- `downstream_gate.adapter_gate_status: BLOCKED_BEFORE_ADAPTER`

This is intentional. A blank manifest must not unlock a download, sidecar
population, adapter dry-run, or residual preview.

## Template Field Groups

The YAML template contains these groups:

- `candidate_context`
- `public_source_gate`
- `file_expectations`
- `download_plan`
- `local_storage_plan`
- `integrity_plan`
- `provenance_requirements`
- `downstream_gate`
- `claim_flags`

These groups are designed to make source, citation, data-use, file expectation,
storage, integrity, provenance, sidecar, and claim-boundary decisions visible
before any dataset contact.

## Required Blocking Fields

The following fields must be populated in a future dataset-specific manifest
before any download:

| field | default_template_value | required_before_download | note |
|---|---|---|---|
| `public_source_gate.source_page_url` | `manual_review_required` | yes | Must be reviewed; this template stores no checked URL. |
| `public_source_gate.dataset_or_release_name` | `unknown` | yes | Release identity must be explicit. |
| `public_source_gate.release_version_or_date` | `unknown` | yes | Version/date cannot remain implicit. |
| `public_source_gate.citation_reference` | `manual_review_required` | yes | Citation path must be auditable. |
| `public_source_gate.data_access_method` | `manual_review_required` | yes | Access method must be known before use. |
| `public_source_gate.data_use_or_license_note` | `manual_review_required` | yes | Data-use note must be checked before download. |
| `file_expectations.expected_timing_model_file` | review placeholders | yes | Expected `.par` or equivalent must be identified. |
| `file_expectations.expected_timing_observation_file` | review placeholders | yes | Expected `.tim` or equivalent must be identified. |
| `download_plan.no_download_until_gate_passed` | `true` | yes | Must remain true until gate passes. |
| `local_storage_plan.local_storage_root` | `manual_review_required` | yes | Local storage path must be planned before download. |
| `integrity_plan.checksum_or_integrity_plan` | `manual_review_required` | yes | Integrity plan must be explicit. |
| `provenance_requirements.provenance_manifest_required` | `true` | yes | Provenance manifest remains mandatory. |
| `provenance_requirements.correction_state_sidecar_required` | `true` | yes | Correction-State sidecar remains mandatory. |
| `provenance_requirements.window_definition_sidecar_required` | `true` | yes | Window/control sidecar remains mandatory. |

## Allowed Placeholder Values

The empty template may use:

- `manual_review_required`
- `unknown`
- `not_applicable`
- `template_blocked`
- `BLOCKED_BEFORE_DOWNLOAD`
- `BLOCKED_BEFORE_SIDECAR_DRAFT`
- `BLOCKED_BEFORE_ADAPTER`
- `manual_source_review_only`
- empty lists for URLs, download items, local files, checksums, and file sizes

These placeholders are not data. They are explicit stop markers.

## Relation To SHAPIROINFO13

SHAPIROINFO13 applied the source/citation gate to J0740+6620 at
source-review level only. It found that the public source and expected
timing/parameter files are identifiable, but download and sidecar gates remain
blocked.

SHAPIROINFO14 does not advance that candidate. It provides only a generic
manifest template needed before any later download-manifest draft.

## Relation To SHAPIROINFO12

SHAPIROINFO12 defined the source, citation, provenance, and usage checklist.
SHAPIROINFO14 gives that checklist a structured YAML target for later manual
review and download planning.

## Relation To SHAPIROINFO11/10

SHAPIROINFO10 defined the Correction-State field schema. SHAPIROINFO11 created
the empty Correction-State sidecar template. SHAPIROINFO14 sits upstream of a
dataset-specific sidecar draft: no dataset may move from public source review
into sidecar population without a filled and reviewed download/provenance
manifest.

## Befund

The repository now has an empty public source/download manifest template. It is
blocked by default and contains no checked URLs, no local files, and no
checksums.

## Interpretation

The template separates public-source review from actual data contact. It makes
source, citation, data-use, local storage, checksum, provenance, sidecar, and
window-definition requirements visible before a future download can be
considered.

## Hypothese

A strict manifest gate may reduce later replay and interpretation risk by
requiring source identity, citation, data-use, storage, and integrity planning
before public timing files are touched.

## Offene Luecke

- no download
- no checked source URL in the template
- no real download URL in the template
- no local data file path populated
- no checksum populated
- no file size recorded
- no `.par` inspected
- no `.tim` inspected
- no Correction-State sidecar populated for a dataset
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
- no candidate residual claim from manifest template creation
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO14A J0740+6620 Manual Source Review Checklist
- SHAPIROINFO15 J0740+6620 Download Manifest Draft for Manual Review Only
- SHAPIROINFO16 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO17 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei `data/QSB-ST-SHAPIROINFO/public_source_download_manifest_template.yaml`
  existiert
- Datei `docs/QSB_ST_SHAPIROINFO14_PUBLIC_SOURCE_DOWNLOAD_MANIFEST_TEMPLATE_SPEC.md`
  existiert
- Manifest enthaelt `manifest_schema_version`
- Manifest enthaelt `BLOCKED_BEFORE_DOWNLOAD`
- Manifest enthaelt `BLOCKED_BEFORE_SIDECAR_DRAFT`
- Manifest enthaelt `no_download_until_gate_passed`
- Manifest enthaelt `source_urls_checked: []`
- Manifest enthaelt `downloaded_files: []`
- Manifest enthaelt `local_files: []`
- Manifest enthaelt `expected_checksums: []`
- Spec enthaelt keine geprueften URLs, keine lokalen Dateien und keine
  Checksummen
- Spec enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
