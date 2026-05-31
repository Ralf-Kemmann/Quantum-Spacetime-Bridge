# QSB-ST SHAPIROINFO63 — Public Documentation and Correction-State Resolution Spec

Date: 2026-06-01  
Status: public-documentation and correction-state resolution specification  
Upstream plan: SHAPIROINFO62_PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_PLAN  
Specification type: documentation / correction-state resolution before value-reading gate  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note specifies the public-documentation and correction-state resolution layer required before any first controlled value-reading gate can be considered.

SHAPIROINFO62 planned this layer because SHAPIROINFO61 kept direct value reading closed.

The reason is simple and methodological: the dictionary/schema/correction-state layer exists, but all correction-state fields remain unresolved by default.

The project must therefore identify which public documentation targets and correction-state fields need to be resolved, documented, or explicitly left unresolved before any value reading can be responsibly planned.

This note is a specification only.

It does not perform public web research.

It does not download documentation.

It does not inspect raw artifacts.

It does not read TIM or PAR values.

It does not compute residuals.

It does not fit timing models.

It does not make anomaly claims.

It does not make QSB-ST Bridge-related claims.

## 2. Upstream state

The current method layer contains:

- TIM schema map
- PAR field dictionary
- PAR prefix-group dictionary
- duplicate-parameter report
- correction-state template
- provenance-requirements table

Known upstream facts:

- tim_schema_records = 43
- dominant_column_count = 41
- dominant_column_count_rows = 7419
- semantic_mapping_status = not_performed
- par_field_dictionary.csv contains 453 rows
- par_prefix_group_dictionary.csv contains 46 rows
- duplicate parameters: ECORR, T2EFAC, T2EQUAD
- correction_state_fields_defined = 17
- unresolved_default_count = 17
- correction_state_layer_status = template_created
- value_reading_gate_status = not_opened
- semantic claims are blocked by provenance requirements

## 3. Specification decision

Decision:

- next_scope = PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_SCRIPT
- next_step = SHAPIROINFO64_PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_SCRIPT
- following_possible_gate = SHAPIROINFO65_PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_EXECUTION
- later_possible_gate = SHAPIROINFO66_FIRST_CONTROLLED_VALUE_READING_GATE_PLAN
- allowed_scope = DOCUMENTATION_TARGETS_AND_CORRECTION_STATE_RESOLUTION_ONLY
- direct_value_reading_gate = NOT_OPENED
- residual_analysis_gate = CLOSED
- model_fitting_gate = CLOSED
- anomaly_claim_gate = CLOSED
- bridge_claim_gate = CLOSED
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- public_web_research = NOT_PERFORMED_BY_THIS_NOTE
- documentation_download = NOT_PERFORMED_BY_THIS_NOTE
- research_status = PHYSICS_MOTIVATED_ACTIVE_ROUTE

The project may proceed to a script that creates a documentation-target and correction-state resolution table.

The project must not proceed directly to value reading, residual computation, model fitting, anomaly search, or Bridge interpretation.

## 4. Required documentation target classes

A later SHAPIROINFO64 script should create a documentation target table with at least the following target classes:

- tim_file_format
- par_file_format
- current_public_source_package
- timing_model_tool_conventions
- clock_correction_conventions
- ephemeris_conventions
- DM_dispersion_correction_conventions
- solarwind_correction_conventions
- noise_model_conventions
- backend_jump_system_parameter_conventions
- frequency_band_conventions
- profile_template_conventions
- observatory_backend_receiver_system_conventions
- checksum_provenance_quarantine_state
- duplicate_parameter_conventions
- value_reading_scope_constraints

Each documentation target must include:

- target_id
- target_class
- target_description
- required_for_value_reading
- required_for_semantic_mapping
- planned_status
- source_requirement
- unresolved_allowed
- stop_if_unavailable
- notes

Allowed planned_status values:

- documentation_required
- documentation_identified
- documentation_unavailable
- not_applicable
- unresolved

Default planned_status should be documentation_required unless a target is clearly not applicable or already covered by upstream local quarantine/checksum notes.

## 5. Required correction-state resolution fields

A later SHAPIROINFO64 script should create a correction-state resolution table covering all 17 fields already defined:

- raw_or_processed_state
- timing_model_source
- timing_model_tool
- clock_correction_state
- clock_reference
- ephemeris_state
- ephemeris_reference
- DM_correction_state
- solarwind_correction_state
- noise_model_state
- backend_jump_state
- whitening_state
- frequency_band_state
- profile_template_state
- observatory_system_state
- provenance_reference
- unresolved_correction_fields

Each correction-state row must include:

- correction_field
- current_status
- required_for_value_reading
- required_for_semantic_mapping
- documentation_target_class
- allowed_resolution_values
- unresolved_allowed
- stop_if_unresolved
- provenance_requirement
- notes

Allowed current_status values:

- known_from_file
- known_from_public_documentation
- inferred_from_structure
- unresolved
- not_applicable
- forbidden_to_assume

Default current_status should be unresolved.

Unknown is acceptable.

Unresolved is acceptable.

Assumed is not acceptable.

Silent assumptions are not acceptable.

## 6. Duplicate-parameter follow-up specification

A later SHAPIROINFO64 script should create a duplicate-parameter follow-up table for:

- ECORR
- T2EFAC
- T2EQUAD

Each duplicate follow-up row must include:

- parameter_name
- duplicate_status
- required_documentation_target
- expected_scope_question
- interpretation_status
- value_reading_status
- required_followup
- notes

Allowed duplicate_status values:

- duplicate_observed
- expected_by_convention_unconfirmed
- expected_by_convention_documented
- unresolved
- forbidden_to_interpret

Allowed interpretation_status values:

- not_interpreted
- documentation_required
- unresolved
- forbidden_to_infer

The duplicate follow-up may ask whether duplicates are expected by timing-tool or release conventions.

It may not interpret duplicate values physically.

It may not select duplicate parameters for fitting.

It may not treat duplicates as anomalies.

It may not claim QSB-ST relevance.

## 7. Semantic mapping rule specification

A later SHAPIROINFO64 script should create a semantic mapping rule table.

Required fields:

- mapping_scope
- allowed_mapping_source
- mapping_status
- semantic_claim_allowed
- physical_interpretation_allowed
- required_provenance
- notes

Allowed mapping_status values:

- not_performed
- documentation_required
- source_documentation_identified
- source_documentation_unavailable
- unresolved
- forbidden_to_infer

Default mapping_status should be documentation_required or not_performed.

semantic_claim_allowed must remain false.

physical_interpretation_allowed must remain false.

No field or parameter name may be mapped to physical meaning by intuition alone.

## 8. Provenance resolution specification

A later SHAPIROINFO64 script should create a provenance resolution requirements table.

Required fields:

- provenance_item
- source_type_required
- source_path_or_reference
- current_status
- provenance_confidence
- semantic_claim_allowed
- value_reading_allowed
- notes

Allowed source_type_required values:

- local_generated_output
- local_manifest_or_checksum_note
- public_release_documentation
- timing_tool_documentation
- unresolved

Allowed current_status values:

- available_locally
- public_documentation_required
- unresolved
- not_applicable

Allowed provenance_confidence values:

- high
- medium
- low
- unresolved

semantic_claim_allowed must remain false.

value_reading_allowed must remain false by default.

## 9. Required output files for SHAPIROINFO64 execution later

A later execution block should write outputs under:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO64_PUBLIC_DOCUMENTATION_CORRECTION_STATE_RESOLUTION/

Recommended output files:

- public_documentation_targets.csv
- correction_state_resolution_table.csv
- duplicate_parameter_followup_table.csv
- semantic_mapping_rules.csv
- provenance_resolution_requirements.csv
- documentation_resolution_summary.json
- public_documentation_correction_state_readout.md
- public_documentation_correction_state_config_resolved.json

Outputs are run artifacts first unless explicitly reviewed and tracked later.

## 10. Required summary fields

documentation_resolution_summary.json should include:

- generated_at_utc
- output_root
- documentation_target_count
- correction_state_field_count
- unresolved_correction_state_count
- duplicate_parameter_followup_count
- semantic_mapping_status
- direct_value_reading_gate
- residual_analysis_gate
- model_fitting_gate
- bridge_claim_gate
- public_web_research_status
- documentation_download_status
- claim_boundary

Default gate status values:

- direct_value_reading_gate = not_opened
- residual_analysis_gate = closed
- model_fitting_gate = closed
- bridge_claim_gate = closed
- public_web_research_status = not_performed
- documentation_download_status = not_performed

## 11. Requirements for SHAPIROINFO64 script

The script must:

- use Python standard library only
- create output directory only when executed
- not inspect raw artifacts
- not read TIM/PAR values
- not perform public web research
- not download documentation
- not compute residuals
- not fit timing models
- not interpret values physically
- not make anomaly claims
- not make QSB-ST Bridge claims
- generate documentation target and correction-state resolution tables
- preserve unresolved states
- preserve stop conditions
- preserve claim boundaries

## 12. Stop conditions

The route must stop or downgrade if:

- documentation targets cannot be identified
- documentation requirements cannot be represented
- correction-state fields cannot be represented
- duplicate-parameter follow-up cannot be represented without interpretation
- semantic mapping would require undocumented inference
- value reading would require assuming correction-state status
- any output begins to frame values as physical evidence

A stop condition is a valid scientific result.

## 13. Claim boundary

This note is a documentation and correction-state resolution specification within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only specifies the documentation-target and correction-state resolution layer required before any later first controlled value-reading gate can be considered.
