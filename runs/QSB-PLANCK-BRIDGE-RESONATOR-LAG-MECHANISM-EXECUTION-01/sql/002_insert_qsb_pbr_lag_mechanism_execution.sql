BEGIN;

DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_execution_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_test_results WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_index_relabeling WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_order_scrambling WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_independent_lag_variable WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_shift_operator WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_toeplitz_dependency WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_physical_proxy WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_nullmodel_operationalization WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_decision WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_lineage WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_validation_results WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';

COPY qsb_planck_bridge.pbr_lag_mechanism_execution_summary (run_id, source_run_id, execution_status, claim_status, physical_claim_release, input_specificity_classification, input_critical_nullmodel, input_critical_reproduction_rate, final_decision_class, decision_rationale, next_gate, created_at_utc, git_commit) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	execution_status	claim_status	physical_claim_release	input_specificity_classification	input_critical_nullmodel	input_critical_reproduction_rate	final_decision_class	decision_rationale	next_gate	created_at_utc	git_commit
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	executed	lag_mechanism_execution_only	blocked_no_physics_claim	no_specificity	lag_preserving_shuffle_null	1.0	inconclusive_requires_more_inputs	Lag-/Toeplitz- und Ordnungsdiagnostik zeigen starke formale Lag-Abhängigkeit, aber unabhängige Lag-Variablen und physische Proxy-Daten fehlen.	input_artifact_enrichment_required	2026-07-08T09:57:42+00:00	0d600c6
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_test_results (run_id, source_run_id, test_id, test_key, deutscher_testname, execution_status, input_artifact, seed, sample_count, rank6_preserved_rate, lag_structure_preserved_rate, order_dependence_score, label_dependence_score, shift_orbit_consistency, shift_commutator_norm, toeplitz_fit_score, lag_explained_variance_ratio, independent_variable_available, independent_variable_name, lag_reconstruction_accuracy, physical_proxy_available, physical_proxy_name, proxy_lag_correlation, nullmodel_appropriateness_class, decision_signal, decision_class, specificity_relation, claim_implication, physical_claim_release, next_gate) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	test_id	test_key	deutscher_testname	execution_status	input_artifact	seed	sample_count	rank6_preserved_rate	lag_structure_preserved_rate	order_dependence_score	label_dependence_score	shift_orbit_consistency	shift_commutator_norm	toeplitz_fit_score	lag_explained_variance_ratio	independent_variable_available	independent_variable_name	lag_reconstruction_accuracy	physical_proxy_available	physical_proxy_name	proxy_lag_correlation	nullmodel_appropriateness_class	decision_signal	decision_class	specificity_relation	claim_implication	physical_claim_release	next_gate
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	LMX-001	index_relabeling_test	Index-Umbenennungstest	executed	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv	2026070802	1000	1.0	1.0		0.0					false			false				labels_alone_not_mechanism	inconclusive_requires_more_inputs	tests_lag_mechanism_after_no_specificity	formal_diagnostic_only	blocked_no_physics_claim	input_artifact_enrichment_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	LMX-002	order_scrambling_test	Ordnungsverwürfelungstest	executed	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv	2026070802	1000	1.0	0.001	0.999						false			false				lag_structure_order_dependent	inconclusive_requires_more_inputs	tests_lag_mechanism_after_no_specificity	formal_diagnostic_only	blocked_no_physics_claim	input_artifact_enrichment_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	LMX-003	independent_lag_variable_test	Unabhängige-Lag-Variablen-Test	blocked_missing_required_input	not_available	2026070802	0									false	phase_response_raw_range_assessed_as_lag_alias	0.0	false				candidate_variable_present_but_alias_of_abs_lag	inconclusive_requires_more_inputs	tests_lag_mechanism_after_no_specificity	formal_diagnostic_only	blocked_no_physics_claim	input_artifact_enrichment_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	LMX-004	shift_operator_test	Shift-Operator-Test	executed	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv	2026070802	0					0.0	15.407299555733353			false			false				cyclic_shift_operator_diagnostic_executed	inconclusive_requires_more_inputs	tests_lag_mechanism_after_no_specificity	formal_diagnostic_only	blocked_no_physics_claim	input_artifact_enrichment_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	LMX-005	toeplitz_dependency_test	Toeplitz-Abhängigkeitstest	executed	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv	2026070802	0							1.0	1.0	false			false				strong_lag_class_dependence_relative_to_scrambled_order	inconclusive_requires_more_inputs	tests_lag_mechanism_after_no_specificity	formal_diagnostic_only	blocked_no_physics_claim	input_artifact_enrichment_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	LMX-006	physical_proxy_test	Physikalischer-Proxy-Test	blocked_missing_physical_proxy_input	not_available	2026070802	0									false			false	not_available	0.0		physical_proxy_test_blocked_no_source_data	inconclusive_requires_more_inputs	tests_lag_mechanism_after_no_specificity	no_physical_proxy_claim	blocked_no_physics_claim	input_artifact_enrichment_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	LMX-007	nullmodel_operationalization_review	Nullmodell-Operationalisierungsreview	executed	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv	2026070802	0									false			false			hypothesis_preserving_control	nullmodel_preserves_target_mechanism_not_sufficient_for_physical_or_independent_claim	inconclusive_requires_more_inputs	tests_lag_mechanism_after_no_specificity	formal_diagnostic_only	blocked_no_physics_claim	input_artifact_enrichment_required
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_index_relabeling (run_id, sample_id, seed, structure_preserved_under_relabeling, label_permutation) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	sample_id	seed	structure_preserved_under_relabeling	label_permutation
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	1	2026070803	true	[3, 2, 4, 0, 6, 5, 1]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	2	2026070804	true	[0, 4, 6, 2, 5, 3, 1]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	3	2026070805	true	[0, 5, 2, 4, 1, 3, 6]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	4	2026070806	true	[2, 0, 4, 3, 5, 1, 6]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	5	2026070807	true	[2, 3, 0, 5, 1, 4, 6]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	6	2026070808	true	[0, 2, 6, 3, 4, 5, 1]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	7	2026070809	true	[2, 6, 3, 5, 4, 0, 1]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	8	2026070810	true	[3, 6, 1, 5, 0, 2, 4]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	9	2026070811	true	[2, 5, 1, 6, 3, 4, 0]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	10	2026070812	true	[2, 0, 6, 3, 5, 4, 1]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	11	2026070813	true	[3, 2, 4, 1, 6, 0, 5]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	12	2026070814	true	[5, 2, 1, 3, 6, 0, 4]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	13	2026070815	true	[3, 6, 2, 4, 0, 1, 5]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	14	2026070816	true	[2, 0, 1, 5, 6, 3, 4]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	15	2026070817	true	[3, 6, 5, 4, 1, 0, 2]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	16	2026070818	true	[6, 2, 3, 0, 1, 4, 5]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	17	2026070819	true	[0, 2, 3, 5, 4, 1, 6]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	18	2026070820	true	[6, 2, 0, 3, 5, 4, 1]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	19	2026070821	true	[3, 6, 0, 2, 5, 1, 4]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	20	2026070822	true	[6, 0, 5, 4, 3, 1, 2]
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_order_scrambling (run_id, sample_id, seed, scrambled_order, rank6_preserved, lag_structure_preserved, collapse_score, lag_structure_distance, antiparallelity_preserved) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	sample_id	seed	scrambled_order	rank6_preserved	lag_structure_preserved	collapse_score	lag_structure_distance	antiparallelity_preserved
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	1	2027070803	[6, 2, 4, 5, 0, 1, 3]	true	false	0.29395195545109631	4.4888457473362937	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	2	2027070804	[3, 5, 0, 1, 4, 6, 2]	true	false	0.26372428216240729	4.5044888421415559	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	3	2027070805	[2, 1, 0, 4, 5, 3, 6]	true	false	0.3019793736386811	4.0841504295367104	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	4	2027070806	[1, 5, 6, 3, 2, 0, 4]	true	false	0.25275303890520806	4.1357365634347927	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	5	2027070807	[2, 6, 5, 0, 3, 1, 4]	true	false	0.25746526036633621	4.4358927381823898	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	6	2027070808	[4, 3, 6, 2, 1, 5, 0]	true	false	0.31231320062832468	3.965000670239001	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	7	2027070809	[0, 1, 2, 3, 6, 5, 4]	true	false	0.60714888126596489	3.894770559091119	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	8	2027070810	[2, 1, 0, 5, 3, 6, 4]	true	false	0.24572067950947166	4.7110010112556333	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	9	2027070811	[0, 5, 1, 6, 3, 4, 2]	true	false	0.30811487010713334	4.1996457198335326	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	10	2027070812	[0, 1, 3, 6, 4, 2, 5]	true	false	0.31515518615722327	3.9905422363349596	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	11	2027070813	[3, 0, 4, 5, 6, 1, 2]	true	false	0.30833684019194729	4.6004639749383598	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	12	2027070814	[3, 2, 0, 5, 1, 4, 6]	true	false	0.29801011396614835	4.4108351860124291	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	13	2027070815	[1, 3, 2, 6, 4, 0, 5]	true	false	0.34724636016140537	4.2142142168931391	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	14	2027070816	[5, 2, 1, 4, 0, 6, 3]	true	false	0.31098546336834176	4.702896310323581	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	15	2027070817	[4, 1, 0, 3, 2, 6, 5]	true	false	0.35662143549212638	3.6829231080896485	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	16	2027070818	[1, 6, 2, 5, 4, 3, 0]	true	false	0.28788222412772724	4.4155970766718058	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	17	2027070819	[1, 4, 0, 3, 6, 5, 2]	true	false	0.35763074047258631	4.5372743599987162	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	18	2027070820	[5, 0, 4, 2, 1, 6, 3]	true	false	0.22899519119221204	4.5514342438030981	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	19	2027070821	[5, 0, 1, 2, 6, 3, 4]	true	false	0.32288771222191598	4.4626299203205102	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	20	2027070822	[1, 3, 6, 4, 5, 0, 2]	true	false	0.31727679832744593	5.054265449321993	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	21	2027070823	[4, 1, 5, 3, 2, 6, 0]	true	false	0.34157560812231647	4.2735268077295272	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	22	2027070824	[3, 2, 6, 1, 0, 5, 4]	true	false	0.33323483713253954	4.4729655241080168	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	23	2027070825	[4, 5, 0, 2, 1, 3, 6]	true	false	0.28290392429797301	4.3483449392147655	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	24	2027070826	[0, 4, 5, 3, 6, 2, 1]	true	false	0.35393584417565593	4.6289106583715984	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	25	2027070827	[6, 0, 5, 4, 2, 3, 1]	true	false	0.37636532007378254	3.3549075505759891	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	26	2027070828	[4, 0, 6, 1, 5, 2, 3]	true	false	0.25740404852908483	4.5507566791865655	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	27	2027070829	[4, 6, 0, 2, 1, 5, 3]	true	false	0.33936084287342277	4.6189190894925547	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	28	2027070830	[2, 3, 4, 0, 6, 1, 5]	true	false	0.25937618632249715	4.4641463923118758	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	29	2027070831	[2, 1, 3, 5, 6, 4, 0]	true	false	0.33983742212596041	4.5004994900679698	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	30	2027070832	[0, 6, 3, 2, 4, 5, 1]	true	false	0.37103637952427698	3.963205240690248	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	31	2027070833	[5, 2, 3, 0, 1, 6, 4]	true	false	0.31633175326961388	4.6959771768512821	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	32	2027070834	[0, 3, 6, 1, 4, 2, 5]	true	false	0.42891818908275631	3.5699970436671302	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	33	2027070835	[3, 5, 0, 4, 6, 1, 2]	true	false	0.29550179103062552	3.7892502993694852	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	34	2027070836	[4, 1, 5, 2, 3, 0, 6]	true	false	0.38414599347417888	4.3427344600535385	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	35	2027070837	[6, 4, 0, 5, 3, 1, 2]	true	false	0.35620091152135247	3.6708244877070988	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	36	2027070838	[6, 3, 2, 1, 5, 4, 0]	true	false	0.30292745045516334	3.4904598495514843	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	37	2027070839	[4, 2, 5, 3, 6, 0, 1]	true	false	0.33487855938103939	4.1034962227727974	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	38	2027070840	[2, 3, 6, 5, 1, 0, 4]	true	false	0.26885327566690653	4.0408681177447763	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	39	2027070841	[0, 4, 2, 5, 1, 6, 3]	true	false	0.29957209344220742	4.0001973120143379	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	40	2027070842	[3, 0, 5, 2, 1, 4, 6]	true	false	0.3644909399213116	3.7783468003304552	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	41	2027070843	[3, 2, 6, 0, 4, 1, 5]	true	false	0.35417795941663988	4.9616852293139351	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	42	2027070844	[3, 0, 4, 6, 1, 2, 5]	true	false	0.24955037172150932	4.3007510022720279	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	43	2027070845	[3, 1, 5, 4, 6, 0, 2]	true	false	0.33936084287342272	4.6189190894925547	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	44	2027070846	[4, 0, 1, 6, 3, 5, 2]	true	false	0.25746526036633627	4.4358927381823898	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	45	2027070847	[6, 3, 1, 2, 5, 0, 4]	true	false	0.25769855643769707	4.3151322793481617	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	46	2027070848	[3, 2, 1, 4, 0, 6, 5]	true	false	0.36794166265418748	3.7319104290426295	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	47	2027070849	[4, 3, 6, 5, 1, 0, 2]	true	false	0.3104612183995028	4.6127794495451768	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	48	2027070850	[6, 5, 4, 3, 2, 1, 0]	true	true	1	9.5757364394855573e-16	true
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	49	2027070851	[5, 1, 3, 6, 0, 2, 4]	true	false	0.37998527608981397	4.5505178201772702	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	50	2027070852	[1, 0, 5, 4, 2, 6, 3]	true	false	0.24296726667794902	4.1560778020638756	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	51	2027070853	[0, 5, 3, 1, 4, 6, 2]	true	false	0.31406410901037951	4.3745154911995385	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	52	2027070854	[2, 5, 0, 1, 6, 3, 4]	true	false	0.45295317362524085	4.2713432487228911	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	53	2027070855	[1, 0, 5, 3, 6, 2, 4]	true	false	0.21539639758336376	3.940721443697643	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	54	2027070856	[0, 5, 4, 1, 6, 3, 2]	true	false	0.55559871454591125	4.1146748611070922	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	55	2027070857	[1, 3, 6, 2, 0, 5, 4]	true	false	0.22464086762218682	4.192197382048775	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	56	2027070858	[0, 2, 4, 3, 6, 1, 5]	true	false	0.27476490507309864	4.1431705002345343	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	57	2027070859	[5, 6, 0, 1, 2, 4, 3]	true	false	0.43108197195072939	4.3483647932131912	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	58	2027070860	[2, 5, 3, 0, 4, 1, 6]	true	false	0.33568783160527077	4.4204080558734793	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	59	2027070861	[5, 0, 6, 3, 2, 4, 1]	true	false	0.41894370429716116	4.0455465446990422	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	60	2027070862	[0, 4, 1, 6, 3, 5, 2]	true	false	0.35381616284009032	3.9668751132362949	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	61	2027070863	[5, 2, 6, 0, 3, 4, 1]	true	false	0.33290526813472016	4.4739993592659655	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	62	2027070864	[0, 1, 5, 4, 6, 2, 3]	true	false	0.30320370321689943	3.9451775636678943	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	63	2027070865	[4, 6, 0, 5, 3, 2, 1]	true	false	0.25786125846330138	4.378171267284884	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	64	2027070866	[4, 3, 6, 0, 5, 2, 1]	true	false	0.3242685593399473	3.988762548193252	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	65	2027070867	[1, 4, 0, 3, 5, 2, 6]	true	false	0.41583022907278	3.8865590575649804	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	66	2027070868	[3, 6, 2, 1, 0, 5, 4]	true	false	0.30833684019194718	4.6004639749383589	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	67	2027070869	[0, 4, 5, 1, 6, 3, 2]	true	false	0.24538707085830752	4.2994730174457176	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	68	2027070870	[3, 5, 0, 4, 6, 2, 1]	true	false	0.27363428596597517	4.0491000120123735	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	69	2027070871	[6, 5, 0, 4, 1, 2, 3]	true	false	0.34858849477113463	4.500900725754283	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	70	2027070872	[2, 4, 6, 3, 0, 5, 1]	true	false	0.25973598118941549	4.3013363341933193	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	71	2027070873	[4, 0, 6, 3, 5, 2, 1]	true	false	0.22066732052852087	4.4219635155953823	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	72	2027070874	[1, 6, 0, 5, 2, 4, 3]	true	false	0.43640244213861235	4.1055532203318661	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	73	2027070875	[2, 6, 1, 4, 0, 3, 5]	true	false	0.31229770360492964	4.4127321588916928	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	74	2027070876	[1, 5, 4, 6, 3, 0, 2]	true	false	0.33001865700119393	4.5742600098627797	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	75	2027070877	[6, 4, 0, 2, 1, 3, 5]	true	false	0.44108488633729498	4.7042087145068008	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	76	2027070878	[6, 2, 3, 1, 5, 0, 4]	true	false	0.41015987098672435	4.6124187570967399	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	77	2027070879	[5, 4, 6, 0, 2, 3, 1]	true	false	0.32245277353228863	3.833243437361963	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	78	2027070880	[0, 3, 1, 5, 4, 6, 2]	true	false	0.29510658876247386	4.2406279733810157	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	79	2027070881	[3, 1, 2, 4, 0, 6, 5]	true	false	0.32474404743245844	4.360121785373865	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	80	2027070882	[4, 2, 3, 6, 5, 1, 0]	true	false	0.32161275246452448	4.2449711169007163	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	81	2027070883	[5, 2, 1, 6, 3, 4, 0]	true	false	0.31508735780472252	4.2146728827342903	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	82	2027070884	[5, 1, 4, 6, 0, 3, 2]	true	false	0.26975264926193049	4.1016083986676275	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	83	2027070885	[3, 2, 5, 6, 4, 0, 1]	true	false	0.2665317874745573	4.2592233075133246	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	84	2027070886	[4, 6, 1, 5, 2, 0, 3]	true	false	0.32349432627887048	4.4015705877074556	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	85	2027070887	[6, 2, 0, 1, 3, 5, 4]	true	false	0.33983742212596041	4.5004994900679698	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	86	2027070888	[4, 3, 1, 2, 5, 0, 6]	true	false	0.25130563694420188	4.3196666535058563	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	87	2027070889	[1, 2, 0, 6, 5, 3, 4]	true	false	0.34861814970692062	4.5999465118690699	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	88	2027070890	[1, 0, 4, 2, 3, 6, 5]	true	false	0.33269389777760566	3.6156245823522264	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	89	2027070891	[4, 2, 0, 1, 6, 5, 3]	true	false	0.3054846021297174	4.4472968465455667	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	90	2027070892	[4, 0, 5, 6, 3, 1, 2]	true	false	0.2558275982389327	4.1378260683988062	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	91	2027070893	[6, 4, 0, 5, 1, 2, 3]	true	false	0.25906011572735188	4.3025109999506972	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	92	2027070894	[3, 4, 5, 0, 1, 6, 2]	true	false	0.32286303936052851	4.3900002599610577	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	93	2027070895	[1, 0, 6, 3, 2, 5, 4]	true	false	0.36943190514551771	3.4464250473877795	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	94	2027070896	[6, 1, 5, 4, 2, 0, 3]	true	false	0.2667551997422915	4.1991503574244273	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	95	2027070897	[1, 6, 0, 3, 5, 4, 2]	true	false	0.30100579844652914	4.1139237609404402	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	96	2027070898	[1, 0, 2, 6, 3, 4, 5]	true	false	0.29988978742991329	4.2237119805913244	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	97	2027070899	[6, 4, 2, 3, 0, 5, 1]	true	false	0.27476490507309859	4.1431705002345343	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	98	2027070900	[5, 2, 6, 0, 1, 3, 4]	true	false	0.23406967580009211	4.9704073170888119	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	99	2027070901	[3, 4, 1, 5, 6, 2, 0]	true	false	0.23694444800753819	4.0691897646947783	false
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	100	2027070902	[5, 2, 4, 1, 3, 0, 6]	true	false	0.50290086114262111	4.9660726764617422	false
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_independent_lag_variable (run_id, test_key, execution_status, independent_variable_available, independent_variable_name, lag_reconstruction_accuracy, lag_proxy_correlation, lag_proxy_rank_correlation, lag_proxy_mutual_information_or_group_score, decision_signal) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	execution_status	independent_variable_available	independent_variable_name	lag_reconstruction_accuracy	lag_proxy_correlation	lag_proxy_rank_correlation	lag_proxy_mutual_information_or_group_score	decision_signal
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	independent_lag_variable_test	blocked_missing_required_input	False	phase_response_raw_range_assessed_as_lag_alias	0.0	1.0	1.0	1.0	candidate_variable_present_but_alias_of_abs_lag
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_shift_operator (run_id, test_key, execution_status, shift_operator_constructed, shift_orbit_consistency, shift_commutator_norm, shift_class_reproduction_score, translation_invariance_score, decision_signal) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	execution_status	shift_operator_constructed	shift_orbit_consistency	shift_commutator_norm	shift_class_reproduction_score	translation_invariance_score	decision_signal
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	shift_operator_test	executed	True	0.0	15.407299555733353	0.24681707126788255	0.24681707126788255	cyclic_shift_operator_diagnostic_executed
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_toeplitz_dependency (run_id, test_key, execution_status, toeplitz_fit_score, within_lag_variance_mean, between_lag_variance, lag_explained_variance_ratio, toeplitz_residual_norm, scrambled_toeplitz_fit_score_mean, decision_signal) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	execution_status	toeplitz_fit_score	within_lag_variance_mean	between_lag_variance	lag_explained_variance_ratio	toeplitz_residual_norm	scrambled_toeplitz_fit_score_mean	decision_signal
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	toeplitz_dependency_test	executed	1.0	2.5399476761595057e-33	0.1930328739481814	1.0	2.1361427427109544e-15	0.15194353256412516	strong_lag_class_dependence_relative_to_scrambled_order
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_physical_proxy (run_id, test_key, execution_status, physical_proxy_available, physical_proxy_name, physical_proxy_source_artifact, proxy_lag_correlation, proxy_lag_monotonicity_score, proxy_group_reproduction_rate, proxy_independence_assessment, proxy_status, claim_implication, decision_signal) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	execution_status	physical_proxy_available	physical_proxy_name	physical_proxy_source_artifact	proxy_lag_correlation	proxy_lag_monotonicity_score	proxy_group_reproduction_rate	proxy_independence_assessment	proxy_status	claim_implication	decision_signal
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	physical_proxy_test	blocked_missing_physical_proxy_input	False	not_available	not_available	0.0	0.0	0.0	no_independent_physical_proxy_input_found	not_available	no_physical_proxy_claim	physical_proxy_test_blocked_no_source_data
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_nullmodel_operationalization (run_id, test_key, execution_status, lag_preserving_nullmodel_role, overpreservation_risk, hypothesis_preservation_score, nullmodel_appropriateness_class, review_conclusion, decision_signal, critical_reproduction_rate) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	execution_status	lag_preserving_nullmodel_role	overpreservation_risk	hypothesis_preservation_score	nullmodel_appropriateness_class	review_conclusion	decision_signal	critical_reproduction_rate
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	nullmodel_operationalization_review	executed	preserves_hypothesized_lag_class_mechanism	high	1.0	hypothesis_preserving_control	1000_of_1000_reproduction_is_expected_if_lag_class_membership_is_the_target_mechanism	nullmodel_preserves_target_mechanism_not_sufficient_for_physical_or_independent_claim	1.0
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_decision (run_id, final_decision_class, decision_rationale, order_dependence_score, toeplitz_fit_score, shift_class_reproduction_score, independent_variable_available, physical_proxy_available, claim_status, physical_claim_release, next_gate) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	final_decision_class	decision_rationale	order_dependence_score	toeplitz_fit_score	shift_class_reproduction_score	independent_variable_available	physical_proxy_available	claim_status	physical_claim_release	next_gate
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	inconclusive_requires_more_inputs	Lag-/Toeplitz- und Ordnungsdiagnostik zeigen starke formale Lag-Abhängigkeit, aber unabhängige Lag-Variablen und physische Proxy-Daten fehlen.	0.999	1.0	0.24681707126788255	false	false	lag_mechanism_execution_only	blocked_no_physics_claim	input_artifact_enrichment_required
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_claim_boundaries (run_id, claim_key, status, claim_text, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	claim_key	status	claim_text	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	formal_lag_diagnostic	allowed_formal_only	Die Lag-Diagnostik ist ein formaler Befund ohne physikalische Freigabe.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	qsb_physical_validation	blocked	Eine physische QSB-Validierungsbehauptung ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	pbr_physical_existence	blocked	Eine physische PBR-Existenzbehauptung ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	lag_axes_dimensions	blocked	Eine Deutung der sechs Lag-Achsen als Raumzeitdimensionen ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	spacetime_emergence	blocked	Ein Beweis für Raumzeit-Entstehung ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	empirical_validation	blocked	Empirische Validierung ist nicht freigegeben.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	lag_mechanism_physical_proof	blocked	Ein physischer Beweis des Lag-Mechanismus ist nicht freigegeben.	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_lineage (run_id, source_run_id, source_path, source_role, sha256) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	source_path	source_role	sha256
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	design_input	directory_reference
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	result_review_input	directory_reference
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01	nullmodel_execution_context	directory_reference
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-EXTRACT03A-R1	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv	matrix_input	e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-EXTRACT03A-R1	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/10_phase_response_vector_summary.csv	assessed_candidate_proxy_alias	adb297a1964527425361304af4fe11d0397c9d29074e721a279039de6cc0e5b6
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	QSB-EXTRACT03A-R1	runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv	matrix_validation_context	a0137b42013e3191657d8b3e0b53c28015cb1eb63e5b6371fc96c4e144bbec27
\.

-- BEGIN generated validation results import
COPY qsb_planck_bridge.pbr_lag_mechanism_validation_results (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:README.md	pass	README.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01.md	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:RUN_COMMANDS_PBR_LAG_MECHANISM_EXECUTION01.md	pass	RUN_COMMANDS_PBR_LAG_MECHANISM_EXECUTION01.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/lag_mechanism_execution_summary.csv	pass	data/lag_mechanism_execution_summary.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/lag_mechanism_test_results.csv	pass	data/lag_mechanism_test_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/index_relabeling_results.csv	pass	data/index_relabeling_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/order_scrambling_results.csv	pass	data/order_scrambling_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/independent_lag_variable_results.csv	pass	data/independent_lag_variable_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/shift_operator_results.csv	pass	data/shift_operator_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/toeplitz_dependency_results.csv	pass	data/toeplitz_dependency_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/physical_proxy_results.csv	pass	data/physical_proxy_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/nullmodel_operationalization_review.csv	pass	data/nullmodel_operationalization_review.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/lag_mechanism_decision.csv	pass	data/lag_mechanism_decision.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/claim_boundaries.csv	pass	data/claim_boundaries.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/input_run_lineage.csv	pass	data/input_run_lineage.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:data/lag_mechanism_execution_manifest.json	pass	data/lag_mechanism_execution_manifest.json
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_SUMMARY_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_SUMMARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_TEST_RESULTS_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_TEST_RESULTS_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_CLAIM_BOUNDARY_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_CLAIM_BOUNDARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_NEXT_GATE_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_NEXT_GATE_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:docs/PBR_LAG_MECHANISM_EXECUTION_INTERPRETATION_DE.md	pass	docs/PBR_LAG_MECHANISM_EXECUTION_INTERPRETATION_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:scripts/run_pbr_lag_mechanism_execution.py	pass	scripts/run_pbr_lag_mechanism_execution.py
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:scripts/validate_pbr_lag_mechanism_execution.py	pass	scripts/validate_pbr_lag_mechanism_execution.py
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:sql/001_create_qsb_pbr_lag_mechanism_execution.sql	pass	sql/001_create_qsb_pbr_lag_mechanism_execution.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:sql/002_insert_qsb_pbr_lag_mechanism_execution.sql	pass	sql/002_insert_qsb_pbr_lag_mechanism_execution.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:sql/003_validation_queries.sql	pass	sql/003_validation_queries.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	exists:validation/validation_results.csv	pass	validation/validation_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	run_id_consistency	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	lineage_includes_design_and_review	pass	QSB-EXTRACT03A-R1,QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01,QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01,QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	all_seven_test_families	pass	independent_lag_variable_test,index_relabeling_test,nullmodel_operationalization_review,order_scrambling_test,physical_proxy_test,shift_operator_test,toeplitz_dependency_test
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	valid_execution_status_each_test	pass	status set
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	final_decision_allowed	pass	inconclusive_requires_more_inputs
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	physical_claim_release_blocked	pass	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	physical_proxy_candidate_requires_source	pass	not_available
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	missing_proxy_no_proxy_candidate	pass	inconclusive_requires_more_inputs
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	forbidden_context:QSB is physically validated	pass	QSB is physically validated
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	forbidden_context:PBR exists physically	pass	PBR exists physically
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	forbidden_context:six lag axes are spacetime dimensions	pass	six lag axes are spacetime dimensions
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	forbidden_context:spacetime emergence is proven	pass	spacetime emergence is proven
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	forbidden_context:empirical validation exists	pass	empirical validation exists
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	forbidden_context:lag mechanism is physically proven	pass	lag mechanism is physically proven
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	sql_copy_column_lists_match_rows	pass	COPY TSV blocks
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	csv_lf_line_endings	pass	13 CSV files
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	csv_lineterminator_declared	pass	csv.DictWriter lineterminator
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	utf8_text_files_readable	pass	27 files
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	git_diff_check	pass	ok
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01	no_files_outside_run_package_modified	pass	ok
\.
-- END generated validation results import
COMMIT;
