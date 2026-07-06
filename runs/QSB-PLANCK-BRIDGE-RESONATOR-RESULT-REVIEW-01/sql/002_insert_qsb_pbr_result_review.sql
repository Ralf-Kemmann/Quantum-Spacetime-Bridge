-- QSB Planck-Bridge Resonator Result Review 01 import
-- Run from repository root.

BEGIN;

DELETE FROM qsb_planck_bridge.pbr_result_review_run
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

INSERT INTO qsb_planck_bridge.pbr_result_review_run (
    review_run_id,
    work_package,
    created_date,
    review_status,
    review_outcome,
    claim_status,
    physical_claim_release,
    external_readiness,
    next_gate
) VALUES (
    'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01',
    'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01',
    '2026-07-06',
    'reviewed_formal_chain_requires_nullmodels',
    'formal_chain_complete_for_current_matrix__not_physics_validated',
    'result_review_only',
    'blocked_no_physics_claim',
    'internal_only_or_careful_methods_note',
    'nullmodel_design_required'
);

\copy qsb_planck_bridge.pbr_result_review_input_lineage (review_run_id,input_run_id,input_path,present,role) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/data/input_run_lineage.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_result_review_summary (review_id,review_run_id,state_spec_run_present,psd_test_run_present,spectral_readout_run_present,psd_pass,spectral_rank,spectral_nullity,parallel_count,antiparallel_count,formal_chain_status,review_outcome,claim_status,physical_claim_release,external_readiness,next_gate,review_status) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/data/result_review_summary.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_result_review_formal_finding (review_run_id,finding_id,finding_class,finding_text,evidence_ref,claim_status) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/data/formal_findings.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_result_review_construction_bound_finding (review_run_id,finding_id,finding_class,finding_text,physical_claim_release) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/data/construction_bound_findings.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_result_review_blocked_claim (review_run_id,blocked_claim_id,blocked_claim_key,claim_text,physical_claim_release,release_status) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/data/blocked_claims.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_result_review_next_test (review_run_id,test_id,test_key,test_class,recommendation,next_gate) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/data/recommended_next_tests.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_result_review_external_readiness (review_run_id,item_id,communication_item,readiness,wording_or_rationale) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01/data/external_communication_readiness.csv' WITH (FORMAT csv, HEADER true)

COMMIT;
