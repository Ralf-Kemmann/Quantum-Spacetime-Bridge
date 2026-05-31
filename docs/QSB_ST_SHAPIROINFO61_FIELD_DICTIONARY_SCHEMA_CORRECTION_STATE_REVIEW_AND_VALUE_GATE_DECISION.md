# QSB-ST SHAPIROINFO61 — Field Dictionary, Schema, Correction-State Review and Value-Gate Decision

Date: 2026-06-01  
Status: dictionary / schema / correction-state review and value-gate decision  
Upstream result: SHAPIROINFO60_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_RESULT_NOTE  
Decision type: next-gate posture after dictionary/schema/correction-state layer  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note reviews the SHAPIROINFO60 dictionary/schema/correction-state result and decides the next gate posture.

The project has now created a method-layer bridge between TIM/PAR content-structure review and any possible later controlled value-reading gate.

This note decides whether the project may proceed directly to value reading, whether additional documentation is required, or whether the route should stop.

This note does not inspect raw artifacts.

This note does not read TIM or PAR values.

This note does not compute residuals.

This note does not fit timing models.

This note does not make anomaly claims.

This note does not make QSB-ST Bridge-related claims.

## 2. Upstream result reviewed

SHAPIROINFO60 documented the SHAPIROINFO59 output layer.

The generated layer contains:

- TIM schema map
- PAR field dictionary
- PAR prefix-group dictionary
- duplicate-parameter report
- correction-state template
- provenance-requirements table

TIM schema result:

- tim_schema_records = 43
- dominant_column_count = 41
- dominant_column_count_rows = 7419
- secondary_column_count_patterns = [{'apparent_column_count': 2, 'row_count': 2}]
- semantic_mapping_status = not_performed

PAR dictionary result:

- par_field_dictionary.csv contains 453 rows
- par_prefix_group_dictionary.csv contains 46 rows
- duplicate parameters reported: ECORR, T2EFAC, T2EQUAD

Correction-state result:

- correction_state_fields_defined = 17
- unresolved_default_count = 17
- correction_state_layer_status = template_created
- value_reading_gate_status = not_opened

Provenance result:

- provenance_requirements.csv contains 5 rows
- semantic claims are marked false

## 3. Review interpretation

The dictionary/schema/correction-state layer is complete at the current method depth.

The TIM structure is now represented as a schema map without semantic mapping.

The PAR parameter names are now represented as a field dictionary without physical interpretation.

The duplicate parameters are explicitly flagged for follow-up.

The correction-state layer exists, but all 17 correction-state fields remain unresolved by default.

This is acceptable at the dictionary/schema stage.

It is not sufficient for physical interpretation.

The unresolved correction-state layer is the central reason why a full value-reading or residual-analysis gate must remain closed.

## 4. Value-gate posture

Decision:

- direct_value_reading_gate = NOT_OPENED
- residual_analysis_gate = CLOSED
- model_fitting_gate = CLOSED
- anomaly_claim_gate = CLOSED
- bridge_claim_gate = CLOSED
- next_scope = PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_BEFORE_VALUE_READING
- next_step = SHAPIROINFO62_PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_PLAN
- following_possible_gate = SHAPIROINFO63_FIRST_CONTROLLED_VALUE_READING_GATE_PLAN
- allowed_scope = DOCUMENTATION_MAPPING_AND_CORRECTION_STATE_RESOLUTION_ONLY
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- research_status = PHYSICS_MOTIVATED_ACTIVE_ROUTE

The project should not proceed directly from dictionary/schema generation to value reading.

The next appropriate step is to resolve public documentation and correction-state requirements enough to decide whether a first controlled value-reading gate is defensible.

## 5. Why value reading is not opened yet

The correction-state template contains 17 unresolved fields.

This means the workflow has not yet established, in documented form, which relevant timing-data layers are raw, processed, clock-adjusted, ephemeris-dependent, DM-corrected, solarwind-corrected, noise-modeled, backend-jump-affected, whitened, or otherwise model-layered.

The provenance table correctly blocks semantic claims.

Therefore, value reading without documentation mapping would risk silent assumptions.

Silent assumptions are not acceptable.

Unknown or unresolved states are acceptable only if they remain explicitly marked as unknown or unresolved.

## 6. Allowed scope for SHAPIROINFO62

SHAPIROINFO62 may define a plan to map public documentation and correction-state fields.

Allowed tasks:

- identify which public release documentation is required
- define documentation sources that must be checked
- define correction-state fields to resolve
- define which fields may remain unresolved
- define how unresolved fields block value reading
- define source-backed semantic mapping rules
- define provenance requirements for any future field meaning
- define stop conditions if documentation is unavailable

SHAPIROINFO62 may prepare later source-backed semantic mapping.

It may not perform physical value interpretation.

It may not compute residuals.

It may not fit timing models.

It may not classify anomalies.

It may not claim QSB-ST Bridge support.

## 7. Required documentation targets

The next documentation-resolution layer should cover at least:

- TIM file format documentation
- PAR file format documentation
- public release notes for the current source package
- timing-model tool convention documentation if needed
- clock-correction documentation if available
- ephemeris documentation if available
- DM / dispersion correction documentation if available
- solarwind correction documentation if available
- noise-model documentation if available
- backend jump / system parameter documentation if available
- provenance of the downloaded public package
- checksum and local quarantine state already documented upstream

If a documentation target is unavailable, the corresponding correction-state field must remain unresolved.

Unresolved is acceptable.

Assumed is not acceptable.

## 8. Duplicate-parameter follow-up

The duplicate-parameter report identified:

- ECORR
- T2EFAC
- T2EQUAD

These duplicate parameters require follow-up before any value-reading gate.

The follow-up should determine only:

- whether duplicates are expected in the relevant file convention
- whether duplicates are system-, backend-, band-, or flag-scoped
- whether public documentation is required before interpretation
- whether duplicates must remain unresolved

This follow-up must not interpret the duplicate parameter values physically.

It must not rank them by physical relevance.

It must not select them for fitting.

## 9. First controlled value-reading gate precondition

A future first controlled value-reading gate may be planned only if SHAPIROINFO62 establishes a documentation and correction-state posture.

Minimum preconditions:

- TIM/PAR format documentation targets identified
- correction-state fields reviewed
- unresolved fields explicitly listed
- duplicate-parameter follow-up specified
- provenance source types defined
- semantic mapping rules defined
- value-reading scope limited to descriptive inspection only
- residual computation remains forbidden
- model fitting remains forbidden
- physical interpretation remains forbidden
- Bridge claims remain forbidden

## 10. Stop conditions

The route must stop or downgrade if:

- public documentation cannot be identified
- correction-state fields cannot be mapped or explicitly marked unresolved
- duplicate parameters cannot be documented without semantic assumptions
- TIM column meanings require undocumented inference
- PAR parameter meanings require undocumented inference
- value reading would require assuming correction state
- residual computation is needed before correction-state documentation
- any next output would frame values as physical evidence

A stop condition is a valid scientific result.

## 11. Claim boundary

This note is a next-gate decision within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only decides that direct value reading remains closed until public documentation and correction-state requirements are reviewed and resolved or explicitly marked unresolved.
