# QSB-ST-SHAPIROINFO02 — Minimal Signal Record Schema Spec

## Purpose

Minimal schema for later A/B signal comparison in a ShapiroInfo-style
residual search. The schema is intended as a small working frame for future
records, not as data, code, or an evaluation result.

Current anchor:

- `8e9d7ce Add QSB-ST interface ShapiroInfo result readout`

Builds on:

- `docs/QSB_ST_INTERFACE03_RT_QM_CAUSALITY_ROSETTA_TRANSLATOR_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_INTERFACE_SHAPIROINFO_RESULT_READOUT_2026_05_28.md`

## Scope

- schema only
- no empirical claim
- no physical validation
- no Shapiro modification claim
- no implementation yet

## Signal-Pair Logic

- `signal_A_reference`: reference signal or path-side record for comparison.
- `signal_B_influenced`: gravitationally influenced, medium-influenced, or
  otherwise tested signal-side record.
- `correction_layers`: documented correction stack before any residual wording.
- `residual_candidate`: only considered after known corrections, uncertainty
  accounting, and controls are recorded.

## Required Field List

| field_name | field_type | field_description | required_flag | claim_risk_note |
|---|---|---|---|---|
| `record_id` | string | Stable identifier for one signal record. | required | Administrative only; no evidence content by itself. |
| `experiment_family` | string | Family label for related comparison records. | required | Groups records; does not imply physical specificity. |
| `signal_pair_id` | string | Identifier linking A/B/control records. | required | Pairing aid; not a residual result. |
| `signal_role` | enum[`reference`,`influenced`,`control`] | Role of the record within the comparison. | required | Role label only; no Bridge or Shapiro conclusion. |
| `source_id` | string | Identifier for the signal source. | required | Source metadata; quality depends on later documentation. |
| `receiver_id` | string | Identifier for the receiver or detector. | required | Receiver metadata; no validation by schema alone. |
| `path_id` | string | Identifier for the modeled or measured signal path. | required | Path label; geometry must be supplied elsewhere. |
| `path_class` | enum[`reference_path`,`gravitationally_influenced_path`,`control_path`,`synthetic_path`] | Coarse class of the path used in comparison. | required | Classification is not a modification claim. |
| `timestamp_utc` | string | UTC timestamp or interval marker for the record. | required | Time label only; precision must be checked later. |
| `time_standard` | string | Timing standard used for the timestamp and arrival time. | required | Does not certify timing traceability alone. |
| `sampling_rate_hz` | float | Sampling rate for the recorded signal. | required | Instrument detail; no residual status by itself. |
| `carrier_frequency_hz` | float | Carrier frequency of the signal. | required | Basic signal descriptor; not a derivation of c. |
| `wavelength_m` | float | Wavelength associated with the signal record. | required | Later ratios must remain derived/read-only. |
| `signal_bandwidth_hz` | float | Effective signal bandwidth. | required | Descriptive field; no information residual by itself. |
| `modulation_type` | string | Modulation family or encoding description. | required | Vocabulary field; no QM/RT replacement claim. |
| `polarization_state` | string | Polarization state or recording convention. | required | Needs later calibration context. |
| `phase_reference_method` | string | Method used to define or recover phase reference. | required | Method label; phase claims require later checks. |
| `measured_arrival_time_s` | float | Measured arrival time in seconds. | required | Raw timing value; corrections and uncertainty remain separate. |
| `timing_uncertainty_s` | float | Timing uncertainty in seconds. | required | Must accompany timing residual use. |
| `measured_phase_rad` | float | Measured phase in radians. | required | Raw phase value; no residual reading alone. |
| `phase_uncertainty_rad` | float | Phase uncertainty in radians. | required | Must accompany phase residual use. |
| `measured_frequency_shift_hz` | float | Measured frequency shift in hertz. | required | Shift value only; cause remains open. |
| `frequency_uncertainty_hz` | float | Frequency uncertainty in hertz. | required | Needed before frequency residual wording. |
| `spectrum_fingerprint_method` | string | Method used to create a spectrum fingerprint. | required | Method metadata; no specificity by itself. |
| `spectrum_fingerprint_value` | string | Recorded spectrum fingerprint value. | required | Candidate descriptor; not evidence alone. |
| `modulation_fingerprint_method` | string | Method used to create a modulation fingerprint. | required | Method metadata; no information claim alone. |
| `modulation_fingerprint_value` | string | Recorded modulation fingerprint value. | required | Candidate descriptor; controls still needed. |
| `relational_fingerprint_method` | string | Method for relational comparison between records. | required | Comparison vocabulary; not physical validation. |
| `relational_fingerprint_value` | string | Relational fingerprint value for the record or pair. | required | Needs later comparator and controls. |
| `gr_shapiro_correction_s` | float | General-relativistic Shapiro correction in seconds, if modeled. | required | Baseline correction field; no Shapiro modification claim. |
| `plasma_correction_s` | float | Plasma-related timing correction in seconds. | required | Known correction layer; not residual evidence. |
| `medium_correction_s` | float | Propagation-medium correction in seconds. | required | Known correction layer; model limits must be recorded later. |
| `source_model_correction` | string | Source-side correction description or identifier. | required | Textual correction note; no validation by itself. |
| `instrument_correction` | string | Instrument correction description or identifier. | required | Calibration-dependent; must remain auditable. |
| `calibration_reference` | string | Calibration reference, standard, or file identifier. | required | Reference pointer; does not certify the record alone. |
| `noise_model` | string | Noise model description or identifier. | required | Model choice; residual wording depends on adequacy. |
| `lensing_model` | string | Lensing model description or identifier. | required | Context correction; no Bridge conclusion. |
| `residual_timing_s` | float | Timing residual after stated corrections. | required | Candidate quantity only; status field controls wording. |
| `residual_phase_rad` | float | Phase residual after stated corrections. | required | Candidate quantity only; no physical reading alone. |
| `residual_frequency_hz` | float | Frequency residual after stated corrections. | required | Candidate quantity only; no cause assigned here. |
| `residual_fingerprint_score` | float | Score from a later fingerprint comparator. | required | Comparator output; no evidence claim from schema alone. |
| `residual_status` | enum[`not_evaluated`,`no_residual`,`candidate_residual`,`artifact_likely`,`inconclusive`] | Conservative residual state after corrections and controls. | required | `candidate_residual` is not physical validation. |
| `control_family` | string | Control group or control strategy label. | required | Control metadata; no result by itself. |
| `negative_control_id` | string | Identifier for a negative control record or family. | required | Required guardrail; interpretation remains separate. |
| `reproducibility_group_id` | string | Identifier for repeat or reproducibility grouping. | required | Grouping aid; reproducibility is not implied by label alone. |
| `analysis_version` | string | Version label for later analysis logic. | required | Version label only; no hidden algorithm content. |
| `schema_version` | string | Version label for this record schema. | required | Schema traceability only. |
| `notes` | string | Free text for constraints, caveats, or record comments. | required | Notes must not override claim boundaries. |
| `claim_boundary_flag` | boolean | Explicit flag that the record is governed by the claim boundary. | required | Guardrail field; does not make claims safer by itself. |
| `c_from_lambda_f_m_per_s` | float | Later derived value from wavelength and frequency. | derived/read-only candidate | Not a derivation of c; diagnostic ratio only. |
| `c_from_omega_over_k_m_per_s` | float | Later derived value from angular frequency over wavenumber. | derived/read-only candidate | Diagnostic ratio only; no numerical explanation of c. |
| `energy_momentum_ratio_m_per_s` | float | Later derived energy/momentum ratio when inputs exist. | derived/read-only candidate | Vocabulary bridge candidate; no Bridge confirmation. |
| `phase_velocity_m_per_s` | float | Later derived phase velocity estimate. | derived/read-only candidate | Propagation descriptor; no replacement claim. |
| `group_velocity_m_per_s` | float | Later derived group velocity estimate. | derived/read-only candidate | Propagation descriptor; model-dependent. |
| `normalized_residual_score` | float | Later derived normalized residual score. | derived/read-only candidate | Ranking aid; not evidence from schema alone. |
| `correction_budget_summary` | string | Later derived summary of applied correction layers. | derived/read-only candidate | Summary aid; underlying corrections remain decisive. |

## Residual Decision Logic

- If corrected_B is approximately corrected_A within uncertainty:
  `residual_status=no_residual`.
- If corrected_B differs reproducibly beyond uncertainty and controls:
  `residual_status=candidate_residual`.
- `candidate_residual` is not physical validation.

## Claim Boundary

- no derivation of c
- no explanation of numerical value of c
- no Bridge confirmation
- no spacetime emergence claim
- no replacement of relativity or quantum mechanics
- no Shapiro modification claim
- no evidence claim from schema alone

## Acceptance Checks

- Datei existiert.
- Field list contains `field_name`, `field_type`, `field_description`.
- Risk grep is clean.
- `git diff --check` clean.
- `git status --short` reported.
