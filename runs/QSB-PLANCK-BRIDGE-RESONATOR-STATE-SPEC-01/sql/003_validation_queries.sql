-- Validation queries for QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01

SELECT current_database() AS db, current_user AS db_user, current_schema() AS current_schema;

SELECT *
FROM qsb_planck_bridge.v_pbr_state_spec01_summary;

SELECT
    'run_exists' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_state_spec_run
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';

SELECT
    'required_local_fields_present' AS check_name,
    CASE WHEN COUNT(*) = 5 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_field_registry
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01'
  AND field_symbol IN ('H_i', 'Phi_i', 'M_i', 'gamma_i', 'sigma_i')
  AND required = 'yes';

SELECT
    'psd_gate_registered' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_admissibility_gate
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01'
  AND gate_id = 'GATE-PSD-01';

SELECT
    'psd_gate_fields_registered' AS check_name,
    CASE WHEN COUNT(*) >= 13 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_gate_spec
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';

SELECT
    'blocked_claims_present' AS check_name,
    CASE WHEN COUNT(*) >= 5 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_claim_boundary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01'
  AND boundary_type = 'blocked_claim';

SELECT
    'no_physics_claim_release' AS check_name,
    CASE WHEN COUNT(*) = 0 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS unsafe_count
FROM qsb_planck_bridge.pbr_claim_boundary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01'
  AND boundary_type = 'blocked_claim'
  AND release_status NOT LIKE 'blocked%';

SELECT *
FROM qsb_planck_bridge.v_pbr_state_spec01_claim_boundary
ORDER BY boundary_type, boundary_id;

SELECT *
FROM qsb_planck_bridge.v_pbr_state_spec01_psd_gate
ORDER BY field_name;
