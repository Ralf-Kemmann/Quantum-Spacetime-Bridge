# QSB-ST-SHAPIROINFO28 -- File-Link Metadata Review Plan

## Current Anchor

`c8cc382 Add QSB-ST ShapiroInfo gate checker negative test result note`

## Purpose

SHAPIROINFO28 definiert, welche Link- und HTTP-/Dateimetadaten spaeter vor
einem moeglichen Download-Gate geprueft werden koennten. Ziel ist,
Dateikontakt reproduzierbar und begrenzt vorzubereiten, ohne Dateiinhalt als
Daten zu verarbeiten.

Dieser Block ist ein Plan, kein Download und keine Dateiinhalt-Inspektion.

## Scope

- file-link metadata review plan only
- no download
- no file body retrieval
- no linked timing-data file opened
- no linked parameter file opened
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Key Distinction

File-link metadata is not data ingestion.
A later metadata review may inspect link target metadata, headers, filenames,
sizes, timestamps, and source-page linkage.
It must not parse timing data, parameter values, TOAs, residuals, or scientific
content.

Deutsch:
Der Tuersteher prueft noch nicht den Tascheninhalt. Er prueft hoechstens das
Etikett, die Paketgroesse, den Absender und ob das Paket ueberhaupt eindeutig
adressiert ist.

## Candidate Context

- Candidate: NANOGrav J0740+6620
- Source page identified
- Link labels identified:
  - J0740+6620 timing data
  - J0740+6620 parameter file
- TEMPO/TEMPO2-compatible context seen at source-page level
- File-level documentation unresolved
- Data-use/license unresolved
- Correction context unresolved
- Gate checker exists and has positive and negative tests

## Planned Metadata Classes

| metadata_class | planned_check | allowed_method_later | forbidden_boundary | gate_effect |
|---|---|---|---|---|
| `source_page_link_target` | confirm source-page relationship to target | source-page text/link review | no file body retrieval | context only |
| `download_url_or_href` | record URL or href target | browser-visible copy or HEAD request if server supports it | no GET body download | context only |
| `filename_from_link` | record visible or suggested filename | source-page/link metadata | no file save | context only |
| `file_extension` | record extension expectation | link target string or headers | no `.par` / `.tim` parsing | context only |
| `content_type_header` | record HTTP content type | HEAD request if server supports it | no body read | context only |
| `content_length_header` | record HTTP size header | HEAD request if server supports it | no body read | context only |
| `last_modified_header` | record HTTP timestamp header | HEAD request if server supports it | no body read | context only |
| `etag_header` | record entity tag if provided | HEAD request if server supports it | no body read | context only |
| `checksum_if_provided_by_source` | record source-provided checksum only | source-page or metadata text | no checksum from downloaded raw file | context only |
| `release_date_or_page_timestamp` | record page or release timestamp | source-page review | no file inspection | context only |
| `redirect_chain` | record redirects if visible by metadata method | HEAD request with redirect reporting | no body save | context only |
| `http_status_code` | record status code | HEAD request if server supports it | no body read | context only |
| `manual_browser_visible_label` | record visible link label | browser-visible page review | no linked file opened | context only |
| `citation_or_acknowledgement_linkage` | record citation/acknowledgement link context | source-page review | no data interpretation | context only |
| `license_or_usage_linkage` | record license/use context link | source-page review | no reuse authorization implied | keeps gate blocked |
| `local_planned_path` | propose later local target path | manifest planning | no directory creation here | planning only |
| `retrieval_command_preview` | draft later command shape | command preview text | no execution here | planning only |

## Allowed Later Methods

Spaetere, noch nicht ausgefuehrte Moeglichkeiten:

- HEAD request if server supports it
- curl `--head` or equivalent
- browser-visible link target copying
- recording URL without downloading file body
- recording filename suggested by source
- recording source-page context
- no file body save
- no parsing
- no checksum from downloaded file unless download gate later passes

Diese Methoden werden in SHAPIROINFO28 nicht ausgefuehrt.

## Forbidden In Metadata Review

- no GET body download
- no saving `.par`
- no saving `.tim`
- no opening downloaded file
- no reading TOAs
- no reading timing model parameters
- no extracting DM / ephemeris / backend data from files
- no checksum from downloaded raw file
- no sidecar population from file contents
- no adapter run
- no residual calculation

## Planned Metadata Record Fields

| field_name | field_type | field_description | required_for_download_gate | claim_boundary_note |
|---|---|---|---|---|
| `source_page_url` | string | Public source page that exposes the link label. | yes | Source context only. |
| `link_label` | string | Human-visible link label from source page. | yes | Label is not file content. |
| `link_target_url` | string | Link target URL or href recorded without body retrieval. | yes | URL does not imply permission. |
| `link_target_review_status` | enum string | Review state for target metadata. | yes | Status only. |
| `http_status_code` | integer or unknown | Status code from allowed later metadata request. | yes if request performed | Not data content. |
| `content_type` | string or unknown | HTTP content-type metadata. | yes if available | Not format validation. |
| `content_length_bytes` | integer or unknown | HTTP size metadata. | yes if available | Size is not evidence. |
| `last_modified` | string or unknown | HTTP last-modified metadata. | optional | Timestamp only. |
| `etag` | string or unknown | HTTP ETag metadata. | optional | Identifier only. |
| `source_provided_checksum` | string or unknown | Checksum provided by source, not computed from downloaded file. | optional | No raw-file checksum here. |
| `filename` | string or unknown | Filename suggested by link or header. | yes | Filename is not content. |
| `file_extension` | string or unknown | Extension expectation, e.g. `.par` or `.tim`. | yes | No parsing follows. |
| `expected_file_role` | enum string | Expected role such as timing data or parameter file. | yes | Role expectation only. |
| `expected_format_family` | enum string | Expected family such as TEMPO/TEMPO2-compatible. | yes | Compatibility not proven. |
| `redirect_chain_recorded` | boolean | Whether redirect metadata was recorded. | yes if redirects occur | No body retrieval. |
| `retrieval_method_planned` | string | Planned future metadata method. | yes | No execution here. |
| `local_target_path_planned` | string | Planned local raw/quarantine path if later allowed. | yes | No directory creation here. |
| `metadata_review_timestamp_utc` | string | Future review timestamp. | yes when performed | Review audit only. |
| `reviewer_note` | string | Manual boundary and caveat note. | yes | No scientific claim. |
| `download_allowed_after_metadata_review` | boolean | Whether metadata review alone opens download. | yes | Must remain false unless separate gate decides otherwise. |

`download_allowed_after_metadata_review` bleibt `false`, ausser spaeter ein
separater Download-Gate-Block entscheidet anders.

## Gate Statuses After SHAPIROINFO28

`file_link_metadata_plan_status = FILE_LINK_METADATA_PLAN_DEFINED`

`download_gate_status = BLOCKED_BEFORE_DOWNLOAD`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

## Relation To Gate Checker

Der Gate-Checker aus SHAPIROINFO24B/25/26B bleibt vor jedem spaeteren
Datenkontakt relevant. Ein spaeterer Metadata Review darf nur weitergehen,
wenn der Checker nicht versehentlich ein geoeffnetes Gate oder eine
Claim-Flag-Verletzung meldet.

## Relation To SHAPIROINFO23

SHAPIROINFO23 definierte lokale Speicher- und Rohdatenpolitik. SHAPIROINFO28
plant, welche Link-Metadaten spaeter vor einem Download-Gate dokumentiert
werden muessten.

## Befund

Das Projekt hat nun einen geprueften Gate-Checker und plant den naechsten engen
Schritt: File-Link-Metadaten, nicht Dateninhalt.

## Interpretation

Metadata review kann helfen, einen spaeteren Download reproduzierbar
vorzubereiten, ohne die Grenze zur Datenverarbeitung zu ueberschreiten.

## Hypothese

Ein sauberer Link-Metadatenplan reduziert das Risiko, dass spaetere Downloads
unklar, unreproduzierbar oder lizenz-/provenance-seitig unsauber erfolgen.

## Offene Luecke

- no metadata request executed
- no link target inspected by HTTP
- no file downloaded
- no file body opened
- no `.par` parsed
- no `.tim` parsed
- no checksum from downloaded file
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
- no candidate residual claim from metadata planning
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO29 File-Link Metadata Review Result
- SHAPIROINFO30 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO31 Targeted Binary Pulsar Dry-Run Adapter Spec
- SHAPIROINFO32 Controlled Download Gate Decision

## Acceptance Checks

- Datei existiert
- enthaelt FILE_LINK_METADATA_PLAN_DEFINED
- enthaelt BLOCKED_BEFORE_DOWNLOAD
- enthaelt BLOCKED_RAW_DATA_TRACKING
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DRY_RUN
- enthaelt HEAD request
- enthaelt no GET body download
- enthaelt no file body opened
- enthaelt download_allowed_after_metadata_review
- enthaelt field_name
- enthaelt field_type
- enthaelt field_description
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
