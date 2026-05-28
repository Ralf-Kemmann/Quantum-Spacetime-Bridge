# QSB-ST-SHAPIROINFO08 -- Toy-to-Semi-Real Adapter Plan

## Current anchor

`2fe5456 Add QSB-ST ShapiroInfo public dataset feasibility matrix spec`

## Purpose

SHAPIROINFO08 plant den Uebergang vom Toy-Comparator zu einem semi-realen
Eingangsformat. Kein Real-Datenlauf, keine Residualsuche, keine Aussage ueber
reale Daten.

Der Adapter soll spaeter zunaechst nur `.par`/`.tim`-nahe Daten und
Correction-State-Metadaten in das SHAPIROINFO02-Record-Schema abbilden.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO03_TOY_COMPARATOR_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO04_TOY_COMPARATOR_MINIMAL_RUNNER_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO05_TOY_COMPARATOR_RESULT_NOTE.md`
- `docs/QSB_ST_SHAPIROINFO06_DATA_AND_SCENARIO_INVENTORY_NOTE.md`
- `docs/QSB_ST_SHAPIROINFO07_PUBLIC_DATASET_FEASIBILITY_MATRIX_SPEC.md`

## Scope

- adapter plan only
- no data download
- no `.par` / `.tim` ingestion yet
- no PINT / tempo2 run
- no real residual calculation
- no empirical result
- no Bridge claim
- no Shapiro modification claim

## Target First Semi-Real Class

Empfohlener Kandidat:

- targeted binary pulsar package such as NANOGrav J0740+6620

Alternative spaeter:

- small NANOGrav/InPTA subset

Nicht zuerst:

- Cassini
- VLBI
- lensing time delays

## Adapter Role

Der Adapter soll spaeter:

- `.par` file metadata lesen oder als manuell extrahierte Metadaten aufnehmen
- `.tim` TOA records lesen oder als tabellarisch normalisierte TOAs aufnehmen
- Correction-State-Metadaten aufnehmen
- A/B- oder Kontrollfenster definieren
- TOA-/Residual-nahe Werte in SHAPIROINFO02-Felder abbilden
- keine physikalische Interpretation ausgeben

## Minimal Future Input Classes

| input_class | example | expected_content | required_for_first_adapter | risk_note |
|---|---|---|---|---|
| `timing_model_file` | `.par` | pulsar parameters, binary model, astrometry, spin, DM, model terms | required | Timing-model state must be explicit before any window comparison. |
| `timing_observation_file` | `.tim` | TOAs, observing frequency, observatory/backend tags, uncertainties | required | TOA rows without timing uncertainties or tags are not enough. |
| `correction_state_metadata` | manual YAML / JSON sidecar | clock state, ephemeris state, DM/solarwind state, backend state, noise model state | required | Missing Correction-State blocks semi-real use. |
| `window_definition_file` | adapter YAML | reference windows, influenced windows, orbit-phase / off-phase controls | required | Window labels are workflow controls, not physical statements. |
| `provenance_manifest` | manifest JSON | dataset URL, citation, release version, local checksum, retrieval date, processing notes | required | Provenance gaps make replay and audit weak. |

## Mapping To SHAPIROINFO02

| SHAPIROINFO02_field | semi_real_source | required_or_optional | mapping_note | risk_note |
|---|---|---|---|---|
| `record_id` | adapter-generated record key | required | Stable key per TOA-derived preview row. | Administrative only. |
| `experiment_family` | adapter config | required | Example: `shapiroinfo_pulsar_timing_pilot`. | Family label is not a result. |
| `signal_pair_id` | window definition | required | Links A/B/control windows or paired records. | Pairing needs documented window logic. |
| `signal_role` | window definition | required | One of `reference`, `influenced`, `control`. | Role label is not a physical claim. |
| `source_id` | `.par` pulsar name / metadata | required | Pulsar identifier, e.g. J0740+6620. | Source aliases must be resolved. |
| `receiver_id` | `.tim` observatory/backend tags | required if available | Observatory, receiver, backend, or system tag. | Missing backend state can hide offsets. |
| `path_id` | adapter config / window geometry | required | Synthetic path label for TOA/window relation. | Path label only. |
| `path_class` | adapter config | required | Likely `control_path` or `reference_path` for preview rows. | Avoid overloading with physical interpretation. |
| `timestamp_utc` | `.tim` TOA after documented time conversion | required | Store declared timestamp convention or converted UTC if available. | Time-standard ambiguity blocks comparison. |
| `time_standard` | `.par`/`.tim`/sidecar | required | TT/TDB/observatory convention as documented. | Must not be guessed silently. |
| `sampling_rate_hz` | sidecar or not available marker | optional for first adapter | Pulsar TOAs may not expose a sampling rate. | Use `not_available` note rather than fabricate. |
| `carrier_frequency_hz` | `.tim` observing frequency | required if present | Convert MHz-like TOA frequency to Hz with unit note. | Unit mistakes directly affect derived fields. |
| `wavelength_m` | derived/read-only from frequency, if allowed | optional | Only compute in preview if frequency and constants policy are explicit. | Not a derivation of c. |
| `signal_bandwidth_hz` | sidecar / release metadata | optional | Bandwidth if documented by release or sidecar. | Missing bandwidth limits fingerprint use. |
| `modulation_type` | sidecar | optional | Usually `pulsar_toa_timing` or similar controlled label. | Vocabulary field only. |
| `polarization_state` | sidecar / release metadata | optional | Preserve if release provides polarization context. | Often absent in first timing-only path. |
| `phase_reference_method` | `.par` timing model / sidecar | required if phase windows are used | Timing model phase convention or template reference. | Phase language needs exact convention. |
| `measured_arrival_time_s` | `.tim` TOA normalized by adapter | required for preview | TOA represented in seconds or linked time unit. | No residual status without uncertainty. |
| `timing_uncertainty_s` | `.tim` TOA uncertainty | required | Convert to seconds with unit note. | Missing sigma blocks status language. |
| `measured_phase_rad` | not first-pass / optional derived preview | optional | Only if phase observable is explicitly produced later. | Do not infer phase from TOA alone without method. |
| `phase_uncertainty_rad` | not first-pass / optional derived preview | optional | Pair with measured phase only. | Empty unless phase method exists. |
| `measured_frequency_shift_hz` | not first-pass / sidecar | optional | Not expected in `.par`/`.tim` pilot. | Do not substitute TOA frequency for frequency shift. |
| `frequency_uncertainty_hz` | not first-pass / sidecar | optional | Pair with measured frequency shift only. | Missing in timing-only preview. |
| `spectrum_fingerprint_method` | sidecar / release auxiliary metadata | optional | Method name if spectra or band products are available. | Not required for first timing-only adapter. |
| `spectrum_fingerprint_value` | sidecar / future auxiliary output | optional | Value or `not_available` marker. | Missing fingerprint is a format boundary. |
| `modulation_fingerprint_method` | sidecar / future auxiliary output | optional | Method name for pulse-profile or modulation descriptor. | No method, no value. |
| `modulation_fingerprint_value` | sidecar / future auxiliary output | optional | Descriptor value if available. | Do not generate hidden descriptors. |
| `relational_fingerprint_method` | adapter config | optional for first preview | A/B window comparison method, if configured. | Comparison method must be named. |
| `relational_fingerprint_value` | future adapter preview | optional | Derived preview value only in dry-run mode. | Not evidence by itself. |
| `gr_shapiro_correction_s` | timing model state / sidecar | optional but tracked | Store model-state pointer or value only if explicitly available. | Do not reconstruct silently. |
| `plasma_correction_s` | DM/ISM/solarwind sidecar | optional but tracked | Store value or state note when correction is explicit. | Chromatic remnants are a key artifact risk. |
| `medium_correction_s` | sidecar | optional | Generic propagation-medium correction if documented. | Avoid double-counting with DM/plasma fields. |
| `source_model_correction` | `.par`/sidecar | required | Timing model, binary model, and source-model note. | Source-model ambiguity blocks pilot use. |
| `instrument_correction` | `.tim` tags / sidecar | required | Backend jumps, observatory/system tags, calibration state. | Backend offsets can mimic structure. |
| `calibration_reference` | provenance manifest / sidecar | required | Release calibration pointer or declared not available. | Must be auditable. |
| `noise_model` | sidecar / release docs | required | White/red noise, EFAC/EQUAD/ECORR-like state if known. | Status thresholds depend on noise model. |
| `lensing_model` | not applicable marker | required as boundary marker | Use `not_applicable_pulsar_timing`. | Prevent accidental lensing analogy. |
| `residual_timing_s` | future preview only | optional for dry-run | Empty or `not_evaluated` until residual workflow exists. | No residual calculation in SHAPIROINFO08. |
| `residual_phase_rad` | future preview only | optional | Empty or `not_evaluated`. | No phase residual in adapter planning. |
| `residual_frequency_hz` | future preview only | optional | Empty or `not_evaluated`. | No frequency residual in adapter planning. |
| `residual_fingerprint_score` | future preview only | optional | Empty or `not_evaluated`. | No fingerprint scoring yet. |
| `residual_status` | adapter dry-run status | required | Default `not_evaluated` for record preview. | Semi-real adapter must not emit physical status. |
| `control_family` | window definition | required | A/B, negative control, shuffle control family. | Control names must be explicit. |
| `negative_control_id` | window definition | required | Identifier for off-phase or null window. | No negative control, no pilot. |
| `reproducibility_group_id` | adapter config | required | Grouping for replay or repeated windows. | Not a reproducibility statement. |
| `analysis_version` | adapter version | required | Future adapter code/config version. | Version is not validation. |
| `schema_version` | SHAPIROINFO02 schema marker | required | Pin schema target. | Schema drift must be visible. |
| `notes` | sidecar / adapter config | required | Caveats and missing-state notes. | Notes must not override boundaries. |
| `claim_boundary_flag` | adapter constant | required | Always true for semi-real preview records. | Guardrail, not a result. |

## Correction-State Requirements

Fuer SHAPIROINFO08/09 darf kein halb-realer Datensatz ohne
Correction-State-Sidecar benutzt werden. Der Sidecar ist der Ort, an dem
Timingmodell, Uhren, Ephemeriden, DM/ISM, Solarwind, Backend, Noise, QC und
Provenance sichtbar werden.

| correction_layer | required_state_field | source_in_pulsar_context | blocking_if_missing |
|---|---|---|---|
| timing model state | `timing_model_state` | `.par`, release docs, sidecar | yes |
| binary model state | `binary_model_state` | `.par`, targeted binary package docs | yes for binary-pulsar pilot |
| clock correction state | `clock_correction_state` | release clock files, timing docs, sidecar | yes |
| ephemeris state | `ephemeris_state` | `.par`, release docs, sidecar | yes |
| DM / ISM state | `dm_ism_state` | `.par`, wideband/DM products, sidecar | yes |
| solar wind state | `solar_wind_state` | timing model, release docs, sidecar | yes if solar-window controls are used |
| backend / instrument state | `backend_instrument_state` | `.tim` flags, backend tags, release docs | yes |
| noise model state | `noise_model_state` | release noise files/docs, sidecar | yes |
| QC / outlier state | `qc_outlier_state` | release flags, adapter sidecar | yes |
| provenance / release state | `provenance_release_state` | manifest, citation, release version, checksum | yes |

## A/B Window Concept

- `A_reference_window`: Kontrollfenster, z. B. off-orbit-phase oder stabiler
  Vergleichszeitraum.
- `B_influenced_window`: potenziell modellrelevanter Fensterbereich, z. B.
  orbit-phase-nahe Region bei binaerem Pulsar.
- `negative_control_window`: Fenster ohne erwarteten Shapiro-/modellnahen
  Kontrast.
- `shuffle_control`: epoch / window shuffle zur False-Positive-Kontrolle.

Diese Fenster sind zunaechst workflow-technische Vergleichsfenster, keine
physikalische Behauptung.

## Minimal Adapter Outputs For Future SHAPIROINFO09

Noch nicht erzeugen, nur planen:

- `data/QSB-ST-SHAPIROINFO/pulsar_adapter_config.yaml`
- `data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml`
- `scripts/run_qsb_st_shapiroinfo_pulsar_adapter.py`
- `runs/QSB-ST-SHAPIROINFO09/pulsar_adapter_dryrun/`

Future outputs:

- `summary.json`
- `readout.md`
- `semi_real_record_preview.csv`
- `correction_state_report.csv`
- `field_mapping_report.csv`

## Go/No-Go Gates Before Implementation

GO only if:

- selected dataset is public and cited
- `.par` and `.tim` or equivalent are accessible
- correction-state sidecar can be populated
- no hidden preprocessing assumptions
- A/B windows can be defined defensively
- negative controls exist
- adapter can run in dry-run/preview mode first

NO-GO if:

- correction-state opaque
- timing model state unclear
- clock/ephemeris state unknown
- no control windows
- broad multi-release ingestion required at first step
- data use/citation unclear

## Relation To SHAPIROINFO04 Toy Comparator

Der Toy Comparator bleibt Referenz fuer Statuslogik:

- `no_residual`
- `artifact_likely`
- `candidate_residual`
- `inconclusive`

Semi-real adapter darf diese Status nicht als physikalische Aussagen deuten.

## Relation To SHAPIROINFO07

SHAPIROINFO07 waehlt Pulsar Timing als ersten Go-for-Pilot-Kandidaten.
SHAPIROINFO08 plant nur den engen Adapter fuer diesen Pfad.

## Befund

SHAPIROINFO07 liefert eine Matrix, nach der ein targeted binary pulsar package
der sicherste erste halb-reale Kandidat ist. SHAPIROINFO08 konkretisiert, wie
dieser Pfad technisch vorbereitet werden kann.

## Interpretation

Der naechste Fortschritt liegt nicht in einer sofortigen Analyse, sondern im
sauberen Uebergang von Toy-Records zu halb-realen Record-Previews mit
vollstaendigem Correction-State.

## Hypothese

Ein enger Pulsar-Timing-Adapter koennte als erster kontrollierter
Realwelt-Anschluss dienen, wenn Correction-State, Provenance und
Kontrollfenster ausreichend dokumentiert sind.

## Offene Luecke

- keine Daten geladen
- kein Adapter implementiert
- kein PINT/tempo2-Lauf
- keine Realanalyse
- keine Residualsuche
- keine Entscheidung fuer konkreten Download
- keine Aussage ueber reale Pulsardaten

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from adapter planning

## Next Possible Blocks

- SHAPIROINFO09 Targeted Binary Pulsar Pilot Plan
- SHAPIROINFO10 Correction-State Field Schema
- SHAPIROINFO11 Adapter Dry-Run Spec
- SHAPIROINFO12 Cassini Feasibility Study Plan
- SHAPIROINFO13 VLBI Feasibility Study Plan

## Acceptance Checks

- Datei existiert.
- Enthaelt J0740+6620.
- Enthaelt `.par`.
- Enthaelt `.tim`.
- Enthaelt Correction-State.
- Enthaelt `A_reference_window`.
- Enthaelt `B_influenced_window`.
- Enthaelt `negative_control_window`.
- Enthaelt `shuffle_control`.
- Enthaelt no Bridge confirmation.
- Risk grep clean.
- `git diff --check` clean.
- `git status --short` reported.
