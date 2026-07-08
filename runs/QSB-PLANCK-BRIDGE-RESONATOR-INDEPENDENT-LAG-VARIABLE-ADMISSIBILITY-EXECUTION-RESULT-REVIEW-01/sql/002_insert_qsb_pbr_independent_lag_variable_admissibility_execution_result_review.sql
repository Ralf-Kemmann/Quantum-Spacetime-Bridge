BEGIN;

DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_lineage WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_results WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_blockers WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_repair_candidates WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_not_pair_mappable WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_deep_research_boundary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_next_gate WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_recommended_work WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_summary (run_id, run_type, source_run_id, review_outcome, confirmed_execution_status, confirmed_final_admissibility_status, candidate_count_total, candidate_count_admissible_for_testing, dominant_blocker, dominant_blocker_count, lineage_repair_candidate_count, metadata_repair_candidate_count, mechanism_testing_readiness, claim_status, physical_claim_release, external_readiness, next_gate, secondary_next_gate, tertiary_next_gate, lineage_commit_status, pre_existing_modified_files_detected, git_head, created_at_utc) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	run_type	source_run_id	review_outcome	confirmed_execution_status	confirmed_final_admissibility_status	candidate_count_total	candidate_count_admissible_for_testing	dominant_blocker	dominant_blocker_count	lineage_repair_candidate_count	metadata_repair_candidate_count	mechanism_testing_readiness	claim_status	physical_claim_release	external_readiness	next_gate	secondary_next_gate	tertiary_next_gate	lineage_commit_status	pre_existing_modified_files_detected	git_head	created_at_utc
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	independent_lag_variable_admissibility_execution_result_review	QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01	admissibility_execution_review_completed	admissibility_execution_completed_with_repair_required_candidates	admissibility_execution_completed_with_repair_required_candidates	260	0	not_pair_mappable	257	2	1	not_ready_no_admissible_candidates	admissibility_execution_result_review_only	blocked_no_physics_claim	internal_only	lineage_repair_required	physical_proxy_source_review_required	deep_research_method_criteria_review_pending	committed_or_no_local_delta_detected	false	e3c2f42	2026-07-08T15:29:52+00:00
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_lineage (run_id, source_run_id, source_status, source_execution_status, source_validation_pass_count, source_validation_fail_count, lineage_commit_status) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	source_status	source_execution_status	source_validation_pass_count	source_validation_fail_count	lineage_commit_status
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01	available	admissibility_execution_completed_with_repair_required_candidates	27	0	committed_or_no_local_delta_detected
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_results (run_id, review_question, review_answer, interpretation_boundary, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	review_question	review_answer	interpretation_boundary	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	what_did_execution_establish	260 Kandidaten wurden gegen Nicht-Alias-, Lineage-, Pair-Mapping- und Metadatenkriterien geprüft; kein Kandidat wurde unmittelbar für spätere Lag-Mechanismus-Tests zugelassen.	Das widerlegt QSB/PBR nicht und beweist keine reine Indexkonstruktion; es begrenzt nur die aktuelle Artefaktzulassung.	admissibility_result_review_only_no_physical_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_blockers (run_id, blocker_key, blocker_count, blocker_role, review_interpretation, next_action, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	blocker_key	blocker_count	blocker_role	review_interpretation	next_action	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	not_pair_mappable	257	dominant_blocker	Ohne Pair-Mapping sind Kandidaten nicht für 42 directed pair-feature Lag-Mechanismus-Tests nutzbar.	do_not_use_without_pair_mapping_repair	no_lag_mechanism_test_admissibility
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	lineage_incomplete	2	repair_gate	Lineage-Lücken müssen vor erneuter Admissibility-Prüfung geschlossen werden.	lineage_repair_required	no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	metadata_incomplete	1	secondary_repair_gate	Proxy-artige Kandidaten brauchen Einheiten-/Dimensionskontext.	physical_proxy_source_review_required	no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	no_admissible_candidate	0	mechanism_testing_readiness	0 zugelassene Kandidaten bedeutet: aktuelle Artefakte erfüllen die Zulassung nicht.	do_not_start_lag_mechanism_testing_from_current_candidates	not_ready_no_admissible_candidates
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_repair_candidates (run_id, candidate_id, candidate_variable_name, repair_type, source_type, source_path_or_table, current_decision_class, repair_need, minimum_repair_requirement, allowed_next_use_after_repair, claim_boundary) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	candidate_id	candidate_variable_name	repair_type	source_type	source_path_or_table	current_decision_class	repair_need	minimum_repair_requirement	allowed_next_use_after_repair	claim_boundary
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	CAND-0091	delta_phi_or_phase	metadata_repair	repo_file	data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql	candidate_admissible_only_after_metadata_repair	metadata_repair	unit_dimension_metadata_and_proxy_source_review	rerun_admissibility_execution_only	repair_candidate_not_mechanism_evidence
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	CAND-0127	candidate_term_match	lineage_repair	repo_file	data/bmc01/bmc01_baseline_relational_table_template.csv	candidate_admissible_only_after_lineage_repair	lineage_repair	source_lineage_and_non_alias_evidence	rerun_admissibility_execution_only	repair_candidate_not_mechanism_evidence
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	CAND-0128	candidate_term_match	lineage_repair	repo_file	data/bmc04/bmc04_baseline_relational_table_template.csv	candidate_admissible_only_after_lineage_repair	lineage_repair	source_lineage_and_non_alias_evidence	rerun_admissibility_execution_only	repair_candidate_not_mechanism_evidence
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_not_pair_mappable (run_id, rejected_not_pair_mappable_count, interpretation, next_action, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	rejected_not_pair_mappable_count	interpretation	next_action	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	257	not_pair_mappable_candidates_cannot_be_used_for_42_directed_pair_feature_lag_mechanism_testing	do_not_use_without_pair_mapping_repair	no_lag_mechanism_test_admissibility
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_claim_boundaries (run_id, claim_key, claim_text, status, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	claim_key	claim_text	status	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-001	QSB is physically validated	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-002	PBR exists physically	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-003	six lag axes are spacetime dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-004	spacetime emergence is proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-005	empirical validation exists	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-006	lag classes are physical dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-007	lag mechanism is physically proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-008	admissibility execution proves independent lag variable	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-009	admissibility execution proves physical proxy	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-010	0 admissible candidates disproves QSB	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-011	0 admissible candidates proves pure index construction	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-012	repair candidate proves mechanism	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-013	Deep Research can replace internal lineage	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-014	DWH presence alone proves independence	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-015	repo presence alone proves independence	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	BLOCK-016	literature note alone proves proxy for current matrix	blocked	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_deep_research_boundary (run_id, deep_research_status, deep_research_role, deep_research_cannot_replace_internal_lineage, deep_research_cannot_confirm_current_matrix_proxy, allowed_use, not_allowed_use) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	deep_research_status	deep_research_role	deep_research_cannot_replace_internal_lineage	deep_research_cannot_confirm_current_matrix_proxy	allowed_use	not_allowed_use
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	pending_or_parallel	method_criteria_and_reviewer_risk_only	true	true	criteria_context_and_red_team_risk	internal_evidence_substitution
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_next_gate (run_id, next_gate, secondary_next_gate, tertiary_next_gate, physical_claim_release, execution_authorization) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	next_gate	secondary_next_gate	tertiary_next_gate	physical_claim_release	execution_authorization
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	lineage_repair_required	physical_proxy_source_review_required	deep_research_method_criteria_review_pending	blocked_no_physics_claim	not_authorized_in_this_review_run
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_recommended_work (run_id, recommended_run_id, priority, rationale) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	recommended_run_id	priority	rationale
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-DESIGN-01	primary	Design source-lineage repair for the two lineage repair candidates.
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-PHYSICAL-PROXY-SOURCE-REVIEW-01	secondary	Review proxy-source artifacts separately.
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-DEEP-RESEARCH-METHOD-CRITERIA-INTEGRATION-01	later	Integrate Deep Research criteria as context only.
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	pending_validator	not_run	Review generated; run validator.
\.

-- BEGIN generated validation results import
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	run_directory_exact	PASS	/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	required_files_exist	PASS	all_required_files_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	utf8_lf_files	PASS	all_required_text_files_utf8_lf
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	run_id_exact	PASS	QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	run_type	PASS	independent_lag_variable_admissibility_execution_result_review
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	source_run_referenced	PASS	QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	review_outcome_allowed	PASS	admissibility_execution_review_completed
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	confirmed_execution_status_recorded	PASS	admissibility_execution_completed_with_repair_required_candidates
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	candidate_count_admissible_zero_if_source_zero	PASS	review=0 source=0
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	dominant_blocker_not_pair_mappable	PASS	not_pair_mappable:257
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	next_gates_exact	PASS	lineage_repair_required|physical_proxy_source_review_required|deep_research_method_criteria_review_pending
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	physical_claim_release_blocked	PASS	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	deep_research_boundary_recorded	PASS	{"run_id": "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01", "deep_research_status": "pending_or_parallel", "deep_research_role": "method_criteria_and_reviewer_risk_only", "deep_research_cannot_replace_internal_lineage": "true", "deep_research_cannot_confirm_current_matrix_proxy": "true", "allowed_use": "criteria_context_and_red_team_risk", "not_allowed_use": "internal_evidence_substitution"}
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	no_execution_tests_in_review	PASS	manifest_execution_flags
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	repair_candidate_count_matches_source	PASS	repair_rows=3
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	required_blockers_present	PASS	lineage_incomplete|metadata_incomplete|no_admissible_candidate|not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	claim_boundaries_blocked	PASS	claim_rows=16
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	primary_next_work_recorded	PASS	rows=3
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	german_view_created	PASS	view_name_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	sql_copy_tables_present	PASS	required_copy_tables_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	forbidden_phrases_only_blocked_context	PASS	no_unblocked_forbidden_phrase_hits
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	no_files_outside_run_package_modified	PASS	no_outside_changes
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01	git_diff_check_passes	PASS	git diff --check
\.
-- END generated validation results import
COMMIT;
