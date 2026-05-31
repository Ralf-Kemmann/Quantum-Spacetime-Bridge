# QSB-ST SHAPIROINFO62 — Public Documentation and Correction-State Resolution Plan

Date: 2026-06-01  
Status: public-documentation and correction-state resolution plan  
Upstream decision: SHAPIROINFO61_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_REVIEW_AND_VALUE_GATE_DECISION  
Plan type: documentation / correction-state resolution before value-reading gate  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note defines the public-documentation and correction-state resolution plan required before any first controlled value-reading gate can be considered.

SHAPIROINFO61 decided that direct value reading remains closed because the correction-state layer exists but remains unresolved.

The current task is therefore not to read values.

The current task is to define what public documentation and correction-state information must be checked, recorded, or explicitly left unresolved before a later value-reading gate can be responsibly planned.

This note does not inspect raw artifacts.

This note does not read TIM or PAR values.

This note does not compute residuals.

This note does not fit timing models.

This note does not make anomaly claims.

This note does not make QSB-ST Bridge-related claims.

## 2. Upstream state

The current method layer contains:

- TIM schema map
- PAR field dictionary
- PAR prefix-group dictionary
- duplicate-parameter report
- correction-state template
- provenance-requirements table

Known SHAPIROINFO60/61 facts:

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

The central unresolved issue is correction-state status.

## 3. Planning decision

Decision:

- next_scope = PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_SPEC
- next_step = SHAPIROINFO63_PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_SPEC
- following_possible_gate = SHAPIROINFO64_FIRST_CONTROLLED_VALUE_READING_GATE_PLAN
- allowed_scope = DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_ONLY
- direct_value_reading_gate = NOT_OPENED
- residual_analysis_gate = CLOSED
- model_fitting_gate = CLOSED
- anomaly_claim_gate = CLOSED
- bridge_claim_gate = CLOSED
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- research_status = PHYSICS_MOTIVATED_ACTIVE_ROUTE

The project may proceed to a documentation and correction-state resolution specification.

The project must not proceed directly to value reading, residual computation, model fitting, anomaly search, or Bridge interpretation.

## 4. Documentation targets

The next specification must identify public documentation targets for at least:

- TIM file format
- PAR file format
- the current public source package
- timing-model tool conventions
- clock-correction conventions
- ephemeris conventions
- DM / dispersion correction conventions
- solarwind correction conventions
- noise-model conventions
- backend jump / system parameter conventions
- frequency-band conventions
- profile-template conventions
- observatory / backend / receiver system conventions
- checksum / provenance / quarantine state already documented upstream

Each target must be assigned one of the following planned statuses:

- documentation_required
- documentation_identified
- documentation_unavailable
- not_applicable
- unresolved

No target may be silently assumed.

## 5. Correction-state fields to resolve

The correction-state resolution layer must address the 17 fields already defined:

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

Allowed correction-state outcomes:

- known_from_file
- known_from_public_documentation
- inferred_from_structure
- unresolved
- not_applicable
- forbidden_to_assume

At this stage, unresolved remains acceptable.

Assumed remains unacceptable.

## 6. Duplicate-parameter documentation follow-up

The duplicate parameter report identified:

- ECORR
- T2EFAC
- T2EQUAD

The next specification must define how to document these duplicates without interpreting their values physically.

Allowed duplicate-parameter questions:

- Are duplicate entries expected by the relevant TIM/PAR or timing-tool convention?
- Are duplicate entries scoped by backend, receiver system, observing band, flag, or data subset?
- Is public documentation required before interpreting duplicate entries?
- Should the duplicate state remain unresolved?

Forbidden duplicate-parameter questions:

- What do the duplicate values imply physically?
- Which duplicate values matter for residuals?
- Which duplicate values should be fitted?
- Do duplicates indicate anomaly candidates?
- Do duplicates support QSB-ST?

## 7. Semantic mapping posture

Current status:

- semantic_mapping_status = not_performed
- semantic claims marked false

This posture remains active.

The next specification may define source-backed semantic mapping rules.

It may not perform semantic mapping unless the relevant documentation source has been identified and a later explicit step authorizes the mapping.

Allowed semantic mapping statuses:

- not_performed
- documentation_required
- source_documentation_identified
- source_documentation_unavailable
- unresolved
- forbidden_to_infer

No field or parameter name may be mapped to physical meaning by intuition alone.

## 8. Minimum requirements before a future value-reading gate

A future first controlled value-reading gate may be considered only after the documentation/correction-state layer has produced:

- list of required public documentation targets
- documentation status for each target
- correction-state status for each of the 17 fields
- explicit unresolved field list
- duplicate-parameter follow-up posture
- semantic mapping rule set
- provenance rule set
- stop conditions for missing documentation
- clear statement that residual computation remains closed
- clear statement that model fitting remains closed
- clear statement that physical interpretation remains closed

The value-reading gate may still remain closed after this step.

## 9. Allowed outputs for a later implementation

A later documentation-resolution script or documentation note may produce:

- public_documentation_targets.csv
- correction_state_resolution_table.csv
- duplicate_parameter_followup_table.csv
- semantic_mapping_rules.csv
- provenance_resolution_requirements.csv
- documentation_resolution_summary.json
- public_documentation_correction_state_readout.md

These outputs should be written under:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO63_PUBLIC_DOCUMENTATION_CORRECTION_STATE_RESOLUTION/

Outputs are run artifacts first unless explicitly reviewed and tracked later.

## 10. Stop conditions

The route must stop or downgrade if:

- public documentation targets cannot be identified
- documentation cannot support semantic mapping
- correction-state fields remain too unresolved for value reading
- duplicate parameters cannot be documented without physical assumptions
- TIM column meaning would require undocumented inference
- PAR parameter meaning would require undocumented inference
- value reading would require assuming correction-state status
- residual computation would be needed before correction-state resolution
- any output begins to frame values as physical evidence

A stop condition is a valid scientific result.

## 11. Claim boundary

This note is a documentation and correction-state resolution plan within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only defines the documentation and correction-state resolution work required before a later first controlled value-reading gate can be considered.
