-- QSB Planck-Bridge Resonator PSD Test 01 import
-- Usage:
-- Run from repository root:
-- psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/sql/002_insert_qsb_pbr_psd_test.sql

BEGIN;

CREATE TEMP TABLE tmp_pbr_psd_test_eigenvalue_report (
    metric text NOT NULL,
    value text NOT NULL
) ON COMMIT DROP;

DELETE FROM qsb_planck_bridge.pbr_psd_test_run
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01';

INSERT INTO qsb_planck_bridge.pbr_psd_test_run (
    run_id,
    work_package,
    created_date,
    state_spec_run_id,
    purpose,
    claim_status,
    physical_claim_release,
    review_status,
    tolerance,
    matrix_source,
    validation_source
) VALUES (
    'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01',
    'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01',
    '2026-07-06',
    'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01',
    'Re-evaluate the existing K_candidate matrix under the PBR-State-Spec Gram/PSD admissibility gate.',
    'formal_admissibility_result_only',
    'blocked_no_physics_claim',
    'requires_human_review',
    1e-10,
    'runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv',
    'runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv'
);

\copy qsb_planck_bridge.pbr_psd_test_input_lineage (run_id,input_id,source_path,sha256,expected_sha256,hash_match,lineage_bundle_sha256) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/data/input_lineage.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_psd_test_gate_result (result_id,run_id,input_id,matrix_sha256,prior_validation_sha256,lineage_bundle_sha256,n,is_square,is_symmetric,max_symmetry_deviation,min_diagonal,max_diagonal_deviation,lambda_min,lambda_max,negative_eigenvalue_count,negative_eigenvalue_mass,tolerance,psd_pass,admissibility_result,claim_status,physical_claim_release) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/results/psd_gate_result.csv' WITH (FORMAT csv, HEADER true)
\copy tmp_pbr_psd_test_eigenvalue_report (metric,value) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/results/eigenvalue_report.csv' WITH (FORMAT csv, HEADER true)
INSERT INTO qsb_planck_bridge.pbr_psd_test_eigenvalue_report (run_id, metric, value)
SELECT 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01', metric, value
FROM tmp_pbr_psd_test_eigenvalue_report;
\copy qsb_planck_bridge.pbr_psd_test_claim_boundary (run_id,boundary_id,boundary_type,claim_status,physical_claim_release,review_status,claim_text,release_status,rationale) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/data/claim_boundaries.csv' WITH (FORMAT csv, HEADER true)

COMMIT;
