# QSB-ST SHAPIROINFO56 — Field Dictionary, Schema, and Correction-State Decision

Date: 2026-05-31  
Status: field dictionary / schema / correction-state decision  
Upstream result: SHAPIROINFO55_TIM_PAR_CONTENT_STRUCTURE_REVIEW_RESULT_NOTE  
External review state: Red-Team and Deep Research reviewed before this decision  
Decision type: next-method-scope decision before any value-reading or analysis gate  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note records the SHAPIROINFO56 decision after the TIM/PAR content-structure review and the external Red-Team / Deep Research review.

The project has moved beyond external file labels.

It has established that the TIM and PAR artifacts contain internally readable content structures at the allowed review depth.

The next step must therefore not be another purely external inventory step.

However, the next step must also not jump directly into physical value interpretation, timing residual search, anomaly detection, model fitting, or QSB-ST Bridge claims.

The purpose of this decision is to define the next defensible method layer:

- field dictionary,
- TIM/PAR schema map,
- correction-state and provenance layer.

This layer is required before any later first controlled value-reading gate can be responsibly considered.

## 2. Upstream technical state

SHAPIROINFO55 documented the following content-structure results.

TIM structure:

- total_tim_lines = 10939
- total_tim_data_like_lines = 7421
- column_count_min = 2
- column_count_max = 41
- 7419 rows with 41 columns
- malformed_like = 0

PAR structure:

- total_par_lines = 456
- total_parameter_like_lines = 456
- unique_parameter_names = 453
- duplicate_parameter_name_count = 3
- visible lexical groups include DMX, DMXEP, DMXF1, DMXF2, DMXR1, DMXR2

This establishes that the TIM/PAR artifacts are not merely identifiable by file extension.

They are content-bearing technical artifacts with reviewable internal organization.

## 3. External review synthesis

The Red-Team review converged on one central warning:

The project has been methodically disciplined, but further purely structural gating risks becoming gate inflation.

The Red-Team also converged on one central recommendation:

The next defensible step should be a neutral field/parameter dictionary and TIM/PAR schema-map layer, not immediate residual analysis.

The more aggressive review line urged the project to move toward physics and falsifiability.

That warning is accepted as a pressure against indefinite infrastructure work.

However, direct model fitting, residual search, anomaly search, or hypothesis testing is considered premature at SHAPIROINFO56 because the field dictionary, schema map, correction-state, and provenance layer have not yet been formalized.

Deep Research added a second essential constraint:

Correction state must become a first-class data field before any residual analysis.

A future value-reading or residual workflow must know whether values are raw, processed, corrected, whitened, clock-adjusted, ephemeris-dependent, DM-corrected, solarwind-corrected, backend-jump-affected, or otherwise model-layered.

Therefore, the next step must combine the Red-Team dictionary/schema recommendation with the Deep Research correction-state requirement.

## 4. Decision

Decision:

- next_scope = FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_LAYER
- next_step = SHAPIROINFO57_TIM_PAR_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_SPEC
- following_gate = SHAPIROINFO58_FIRST_CONTROLLED_VALUE_READING_GATE_PLAN
- allowed_scope = DICTIONARY_SCHEMA_CORRECTION_STATE_ONLY
- raw_artifact_access = NO_RAW_ACCESS_BY_THIS_NOTE
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- anomaly_claims = FORBIDDEN
- bridge_claim_gate = CLOSED
- correction_state_layer = REQUIRED_BEFORE_VALUE_READING
- research_status = PHYSICS_MOTIVATED_ACTIVE_ROUTE

The project may proceed to specify a field dictionary, TIM/PAR schema map, and correction-state/provenance layer.

The project must not proceed directly to timing residuals, value interpretation, model fitting, anomaly detection, or QSB-ST Bridge interpretation from this note.

## 5. Allowed scope for SHAPIROINFO57

SHAPIROINFO57 may define a specification for:

- TIM column-position inventory
- TIM table-schema map
- TIM row-class and delimiter documentation
- PAR parameter-name inventory
- PAR lexical prefix-group dictionary
- PAR duplicate-parameter documentation
- PAR value-format class dictionary
- source/provenance fields
- correction-state fields
- unknown/not-yet-resolved correction-state markers
- field origin markers such as:
  - observed_in_file
  - inferred_from_structure
  - public_documentation_required
  - unresolved
  - forbidden_to_interpret

SHAPIROINFO57 may prepare the structure needed for later value reading.

It may not read values physically.

## 6. Forbidden scope for SHAPIROINFO57

SHAPIROINFO57 must not:

- compute timing residuals
- fit timing models
- inspect values as physical evidence
- classify parameters by physical relevance
- claim anomaly candidates
- compare values with GR, QSB-ST, or alternative models
- infer a Shapiro-information residual
- claim QSB-ST Bridge support
- create publication-facing evidence summaries
- silently map parameter names to physical meanings without source/provenance control

## 7. Correction-state layer requirement

Deep Research made clear that correction state is not optional.

Before any future value-reading gate, the workflow must be able to represent at least:

- raw_or_processed_state
- timing_model_source
- clock_correction_state
- ephemeris_state
- DM_correction_state
- solarwind_correction_state
- noise_model_state
- backend_jump_state
- whitening_state
- provenance_reference
- unresolved_correction_fields

The correction-state layer may contain unknown or unresolved values.

Unknown is acceptable.

Silent assumptions are not acceptable.

## 8. Field dictionary and schema-map requirement

The field dictionary and schema-map layer should answer:

- Which TIM columns exist by position?
- Which row classes exist?
- Which delimiter and column-count patterns exist?
- Which PAR parameter names exist?
- Which PAR prefix groups exist?
- Which parameter names are duplicated?
- Which value-format classes occur?
- Which fields require public documentation before interpretation?
- Which fields are structurally known but semantically unresolved?

This is not yet physics analysis.

It is the technical bridge between readable content structure and any future controlled value-reading gate.

## 9. First value-reading gate preplanning

SHAPIROINFO58 may be planned as a first controlled value-reading gate.

However, SHAPIROINFO58 must be planned only after SHAPIROINFO57 defines the dictionary/schema/correction-state layer.

A future first value-reading gate may allow limited operations such as:

- reading selected numeric fields as values,
- checking value ranges,
- checking missing-value markers,
- identifying units or unit-like markers,
- documenting whether a residual column already exists or must be generated by an external timing tool.

It must still not automatically allow:

- timing residual computation,
- timing-model fitting,
- anomaly detection,
- physical interpretation,
- QSB-ST Bridge claims.

## 10. Stop conditions

The route must stop or downgrade if:

- TIM columns cannot be mapped without undocumented assumptions
- PAR parameter names cannot be documented without semantic overreach
- correction-state fields cannot be represented
- public documentation is required but unavailable
- any next step would require physical interpretation before dictionary/schema completion
- residual computation is required before correction-state documentation
- run outputs would be framed as evidence rather than method artifacts

A stop condition is a valid scientific result.

## 11. Claim boundary

This note is a next-scope decision within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only decides that the next defensible step is a field dictionary, TIM/PAR schema map, and correction-state/provenance layer before any later controlled value-reading gate can be considered.
