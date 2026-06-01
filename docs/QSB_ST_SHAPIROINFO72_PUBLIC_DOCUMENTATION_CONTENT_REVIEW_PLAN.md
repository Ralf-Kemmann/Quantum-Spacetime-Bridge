# QSB-ST SHAPIROINFO72 — Public Documentation Content-Review Plan

Date: 2026-06-02
Status: public documentation content-review plan
Upstream decision: SHAPIROINFO71_PUBLIC_DOCUMENTATION_RESEARCH_REVIEW_AND_DOWNLOAD_GATE_DECISION
Plan type: narrow public webpage / landing-page / documentation-page content-review plan
Raw artifact access: no raw artifact inspection by this note
Physics-analysis status: closed for physical value interpretation, residual search, and model fitting
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note defines the public documentation content-review plan allowed by SHAPIROINFO71.

SHAPIROINFO69 identified candidate public documentation sources.

SHAPIROINFO70 documented that source-identification result.

SHAPIROINFO71 decided that a narrow public webpage and landing-page content-review plan may be prepared, while documentation downloads, raw artifact access, value reading, residual analysis, model fitting, and Bridge claims remain closed.

The current task is not to review source content.

The current task is to define how a later source-content review may be performed.

This note does not perform additional public web research.

This note does not download documentation.

This note does not inspect raw artifacts.

This note does not read TIM or PAR values.

This note does not compute residuals.

This note does not fit timing models.

This note does not make anomaly claims.

This note does not make QSB-ST Bridge-related claims.

## 2. Upstream state

SHAPIROINFO70 documented the SHAPIROINFO69 source-identification run.

The source-identification layer reported:

* source_candidate_count = 18
* documentation_target_count = 16
* documentation_targets_with_candidate_sources = 15
* documentation_targets_unresolved = 1
* correction_state_fields_with_candidate_sources = 16
* correction_state_fields_unresolved = 1
* duplicate_parameter_candidates_found = 3
* public_web_research_status = performed_for_source_identification_only
* documentation_download_status = not_performed
* raw_artifact_access_status = not_performed
* direct_value_reading_gate = not_opened
* residual_analysis_gate = closed
* model_fitting_gate = closed
* bridge_claim_gate = closed

The unresolved documentation target is:

* profile_template_conventions

The unresolved correction-state field is:

* profile_template_state

Candidate source examples include:

* NANOGrav Data
* NANOGrav J0740+6620 timing data
* PINT timing-data format explanation
* PINT timing models
* PINT clock/observatory documentation
* Tempo reference manual
* Tempo page
* Tempo2 page
* NANOGrav 15-year observations/timing arXiv landing page
* Tempo2 overview arXiv landing page

## 3. Planning decision

Decision:

* next_scope = PUBLIC_DOCUMENTATION_CONTENT_REVIEW_EXECUTION
* next_step = SHAPIROINFO73_PUBLIC_DOCUMENTATION_CONTENT_REVIEW_EXECUTION
* following_possible_step = SHAPIROINFO74_PUBLIC_DOCUMENTATION_CONTENT_REVIEW_RESULT_NOTE
* later_possible_gate = SHAPIROINFO75_DOCUMENTATION_DOWNLOAD_GATE_DECISION
* later_value_gate = SHAPIROINFO76_CORRECTION_STATE_RESOLUTION_AND_VALUE_READING_GATE_DECISION
* allowed_scope = PUBLIC_WEBPAGE_AND_LANDING_PAGE_CONTENT_REVIEW_ONLY
* public_documentation_content_review = ALLOWED_FOR_ALREADY_IDENTIFIED_SOURCES_ONLY
* additional_public_web_search = FORBIDDEN
* documentation_download = FORBIDDEN
* raw_artifact_access = FORBIDDEN
* direct_value_reading_gate = NOT_OPENED
* residual_analysis_gate = CLOSED
* model_fitting_gate = CLOSED
* anomaly_claim_gate = CLOSED
* bridge_claim_gate = CLOSED
* physical_value_interpretation = FORBIDDEN
* residual_search = FORBIDDEN
* model_fitting = FORBIDDEN
* research_status = PHYSICS_MOTIVATED_ACTIVE_ROUTE

The project may proceed to a narrow public documentation content-review execution.

That later execution may review already identified public web pages, documentation pages, repository pages, release pages, and landing pages.

The project must not download PDFs, data files, documentation files, or bibliography files.

The project must not inspect raw artifacts, read TIM/PAR values, compute residuals, fit models, or make physical claims.

## 4. Allowed source-content review targets

A later SHAPIROINFO73 content-review execution may review only already identified source candidates from SHAPIROINFO69.

Allowed source classes:

* official_release_page
* official_dataset_documentation
* official_tool_documentation
* official_repository_documentation
* arxiv_or_journal_landing_page
* peer_reviewed_release_paper landing pages only
* secondary_orientation_source only if primary sources are insufficient

Allowed specific source examples include:

* NANOGrav Data page
* NANOGrav J0740+6620 timing data page
* PINT timing-data format explanation page
* PINT timing models page
* PINT clock/observatory documentation page
* Tempo reference manual page
* Tempo page
* Tempo2 page
* NANOGrav 15-year observations/timing landing page
* Tempo2 overview landing page

The execution must not use source content to interpret TIM/PAR values.

## 5. Forbidden source-content review targets

SHAPIROINFO73 must not review:

* downloaded PDFs
* downloaded data files
* locally stored documentation files
* raw TIM/PAR artifact contents
* raw data products
* untracked raw artifacts
* any source not identified in SHAPIROINFO69 unless a later search-extension gate is opened

If a source requires download before content can be reviewed, it must be marked as download_required_but_not_performed.

## 6. Required content-review fields

A later SHAPIROINFO73 execution should create a source-content review table with at least:

* source_id
* source_title
* source_type
* source_url_or_reference
* reviewed_content_location
* review_status
* documentation_target_classes_addressed
* correction_state_fields_addressed
* duplicate_parameter_topics_addressed
* semantic_mapping_support_status
* correction_state_support_status
* value_reading_support_status
* download_required_for_full_review
* source_insufficient_reason
* provenance_confidence
* short_evidence_note
* notes

Allowed review_status values:

* reviewed_webpage_content
* reviewed_landing_page_metadata
* content_not_accessible_without_download
* source_insufficient
* unresolved

Allowed semantic_mapping_support_status values:

* supports_later_mapping
* partial_support
* does_not_support
* unresolved
* forbidden_to_infer

Allowed correction_state_support_status values:

* supports_later_resolution
* partial_support
* does_not_support
* unresolved
* forbidden_to_infer

Allowed value_reading_support_status values:

* not_opened
* requires_later_gate
* forbidden_currently

The content review may identify whether a source appears useful for later semantic mapping or correction-state resolution.

It may not perform physical interpretation.

## 7. Documentation target coverage review

A later SHAPIROINFO73 execution should update documentation target coverage using content-review evidence.

Required fields:

* documentation_target_class
* candidate_source_ids_reviewed
* content_review_status
* source_support_level
* download_required_for_full_resolution
* unresolved_allowed
* stop_if_unresolved
* notes

Allowed content_review_status values:

* supported_by_reviewed_webpage
* partially_supported_by_reviewed_webpage
* landing_page_only
* download_required_but_not_performed
* unresolved
* not_applicable

Allowed source_support_level values:

* primary_source_support
* secondary_source_support
* weak_orientation_only
* no_support
* unresolved

## 8. Correction-state evidence mapping review

A later SHAPIROINFO73 execution should map reviewed source content to correction-state fields.

Required fields:

* correction_state_field
* candidate_source_ids_reviewed
* evidence_status
* documentation_target_class
* resolution_possible_after_review
* download_required_for_full_resolution
* unresolved_allowed
* stop_if_unresolved
* notes

Allowed evidence_status values:

* source_content_supports_resolution
* source_content_partially_supports_resolution
* source_identified_but_content_insufficient
* download_required_but_not_performed
* unresolved
* not_applicable

The content review may determine whether source content is sufficient for later correction-state resolution.

It may not mark correction-state fields as physically resolved unless a later correction-state resolution gate authorizes that step.

## 9. Duplicate-parameter content review

A later SHAPIROINFO73 execution should review whether already identified sources contain documentation relevant to:

* ECORR
* T2EFAC
* T2EQUAD

Required fields:

* parameter_name
* candidate_source_ids_reviewed
* content_review_status
* convention_support_status
* interpretation_status
* value_reading_status
* download_required_for_full_resolution
* notes

Allowed convention_support_status values:

* convention_documentation_candidate
* partial_candidate
* no_support_found
* unresolved
* forbidden_to_infer

The content review may identify candidate convention documentation.

It must not interpret duplicate parameter values physically.

It must not select duplicate parameters for fitting.

It must not treat duplicates as anomalies.

It must not claim QSB-ST relevance.

## 10. Handling profile-template unresolved state

The unresolved target remains:

* profile_template_conventions

The unresolved correction-state field remains:

* profile_template_state

SHAPIROINFO73 may check whether already identified source candidates contain profile-template information.

It may not perform new searches for this target unless a later search-extension gate is opened.

If no identified source supports this target, the result should remain unresolved.

Unresolved is acceptable.

Assumed is not acceptable.

## 11. Required output files for SHAPIROINFO73

A later SHAPIROINFO73 execution should write outputs under:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO73_PUBLIC_DOCUMENTATION_CONTENT_REVIEW/

Recommended output files:

* public_documentation_content_review_table.csv
* documentation_target_content_coverage_matrix.csv
* correction_state_content_evidence_matrix.csv
* duplicate_parameter_content_review_table.csv
* unresolved_profile_template_followup_table.csv
* public_documentation_content_review_summary.json
* public_documentation_content_review_readout.md
* public_documentation_content_review_config_resolved.json

Outputs are run artifacts first unless explicitly reviewed and tracked later.

## 12. Required summary fields

public_documentation_content_review_summary.json should include:

* generated_at_utc
* output_root
* source_candidates_reviewed_count
* documentation_targets_supported_by_content
* documentation_targets_unresolved_after_content_review
* correction_state_fields_supported_by_content
* correction_state_fields_unresolved_after_content_review
* duplicate_parameter_topics_with_content_support
* sources_requiring_download_for_full_review
* public_web_content_review_status
* additional_public_web_search_status
* documentation_download_status
* raw_artifact_access_status
* direct_value_reading_gate
* residual_analysis_gate
* model_fitting_gate
* anomaly_claim_gate
* bridge_claim_gate
* claim_boundary

Default gate status values:

* public_web_content_review_status = planned_not_performed_by_this_note
* additional_public_web_search_status = forbidden
* documentation_download_status = not_performed
* raw_artifact_access_status = not_performed
* direct_value_reading_gate = not_opened
* residual_analysis_gate = closed
* model_fitting_gate = closed
* anomaly_claim_gate = closed
* bridge_claim_gate = closed

## 13. Stop conditions

The route must stop or downgrade if:

* sources cannot be reviewed without download
* reviewed pages do not contain content relevant to correction-state review
* content review would require reading TIM/PAR values
* content review would require interpreting parameter values physically
* source metadata is mistaken for source-content evidence
* documentation gaps are silently converted into assumptions
* unresolved profile-template state becomes necessary for value reading
* any output frames documentation as physical evidence
* any output begins to imply QSB-ST Bridge validation

A stop condition is a valid scientific result.

## 14. Claim boundary

This note is a public documentation content-review plan within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.

It does not interpret TIM or PAR values as physical evidence.

It only defines how a later narrow documentation-content review may inspect already identified public web pages, documentation pages, repository pages, release pages, and landing pages without downloading documentation, reading raw artifacts, or opening value reading.
