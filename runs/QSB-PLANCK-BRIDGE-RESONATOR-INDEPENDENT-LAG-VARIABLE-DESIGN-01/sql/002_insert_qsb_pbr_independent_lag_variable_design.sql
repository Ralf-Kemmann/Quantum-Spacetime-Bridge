BEGIN;

DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_design_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_input_scout_lineage WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_independence_criteria WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_alias_rules WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_classification_schema WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_test_design WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_decision_logic WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_source_lineage_requirements WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_pair_mapping_requirements WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_unit_dimension_requirements WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_phase_response_rule WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_deep_research_handoff WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_next_gate WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';

COPY qsb_planck_bridge.pbr_independent_lag_variable_design_summary (run_id, run_type, design_status, execution_status, claim_status, physical_claim_release, input_scout_run_id, input_scout_status, input_scout_decision, input_scout_candidate_count, input_scout_repo_artifact_match_count, input_scout_dwh_artifact_match_count, lineage_commit_status, pre_existing_modified_files_detected, pre_existing_modified_files, next_gate, secondary_next_gate, no_tests_executed, no_nullmodels_executed, git_head, created_at_utc) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	run_type	design_status	execution_status	claim_status	physical_claim_release	input_scout_run_id	input_scout_status	input_scout_decision	input_scout_candidate_count	input_scout_repo_artifact_match_count	input_scout_dwh_artifact_match_count	lineage_commit_status	pre_existing_modified_files_detected	pre_existing_modified_files	next_gate	secondary_next_gate	no_tests_executed	no_nullmodels_executed	git_head	created_at_utc
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	independent_lag_variable_design	independent_lag_variable_design_completed_execution_required	design_only_not_executed	independent_lag_variable_design_only	blocked_no_physics_claim	QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	available	candidate_artifacts_found_but_alias_risk_high	260	5740	145	committed_or_no_local_delta_detected	false		independent_lag_variable_admissibility_execution_required	physical_proxy_source_review_required	true	true	119cdbd	2026-07-08T11:03:36+00:00
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_input_scout_lineage (run_id, input_scout_run_id, input_file, input_status, input_scout_decision, candidate_count, alias_high_count, proxy_family_count, gap_count, lineage_commit_status, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	input_scout_run_id	input_file	input_status	input_scout_decision	candidate_count	alias_high_count	proxy_family_count	gap_count	lineage_commit_status	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/scout_summary.csv	available	candidate_artifacts_found_but_alias_risk_high	260	51	8	5	committed_or_no_local_delta_detected	input_scout_used_for_design_only_no_independence_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_independence_criteria (run_id, criterion_key, deutscher_name, criterion_definition, required_evidence, design_status, claim_implication, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	criterion_key	deutscher_name	criterion_definition	required_evidence	design_status	claim_implication	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C01_pre_pair_existence	Vor-Paar-Existenz	Variable muss vor oder unabhängig von Pair-Konstruktion existieren oder Source-Lineage haben, die nicht aus pair_id, lag, |j-i| oder Kanalindexordnung abgeleitet ist.	later_execution_artifact_required	criteria_defined	candidate_only_requires_execution	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C02_non_alias_derivation	Nicht-Alias-Ableitung	Variable darf nicht aus lag, |j-i|, pair_id, i, j, Kanalindex oder Kanalordnung berechnet sein.	later_execution_artifact_required	criteria_defined	alias_if_derivation_from_forbidden_basis	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C03_independent_source_lineage	unabhängige Source-Lineage	Generating Run, Datei/Tabelle und Transformationsregel müssen nachvollziehbar sein.	later_execution_artifact_required	criteria_defined	lineage_incomplete_blocks_admissibility	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C04_pair_mappability	Paar-Mappbarkeit	Variable muss auf 42 gerichtete Pair-Features mappbar sein, ohne lag selbst als Wertquelle zu benutzen; i/j-Mapping darf nur dokumentierter Schlüssel sein.	later_execution_artifact_required	criteria_defined	not_pair_mappable_blocks_lag_mechanism_testing	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C05_value_variation_not_lag_determined	nicht vollständig lag-determiniert	Werte dürfen nicht vollständig deterministische Funktion von lag oder |lag| sein.	later_execution_artifact_required	criteria_defined	deterministic_lag_function_is_alias	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C06_symmetry_directionality_check	Richtungs-/Symmetrieprüfung	Verhalten unter i-j-Umkehr muss dokumentiert sein; Richtung, Antirichtung, Symmetrie oder Absolutheit sind keine Unabhängigkeitsbelege.	later_execution_artifact_required	criteria_defined	directionality_is_documentation_not_independence	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C07_unit_dimension_metadata	Einheiten-/Dimensionsmetadaten	Physikalische oder proxy-artige Variablen brauchen Einheiten-/Dimensionsmetadaten oder dokumentierte Dimensionslosigkeit.	later_execution_artifact_required	criteria_defined	metadata_missing_blocks_physical_proxy_review	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	C08_null_alias_stress_test_design	Null-Alias-Stresstest	Spätere Ausführung muss gegen lag, |lag|, pair_id, i, j und permutierte Ordnungsbaselines vergleichen.	later_execution_artifact_required	criteria_defined	requires_execution_no_result_claim	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_alias_rules (run_id, flag_key, deutscher_name, detection_rule, required_evidence, claim_implication, recommended_action, design_status, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	flag_key	deutscher_name	detection_rule	required_evidence	claim_implication	recommended_action	design_status	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	exact_lag_alias	exakter lag-Alias	Kandidat ist identisch oder deterministisch äquivalent zu lag.	Wertvergleich gegen lag; R2/Lookup exakt.	no_independent_lag_variable_claim	reject_as_alias	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	absolute_lag_alias	absoluter lag-Alias	Kandidat ist identisch oder deterministisch äquivalent zu |lag|.	Wertvergleich gegen |lag|; Richtung geht verloren.	no_independent_lag_variable_claim	reject_as_abs_lag_alias	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	pair_id_lookup_alias	pair_id-Lookup-Alias	Kandidat wird über pair_id nachgeschlagen oder aus pair_id rekonstruiert.	Lookup-Accuracy gegen pair_id.	pair_presence_not_independence	reject_or_require_source_repair	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	index_order_alias	Indexordnungs-Alias	Kandidat folgt i, j, Kanalindex oder Kanalordnung.	Regression/Lookup gegen i, j und Order-Baselines.	index_surrogate_not_independence	reject_or_scramble_test	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	monotonic_lag_surrogate	monotones lag-Surrogat	Kandidat ist monotone Transformation von lag oder |lag|.	Monotonie- und Rangsvergleich.	high_alias_risk_no_confirmation	require_information_gain_test	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	piecewise_lag_surrogate	stückweises lag-Surrogat	Kandidat ist stückweise aus lag-Klassen ableitbar.	Piecewise-Modelle und Residualprüfung.	high_alias_risk_no_confirmation	require_residual_entropy_test	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	symmetry_only_alias	reiner Symmetrie-Alias	Kandidat trägt nur Symmetrie-/Absolutwertinformation der Pair-Ordnung.	i-j-Reversal und Absolutwertprüfung.	symmetry_is_not_independence	require_directionality_review	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	phase_response_abs_lag_alias	Phase-Response-|lag|-Alias	Wenn Phase-Response upstream als Alias von |j-i| bewertet wurde, darf sie nicht als unabhängige Lag-Variable genutzt werden, außer ein neues Quellartefakt belegt unabhängige Erzeugung und Nicht-Alias-Verhalten.	Upstream-Aliasbefund plus neues Source-Artefakt und Nicht-Alias-Test.	phase_response_no_independent_lag_variable_claim_without_new_source	block_until_new_source_and_tests	criteria_defined	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	unknown_alias_risk	unbekanntes Alias-Risiko	Lineage oder Testlage reicht nicht zur Aliasentscheidung.	Vollständige Lineage- und Alias-Testausführung.	requires_review_no_confirmation	route_to_red_team_review	criteria_defined	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_classification_schema (run_id, candidate_class, class_definition, allowed_status, claim_implication, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	candidate_class	class_definition	allowed_status	claim_implication	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	admissible_independent_lag_variable_candidate	Alle Designkriterien scheinen erfüllbar; spätere Ausführung erforderlich.	candidate_class_defined	candidate_class_only_no_confirmation	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	formal_independent_variable_candidate_requires_execution	Formal plausibler Kandidat mit offener Testausführung.	candidate_class_defined	requires_execution	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	physical_proxy_candidate_requires_source_review	Proxy-artiger Kandidat mit Source-, Einheiten- und Dimensionsreview-Bedarf.	candidate_class_defined	no_physical_proxy_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	alias_of_abs_lag_or_lag	Kandidat ist oder wirkt wie lag/|lag|-Alias.	candidate_class_defined	reject_for_independent_lag_gate	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	alias_of_pair_id_or_index_order	Kandidat folgt pair_id, i/j oder Kanalordnung.	candidate_class_defined	reject_or_repair_lineage	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	lineage_incomplete_requires_repair	Source-Lineage reicht nicht aus.	candidate_class_defined	repair_before_use	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	not_pair_mappable	Mapping auf 42 gerichtete Pair-Features fehlt.	candidate_class_defined	cannot_enter_lag_mechanism_test	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	unit_or_dimension_missing_requires_metadata	Einheiten-/Dimensionsmetadaten fehlen bei proxy-artigem Kandidat.	candidate_class_defined	metadata_repair_required	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	excluded_not_relevant	Nicht relevant für unabhängige Lag-Variable.	candidate_class_defined	exclude_from_gate	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	unknown_requires_review	Befund unklar.	candidate_class_defined	manual_review_required	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_test_design (run_id, test_key, purpose, required_later_metrics, execution_status, design_status, claim_implication, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	purpose	required_later_metrics	execution_status	design_status	claim_implication	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	deterministic_alias_test	Prüfen, ob Kandidatenwerte exakt oder nahezu exakt aus lag, |lag|, pair_id, i, j oder Indexordnung berechenbar sind.	r2_lag|r2_abs_lag|lookup_accuracy_pair_id|lookup_accuracy_index_order|residual_entropy|alias_classification	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	scramble_invariance_test	Prüfen, ob Kandidatenwerte bei Neuordnung/Permutation der Kanalordnung unabhängig bleiben.	scramble_count|candidate_value_preservation_rate|lag_relation_change_rate|independence_stability_score	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	source_lineage_audit	Prüfen, ob Kandidatenwerte upstream unabhängig erzeugt wurden.	source_artifact_present|generation_rule_present|transformation_chain_complete|derived_from_lag_flag|derived_from_pair_id_flag|lineage_score	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	pair_mapping_audit	Prüfen, ob Kandidaten sauber auf die 42 gerichteten Pair-Features mappbar sind.	pair_mapping_coverage|directed_pair_coverage|missing_pair_count|mapping_uses_lag_as_value_source|mapping_uses_pair_id_as_value_source	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	information_gain_over_lag_test	Prüfen, ob die Kandidatenvariable zusätzliche Information über lag oder |lag| hinaus trägt.	mutual_information_candidate_lag|conditional_entropy_candidate_given_lag|residual_variance_after_lag_model|information_gain_over_lag	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	directionality_consistency_test	Prüfen, ob Richtung, Vorzeichen und i/j-Umkehr unabhängig dokumentiert sind.	directionality_class|ij_reversal_behavior|antisymmetry_score|symmetry_score|absolute_value_risk	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	unit_dimension_metadata_audit	Prüfen, ob physikalisch/proxy-artige Kandidaten Einheit und Dimension korrekt dokumentieren.	unit_present|dimension_vector_present|dimensionless_reason_present|conversion_rule_present|metadata_score	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_admissibility_gate	Zusammenführen aller Prüfungen zu einer Gate-Entscheidung.	criteria_pass_count|criteria_fail_count|critical_failures|admissibility_class|allowed_next_use|claim_boundary	not_executed_design_only	test_design_defined	requires_execution_no_result_claim	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_decision_logic (run_id, decision_class, required_conditions, blocking_conditions, allowed_next_use, claim_implication, physical_claim_release, design_status) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	decision_class	required_conditions	blocking_conditions	allowed_next_use	claim_implication	physical_claim_release	design_status
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_admissible_for_lag_mechanism_testing	All criteria pass in later execution; no critical alias flags.	Any confirmed alias, missing lineage, missing pair mapping.	later_lag_mechanism_testing_input_only	admissible_for_testing_not_confirmation	blocked_no_physics_claim	test_design_defined
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_admissible_only_after_lineage_repair	Non-alias plausible but lineage incomplete.	No repair artifact.	lineage_repair_then_retest	no_independence_claim	blocked_no_physics_claim	test_design_defined
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_admissible_only_after_metadata_repair	Proxy-like candidate missing units/dimensions.	Metadata absent after repair window.	metadata_repair_then_review	no_physical_proxy_claim	blocked_no_physics_claim	test_design_defined
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_rejected_alias_of_lag	Exact/absolute/monotonic/piecewise lag alias detected.	None.	exclude_from_independent_lag_gate	alias_rejection	blocked_no_physics_claim	test_design_defined
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_rejected_alias_of_pair_or_index	pair_id/index/order alias detected.	None.	exclude_from_independent_lag_gate	alias_rejection	blocked_no_physics_claim	test_design_defined
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_rejected_not_pair_mappable	Cannot map to 42 directed pair features.	None.	exclude_from_lag_mechanism_testing	mapping_rejection	blocked_no_physics_claim	test_design_defined
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_rejected_not_independent	Information gain and lineage do not support independence.	None.	exclude_from_independent_lag_gate	no_independence_claim	blocked_no_physics_claim	test_design_defined
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	candidate_requires_red_team_review	Conflicting tests, high correlation, or unclear alias risk.	Review not completed.	manual_review_before_any_use	requires_review_no_confirmation	blocked_no_physics_claim	test_design_defined
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_source_lineage_requirements (run_id, requirement_key, requirement_text, blocking_if_missing, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	requirement_key	requirement_text	blocking_if_missing	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	generating_run	Generating Run oder Datenquelle muss eindeutig angegeben sein.	true	lineage_required_before_admissibility
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	source_file_or_table	Quell-Datei oder DWH-Tabelle muss angegeben sein.	true	lineage_required_before_admissibility
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	transformation_rule	Transformationsregel muss vollständig dokumentiert sein.	true	lineage_required_before_admissibility
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	not_derived_from_forbidden_basis	Nicht-Ableitung aus lag, |j-i|, pair_id oder Indexordnung muss belegbar sein.	true	lineage_required_before_admissibility
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_pair_mapping_requirements (run_id, requirement_key, requirement_text, blocking_if_missing, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	requirement_key	requirement_text	blocking_if_missing	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	directed_pair_coverage	Coverage für 42 gerichtete Pair-Features muss messbar sein.	true	pair_mapping_required_before_testing
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	mapping_key_separation	Mapping-Schlüssel darf nicht zugleich Wertquelle sein.	true	pair_mapping_required_before_testing
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	missing_pair_report	Fehlende Paare müssen explizit gelistet werden.	true	pair_mapping_required_before_testing
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_unit_dimension_requirements (run_id, requirement_key, requirement_text, blocking_if_missing, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	requirement_key	requirement_text	blocking_if_missing	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	unit_present	Einheit muss vorhanden sein, wenn Kandidat physikalisch/proxy-artig ist.	true	metadata_required_for_proxy_review
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	dimension_vector_present	Dimensionsvektor oder dimensionslose Begründung muss vorhanden sein.	true	metadata_required_for_proxy_review
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	conversion_rule_present	Konversionsregel muss dokumentiert sein, falls Werte transformiert wurden.	true	metadata_required_for_proxy_review
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	dimensionless_reason_present	Dimensionslosigkeit muss begründet sein, falls keine Einheit vorliegt.	conditional	metadata_required_for_proxy_review
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_phase_response_rule (run_id, rule_key, rule_text, upstream_basis, required_new_evidence, claim_implication, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	rule_key	rule_text	upstream_basis	required_new_evidence	claim_implication	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	phase_response_abs_lag_alias	Wenn Phase-Response-Werte upstream als Alias von |j-i| bewertet wurden, dürfen sie nicht als unabhängige Lag-Variablen genutzt werden, außer ein neues Quellartefakt belegt unabhängige Erzeugung und Nicht-Alias-Verhalten.	input_scout_alias_risk_high_and_prior_phase_response_alias_assessment	new_source_artifact|source_lineage_audit|deterministic_alias_test|information_gain_over_lag_test	phase_response_no_independent_lag_variable_claim_without_new_source	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_deep_research_handoff (run_id, question_id, handoff_question, evidence_status) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	question_id	handoff_question	evidence_status
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	DRQ-001	Welche mathematischen Nicht-Alias-Kriterien sind für lag-dominierte Matrizen geeignet?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	DRQ-002	Welche Informationsmaße eignen sich zur Trennung von Kandidatenvariable und lag/|lag|?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	DRQ-003	Welche formalen Kriterien unterscheiden unabhängige Ordnungsvariablen von Indexsurrogaten?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	DRQ-004	Welche Reviewer-Einwände entstehen bei Kandidatenvariablen, die hoch mit |lag| korrelieren?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	DRQ-005	Welche Proxy-Kriterien sind in Moden-, Phasen-, Energie- und Impulsstrukturen methodisch zulässig?	question_only_no_deep_research_answer
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_claim_boundaries (run_id, claim_key, claim_text, status, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	claim_key	claim_text	status	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-001	QSB is physically validated	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-002	PBR exists physically	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-003	six lag axes are spacetime dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-004	spacetime emergence is proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-005	empirical validation exists	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-006	lag classes are physical dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-007	lag mechanism is physically proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-008	candidate artifact proves independent lag mechanism	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-009	candidate artifact proves physical proxy	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-010	DWH presence alone proves independence	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-011	repo presence alone proves independence	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-012	literature note alone proves proxy for current matrix	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-013	phase-response values are independent lag variables despite alias assessment	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-014	criteria definition confirms independence	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	BLOCK-015	admissible candidate class releases physical claim	blocked	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_independent_lag_variable_next_gate (run_id, next_gate, secondary_next_gate, execution_authorization, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	next_gate	secondary_next_gate	execution_authorization	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	independent_lag_variable_admissibility_execution_required	physical_proxy_source_review_required	not_authorized_in_this_design_run	blocked_no_physics_claim
\.

-- BEGIN generated validation results import
DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
COPY qsb_planck_bridge.pbr_independent_lag_variable_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	run_directory_exact	PASS	/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	required_files_exist	PASS	all_required_files_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	utf8_lf_text_files	PASS	all_required_text_files_utf8_lf
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	run_id_exact	PASS	QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	run_type	PASS	independent_lag_variable_design
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	execution_status_design_only	PASS	design_only_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	physical_claim_release_blocked	PASS	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	input_scout_referenced_or_blocked	PASS	available
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	next_gate_design_completed	PASS	independent_lag_variable_admissibility_execution_required
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	all_required_independence_criteria_present	PASS	criterion_rows=8
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	criteria_definition_no_confirmation	PASS	criteria_claim_implications_checked
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	all_required_alias_flags_present	PASS	all_alias_flags_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	phase_response_special_alias_rule_present	PASS	phase_response_abs_lag_alias
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	all_required_candidate_classes_present	PASS	all_classes_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	no_class_confirms_independence_or_physical_proxy	PASS	no_confirming_classes
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	all_required_test_designs_present	PASS	all_test_designs_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	no_tests_executed	PASS	test_design_only
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	all_required_decision_classes_present	PASS	all_decisions_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	decision_logic_claim_release_blocked	PASS	all_decisions_block_physical_claims
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	phase_response_special_rule_file_present	PASS	phase_response_abs_lag_alias
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	deep_research_questions_only	PASS	question_rows=5
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	manifest_target_run_id	PASS	QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	manifest_no_tests_no_nullmodels	PASS	tests=True nullmodels=True
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	no_nullmodels_executed	PASS	true
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	claim_boundaries_blocked	PASS	claim_rows=15
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	german_view_created	PASS	view_name_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	sql_copy_tables_present	PASS	required_copy_tables_present
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	forbidden_phrases_only_blocked_context	PASS	no_unblocked_forbidden_phrase_hits
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	no_files_outside_run_package_modified	PASS	no_outside_changes
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	pre_existing_modifications_recorded	PASS	
QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01	git_diff_check_passes	PASS	git diff --check
\.
-- END generated validation results import
COMMIT;
