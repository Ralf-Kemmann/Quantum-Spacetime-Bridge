BEGIN;

DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_scout_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_repo_inventory WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_dwh_inventory WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_candidate_variables WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_lineage_assessment WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_alias_risk WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_physical_proxy_sources WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_pair_mapping_readiness WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_gap_update WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_deep_research_handoff WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_next_gate WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_scout_summary (run_id, run_type, execution_status, claim_status, physical_claim_release, input_gate, source_final_decision_class, scout_decision, next_gate, repo_scout_status, dwh_scout_status, candidate_count, repo_artifact_match_count, dwh_artifact_match_count, pre_existing_modified_review_run, git_head, created_at_utc) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	run_type	execution_status	claim_status	physical_claim_release	input_gate	source_final_decision_class	scout_decision	next_gate	repo_scout_status	dwh_scout_status	candidate_count	repo_artifact_match_count	dwh_artifact_match_count	pre_existing_modified_review_run	git_head	created_at_utc
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	dwh_repo_artifact_scout	executed	input_artifact_scout_only	blocked_no_physics_claim	input_artifact_enrichment_required	inconclusive_requires_more_inputs	candidate_artifacts_found_but_alias_risk_high	independent_lag_variable_design_required	executed	executed	260	5740	145	 M runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01/data/lag_mechanism_execution_review_summary.csv| M runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01/sql/002_insert_qsb_pbr_lag_mechanism_execution_result_review.sql	e64dd18	2026-07-08T10:47:33+00:00
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_repo_inventory (run_id, source_path, matched_terms, artifact_kind) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	source_path	matched_terms	artifact_kind
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-06/public_profile_links.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-06/source_inventory.md	E_i|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/FIELD_LIST.md	E_i|Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/compact_contact_table_en.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/compact_contact_table_es.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/contact_figure_content_spec.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_records.json	E_i|Phase|mode|p_i|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_schema.json	E_i|Phase|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/field_aliases_de.json	E_i|Paar|Phase|lag|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/field_aliases_en.json	E_i|Phase|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/OUTREACH01A-DTC-DEMO01/field_aliases_es.json	E_i|Phase|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-01/candidate_source_registry.csv	E_i|E_j|Matrix|Phase|frequency|mode|phase|phase_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-01/preflight_config.json	E_i|Matrix|Phase|frequency|mode|phase|phase_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02A/benzene_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02A/benzene_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02A/c60_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02A/c60_faces.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02A/c60_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02A/sp2_contrast_config.json	Phase|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02A/sp2_contrast_manifest.json	Phase|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/adamantane_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/adamantane_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_config.json	r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json	r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/ethyne_edges.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02B/ethyne_nodes.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02C/control_edges.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02C/control_ensemble_config.json	r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json	r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02C/control_family_summary.csv	r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02C/control_nodes.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02C/control_validation_summary.csv	r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02D/control_diagnostic_summary.csv	lag|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02D/highest_risk_mimic_diagnostic.csv	lag	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02D/original_vs_control_separation.csv	lag|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02E/README.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02E/control_destruction_effectiveness_summary.csv	lag|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02E/control_mimic_failure_inventory.csv	E_i|lag|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02E/control_mimicry_revision_manifest.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02E/diagnostic_specificity_summary.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02E/mimic_family_risk_summary.csv	lag|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-BRIDGE-DATA-02E/revision_recommendation_summary.csv	lag|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-02/FIELD_LIST.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-02/candidate_state_record_schema.json	E_i|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-02/example_candidate_state_records.json	E_i|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-04/field_aliases_de.json	E_i|Kandidat	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-04/inner_sphere_et_state_records.json	E_i|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-04/source_inventory.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-04/transition_candidates.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-05/field_aliases_de.json	E_i|lag	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-05/negative_control_state_pairs.json	E_i|mode|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-05/robustness_test_cases.json	E_i|mode|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-06/field_aliases_de.json	E_i|Kandidat|Modus|lag|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-06/oxalate_case_state_records.json	E_i|mode|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-06/oxalate_transition_candidates.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY06B-06/source_inventory.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-02/cycle_phase_rules.json	E_i|Phase|mode|phase|phase_i|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-02/field_aliases_de.json	E_i|Modus|Phase|mode|phase|phase_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-02/oregonator_config.json	E_i|Phase|mode|phase|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-02/source_inventory.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-03/cycle_semantics_hardening_config.json	Phase|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04/causal_condition_registry.json	Phase|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04/controlled_causal_structure_config.json	E_i|Phase|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04A/independent_transition_reconstruction_config.json	E_i|Phase|frequency|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04A/reconstruction_rule_registry.json	E_i|Phase|phase|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04B/calibration_metric_registry.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04B/heuristic_calibration_config.json	Matrix|Phase|frequency|mode|phase|r_s	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04C/fine_calibration_metric_registry.json	lag	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CAUSALITY07-04C/fine_calibration_sweep_config.json	Phase|frequency|mode|p_i|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CORRCORE01/correlation_core_claim_boundary_registry.json	Matrix|lag|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CORRCORE01/correlation_core_cross_strand_map.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CORRCORE01/correlation_core_equation_registry.json	Matrix|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CORRCORE01/correlation_core_object_registry.json	E_i|Matrix|Phase|lag|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CORRCORE01/correlation_core_quantity_registry.json	Matrix|Phase|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-CORRCORE01/correlation_core_source_inventory.json	E_i|Matrix|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-DB/schema/qsb_research_db_schema.sql	E_i|lag|mode|p_i	sql
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-01/repository_metadata_inventory_config.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-02/canonical_metadata_contract_config.json	E_i|Matrix|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-02/canonical_metadata_schema.sql	E_i|mode	sql
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-02/controlled_vocabularies.json	lag|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-02/example_metadata_records.json	E_i|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-02/unit_dimension_registry.json	E_i|Phase|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-03/causality07_metadata_mapping.json	E_i|Phase|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META01-03/causality07_pilot_metadata_config.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META02/cross_mart_key_mapping_schema.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META02/cross_mart_seed_mappings.json	E_i|E_j|Matrix|Phase|mode|p_i|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META02/cross_mart_semantic_relation_registry.json	E_i|Phase|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-META02/cross_mart_transformation_rule_registry.json	E_i|Matrix|Phase|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql	E_i|E_j|Phase|mode|pair_id|phase|r_s	sql
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-OUTREACH01A/002_qsb_outreach01a_sqlite_views.sql	E_i|E_j|Paar|Phase|mode|phase|r_s	sql
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-OUTREACH01A/canonical_schema.json	E_i|E_j|Phase|mode|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-OUTREACH01A/field_aliases.csv	E_i|E_j|Phase|phase|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-OUTREACH01A/synthetic_demonstrator_config.yaml	E_i|lag|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json	E_i|Phase|lag|p_i|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json	E_i|Phase|lag|p_i|phase	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/archival_cluster_inventory.csv	E_i|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/canonical_rerun_map.csv	E_i|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/preregistered_hypotheses.csv	E_i|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/provenance_status_table.csv	E_i|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/recovered_file_manifest.csv	E_i|Phase|mode|phase|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml	Phase|lag|mode|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml	E_i|lag|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml	lag|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/dwh14a_high_priority_manual_evidence.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_binary_ell1.py	Phase|frequency|lag|mode|phase	py
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_stand_alone_ELL1_model.py	Phase|mode|phase	py
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_timing_model.py	E_i|E_j|Matrix|Phase|frequency|lag|mode|omega|phase|phase_i|phase_j|r_s	py
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_pulsar_1_1_5_METADATA.txt	Phase|mode|phase	txt
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping_evidence.md	E_i|Phase|mode|omega|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping_manifest.csv	E_i|Phase|mode|phase	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_examples_ver1.pdf	E_i|lag	pdf
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_manual.pdf	E_i|lag|p_j	pdf
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo_reference_toa_format.txt	Phase|frequency|lag|phase	txt
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1_primary_evidence_manifest.csv	E_i|frequency|lag|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1_primary_field_definition.md	E_i|frequency|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/public_source_download_manifest_template.yaml	E_i|lag|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/j0740_6620_quarantine_download_manifest_2026_05_29.yaml	lag	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim	mode	tim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par	mode	par
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_claim_true.yaml	E_i|lag	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_download_open.yaml	E_i|lag	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/QSB-ST-SHAPIROINFO/toy_comparator_config.yaml	Phase|frequency|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/README_BMC07_inputs.md	E_i|Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/README_BMC07_inputs_minimal_bundle.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc01/bmc01_baseline_relational_table_template.csv	pair_id	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc04/bmc04_baseline_relational_table_template.csv	pair_id	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc07_config_coupling_arm.yaml	Matrix|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc07_config_minimal_readouts.yaml	Matrix|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc07c_backbone_variation_config.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08_dataset_manifest.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08_dataset_manifest.template.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08_realdata_config.template.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08_realdata_config.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08a_m39x1_featuretable_config.template.yaml	Phase|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08a_m39x1_featuretable_config.yaml	Phase|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08a_real_units_feature_table.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08a_real_units_feature_table.template.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08b_m39x1_no_ring_mirror_config.yaml	Phase|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08b_real_units_feature_table.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08b_realdata_config.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08c_m39x1_sign_sensitive_ring_config.yaml	Phase|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08c_real_units_feature_table.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc08c_realdata_config.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09a_knn_inputs/k_2/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09a_knn_inputs/k_3/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09a_knn_inputs/k_4/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09a_realdata_config.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09b_runner_config_k_2.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09b_runner_config_k_3.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09b_runner_config_k_4.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09c_mutual_knn_inputs/k_2/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09c_mutual_knn_inputs/k_3/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09c_mutual_knn_inputs/k_4/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09c_runner_config_k_2.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09c_runner_config_k_3.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09c_runner_config_k_4.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_runner_config_hybrid_k3_tau_025.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_runner_config_hybrid_k3_tau_03.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_runner_config_threshold_tau_025.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_runner_config_threshold_tau_03.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_runner_config_threshold_tau_035.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_threshold_hybrid_compare_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_threshold_hybrid_inputs/graph_build_diagnostics.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_threshold_hybrid_inputs/hybrid_k3_tau_025/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_threshold_hybrid_inputs/hybrid_k3_tau_03/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_threshold_hybrid_inputs/threshold_tau_025/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_threshold_hybrid_inputs/threshold_tau_03/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc09d_threshold_hybrid_inputs/threshold_tau_035/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_compare_config.yaml	E_i|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_config.yaml	mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/graph_build_diagnostics.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/nullmodel_feature_table.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/nullmodel_feature_table.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/nullmodel_feature_table.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_032/baseline_relational_table_real.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_032/graph_build_summary.json	mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_032/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_101_threshold_tau_028.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_101_threshold_tau_03.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_101_threshold_tau_032.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_202_threshold_tau_028.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_202_threshold_tau_03.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_202_threshold_tau_032.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_303_threshold_tau_028.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_303_threshold_tau_03.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc10_runner_config_seed_303_threshold_tau_032.yaml	Matrix|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_baseline_relational_table_seed_101.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_baseline_relational_table_seed_202.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_baseline_relational_table_seed_303.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_cov_null_feature_table.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_cov_nullmodel_compare_config.yaml	E_i|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_cov_nullmodel_config.yaml	mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_node_metadata_seed_101.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_node_metadata_seed_202.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_node_metadata_seed_303.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_101_threshold_tau_028.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_101_threshold_tau_03.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_101_threshold_tau_032.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_202_threshold_tau_028.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_202_threshold_tau_03.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_202_threshold_tau_032.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_303_threshold_tau_028.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_303_threshold_tau_03.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc11_runner_config_seed_303_threshold_tau_032.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12_feature_leaveoneout_config.yaml	E_i|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12_feature_table_with_derived.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12_feature_table_with_derived_from_bmc08c.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12b_matched_leaveoneout_config.yaml	E_i|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_configs/baseline_all_features_fixed_tau.yaml	E_i|Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_configs/matched_drop_feature_length_scale.yaml	E_i|Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_configs/matched_drop_feature_mode_frequency.yaml	E_i|Matrix|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_configs/matched_drop_feature_shape_factor.yaml	E_i|Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_configs/matched_drop_feature_spectral_index.yaml	E_i|Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/baseline_all_features_fixed_tau/baseline_relational_table_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/baseline_all_features_fixed_tau/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_length_scale/baseline_relational_table_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_length_scale/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_mode_frequency/baseline_relational_table_real.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_mode_frequency/node_metadata_real.csv	E_i|frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_shape_factor/baseline_relational_table_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_shape_factor/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_spectral_index/baseline_relational_table_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_inputs/matched_drop_feature_spectral_index/node_metadata_real.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12c_backbone_aware_matched_loo_config.yaml	E_i|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_neighborhood_sweep_config.yaml	E_i|frequency|mode|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_70/baseline_all_features.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_70/drop_feature_length_scale.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_70/drop_feature_mode_frequency.yaml	Matrix|frequency|mode|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_70/drop_feature_shape_factor.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_70/drop_feature_spectral_index.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_75/baseline_all_features.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_75/drop_feature_length_scale.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_75/drop_feature_mode_frequency.yaml	Matrix|frequency|mode|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_75/drop_feature_shape_factor.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_75/drop_feature_spectral_index.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_81/baseline_all_features.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_81/drop_feature_length_scale.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_81/drop_feature_mode_frequency.yaml	Matrix|frequency|mode|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_81/drop_feature_shape_factor.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_81/drop_feature_spectral_index.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_87/baseline_all_features.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_87/drop_feature_length_scale.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_87/drop_feature_mode_frequency.yaml	Matrix|frequency|mode|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_87/drop_feature_shape_factor.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_87/drop_feature_spectral_index.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_92/baseline_all_features.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_92/drop_feature_length_scale.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_92/drop_feature_mode_frequency.yaml	Matrix|frequency|mode|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_92/drop_feature_shape_factor.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/N_92/drop_feature_spectral_index.yaml	Matrix|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/backbone_variant_summary.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/readout.md	frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/repeat_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/run_metadata.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/strength_topalpha_025/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/strength_topalpha_025/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/strength_topalpha_050/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/strength_topalpha_050/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/strength_topk_6/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/strength_topk_6/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_70/drop_feature_mode_frequency/validation.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/backbone_variant_summary.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/readout.md	frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/repeat_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/run_metadata.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/strength_topalpha_025/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/strength_topalpha_025/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/strength_topalpha_050/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/strength_topalpha_050/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/strength_topk_6/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/strength_topk_6/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_75/drop_feature_mode_frequency/validation.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/backbone_variant_summary.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/readout.md	frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/repeat_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/run_metadata.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/strength_topalpha_025/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/strength_topalpha_025/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/strength_topalpha_050/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/strength_topalpha_050/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/strength_topk_6/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/strength_topk_6/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_81/drop_feature_mode_frequency/validation.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/backbone_variant_summary.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/readout.md	frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/repeat_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/run_metadata.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/strength_topalpha_025/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/strength_topalpha_025/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/strength_topalpha_050/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/strength_topalpha_050/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/strength_topk_6/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/strength_topk_6/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_87/drop_feature_mode_frequency/validation.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/backbone_variant_summary.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/readout.md	frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/repeat_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/run_metadata.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/strength_topalpha_025/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/strength_topalpha_025/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/strength_topalpha_050/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/strength_topalpha_050/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/strength_topk_6/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/strength_topk_6/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_92/drop_feature_mode_frequency/validation.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/baseline_all_features/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/baseline_all_features/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_length_scale/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_length_scale/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_mode_frequency/baseline_relational_table_real.csv	frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_mode_frequency/node_metadata_real.csv	E_i|frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_shape_factor/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_shape_factor/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_spectral_index/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_70/drop_feature_spectral_index/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/baseline_all_features/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/baseline_all_features/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_length_scale/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_length_scale/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_mode_frequency/baseline_relational_table_real.csv	frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_mode_frequency/node_metadata_real.csv	E_i|frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_shape_factor/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_shape_factor/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_spectral_index/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_75/drop_feature_spectral_index/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/baseline_all_features/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/baseline_all_features/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_length_scale/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_length_scale/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_mode_frequency/baseline_relational_table_real.csv	frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_mode_frequency/node_metadata_real.csv	E_i|frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_shape_factor/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_shape_factor/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_spectral_index/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_81/drop_feature_spectral_index/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/baseline_all_features/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/baseline_all_features/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_length_scale/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_length_scale/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_mode_frequency/baseline_relational_table_real.csv	frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_mode_frequency/node_metadata_real.csv	E_i|frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_shape_factor/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_shape_factor/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_spectral_index/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_87/drop_feature_spectral_index/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/baseline_all_features/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/baseline_all_features/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_length_scale/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_length_scale/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_mode_frequency/baseline_relational_table_real.csv	frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_mode_frequency/node_metadata_real.csv	E_i|frequency|mode|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_shape_factor/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_shape_factor/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_spectral_index/baseline_relational_table_real.csv	p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12e_edgecount_sweep_inputs/N_92/drop_feature_spectral_index/node_metadata_real.csv	E_i|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc12f_decision_threshold_gap_sweep_config.yaml	frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc13_alternative_backbone_consensus_config.yaml	E_i|mode|p_j	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc14_null_model_feature_control_config.yaml	E_i|E_j|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc14d_covariance_structured_null_controls_config.yaml	E_i|E_j|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc14e_degree_copula_structured_nulls_config.yaml	E_i|E_j|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15_geometry_proxy_diagnostics_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15b_geometry_proxy_null_comparison_config.yaml	E_i|frequency|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15e_geometry_control_nulls_config.yaml	mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15f1_node_aligned_envelope_sensitivity_config.yaml	Matrix|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15f2_connectedness_transition_sweep_config.yaml	Matrix|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15f_envelope_construction_sensitivity_config.yaml	Matrix|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15g_core_perturbation_robustness_config.yaml	mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bmc15h_structured_specificity_extension_config.yaml	E_i|E_j|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu01_c60_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu01_c60_faces.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu01_c60_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu01_c60_structure_config.yaml	E_i|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu01b_c60_core_selection_config.yaml	mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu01c_c60_motif_topology_config.yaml	E_i|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02b_carrier_sharpness_config.yaml	Matrix|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02c_representation_resolved_config.yaml	Matrix	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02d1_face_parser_repair_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02d_carrier_role_geometry_config.yaml	E_i|E_j	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02e1_role_balance_localization_config.yaml	E_j	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02f1_face_id_interval_repair_config.yaml	E_i|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02f_carrier_role_visualization_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1_structure_inventory_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_armchair_repaired_cells.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_armchair_repaired_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_armchair_repaired_manifest.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_armchair_repaired_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_topology_repair_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_topology_repair_config_resolved.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_topology_repair_inventory.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_topology_repair_manifest.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_zigzag_repaired_cells.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_zigzag_repaired_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_zigzag_repaired_manifest.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g1b_nanotube_zigzag_repaired_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g2_carrier_diagnostic_transfer_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g3_real_structure_memory_null_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4_symmetry_orbit_inspection_config.yaml	E_i|E_j|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4b_exhaustive_connected_patch_signature_config.yaml	E_i|E_j|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_full_raw_order_replay_certification_preflight_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_full_raw_order_replay_stage1_disabled_run_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_full_raw_order_replay_stage2_candidate_008_disabled_smoke_config.yaml	E_i|K_candidate|lag|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_full_raw_order_replay_stage3_disabled_full_replay_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26179015_26180015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26179015_26189015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26179015_26279015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26180015_26181015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26181015_26182015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26182015_26183015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26183015_26184015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26184015_26185015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26185015_26186015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26186015_26187015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187015_26187115.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187015_26188015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187115_26187125.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187115_26187215.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187125_26187135.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187135_26187145.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187145_26187155.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187155_26187165.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187165_26187175.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187175_26187176.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187175_26187185.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187176_26187177.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187177_26187178.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187178_26187179.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187179_26187180.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187180_26187181.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187181_26187182.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187182_26187183.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187183_26187184.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187184_26187185.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187185_26187195.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187195_26187205.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187205_26187215.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187215_26187315.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187315_26187415.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187415_26187515.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187515_26187615.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187615_26187715.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187715_26187815.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187815_26187915.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26187915_26188015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26188015_26189015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26189015_26199015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26199015_26209015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26209015_26219015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26219015_26229015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26229015_26239015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26239015_26249015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26249015_26259015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26259015_26269015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_inspect_window_26269015_26279015.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g4c_orbit_reduced_resumable_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5_role_assignment_sensitivity_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5b_first500_enumeration_smoke_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5b_window_around_exact_patch_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5d_automorphy_only_role_transport_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5e1_near_match_localization_config.yaml	E_i|mode|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5e2_near_match_decoy_classification_config.yaml	E_i|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5f_raw_order_replay_certification_config.yaml	E_i|p_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5g2_narrow_per_index_replay_photo_certification_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g5g_fu02g4c_raw_order_replay_certification_config.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_c60_reference_cells.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_c60_reference_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_c60_reference_manifest.json	E_i|lag	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_c60_reference_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_graphene_patch_cells.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_graphene_patch_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_graphene_patch_manifest.json	E_i|lag	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_graphene_patch_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_armchair_cells.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_armchair_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_armchair_manifest.json	E_i|lag	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_armchair_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_zigzag_cells.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_zigzag_edges.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_zigzag_manifest.json	E_i|lag	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_nanotube_zigzag_nodes.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_structure_inventory.csv	E_i|lag	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_structure_inventory_config_resolved.yaml	E_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_structure_inventory_manifest.json	E_i|lag	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_fu02g_structure_inventory_warnings.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_is01_isotope_structure_config.yaml	E_i|Phase|energy|mode|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_is01b_family_balanced_config.yaml	E_i|Phase|energy|mode|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/bms_st01_structure_information_config.yaml	E_i|mode	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/fu02g4c_stage3_execution_config.json	E_i	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/node_metadata.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/node_metadata_real.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/node_metadata_real_bmc08b.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/node_metadata_real_bmc08c.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_num_04a_phase_sensitive_toy_config.yaml	Phase|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_num_05a_geometric_validation_config.yaml	E_j|Matrix|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_num_05b_phase_gauge_flux_config.yaml	Matrix|Phase|frequency|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_num_05c_perturbation_noise_boundary_config.yaml	Phase|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01a_existing_result_index.csv	E_i|frequency|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01a_marker_axis_map.csv	E_i|lag|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01b_cross_test_pattern_matrix.csv	E_i|Matrix|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01c_evidence_binding_table.csv	E_i|lag|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01d_c60_candidate_gate_table.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01d_null_family_normalization_table.csv	E_i|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01d_proxy_marker_source_binding.csv	mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01d_replay_certification_ladder.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01e_readout_claim_map.csv	E_i|Kandidat|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01f_documentation_synthesis_map.csv	E_i|Matrix|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01g_visual_map_edges.csv	E_i|Matrix	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_01g_visual_map_nodes.csv	E_i|Matrix	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_02a_result_summary_claims.csv	E_i|Matrix|p_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_02e_math_bridge_concept_map.csv	E_i|Phase|mode|phase|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_03a_bmc12_per_variant_binding.csv	E_i|Phase|frequency|mode|phase	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_bridge_synth_03b_geometry_proxy_component_binding.csv	E_i|E_j|mode|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01_wifm01_minimal_metric_config.yaml	E_i|Phase|delta_p|mode|pair_id|phase|phase_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep_config.yaml	E_i|Phase|delta_p|mode|phase|phase_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01_wifm01c_adversarial_ambiguity_stress_config.yaml	E_i|Phase|delta_p|mode|pair_id|phase|phase_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1b_wave_identity_residual_minimal_config.yaml	E_i|E_j|Phase|mode|pair_id|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1c_wave_identity_residual_control_stress_config.yaml	E_i|E_j|Phase|mode|pair_id|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1d_wave_identity_manifold_degeneracy_audit_config.yaml	E_i|E_j|Phase|mode|pair_id|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1e_collision_aware_wave_identity_profile_config.yaml	E_i|E_j|Phase|mode|pair_id|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1f_collision_aware_profile_robustness_sweep_config.yaml	E_i|Phase|mode|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1g_warning_driver_decomposition_config.yaml	E_i|Phase|lag|mode|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1h_cyclic_coordinate_acceptance_region_config.yaml	E_i|Phase|mode|phase|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1i_cyclic_phase_source_validation_overstrictness_config.yaml	E_i|Phase|mode|phase	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1j_explicit_phase_field_exposure_cyclic_recheck_config.yaml	E_i|E_j|Phase|delta_p|delta_phi|phase|phase_i|phase_j	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1k_deterministic_synthetic_phase_field_exposure_config.yaml	E_i|Phase|mode|phase|phase_i|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1l_synthetic_phase_leakage_tautology_audit_config.yaml	E_i|E_j|Phase|mode|phase|phase_i|phase_j	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1m_multi_channel_synthetic_phase_identity_profile_config.yaml	E_i|Phase|mode|phase|phase_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1n_d1m_output_audit_and_runner_refinement_config.yaml	E_i|Phase|mode|phase|phase_i|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1o_d1m_refined_multi_channel_profile_config.yaml	E_i|Phase|mode|phase|phase_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_comp01d1p_d1o_refined_output_audit_regression_config.yaml	E_i|Phase|lag|mode|phase|phase_i	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml	E_i|Matrix|Phase|mode|p_i|phase|phase_i|phase_response|r_s	yaml
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/backbone_variant_summary.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/readout.md	frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/repeat_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/run_metadata.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/strength_topalpha_025/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/strength_topalpha_025/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/strength_topalpha_050/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/strength_topalpha_050/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/strength_topk_6/arm_metrics.csv	frequency|mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/strength_topk_6/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/summary.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	data/runs/BMC-12c/backbone_aware_matched_loo_open/matched_drop_feature_mode_frequency/validation.json	frequency|mode	json
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC07_block_restart_spec.md	Matrix|Modus	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC07b_coupling_arm_spec.md	lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC07c_backbone_variation_spec.md	Matrix|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC07d_backbone_variant_legitimation.md	Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC07d_backbone_variant_legitimation_matrix.csv	Matrix	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08_realdata_io_spec.md	E_i|Matrix|Paar|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08_realdata_mapping_note.md	E_i|Frequenz|Kandidat|Matrix|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08_realdata_transfer_spec.md	E_i|Matrix|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08a_build_script_note.md	E_i|Paar|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08a_family_specific_L_major_L_minor_m_ref.md	E_i|Frequenz|Modenindex|Phase|frequency|mode|mode_index|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08a_feature_shape_and_spectral_definitions.md	E_i|Frequenz|Modenindex|frequency|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08a_m39x1_featuretable_script_note.md	E_i|Energie|Phase|frequency|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08a_ring_cavity_membrane_mapping_spec.md	E_i|Energie|Frequenz|Kandidat|Paar|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08a_small_open_feature_list.md	E_i|Energie|Frequenz|Modenindex|frequency|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08b_ring_symmetry_removed_note.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC08c_sign_sensitive_ring_spec.md	frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC09a_knn_graph_on_BMC08c_spec.md	Paar|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC09d_threshold_hybrid_local_graph_spec.md	Kandidat|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC10_nullmodel_run_note.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC11_note.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12B_MATCHED_LEAVEONEOUT_SPEC.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12C_BACKBONE_AWARE_MATCHED_LOO_SPEC.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12D_RED_TEAM_INTEGRATION_ADDENDUM_GROK.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12E_EDGECOUNT_NEIGHBORHOOD_RESULT_NOTE.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12E_EDGECOUNT_NEIGHBORHOOD_SWEEP_SPEC.md	E_i|frequency|mode|p_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12F_DECISION_THRESHOLD_GAP_SWEEP_RESULT_NOTE.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12F_DECISION_THRESHOLD_GAP_SWEEP_SPEC.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12_ABC_FEATURE_DOMINANCE_RESULT_NOTE.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC12_FEATURE_LEAVEONEOUT_SPEC.md	E_i|delta_E|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC13_ALTERNATIVE_BACKBONE_CONSENSUS_RESULT_NOTE.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC13_ALTERNATIVE_BACKBONE_CONSENSUS_SPEC.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14D_COVARIANCE_STRUCTURED_NULL_CONTROLS_RESULT_NOTE.md	E_i|Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14D_COVARIANCE_STRUCTURED_NULL_CONTROLS_SPEC.md	E_i|E_j|Matrix|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14E_DEGREE_COPULA_STRUCTURED_NULLS_RESULT_NOTE.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14E_DEGREE_COPULA_STRUCTURED_NULLS_SPEC.md	E_i|E_j|Matrix|frequency|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14_NULL_MODEL_FEATURE_CONTROL_RESULT_NOTE.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14_NULL_MODEL_FEATURE_CONTROL_SPEC.md	E_i|E_j|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14_RED_TEAM_INTEGRATION_NOTE.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC14_SERIES_CONSOLIDATED_ROBUSTNESS_NOTE.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15B_GEOMETRY_PROXY_NULL_COMPARISON_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15B_GEOMETRY_PROXY_NULL_COMPARISON_SPEC.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15B_READOUT_LABEL_REFINEMENT_PATCH_SPEC.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15D_GEOMETRY_PROXY_RED_TEAM_INTEGRATION_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15D_RED_TEAM_PROMPT_PACK.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15E2_NODE_ALIGNED_GEOMETRY_CONTROL_PREFLIGHT_SPEC.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15E_GEOMETRY_CONTROL_NULLS_HUMAN_READABLE_WITH_MATH.md	Matrix|Paar|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15E_GEOMETRY_CONTROL_NULLS_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15E_GEOMETRY_CONTROL_NULLS_SPEC.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15E_PREFLIGHT_GRAPH_OBJECT_EXPORT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15E_READOUT_LABEL_REFINEMENT_PATCH_SPEC.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15E_RUNNER_FIELD_LIST.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15F1_NODE_ALIGNED_ENVELOPE_SENSITIVITY_RESULT_NOTE.md	Kandidat|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15F2_CONNECTEDNESS_TRANSITION_SWEEP_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15F_ENVELOPE_CONSTRUCTION_SENSITIVITY_RESULT_NOTE.md	Kandidat|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15F_ENVELOPE_CONSTRUCTION_SENSITIVITY_SPEC.md	E_i|E_j|Matrix|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15F_RUNNER_FIELD_LIST.md	E_j|Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15G_CORE_PERTURBATION_ROBUSTNESS_RESULT_NOTE.md	E_j|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15G_CORE_PERTURBATION_ROBUSTNESS_SPEC.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15G_RUNNER_FIELD_LIST.md	E_i|E_j	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15H_CORE_SEEDED_DECOY_EXTENSION_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15H_FEATURE_STRUCTURED_RERUN_RESULT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15H_RUNNER_FIELD_LIST.md	E_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15H_STRUCTURED_SPECIFICITY_EXTENSION_SPEC.md	E_j|Phase|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15H_STRUCTURED_SPECIFICITY_INITIAL_RESULT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15_AI_EXTERNAL_REVIEW_PACKET.md	Kandidat|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15_GEOMETRY_PROXY_DIAGNOSTICS_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15_GEOMETRY_PROXY_DIAGNOSTICS_SPEC.md	E_i|Matrix|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15_SERIES_GEOMETRY_PROXY_CONSOLIDATED_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMC15_SERIES_GEOMETRY_PROXY_SYNTHESIS_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU01B_C60_CORE_SELECTION_INITIAL_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU01B_C60_CORE_SELECTION_SENSITIVITY_SPEC.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU01B_RUNNER_FIELD_LIST.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_EXTENSION_SPEC.md	E_i|Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU01C_RUNNER_FIELD_LIST.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU01_C60_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU01_RUNNER_FIELD_LIST.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02B_CARRIER_SHARPNESS_INITIAL_RESULT_NOTE.md	r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02B_CARRIER_SHARPNESS_RANK_STABILITY_SPEC.md	Matrix|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02B_RUNNER_FIELD_LIST.md	E_i|Matrix|mode|p_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02C_REPRESENTATION_RESOLVED_CARRIER_DELTA_INITIAL_RESULT_NOTE.md	Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02C_REPRESENTATION_RESOLVED_CARRIER_DELTA_SPEC.md	Matrix|delta_E	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02C_RUNNER_FIELD_LIST.md	delta_E	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02D1_FACE_PARSER_REPAIR_AND_FACE_LOCALIZATION_INITIAL_RESULT_NOTE.md	E_i|E_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02D1_FACE_PARSER_REPAIR_AND_FACE_LOCALIZATION_SPEC.md	E_i|E_j	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02D1_RUNNER_FIELD_LIST.md	E_i|E_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02D_CARRIER_ROLE_GEOMETRY_PATCH_DISTRIBUTION_INITIAL_RESULT_NOTE.md	E_j	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02D_CARRIER_ROLE_GEOMETRY_PATCH_DISTRIBUTION_SPEC.md	E_i|E_j|Matrix|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02D_RUNNER_FIELD_LIST.md	E_i|E_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02E1_ROLE_BALANCE_LOCALIZATION_SPEC.md	lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02E1_RUNNER_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02E_RUNNER_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02F1_FACE_ID_INTERVAL_REPAIR_3D_GRAPH_LAYOUT_INITIAL_RESULT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02F1_FACE_ID_INTERVAL_REPAIR_3D_GRAPH_LAYOUT_SPEC.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02F1_RUNNER_FIELD_LIST.md	E_i|E_j|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02F_CARRIER_ROLE_VISUALIZATION_SYMMETRY_ORBIT_INITIAL_RESULT_NOTE.md	E_i|E_j|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02F_CARRIER_ROLE_VISUALIZATION_SYMMETRY_ORBIT_SPEC.md	E_i|E_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02F_RUNNER_FIELD_LIST.md	E_i|E_j	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G0_REAL_STRUCTURE_MEMORY_SYMMETRY_CONTROL_METHOD_PLAN.md	E_i|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G1B_NANOTUBE_TOPOLOGY_REPAIR_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G1B_NANOTUBE_TOPOLOGY_REPAIR_VALIDATION_INITIAL_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G1B_NANOTUBE_TOPOLOGY_REPAIR_VALIDATION_SPEC.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_FIELD_LIST.md	E_i|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_INITIAL_RESULT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_SPEC.md	E_i|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_FIELD_LIST.md	E_i|lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_GEOMETRY_CONTROLS_SPEC.md	E_i|lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_FIELD_LIST.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_INITIAL_RESULT_NOTE.md	mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_SPEC.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_FIELD_LIST.md	E_i|E_j|frequency|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_INITIAL_BOUNDED_RESULT_NOTE.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_SPEC.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_CHUNK_0000000_0999999_RESULT_NOTE.md	r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_CHUNK_1000000_1999999_ORBIT_REDUCED_RESULT_NOTE.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_CHUNK_2000000_2999999_ORBIT_REDUCED_RESULT_NOTE.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_CANDIDATE_008_ONLY_SMOKE_WRAPPER_SPEC.md	E_i|K_candidate|Kandidat|Modus|lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_CERTIFICATION_PREFLIGHT_FIELD_LIST.md	E_i|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_DRY_RUN_PLAN.md	E_i|Kandidat|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE0_INPUT_PATH_VALIDATION_RESULT_NOTE.md	Kandidat|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE1_DISABLED_RUN_CONFIG_RESULT_NOTE.md	Kandidat|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE2_BLOCKED_RESULT_NOTE.md	E_i|K_candidate|Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE2_BOUNDED_SMOKE_CHECK_PLAN.md	E_i|K_candidate|Kandidat|Modus|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE2_CANDIDATE_008_DISABLED_SMOKE_CONFIG_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE2_CANDIDATE_008_REFERENCE_SMOKE_PASS_RESULT_NOTE.md	E_i|E_j|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE2_COMMAND_GATE_PLAN.md	E_i|K_candidate|Kandidat|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE2_DRY_RUN_GATE_BLOCKED_RESULT_NOTE.md	K_candidate	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE2_DRY_RUN_GATE_READY_RESULT_NOTE.md	E_i|Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE3_COMMAND_GATE_PLAN.md	E_i|Kandidat|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE3_EXECUTION_GATE_PLAN.md	Kandidat|Modus|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE3_GATE_STATUS_HANDOFF_2026-05-09.md	Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE3_NEGATIVE_EXECUTION_GATE_BLOCKED_RESULT_NOTE.md	lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE3_WRAPPER_DRY_RUN_READY_RESULT_NOTE.md	mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE3_WRAPPER_RUNNER_SPEC.md	E_i|Kandidat|Modus|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_FULL_RAW_ORDER_REPLAY_STAGE3_WRAPPER_SCAFFOLD_RESULT_NOTE.md	Kandidat|lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_ORBIT_REDUCED_RESUMABLE_CONNECTED_PATCH_ENUMERATION_FIELD_LIST.md	E_i|frequency|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_ORBIT_REDUCED_RESUMABLE_CONNECTED_PATCH_ENUMERATION_SPEC.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4C_STAGE3A_WRAPPER_SCAFFOLD_AUDIT_RESULT_NOTE.md	Kandidat|Modus|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4D_COVERAGE_AND_LOG_AUDIT_SPEC.md	E_i|lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_C60_REFERENCE_SPEC.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_COMPLETE_RESULT_NOTE.md	mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_FIELD_LIST.md	E_i|E_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_INITIAL_RESULT_NOTE.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5C_ROLE_TRANSPORT_RULE_SPEC.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5D_AUTOMORPHY_ONLY_ROLE_TRANSPORT_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5D_AUTOMORPHY_ONLY_ROLE_TRANSPORT_RESULT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5E1_NEAR_MATCH_LOCALIZATION_FIELD_LIST.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5E2_NEAR_MATCH_DECOY_CLASSIFICATION_FIELD_LIST.md	E_i|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5E2_RED_TEAM_PACKET.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5E3_RED_TEAM_SYNTHESIS_AND_NEXT_CONTROLS.md	E_i|lag|p_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5F_RAW_ORDER_REPLAY_CERTIFICATION_FIELD_LIST.md	E_i|lag|p_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5G2_NARROW_PER_INDEX_REPLAY_PHOTO_CERTIFICATION_FIELD_LIST.md	E_i|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5G2_TO_FU02G4C_FULL_REPLAY_HANDOFF_2026-05-09.md	Kandidat|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5G_FU02G4C_RAW_ORDER_REPLAY_CERTIFICATION_FIELD_LIST.md	E_i|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5G_RAW_ORDER_REPLAY_CERTIFICATION_RESULT_NOTE.md	E_i|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5_ROLE_ASSIGNMENT_SENSITIVITY_FIELD_LIST.md	E_i|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02G5_ROLE_ASSIGNMENT_SENSITIVITY_SPEC.md	r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02_LOAD_BEARING_PATTERN_ANALYSIS_SPEC.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02_LOAD_BEARING_PATTERN_INITIAL_RESULT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_FU02_RUNNER_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_IE01_ISOELECTRONIC_MATTER_INFORMATION_TEST_SPEC.md	E_i|E_j|Matrix|energy|frequency|lag|mode|omega	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_IS01B_FAMILY_BALANCED_EXTENSION_SPEC.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_IS01B_FAMILY_BALANCED_RESULT_NOTE.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_IS01B_RUNNER_FIELD_LIST.md	E_i|energy|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_IS01_ISOTOPE_STRUCTURE_BMC15H_METHOD_PLAN.md	E_i|energy|frequency|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_IS01_ISOTOPE_STRUCTURE_INITIAL_RESULT_NOTE.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_IS01_RUNNER_FIELD_LIST.md	E_i|energy|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_ST01_RUNNER_FIELD_LIST.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_ST01_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/BMS_ST01_STRUCTURE_INFORMATION_INITIAL_RESULT_NOTE.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/DR01_LITERATURE_METHOD_POSITIONING_NOTE.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/GROK_PROJECT_RESET_BMC12_REVIEW_PROMPT.md	E_i|frequency|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_01_AG_GUREVICH_FIT_CONTACT_GOAL_AND_EVIDENCE_BOUNDARY.md	E_i|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_02_AG_GUREVICH_SINGLE_DEMONSTRATOR_SELECTION.md	E_i|Kandidat|Matrix|Phase|lag|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_03_MINIMAL_SYNTHETIC_DTC_STATE_IDENTITY_DEMONSTRATOR_SPEC.md	E_i|Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_04_MULTILINGUAL_PRESENTATION_VIEWS_AND_TWO_PAGE_TECHNICAL_NOTE_SPEC.md	E_i|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_EN.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_ES.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_05_CONTACT_PACKAGE_README.md	E_i|Phase|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_05_VISIBLE_CONTACT_FIGURE_AND_PACKAGE_ASSEMBLY_SPEC.md	E_i|Phase|lag|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_06_COMPETENCE_AND_BOUNDARIES_PROFILE_EN.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_06_CONTACT_LETTER_AND_RESEARCH_CONTEXT_SPEC.md	Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_06_CONTACT_LETTER_DRAFT_EN.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_06_RESEARCH_CONTEXT_NOTE_EN.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/OUTREACH01A_07_FINAL_PRESEND_CORRECTION_AND_FLAT_PACKAGE_SPEC.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/PROJEKTSTAND_QSB_BMC12_TIMELINE_MENSCHLICH.md	Kandidat|Phase|frequency|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY01/QSB_CAUSALITY01_DEFINITION_CATALOG.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY01/QSB_CAUSALITY01_DIRECTION_MECHANISM_MATRIX.csv	Matrix	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY01/QSB_CAUSALITY01_FINAL_STATUS.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY01/QSB_CAUSALITY01_PARTIAL_ORDER_REQUIREMENTS.csv	mode	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY01/QSB_CAUSALITY01_TAU_STATUS_MATRIX.csv	Matrix	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_ADMISSIBILITY_CANDIDATES.csv	E_i|Paar	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_CLAIM_BOUNDARY.md	Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_CONCEPT_NOTE.md	Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_DISTANCE_PROPERTY_MATRIX.csv	Matrix	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_FINAL_STATUS.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_MONOTONICITY_ASSESSMENT.csv	E_i|Paar	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_NEIGHBORHOOD_ANALYSIS.csv	r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_ORDER_MEASURE_CANDIDATES.csv	E_i|Paar	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02A/QSB_CAUSALITY02A_TAU_DISTANCE_ROLE.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_ACYCLICITY_ARGUMENT.md	Kandidat|omega	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_ADMISSIBILITY_RULES.csv	E_i	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_CLAIM_BOUNDARY.md	Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_CONCEPT_NOTE.md	Kandidat|omega	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_CONTINUATION_SPACE_ANALYSIS.csv	omega	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_EQUIVALENCE_ASSESSMENT.csv	omega|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_FINAL_STATUS.csv	E_i|r_s	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB-CAUSALITY02B/QSB_CAUSALITY02B_FIXATION_DEFINITIONS.csv	omega	csv
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ABSCHLUSSBERICHT_2026-05-09_FU02G5G2.md	E_i|Kandidat|Modus|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_APERIODIC_NONLATTICE_CONTEXT_NOTE.md	lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BMS_FU03_RED_TEAM_PROMPT_2026-05-04.md	E_i|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BMS_IS_IE_ST_FU_Interne_Gesamtnotiz_2026-05-01.pdf	lag|mode	pdf
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_01_PREFLIGHT_PLAN.md	E_i|Matrix|Phase|frequency|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_01_RESULT_DISCUSSION.md	Matrix|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_01_RESULT_NOTE.md	Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02A_RESULT_DISCUSSION.md	Matrix|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02A_TESTDATA_SCAFFOLD_PLAN.md	E_i|Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02B_CARBON_BONDING_ORGANIZATION_PLAN.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02B_RESULT_DISCUSSION.md	Matrix|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02C_CONTROL_ENSEMBLES_PLAN.md	E_i|lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02C_RESULT_DISCUSSION.md	Matrix|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02C_RESULT_NOTE.md	lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02D_DIAGNOSTIC_SEPARATION_PLAN.md	Matrix|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02D_PROGRAMMABLAUFPLAN.md	Paar|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02D_RESULT_DISCUSSION.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02E_CONTROL_MIMICRY_DIAGNOSTIC_REVISION_PLAN.md	E_i|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_DATA_02E_RESULT_DISCUSSION.md	mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NEXT_AFTER_RED_TEAM_2026_05_12.md	E_i|Matrix|Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_04A_PHASE_SENSITIVE_TOY_SPEC.md	E_i|E_j|Matrix|Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_04A_RESULT_NOTE.md	E_i|E_j|Matrix|Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05A_GEOMETRIC_VALIDATION_HOSTILE_CONTROLS_SPEC.md	E_i|Matrix|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05A_RESULT_DISCUSSION.md	Matrix|Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05A_RESULT_NOTE.md	Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05B_PHASE_GAUGE_FLUX_STRESS_TEST_SPEC.md	E_i|Matrix|Phase|frequency|phase|spectral_gap	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05B_RESULT_DISCUSSION.md	E_i|Matrix|Phase|energy|frequency|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05B_RESULT_NOTE.md	E_i|Matrix|Phase|frequency|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05C_PERTURBATION_NOISE_BOUNDARY_MAP_SPEC.md	Phase|phase|r_s|spectral_gap	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05C_RESULT_DISCUSSION.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_NUM_05C_RESULT_NOTE.md	Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01A_MARKER_AXIS_MAP_FIELD_LIST.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01A_RESULT_NOTE.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01B_CROSS_TEST_PATTERN_MATRIX_FIELD_LIST.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01B_RESULT_NOTE.md	E_i|Kandidat|Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01C_RESULT_NOTE.md	E_i|Kandidat|Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01D_C60_CANDIDATE_GATE_TABLE_FIELD_LIST.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01D_PROXY_MARKER_SOURCE_BINDING_FIELD_LIST.md	mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01D_REPLAY_CERTIFICATION_LADDER_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01D_RESULT_NOTE.md	Kandidat|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01E_CONSERVATIVE_CROSS_TEST_READOUT.md	Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01E_READOUT_CLAIM_MAP_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01E_RESULT_NOTE.md	Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01F_DOCUMENTATION_READY_SYNTHESIS_MAP.md	Matrix|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01G_VISUAL_DOCUMENTATION_MAP.md	Matrix	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01G_VISUAL_MAP_EDGES_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_01G_VISUAL_MAP_NODES_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_02A_RESULT_NOTE.md	p_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_02A_RESULT_SUMMARY_CLAIMS_FIELD_LIST.md	E_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_02B_RESULT_NOTE.md	lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_02C_PUBLIC_CAUTIOUS_SUMMARY.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_02E_HUMAN_READABLE_MATHEMATICAL_BRIDGE_NOTE.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_02E_MATH_BRIDGE_CONCEPT_MAP_FIELD_LIST.md	E_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_02E_RESULT_NOTE.md	Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_BRIDGE_SYNTH_03B_GEOMETRY_PROXY_COMPONENT_BINDING_FIELD_LIST.md	r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY06B_01_EVIDENCE_GATED_INNER_SPHERE_ET_STATE_SPEC.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY06B_02_INNER_SPHERE_ET_CANDIDATE_STATE_RECORD_SCHEMA_SPEC.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY06B_03_INNER_SPHERE_ET_TRANSITION_ADMISSIBILITY_SPEC.md	E_i|Matrix|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY06B_04_FIRST_INNER_SPHERE_ET_DATA_AND_ADMISSIBILITY_RUNNER_SPEC.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY06B_05_ADMISSIBILITY_ROBUSTNESS_AND_NEGATIVE_CONTROL_RUNNER_SPEC.md	r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY06B_06_SECOND_INDEPENDENT_INNER_SPHERE_ET_CASE_RUNNER_SPEC.md	lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_01_OSCILLATORY_REACTION_STATE_CYCLE_CASE_DEFINITION.md	E_i|Phase|energy|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_02_FIRST_OSCILLATORY_STATE_CYCLE_DATA_AND_RUNNER_SPEC.md	E_i|Phase|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_03_CYCLE_SEMANTICS_HARDENING_NEGATIVE_CONTROLS_SPEC.md	E_i|Phase|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_03_FINAL_RESULT_NOTE.md	E_i|Phase|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04A_FINAL_RESULT_NOTE.md	Phase|frequency|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04A_INDEPENDENT_TRANSITION_PREDECESSOR_RECONSTRUCTION_SPEC.md	Phase|frequency|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04B_FINAL_RESULT_NOTE.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04B_HEURISTIC_CALIBRATION_CURVE_SENSITIVITY_SWEEP_SPEC.md	Matrix|Phase|frequency|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04C_FINAL_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04C_FINE_CALIBRATION_SWEEP_SPEC.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04_FINAL_RESULT_NOTE.md	Matrix|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CAUSALITY07_04_MINIMAL_CONDITIONS_CONTROLLED_CAUSAL_STRUCTURE_SPEC.md	Matrix|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CHAT_UMZUG_BMC15B_STATUS.md	Modus|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CHAT_UMZUG_BMS_FU02G4C_2026-05-03.md	E_i|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CHAT_UMZUG_BMS_FU02G4C_TO_G5_2026-05-06.md	Kandidat|Modus|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CODEX_AUFTRAG_FU02G4C_STAGE3_EXECUTION_PATH_IMPLEMENTATION_2026-05-10.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CODEX_KURZE_LEINE_RULES_2026-05-09.md	lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CORRCORE01_CORRELATION_MATRIX_CORE_DWH_INTEGRATION_SPEC.md	Matrix|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_CORRCORE01_FINAL_RESULT_NOTE.md	Matrix|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB01_RESEARCH_DATABASE_REPO_LINEAGE_SCHEMA_PLAN.md	E_i|lag|mode|p_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB02_SQLITE_SCHEMA_SPEC.md	E_i|lag|mode|p_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB04_SQLITE_EMPTY_DATABASE_CREATION_PLAN.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB07_SQLITE_SCHEMA_INSPECTION_RESULT_NOTE.md	lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB08_SQLITE_DB_BROWSER_INSPECTION_PLAN.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB09_SQLITE_DB_BROWSER_INSPECTION_EXECUTION_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB10_METADATA_SEED_PLAN.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB11_METADATA_SEED_SPEC.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB14_METADATA_SEED_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB15_SYNTHETIC_SAMPLE_DATA_PLAN.md	E_i|Phase|lag|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB16_SYNTHETIC_SAMPLE_DATA_SPEC.md	E_i|lag|mode|p_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DB19_SYNTHETIC_SAMPLE_DATA_RESULT_NOTE.md	E_i|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DEBROGLIE_EXKURS_CHAT_TRANSCRIPT_2026-05-17.md	Energie|Frequenz|Impuls|Kandidat|Phase|Planck|lag|omega|p_i|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DEBROGLIE_RELATIVITY_BRIDGE_ANCHOR_NOTE_2026-05-17.md	Energie|Frequenz|Impuls|Phase|lag|lambda_C|omega|p_i|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_DEEP_RESEARCH_PROMPT_AFTER_04A_2026-05-12.md	E_i|Matrix|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_FU01_FU01b_FU01c_Interne_Ergebnisnotiz_2026-05-01.pdf	lag|mode	pdf
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_FU02G4C_RESULT_NOTE_AUTOMORPHIC_EXACT_MATCH_2026-05-06.md	r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_FU02G4C_STAGE3_EXECUTION_PATH_RESULT_NOTE_2026-05-10.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_FU02G4C_STAGE3_EXECUTION_PATH_SPEC_2026-05-10.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_FU02G4C_STAGE3_IMPLEMENTATION_SPEC_2026-05-10.md	E_i|Kandidat|Modus|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_LITERATURE_CONTEXT_APERIODIC_NONLATTICE_SPACETIME_DEEP_RESEARCH_2026-05-07.md	Frequenz|Modus|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_MASCHINENRAUM_WORKFLOW_ETHIK_PERSONALITY_2026-05-09.md	Kandidat|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_MASCHINENRAUM_WORKFLOW_FREEZE_2026-05-09.md	lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_META01_01_EXISTING_METADATA_LINEAGE_INVENTORY_AND_CANONICAL_CONTRACT_SPEC.md	E_i|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_META01_02_CANONICAL_METADATA_SCHEMA_IDENTIFIER_LINEAGE_AND_VALIDATION_CONTRACT_SPEC.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_META01_03_CAUSALITY07_PILOT_METADATA_GENERATOR_SPEC.md	Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_META01_03_FINAL_RESULT_NOTE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_META02_CROSS_MART_KEY_MAPPING_AND_TRANSFORMATION_REGISTRY_SPEC.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_NEW_CHAT_START_PROMPT_FU02G4C_2026-05-03.md	Modus|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_NEW_CHAT_START_PROMPT_FU02G5_2026-05-06.md	Kandidat	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_NOVA_CHARACTER_AND_WORKING_STYLE_2026-05-06.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_01_SCOPE_AND_CONTACT_STRATEGY_SPEC.md	Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_02_RESEARCH_GROUP_FIT_MAPPING.md	Matrix|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_03_RELATIONAL_STATE_IDENTITY_MATHEMATICAL_SPEC.md	E_i|E_j|Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_04_DWH_AND_MULTILINGUAL_VIEW_SPEC.md	E_i|E_j|lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_05_SYNTHETIC_DEMONSTRATOR_CASE_DEFINITION.md	E_i|Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_06_SYNTHETIC_DEMONSTRATOR_RESULT_NOTE.md	E_i|E_j|Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_06_SYNTHETIC_DEMONSTRATOR_RUNNER_SPEC.md	E_i|E_j|Phase|lag|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_09_CONTACT_GATE_CHECKLIST.md	lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_OUTREACH01A_SETUP_RESULT_NOTE.md	E_i|E_j|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_PROJECT_STATUS_FOR_HUMANS_BMC15B.md	lag|mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_PROJEKTSTAND_MIT_MATHE_LESBAR_2026-05-04.md	E_i|Kandidat|Modus|lag|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_PROJEKTZUSAMMENFASSUNG_2026-05-06_FU02G5B.md	Kandidat|Modus|lag|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_PROJEKTZUSAMMENFASSUNG_2026-05-07_FU02G5E1.md	E_i|Kandidat|Modus|Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_RED_TEAM_BRIEF_2026-05-12_AFTER_04A.md	E_i|Matrix|Phase|frequency|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_BRIDGE_NATURE_01A_RED_TEAM_PROMPT_PACK.md	E_i|Phase|Planck|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_BRIDGE_NATURE_01B_RED_TEAM_AND_CODEX_LITERATURE_SYNTHESIS_GATE.md	Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_BRIDGE_NATURE_WORKING_MODEL.md	Kandidat|Matrix|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01B_COMPONENT_RESOLVED_COMPATIBILITY_INSPECTION_PLAN.md	E_i|Phase|mode|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01B_COMPONENT_RESOLVED_COMPATIBILITY_RESULT_NOTE.md	Phase|mode|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md	E_i|Phase|frequency|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_HARDER_LABEL_SHUFFLE_CONTROLS_PLAN.md	Matrix|Phase|mode|phase|phase_response|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_RESULT_NOTE.md	Phase|mode|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01C3_REAL_KERNEL_RESIMULATION_LABEL_SHUFFLE_RESULT_NOTE.md	E_i|Phase|mode|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01C3_REAL_KERNEL_RESIMULATION_LABEL_SHUFFLE_SPECTRUM_MATCHED_CONTROL_PLAN.md	Matrix|Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_PLAN.md	E_i|Paar|Phase|mode|pair_id|phase|phase_response|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_RESULT_NOTE.md	Phase|mode|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1A_WAVE_IDENTITY_RESIDUAL_SCANNER_SPEC.md	E_i|E_j|Phase|lag|pair_id|phase|phase_i|phase_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1B_WAVE_IDENTITY_RESIDUAL_MINIMAL_SCANNER_IMPLEMENTATION_PLAN.md	E_i|E_j|Phase|lag|mode|pair_id|phase|phase_i|phase_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1B_WAVE_IDENTITY_RESIDUAL_MINIMAL_SCANNER_RESULT_NOTE.md	E_i|Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1B_WAVE_IDENTITY_RESIDUAL_MINIMAL_SCANNER_RESULT_NOTE_TEMPLATE.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1C_WAVE_IDENTITY_RESIDUAL_CONTROL_STRESS_RESULT_NOTE.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1C_WAVE_IDENTITY_RESIDUAL_CONTROL_STRESS_RESULT_NOTE_TEMPLATE.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1C_WAVE_IDENTITY_RESIDUAL_CONTROL_STRESS_WEIGHT_SENSITIVITY_PLAN.md	E_i|E_j|Phase|lag|pair_id|phase|phase_i|phase_j	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1D_WAVE_IDENTITY_MANIFOLD_DEGENERACY_AUDIT_PLAN.md	E_i|Phase|delta_p|delta_phi|lag|pair_id|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1D_WAVE_IDENTITY_MANIFOLD_DEGENERACY_AUDIT_RESULT_NOTE.md	E_i|Phase|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1D_WAVE_IDENTITY_MANIFOLD_DEGENERACY_AUDIT_RESULT_NOTE_TEMPLATE.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1E_COLLISION_AWARE_MANIFOLD_INFORMED_WAVE_IDENTITY_PROFILE_PLAN.md	E_i|Phase|delta_p|delta_phi|lag|pair_id|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1E_COLLISION_AWARE_WAVE_IDENTITY_PROFILE_RESULT_NOTE.md	E_i|Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1E_COLLISION_AWARE_WAVE_IDENTITY_PROFILE_RESULT_NOTE_TEMPLATE.md	E_i|Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1F_COLLISION_AWARE_PROFILE_ROBUSTNESS_PARAMETER_SWEEP_PLAN.md	E_i|Phase|lag|pair_id|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1F_COLLISION_AWARE_PROFILE_ROBUSTNESS_PARAMETER_SWEEP_RESULT_NOTE.md	E_i|Phase|lag|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1F_COLLISION_AWARE_PROFILE_ROBUSTNESS_PARAMETER_SWEEP_RESULT_NOTE_TEMPLATE.md	E_i|Phase|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1G_WARNING_DRIVER_DECOMPOSITION_FAILURE_MODE_ANALYSIS_PLAN.md	E_i|Phase|lag|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1G_WARNING_DRIVER_DECOMPOSITION_FAILURE_MODE_ANALYSIS_RESULT_NOTE.md	E_i|Kandidat|Phase|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1G_WARNING_DRIVER_DECOMPOSITION_FAILURE_MODE_ANALYSIS_RESULT_NOTE_TEMPLATE.md	mode	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1H_CYCLIC_COORDINATE_ACCEPTANCE_REGION_IMPOSTOR_EXCLUSION_PLAN.md	E_i|Phase|delta_p|delta_phi|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1H_CYCLIC_COORDINATE_ACCEPTANCE_REGION_IMPOSTOR_EXCLUSION_RESULT_NOTE.md	E_i|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1H_CYCLIC_COORDINATE_ACCEPTANCE_REGION_IMPOSTOR_EXCLUSION_RESULT_NOTE_TEMPLATE.md	Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1I_CYCLIC_PHASE_SOURCE_VALIDATION_OVERSTRICTNESS_AUDIT_PLAN.md	E_i|Phase|delta_p|delta_phi|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1I_CYCLIC_PHASE_SOURCE_VALIDATION_OVERSTRICTNESS_AUDIT_RESULT_NOTE.md	E_i|Phase|delta_E|delta_p|delta_phi|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1I_CYCLIC_PHASE_SOURCE_VALIDATION_OVERSTRICTNESS_AUDIT_RESULT_NOTE_TEMPLATE.md	Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1JKL_SYNTHETIC_PHASE_EXPOSURE_LEAKAGE_AUDIT_SYNTHESIS_NOTE.md	E_i|Phase|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_PLAN.md	E_i|E_j|Phase|delta_p|delta_phi|lag|mode|phase|phase_i|phase_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_RESULT_NOTE.md	E_i|E_j|Phase|delta_p|delta_phi|mode|phase|phase_i|phase_j	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_RESULT_NOTE_TEMPLATE.md	E_i|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_PLAN.md	E_i|Phase|delta_p|delta_phi|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_RESULT_NOTE.md	E_i|Phase|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_RESULT_NOTE_TEMPLATE.md	E_i|Phase|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_PLAN.md	E_i|E_j|Phase|lag|mode|phase|phase_i|phase_j	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE.md	E_i|Phase|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE_TEMPLATE.md	E_i|Phase|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_PLAN.md	E_i|Phase|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RESULT_NOTE.md	E_i|Phase|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RUNNER_SPEC.md	E_i|Phase|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_PLAN.md	E_i|Phase|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_RESULT_NOTE.md	E_i|Phase|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1O_D1M_REFINED_MULTI_CHANNEL_PROFILE_RESULT_NOTE.md	E_i|Phase|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1O_D1M_RUNNER_REFINEMENT_SPECIFICATION.md	E_i|Phase|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1P_D1O_REFINED_OUTPUT_AUDIT_REGRESSION_RESULT_NOTE.md	E_i|Phase|lag|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D1_WAVE_IDENTITY_FINGERPRINT_MINIMAL_DESIGN_PLAN.md	E_i|E_j|Phase|mode|pair_id|phase|phase_i|phase_j|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01D_WAVE_IDENTITY_FINGERPRINT_OBSERVABLES_CONCEPT.md	E_i|Phase|frequency|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_OBSERVABLE_SCANNER_CONCEPT.md	E_i|Phase|energy|mode|p_i|phase|phase_i|spectral_gap	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_SCANNER_IMPLEMENTATION_PLAN.md	E_i|Phase|energy|mode|phase|phase_response|spectral_gap	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_SCANNER_RESULT_NOTE.md	Phase|mode|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_D1M_D1P_CONSOLIDATION_AND_NEXT_STEP_GATE_NOTE.md	E_i|Phase|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md	E_i|Phase|delta_p|mode|p_i|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_RUNNER_SPEC.md	E_i|Phase|delta_p|mode|pair_id|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md	E_i|Phase|delta_p|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_RESULT_NOTE.md	E_i|Phase|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_SPEC.md	E_i|Phase|delta_p|lag|mode|pair_id|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WIFM01C_ADVERSARIAL_AMBIGUITY_STRESS_CASE_SPEC.md	E_i|Phase|delta_p|lag|mode|pair_id|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WIFM01C_ADVERSARIAL_AMBIGUITY_STRESS_RESULT_NOTE.md	E_i|Phase|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WIFM01D_CONSOLIDATION_AND_GATE_NOTE.md	E_i|Phase|Planck|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md	E_i|Phase|delta_p|lag|mode|phase|phase_i|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_CPNS02_MAXENT_DEGENERACY_SPEC.md	Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_CSTRUCT01_C_AS_LORENTZ_COMPATIBLE_RELATIONAL_LIMIT_CONCEPT_NOTE.md	Energie|energy|mode|momentum	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_IDSPACE01_CPNS02_MAXENT_PREPARATION_PLAN.md	Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_IDSPACE01_IDENTITY_SPACE_DEFINITION_SPEC.md	E_i|Phase|lag|p_i|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_IDSPACE_CPNS03_MINIMAL_SCHEMA_ACCEPTANCE_TEST_PLAN.md	E_i|Phase|lag|p_i|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_IDSPACE_CPNS04_MINIMAL_SCHEMA_SCAFFOLD_RESULT_NOTE.md	E_i|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_IDSPACE_CPNS05_MINIMAL_SCHEMA_VALIDATION_RUNNER_PLAN.md	E_i|Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_IDSPACE_CPNS06_MINIMAL_SCHEMA_VALIDATION_RESULT_NOTE.md	E_i|Phase|lag|mode|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_INTERFACE01_CONNECTOR_DIAGNOSTIC_SPEC.md	Kandidat|Paar|Phase|lag|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_INTERFACE02_MINIMAL_RECORD_SCHEMA_AND_ACCEPTANCE_SPEC.md	E_i|Paar|lag	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_INTERFACE03_RT_QM_CAUSALITY_ROSETTA_TRANSLATOR_SPEC.md	Compton|Phase|energy|frequency|lag|mode|momentum|phase|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_INTERFACE_SHAPIROINFO_RESULT_READOUT_2026_05_28.md	Kandidat|mode|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_PRE_SPEC_INGREDIENTS.md	E_i|Kandidat|Phase|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_CONTROL_EXTENSION_PLAN.md	E_i|Phase|phase|phase_i|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_CONTROL_RUN_RESULT_NOTE.md	Matrix|Phase|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_DECISION_STATUS_AFTER_J.md	Phase|lag|mode|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_GLOBAL_PHASE_INVARIANT_OBSERVABLE_PROBE_PLAN.md	E_i|Phase|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_GLOBAL_PHASE_INVARIANT_PROBE_RESULT_NOTE.md	E_i|Matrix|Phase|phase|phase_i|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_MINIMAL_RUN_RESULT_NOTE.md	Matrix|Phase|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_NEXT_AFTER_OBSERVABLE_AUDIT_STATUS_NOTE.md	E_i|Matrix|Phase|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_OBSERVABLE_NORMALIZATION_AUDIT_PLAN.md	Phase|phase	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_OBSERVABLE_NORMALIZATION_AUDIT_RESULT_NOTE.md	Phase|phase|phase_response	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_PHASE_RESPONSE_CONFIG_FIELDS.md	E_i|Matrix|Phase|mode|phase|phase_response|r_s	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_RESIDUAL_CONTROL_WARNING_ANALYSIS_PLAN.md	E_i|Phase|mode|phase|phase_i	md
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	docs/QSB_ST_LIC01_TAU_EPSILON_RESIDUAL_CONTROL_WARNING_ANALYSIS_RESULT_NOTE.md	Phase|phase|phase_response	md
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_dwh_inventory (run_id, object_type, table_schema, table_name, column_name, matched_reason) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	object_type	table_schema	table_name	column_name	matched_reason
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_decision_cases	lag_structure_status	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_design_summary	input_critical_nullmodel	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_execution_result_review_decision	not_formal_lag_mechanism_candidate_reason	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_execution_summary	input_critical_nullmodel	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_failure_modes	failure_modes	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_independent_lag_variable	lag_proxy_correlation	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_independent_lag_variable	lag_proxy_mutual_information_or_group_score	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_independent_lag_variable	lag_proxy_rank_correlation	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_independent_lag_variable	lag_reconstruction_accuracy	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_nullmodel_operationalization	lag_preserving_nullmodel_role	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_nullmodel_operationalization	nullmodel_appropriateness_class	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_order_scrambling	lag_structure_distance	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_order_scrambling	lag_structure_preserved	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_physical_proxy	proxy_lag_correlation	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_physical_proxy	proxy_lag_monotonicity_score	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_test_family_spec	failure_modes	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_test_results	lag_explained_variance_ratio	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_test_results	lag_reconstruction_accuracy	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_test_results	lag_structure_preserved_rate	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_test_results	nullmodel_appropriateness_class	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_test_results	proxy_lag_correlation	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_toeplitz_dependency	between_lag_variance	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_toeplitz_dependency	lag_explained_variance_ratio	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_lag_mechanism_toeplitz_dependency	within_lag_variance_mean	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_comparison_metrics	critical_nullmodel_reproduction	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_comparison_metrics	lag_structure_z_score	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_comparison_metrics	nullmodel_family	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_design_summary	nullmodel_family_count	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_diagnostics_required	nullmodel_key	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_execution_authorization	nullmodel_key	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_execution_result_review_critical_findings	critical_nullmodel	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_execution_result_review_family	nullmodel_family	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_execution_result_review_summary	critical_nullmodel	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_execution_result_review_summary	critical_nullmodel_reproduction	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_execution_summary	nullmodel_family_count	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_failure_modes	failure_mode	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_failure_modes	failure_mode_id	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_failure_modes	nullmodel_key	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_family_spec	failure_modes	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_family_spec	nullmodel_id	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_family_spec	nullmodel_key	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_family_summary	nullmodel_family	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	between_lag_separation	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	directed_pair_consistency	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	directed_pair_feature_count	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	lag_axis_collapse_score	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	lag_class_count	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	lag_class_structure_preserved	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	lag_structure_distance	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	lag_structure_reproduction_class	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	nullmodel_family	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	nullmodel_name	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_lag_class_metrics	within_lag_similarity	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	between_lag_separation	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	directed_pair_consistency	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	directed_pair_feature_count	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	lag_axis_collapse_score	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	lag_class_count	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	lag_class_structure_preserved	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	lag_structure_distance	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	lag_structure_reproduction_class	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	lambda_max	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	lambda_min	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	nullmodel_family	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	nullmodel_name	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_sample_results	within_lag_similarity	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_specificity_classification	critical_nullmodel	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_specificity_classification	strengthening_nullmodel	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_spectral_core_metrics	lambda_max	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_spectral_core_metrics	lambda_min	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_spectral_core_metrics	nullmodel_family	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_nullmodel_spectral_core_metrics	nullmodel_name	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_psd_test_gate_result	lambda_max	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_psd_test_gate_result	lambda_min	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_effective_lag_axis_gram	lag_axis	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_effective_lag_axis_gram	representative_pair_id	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_lag_class_membership	abs_lag	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_lag_class_membership	lag	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_lag_class_membership	lag_axis	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_lag_class_membership	pair_id	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_lag_class_summary	abs_lag	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_lag_class_summary	lag_axis	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_relation_pair	pair_id_a	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_relation_pair	pair_id_b	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_result	lambda_max	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	pbr_spectral_readout_result	lambda_min	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_lag_mechanismus_ergebnis_de	Lag-Rekonstruktionsgenauigkeit	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_lag_mechanismus_ergebnis_de	Lag-Struktur-Erhaltungsrate	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_lag_mechanismus_ergebnis_de	Lag-erklärte Varianz	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_lag_mechanismus_ergebnis_de	Nullmodell-Angemessenheitsklasse	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_lag_mechanismus_ergebnis_de	Proxy-Lag-Korrelation	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_lag_mechanismus_ergebnis_de	unabhängige Lag-Variable	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_lag_mechanismus_ergebnis_de	unabhängige Lag-Variable verfügbar	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Anzahl Lag-Klassen	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Innerhalb-Lag-Ähnlichkeit	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Lag-Achsen-Kollapswert	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Lag-Klassen-Struktur erhalten	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Lag-Struktur-Abstand	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Lag-Struktur-Reproduktion	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Nullmodell-Familie	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Nullmodell-Name	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Nullmodell-Probe-ID	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	Zwischen-Lag-Trennung	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	kritisches Nullmodell	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_ergebnis_de	stärkendes Nullmodell	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_nullmodell_result_review_de	kritisches Nullmodell	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_psd_test01_gate_result	lambda_max	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_psd_test01_gate_result	lambda_min	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_psd_test01_summary	lambda_max	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_psd_test01_summary	lambda_min	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_spectral_readout01_lag_class_summary	abs_lag	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_spectral_readout01_lag_class_summary	lag_axis	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_spectral_readout01_summary	lambda_max	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	column	qsb_planck_bridge	v_pbr_spectral_readout01_summary	lambda_min	candidate_column_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	mart	v_qsb_metadata_aliases_de		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	mart	v_qsb_metadata_fields		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	mart	v_qsb_metadata_units		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	mart	v_sparc_field_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	mart	v_sparc_unit_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_alias		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_claim		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_dataset		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_field		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_lineage		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_search_token		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_unit		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	metadata	meta_view		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	pg_catalog	pg_largeobject_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	lit_addendum_ashreurov_2014_claim_boundary_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	lit_addendum_ashreurov_2014_field_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	lit_addendum_ashreurov_2014_metadata_integration_run		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	litnote01_claim_boundary_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	litnote01_field_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	litnote01_metadata_integration_run		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	scale_mapping_note01_claim_boundary_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	scale_mapping_note01_field_metadata		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	scale_mapping_note01_metadata_integration_run		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	v_planck_bridge_lit_addendum_ashreurov_2014_metadata_dashboard		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	v_planck_bridge_lit_addendum_ashreurov_2014_metadata_search		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	v_planck_bridge_litnote01_metadata_dashboard		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	v_planck_bridge_litnote01_metadata_search		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	v_planck_bridge_scale_mapping_note01_metadata_dashboard		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	qsb_metadata	v_planck_bridge_scale_mapping_note01_metadata_search		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	server	metadata_server_config		metadata_table_name
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	metadata_table	server	metadata_server_endpoint		metadata_table_name
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_candidate_variables (run_id, candidate_id, source_type, source_path_or_table, candidate_variable_name, candidate_category, artifact_level, pair_mappable, has_i_j_or_pair_id, has_lag, has_units, has_dimension_metadata, has_source_lineage, upstream_generation_stage, derived_from_index_order, derived_from_lag_or_abs_lag, derived_from_pair_id, non_alias_evidence, alias_risk_level, independence_status, review_need, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	candidate_id	source_type	source_path_or_table	candidate_variable_name	candidate_category	artifact_level	pair_mappable	has_i_j_or_pair_id	has_lag	has_units	has_dimension_metadata	has_source_lineage	upstream_generation_stage	derived_from_index_order	derived_from_lag_or_abs_lag	derived_from_pair_id	non_alias_evidence	alias_risk_level	independence_status	review_need	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0001	repo_file	data/OUTREACH01A-06/public_profile_links.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0002	repo_file	data/OUTREACH01A-06/source_inventory.md	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0003	repo_file	data/OUTREACH01A-DTC-DEMO01/FIELD_LIST.md	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0004	repo_file	data/OUTREACH01A-DTC-DEMO01/compact_contact_table_en.md	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0005	repo_file	data/OUTREACH01A-DTC-DEMO01/compact_contact_table_es.md	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0006	repo_file	data/OUTREACH01A-DTC-DEMO01/contact_figure_content_spec.md	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0007	repo_file	data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_records.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0008	repo_file	data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_schema.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0009	repo_file	data/OUTREACH01A-DTC-DEMO01/field_aliases_de.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0010	repo_file	data/OUTREACH01A-DTC-DEMO01/field_aliases_en.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0011	repo_file	data/OUTREACH01A-DTC-DEMO01/field_aliases_es.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0012	repo_file	data/QSB-BRIDGE-DATA-01/candidate_source_registry.csv	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0013	repo_file	data/QSB-BRIDGE-DATA-01/preflight_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0014	repo_file	data/QSB-BRIDGE-DATA-02A/benzene_edges.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0015	repo_file	data/QSB-BRIDGE-DATA-02A/benzene_nodes.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0016	repo_file	data/QSB-BRIDGE-DATA-02A/c60_edges.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0017	repo_file	data/QSB-BRIDGE-DATA-02A/c60_faces.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0018	repo_file	data/QSB-BRIDGE-DATA-02A/c60_nodes.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0019	repo_file	data/QSB-BRIDGE-DATA-02A/sp2_contrast_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0020	repo_file	data/QSB-BRIDGE-DATA-02A/sp2_contrast_manifest.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0021	repo_file	data/QSB-BRIDGE-DATA-02B/adamantane_edges.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0022	repo_file	data/QSB-BRIDGE-DATA-02B/adamantane_nodes.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0023	repo_file	data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_config.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0024	repo_file	data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0025	repo_file	data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0026	repo_file	data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0027	repo_file	data/QSB-BRIDGE-DATA-02B/ethyne_edges.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0028	repo_file	data/QSB-BRIDGE-DATA-02B/ethyne_nodes.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0029	repo_file	data/QSB-BRIDGE-DATA-02C/control_edges.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0030	repo_file	data/QSB-BRIDGE-DATA-02C/control_ensemble_config.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0031	repo_file	data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0032	repo_file	data/QSB-BRIDGE-DATA-02C/control_family_summary.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0033	repo_file	data/QSB-BRIDGE-DATA-02C/control_nodes.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0034	repo_file	data/QSB-BRIDGE-DATA-02C/control_validation_summary.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0035	repo_file	data/QSB-BRIDGE-DATA-02D/control_diagnostic_summary.csv	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0036	repo_file	data/QSB-BRIDGE-DATA-02D/highest_risk_mimic_diagnostic.csv	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0037	repo_file	data/QSB-BRIDGE-DATA-02D/original_vs_control_separation.csv	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0038	repo_file	data/QSB-BRIDGE-DATA-02E/README.md	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0039	repo_file	data/QSB-BRIDGE-DATA-02E/control_destruction_effectiveness_summary.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0040	repo_file	data/QSB-BRIDGE-DATA-02E/control_mimic_failure_inventory.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0041	repo_file	data/QSB-BRIDGE-DATA-02E/control_mimicry_revision_manifest.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0042	repo_file	data/QSB-BRIDGE-DATA-02E/diagnostic_specificity_summary.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0043	repo_file	data/QSB-BRIDGE-DATA-02E/mimic_family_risk_summary.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0044	repo_file	data/QSB-BRIDGE-DATA-02E/revision_recommendation_summary.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0045	repo_file	data/QSB-CAUSALITY06B-02/FIELD_LIST.md	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0046	repo_file	data/QSB-CAUSALITY06B-02/candidate_state_record_schema.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0047	repo_file	data/QSB-CAUSALITY06B-02/example_candidate_state_records.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0048	repo_file	data/QSB-CAUSALITY06B-04/field_aliases_de.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0049	repo_file	data/QSB-CAUSALITY06B-04/inner_sphere_et_state_records.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0050	repo_file	data/QSB-CAUSALITY06B-04/source_inventory.md	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0051	repo_file	data/QSB-CAUSALITY06B-04/transition_candidates.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0052	repo_file	data/QSB-CAUSALITY06B-05/field_aliases_de.json	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0053	repo_file	data/QSB-CAUSALITY06B-05/negative_control_state_pairs.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0054	repo_file	data/QSB-CAUSALITY06B-05/robustness_test_cases.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0055	repo_file	data/QSB-CAUSALITY06B-06/field_aliases_de.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0056	repo_file	data/QSB-CAUSALITY06B-06/oxalate_case_state_records.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0057	repo_file	data/QSB-CAUSALITY06B-06/oxalate_transition_candidates.json	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0058	repo_file	data/QSB-CAUSALITY06B-06/source_inventory.md	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0059	repo_file	data/QSB-CAUSALITY07-02/cycle_phase_rules.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0060	repo_file	data/QSB-CAUSALITY07-02/field_aliases_de.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0061	repo_file	data/QSB-CAUSALITY07-02/oregonator_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0062	repo_file	data/QSB-CAUSALITY07-02/source_inventory.md	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0063	repo_file	data/QSB-CAUSALITY07-03/cycle_semantics_hardening_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0064	repo_file	data/QSB-CAUSALITY07-04/causal_condition_registry.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0065	repo_file	data/QSB-CAUSALITY07-04/controlled_causal_structure_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0066	repo_file	data/QSB-CAUSALITY07-04A/independent_transition_reconstruction_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0067	repo_file	data/QSB-CAUSALITY07-04A/reconstruction_rule_registry.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0068	repo_file	data/QSB-CAUSALITY07-04B/calibration_metric_registry.json	candidate_term_match	unknown	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0069	repo_file	data/QSB-CAUSALITY07-04B/heuristic_calibration_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0070	repo_file	data/QSB-CAUSALITY07-04C/fine_calibration_metric_registry.json	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0071	repo_file	data/QSB-CAUSALITY07-04C/fine_calibration_sweep_config.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0072	repo_file	data/QSB-CORRCORE01/correlation_core_claim_boundary_registry.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0073	repo_file	data/QSB-CORRCORE01/correlation_core_cross_strand_map.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0074	repo_file	data/QSB-CORRCORE01/correlation_core_equation_registry.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0075	repo_file	data/QSB-CORRCORE01/correlation_core_object_registry.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0076	repo_file	data/QSB-CORRCORE01/correlation_core_quantity_registry.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0077	repo_file	data/QSB-CORRCORE01/correlation_core_source_inventory.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0078	repo_file	data/QSB-DB/schema/qsb_research_db_schema.sql	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0079	repo_file	data/QSB-META01-01/repository_metadata_inventory_config.json	candidate_term_match	unknown	unknown_level	false	false	false	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0080	repo_file	data/QSB-META01-02/canonical_metadata_contract_config.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0081	repo_file	data/QSB-META01-02/canonical_metadata_schema.sql	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0082	repo_file	data/QSB-META01-02/controlled_vocabularies.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0083	repo_file	data/QSB-META01-02/example_metadata_records.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0084	repo_file	data/QSB-META01-02/unit_dimension_registry.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0085	repo_file	data/QSB-META01-03/causality07_metadata_mapping.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0086	repo_file	data/QSB-META01-03/causality07_pilot_metadata_config.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0087	repo_file	data/QSB-META02/cross_mart_key_mapping_schema.json	candidate_term_match	unknown	unknown_level	false	false	false	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0088	repo_file	data/QSB-META02/cross_mart_seed_mappings.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	true	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0089	repo_file	data/QSB-META02/cross_mart_semantic_relation_registry.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0090	repo_file	data/QSB-META02/cross_mart_transformation_rule_registry.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0091	repo_file	data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql	delta_phi_or_phase	phase_proxy	unknown_level	true	true	false	true	false	true	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0092	repo_file	data/QSB-OUTREACH01A/002_qsb_outreach01a_sqlite_views.sql	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0093	repo_file	data/QSB-OUTREACH01A/canonical_schema.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	true	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0094	repo_file	data/QSB-OUTREACH01A/field_aliases.csv	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0095	repo_file	data/QSB-OUTREACH01A/synthetic_demonstrator_config.yaml	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0096	repo_file	data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0097	repo_file	data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0098	repo_file	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/archival_cluster_inventory.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0099	repo_file	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/canonical_rerun_map.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0100	repo_file	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/preregistered_hypotheses.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0101	repo_file	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/provenance_status_table.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0102	repo_file	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/recovered_file_manifest.csv	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0103	repo_file	data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0104	repo_file	data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0105	repo_file	data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0106	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/dwh14a_high_priority_manual_evidence.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0107	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_binary_ell1.py	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0108	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_stand_alone_ELL1_model.py	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0109	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_timing_model.py	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	true	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0110	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_pulsar_1_1_5_METADATA.txt	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0111	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping_evidence.md	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	true	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0112	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping_manifest.csv	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	true	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0113	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_examples_ver1.pdf	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0114	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_manual.pdf	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0115	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo_reference_toa_format.txt	delta_phi_or_phase	phase_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0116	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1_primary_evidence_manifest.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	true	false	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0117	repo_file	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1_primary_field_definition.md	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	true	false	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0118	repo_file	data/QSB-ST-SHAPIROINFO/public_source_download_manifest_template.yaml	mode_or_frequency	frequency_proxy	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0119	repo_file	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/j0740_6620_quarantine_download_manifest_2026_05_29.yaml	candidate_term_match	unknown	unknown_level	false	false	true	false	false	true	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0120	repo_file	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0121	repo_file	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0122	repo_file	data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_claim_true.yaml	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0123	repo_file	data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_download_open.yaml	candidate_term_match	unknown	unknown_level	false	false	true	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0124	repo_file	data/QSB-ST-SHAPIROINFO/toy_comparator_config.yaml	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0125	repo_file	data/README_BMC07_inputs.md	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0126	repo_file	data/README_BMC07_inputs_minimal_bundle.md	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0127	repo_file	data/bmc01/bmc01_baseline_relational_table_template.csv	candidate_term_match	unknown	unknown_level	true	true	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0128	repo_file	data/bmc04/bmc04_baseline_relational_table_template.csv	candidate_term_match	unknown	unknown_level	true	true	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0129	repo_file	data/bmc07_config_coupling_arm.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0130	repo_file	data/bmc07_config_minimal_readouts.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0131	repo_file	data/bmc07c_backbone_variation_config.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0132	repo_file	data/bmc08_dataset_manifest.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0133	repo_file	data/bmc08_dataset_manifest.template.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0134	repo_file	data/bmc08_realdata_config.template.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0135	repo_file	data/bmc08_realdata_config.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0136	repo_file	data/bmc08a_m39x1_featuretable_config.template.yaml	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0137	repo_file	data/bmc08a_m39x1_featuretable_config.yaml	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0138	repo_file	data/bmc08a_real_units_feature_table.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0139	repo_file	data/bmc08a_real_units_feature_table.template.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0140	repo_file	data/bmc08b_m39x1_no_ring_mirror_config.yaml	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0141	repo_file	data/bmc08b_real_units_feature_table.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0142	repo_file	data/bmc08b_realdata_config.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0143	repo_file	data/bmc08c_m39x1_sign_sensitive_ring_config.yaml	delta_phi_or_phase	phase_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	high	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0144	repo_file	data/bmc08c_real_units_feature_table.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0145	repo_file	data/bmc08c_realdata_config.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0146	repo_file	data/bmc09a_knn_inputs/k_2/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0147	repo_file	data/bmc09a_knn_inputs/k_3/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0148	repo_file	data/bmc09a_knn_inputs/k_4/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0149	repo_file	data/bmc09a_realdata_config.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0150	repo_file	data/bmc09b_runner_config_k_2.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0151	repo_file	data/bmc09b_runner_config_k_3.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0152	repo_file	data/bmc09b_runner_config_k_4.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0153	repo_file	data/bmc09c_mutual_knn_inputs/k_2/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0154	repo_file	data/bmc09c_mutual_knn_inputs/k_3/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0155	repo_file	data/bmc09c_mutual_knn_inputs/k_4/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0156	repo_file	data/bmc09c_runner_config_k_2.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0157	repo_file	data/bmc09c_runner_config_k_3.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0158	repo_file	data/bmc09c_runner_config_k_4.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0159	repo_file	data/bmc09d_runner_config_hybrid_k3_tau_025.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0160	repo_file	data/bmc09d_runner_config_hybrid_k3_tau_03.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0161	repo_file	data/bmc09d_runner_config_threshold_tau_025.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0162	repo_file	data/bmc09d_runner_config_threshold_tau_03.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0163	repo_file	data/bmc09d_runner_config_threshold_tau_035.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0164	repo_file	data/bmc09d_threshold_hybrid_compare_config.yaml	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0165	repo_file	data/bmc09d_threshold_hybrid_inputs/graph_build_diagnostics.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0166	repo_file	data/bmc09d_threshold_hybrid_inputs/hybrid_k3_tau_025/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0167	repo_file	data/bmc09d_threshold_hybrid_inputs/hybrid_k3_tau_03/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0168	repo_file	data/bmc09d_threshold_hybrid_inputs/threshold_tau_025/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0169	repo_file	data/bmc09d_threshold_hybrid_inputs/threshold_tau_03/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0170	repo_file	data/bmc09d_threshold_hybrid_inputs/threshold_tau_035/node_metadata_real.csv	candidate_term_match	unknown	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0171	repo_file	data/bmc10_nullmodel_compare_config.yaml	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0172	repo_file	data/bmc10_nullmodel_config.yaml	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	true	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0173	repo_file	data/bmc10_nullmodel_inputs/graph_build_diagnostics.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0174	repo_file	data/bmc10_nullmodel_inputs/seed_101/nullmodel_feature_table.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0175	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0176	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0177	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0178	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0179	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0180	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0181	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0182	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0183	repo_file	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0184	repo_file	data/bmc10_nullmodel_inputs/seed_202/nullmodel_feature_table.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0185	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0186	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0187	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0188	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0189	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0190	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0191	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0192	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0193	repo_file	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0194	repo_file	data/bmc10_nullmodel_inputs/seed_303/nullmodel_feature_table.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0195	repo_file	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0196	repo_file	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0197	repo_file	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0198	repo_file	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/baseline_relational_table_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0199	repo_file	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/graph_build_summary.json	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0200	repo_file	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/node_metadata_real.csv	mode_or_frequency	frequency_proxy	unknown_level	false	false	false	false	false	false	repo	unknown	unknown	unknown	not_established_by_scout	unknown	unknown_requires_lineage	review_required_before_use	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0201	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_decision_cases	lag_structure_status	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0202	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_design_summary	input_critical_nullmodel	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0203	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_decision	not_formal_lag_mechanism_candidate_reason	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0204	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_execution_summary	input_critical_nullmodel	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0205	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_failure_modes	failure_modes	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0206	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_independent_lag_variable	lag_proxy_correlation	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0207	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_independent_lag_variable	lag_proxy_mutual_information_or_group_score	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0208	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_independent_lag_variable	lag_proxy_rank_correlation	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0209	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_independent_lag_variable	lag_reconstruction_accuracy	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0210	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_nullmodel_operationalization	lag_preserving_nullmodel_role	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0211	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_nullmodel_operationalization	nullmodel_appropriateness_class	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0212	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_order_scrambling	lag_structure_distance	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0213	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_order_scrambling	lag_structure_preserved	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0214	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_physical_proxy	proxy_lag_correlation	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0215	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_physical_proxy	proxy_lag_monotonicity_score	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0216	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_test_family_spec	failure_modes	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0217	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_test_results	lag_explained_variance_ratio	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0218	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_test_results	lag_reconstruction_accuracy	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0219	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_test_results	lag_structure_preserved_rate	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0220	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_test_results	nullmodel_appropriateness_class	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0221	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_test_results	proxy_lag_correlation	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0222	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_toeplitz_dependency	between_lag_variance	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0223	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_toeplitz_dependency	lag_explained_variance_ratio	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0224	dwh_table	qsb_planck_bridge.pbr_lag_mechanism_toeplitz_dependency	within_lag_variance_mean	unknown	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0225	dwh_table	qsb_planck_bridge.pbr_nullmodel_comparison_metrics	critical_nullmodel_reproduction	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0226	dwh_table	qsb_planck_bridge.pbr_nullmodel_comparison_metrics	lag_structure_z_score	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0227	dwh_table	qsb_planck_bridge.pbr_nullmodel_comparison_metrics	nullmodel_family	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0228	dwh_table	qsb_planck_bridge.pbr_nullmodel_design_summary	nullmodel_family_count	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0229	dwh_table	qsb_planck_bridge.pbr_nullmodel_diagnostics_required	nullmodel_key	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0230	dwh_table	qsb_planck_bridge.pbr_nullmodel_execution_authorization	nullmodel_key	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0231	dwh_table	qsb_planck_bridge.pbr_nullmodel_execution_result_review_critical_findings	critical_nullmodel	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0232	dwh_table	qsb_planck_bridge.pbr_nullmodel_execution_result_review_family	nullmodel_family	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0233	dwh_table	qsb_planck_bridge.pbr_nullmodel_execution_result_review_summary	critical_nullmodel	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0234	dwh_table	qsb_planck_bridge.pbr_nullmodel_execution_result_review_summary	critical_nullmodel_reproduction	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0235	dwh_table	qsb_planck_bridge.pbr_nullmodel_execution_summary	nullmodel_family_count	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0236	dwh_table	qsb_planck_bridge.pbr_nullmodel_failure_modes	failure_mode	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0237	dwh_table	qsb_planck_bridge.pbr_nullmodel_failure_modes	failure_mode_id	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0238	dwh_table	qsb_planck_bridge.pbr_nullmodel_failure_modes	nullmodel_key	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0239	dwh_table	qsb_planck_bridge.pbr_nullmodel_family_spec	failure_modes	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0240	dwh_table	qsb_planck_bridge.pbr_nullmodel_family_spec	nullmodel_id	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0241	dwh_table	qsb_planck_bridge.pbr_nullmodel_family_spec	nullmodel_key	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0242	dwh_table	qsb_planck_bridge.pbr_nullmodel_family_summary	nullmodel_family	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0243	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	between_lag_separation	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0244	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	directed_pair_consistency	frequency_proxy	metadata_level	unknown	true	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0245	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	directed_pair_feature_count	frequency_proxy	metadata_level	unknown	true	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0246	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	lag_axis_collapse_score	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0247	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	lag_class_count	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0248	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	lag_class_structure_preserved	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0249	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	lag_structure_distance	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0250	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	lag_structure_reproduction_class	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0251	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	nullmodel_family	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0252	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	nullmodel_name	frequency_proxy	metadata_level	unknown	unknown	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0253	dwh_table	qsb_planck_bridge.pbr_nullmodel_lag_class_metrics	within_lag_similarity	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0254	dwh_table	qsb_planck_bridge.pbr_nullmodel_sample_results	between_lag_separation	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0255	dwh_table	qsb_planck_bridge.pbr_nullmodel_sample_results	directed_pair_consistency	frequency_proxy	metadata_level	unknown	true	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0256	dwh_table	qsb_planck_bridge.pbr_nullmodel_sample_results	directed_pair_feature_count	frequency_proxy	metadata_level	unknown	true	unknown	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0257	dwh_table	qsb_planck_bridge.pbr_nullmodel_sample_results	lag_axis_collapse_score	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0258	dwh_table	qsb_planck_bridge.pbr_nullmodel_sample_results	lag_class_count	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0259	dwh_table	qsb_planck_bridge.pbr_nullmodel_sample_results	lag_class_structure_preserved	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0260	dwh_table	qsb_planck_bridge.pbr_nullmodel_sample_results	lag_structure_distance	frequency_proxy	metadata_level	unknown	unknown	true	unknown	unknown	unknown	dwh	unknown	unknown	unknown	not_established_by_dwh_presence	unknown	unknown_requires_lineage	dwh_source_lineage_check_required	dwh_presence_alone_no_independence_claim
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_lineage_assessment (run_id, candidate_id, source_path_or_table, has_source_lineage, lineage_assessment) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	candidate_id	source_path_or_table	has_source_lineage	lineage_assessment
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0001	data/OUTREACH01A-06/public_profile_links.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0002	data/OUTREACH01A-06/source_inventory.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0003	data/OUTREACH01A-DTC-DEMO01/FIELD_LIST.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0004	data/OUTREACH01A-DTC-DEMO01/compact_contact_table_en.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0005	data/OUTREACH01A-DTC-DEMO01/compact_contact_table_es.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0006	data/OUTREACH01A-DTC-DEMO01/contact_figure_content_spec.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0007	data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_records.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0008	data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_schema.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0009	data/OUTREACH01A-DTC-DEMO01/field_aliases_de.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0010	data/OUTREACH01A-DTC-DEMO01/field_aliases_en.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0011	data/OUTREACH01A-DTC-DEMO01/field_aliases_es.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0012	data/QSB-BRIDGE-DATA-01/candidate_source_registry.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0013	data/QSB-BRIDGE-DATA-01/preflight_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0014	data/QSB-BRIDGE-DATA-02A/benzene_edges.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0015	data/QSB-BRIDGE-DATA-02A/benzene_nodes.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0016	data/QSB-BRIDGE-DATA-02A/c60_edges.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0017	data/QSB-BRIDGE-DATA-02A/c60_faces.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0018	data/QSB-BRIDGE-DATA-02A/c60_nodes.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0019	data/QSB-BRIDGE-DATA-02A/sp2_contrast_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0020	data/QSB-BRIDGE-DATA-02A/sp2_contrast_manifest.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0021	data/QSB-BRIDGE-DATA-02B/adamantane_edges.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0022	data/QSB-BRIDGE-DATA-02B/adamantane_nodes.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0023	data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0024	data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0025	data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0026	data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0027	data/QSB-BRIDGE-DATA-02B/ethyne_edges.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0028	data/QSB-BRIDGE-DATA-02B/ethyne_nodes.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0029	data/QSB-BRIDGE-DATA-02C/control_edges.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0030	data/QSB-BRIDGE-DATA-02C/control_ensemble_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0031	data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0032	data/QSB-BRIDGE-DATA-02C/control_family_summary.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0033	data/QSB-BRIDGE-DATA-02C/control_nodes.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0034	data/QSB-BRIDGE-DATA-02C/control_validation_summary.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0035	data/QSB-BRIDGE-DATA-02D/control_diagnostic_summary.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0036	data/QSB-BRIDGE-DATA-02D/highest_risk_mimic_diagnostic.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0037	data/QSB-BRIDGE-DATA-02D/original_vs_control_separation.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0038	data/QSB-BRIDGE-DATA-02E/README.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0039	data/QSB-BRIDGE-DATA-02E/control_destruction_effectiveness_summary.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0040	data/QSB-BRIDGE-DATA-02E/control_mimic_failure_inventory.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0041	data/QSB-BRIDGE-DATA-02E/control_mimicry_revision_manifest.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0042	data/QSB-BRIDGE-DATA-02E/diagnostic_specificity_summary.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0043	data/QSB-BRIDGE-DATA-02E/mimic_family_risk_summary.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0044	data/QSB-BRIDGE-DATA-02E/revision_recommendation_summary.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0045	data/QSB-CAUSALITY06B-02/FIELD_LIST.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0046	data/QSB-CAUSALITY06B-02/candidate_state_record_schema.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0047	data/QSB-CAUSALITY06B-02/example_candidate_state_records.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0048	data/QSB-CAUSALITY06B-04/field_aliases_de.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0049	data/QSB-CAUSALITY06B-04/inner_sphere_et_state_records.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0050	data/QSB-CAUSALITY06B-04/source_inventory.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0051	data/QSB-CAUSALITY06B-04/transition_candidates.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0052	data/QSB-CAUSALITY06B-05/field_aliases_de.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0053	data/QSB-CAUSALITY06B-05/negative_control_state_pairs.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0054	data/QSB-CAUSALITY06B-05/robustness_test_cases.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0055	data/QSB-CAUSALITY06B-06/field_aliases_de.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0056	data/QSB-CAUSALITY06B-06/oxalate_case_state_records.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0057	data/QSB-CAUSALITY06B-06/oxalate_transition_candidates.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0058	data/QSB-CAUSALITY06B-06/source_inventory.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0059	data/QSB-CAUSALITY07-02/cycle_phase_rules.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0060	data/QSB-CAUSALITY07-02/field_aliases_de.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0061	data/QSB-CAUSALITY07-02/oregonator_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0062	data/QSB-CAUSALITY07-02/source_inventory.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0063	data/QSB-CAUSALITY07-03/cycle_semantics_hardening_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0064	data/QSB-CAUSALITY07-04/causal_condition_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0065	data/QSB-CAUSALITY07-04/controlled_causal_structure_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0066	data/QSB-CAUSALITY07-04A/independent_transition_reconstruction_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0067	data/QSB-CAUSALITY07-04A/reconstruction_rule_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0068	data/QSB-CAUSALITY07-04B/calibration_metric_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0069	data/QSB-CAUSALITY07-04B/heuristic_calibration_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0070	data/QSB-CAUSALITY07-04C/fine_calibration_metric_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0071	data/QSB-CAUSALITY07-04C/fine_calibration_sweep_config.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0072	data/QSB-CORRCORE01/correlation_core_claim_boundary_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0073	data/QSB-CORRCORE01/correlation_core_cross_strand_map.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0074	data/QSB-CORRCORE01/correlation_core_equation_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0075	data/QSB-CORRCORE01/correlation_core_object_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0076	data/QSB-CORRCORE01/correlation_core_quantity_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0077	data/QSB-CORRCORE01/correlation_core_source_inventory.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0078	data/QSB-DB/schema/qsb_research_db_schema.sql	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0079	data/QSB-META01-01/repository_metadata_inventory_config.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0080	data/QSB-META01-02/canonical_metadata_contract_config.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0081	data/QSB-META01-02/canonical_metadata_schema.sql	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0082	data/QSB-META01-02/controlled_vocabularies.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0083	data/QSB-META01-02/example_metadata_records.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0084	data/QSB-META01-02/unit_dimension_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0085	data/QSB-META01-03/causality07_metadata_mapping.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0086	data/QSB-META01-03/causality07_pilot_metadata_config.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0087	data/QSB-META02/cross_mart_key_mapping_schema.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0088	data/QSB-META02/cross_mart_seed_mappings.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0089	data/QSB-META02/cross_mart_semantic_relation_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0090	data/QSB-META02/cross_mart_transformation_rule_registry.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0091	data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0092	data/QSB-OUTREACH01A/002_qsb_outreach01a_sqlite_views.sql	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0093	data/QSB-OUTREACH01A/canonical_schema.json	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0094	data/QSB-OUTREACH01A/field_aliases.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0095	data/QSB-OUTREACH01A/synthetic_demonstrator_config.yaml	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0096	data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0097	data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0098	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/archival_cluster_inventory.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0099	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/canonical_rerun_map.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0100	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/preregistered_hypotheses.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0101	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/provenance_status_table.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0102	data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/recovered_file_manifest.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0103	data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0104	data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0105	data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0106	data/QSB-ST-SHAPIROINFO/manual_evidence/dwh14a_high_priority_manual_evidence.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0107	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_binary_ell1.py	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0108	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_stand_alone_ELL1_model.py	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0109	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_1_1_5_timing_model.py	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0110	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping/pint_pulsar_1_1_5_METADATA.txt	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0111	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping_evidence.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0112	data/QSB-ST-SHAPIROINFO/manual_evidence/ell1_geometric_phase_mapping_manifest.csv	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0113	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_examples_ver1.pdf	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0114	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo2_manual.pdf	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0115	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1/tempo_reference_toa_format.txt	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0116	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1_primary_evidence_manifest.csv	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0117	data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1_primary_field_definition.md	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0118	data/QSB-ST-SHAPIROINFO/public_source_download_manifest_template.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0119	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/j0740_6620_quarantine_download_manifest_2026_05_29.yaml	true	lineage_present_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0120	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0121	data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0122	data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_claim_true.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0123	data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_download_open.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0124	data/QSB-ST-SHAPIROINFO/toy_comparator_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0125	data/README_BMC07_inputs.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0126	data/README_BMC07_inputs_minimal_bundle.md	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0127	data/bmc01/bmc01_baseline_relational_table_template.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0128	data/bmc04/bmc04_baseline_relational_table_template.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0129	data/bmc07_config_coupling_arm.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0130	data/bmc07_config_minimal_readouts.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0131	data/bmc07c_backbone_variation_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0132	data/bmc08_dataset_manifest.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0133	data/bmc08_dataset_manifest.template.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0134	data/bmc08_realdata_config.template.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0135	data/bmc08_realdata_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0136	data/bmc08a_m39x1_featuretable_config.template.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0137	data/bmc08a_m39x1_featuretable_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0138	data/bmc08a_real_units_feature_table.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0139	data/bmc08a_real_units_feature_table.template.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0140	data/bmc08b_m39x1_no_ring_mirror_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0141	data/bmc08b_real_units_feature_table.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0142	data/bmc08b_realdata_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0143	data/bmc08c_m39x1_sign_sensitive_ring_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0144	data/bmc08c_real_units_feature_table.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0145	data/bmc08c_realdata_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0146	data/bmc09a_knn_inputs/k_2/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0147	data/bmc09a_knn_inputs/k_3/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0148	data/bmc09a_knn_inputs/k_4/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0149	data/bmc09a_realdata_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0150	data/bmc09b_runner_config_k_2.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0151	data/bmc09b_runner_config_k_3.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0152	data/bmc09b_runner_config_k_4.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0153	data/bmc09c_mutual_knn_inputs/k_2/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0154	data/bmc09c_mutual_knn_inputs/k_3/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0155	data/bmc09c_mutual_knn_inputs/k_4/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0156	data/bmc09c_runner_config_k_2.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0157	data/bmc09c_runner_config_k_3.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0158	data/bmc09c_runner_config_k_4.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0159	data/bmc09d_runner_config_hybrid_k3_tau_025.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0160	data/bmc09d_runner_config_hybrid_k3_tau_03.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0161	data/bmc09d_runner_config_threshold_tau_025.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0162	data/bmc09d_runner_config_threshold_tau_03.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0163	data/bmc09d_runner_config_threshold_tau_035.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0164	data/bmc09d_threshold_hybrid_compare_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0165	data/bmc09d_threshold_hybrid_inputs/graph_build_diagnostics.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0166	data/bmc09d_threshold_hybrid_inputs/hybrid_k3_tau_025/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0167	data/bmc09d_threshold_hybrid_inputs/hybrid_k3_tau_03/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0168	data/bmc09d_threshold_hybrid_inputs/threshold_tau_025/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0169	data/bmc09d_threshold_hybrid_inputs/threshold_tau_03/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0170	data/bmc09d_threshold_hybrid_inputs/threshold_tau_035/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0171	data/bmc10_nullmodel_compare_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0172	data/bmc10_nullmodel_config.yaml	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0173	data/bmc10_nullmodel_inputs/graph_build_diagnostics.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0174	data/bmc10_nullmodel_inputs/seed_101/nullmodel_feature_table.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0175	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0176	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0177	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_028/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0178	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0179	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0180	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_03/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0181	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0182	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0183	data/bmc10_nullmodel_inputs/seed_101/threshold_tau_032/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0184	data/bmc10_nullmodel_inputs/seed_202/nullmodel_feature_table.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0185	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0186	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0187	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_028/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0188	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0189	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0190	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_03/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0191	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0192	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0193	data/bmc10_nullmodel_inputs/seed_202/threshold_tau_032/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0194	data/bmc10_nullmodel_inputs/seed_303/nullmodel_feature_table.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0195	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0196	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0197	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_028/node_metadata_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0198	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/baseline_relational_table_real.csv	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0199	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/graph_build_summary.json	false	lineage_incomplete
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0200	data/bmc10_nullmodel_inputs/seed_303/threshold_tau_03/node_metadata_real.csv	false	lineage_incomplete
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_alias_risk (run_id, candidate_id, candidate_variable_name, alias_reference, alias_risk_level, independence_status, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	candidate_id	candidate_variable_name	alias_reference	alias_risk_level	independence_status	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0001	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0002	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0003	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0004	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0005	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0006	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0007	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0008	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0009	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0010	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0011	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0012	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0013	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0014	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0015	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0016	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0017	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0018	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0019	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0020	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0021	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0022	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0023	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0024	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0025	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0026	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0027	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0028	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0029	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0030	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0031	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0032	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0033	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0034	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0035	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0036	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0037	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0038	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0039	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0040	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0041	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0042	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0043	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0044	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0045	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0046	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0047	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0048	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0049	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0050	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0051	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0052	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0053	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0054	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0055	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0056	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0057	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0058	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0059	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0060	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0061	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0062	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0063	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0064	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0065	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0066	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0067	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0068	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0069	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0070	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0071	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0072	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0073	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0074	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0075	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0076	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0077	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0078	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0079	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0080	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0081	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0082	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0083	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0084	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0085	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0086	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0087	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0088	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0089	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0090	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0091	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0092	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0093	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0094	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0095	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0096	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0097	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0098	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0099	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0100	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0101	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0102	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0103	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0104	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0105	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0106	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0107	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0108	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0109	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0110	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0111	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0112	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0113	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0114	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0115	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0116	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0117	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0118	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0119	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0120	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0121	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0122	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0123	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0124	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0125	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0126	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0127	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0128	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0129	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0130	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0131	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0132	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0133	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0134	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0135	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0136	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0137	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0138	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0139	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0140	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0141	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0142	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0143	delta_phi_or_phase	unknown	high	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0144	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0145	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0146	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0147	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0148	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0149	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0150	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0151	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0152	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0153	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0154	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0155	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0156	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0157	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0158	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0159	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0160	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0161	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0162	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0163	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0164	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0165	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0166	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0167	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0168	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0169	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0170	candidate_term_match	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0171	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0172	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0173	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0174	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0175	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0176	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0177	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0178	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0179	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0180	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0181	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0182	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0183	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0184	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0185	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0186	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0187	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0188	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0189	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0190	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0191	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0192	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0193	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0194	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0195	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0196	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0197	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0198	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0199	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0200	mode_or_frequency	unknown	unknown	unknown_requires_lineage	candidate_only_no_independence_claim
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_physical_proxy_sources (run_id, proxy_family, candidate_status, source_path_or_table, claim_implication) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	proxy_family	candidate_status	source_path_or_table	claim_implication
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	momentum_proxy	source_candidate_not_found	not_available	source_candidate_only_no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	energy_proxy	source_candidate_not_found	not_available	source_candidate_only_no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	frequency_proxy	source_candidate_found_not_pair_mappable	data/OUTREACH01A-06/source_inventory.md	source_candidate_only_no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	phase_proxy	source_candidate_found_requires_mapping_review	data/OUTREACH01A-DTC-DEMO01/FIELD_LIST.md	source_candidate_only_no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	mode_proxy	source_candidate_not_found	not_available	source_candidate_only_no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	spectral_gap_proxy	source_candidate_not_found	not_available	source_candidate_only_no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	compton_schwarzschild_proxy	source_candidate_not_found	not_available	source_candidate_only_no_physical_proxy_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	planck_scale_mapping_proxy	source_candidate_not_found	not_available	source_candidate_only_no_physical_proxy_claim
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_pair_mapping_readiness (run_id, candidate_id, pair_mappable, mapping_readiness) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	candidate_id	pair_mappable	mapping_readiness
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0001	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0002	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0003	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0004	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0005	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0006	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0007	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0008	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0009	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0010	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0011	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0012	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0013	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0014	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0015	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0016	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0017	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0018	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0019	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0020	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0021	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0022	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0023	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0024	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0025	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0026	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0027	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0028	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0029	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0030	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0031	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0032	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0033	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0034	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0035	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0036	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0037	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0038	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0039	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0040	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0041	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0042	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0043	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0044	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0045	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0046	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0047	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0048	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0049	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0050	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0051	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0052	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0053	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0054	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0055	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0056	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0057	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0058	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0059	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0060	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0061	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0062	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0063	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0064	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0065	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0066	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0067	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0068	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0069	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0070	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0071	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0072	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0073	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0074	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0075	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0076	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0077	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0078	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0079	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0080	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0081	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0082	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0083	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0084	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0085	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0086	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0087	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0088	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0089	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0090	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0091	true	pair_mappable_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0092	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0093	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0094	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0095	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0096	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0097	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0098	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0099	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0100	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0101	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0102	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0103	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0104	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0105	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0106	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0107	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0108	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0109	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0110	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0111	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0112	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0113	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0114	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0115	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0116	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0117	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0118	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0119	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0120	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0121	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0122	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0123	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0124	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0125	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0126	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0127	true	pair_mappable_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0128	true	pair_mappable_requires_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0129	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0130	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0131	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0132	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0133	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0134	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0135	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0136	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0137	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0138	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0139	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0140	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0141	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0142	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0143	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0144	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0145	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0146	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0147	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0148	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0149	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0150	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0151	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0152	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0153	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0154	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0155	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0156	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0157	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0158	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0159	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0160	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0161	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0162	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0163	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0164	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0165	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0166	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0167	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0168	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0169	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0170	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0171	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0172	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0173	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0174	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0175	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0176	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0177	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0178	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0179	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0180	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0181	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0182	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0183	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0184	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0185	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0186	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0187	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0188	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0189	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0190	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0191	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0192	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0193	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0194	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0195	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0196	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0197	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0198	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0199	false	not_pair_mappable
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	CAND-0200	false	not_pair_mappable
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_gap_update (run_id, gap_key, gap_status, why_needed, update_note) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	gap_key	gap_status	why_needed	update_note
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	independent_lag_variable_artifact	open_candidate_scout_completed	Need non-alias lag variable with lineage.	candidate_artifacts_require_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	physical_proxy_source_artifact	open_candidate_scout_completed	Need mappable physical proxy source values.	candidate_sources_require_mapping_review
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	proxy_independence_criteria	open_requires_design	Need criteria distinguishing proxy from lag alias.	deep_research_or_design_criteria_required
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	phase_response_alias_review	high_priority	Phase response appears alias-like against abs_lag.	alias_review_required
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	source_lineage_for_candidate_variables	open_requires_lineage_review	Need source lineage for candidate variables.	lineage_repair_or_review_required
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_deep_research_handoff (run_id, question_id, handoff_question, evidence_status) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	question_id	handoff_question	evidence_status
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	DRQ-001	Welche formalen Kriterien unterscheiden eine unabhängige Lag-Variable von einem Alias von |j-i|?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	DRQ-002	Welche mathematischen Strukturen sind für lag-dominierte Matrizen relevant?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	DRQ-003	Welche Kriterien gelten für Shift-/Translations-/Toeplitz-Strukturen?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	DRQ-004	Welche physikalischen Proxy-Größen wären bei Moden-, Phasen-, Energie- oder Impulsstrukturen methodisch zulässig?	question_only_no_deep_research_answer
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	DRQ-005	Welche Reviewer-Einwände entstehen bei Proxy-Korrelationen?	question_only_no_deep_research_answer
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_claim_boundaries (run_id, claim_key, claim_text, status, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	claim_key	claim_text	status	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-001	QSB is physically validated	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-002	PBR exists physically	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-003	six lag axes are spacetime dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-004	spacetime emergence is proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-005	empirical validation exists	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-006	lag classes are physical dimensions	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-007	lag mechanism is physically proven	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-008	candidate artifact proves independent lag mechanism	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-009	candidate artifact proves physical proxy	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-010	DWH presence alone proves independence	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-011	repo presence alone proves independence	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-012	literature note alone proves proxy for current matrix	blocked	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	BLOCK-013	phase-response values are independent lag variables despite alias assessment	blocked	blocked_no_physics_claim
\.

COPY qsb_planck_bridge.pbr_input_artifact_enrichment_next_gate (run_id, next_gate, secondary_next_gate, execution_authorization, physical_claim_release) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	next_gate	secondary_next_gate	execution_authorization	physical_claim_release
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	independent_lag_variable_design_required	deep_research_criteria_review_required	not_authorized_in_this_scout_run	blocked_no_physics_claim
\.
-- BEGIN generated validation results import
DELETE FROM qsb_planck_bridge.pbr_input_artifact_enrichment_validation WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
COPY qsb_planck_bridge.pbr_input_artifact_enrichment_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
run_id	check_name	status	detail
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	run_directory_name	PASS	/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/runs/QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	required_files_exist	PASS	all_required_files_present
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	utf8_lf_files	PASS	all_required_text_files_utf8_lf
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	summary_run_id_exact	PASS	QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	summary_run_type	PASS	dwh_repo_artifact_scout
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	execution_status	PASS	executed
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	physical_claim_release_blocked	PASS	blocked_no_physics_claim
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	dwh_status_recorded	PASS	executed
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	candidate_inventory_present	PASS	candidate_rows=260
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	no_confirmed_independence_or_physical_proxy	PASS	no_forbidden_confirmations
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	presence_alone_not_treated_as_proof	PASS	no_presence_as_proof
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	all_proxy_families_represented	PASS	all_proxy_families_present
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	proxy_rows_candidate_only	PASS	all_proxy_rows_candidate_only
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	phase_response_alias_risk_high	PASS	phase_rows=51
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	gap_update_present	PASS	gap_rows=5
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	deep_research_handoff_questions_only	PASS	question_rows=5
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	target_run_id_verified	PASS	QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	no_lag_mechanism_tests_executed	PASS	True
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	no_nullmodels_executed	PASS	True
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	claim_boundaries_block_forbidden_claims	PASS	claim_rows=13
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	german_view_created	PASS	view_name_present
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	sql_copy_tables_present	PASS	required_copy_tables_present
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	forbidden_phrases_only_in_blocked_context	PASS	no_unblocked_forbidden_phrase_hits
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	working_tree_scope	PASS	only_scout_run_plus_pre_existing_review_modifications
QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01	pre_existing_review_modifications_reported	PASS	 M runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01/data/lag_mechanism_execution_review_summary.csv| M runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01/sql/002_insert_qsb_pbr_lag_mechanism_execution_result_review.sql
\.
-- END generated validation results import
COMMIT;
