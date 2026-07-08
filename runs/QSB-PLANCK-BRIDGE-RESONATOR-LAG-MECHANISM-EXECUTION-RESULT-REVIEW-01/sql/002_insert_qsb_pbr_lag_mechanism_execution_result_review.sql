BEGIN;

DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_test WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_blocked_test WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_decision WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_input_gaps WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_next_gate WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_recommended_work WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_lineage WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_summary (run_id, source_run_id, review_outcome, formal_finding_status, mechanism_status, physical_proxy_status, pure_index_status, claim_status, physical_claim_release, external_readiness, next_gate, secondary_next_gate, tertiary_next_gate, review_timestamp_utc, git_commit) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	review_outcome	formal_finding_status	mechanism_status	physical_proxy_status	pure_index_status	claim_status	physical_claim_release	external_readiness	next_gate	secondary_next_gate	tertiary_next_gate	review_timestamp_utc	git_commit
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	inconclusive_requires_more_inputs_confirmed	strong_formal_lag_dependence_observed	independent_mechanism_not_established	no_independent_physical_proxy_available	not_conclusively_proven	lag_mechanism_execution_result_review_only	blocked_no_physics_claim	internal_only	input_artifact_enrichment_required	independent_lag_variable_design_required	physical_proxy_source_review_required	2026-07-08T10:15:00+00:00	c605bc8
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_test (run_id, test_key, source_execution_status, review_status, contribution_to_decision, claim_implication, next_input_need) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	source_execution_status	review_status	contribution_to_decision	claim_implication	next_input_need
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	index_relabeling_test	executed	reviewed_executed_test	labels_alone_not_mechanism	formal_diagnostic_only	none_for_label_check
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	order_scrambling_test	executed	reviewed_executed_test	strong_order_dependence_signal	formal_diagnostic_only	independent_order_variable_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	independent_lag_variable_test	blocked_missing_required_input	reviewed_blocked_test	blocked_no_independent_variable	formal_diagnostic_only	independent_lag_variable_artifact_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	shift_operator_test	executed	reviewed_executed_test	shift_diagnostic_executed_but_not_sufficient_for_independent_mechanism	formal_diagnostic_only	independent_shift_orbit_source_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	toeplitz_dependency_test	executed	reviewed_executed_test	strong_formal_lag_dependence_signal	formal_diagnostic_only	independent_lag_variable_artifact_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	physical_proxy_test	blocked_missing_physical_proxy_input	reviewed_blocked_test	blocked_no_physical_proxy	no_physical_proxy_claim	physical_proxy_source_artifact_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	nullmodel_operationalization_review	executed	reviewed_executed_test	lag_preserving_nullmodel_preserves_target_mechanism	formal_diagnostic_only	red_team_nullmodel_role_review_optional
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_blocked_test (run_id, test_key, blocked_reason, claim_implication, next_input_need) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	blocked_reason	claim_implication	next_input_need
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	independent_lag_variable_test	phase_response_values_assessed_as_alias_of_abs_lag	no_independent_lag_variable_claim	independent_lag_variable_artifact_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	physical_proxy_test	no_independent_physical_proxy_data_found	no_physical_proxy_claim	physical_proxy_source_artifact_required
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_decision (run_id, source_run_id, source_final_decision_class, review_confirmed_decision_class, not_formal_lag_mechanism_candidate_reason, not_physical_proxy_candidate_reason, not_pure_index_construction_reason, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	source_final_decision_class	review_confirmed_decision_class	not_formal_lag_mechanism_candidate_reason	not_physical_proxy_candidate_reason	not_pure_index_construction_reason	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	inconclusive_requires_more_inputs	inconclusive_requires_more_inputs	no_independent_lag_variable_or_shift_proxy_artifact_sufficient_to_establish_independent_mechanism	no_independent_physical_proxy_data_found	strong_formal_lag_dependence_observed_but_not_sufficient_to_prove_pure_index_construction	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_input_gaps (run_id, gap_key, gap_status, why_needed, minimum_required_content, claim_unlocked_if_resolved, claim_still_blocked_after_resolution) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	gap_key	gap_status	why_needed	minimum_required_content	claim_unlocked_if_resolved	claim_still_blocked_after_resolution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	independent_lag_variable_artifact	missing	Needed to distinguish lag aliasing from independent formal carrier.	Per-pair or per-channel variable not derived solely from j-i.	formal_lag_mechanism_candidate review	physical_claims_remain_gate_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	physical_proxy_source_artifact	missing	Needed for any physical proxy candidate assessment.	Momentum, energy, phase, frequency, mode, or scale variable with lineage and independence note.	physical_proxy_candidate review	physical_claims_remain_gate_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	proxy_independence_criteria	missing	Needed to prevent post-hoc alias use.	Rules distinguishing independent proxy from abs-lag alias.	cleaner proxy admissibility	physical_claims_remain_gate_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	phase_response_alias_review	required	Phase response values were assessed as abs-lag aliases.	Review note proving whether phase-response ranges are independent or construction-derived.	independent_lag_variable eligibility if resolved	physical_claims_remain_gate_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	source_lineage_for_candidate_variables	missing	Needed to audit any candidate variable source.	Artifact path, schema, hash, unit/dimension status, and derivation boundary.	auditable input enrichment	physical_claims_remain_gate_required
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_claim_boundaries (run_id, claim_key, claim_text, status, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	claim_key	claim_text	status	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-001	QSB is physically validated	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-002	PBR exists physically	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-003	six lag axes are spacetime dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-004	spacetime emergence is proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-005	empirical validation exists	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-006	lag classes are physical dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-007	lag mechanism is physically proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-008	execution proves physical proxy	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-009	execution proves independent formal lag mechanism	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-010	execution proves pure index construction	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-011	inconclusive_requires_more_inputs proves QSB	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-012	inconclusive_requires_more_inputs disproves QSB	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	BLOCK-013	phase-response values are independent lag variables despite alias assessment	blocked	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_next_gate (run_id, next_gate, secondary_next_gate, tertiary_next_gate, physical_claim_release, execution_authorization) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	next_gate	secondary_next_gate	tertiary_next_gate	physical_claim_release	execution_authorization
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	input_artifact_enrichment_required	independent_lag_variable_design_required	physical_proxy_source_review_required	blocked_no_physics_claim	not_authorized_in_this_review_run
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_recommended_work (run_id, recommended_run_id, recommendation_rank, purpose) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	recommended_run_id	recommendation_rank	purpose
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DESIGN-01	primary	Define enrichment package for independent lag variables and proxy sources.
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	secondary	Define criteria for independent lag variable admissibility.
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-PHYSICAL-PROXY-SOURCE-REVIEW-01	tertiary	Review possible physical proxy source systems without releasing physical claims.
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_lineage (run_id, source_run_id, source_path, source_exists) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	source_path	source_exists
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01	true
\.

-- BEGIN generated validation results import
COPY qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:README.md	pass	README.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01.md	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:RUN_COMMANDS_PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW01.md	pass	RUN_COMMANDS_PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW01.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/input_run_lineage.csv	pass	data/input_run_lineage.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/lag_mechanism_execution_review_summary.csv	pass	data/lag_mechanism_execution_review_summary.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/lag_mechanism_test_review.csv	pass	data/lag_mechanism_test_review.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/blocked_test_review.csv	pass	data/blocked_test_review.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/decision_class_review.csv	pass	data/decision_class_review.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/input_artifact_gap_analysis.csv	pass	data/input_artifact_gap_analysis.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/claim_boundaries.csv	pass	data/claim_boundaries.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/next_gate_decision.csv	pass	data/next_gate_decision.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/recommended_next_work.csv	pass	data/recommended_next_work.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:data/review_manifest.json	pass	data/review_manifest.json
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_TESTS_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_TESTS_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_INPUT_GAPS_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_INPUT_GAPS_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:scripts/run_pbr_lag_mechanism_execution_result_review.py	pass	scripts/run_pbr_lag_mechanism_execution_result_review.py
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:scripts/validate_pbr_lag_mechanism_execution_result_review.py	pass	scripts/validate_pbr_lag_mechanism_execution_result_review.py
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:sql/001_create_qsb_pbr_lag_mechanism_execution_result_review.sql	pass	sql/001_create_qsb_pbr_lag_mechanism_execution_result_review.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:sql/002_insert_qsb_pbr_lag_mechanism_execution_result_review.sql	pass	sql/002_insert_qsb_pbr_lag_mechanism_execution_result_review.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:sql/003_validation_queries.sql	pass	sql/003_validation_queries.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	exists:validation/validation_results.csv	pass	validation/validation_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	run_id_consistency	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	source_run_referenced	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	lineage_includes_required_runs	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01,QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01,QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01,QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01,QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01,QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01,QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01,QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	all_seven_tests_reviewed	pass	independent_lag_variable_test,index_relabeling_test,nullmodel_operationalization_review,order_scrambling_test,physical_proxy_test,shift_operator_test,toeplitz_dependency_test
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	blocked_independent_lag_variable_reviewed	pass	independent_lag_variable_test,physical_proxy_test
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	blocked_physical_proxy_reviewed	pass	independent_lag_variable_test,physical_proxy_test
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	source_final_decision	pass	inconclusive_requires_more_inputs
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	review_confirmed_decision	pass	inconclusive_requires_more_inputs
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	review_outcome	pass	inconclusive_requires_more_inputs_confirmed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	formal_finding_status	pass	strong_formal_lag_dependence_observed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	mechanism_status	pass	independent_mechanism_not_established
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	physical_proxy_status	pass	no_independent_physical_proxy_available
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	pure_index_status	pass	not_conclusively_proven
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	physical_claim_release_blocked	pass	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	next_gate	pass	input_artifact_enrichment_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	secondary_next_gate	pass	independent_lag_variable_design_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	tertiary_next_gate	pass	physical_proxy_source_review_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	no_tests_or_nullmodels_executed	pass	manifest flags
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	recommended_primary_next_run	pass	QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DESIGN-01
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	forbidden_context:QSB is physically validated	pass	QSB is physically validated
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	forbidden_context:PBR exists physically	pass	PBR exists physically
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	forbidden_context:six lag axes are spacetime dimensions	pass	six lag axes are spacetime dimensions
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	forbidden_context:spacetime emergence is proven	pass	spacetime emergence is proven
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	forbidden_context:empirical validation exists	pass	empirical validation exists
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	sql_copy_column_lists_match_rows	pass	COPY TSV blocks
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	csv_lf_line_endings	pass	10 CSV files
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	csv_lineterminator_declared	pass	csv.DictWriter lineterminator
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	utf8_text_files_readable	pass	24 files
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	git_diff_check	pass	ok
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01	no_files_outside_run_package_modified	pass	ok
\.
-- END generated validation results import
COMMIT;
