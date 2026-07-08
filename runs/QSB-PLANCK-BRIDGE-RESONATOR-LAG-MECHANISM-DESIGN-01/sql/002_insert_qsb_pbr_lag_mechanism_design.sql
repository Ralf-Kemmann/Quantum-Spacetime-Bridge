BEGIN;

DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_design_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_test_family_spec WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_decision_cases WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_required_inputs WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_required_metrics WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_next_gate_decision WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_failure_modes WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
DELETE FROM qsb_planck_bridge.pbr_lag_mechanism_validation_results WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';

COPY qsb_planck_bridge.pbr_lag_mechanism_design_summary (run_id, source_run_id, design_status, execution_status, claim_status, physical_claim_release, input_specificity_classification, input_critical_nullmodel, input_critical_reproduction_rate, next_gate, secondary_next_gate, created_at_utc, git_commit) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_run_id	design_status	execution_status	claim_status	physical_claim_release	input_specificity_classification	input_critical_nullmodel	input_critical_reproduction_rate	next_gate	secondary_next_gate	created_at_utc	git_commit
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01	lag_mechanism_design_completed_execution_required	design_only_not_executed	lag_mechanism_design_only	blocked_no_physics_claim	no_specificity	lag_preserving_shuffle_null	1.0	lag_mechanism_execution_required	nullmodel_operationalization_review_required	2026-07-08T09:33:49+00:00	db46ae0
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_test_family_spec (test_id, test_key, deutscher_testname, purpose_de, core_question_de, preserved_quantities, perturbed_quantities, required_input_artifacts, required_metrics, expected_diagnostics, admissibility_criteria, decision_rule, failure_modes, claim_implication_if_pass, claim_implication_if_fail, execution_authorization_status, next_gate_implication, run_id, source_run_id) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
test_id	test_key	deutscher_testname	purpose_de	core_question_de	preserved_quantities	perturbed_quantities	required_input_artifacts	required_metrics	expected_diagnostics	admissibility_criteria	decision_rule	failure_modes	claim_implication_if_pass	claim_implication_if_fail	execution_authorization_status	next_gate_implication	run_id	source_run_id
LM-001	index_relabeling_test	Index-Umbenennungstest	Prüfen, ob die Struktur bei beliebiger Umbenennung der Kanäle erhalten bleibt.	Hängt die Struktur an den Namen/Labels der Indizes?	Matrixdimension; Paaranzahl; Auswertetoleranzen	Kanalnamen und Labelzuordnung	K_candidate; pair_id-Tabelle; Kanal-Label-Mapping	Rang; Lag-Struktur-Distanz; Reproduktionsrate unter Relabeling	Relabeling-Invarianzprofil; Strukturverlust bei nicht ordnungserhaltender Umbenennung	Bijektive Umbenennung; keine Testausführung in Designlauf	Wenn Struktur beliebige Umbenennung überlebt, spricht das gegen reine Labelabhängigkeit.	Nicht-bijektive Labels; verdeckte Ordnungserhaltung	Formal keine stärkere Spezifität; nur Testdesign	Hinweis auf Ordnung/Label als mögliche Träger prüfen	design_only_not_executed	lag_mechanism_execution_required	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
LM-002	order_scrambling_test	Ordnungsverwürfelungstest	Prüfen, ob die Struktur verschwindet, wenn die Kanalordnung zerstört wird.	Ist die Ordnung selbst der Träger des Befunds?	Matrixdimension; Paaranzahl; Seedplan	Kanalordnung und daraus berechnete Lags	K_candidate; ursprüngliche Kanalordnung; Scrambling-Regel	Lag-Klassen-Reproduktion; Rang; Antiparallelität; Eigenprofilabstand	Strukturverlust oder Strukturerhalt nach Ordnungszerstörung	Permutation muss dokumentiert und reproduzierbar sein	Wenn Scrambling die Struktur zerstört, ist Ordnung zentraler Trägerkandidat.	Scrambling erhält unbeabsichtigt Nachbarschaften	Formaler Hinweis auf Ordnungsabhängigkeit	Keine unabhängige Lag-Mechanik ohne weitere Herleitung	design_only_not_executed	lag_mechanism_execution_required	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
LM-003	independent_lag_variable_test	Unabhängige-Lag-Variablen-Test	Prüfen, ob Lag-Klassen aus einer unabhängigen Größe rekonstruiert werden können.	Gibt es eine unabhängige Größe, die die Lag-Klassen trägt?	Matrix; Paarfeatures; Toleranzen	Zuordnung der Lag-Klasse durch unabhängige Variable	Momentum-, Energie-, Phasen-, Frequenz-, Moden-, Spektrallücken- oder Skalenmapping-Tabelle	Übereinstimmung unabhängiger Klassen mit Lag-Klassen; Clusterreinheit; Distanzmatrix-Korrelation	Rekonstruktionsquote; Fehlklassifikationsprofil	Unabhängige Variable muss vor Testausführung fixiert sein	Pass stützt Kandidat eines unabhängigen formalen Mechanismus.	Proxy nachträglich angepasst; fehlende Unabhängigkeit	Nur formaler Mechanismuskandidat; keine Physikfreigabe	Bei Fail bleibt Lag als Index-/Ordnungskonstruktion plausibler	design_only_not_executed	lag_mechanism_execution_required	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
LM-004	shift_operator_test	Shift-Operator-Test	Prüfen, ob die Lag-Klassenstruktur einer echten Shift-/Translationsstruktur entspricht.	Entsprechen Lag-Klassen Orbits oder Klassen eines unabhängigen Shift-Operators?	Featuremenge; Kanalanzahl; formale Operatorregel	Operatorwirkung auf Kanäle und Paare	Definierter Shift-Operator; Orbit-Tabelle; K_candidate	Orbit-Kohärenz; Klassenstabilität; Kommutator-/Invarianzdiagnostik	Orbitklassenvergleich mit Lag-Klassen	Operator muss unabhängig von Zielbefund definiert sein	Pass stützt formalen Shift-/Translationsmechanismus.	Operator wird aus Lag-Befund rückkonstruiert	Formal stärkere Mechanismushypothese möglich	Kein unabhängiger Shift-Mechanismus belegt	design_only_not_executed	lag_mechanism_execution_required	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
LM-005	toeplitz_dependency_test	Toeplitz-Abhängigkeitstest	Prüfen, ob K_ij im Wesentlichen von j-i abhängt.	Ist die Matrixstruktur Toeplitz-artig oder lag-dominiert?	Matrixform; Eintragswerte; Toleranzen	Abhängigkeit von absoluter Position versus Lag	K_candidate; Paarmetadaten; Lag-Zuordnung	Lag-only-Fit; Residuen; Toeplitz-Distanz; positionsabhängige Reststruktur	Residuenprofil nach Lag-only-Modell	Modell und Residuentoleranz vor Ausführung fixieren	Pass stützt lag-dominierte formale Struktur.	Toeplitz-Fit trivialisiert durch Konstruktion	Formale Lag-Dominanz, keine Physikfreigabe	Positionseffekte sprechen gegen reines Lag-only-Modell	design_only_not_executed	lag_mechanism_execution_required	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
LM-006	physical_proxy_test	Physikalischer-Proxy-Test	Prüfen, ob Lag mit einer unabhängig physikalisch motivierten Proxy-Größe korrespondiert.	Korrespondiert Lag mit einer vorab definierten Proxy-Ordnung?	Matrix; Pairfeatures; Gate-Status	Proxy-Koordinate und Proxy-Abstände	Impulsdifferenz; quadratische Impulsdifferenz; Energiedifferenz; Phasenfortschritt; Frequenzabstand; Modenabstand; Skalenmapping	Proxy-Lag-Korrelation; Klassenreinheit; Robustheit gegen alternative Proxies	Proxy-Rekonstruktionsprofil und Negativkontrollen	Proxy muss unabhängig und vorab begründet sein	Pass stützt nur physikalisch motivierbaren Proxy-Kandidaten.	Proxy post hoc gewählt; physikalische Überdeutung	Keine physikalische Validierung; nur Gate-Kandidat	Kein tragfähiger Proxy in dieser Operationalisierung	design_only_not_executed	lag_mechanism_execution_required	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
LM-007	nullmodel_operationalization_review	Nullmodell-Operationalisierungsreview	Bewerten, ob das lag-erhaltende Shuffle-Nullmodell genau angemessen, zu permissiv oder hypothesenzerstörend übererhaltend ist.	Hat das lag_preserving_shuffle_null genau den zu prüfenden Mechanismus erhalten und deshalb zwangsläufig reproduziert?	Execution-Artefakte; Nullmodelldefinitionen; Claim-Boundary	Interpretation der Erhaltungsregeln	Nullmodel-Design; Execution-Summary; Familienmetriken	Erhaltungsgrad; Hypothesenbezug; Reproduktionszwang	Klassifikation als angemessen, zu permissiv oder übererhaltend	Review muss ohne neue Tests auskommen	Pass klärt, ob das Nullmodell den Zielmechanismus konserviert.	Review vermischt Testausführung und Designbewertung	Schärft Folgearchitektur ohne neue Claims	Unklarheit erzwingt Re-Design vor Ausführung	design_only_not_executed	lag_mechanism_execution_required	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_decision_cases (run_id, case_id, lag_structure_status, meaning_de, allowed_conclusion_de, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	case_id	lag_structure_status	meaning_de	allowed_conclusion_de	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	CASE-001	pure_index_construction	Lag-Klassen entstehen nur durch Kanalnummerierung und pair_id-Lagdefinition.	Die Lag-Klassenstruktur ist formal vorhanden, aber nicht als unabhängiger Mechanismus belegt.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	CASE-002	formal_lag_mechanism_candidate	Lag-Klassen können aus unabhängiger formaler Struktur abgeleitet werden.	Die Lag-Klassenstruktur ist Kandidat eines unabhängigen formalen Mechanismus.	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	CASE-003	physical_proxy_candidate	Lag-Klassen korrelieren mit vorab definierter physikalisch motivierter Proxy-Größe.	Die Lag-Klassenstruktur ist Kandidat einer physikalisch motivierbaren Ordnungsrelation; Interpretation bleibt gate-pflichtig.	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_required_inputs (run_id, test_key, required_input_artifacts, input_status) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	required_input_artifacts	input_status
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	index_relabeling_test	K_candidate; pair_id-Tabelle; Kanal-Label-Mapping	required_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	order_scrambling_test	K_candidate; ursprüngliche Kanalordnung; Scrambling-Regel	required_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	independent_lag_variable_test	Momentum-, Energie-, Phasen-, Frequenz-, Moden-, Spektrallücken- oder Skalenmapping-Tabelle	required_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	shift_operator_test	Definierter Shift-Operator; Orbit-Tabelle; K_candidate	required_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	toeplitz_dependency_test	K_candidate; Paarmetadaten; Lag-Zuordnung	required_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	physical_proxy_test	Impulsdifferenz; quadratische Impulsdifferenz; Energiedifferenz; Phasenfortschritt; Frequenzabstand; Modenabstand; Skalenmapping	required_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	nullmodel_operationalization_review	Nullmodel-Design; Execution-Summary; Familienmetriken	required_before_execution
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_required_metrics (run_id, test_key, required_metrics, metric_status) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	required_metrics	metric_status
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	index_relabeling_test	Rang; Lag-Struktur-Distanz; Reproduktionsrate unter Relabeling	defined_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	order_scrambling_test	Lag-Klassen-Reproduktion; Rang; Antiparallelität; Eigenprofilabstand	defined_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	independent_lag_variable_test	Übereinstimmung unabhängiger Klassen mit Lag-Klassen; Clusterreinheit; Distanzmatrix-Korrelation	defined_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	shift_operator_test	Orbit-Kohärenz; Klassenstabilität; Kommutator-/Invarianzdiagnostik	defined_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	toeplitz_dependency_test	Lag-only-Fit; Residuen; Toeplitz-Distanz; positionsabhängige Reststruktur	defined_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	physical_proxy_test	Proxy-Lag-Korrelation; Klassenreinheit; Robustheit gegen alternative Proxies	defined_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	nullmodel_operationalization_review	Erhaltungsgrad; Hypothesenbezug; Reproduktionszwang	defined_not_executed
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_claim_boundaries (run_id, claim_key, claim_text, status, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	claim_key	claim_text	status	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-001	QSB is physically validated	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-002	PBR exists physically	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-003	six lag axes are spacetime dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-004	spacetime emergence is proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-005	empirical validation exists	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-006	lag classes are physical dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-007	lag mechanism is physically proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-008	no_specificity disproves QSB	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	BLOCK-009	no_specificity proves QSB	blocked	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_next_gate_decision (run_id, next_gate, secondary_next_gate, execution_authorization, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	next_gate	secondary_next_gate	execution_authorization	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	lag_mechanism_execution_required	nullmodel_operationalization_review_required	not_authorized_in_this_design_run	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_lag_mechanism_failure_modes (run_id, test_key, failure_modes, mitigation_status) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	test_key	failure_modes	mitigation_status
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	index_relabeling_test	Nicht-bijektive Labels; verdeckte Ordnungserhaltung	review_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	order_scrambling_test	Scrambling erhält unbeabsichtigt Nachbarschaften	review_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	independent_lag_variable_test	Proxy nachträglich angepasst; fehlende Unabhängigkeit	review_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	shift_operator_test	Operator wird aus Lag-Befund rückkonstruiert	review_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	toeplitz_dependency_test	Toeplitz-Fit trivialisiert durch Konstruktion	review_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	physical_proxy_test	Proxy post hoc gewählt; physikalische Überdeutung	review_before_execution
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	nullmodel_operationalization_review	Review vermischt Testausführung und Designbewertung	review_before_execution
\.

-- BEGIN generated validation results import
COPY qsb_planck_bridge.pbr_lag_mechanism_validation_results (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:README.md	pass	README.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01.md	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:RUN_COMMANDS_PBR_LAG_MECHANISM_DESIGN01.md	pass	RUN_COMMANDS_PBR_LAG_MECHANISM_DESIGN01.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_design_summary.csv	pass	data/lag_mechanism_design_summary.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_test_family_spec.csv	pass	data/lag_mechanism_test_family_spec.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_decision_cases.csv	pass	data/lag_mechanism_decision_cases.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_required_inputs.csv	pass	data/lag_mechanism_required_inputs.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_required_metrics.csv	pass	data/lag_mechanism_required_metrics.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_claim_boundaries.csv	pass	data/lag_mechanism_claim_boundaries.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_next_gate_decision.csv	pass	data/lag_mechanism_next_gate_decision.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_failure_modes.csv	pass	data/lag_mechanism_failure_modes.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:data/lag_mechanism_design_manifest.json	pass	data/lag_mechanism_design_manifest.json
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:docs/PBR_LAG_MECHANISM_DESIGN_SUMMARY_DE.md	pass	docs/PBR_LAG_MECHANISM_DESIGN_SUMMARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:docs/PBR_LAG_MECHANISM_DESIGN_TESTS_DE.md	pass	docs/PBR_LAG_MECHANISM_DESIGN_TESTS_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:docs/PBR_LAG_MECHANISM_DESIGN_CLAIM_BOUNDARY_DE.md	pass	docs/PBR_LAG_MECHANISM_DESIGN_CLAIM_BOUNDARY_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:docs/PBR_LAG_MECHANISM_DESIGN_NEXT_GATE_DE.md	pass	docs/PBR_LAG_MECHANISM_DESIGN_NEXT_GATE_DE.md
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:scripts/run_pbr_lag_mechanism_design.py	pass	scripts/run_pbr_lag_mechanism_design.py
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:scripts/validate_pbr_lag_mechanism_design.py	pass	scripts/validate_pbr_lag_mechanism_design.py
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:sql/001_create_qsb_pbr_lag_mechanism_design.sql	pass	sql/001_create_qsb_pbr_lag_mechanism_design.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:sql/002_insert_qsb_pbr_lag_mechanism_design.sql	pass	sql/002_insert_qsb_pbr_lag_mechanism_design.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:sql/003_validation_queries.sql	pass	sql/003_validation_queries.sql
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	exists:validation/validation_results.csv	pass	validation/validation_results.csv
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	run_id_consistency	pass	QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	design_only_execution_status	pass	design_only_not_executed
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	no_tests_executed	pass	manifest flags
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	all_seven_test_families_once	pass	['independent_lag_variable_test', 'index_relabeling_test', 'nullmodel_operationalization_review', 'order_scrambling_test', 'physical_proxy_test', 'shift_operator_test', 'toeplitz_dependency_test']
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	all_three_decision_cases_once	pass	['formal_lag_mechanism_candidate', 'physical_proxy_candidate', 'pure_index_construction']
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	input_specificity_no_specificity	pass	no_specificity
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	input_critical_nullmodel	pass	lag_preserving_shuffle_null
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	input_critical_reproduction_rate	pass	1.0
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	physical_claim_release_blocked	pass	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	next_gate	pass	lag_mechanism_execution_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	secondary_next_gate	pass	nullmodel_operationalization_review_required
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	blocked_claims_present	pass	[]
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	forbidden_context:QSB is physically validated	pass	QSB is physically validated
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	forbidden_context:PBR exists physically	pass	PBR exists physically
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	forbidden_context:six lag axes are spacetime dimensions	pass	six lag axes are spacetime dimensions
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	forbidden_context:spacetime emergence is proven	pass	spacetime emergence is proven
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	forbidden_context:empirical validation exists	pass	empirical validation exists
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	sql_copy_column_lists_match_rows	pass	COPY TSV blocks
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	csv_lf_line_endings	pass	9 CSV files
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	csv_lineterminator_declared	pass	csv.DictWriter lineterminator
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	utf8_text_files_readable	pass	22 files
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	git_diff_check	pass	ok
QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01	no_files_outside_run_package_modified	pass	ok
\.
-- END generated validation results import
COMMIT;
