-- Import CSV artifacts for QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01.
    -- Run from repository root after 001_create_qsb_pbr_nullmodel_design.sql.

    \copy qsb_planck_bridge.pbr_nullmodel_design_summary FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_design_summary.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_family_spec FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_family_spec.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_claim_boundaries FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/claim_boundaries.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_input_artifact_requirements FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/input_artifact_requirements.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_gate_decision FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/gate_decision.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_diagnostics_required FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_diagnostics_required.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_failure_modes FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_failure_modes.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_execution_authorization FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/data/nullmodel_execution_authorization.csv' WITH (FORMAT csv, HEADER true)
    \copy qsb_planck_bridge.pbr_nullmodel_validation_results FROM 'runs/QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01/validation/validation_results.csv' WITH (FORMAT csv, HEADER true)
