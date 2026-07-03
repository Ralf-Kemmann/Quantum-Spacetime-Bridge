BEGIN;

CREATE SCHEMA IF NOT EXISTS qsb_scale_mapping;

CREATE TABLE IF NOT EXISTS qsb_scale_mapping.scale_mapping_run (
    run_id text PRIMARY KEY,
    work_package text NOT NULL,
    created_at date NOT NULL,
    note_version text NOT NULL,
    mapping_scope text NOT NULL,
    note_sha256 text NOT NULL,
    mapping_definition_count integer NOT NULL,
    variable_count integer NOT NULL,
    special_case_count integer NOT NULL,
    claim_boundary_count integer NOT NULL,
    dimensional_check_count integer NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL,
    claim_boundary text NOT NULL,
    inserted_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qsb_scale_mapping.mapping_definition (
    mapping_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES qsb_scale_mapping.scale_mapping_run(run_id),
    mapping_level integer NOT NULL,
    mapping_name text NOT NULL,
    mapping_formula text NOT NULL,
    mapping_condition text NOT NULL,
    qsb_interpretation text NOT NULL,
    dimensional_status text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_scale_mapping.variable_registry (
    variable_key text PRIMARY KEY,
    run_id text NOT NULL REFERENCES qsb_scale_mapping.scale_mapping_run(run_id),
    label text NOT NULL,
    dimension_vector text NOT NULL,
    definition_formula text NOT NULL,
    qsb_role text NOT NULL,
    physical_claim_release text NOT NULL DEFAULT 'blocked_no_physics_claim',
    review_status text NOT NULL DEFAULT 'requires_dimensional_and_physical_review'
);

CREATE TABLE IF NOT EXISTS qsb_scale_mapping.special_case (
    special_case_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES qsb_scale_mapping.scale_mapping_run(run_id),
    assumption text NOT NULL,
    derived_expression text NOT NULL,
    qsb_interpretation text NOT NULL,
    physical_claim_release text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_scale_mapping.claim_boundary (
    claim_boundary_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES qsb_scale_mapping.scale_mapping_run(run_id),
    scope_type text NOT NULL,
    scope_key text NOT NULL,
    allowed_claim text NOT NULL,
    forbidden_claim text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_scale_mapping.dimensional_check (
    check_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES qsb_scale_mapping.scale_mapping_run(run_id),
    expression text NOT NULL,
    expected_dimension text NOT NULL,
    actual_dimension text NOT NULL,
    status text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_scale_mapping.scale_mapping_validation_result (
    validation_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES qsb_scale_mapping.scale_mapping_run(run_id),
    validation_scope text NOT NULL,
    check_name text NOT NULL,
    expected_value text NOT NULL,
    actual_value text NOT NULL,
    passed boolean NOT NULL,
    severity text NOT NULL,
    created_at timestamptz DEFAULT now()
);

INSERT INTO qsb_scale_mapping.scale_mapping_run (
    run_id, work_package, created_at, note_version, mapping_scope, note_sha256,
    mapping_definition_count, variable_count, special_case_count, claim_boundary_count,
    dimensional_check_count, claim_status, physical_claim_release, review_status, claim_boundary
) VALUES (
    'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01', DATE '2026-07-03', 'v0.1',
    'compton_schwarzschild_scale_mapping_as_planck_bridge_gate', '31e6fa739f7e6912cd41346865e258cf7b900661449d0b7364682a291126d7ed',
    2, 14, 3, 4, 7,
    'scale_mapping_candidate', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review',
    'Scale mappings mark a formal bridge zone; they do not prove a Planck-Bridge-Resonator or redefine c.'
)
ON CONFLICT (run_id) DO UPDATE SET
    note_sha256 = EXCLUDED.note_sha256,
    mapping_definition_count = EXCLUDED.mapping_definition_count,
    variable_count = EXCLUDED.variable_count,
    special_case_count = EXCLUDED.special_case_count,
    claim_boundary_count = EXCLUDED.claim_boundary_count,
    dimensional_check_count = EXCLUDED.dimensional_check_count,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;

INSERT INTO qsb_scale_mapping.mapping_definition VALUES ('MAP-BETA-01','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01',1,'direct_compton_schwarzschild_scale_ratio_beta_B','beta_B = r_s / lambda_C = 2 * G * m^2 / (hbar * c)','beta_B approximately 1 marks the Compton-Schwarzschild scale gate','Measures how close the Compton localization scale and Schwarzschild radius scale are.','dimensionless_verified','scale_mapping_candidate','blocked_no_physics_claim','requires_dimensional_and_physical_review')
ON CONFLICT (mapping_id) DO UPDATE SET
    mapping_formula = EXCLUDED.mapping_formula,
    mapping_condition = EXCLUDED.mapping_condition,
    qsb_interpretation = EXCLUDED.qsb_interpretation,
    dimensional_status = EXCLUDED.dimensional_status,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;
INSERT INTO qsb_scale_mapping.mapping_definition VALUES ('MAP-XI-01','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01',2,'two_sided_speed_matching_Xi_CS','Xi_CS = c_comp^2 / c_schwarz^2 = hbar^2 * r_s / (2 * G * m_schwarz * m_comp^2 * lambda_C^2)','Xi_CS = 1 marks algebraic consistency of the two reconstructed speed scales','Separates Compton-side and Schwarzschild-side origin indices before checking bridge consistency.','dimensionless_verified','scale_mapping_candidate','blocked_no_physics_claim','requires_dimensional_and_physical_review')
ON CONFLICT (mapping_id) DO UPDATE SET
    mapping_formula = EXCLUDED.mapping_formula,
    mapping_condition = EXCLUDED.mapping_condition,
    qsb_interpretation = EXCLUDED.qsb_interpretation,
    dimensional_status = EXCLUDED.dimensional_status,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('lambda_C','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Compton scale / reduced Compton wavelength','L','hbar / (m * c)','length scale on quantum localization side')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('r_s','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Schwarzschild radius','L','2 * G * m / c^2','length scale on gravitational radius side')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('m','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','single mass parameter','M','m','mass used in direct ratio mapping')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('m_comp','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Compton-side mass marker','M','m_comp','mass indexed to the Compton-side reconstruction')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('m_schwarz','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Schwarzschild-side mass marker','M','m_schwarz','mass indexed to the Schwarzschild-side reconstruction')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('c','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','physical speed of light / reference speed','L T^-1','c','reference constant; not redefined')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('c_comp','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Compton-side reconstructed speed scale','L T^-1','hbar / (m_comp * lambda_C)','algebraic speed scale reconstructed from Compton side')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('c_schwarz','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Schwarzschild-side reconstructed speed scale','L T^-1','sqrt(2 * G * m_schwarz / r_s)','algebraic speed scale reconstructed from Schwarzschild side')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('beta_B','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','direct scale gate parameter','1','r_s / lambda_C','dimensionless proximity of length scales')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('Xi_CS','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','two-sided speed matching parameter','1','c_comp^2 / c_schwarz^2','dimensionless consistency of reconstructed speeds')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('L_B','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','bridge length special-case marker','L','hbar^2 / (2 * G * m_schwarz * m_comp^2)','length when lambda_C = r_s in two-sided mapping')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('m_B','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','bridge mass special-case marker','M','sqrt(hbar * c / (2 * G))','mass at exact direct scale matching')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('hbar','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','reduced Planck constant','M L^2 T^-1','hbar','fundamental constant')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.variable_registry (variable_key, run_id, label, dimension_vector, definition_formula, qsb_role)
VALUES ('G','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Newton gravitational constant','L^3 M^-1 T^-2','G','fundamental constant')
ON CONFLICT (variable_key) DO UPDATE SET
    label = EXCLUDED.label,
    dimension_vector = EXCLUDED.dimension_vector,
    definition_formula = EXCLUDED.definition_formula,
    qsb_role = EXCLUDED.qsb_role;
INSERT INTO qsb_scale_mapping.special_case VALUES ('SC-EQUAL-LENGTH','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','lambda_C = r_s = L_B','L_B = hbar^2 / (2 * G * m_schwarz * m_comp^2)','Bridge length depends on mass pair (m_comp, m_schwarz).','blocked_no_physics_claim')
ON CONFLICT (special_case_id) DO UPDATE SET
    assumption = EXCLUDED.assumption,
    derived_expression = EXCLUDED.derived_expression,
    qsb_interpretation = EXCLUDED.qsb_interpretation,
    physical_claim_release = EXCLUDED.physical_claim_release;
INSERT INTO qsb_scale_mapping.special_case VALUES ('SC-EQUAL-MASS','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','m_comp = m_schwarz = m','L_B = hbar^2 / (2 * G * m^3)','Collapses the two-origin mass mapping to a single-mass special case.','blocked_no_physics_claim')
ON CONFLICT (special_case_id) DO UPDATE SET
    assumption = EXCLUDED.assumption,
    derived_expression = EXCLUDED.derived_expression,
    qsb_interpretation = EXCLUDED.qsb_interpretation,
    physical_claim_release = EXCLUDED.physical_claim_release;
INSERT INTO qsb_scale_mapping.special_case VALUES ('SC-PLANCK-MATCHING','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','lambda_C = r_s and c is the physical reference speed','m_B = sqrt(hbar * c / (2 * G)) = m_P / sqrt(2)','Recovers Planck-near matching condition up to the Schwarzschild factor 2.','blocked_no_physics_claim')
ON CONFLICT (special_case_id) DO UPDATE SET
    assumption = EXCLUDED.assumption,
    derived_expression = EXCLUDED.derived_expression,
    qsb_interpretation = EXCLUDED.qsb_interpretation,
    physical_claim_release = EXCLUDED.physical_claim_release;
INSERT INTO qsb_scale_mapping.claim_boundary VALUES ('CB-WORKPACKAGE-01','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','work_package','QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01','Scale mappings can mark a formal Compton-Schwarzschild bridge zone.','They do not prove the existence of a Planck-Bridge-Resonator.','scale_mapping_candidate','blocked_no_physics_claim','requires_dimensional_and_physical_review')
ON CONFLICT (claim_boundary_id) DO UPDATE SET
    allowed_claim = EXCLUDED.allowed_claim,
    forbidden_claim = EXCLUDED.forbidden_claim,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;
INSERT INTO qsb_scale_mapping.claim_boundary VALUES ('CB-BETA-01','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','mapping','MAP-BETA-01','beta_B can be used as a dimensionless length-scale proximity parameter.','beta_B does not imply that Planck length is a proven space pixel.','scale_mapping_candidate','blocked_no_physics_claim','requires_dimensional_and_physical_review')
ON CONFLICT (claim_boundary_id) DO UPDATE SET
    allowed_claim = EXCLUDED.allowed_claim,
    forbidden_claim = EXCLUDED.forbidden_claim,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;
INSERT INTO qsb_scale_mapping.claim_boundary VALUES ('CB-XI-01','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','mapping','MAP-XI-01','Xi_CS can test algebraic consistency between separately reconstructed speed scales.','Xi_CS does not redefine the physical speed of light.','scale_mapping_candidate','blocked_no_physics_claim','requires_dimensional_and_physical_review')
ON CONFLICT (claim_boundary_id) DO UPDATE SET
    allowed_claim = EXCLUDED.allowed_claim,
    forbidden_claim = EXCLUDED.forbidden_claim,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;
INSERT INTO qsb_scale_mapping.claim_boundary VALUES ('CB-MASS-INDEX-01','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','concept','m_comp_vs_m_schwarz','Separate mass indices preserve origin-side information before imposing special cases.','Separate indices do not assert two physically distinct masses without model context.','scale_mapping_candidate','blocked_no_physics_claim','requires_dimensional_and_physical_review')
ON CONFLICT (claim_boundary_id) DO UPDATE SET
    allowed_claim = EXCLUDED.allowed_claim,
    forbidden_claim = EXCLUDED.forbidden_claim,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;
INSERT INTO qsb_scale_mapping.dimensional_check VALUES ('DIM-LAMBDA-C','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','lambda_C = hbar / (m*c)','L','L','pass')
ON CONFLICT (check_id) DO UPDATE SET
    expression = EXCLUDED.expression,
    expected_dimension = EXCLUDED.expected_dimension,
    actual_dimension = EXCLUDED.actual_dimension,
    status = EXCLUDED.status;
INSERT INTO qsb_scale_mapping.dimensional_check VALUES ('DIM-R-S','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','r_s = 2*G*m/c^2','L','L','pass')
ON CONFLICT (check_id) DO UPDATE SET
    expression = EXCLUDED.expression,
    expected_dimension = EXCLUDED.expected_dimension,
    actual_dimension = EXCLUDED.actual_dimension,
    status = EXCLUDED.status;
INSERT INTO qsb_scale_mapping.dimensional_check VALUES ('DIM-BETA-B','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','beta_B = r_s / lambda_C','1','1','pass')
ON CONFLICT (check_id) DO UPDATE SET
    expression = EXCLUDED.expression,
    expected_dimension = EXCLUDED.expected_dimension,
    actual_dimension = EXCLUDED.actual_dimension,
    status = EXCLUDED.status;
INSERT INTO qsb_scale_mapping.dimensional_check VALUES ('DIM-C-COMP','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','c_comp = hbar/(m_comp*lambda_C)','L T^-1','L T^-1','pass')
ON CONFLICT (check_id) DO UPDATE SET
    expression = EXCLUDED.expression,
    expected_dimension = EXCLUDED.expected_dimension,
    actual_dimension = EXCLUDED.actual_dimension,
    status = EXCLUDED.status;
INSERT INTO qsb_scale_mapping.dimensional_check VALUES ('DIM-C-SCHWARZ','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','c_schwarz = sqrt(2*G*m_schwarz/r_s)','L T^-1','L T^-1','pass')
ON CONFLICT (check_id) DO UPDATE SET
    expression = EXCLUDED.expression,
    expected_dimension = EXCLUDED.expected_dimension,
    actual_dimension = EXCLUDED.actual_dimension,
    status = EXCLUDED.status;
INSERT INTO qsb_scale_mapping.dimensional_check VALUES ('DIM-XI-CS','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','Xi_CS = c_comp^2 / c_schwarz^2','1','1','pass')
ON CONFLICT (check_id) DO UPDATE SET
    expression = EXCLUDED.expression,
    expected_dimension = EXCLUDED.expected_dimension,
    actual_dimension = EXCLUDED.actual_dimension,
    status = EXCLUDED.status;
INSERT INTO qsb_scale_mapping.dimensional_check VALUES ('DIM-L-B','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','L_B = hbar^2/(2*G*m_schwarz*m_comp^2)','L','L','pass')
ON CONFLICT (check_id) DO UPDATE SET
    expression = EXCLUDED.expression,
    expected_dimension = EXCLUDED.expected_dimension,
    actual_dimension = EXCLUDED.actual_dimension,
    status = EXCLUDED.status;

CREATE OR REPLACE VIEW qsb_scale_mapping.v_planck_bridge_scale_mapping_claim_boundary AS
SELECT
    md.mapping_id,
    md.mapping_level,
    md.mapping_name,
    md.mapping_formula,
    md.mapping_condition,
    md.qsb_interpretation,
    md.dimensional_status,
    md.claim_status,
    md.physical_claim_release,
    md.review_status,
    cb.allowed_claim,
    cb.forbidden_claim
FROM qsb_scale_mapping.mapping_definition md
LEFT JOIN qsb_scale_mapping.claim_boundary cb
    ON cb.scope_type = 'mapping' AND cb.scope_key = md.mapping_id
WHERE md.run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01';

CREATE OR REPLACE VIEW qsb_scale_mapping.v_planck_bridge_scale_mapping_dashboard AS
SELECT
    r.run_id,
    r.work_package,
    r.mapping_definition_count,
    (SELECT count(*) FROM qsb_scale_mapping.mapping_definition WHERE run_id = r.run_id) AS actual_mapping_count,
    r.variable_count,
    (SELECT count(*) FROM qsb_scale_mapping.variable_registry WHERE run_id = r.run_id) AS actual_variable_count,
    r.special_case_count,
    (SELECT count(*) FROM qsb_scale_mapping.special_case WHERE run_id = r.run_id) AS actual_special_case_count,
    r.claim_boundary_count,
    (SELECT count(*) FROM qsb_scale_mapping.claim_boundary WHERE run_id = r.run_id) AS actual_claim_boundary_count,
    r.dimensional_check_count,
    (SELECT count(*) FROM qsb_scale_mapping.dimensional_check WHERE run_id = r.run_id) AS actual_dimensional_check_count,
    r.physical_claim_release,
    r.review_status,
    r.claim_boundary
FROM qsb_scale_mapping.scale_mapping_run r
WHERE r.run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01';

COMMIT;
