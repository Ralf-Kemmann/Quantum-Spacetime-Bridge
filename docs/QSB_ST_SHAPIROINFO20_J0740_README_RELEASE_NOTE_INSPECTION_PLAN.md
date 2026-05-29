# QSB-ST-SHAPIROINFO20 -- J0740 README / Release-Note Inspection Plan

## Current anchor

`a25ccac Update QSB-ST ShapiroInfo J0740 manifest after data-use review`

## Purpose

SHAPIROINFO20 definiert, welche README-/Release-Note-/Link-Level-Informationen
vor einem spaeteren kontrollierten Datei-Zugriff geprueft werden muessen.

SHAPIROINFO20 plant die spaetere Pruefung von README-, Release-Note-,
Source-Page-, Link-Level- und Datei-Kontextinformationen fuer J0740+6620.
Dieser Block inspiziert noch keine Dateien und oeffnet keine Download-,
Sidecar- oder Dry-run-Gates.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO18_J0740_DATA_USE_AND_LICENSE_REVIEW_NOTE.md`
- `docs/QSB_ST_SHAPIROINFO19_J0740_MANIFEST_UPDATE_AFTER_DATA_USE_REVIEW.md`
- `docs/QSB_ST_SHAPIROINFO17_J0740_DOWNLOAD_MANIFEST_UPDATE_AFTER_SOURCE_REVIEW.md`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`

## Scope

- inspection plan only
- no download
- no opening linked data files
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Gate Principle

README and release-note inspection is a pre-download context gate.
It does not authorize download.
It only defines what must be checked before download can even be reconsidered.

Der Tuersteher liest noch nicht die Tasche aus. Er prueft zuerst, ob es
ueberhaupt eine Packliste, Nutzungsnotiz, Release-Identitaet und
Kontextbeschreibung gibt.

## Candidate Context

- Candidate: NANOGrav J0740+6620
- Source page already identified in SHAPIROINFO13
- Source/citation reviewed in SHAPIROINFO16
- Data-use/policy context reviewed in SHAPIROINFO18
- Manifest updated through SHAPIROINFO19
- Current gates remain closed:
  - `download_allowed: false`
  - `raw_data_tracking_allowed: false`
  - `raw_data_commit_allowed: false`
  - `sidecar_population_allowed: false`
  - `dry_run_preview_allowed: false`

## Inspection Target Classes

| inspection_target | what_to_check | expected_evidence | blocking_if_missing | note |
|---|---|---|---|---|
| `source_page_text` | Public source-page text and visible release framing. | Stable page text or archived citation note. | yes | Page visibility is context only. |
| `download_link_labels` | Whether link labels identify timing data and parameter file clearly. | Link labels visible without opening linked data files. | yes | Labels are not file inspection. |
| `parameter_file_link_context` | Context around the parameter-file link. | Label, nearby text, format hints, warnings. | yes | Do not open the linked parameter file in this plan. |
| `timing_data_link_context` | Context around the timing-data link. | Label, nearby text, format hints, warnings. | yes | Do not open the linked timing data in this plan. |
| `readme_or_release_notes` | Whether README or release-note text/page exists. | README page, release note page, or explicit absence. | yes | README/Release-Note context is required before data contact. |
| `citation_or_acknowledgement_text` | Required citation or acknowledgement wording. | Source-page, README, release-note, or policy text. | yes | Exact wording must be captured later. |
| `data_use_or_license_text` | Dataset-specific use, license, or reuse text. | License note, data-use note, or explicit missing state. | yes | Public page alone is not enough. |
| `file_format_notes` | File format descriptions. | `.par`, `.tim`, TEMPO/TEMPO2, or equivalent notes. | yes | Format expectation remains pre-download. |
| `tempo_tempo2_compatibility_note` | TEMPO/TEMPO2 compatibility statement. | Source page, README, data page, or release note. | yes | Supports format expectation only. |
| `clock_timescale_context` | Time standards and clock correction context. | README/release-note/source-page text. | yes | Needed before Correction-State sidecar. |
| `ephemeris_context` | Solar-system ephemeris or barycentering context. | README/release-note/source-page text. | yes | Needed before Correction-State sidecar. |
| `binary_model_context` | Binary timing model context. | README, release note, parameter context, or paper context. | yes | No model parsing in this plan. |
| `dm_ism_context` | DM/ISM or chromatic correction context. | README/release-note/source-page text. | yes | Unknown remains blocking. |
| `noise_model_context` | Noise model context or explicit absence. | README/release-note/source-page text. | yes | Needed before comparator planning. |
| `backend_or_observatory_flags_context` | Backend, receiver, observatory, or flag context. | README/release-note/source-page text. | yes | Needed before window/control planning. |
| `quality_flags_or_exclusions_context` | QC, outlier, exclusion, or flag rules. | README/release-note/source-page text. | yes | Hidden exclusions are not acceptable. |
| `version_or_date_context` | Release date, version, or file date context. | Source page, README, release note, or manifest note. | yes | Needed before any manifest pass. |
| `contact_or_project_policy_context` | Project policy, contact, citation, or publication-policy context. | NANOGrav policy page or source-page policy text. | yes | Policy context does not authorize download by itself. |

## Specific Inspection Questions

Allowed statuses:

- `planned`
- `reviewed_known_documented`
- `reviewed_missing`
- `unknown`
- `manual_review_required`
- `blocking_missing`
- `not_applicable`

| question_id | question | required_before | possible_status | blocking_effect |
|---|---|---|---|---|
| `Q01` | Is the source page still publicly reachable? | Any manifest update. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing page blocks download reconsideration. |
| `Q02` | Are timing data and parameter file links clearly labeled? | Download-manifest update. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Ambiguous links block file contact. |
| `Q03` | Is there a README or release-note file/page? | Data-contact decision. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing documentation blocks sidecar population. |
| `Q04` | Is the release version/date explicit? | Download-manifest update. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing release identity blocks download reconsideration. |
| `Q05` | Is the citation requirement explicit? | Download-manifest update. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing citation wording blocks download reconsideration. |
| `Q06` | Is acknowledgement wording explicit? | Download-manifest update. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing acknowledgement context blocks raw-data handling. |
| `Q07` | Is data-use/license text explicit? | Download gate. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing use/license text keeps download blocked. |
| `Q08` | Is redistribution or raw-data tracking allowed, discouraged, or unclear? | Raw-data policy decision. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Unclear redistribution keeps raw tracking blocked. |
| `Q09` | Are file formats described as `.par`, `.tim`, TEMPO/TEMPO2, or equivalent? | Download-manifest update. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing format notes block `.par`/`.tim` assumptions. |
| `Q10` | Are time standards / clock corrections described? | Correction-State sidecar draft. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing clock context blocks sidecar population. |
| `Q11` | Is the solar-system ephemeris context described? | Correction-State sidecar draft. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing ephemeris context blocks sidecar population. |
| `Q12` | Is the binary timing model context described? | Correction-State sidecar draft. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing binary model context blocks sidecar population. |
| `Q13` | Are DM/ISM or chromatic corrections described? | Correction-State sidecar draft. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing DM/ISM context blocks sidecar population. |
| `Q14` | Is noise-model context described? | Correction-State sidecar draft. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing noise context blocks sidecar population. |
| `Q15` | Are backend/instrument flags described? | Correction-State sidecar draft. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing backend context blocks controls. |
| `Q16` | Are QC/outlier/exclusion rules described? | Correction-State sidecar draft. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing | Missing QC context blocks sidecar population. |
| `Q17` | Can a Correction-State sidecar be populated after inspection? | Sidecar draft decision. | planned / reviewed_known_documented / reviewed_missing / unknown / manual_review_required / blocking_missing / not_applicable | If no, sidecar remains blocked. |
| `Q18` | Is download still blocked until manifest update? | Any data contact. | planned / reviewed_known_documented / manual_review_required / blocking_missing | Must remain blocked until a later manifest update. |

## Gate Statuses After SHAPIROINFO20

`readme_release_inspection_plan_status = INSPECTION_PLAN_DEFINED`

`download_gate_status = BLOCKED_BEFORE_DOWNLOAD`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

## What SHAPIROINFO20 May Allow Later

Only a later block may perform controlled inspection of public source-page or
README/release-note text.

Even then:

- no raw timing-data download unless separate gate passes
- no `.par` / `.tim` parsing
- no adapter dry-run
- no residual preview

## What Remains Blocked

- file download
- opening linked timing data or parameter file as data
- local raw data directory population
- checksum calculation from downloaded files
- raw data tracking
- correction-state sidecar population
- adapter dry-run
- residual preview

## Relation To SHAPIROINFO19

SHAPIROINFO19 updated the J0740 manifest after data-use review. SHAPIROINFO20
defines the next inspection plan before any further manifest update.

## Relation To SHAPIROINFO18

SHAPIROINFO18 identified policy/data-use context as partial. SHAPIROINFO20
turns the remaining unknowns into an inspection checklist.

## Befund

The project now requires a README/release-note inspection plan before
considering any controlled download gate.

## Interpretation

This separates public-source visibility from file-level interpretability and
usage conditions.

## Hypothese

A formal inspection plan reduces the risk that file format, correction context,
release state, or reuse conditions are silently assumed.

## Offene Luecke

- no README inspected
- no release notes inspected
- no file opened
- no download
- no `.par` parsed
- no `.tim` parsed
- no clock/ephemeris state confirmed
- no noise/correction context confirmed
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
- no candidate residual claim from inspection planning
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO21 README / Release-Note Inspection Result
- SHAPIROINFO22 Local Storage and Raw Data Policy Note
- SHAPIROINFO23 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO24 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- enthaelt INSPECTION_PLAN_DEFINED
- enthaelt BLOCKED_BEFORE_DOWNLOAD
- enthaelt BLOCKED_RAW_DATA_TRACKING
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DRY_RUN
- enthaelt README
- enthaelt Release-Note
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
