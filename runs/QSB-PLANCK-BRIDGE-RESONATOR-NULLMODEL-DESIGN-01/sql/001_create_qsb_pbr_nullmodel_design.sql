-- QSB Planck Bridge Resonator Nullmodel Design 01

    CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_design_summary (
        run_id text PRIMARY KEY,
        previous_run_id text NOT NULL,
        design_status text NOT NULL,
        execution_status text NOT NULL,
        claim_status text NOT NULL,
        physical_claim_release text NOT NULL,
        external_readiness text NOT NULL,
        next_gate text NOT NULL,
        schema_name text NOT NULL,
        nullmodel_family_count integer NOT NULL,
        formal_reference_finding text NOT NULL
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_family_spec (
        run_id text NOT NULL,
        nullmodel_id text NOT NULL,
        nullmodel_key text NOT NULL,
        purpose text NOT NULL,
        preserved_quantities text NOT NULL,
        randomized_quantities text NOT NULL,
        expected_diagnostic_outputs text NOT NULL,
        admissibility_criteria text NOT NULL,
        failure_modes text NOT NULL,
        required_input_artifacts text NOT NULL,
        execution_authorization_status text NOT NULL,
        claim_boundary text NOT NULL,
        next_gate_implication text NOT NULL,
        PRIMARY KEY (run_id, nullmodel_id)
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_claim_boundaries (
        run_id text NOT NULL,
        boundary_id text NOT NULL,
        claim_key text NOT NULL,
        status text NOT NULL,
        claim_boundary_text text NOT NULL,
        PRIMARY KEY (run_id, boundary_id)
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_input_artifact_requirements (
        run_id text NOT NULL,
        artifact_id text NOT NULL,
        artifact_key text NOT NULL,
        required_path text NOT NULL,
        required_for text NOT NULL,
        status text NOT NULL,
        PRIMARY KEY (run_id, artifact_id)
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_gate_decision (
        run_id text NOT NULL,
        gate_id text NOT NULL,
        gate_name text NOT NULL,
        gate_decision text NOT NULL,
        execution_status text NOT NULL,
        physical_claim_release text NOT NULL,
        external_readiness text NOT NULL,
        next_gate text NOT NULL,
        revision_trigger text NOT NULL,
        PRIMARY KEY (run_id, gate_id)
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_diagnostics_required (
        run_id text NOT NULL,
        nullmodel_key text NOT NULL,
        diagnostic_key text NOT NULL,
        required boolean NOT NULL,
        execution_status text NOT NULL,
        output_claim_status text NOT NULL,
        PRIMARY KEY (run_id, nullmodel_key, diagnostic_key)
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_failure_modes (
        run_id text NOT NULL,
        nullmodel_key text NOT NULL,
        failure_mode_id text NOT NULL,
        failure_mode text NOT NULL,
        mitigation_status text NOT NULL,
        PRIMARY KEY (run_id, failure_mode_id)
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_authorization (
        run_id text NOT NULL,
        nullmodel_key text NOT NULL,
        execution_authorization_status text NOT NULL,
        authorization_note text NOT NULL,
        required_before_execution text NOT NULL,
        PRIMARY KEY (run_id, nullmodel_key)
    );

    CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_validation_results (
        run_id text NOT NULL,
        validation_id text NOT NULL,
        check_name text NOT NULL,
        status text NOT NULL,
        severity text NOT NULL,
        observed_value text NOT NULL,
        expected_value text NOT NULL,
        message text NOT NULL,
        blocking text NOT NULL,
        PRIMARY KEY (run_id, validation_id)
    );

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_design_summary
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_family_spec
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_family_spec
        ADD COLUMN IF NOT EXISTS next_gate_implication text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_claim_boundaries
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_input_artifact_requirements
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_gate_decision
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_diagnostics_required
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_failure_modes
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_execution_authorization
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE qsb_planck_bridge.pbr_nullmodel_validation_results
        ADD COLUMN IF NOT EXISTS run_id text;

    UPDATE qsb_planck_bridge.pbr_nullmodel_validation_results
    SET run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01'
    WHERE run_id IS NULL;
