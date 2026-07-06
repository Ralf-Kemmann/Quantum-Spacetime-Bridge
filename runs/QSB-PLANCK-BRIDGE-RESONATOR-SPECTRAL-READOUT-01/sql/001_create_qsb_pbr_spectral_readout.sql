-- QSB Planck-Bridge Resonator Spectral Readout 01

CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_run (
    run_id text PRIMARY KEY,
    work_package text NOT NULL,
    created_date date NOT NULL,
    purpose text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL,
    matrix_source text NOT NULL,
    prior_psd_validation_source text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_input_lineage (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    input_id text NOT NULL,
    source_path text NOT NULL,
    sha256 text NOT NULL,
    expected_sha256 text NOT NULL,
    hash_match boolean NOT NULL,
    lineage_bundle_sha256 text NOT NULL,
    PRIMARY KEY (run_id, input_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_result (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    input_id text NOT NULL,
    matrix_sha256 text NOT NULL,
    prior_psd_validation_sha256 text NOT NULL,
    lineage_bundle_sha256 text NOT NULL,
    n_rows integer NOT NULL,
    n_columns integer NOT NULL,
    all_values_finite boolean NOT NULL,
    symmetry_max_deviation numeric NOT NULL,
    diagonal_max_deviation_from_one numeric NOT NULL,
    trace numeric NOT NULL,
    rank_tol_1e_10 integer NOT NULL,
    nullity integer NOT NULL,
    positive_eigenvalue_sum numeric NOT NULL,
    lambda_min numeric NOT NULL,
    lambda_max numeric NOT NULL,
    negative_eigenvalue_count integer NOT NULL,
    negative_eigenvalue_mass numeric NOT NULL,
    tolerance numeric NOT NULL,
    psd_pass boolean NOT NULL,
    admissibility_result text NOT NULL,
    parallel_count integer NOT NULL,
    antiparallel_count integer NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL,
    PRIMARY KEY (run_id, input_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_eigenvalue_mass (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    component_rank_desc integer NOT NULL,
    eigenvalue numeric NOT NULL,
    fraction_of_trace numeric NOT NULL,
    tolerance numeric NOT NULL,
    PRIMARY KEY (run_id, component_rank_desc)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_lag_class_summary (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    lag_axis text NOT NULL,
    abs_lag integer NOT NULL,
    positive_direction_count integer NOT NULL,
    negative_direction_count integer NOT NULL,
    total_count integer NOT NULL,
    expected_positive_count integer NOT NULL,
    expected_negative_count integer NOT NULL,
    expected_total_count integer NOT NULL,
    class_size_check boolean NOT NULL,
    PRIMARY KEY (run_id, lag_axis)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_parallel_counts (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    metric text NOT NULL,
    observed_count integer NOT NULL,
    expected_count integer NOT NULL,
    status text NOT NULL,
    definition text NOT NULL,
    PRIMARY KEY (run_id, metric)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_lag_class_membership (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    pair_id text NOT NULL,
    i integer NOT NULL,
    j integer NOT NULL,
    lag integer NOT NULL,
    abs_lag integer NOT NULL,
    direction text NOT NULL,
    lag_axis text NOT NULL,
    PRIMARY KEY (run_id, pair_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_relation_pair (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    relation_type text NOT NULL,
    pair_id_a text NOT NULL,
    pair_id_b text NOT NULL,
    row_index integer NOT NULL,
    column_index integer NOT NULL,
    k_candidate numeric NOT NULL,
    PRIMARY KEY (run_id, relation_type, pair_id_a, pair_id_b)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_effective_lag_axis_gram (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    lag_axis text NOT NULL,
    representative_pair_id text NOT NULL,
    l1 numeric NOT NULL,
    l2 numeric NOT NULL,
    l3 numeric NOT NULL,
    l4 numeric NOT NULL,
    l5 numeric NOT NULL,
    l6 numeric NOT NULL,
    PRIMARY KEY (run_id, lag_axis)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_spectral_readout_claim_boundary (
    run_id text REFERENCES qsb_planck_bridge.pbr_spectral_readout_run(run_id) ON DELETE CASCADE,
    boundary_id text NOT NULL,
    boundary_type text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL,
    claim_text text NOT NULL,
    release_status text NOT NULL,
    rationale text NOT NULL,
    PRIMARY KEY (run_id, boundary_id)
);

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_spectral_readout01_summary AS
SELECT
    r.run_id,
    r.claim_status,
    r.physical_claim_release,
    r.review_status,
    s.n_rows,
    s.n_columns,
    s.trace,
    s.rank_tol_1e_10,
    s.nullity,
    s.lambda_min,
    s.lambda_max,
    s.positive_eigenvalue_sum,
    s.parallel_count,
    s.antiparallel_count,
    s.admissibility_result
FROM qsb_planck_bridge.pbr_spectral_readout_run r
JOIN qsb_planck_bridge.pbr_spectral_readout_result s ON s.run_id = r.run_id
WHERE r.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_spectral_readout01_lag_class_summary AS
SELECT *
FROM qsb_planck_bridge.pbr_spectral_readout_lag_class_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_spectral_readout01_parallel_counts AS
SELECT *
FROM qsb_planck_bridge.pbr_spectral_readout_parallel_counts
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_spectral_readout01_claim_boundary AS
SELECT *
FROM qsb_planck_bridge.pbr_spectral_readout_claim_boundary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

