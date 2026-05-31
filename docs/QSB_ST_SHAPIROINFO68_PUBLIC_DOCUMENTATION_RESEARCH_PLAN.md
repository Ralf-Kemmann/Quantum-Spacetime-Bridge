# QSB-ST SHAPIROINFO68 — Public Documentation Research Plan

Date: 2026-06-01  
Status: public documentation research plan  
Upstream decision: SHAPIROINFO67_PUBLIC_DOCUMENTATION_RESOLUTION_REVIEW_AND_RESEARCH_GATE_DECISION  
Plan type: narrow public documentation identification plan  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note defines the public documentation research plan allowed by SHAPIROINFO67.

SHAPIROINFO67 opened a narrow public-web-research gate for documentation identification only.

The purpose of this plan is to define what may be searched, what metadata must be recorded, which source classes are preferred, and what remains forbidden.

This note does not perform public web research.

This note does not download documentation.

This note does not inspect raw artifacts.

This note does not read TIM or PAR values.

This note does not compute residuals.

This note does not fit timing models.

This note does not make anomaly claims.

This note does not make QSB-ST Bridge-related claims.

## 2. Upstream state

SHAPIROINFO66 documented the generated documentation/correction-state tables:

- public_documentation_targets.csv: 16 rows
- correction_state_resolution_table.csv: 17 rows
- duplicate_parameter_followup_table.csv: 3 rows
- semantic_mapping_rules.csv: 5 rows
- provenance_resolution_requirements.csv: 7 rows

SHAPIROINFO67 decided:

- public_web_research_gate = OPENED_NARROWLY
- documentation_download_gate = CLOSED
- raw_artifact_access_gate = CLOSED
- direct_value_reading_gate = NOT_OPENED
- residual_analysis_gate = CLOSED
- model_fitting_gate = CLOSED
- bridge_claim_gate = CLOSED
- allowed_scope = PUBLIC_DOCUMENTATION_IDENTIFICATION_ONLY

The current plan must preserve those boundaries.

## 3. Research decision

Decision:

- next_scope = PUBLIC_DOCUMENTATION_RESEARCH_EXECUTION
- next_step = SHAPIROINFO69_PUBLIC_DOCUMENTATION_RESEARCH_EXECUTION
- following_possible_step = SHAPIROINFO70_PUBLIC_DOCUMENTATION_RESEARCH_RESULT_NOTE
- later_possible_gate = SHAPIROINFO71_CORRECTION_STATE_RESOLUTION_REVIEW_AND_VALUE_READING_GATE_DECISION
- allowed_scope = PUBLIC_DOCUMENTATION_IDENTIFICATION_ONLY
- public_web_research = ALLOWED_FOR_SOURCE_IDENTIFICATION_ONLY
- documentation_download = FORBIDDEN
- raw_artifact_access = FORBIDDEN
- direct_value_reading_gate = NOT_OPENED
- residual_analysis_gate = CLOSED
- model_fitting_gate = CLOSED
- anomaly_claim_gate = CLOSED
- bridge_claim_gate = CLOSED
- physical_value_interpretation = FORBIDDEN
- residual_search = FORBIDDEN
- model_fitting = FORBIDDEN
- research_status = PHYSICS_MOTIVATED_ACTIVE_ROUTE

The project may perform a narrow public documentation search in the next execution block.

The project may identify public source pages, official documentation pages, release notes, tool documentation, and peer-reviewed release papers.

The project may record metadata and target coverage.

The project must not download documentation files or data files.

## 4. Primary research targets

The public documentation search should cover the 16 documentation target classes generated upstream:

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

Targets may remain unresolved after the search.

Unresolved is acceptable.

Assumed is not acceptable.

## 5. Preferred source hierarchy

The documentation search should prioritize sources in this order:

1. Official NANOGrav or relevant public source package documentation.
2. Official dataset release pages.
3. Official TEMPO, TEMPO2, or PINT documentation.
4. Peer-reviewed pulsar-timing or PTA data-release papers.
5. Official collaboration repositories or documentation pages.
6. Official tool repositories or documentation pages.
7. arXiv or journal landing pages for relevant release papers.
8. Secondary explanatory sources only for orientation if primary sources are unavailable.

Secondary sources may not carry primary provenance for semantic mapping or correction-state resolution.

## 6. Allowed search topics

The next research execution may search for public documentation related to:

- NANOGrav data releases
- NANOGrav J0740+6620 data products
- pulsar timing TIM file format
- pulsar timing PAR file format
- TEMPO timing model conventions
- TEMPO2 timing model conventions
- PINT timing model conventions
- PTA timing data release documentation
- clock corrections in pulsar timing
- solar-system ephemerides in pulsar timing
- DMX / dispersion measure correction conventions
- solarwind corrections in pulsar timing
- ECORR parameter conventions
- T2EFAC parameter conventions
- T2EQUAD parameter conventions
- backend jump or system parameter conventions
- public release provenance and checksum documentation

The next execution may identify sources and record source metadata.

It may not use the sources to interpret values physically.

## 7. Required metadata fields for found sources

A later SHAPIROINFO69 research execution should record each candidate source with at least:

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
- source_priority
- notes

Allowed source_type values:

- official_release_page
- official_dataset_documentation
- official_tool_documentation
- official_repository_documentation
- peer_reviewed_release_paper
- arxiv_or_journal_landing_page
- secondary_orientation_source
- unresolved

Allowed access_status values:

- identified_not_downloaded
- landing_page_only
- documentation_page_available
- download_required_but_not_performed
- unresolved

Allowed provenance_confidence values:

- high
- medium
- low
- unresolved

download_required must be recorded but no download may be performed.

## 8. Required output files for SHAPIROINFO69

A later public documentation research execution should write outputs under:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO69_PUBLIC_DOCUMENTATION_RESEARCH/

Recommended output files:

- public_documentation_source_candidates.csv
- documentation_target_coverage_matrix.csv
- correction_state_source_coverage_matrix.csv
- duplicate_parameter_documentation_candidates.csv
- public_documentation_research_summary.json
- public_documentation_research_readout.md
- public_documentation_research_config_resolved.json

Outputs are run artifacts first unless explicitly reviewed and tracked later.

## 9. Required summary fields

public_documentation_research_summary.json should include:

- generated_at_utc
- output_root
- source_candidate_count
- documentation_target_count
- documentation_targets_with_candidate_sources
- documentation_targets_unresolved
- correction_state_fields_with_candidate_sources
- correction_state_fields_unresolved
- duplicate_parameter_candidates_found
- public_web_research_status
- documentation_download_status
- raw_artifact_access_status
- direct_value_reading_gate
- residual_analysis_gate
- model_fitting_gate
- anomaly_claim_gate
- bridge_claim_gate
- claim_boundary

Default gate status values:

- public_web_research_status = performed_for_source_identification_only
- documentation_download_status = not_performed
- raw_artifact_access_status = not_performed
- direct_value_reading_gate = not_opened
- residual_analysis_gate = closed
- model_fitting_gate = closed
- anomaly_claim_gate = closed
- bridge_claim_gate = closed

## 10. Execution mode recommendation

SHAPIROINFO69 may be performed by one of the following modes:

- Deep Research execution,
- browser/search execution,
- local documentation-link inventory script,
- or a hybrid process.

The execution must record which mode was used.

If a live web search or Deep Research tool is used, sources must be recorded with citations or stable references.

If local Codex is used, it must not download documentation and must only record source metadata supplied or found through an explicitly authorized search workflow.

## 11. Download posture

The documentation-download gate remains closed.

Allowed:

- identify source URLs or references
- record source metadata
- record relevance to documentation targets
- record whether later download may be required
- record coverage status

Forbidden:

- download PDFs
- download data files
- copy documentation into the repository
- scrape external documentation
- mirror external documentation
- track downloaded documentation
- treat a source as resolved without later content review

If documentation content review or download becomes necessary, a later explicit gate must be opened.

## 12. Stop conditions

The route must stop or downgrade if:

- no candidate documentation sources can be identified for essential targets
- source candidates are too vague to support future semantic mapping
- correction-state fields remain unsupported by any candidate source
- source identification begins to substitute for source content review
- documentation search begins to drift into physical interpretation
- any output frames documentation discovery as physical evidence
- downloads become necessary before a download gate is opened

A stop condition is a valid scientific result.

## 13. Claim boundary

This note is a public documentation research plan within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only defines how a narrow public documentation research execution may identify candidate documentation sources and provenance references without downloading documentation or opening value reading.
