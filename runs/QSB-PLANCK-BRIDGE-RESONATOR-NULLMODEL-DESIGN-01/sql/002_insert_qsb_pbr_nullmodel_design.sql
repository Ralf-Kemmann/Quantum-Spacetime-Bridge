-- Import CSV artifacts for QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01.
    -- Run from repository root after 001_create_qsb_pbr_nullmodel_design.sql.

    \set ON_ERROR_STOP on
    BEGIN;

    DELETE FROM qsb_planck_bridge.pbr_nullmodel_validation_results WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_execution_authorization WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_failure_modes WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_diagnostics_required WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_gate_decision WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_input_artifact_requirements WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_claim_boundaries WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_family_spec WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';
    DELETE FROM qsb_planck_bridge.pbr_nullmodel_design_summary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';

    \copy qsb_planck_bridge.pbr_nullmodel_design_summary (run_id, previous_run_id, design_status, execution_status, claim_status, physical_claim_release, external_readiness, next_gate, schema_name, nullmodel_family_count, formal_reference_finding) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_design_summary.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_family_spec (run_id, nullmodel_id, nullmodel_key, purpose, preserved_quantities, randomized_quantities, expected_diagnostic_outputs, admissibility_criteria, failure_modes, required_input_artifacts, execution_authorization_status, claim_boundary, next_gate_implication) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_family_spec.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_claim_boundaries (run_id, boundary_id, claim_key, status, claim_boundary_text) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/claim_boundaries.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_input_artifact_requirements (run_id, artifact_id, artifact_key, required_path, required_for, status) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/input_artifact_requirements.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_gate_decision (run_id, gate_id, gate_name, gate_decision, execution_status, physical_claim_release, external_readiness, next_gate, revision_trigger) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/gate_decision.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_diagnostics_required (run_id, nullmodel_key, diagnostic_key, required, execution_status, output_claim_status) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_diagnostics_required.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_failure_modes (run_id, nullmodel_key, failure_mode_id, failure_mode, mitigation_status) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_failure_modes.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_execution_authorization (run_id, nullmodel_key, execution_authorization_status, authorization_note, required_before_execution) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_execution_authorization.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_validation_results (run_id, validation_id, check_name, status, severity, observed_value, expected_value, message, blocking) FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/validation/validation_results.csv' WITH (FORMAT csv, HEADER true)

    COMMIT;
