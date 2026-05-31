# QSB-ST SHAPIROINFO57 — TIM/PAR Field Dictionary, Schema Map, and Correction-State Spec

Date: 2026-05-31  
Status: field dictionary / schema map / correction-state specification  
Upstream decision: SHAPIROINFO56_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_DECISION  
Specification type: method-layer specification before value-reading gate  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note specifies the next method layer for the QSB-ST ShapiroInfo TIM/PAR route.

SHAPIROINFO56 decided that the project should not jump directly from content-structure review to physical value interpretation.

It also decided that further purely external structure work is no longer sufficient.

The required intermediate layer is:

- a TIM field/schema map,
- a PAR parameter dictionary,
- a correction-state and provenance layer.

This layer prepares the project for a later controlled value-reading gate.

It does not open that gate.

This note does not inspect raw artifacts.

This note does not compute residuals.

This note does not fit timing models.

This note does not interpret values physically.

This note does not make QSB-ST Bridge-related claims.

## 2. Upstream basis

The upstream content-structure review established:

TIM structure:

- total_tim_lines = 10939
- total_tim_data_like_lines = 7421
- 7419 rows with 41 columns
- malformed_like = 0

PAR structure:

- total_par_lines = 456
- total_parameter_like_lines = 456
- unique_parameter_names = 453
- duplicate_parameter_name_count = 3
- visible lexical groups include DMX, DMXEP, DMXF1, DMXF2, DMXR1, DMXR2

SHAPIROINFO56 established the active method boundary:

- correction_state_layer = REQUIRED_BEFORE_VALUE_READING
- allowed_scope = DICTIONARY_SCHEMA_CORRECTION_STATE_ONLY
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- bridge_claim_gate = CLOSED

## 3. Design principle

The field dictionary, schema map, and correction-state layer must make the data technically readable without turning readability into interpretation.

The layer may answer:

- Which TIM columns exist by position?
- Which TIM row classes exist?
- Which TIM column-count pattern dominates?
- Which PAR parameter names exist?
- Which PAR lexical groups exist?
- Which value-format classes occur?
- Which parameters are duplicated?
- Which correction-state fields are known, unknown, unresolved, or require public documentation?
- Which provenance fields are required before value reading?

The layer must not answer:

- What do the TIM values physically mean?
- What do the PAR values physically mean?
- Which values support a Shapiro-information residual?
- Which values support QSB-ST?
- Which parameters should be fitted?
- Which data rows are anomalous?
- Which model is physically preferred?

## 4. TIM schema-map specification

A later SHAPIROINFO58 or SHAPIROINFO57 implementation step may produce a TIM schema map.

Allowed TIM schema fields:

- source_file
- relative_path
- row_class
- apparent_column_count
- column_position
- observed_token_format_class
- missing_value_marker_present
- delimiter_hint
- row_count_for_column_count
- example_token_snippet_capped
- schema_confidence
- semantic_status

Allowed semantic_status values:

- structure_observed
- public_documentation_required
- unresolved
- forbidden_to_interpret

The TIM schema map may record column positions.

It may record token format classes.

It may record that 7419 rows have 41 columns.

It may not assign physical meaning to a column unless a later explicit documentation-gated step authorizes source-backed semantic mapping.

## 5. PAR field-dictionary specification

A later implementation step may produce a PAR parameter dictionary.

Allowed PAR dictionary fields:

- source_file
- relative_path
- parameter_name
- prefix_group
- separator_type
- value_format_class
- occurrence_count
- duplicate_flag
- raw_value_presence_flag
- documentation_status
- semantic_status
- correction_state_relevance
- provenance_requirement

Allowed documentation_status values:

- observed_in_file
- public_documentation_required
- source_documented
- unresolved
- not_applicable

Allowed semantic_status values:

- name_observed
- lexical_group_observed
- format_observed
- public_documentation_required
- unresolved
- forbidden_to_interpret

The PAR dictionary may list parameter names.

It may group parameters lexically.

It may document value-format classes.

It may identify duplicate names.

It must not interpret parameter values physically.

It must not classify parameters as QSB-relevant.

It must not silently map parameter names to physical meanings without a later explicit source-backed documentation step.

## 6. Correction-state layer specification

The correction-state layer is required before any value-reading gate.

Required correction-state fields:

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

Allowed correction-state values:

- known_from_file
- known_from_public_documentation
- inferred_from_structure
- unresolved
- not_applicable
- forbidden_to_assume

Unknown is acceptable.

Unresolved is acceptable.

Not applicable is acceptable.

Silent assumptions are not acceptable.

## 7. Provenance layer specification

Every dictionary or schema field that may later affect value reading must carry provenance.

Required provenance fields:

- provenance_source_type
- provenance_source_path
- provenance_source_reference
- provenance_confidence
- provenance_note

Allowed provenance_source_type values:

- observed_in_generated_inventory
- observed_in_content_structure_output
- observed_in_raw_file_readonly
- public_release_documentation_required
- public_release_documentation_confirmed
- unresolved

Allowed provenance_confidence values:

- high
- medium
- low
- unresolved

No semantic claim may be made without an explicit provenance source.

## 8. Required output files for a later implementation

A later implementation block may create a script that writes outputs under:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO57_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE/

Recommended output files:

- tim_schema_map.csv
- tim_schema_summary.json
- par_field_dictionary.csv
- par_prefix_group_dictionary.csv
- par_duplicate_parameter_report.csv
- correction_state_template.csv
- correction_state_summary.json
- provenance_requirements.csv
- field_dictionary_schema_correction_state_readout.md
- field_dictionary_schema_correction_state_config_resolved.json

These outputs are run artifacts first.

They are not automatically tracked.

## 9. Requirements for the later implementation script

Recommended later block:

SHAPIROINFO58_TIM_PAR_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_SCRIPT

The script must:

- read existing SHAPIROINFO54 content-structure outputs
- optionally read raw TIM/PAR files read-only only if explicitly authorized
- not modify raw artifacts
- not copy raw artifacts into tracked paths
- not compute timing residuals
- not fit timing models
- not interpret values physically
- not classify values as anomalies
- not claim QSB-ST Bridge support
- produce machine-readable CSV/JSON outputs
- produce a human-readable readout
- preserve unknown and unresolved states
- report assumptions explicitly
- refuse silent semantic mapping

## 10. First value-reading gate dependency

A later first controlled value-reading gate must not be opened until this dictionary/schema/correction-state layer exists.

The later value-reading gate may be planned as:

SHAPIROINFO59_FIRST_CONTROLLED_VALUE_READING_GATE_PLAN

That later gate may consider limited value-level questions such as:

- Which numeric fields are present?
- Which fields carry missing-value markers?
- Which value ranges are present at a purely descriptive level?
- Which columns or parameters require public documentation before interpretation?
- Is there an existing residual-like column, or would residuals require external timing-tool generation?

Even that later gate must not automatically allow:

- residual computation,
- model fitting,
- anomaly claims,
- QSB-ST Bridge claims,
- physical interpretation.

## 11. Stop conditions

The route must stop or downgrade if:

- TIM columns cannot be mapped without undocumented assumptions
- PAR parameter names cannot be mapped without semantic overreach
- correction-state fields cannot be represented
- public documentation is required but unavailable
- a later value-reading step would require silent assumptions
- residual computation is required before correction-state documentation
- any output begins to frame values as evidence
- dictionary/schema mapping becomes physical interpretation by stealth

A stop condition is a valid scientific result.

## 12. Claim boundary

This note is a method-layer specification within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only specifies the field dictionary, TIM/PAR schema map, and correction-state/provenance layer required before any later controlled value-reading gate can be considered.
