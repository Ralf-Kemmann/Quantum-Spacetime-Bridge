-- QSB Planck-Bridge Resonator Result Review 01

CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_run (
    review_run_id text PRIMARY KEY,
    work_package text NOT NULL,
    created_date date NOT NULL,
    review_status text NOT NULL,
    review_outcome text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    external_readiness text NOT NULL,
    next_gate text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_input_lineage (
    review_run_id text REFERENCES qsb_planck_bridge.pbr_result_review_run(review_run_id) ON DELETE CASCADE,
    input_run_id text NOT NULL,
    input_path text NOT NULL,
    present boolean NOT NULL,
    role text NOT NULL,
    PRIMARY KEY (review_run_id, input_run_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_summary (
    review_id text NOT NULL,
    review_run_id text REFERENCES qsb_planck_bridge.pbr_result_review_run(review_run_id) ON DELETE CASCADE,
    state_spec_run_present boolean NOT NULL,
    psd_test_run_present boolean NOT NULL,
    spectral_readout_run_present boolean NOT NULL,
    psd_pass boolean NOT NULL,
    spectral_rank integer NOT NULL,
    spectral_nullity integer NOT NULL,
    parallel_count integer NOT NULL,
    antiparallel_count integer NOT NULL,
    formal_chain_status text NOT NULL,
    review_outcome text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    external_readiness text NOT NULL,
    next_gate text NOT NULL,
    review_status text NOT NULL,
    PRIMARY KEY (review_run_id, review_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_formal_finding (
    review_run_id text REFERENCES qsb_planck_bridge.pbr_result_review_run(review_run_id) ON DELETE CASCADE,
    finding_id text NOT NULL,
    finding_class text NOT NULL,
    finding_text text NOT NULL,
    evidence_ref text NOT NULL,
    claim_status text NOT NULL,
    PRIMARY KEY (review_run_id, finding_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_construction_bound_finding (
    review_run_id text REFERENCES qsb_planck_bridge.pbr_result_review_run(review_run_id) ON DELETE CASCADE,
    finding_id text NOT NULL,
    finding_class text NOT NULL,
    finding_text text NOT NULL,
    physical_claim_release text NOT NULL,
    PRIMARY KEY (review_run_id, finding_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_blocked_claim (
    review_run_id text REFERENCES qsb_planck_bridge.pbr_result_review_run(review_run_id) ON DELETE CASCADE,
    blocked_claim_id text NOT NULL,
    blocked_claim_key text NOT NULL,
    claim_text text NOT NULL,
    physical_claim_release text NOT NULL,
    release_status text NOT NULL,
    PRIMARY KEY (review_run_id, blocked_claim_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_next_test (
    review_run_id text REFERENCES qsb_planck_bridge.pbr_result_review_run(review_run_id) ON DELETE CASCADE,
    test_id text NOT NULL,
    test_key text NOT NULL,
    test_class text NOT NULL,
    recommendation text NOT NULL,
    next_gate text NOT NULL,
    PRIMARY KEY (review_run_id, test_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_result_review_external_readiness (
    review_run_id text REFERENCES qsb_planck_bridge.pbr_result_review_run(review_run_id) ON DELETE CASCADE,
    item_id text NOT NULL,
    communication_item text NOT NULL,
    readiness text NOT NULL,
    wording_or_rationale text NOT NULL,
    PRIMARY KEY (review_run_id, item_id)
);

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_result_review01_summary AS
SELECT *
FROM qsb_planck_bridge.pbr_result_review_summary
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_result_review01_formal_findings AS
SELECT *
FROM qsb_planck_bridge.pbr_result_review_formal_finding
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_result_review01_construction_bound_findings AS
SELECT *
FROM qsb_planck_bridge.pbr_result_review_construction_bound_finding
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_result_review01_blocked_claims AS
SELECT *
FROM qsb_planck_bridge.pbr_result_review_blocked_claim
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_result_review01_next_tests AS
SELECT *
FROM qsb_planck_bridge.pbr_result_review_next_test
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_result_review01_external_readiness AS
SELECT *
FROM qsb_planck_bridge.pbr_result_review_external_readiness
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';
