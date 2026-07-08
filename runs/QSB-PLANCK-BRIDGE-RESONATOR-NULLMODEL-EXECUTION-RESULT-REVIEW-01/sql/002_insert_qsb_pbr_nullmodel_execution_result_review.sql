BEGIN;

DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_family WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_critical_findings WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_specificity WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_next_gate WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_lineage WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';

COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_summary (run_id, input_run_id, review_status, review_outcome, formal_finding_status, specificity_status, critical_nullmodel, critical_nullmodel_reproduction, claim_status, physical_claim_release, external_readiness, next_gate, secondary_next_gate, review_timestamp_utc, git_commit) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	input_run_id	review_status	review_outcome	formal_finding_status	specificity_status	critical_nullmodel	critical_nullmodel_reproduction	claim_status	physical_claim_release	external_readiness	next_gate	secondary_next_gate	review_timestamp_utc	git_commit
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	review_completed	no_specificity_confirmed_for_current_operationalization	psd_rank6_lag_structure_remains_formal	no_specificity_beyond_lag_preserving_construction	lag_preserving_shuffle_null	1000/1000	nullmodel_result_review_only	blocked_no_physics_claim	internal_only	lag_mechanism_required	nullmodel_operationalization_review_required	2026-07-08T08:54:57+00:00	6553d3e
\.

COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_family (run_id, input_run_id, nullmodel_family, samples_total, complete_reproduction_count, complete_reproduction_rate, partial_reproduction_count, rank6_preservation_count, review_interpretation, claim_implication, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	input_run_id	nullmodel_family	samples_total	complete_reproduction_count	complete_reproduction_rate	partial_reproduction_count	rank6_preservation_count	review_interpretation	claim_implication	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	label_permutation_null	1000	0	0.0	1000	1000	keine_vollstaendige_reproduktion_in_dieser_nullmodellfamilie	stuetzt_nicht_allein_einen_staerkeren_spezifitaetsclaim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	lag_preserving_shuffle_null	1000	1000	1.0	0	1000	vollstaendige_reproduktion_bei_erhaltener_lag_klasse	keine_spezifitaet_ueber_lag_erhaltende_konstruktion_hinaus	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	random_gram_psd_null	1000	0	0.0	1000	1000	keine_vollstaendige_reproduktion_in_dieser_nullmodellfamilie	stuetzt_nicht_allein_einen_staerkeren_spezifitaetsclaim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	directed_pair_rewire_null	1000	0	0.0	1000	1000	keine_vollstaendige_reproduktion_in_dieser_nullmodellfamilie	stuetzt_nicht_allein_einen_staerkeren_spezifitaetsclaim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	sign_flip_antiparallel_null	1000	0	0.0	1000	1000	keine_vollstaendige_reproduktion_in_dieser_nullmodellfamilie	stuetzt_nicht_allein_einen_staerkeren_spezifitaetsclaim	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_critical_findings (run_id, critical_nullmodel, complete_reproduction_count, samples_total, complete_reproduction_rate, interpretation, claim_implication, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	critical_nullmodel	complete_reproduction_count	samples_total	complete_reproduction_rate	interpretation	claim_implication	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	lag_preserving_shuffle_null	1000	1000	1.0	structure_fully_reproduced_when_lag_classes_preserved	no_specificity_beyond_lag_preserving_construction	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_specificity (run_id, input_run_id, specificity_classification, specificity_de_label, specificity_reason, formal_claim_status, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	input_run_id	specificity_classification	specificity_de_label	specificity_reason	formal_claim_status	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	no_specificity	keine formale Spezifität	lag_preserving_shuffle_null_reproduced_complete_structure_1000_of_1000	no_stronger_specificity_claim	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_claim_boundaries (run_id, claim_key, status, claim_text, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	claim_key	status	claim_text	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	formal_review_scope	allowed_formal_only	Die Nullmodell-Ausführung wird nur formal reviewt.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	lag_mechanism	allowed_formal_only	Die Lag-Klassenstruktur erscheint in der aktuellen Operationalisierung als tragender formaler Mechanismus des Befunds.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	qsb_physical_validation	blocked	Eine physische QSB-Validierungsbehauptung ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	pbr_physical_existence	blocked	Eine physische PBR-Existenzbehauptung ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	lag_axes_physical_dimensions	blocked	Eine Deutung der Lag-Klassen als physische Dimensionen ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	proof_or_disproof	blocked	Das Nullmodell-Resultat beweist oder widerlegt QSB nicht.	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_next_gate (run_id, next_gate, secondary_next_gate, execution_authorization, gate_meaning, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	next_gate	secondary_next_gate	execution_authorization	gate_meaning	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	lag_mechanism_required	nullmodel_operationalization_review_required	not_authorized_in_this_review_run	klaeren_ob_lag_klassen_index_konstruktion_oder_unabhaengig_motivierter_mechanismus_sind	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_lineage (run_id, source_run_id, source_path, source_exists, source_role) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	source_path	source_exists	source_role
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	true	review_input
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01	true	upstream_context
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01	true	upstream_context
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01	true	upstream_context
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01	true	upstream_context
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01	true	upstream_context
\.

-- BEGIN generated validation results import
COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:README.md	pass	README.md
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01.md	pass	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01.md
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:RUN_COMMANDS_PBR_NULLMODEL_EXECUTION_RESULT_REVIEW01.md	pass	RUN_COMMANDS_PBR_NULLMODEL_EXECUTION_RESULT_REVIEW01.md
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/input_run_lineage.csv	pass	data/input_run_lineage.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/nullmodel_execution_review_summary.csv	pass	data/nullmodel_execution_review_summary.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/nullmodel_family_review.csv	pass	data/nullmodel_family_review.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/critical_nullmodel_findings.csv	pass	data/critical_nullmodel_findings.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/specificity_interpretation.csv	pass	data/specificity_interpretation.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/claim_boundaries.csv	pass	data/claim_boundaries.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/next_gate_decision.csv	pass	data/next_gate_decision.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/recommended_next_work.csv	pass	data/recommended_next_work.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:data/review_manifest.json	pass	data/review_manifest.json
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md	pass	docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md	pass	docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md	pass	docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_LAG_MECHANISM_DE.md	pass	docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_LAG_MECHANISM_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:scripts/run_pbr_nullmodel_execution_result_review.py	pass	scripts/run_pbr_nullmodel_execution_result_review.py
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:scripts/validate_pbr_nullmodel_execution_result_review.py	pass	scripts/validate_pbr_nullmodel_execution_result_review.py
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:sql/001_create_qsb_pbr_nullmodel_execution_result_review.sql	pass	sql/001_create_qsb_pbr_nullmodel_execution_result_review.sql
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:sql/002_insert_qsb_pbr_nullmodel_execution_result_review.sql	pass	sql/002_insert_qsb_pbr_nullmodel_execution_result_review.sql
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:sql/003_validation_queries.sql	pass	sql/003_validation_queries.sql
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	exists:validation/validation_results.csv	pass	validation/validation_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	run_id_consistency	pass	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	input_execution_run_referenced	pass	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	all_families_reviewed	pass	directed_pair_rewire_null,label_permutation_null,lag_preserving_shuffle_null,random_gram_psd_null,sign_flip_antiparallel_null
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	critical_nullmodel	pass	lag_preserving_shuffle_null
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	critical_reproduction_1000_of_1000	pass	1000/1000
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	specificity_no_specificity	pass	no_specificity
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	review_outcome	pass	no_specificity_confirmed_for_current_operationalization
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	physical_claim_release_blocked	pass	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	no_nullmodels_executed_in_review	pass	review manifest
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	next_gate	pass	lag_mechanism_required
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	secondary_next_gate	pass	nullmodel_operationalization_review_required
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	external_readiness_internal_only	pass	internal_only
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	forbidden_context:QSB is physically validated	pass	QSB is physically validated
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	forbidden_context:PBR exists physically	pass	PBR exists physically
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	forbidden_context:The six lag axes are spacetime dimensions	pass	The six lag axes are spacetime dimensions
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	forbidden_context:Spacetime emergence is proven	pass	Spacetime emergence is proven
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	forbidden_context:Empirical validation exists	pass	Empirical validation exists
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	sql_copy_column_lists_match_rows	pass	COPY TSV blocks
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	csv_lf_line_endings	pass	9 CSV files
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	csv_lineterminator_declared	pass	csv.DictWriter lineterminator
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	utf8_text_files_readable	pass	22 files
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	git_diff_check	pass	ok
QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	no_files_outside_run_package_modified	pass	ok
\.
-- END generated validation results import
COMMIT;
