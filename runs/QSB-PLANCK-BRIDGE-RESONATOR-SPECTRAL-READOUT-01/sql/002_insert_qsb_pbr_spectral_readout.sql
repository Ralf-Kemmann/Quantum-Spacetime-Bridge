-- QSB Planck-Bridge Resonator Spectral Readout 01 import
-- Run from repository root:
-- psql -d qsb_research_dwh -f runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/sql/002_insert_qsb_pbr_spectral_readout.sql

BEGIN;

DELETE FROM qsb_planck_bridge.pbr_spectral_readout_run
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

INSERT INTO qsb_planck_bridge.pbr_spectral_readout_run (
    run_id,
    work_package,
    created_date,
    purpose,
    claim_status,
    physical_claim_release,
    review_status,
    matrix_source,
    prior_psd_validation_source
) VALUES (
    'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01',
    'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01',
    '2026-07-06',
    'Perform a formal spectral readout of the existing K_candidate matrix after the PSD gate has passed.',
    'formal_matrix_structure_readout_only',
    'blocked_no_physics_claim',
    'requires_human_review',
    'runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv',
    'runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv'
);

\copy qsb_planck_bridge.pbr_spectral_readout_input_lineage (run_id,input_id,source_path,sha256,expected_sha256,hash_match,lineage_bundle_sha256) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/data/input_lineage.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_result (run_id,input_id,matrix_sha256,prior_psd_validation_sha256,lineage_bundle_sha256,n_rows,n_columns,all_values_finite,symmetry_max_deviation,diagonal_max_deviation_from_one,trace,rank_tol_1e_10,nullity,positive_eigenvalue_sum,lambda_min,lambda_max,negative_eigenvalue_count,negative_eigenvalue_mass,tolerance,psd_pass,admissibility_result,parallel_count,antiparallel_count,claim_status,physical_claim_release,review_status) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/data/spectral_readout_result.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_eigenvalue_mass (run_id,component_rank_desc,eigenvalue,fraction_of_trace,tolerance) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/data/eigenvalue_mass_report.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_lag_class_summary (run_id,lag_axis,abs_lag,positive_direction_count,negative_direction_count,total_count,expected_positive_count,expected_negative_count,expected_total_count,class_size_check) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/data/lag_class_summary.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_parallel_counts (run_id,metric,observed_count,expected_count,status,definition) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/data/parallel_antiparallel_counts.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_lag_class_membership (run_id,pair_id,i,j,lag,abs_lag,direction,lag_axis) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/results/lag_class_membership.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_relation_pair (run_id,pair_id_a,pair_id_b,row_index,column_index,k_candidate,relation_type) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/results/parallel_pairs.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_relation_pair (run_id,pair_id_a,pair_id_b,row_index,column_index,k_candidate,relation_type) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/results/antiparallel_pairs.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_effective_lag_axis_gram (run_id,lag_axis,representative_pair_id,l1,l2,l3,l4,l5,l6) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/results/effective_lag_axis_gram.csv' WITH (FORMAT csv, HEADER true)
\copy qsb_planck_bridge.pbr_spectral_readout_claim_boundary (run_id,boundary_id,boundary_type,claim_status,physical_claim_release,review_status,claim_text,release_status,rationale) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01/data/claim_boundaries.csv' WITH (FORMAT csv, HEADER true)

COMMIT;

