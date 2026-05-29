# QSB-ST-SHAPIROINFO09 -- Targeted Binary Pulsar Pilot Plan

## Current anchor

`632539e Add QSB-ST ShapiroInfo toy-to-semi-real adapter plan`

## Purpose

SHAPIROINFO09 konkretisiert den ersten moeglichen halb-realen Pilotpfad nach
SHAPIROINFO08. Ziel ist ein enger, kontrollierter Binary-Pulsar-Pilot mit
`.par`/`.tim`-nahen Eingaben, Correction-State-Sidecar und defensiven
A/B-/Kontrollfenstern.

Dieser Block plant nur. Er laedt keine Daten, analysiert keine Daten und
erzeugt keine Residualsuche.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO03_TOY_COMPARATOR_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO04_TOY_COMPARATOR_MINIMAL_RUNNER_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO05_TOY_COMPARATOR_RESULT_NOTE.md`
- `docs/QSB_ST_SHAPIROINFO06_DATA_AND_SCENARIO_INVENTORY_NOTE.md`
- `docs/QSB_ST_SHAPIROINFO07_PUBLIC_DATASET_FEASIBILITY_MATRIX_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO08_TOY_TO_SEMI_REAL_ADAPTER_PLAN.md`

## Scope

- pilot plan only
- no data download
- no `.par` / `.tim` ingestion yet
- no PINT / tempo2 execution
- no residual calculation
- no empirical result
- no Bridge claim
- no Shapiro modification claim
- no real-data evidence claim

## Candidate Class

Bevorzugte Kandidatenklasse:

- targeted binary pulsar package
- example: NANOGrav J0740+6620
- expected files: `.par`, `.tim`, release notes / citation / timing-model context

Warum diese Klasse:

- eng begrenzt
- oeffentlich dokumentierbar
- Binary-Modell / Shapiro-nahe Parameterumgebung
- besser kontrollierbar als breite PTA-Releases
- weniger Rekonstruktionslast als Cassini oder VLBI

## Nicht-Ziele

- kein breiter NANOGrav-15-year-Ingest
- kein IPTA/EPTA/PPTA-Gesamtimport
- kein Cassini-Rohdatenpfad
- kein VLBI-Sessionpfad
- keine Lensing-Analyse
- keine Suche nach neuen physikalischen Effekten

## Required Input Inventory For Future Pilot

| input_item | expected_format | purpose | required_for_pilot | blocking_if_missing | risk_note |
|---|---|---|---|---|---|
| `timing_model_file` | `.par` | pulsar parameters, binary model, spin, astrometry, DM, model terms | yes | yes | Ohne explizites Timingmodell waere jede Fensterlogik zu weich. |
| `timing_observation_file` | `.tim` | TOAs, observing frequency, uncertainties, observatory/backend flags | yes | yes | TOAs ohne Unsicherheiten oder Tags koennen keine kontrollierte Vorschau tragen. |
| `release_documentation` | paper / release page / README | provenance, citation, model context, known limitations | yes | yes | Ohne Release-Kontext sind Datenstand und Modellannahmen nicht auditiert. |
| `correction_state_sidecar` | YAML / JSON | explicit correction-state fields | yes | yes | Der Sidecar ist Pflicht, damit Korrekturzustand nicht implizit bleibt. |
| `window_definition_sidecar` | YAML / JSON | A/B/control windows and shuffle-control definition | yes for dry-run preview | yes for comparison | Vergleichsfenster muessen vor jeder Statuslogik definiert sein. |
| `provenance_manifest` | JSON / YAML | source URL, citation, retrieval date, local checksum, processing notes | yes before any tracked data use | yes for reproducibility | Reproduzierbarkeit ist ohne Quelle, Datum und Checksumme nicht belastbar. |

## Correction-State Sidecar Minimum

| correction_layer | required_field_name | candidate_source | blocking_if_unknown | note |
|---|---|---|---|---|
| timing model state | `timing_model_state` | `.par`, release documentation, sidecar | yes | Modellversion und relevante Terme muessen sichtbar sein. |
| binary model state | `binary_model_state` | `.par`, binary timing documentation, sidecar | yes | Fuer den Binary-Pulsar-Pilot ist der binaere Modellzustand zentral. |
| clock correction state | `clock_correction_state` | release docs, clock files/state notes, sidecar | yes | Unklare Uhrenkorrektur blockiert den Pilotvergleich. |
| ephemeris state | `ephemeris_state` | `.par`, release docs, timing-model context | yes | Ephemeridenzustand darf nicht geraten werden. |
| DM / ISM state | `dm_ism_state` | `.par`, DM products, wideband metadata, sidecar | yes | Chromatische Reststruktur ist ein Artefaktrisiko. |
| solar wind state | `solar_wind_state` | timing model, release docs, sidecar | yes if relevant | Solarwind-Behandlung muss als Zustand oder Nicht-Anwendbarkeit sichtbar sein. |
| backend / instrument state | `backend_instrument_state` | `.tim` flags, backend tags, release docs | yes | Backend-Offsets koennen Fensterkontraste vortaeuschen. |
| noise model state | `noise_model_state` | release noise files/docs, sidecar | yes | Statusschwellen brauchen einen dokumentierten Noise-Kontext. |
| QC / outlier state | `qc_outlier_state` | release flags, exclusion notes, sidecar | yes | Ausreisserlogik darf nicht nachtraeglich unsichtbar wirken. |
| provenance / release state | `provenance_release_state` | provenance manifest, citation, release version | yes | Quelle, Version und lokale Behandlung muessen auditierbar bleiben. |

## A/B And Control Window Pilot Concept

- `A_reference_window`: Off-phase / stable comparison region. Must be selected defensively.
- `B_model_relevant_window`: Region where the binary timing model or Shapiro-related model terms are relevant. This is a workflow comparison window, not a physical claim.
- `negative_control_window`: Region expected not to carry the tested model contrast.
- `shuffle_control`: Epoch/window shuffle to test false-positive sensitivity.
- `backend_homogeneous_window`: optional window constraint to avoid backend/instrument jumps.
- `dm_control_window`: optional chromatic/DM-related control if DM metadata are available.

Diese Fenster sind technische Vergleichsfenster. Sie behaupten keine neue
Physik, keine Shapiro-Modifikation und keinen Datensatzbefund.

## Pilot Workflow Stages

| stage_id | stage_name | action | output_expected | go_no_go_gate |
|---|---|---|---|---|
| `P0_source_identification` | Source identification | Identify candidate package and public source only. | Kandidatenname, Quelltyp, keine lokale Datennutzung. | Quelle muss oeffentlich dokumentierbar sein. |
| `P1_provenance_check` | Provenance check | Record citation, URL, release context, license/data use notes. | Provenance-Notiz fuer spaeteren Manifestentwurf. | Unklare Zitation oder Datennutzung fuehrt zu NO-GO. |
| `P2_file_presence_check` | File presence check | Check whether `.par` and `.tim` or equivalents exist. | Praesenzliste, keine Ingestion. | Fehlende `.par`/`.tim`-aequivalente blockieren. |
| `P3_correction_state_sidecar_draft` | Correction-state sidecar draft | Draft correction-state metadata without interpreting data. | Sidecar-Feldentwurf mit Unknown-Markern. | Opaque Kernzustaende blockieren Vergleich. |
| `P4_mapping_preview_plan` | Mapping preview plan | Plan mapping into SHAPIROINFO02 fields. | Feldgruppen-Klassifikation, keine Records. | Blockierte Pflichtfelder muessen sichtbar sein. |
| `P5_window_definition_plan` | Window definition plan | Define A/B/control window rules. | Fensterregelentwurf, keine realen Fensterwerte. | Mindestens ein negativer Kontrolltyp muss definierbar sein. |
| `P6_dry_run_adapter_spec` | Dry-run adapter spec | Only after P0-P5 pass, prepare later dry-run adapter. | Spaetere Spezifikation fuer SHAPIROINFO10/11. | Erst nach bestandenen P0-P5-Gates. |

## Mapping Preview To SHAPIROINFO02

The first pilot should not try to fill every SHAPIROINFO02 field. It should
classify fields into:

- directly mapped
- sidecar mapped
- derived later
- unavailable in first pilot
- blocked if missing

| field_group | examples | mapping_status | risk_note |
|---|---|---|---|
| identity/provenance fields | `record_id`, `source_id`, `analysis_version`, `schema_version` | directly mapped / sidecar mapped | Alias- und Release-Kontext muessen stabil benannt werden. |
| timing/TOA fields | `timestamp_utc`, `time_standard`, `measured_arrival_time_s` | directly mapped if `.tim` convention is documented | Zeitstandard darf nicht stillschweigend konvertiert werden. |
| uncertainty fields | `timing_uncertainty_s`, uncertainty unit notes | directly mapped if present | Fehlende TOA-Sigmas blockieren Statusvergleiche. |
| frequency/band fields | `carrier_frequency_hz`, `signal_bandwidth_hz` | directly mapped / sidecar mapped | MHz/Hz-Umrechnung und Banddefinition muessen explizit sein. |
| correction-state fields | `gr_shapiro_correction_s`, `plasma_correction_s`, `source_model_correction`, `instrument_correction`, `noise_model` | sidecar mapped / blocked if missing | Korrekturzustand ist kein optionaler Kommentar, sondern Gate-Material. |
| residual fields | `residual_timing_s`, `residual_phase_rad`, `residual_status` | unavailable in first pilot / derived later | Keine Residualwerte in SHAPIROINFO09; Status bleibt Planungssprache. |
| fingerprint fields | `relational_fingerprint_method`, `relational_fingerprint_value`, spectrum/modulation fingerprints | derived later / unavailable in first pilot | Keine versteckten Fingerprints aus Timingdaten ableiten. |
| claim-boundary fields | `claim_boundary_flag`, `notes`, `control_family`, `negative_control_id` | sidecar mapped / blocked if missing | Boundary- und Kontrollfelder schuetzen vor Ueberdeutung. |

## Go / No-Go Before Any Implementation

`GO_FOR_SHAPIROINFO10_OR_11` only if:

- candidate source is public
- `.par` and `.tim` or equivalents are present
- release documentation is sufficient
- correction-state sidecar can be populated
- clock and ephemeris states are not opaque
- binary model state is explicit
- TOA uncertainties are present
- at least one negative control window is definable
- no broad multi-release ingest is required

`NO_GO_FOR_NOW` if:

- correction-state is opaque
- time standard is unclear
- clock/ephemeris state unknown
- timing-model state unclear
- backend/instrument tags absent where needed
- no control windows can be defined
- data use/citation is unclear
- pilot would require broad PTA ingestion

## Relation To SHAPIROINFO08

SHAPIROINFO08 planned the toy-to-semi-real adapter. SHAPIROINFO09 narrows the
first pilot target to a targeted binary pulsar package. It still does not
implement the adapter.

## Relation To SHAPIROINFO04/05

The toy comparator demonstrated technical status separation:

- `no_residual`
- `artifact_likely`
- `candidate_residual`
- `inconclusive`

The binary pulsar pilot must preserve these as diagnostic states only, not
physical claims.

## Relation To INTERFACE03

INTERFACE03 remains vocabulary/interface context only. The pilot does not
derive c, explain the numerical value of c, or change standard relativistic
timing logic.

## Befund

The project now has a defensible path from synthetic toy logic toward a narrow
semi-real pulsar timing pilot.

## Interpretation

A targeted binary pulsar package is the best first semi-real candidate because
it is narrower, more documented, and more compatible with `.par`/`.tim`-style
preview mapping than Cassini, VLBI, or broad PTA ingestion.

## Hypothese

A small targeted binary pulsar pilot may provide a controlled first test of
whether the SHAPIROINFO record schema and comparator status logic can be
attached to public timing data without losing correction-state transparency.

## Offene Luecke

- no data downloaded
- no candidate package inspected locally
- no `.par` / `.tim` parsed
- no PINT / tempo2 run
- no TOA residuals generated
- no real A/B windows selected
- no empirical result
- no residual search

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from pilot planning
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO10 Correction-State Field Schema
- SHAPIROINFO11 Targeted Binary Pulsar Dry-Run Adapter Spec
- SHAPIROINFO12 Public Source and Citation Checklist
- SHAPIROINFO13 Cassini Feasibility Study Plan
- SHAPIROINFO14 VLBI Feasibility Study Plan

## Acceptance Checks

- Datei existiert
- enthaelt J0740+6620
- enthaelt `.par`
- enthaelt `.tim`
- enthaelt correction_state_sidecar
- enthaelt A_reference_window
- enthaelt B_model_relevant_window
- enthaelt negative_control_window
- enthaelt shuffle_control
- enthaelt GO_FOR_SHAPIROINFO10_OR_11
- enthaelt NO_GO_FOR_NOW
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
