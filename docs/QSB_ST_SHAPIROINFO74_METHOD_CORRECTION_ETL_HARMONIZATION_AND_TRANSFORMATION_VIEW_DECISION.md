# QSB-ST SHAPIROINFO74 — Method Correction: ETL Harmonization and Transformation-View Decision

Date: 2026-06-02  
Status: method correction / ETL harmonization / transformation-view decision  
Upstream state: SHAPIROINFO73_PUBLIC_DOCUMENTATION_CONTENT_REVIEW_EXECUTION  
Decision type: method correction before download, value-reading, residual, or interpretation gates  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note records a methodological correction after SHAPIROINFO73.

The documentation path remains important.

It demonstrated source discipline, correction-state awareness, provenance control, and claim-boundary control.

However, the project must avoid turning documentation into a top-down preselection filter.

The project must not allow only those patterns that the documentation path already expects.

The measurement remains primary.

Gates, notes, schemas, documentation layers, and claim-boundary documents are methodological safeguards.

They are not authorities over what may be observed.

Therefore, the project introduces a separate real-data ETL / harmonization / blind-descriptive value track before any interpretation gate.

## 2. Upstream state

SHAPIROINFO73 executed a content review of already identified public documentation sources.

The reported state was:

- source_candidates_reviewed_count = 18
- documentation_targets_supported_by_content = 16
- documentation_targets_unresolved_after_content_review = 1
- correction_state_fields_supported_by_content = 16
- correction_state_fields_unresolved_after_content_review = 1
- duplicate_parameter_topics_with_content_support = 3
- sources_requiring_download_for_full_review = 3

The unresolved documentation target remains:

- profile_template_conventions

The unresolved correction-state field remains:

- profile_template_state

The active gates remain closed:

- direct_value_reading_gate = not_opened
- residual_analysis_gate = closed
- model_fitting_gate = closed
- bridge_claim_gate = closed

No raw artifacts were inspected.

No TIM/PAR values were read.

No documentation or data files were downloaded.

No physical value interpretation, residual search, model fitting, anomaly claim, or QSB-ST Bridge confirmation claim was made.

## 3. Method concern

The project has built a careful documentation and correction-state path.

That path is useful as interpretation protection.

It helps avoid wrong units, wrong tool assumptions, wrong correction-state assumptions, and unsupported semantic mapping.

However, if the documentation path becomes the gatekeeper for what may be observed, it creates a bias risk.

The risk is:

- only expected fields are allowed into analysis,
- only documented patterns are treated as visible,
- unexpected values are filtered before being seen,
- outliers are treated as noise before being understood,
- future context is lost because current documentation did not predict it.

This would be methodologically wrong.

The project must not preselect reality to fit expectation.

## 4. Real-data principle

Real data differ from test data.

Real data may contain:

- missing values,
- blanks,
- null and not-null inconsistencies,
- type mismatches,
- numeric values encoded as strings,
- string values where categories are expected,
- scale issues,
- exponent or power-of-ten problems,
- unit heterogeneity,
- implicit defaults,
- legacy tool conventions,
- comments or flags embedded in data streams,
- file-format differences,
- mappings required for comparability.

These features must be handled as real-data engineering problems.

They must not be hidden by theory assumptions.

## 5. ETL / harmonization decision

Decision:

- next_scope = ETL_HARMONIZATION_AND_BLIND_DESCRIPTIVE_VALUE_TRACK
- next_step = SHAPIROINFO75_ETL_HARMONIZATION_AND_BLIND_VALUE_VIEW_PLAN
- following_possible_step = SHAPIROINFO76_ETL_HARMONIZATION_SCHEMA_AND_TRANSFORMATION_RULES_SPEC
- later_possible_step = SHAPIROINFO77_CONTROLLED_BLIND_DESCRIPTIVE_VALUE_READING_EXECUTION
- documentation_track_status = INTERPRETATION_SAFEGUARD
- etl_track_status = REQUIRED_FOR_REAL_DATA_HANDLING
- transformation_view_track_status = REQUIRED_FOR_CROSS_DOMAIN_VALUE_MAPPING
- allowed_scope = ETL_DESIGN_HARMONIZATION_RULES_AND_BLIND_DESCRIPTIVE_VIEW_PLANNING
- preselection_for_expectation_fitting = FORBIDDEN
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- anomaly_claim_gate = CLOSED
- bridge_claim_gate = CLOSED
- direct_value_reading_gate = NOT_OPENED
- research_status = PHYSICS_MOTIVATED_REAL_DATA_METHOD_ENGINEERING

The project should not continue directly to download-gate or value-reading-gate logic without first defining the ETL / harmonization track.

## 6. ETL track role

The ETL track has three roles.

Extract:

- read data technically when later authorized,
- preserve raw fields,
- preserve observed rows,
- preserve observed tokens,
- identify file structure,
- avoid physical interpretation.

Transform:

- harmonize data types,
- normalize units only when source support exists,
- document scaling rules,
- document casts,
- document mappings,
- document missing-value handling,
- document blanks and null logic,
- document file-format normalization,
- quarantine only technical parse failures.

Load:

- produce a harmonized blind-descriptive value view,
- keep all observed fields unless explicitly quarantined for technical reasons,
- preserve unresolved fields,
- preserve unexpected values,
- preserve outliers,
- preserve block structures and missingness.

## 7. Harmonization boundary

Harmonization is allowed for comparability.

Preselection for expectation-fitting is forbidden.

Allowed:

- datatype harmonization,
- unit harmonization toward SI where source-supported,
- scale normalization where explicitly documented,
- cast rules,
- mapping rules,
- missing-value markers,
- blank/null handling,
- technical file-format normalization,
- preservation of raw token references,
- transformation-rule documentation.

Forbidden:

- removing values because they are unexpected,
- dropping fields because they do not fit the current idea,
- filtering outliers before blind-descriptive review,
- smoothing values,
- correcting values without a documented rule,
- selecting only QSB-interesting parameters,
- treating documentation targets as relevance filters,
- interpreting physical meaning,
- computing residuals,
- fitting models,
- making anomaly claims.

## 8. Blind-descriptive value view

A later blind-descriptive value view may describe data technically.

Allowed future descriptive questions include:

- Which columns or fields are present?
- Which fields are numeric, categorical, textual, or mixed?
- Which values are missing, blank, null-like, or flagged?
- Which value ranges occur?
- Which fields are constant?
- Which fields vary?
- Which block structures appear?
- Which repeated patterns appear?
- Which numeric outliers appear?
- Which fields require casts or mappings?
- Which fields require unit or scale harmonization?

Forbidden at that stage:

- physical interpretation,
- residual calculation,
- model fitting,
- Shapiro-effect search,
- QSB-ST Bridge interpretation,
- anomaly claim,
- field relevance preselection.

## 9. Transformation-view track

The project may later define transformation views across theory-side quantities.

This is a data-model idea.

It should be expressed as documented transformation rules and views.

The goal is to represent values from one domain through values of another domain where valid functional relations exist.

Example concept:

- de Broglie-side quantities,
- relativity-side quantities,
- constants,
- units,
- dimensions,
- observer-dependence,
- transformation rules,
- invertibility status,
- validity conditions,
- assumptions,
- provenance.

A later transformation view may support mappings such as:

- expressing a de Broglie-side momentum through relativity-side quantities,
- expressing a wavelength through energy, mass, constants, and velocity-related relations,
- representing right-side and left-side values through documented functional relations.

This is not a physical validation claim.

It is a data-model / mapping-layer / transformation-view design.

## 10. Data-model implication

The project may later define tables such as:

- quantity_catalog
- quantity_domain_catalog
- transformation_rule_catalog
- unit_dimension_catalog
- transformation_view_catalog
- etl_transformation_log
- harmonized_value_view
- blind_descriptive_value_summary

Each transformation must carry:

- source fields,
- target fields,
- formula or mapping rule,
- units,
- dimensions,
- constants required,
- validity conditions,
- observer/frame dependence if applicable,
- source/provenance status,
- reversibility or invertibility status,
- transformation timestamp or version,
- claim boundary.

No transformation rule may be silently assumed.

## 11. Documentation track role after this correction

The documentation track remains active.

Its role is:

- interpretation safeguard,
- correction-state guard,
- source discipline,
- provenance control,
- claim-boundary support.

Its role is not:

- relevance preselection,
- data filtering,
- pattern suppression,
- expectation-fitting,
- deciding what may be observed.

The documentation track and ETL track should run as complementary tracks.

## 12. Future three-track structure

The project should proceed with three method tracks:

Track A — Documentation / Correction-State

Purpose:

- protect interpretation,
- document source support,
- identify correction-state assumptions,
- keep claims bounded.

Track B — ETL / Harmonized Blind Value View

Purpose:

- handle real data,
- harmonize technical comparability,
- preserve unexpected patterns,
- produce blind-descriptive views.

Track C — Reconciliation / Interpretation Gate

Purpose:

- later compare documented meaning with blind-descriptive observations,
- decide whether interpretation is allowed,
- keep residual, fit, anomaly, and Bridge claims separately gated.

## 13. Stop conditions

The route must stop or downgrade if:

- ETL steps begin to remove inconvenient data,
- harmonization becomes manipulation,
- documentation becomes preselection,
- missingness or outliers are hidden,
- transformations are applied without documented rules,
- units or scales are assumed without source support,
- value reading begins before ETL rules are defined,
- physical interpretation is attached to blind-descriptive outputs,
- transformation views are treated as physical validation.

A stop condition is a valid scientific result.

## 14. Claim boundary

This note is a methodological correction within a physics-motivated real-data research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It does not read TIM or PAR values.

It only records that the project must add an ETL / harmonization / blind-descriptive value track and a later transformation-view design so that real data can be handled respectfully, comparably, and without expectation-fitting preselection.
