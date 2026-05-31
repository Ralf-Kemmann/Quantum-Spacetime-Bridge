# QSB-ST SHAPIROINFO67 — Public Documentation Resolution Review and Research-Gate Decision

Date: 2026-06-01  
Status: public-documentation resolution review and research-gate decision  
Upstream result: SHAPIROINFO66_PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_RESULT_NOTE  
Decision type: public documentation research gate decision before value-reading gate  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note reviews the SHAPIROINFO66 public-documentation and correction-state resolution result and decides whether a narrowly scoped public documentation research gate may be opened.

The project has generated a structured list of documentation targets, correction-state fields, duplicate-parameter follow-up items, semantic mapping rules, and provenance requirements.

However, no public documentation has yet been researched or downloaded.

The current question is therefore not whether values may be read.

The current question is whether the project may begin controlled public documentation research to identify source-backed documentation for TIM/PAR formats, timing-tool conventions, correction-state fields, and provenance requirements.

This note does not perform that research.

This note does not download documentation.

This note does not inspect raw artifacts.

This note does not read TIM or PAR values.

This note does not compute residuals.

This note does not fit timing models.

This note does not make anomaly claims.

This note does not make QSB-ST Bridge-related claims.

## 2. Upstream result reviewed

SHAPIROINFO66 documented the SHAPIROINFO65 execution.

The generated documentation/correction-state layer contains:

- public_documentation_targets.csv: 16 rows
- correction_state_resolution_table.csv: 17 rows
- duplicate_parameter_followup_table.csv: 3 rows
- semantic_mapping_rules.csv: 5 rows
- provenance_resolution_requirements.csv: 7 rows

The key status values are:

- documentation_target_count = 16
- correction_state_field_count = 17
- unresolved_correction_state_count = 17
- duplicate_parameter_followup_count = 3
- semantic_mapping_status = not_performed
- direct_value_reading_gate = not_opened
- residual_analysis_gate = closed
- model_fitting_gate = closed
- bridge_claim_gate = closed
- public_web_research_status = not_performed
- documentation_download_status = not_performed
- raw_artifact_access_status = not_performed

This means the workflow has a research-ready documentation target map, but has not yet performed public documentation research.

## 3. Review interpretation

The documentation/correction-state table layer is complete at the current method depth.

It defines what must be researched before semantic mapping or value reading can be considered.

The unresolved correction-state count remains 17.

This is not a failure.

It is the expected state before public documentation research.

The project should not open a value-reading gate while all correction-state fields remain unresolved.

The project may open a narrowly scoped public documentation research gate because the required documentation targets are now explicitly listed and bounded.

## 4. Decision

Decision:

- next_scope = PUBLIC_DOCUMENTATION_RESEARCH_GATE
- next_step = SHAPIROINFO68_PUBLIC_DOCUMENTATION_RESEARCH_PLAN
- following_possible_step = SHAPIROINFO69_PUBLIC_DOCUMENTATION_RESEARCH_EXECUTION
- later_possible_gate = SHAPIROINFO70_CORRECTION_STATE_RESOLUTION_REVIEW_AND_VALUE_READING_GATE_DECISION
- allowed_scope = PUBLIC_DOCUMENTATION_IDENTIFICATION_ONLY
- public_web_research_gate = OPENED_NARROWLY
- documentation_download_gate = CLOSED
- raw_artifact_access_gate = CLOSED
- direct_value_reading_gate = NOT_OPENED
- residual_analysis_gate = CLOSED
- model_fitting_gate = CLOSED
- anomaly_claim_gate = CLOSED
- bridge_claim_gate = CLOSED
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- research_status = PHYSICS_MOTIVATED_ACTIVE_ROUTE

The project may proceed to a public documentation research plan.

The project may identify public documentation sources.

The project may record source metadata, URLs, titles, publisher/project, topic coverage, and relevance to the documentation targets.

The project must not download documentation files unless a later explicit documentation-download gate is opened.

The project must not read TIM/PAR values, compute residuals, fit models, or make physical claims.

## 5. Allowed scope for SHAPIROINFO68

SHAPIROINFO68 may create a plan for public documentation research.

Allowed tasks:

- define target documentation classes to search
- define preferred source hierarchy
- define source metadata fields
- define relevance categories
- define documentation-target coverage fields
- define citation/provenance capture fields
- define stop conditions
- define whether the research should be done by Deep Research, browser/search, local Codex, or a combination
- define how found sources will be recorded without downloading documents

Allowed source classes:

- official NANOGrav or relevant public release documentation
- official pulsar timing dataset documentation
- official TEMPO / TEMPO2 / PINT documentation
- peer-reviewed pulsar timing / PTA release papers
- official project GitHub or documentation pages
- official data-release pages
- arXiv or journal landing pages for relevant release papers
- authoritative timing-format references

SHAPIROINFO68 may not perform the research itself.

## 6. Forbidden scope for SHAPIROINFO68

SHAPIROINFO68 must not:

- perform public web searches
- download PDFs or data files
- inspect raw artifacts
- read TIM/PAR values
- compute residuals
- fit timing models
- interpret values physically
- classify anomalies
- claim Shapiro-information residual evidence
- claim QSB-ST Bridge support
- create publication-facing evidence summaries
- silently map field names or parameter names to physical meanings

## 7. Research-source priority

A later research execution should prioritize source classes in this order:

1. Official data-release documentation for the current public source package.
2. Official timing-tool documentation for formats and conventions.
3. Peer-reviewed release papers describing the dataset and corrections.
4. Official repositories or documentation pages maintained by the relevant collaboration or tool project.
5. Secondary explanatory sources only if primary sources are unavailable.

Secondary sources may support orientation.

Secondary sources must not carry primary provenance for semantic mapping or correction-state resolution.

## 8. Documentation targets to cover

The research plan should cover the 16 documentation target classes already generated:

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

The plan should allow targets to remain unresolved if public documentation cannot be identified.

Unresolved is acceptable.

Assumed is not acceptable.

## 9. Correction-state coverage

The research plan should support later correction-state resolution for the 17 fields already defined:

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

The research plan should not resolve these fields by intuition.

A later execution may only mark a field as supported if a source is identified and the source actually addresses the field.

## 10. Metadata required for found sources

A later public documentation research execution should record at least:

- source_id
- source_title
- source_type
- source_url_or_reference
- source_provider_or_project
- publication_or_release_year
- documentation_target_classes_covered
- correction_state_fields_covered
- semantic_mapping_relevance
- value_reading_relevance
- download_required
- access_status
- provenance_confidence
- notes

No source should be treated as sufficient merely because it appears relevant by title.

Coverage must be target-specific.

## 11. Download posture

The documentation-download gate remains closed.

Allowed:

- identify candidate source URLs
- record metadata
- record relevance to documentation targets
- record whether a download may be needed later
- record if a source is a web page, paper landing page, official docs page, repository page, or release page

Forbidden:

- download PDFs
- download data
- copy documentation into the repository
- track downloaded documentation
- scrape or mirror external documentation
- treat a source as resolved without reviewing its content in a later authorized step

If documentation download becomes necessary, a later explicit gate must be opened.

## 12. Stop conditions

The route must stop or downgrade if:

- public documentation cannot be identified for essential targets
- available documentation is too ambiguous for semantic mapping
- correction-state fields cannot be supported by identified sources
- research begins to substitute assumption for documentation
- value reading would require unresolved correction-state fields to be treated as known
- documentation research starts to become physical interpretation
- any output frames documentation discovery as physical evidence

A stop condition is a valid scientific result.

## 13. Claim boundary

This note is a public documentation research-gate decision within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only opens a narrow gate to plan public documentation research for source identification and provenance preparation.
