-- QSB Planck-Bridge Resonator PSD Test 01
-- Schema, tables, and views

CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_psd_test_run (
    run_id text PRIMARY KEY,
    work_package text NOT NULL,
    created_date date NOT NULL,
    state_spec_run_id text NOT NULL,
    purpose text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL,
    tolerance numeric NOT NULL,
    matrix_source text NOT NULL,
    validation_source text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_psd_test_input_lineage (
    run_id text REFERENCES qsb_planck_bridge.pbr_psd_test_run(run_id) ON DELETE CASCADE,
    input_id text NOT NULL,
    source_path text NOT NULL,
    sha256 text NOT NULL,
    expected_sha256 text NOT NULL,
    hash_match boolean NOT NULL,
    lineage_bundle_sha256 text NOT NULL,
    PRIMARY KEY (run_id, input_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_psd_test_gate_result (
    run_id text REFERENCES qsb_planck_bridge.pbr_psd_test_run(run_id) ON DELETE CASCADE,
    result_id text NOT NULL,
    input_id text NOT NULL,
    matrix_sha256 text NOT NULL,
    prior_validation_sha256 text NOT NULL,
    lineage_bundle_sha256 text NOT NULL,
    n integer NOT NULL,
    is_square boolean NOT NULL,
    is_symmetric boolean NOT NULL,
    max_symmetry_deviation numeric NOT NULL,
    min_diagonal numeric NOT NULL,
    max_diagonal_deviation numeric NOT NULL,
    lambda_min numeric NOT NULL,
    lambda_max numeric NOT NULL,
    negative_eigenvalue_count integer NOT NULL,
    negative_eigenvalue_mass numeric NOT NULL,
    tolerance numeric NOT NULL,
    psd_pass boolean NOT NULL,
    admissibility_result text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    PRIMARY KEY (run_id, result_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_psd_test_eigenvalue_report (
    run_id text REFERENCES qsb_planck_bridge.pbr_psd_test_run(run_id) ON DELETE CASCADE,
    metric text NOT NULL,
    value text NOT NULL,
    PRIMARY KEY (run_id, metric)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_psd_test_claim_boundary (
    run_id text REFERENCES qsb_planck_bridge.pbr_psd_test_run(run_id) ON DELETE CASCADE,
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

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'qsb_planck_bridge'
          AND table_name = 'pbr_psd_test_gate_result'
          AND column_name = 'matrix_id'
    ) THEN
        ALTER TABLE qsb_planck_bridge.pbr_psd_test_gate_result
            DROP CONSTRAINT IF EXISTS pbr_psd_test_gate_result_pkey,
            ALTER COLUMN matrix_id DROP NOT NULL,
            ALTER COLUMN matrix_source DROP NOT NULL,
            ALTER COLUMN state_spec_run_id DROP NOT NULL,
            ALTER COLUMN n_rows DROP NOT NULL,
            ALTER COLUMN n_columns DROP NOT NULL,
            ALTER COLUMN all_values_finite DROP NOT NULL,
            ALTER COLUMN symmetry_max_deviation DROP NOT NULL,
            ALTER COLUMN diagonal_max_deviation_from_one DROP NOT NULL,
            ALTER COLUMN review_status DROP NOT NULL;
    END IF;
END $$;

ALTER TABLE qsb_planck_bridge.pbr_psd_test_gate_result
    ADD COLUMN IF NOT EXISTS result_id text,
    ADD COLUMN IF NOT EXISTS input_id text,
    ADD COLUMN IF NOT EXISTS matrix_sha256 text,
    ADD COLUMN IF NOT EXISTS prior_validation_sha256 text,
    ADD COLUMN IF NOT EXISTS lineage_bundle_sha256 text,
    ADD COLUMN IF NOT EXISTS n integer,
    ADD COLUMN IF NOT EXISTS is_symmetric boolean,
    ADD COLUMN IF NOT EXISTS max_symmetry_deviation numeric,
    ADD COLUMN IF NOT EXISTS min_diagonal numeric,
    ADD COLUMN IF NOT EXISTS max_diagonal_deviation numeric;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'pbr_psd_test_gate_result_pkey'
          AND conrelid = 'qsb_planck_bridge.pbr_psd_test_gate_result'::regclass
    ) THEN
        ALTER TABLE qsb_planck_bridge.pbr_psd_test_gate_result
            ADD CONSTRAINT pbr_psd_test_gate_result_pkey PRIMARY KEY (run_id, result_id);
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'qsb_planck_bridge'
          AND table_name = 'pbr_psd_test_eigenvalue_report'
          AND column_name = 'matrix_id'
    ) THEN
        ALTER TABLE qsb_planck_bridge.pbr_psd_test_eigenvalue_report
            DROP CONSTRAINT IF EXISTS pbr_psd_test_eigenvalue_report_pkey,
            ALTER COLUMN matrix_id DROP NOT NULL,
            ALTER COLUMN eigenvalue_index DROP NOT NULL,
            ALTER COLUMN eigenvalue DROP NOT NULL,
            ALTER COLUMN below_negative_tolerance DROP NOT NULL,
            ALTER COLUMN tolerance DROP NOT NULL;
    END IF;
END $$;

ALTER TABLE qsb_planck_bridge.pbr_psd_test_eigenvalue_report
    ADD COLUMN IF NOT EXISTS metric text,
    ADD COLUMN IF NOT EXISTS value text;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'pbr_psd_test_eigenvalue_report_pkey'
          AND conrelid = 'qsb_planck_bridge.pbr_psd_test_eigenvalue_report'::regclass
    ) THEN
        ALTER TABLE qsb_planck_bridge.pbr_psd_test_eigenvalue_report
            ADD CONSTRAINT pbr_psd_test_eigenvalue_report_pkey PRIMARY KEY (run_id, metric);
    END IF;
END $$;

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_psd_test01_summary AS
SELECT
    r.run_id,
    r.work_package,
    r.state_spec_run_id,
    r.claim_status,
    r.physical_claim_release,
    r.review_status,
    r.tolerance,
    g.input_id,
    g.n,
    g.is_square,
    g.is_symmetric,
    g.max_symmetry_deviation,
    g.min_diagonal,
    g.max_diagonal_deviation,
    g.lambda_min,
    g.lambda_max,
    g.negative_eigenvalue_count,
    g.negative_eigenvalue_mass,
    g.psd_pass,
    g.admissibility_result,
    COUNT(DISTINCT l.input_id) FILTER (WHERE l.hash_match) AS matching_input_hashes,
    COUNT(DISTINCT b.boundary_id) FILTER (WHERE b.boundary_type = 'blocked_claim') AS blocked_claims
FROM qsb_planck_bridge.pbr_psd_test_run r
LEFT JOIN qsb_planck_bridge.pbr_psd_test_gate_result g ON g.run_id = r.run_id
LEFT JOIN qsb_planck_bridge.pbr_psd_test_input_lineage l ON l.run_id = r.run_id
LEFT JOIN qsb_planck_bridge.pbr_psd_test_claim_boundary b ON b.run_id = r.run_id
WHERE r.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01'
GROUP BY r.run_id, r.work_package, r.state_spec_run_id, r.claim_status,
         r.physical_claim_release, r.review_status, r.tolerance, g.input_id,
         g.n, g.is_square, g.is_symmetric, g.max_symmetry_deviation,
         g.min_diagonal, g.max_diagonal_deviation, g.lambda_min, g.lambda_max,
         g.negative_eigenvalue_count, g.negative_eigenvalue_mass,
         g.psd_pass, g.admissibility_result;

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_psd_test01_gate_result AS
SELECT *
FROM qsb_planck_bridge.pbr_psd_test_gate_result
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_psd_test01_claim_boundary AS
SELECT *
FROM qsb_planck_bridge.pbr_psd_test_claim_boundary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01';
