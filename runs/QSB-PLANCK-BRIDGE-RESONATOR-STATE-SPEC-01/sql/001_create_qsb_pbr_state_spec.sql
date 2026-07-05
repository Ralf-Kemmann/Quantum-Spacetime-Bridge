-- QSB Planck-Bridge Resonator State Spec 01
-- Schema and views

CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_state_spec_run (
    run_id text PRIMARY KEY,
    work_package text NOT NULL,
    created_date date NOT NULL,
    artifact_type text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL,
    purpose text NOT NULL,
    core_object text NOT NULL,
    relational_coupling_general text NOT NULL,
    relational_coupling_minimal text NOT NULL,
    primary_gate text NOT NULL,
    recommended_next_work_package text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_minimal_object_definition (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    object_symbol text NOT NULL,
    object_definition text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    notes text,
    PRIMARY KEY (run_id, object_symbol)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_field_registry (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    field_symbol text NOT NULL,
    canonical_name text NOT NULL,
    field_role text NOT NULL,
    definition text NOT NULL,
    required text NOT NULL,
    claim_boundary text NOT NULL,
    PRIMARY KEY (run_id, field_symbol)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_concept_definition (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    concept text NOT NULL,
    definition text NOT NULL,
    allowed_interpretation text NOT NULL,
    blocked_interpretation text NOT NULL,
    PRIMARY KEY (run_id, concept)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_admissibility_gate (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    gate_id text NOT NULL,
    gate_name text NOT NULL,
    gate_scope text NOT NULL,
    required_condition text NOT NULL,
    pass_meaning text NOT NULL,
    fail_meaning text NOT NULL,
    claim_boundary text NOT NULL,
    PRIMARY KEY (run_id, gate_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_psd_gate_spec (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    field_name text NOT NULL,
    field_type text NOT NULL,
    required text NOT NULL,
    definition text NOT NULL,
    PRIMARY KEY (run_id, field_name)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_claim_boundary (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    boundary_id text NOT NULL,
    boundary_type text NOT NULL,
    claim_text text NOT NULL,
    release_status text NOT NULL,
    rationale text NOT NULL,
    PRIMARY KEY (run_id, boundary_id)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_external_suggestion_triage (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    source_label text NOT NULL,
    item text NOT NULL,
    triage_status text NOT NULL,
    rationale text NOT NULL,
    qsb_action text NOT NULL,
    PRIMARY KEY (run_id, source_label, item)
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_redteam_action_item (
    run_id text REFERENCES qsb_planck_bridge.pbr_state_spec_run(run_id) ON DELETE CASCADE,
    issue_id text NOT NULL,
    issue_class text NOT NULL,
    severity text NOT NULL,
    redteam_finding text NOT NULL,
    required_action text NOT NULL,
    status text NOT NULL,
    PRIMARY KEY (run_id, issue_id)
);

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_state_spec01_summary AS
SELECT
    r.run_id,
    r.work_package,
    r.artifact_type,
    r.physical_claim_release,
    r.review_status,
    r.core_object,
    r.relational_coupling_general,
    r.relational_coupling_minimal,
    r.primary_gate,
    COUNT(DISTINCT f.field_symbol) AS registered_fields,
    COUNT(DISTINCT g.gate_id) AS admissibility_gates,
    COUNT(DISTINCT b.boundary_id) FILTER (WHERE b.boundary_type = 'allowed_claim') AS allowed_claims,
    COUNT(DISTINCT b.boundary_id) FILTER (WHERE b.boundary_type = 'blocked_claim') AS blocked_claims
FROM qsb_planck_bridge.pbr_state_spec_run r
LEFT JOIN qsb_planck_bridge.pbr_field_registry f ON f.run_id = r.run_id
LEFT JOIN qsb_planck_bridge.pbr_admissibility_gate g ON g.run_id = r.run_id
LEFT JOIN qsb_planck_bridge.pbr_claim_boundary b ON b.run_id = r.run_id
WHERE r.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01'
GROUP BY r.run_id, r.work_package, r.artifact_type, r.physical_claim_release,
         r.review_status, r.core_object, r.relational_coupling_general,
         r.relational_coupling_minimal, r.primary_gate;

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_state_spec01_claim_boundary AS
SELECT
    run_id,
    boundary_id,
    boundary_type,
    claim_text,
    release_status,
    rationale
FROM qsb_planck_bridge.pbr_claim_boundary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_state_spec01_psd_gate AS
SELECT
    s.run_id,
    g.gate_id,
    g.gate_name,
    g.required_condition,
    g.pass_meaning,
    g.fail_meaning,
    p.field_name,
    p.field_type,
    p.required,
    p.definition
FROM qsb_planck_bridge.pbr_admissibility_gate g
JOIN qsb_planck_bridge.pbr_psd_gate_spec p ON p.run_id = g.run_id
JOIN qsb_planck_bridge.pbr_state_spec_run s ON s.run_id = g.run_id
WHERE g.gate_id = 'GATE-PSD-01'
  AND s.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';

CREATE OR REPLACE VIEW qsb_planck_bridge.v_pbr_state_spec01_redteam_actions AS
SELECT *
FROM qsb_planck_bridge.pbr_redteam_action_item
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
