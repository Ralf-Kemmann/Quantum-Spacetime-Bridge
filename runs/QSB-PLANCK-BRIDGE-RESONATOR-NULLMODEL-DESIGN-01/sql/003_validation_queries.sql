-- Validation queries for QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01.

    SELECT run_id, design_status, execution_status, physical_claim_release, external_readiness, next_gate
    FROM qsb_planck_bridge.pbr_nullmodel_design_summary
    WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01';

    SELECT nullmodel_key, count(*) AS rows
    FROM qsb_planck_bridge.pbr_nullmodel_family_spec
    WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01'
    GROUP BY nullmodel_key
    ORDER BY nullmodel_key;

    SELECT status, count(*) AS checks
    FROM qsb_planck_bridge.pbr_nullmodel_validation_results
    GROUP BY status
    ORDER BY status;

    SELECT *
    FROM qsb_planck_bridge.pbr_nullmodel_claim_boundaries
    WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01'
    ORDER BY boundary_id;
