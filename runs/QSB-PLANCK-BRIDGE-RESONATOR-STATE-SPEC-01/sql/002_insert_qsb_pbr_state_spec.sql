-- QSB Planck-Bridge Resonator State Spec 01 inserts
BEGIN;
DELETE FROM qsb_planck_bridge.pbr_state_spec_run WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_state_spec_run (run_id, work_package, created_date, artifact_type, physical_claim_release, review_status, purpose, core_object, relational_coupling_general, relational_coupling_minimal, primary_gate, recommended_next_work_package) VALUES (
'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', '2026-07-05', 'formal_state_spec_candidate', 'blocked_no_physics_claim', 'requires_human_formal_review', 'Define a minimal formal Planck-Bridge-Resonator candidate and a Gram/PSD admissibility gate.', 'B_i = (H_i, Phi_i, M_i, gamma_i, sigma_i)', 'K_ij(gamma) = <Phi_i, C_ij(gamma) Phi_j>', 'K_ij = <Phi_i, Phi_j>', 'PSD admissibility gate for minimal Gram interpretation', 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01');

DELETE FROM qsb_planck_bridge.pbr_minimal_object_definition WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_minimal_object_definition (run_id, object_symbol, object_definition, claim_status, physical_claim_release, notes) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'B_i', 'B_i = (H_i, Phi_i, M_i, gamma_i, sigma_i)', 'formal_state_spec_candidate', 'blocked_no_physics_claim', 'Local formal interface candidate only; no physical existence claim.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'K_ij(gamma)', 'K_ij(gamma) = <Phi_i, C_ij(gamma) Phi_j>', 'relational_coupling_candidate', 'blocked_no_physics_claim', 'Relational quantity between candidates; not part of one local object alone.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'K_ij_minimal', 'K_ij = <Phi_i, Phi_j>', 'minimal_gram_interpretation', 'blocked_no_physics_claim', 'Minimal Gram reading implies Hermitian and PSD conditions.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'G_B', 'G_B = (V, E, W)', 'network_candidate', 'blocked_no_physics_claim', 'Network of admitted relations; not automatically spacetime.');

DELETE FROM qsb_planck_bridge.pbr_field_registry WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_field_registry (run_id, field_symbol, canonical_name, field_role, definition, required, claim_boundary) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'H_i', 'internal_state_space', 'local_object_field', 'Complex internal state space for candidate B_i.', 'yes', 'Formal object field only; no physical substrate claim.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Phi_i', 'candidate_state', 'local_object_field', 'Candidate state Phi_i in H_i.', 'yes', 'Formal state only; physical origin not claimed.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'M_i', 'mode_operator', 'local_object_field', 'Registered mode or structure operator on H_i.', 'yes', 'Modes are spectral components of a registered operator, not asserted Planck oscillators.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'gamma_i', 'boundary_condition', 'local_object_field', 'Geometric or field-like boundary condition / test context.', 'yes', 'Boundary condition is a parameter, not established geometry.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'sigma_i', 'scale_gate_status', 'local_object_field', 'Registered scale-gate status for the candidate.', 'yes', 'Scale-gate status is a review state, not evidence of existence.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'C_ij_gamma', 'coupling_operator', 'relational_field', 'Registered comparison/coupling operator under gamma.', 'conditional', 'Allowed only if registered and used in a model decision.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'K_ij', 'coupling_matrix_entry', 'relational_field', 'Relational candidate coupling between B_i and B_j.', 'yes', 'Must not be interpreted as physical spacetime relation without downstream gates.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'S_K', 'strength_function', 'decision_field', 'Registered strength or stability functional applied to K_ij.', 'conditional', 'Decision function must be registered before use.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'theta', 'edge_threshold', 'decision_field', 'Registered threshold for edge admission.', 'conditional', 'Threshold must be declared; no retrofitting after observing desired result.');

DELETE FROM qsb_planck_bridge.pbr_concept_definition WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_concept_definition (run_id, concept, definition, allowed_interpretation, blocked_interpretation) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'phase-bearing', 'Relative phase information can be formed and enters a registered coupling, transition or stability rule.', 'Operational relative phase candidate.', 'Absolute phase is physically real by assertion.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'moded', 'State Phi_i admits decomposition with respect to a registered operator M_i.', 'Spectral decomposition of a formal state.', 'Planck-scale oscillators exist.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'coupling-capable', 'At least one registered relational quantity K_ij exists and affects a model decision.', 'Decision-relevant relation candidate.', 'Coupling is physical merely because a symbol is written.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'gram-hypothesis', 'Minimal interpretation K_ij = <Phi_i, Phi_j>.', 'Formal candidate reading with PSD gate.', 'Empirical validation of QSB.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'network-level', 'Admitted relations can form a weighted graph G_B.', 'Graph candidate for downstream structure tests.', 'Graph is already spacetime.');

DELETE FROM qsb_planck_bridge.pbr_admissibility_gate WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_admissibility_gate (run_id, gate_id, gate_name, gate_scope, required_condition, pass_meaning, fail_meaning, claim_boundary) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'GATE-LOCAL-OBJECT-01', 'local_object_fields', 'B_i', 'H_i, Phi_i, M_i, gamma_i, sigma_i are declared.', 'Local candidate is formally specified.', 'Candidate record incomplete.', 'No physical existence claim.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'GATE-PHASE-01', 'phase_operationalization', 'K_ij', 'Relative phase information is used in a registered rule or invariant.', 'Phase-bearing vocabulary is operationalized.', 'Phase-bearing remains decorative.', 'No absolute phase ontology.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'GATE-MODE-01', 'mode_operator', 'M_i', 'A registered operator and decomposition rule exist.', 'Moded vocabulary is operationalized.', 'Moded remains metaphorical.', 'No claim of physical Planck oscillators.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'GATE-COUPLING-01', 'coupling_decision', 'K_ij', 'K_ij affects edge, transition or stability decision.', 'Coupling is decision-relevant.', 'Coupling is decorative notation.', 'No physical coupling claim.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'GATE-PSD-01', 'psd_admissibility', 'K', 'K is square, Hermitian/symmetric, nonnegative diagonal and PSD within tolerance.', 'Minimal Gram reading is not formally excluded.', 'Minimal Gram reading fails or needs modification.', 'PSD-pass is not QSB validation; PSD-fail is not full QSB refutation.');

DELETE FROM qsb_planck_bridge.pbr_psd_gate_spec WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_psd_gate_spec (run_id, field_name, field_type, required, definition) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'matrix_id', 'text', 'yes', 'Unique identifier for candidate matrix.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'matrix_source', 'text', 'yes', 'Path, table or artifact source of the matrix.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'n', 'integer', 'yes', 'Matrix dimension if square.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'is_square', 'boolean', 'yes', 'Whether matrix is square.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'is_hermitian', 'boolean', 'yes', 'Whether matrix equals conjugate transpose within tolerance.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'max_hermitian_deviation', 'numeric', 'yes', 'Maximum absolute deviation from Hermitian/symmetric condition.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'min_diagonal', 'numeric', 'yes', 'Minimum real diagonal entry.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'lambda_min', 'numeric', 'yes', 'Smallest eigenvalue of Hermitian part / candidate matrix.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'lambda_max', 'numeric', 'yes', 'Largest eigenvalue of Hermitian part / candidate matrix.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'negative_eigenvalue_count', 'integer', 'yes', 'Count of eigenvalues below negative tolerance.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'negative_eigenvalue_mass', 'numeric', 'yes', 'Sum of absolute values of eigenvalues below negative tolerance.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'tolerance', 'numeric', 'yes', 'Numerical tolerance used for the PSD gate.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'psd_pass', 'boolean', 'yes', 'Whether PSD gate passes within tolerance.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'admissibility_result', 'text', 'yes', 'pass / fail / conditional / not_tested.');

DELETE FROM qsb_planck_bridge.pbr_claim_boundary WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_claim_boundary (run_id, boundary_id, boundary_type, claim_text, release_status, rationale) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'ALLOW-001', 'allowed_claim', 'B_i is defined as a formal QSB-internal interface candidate.', 'released_formal_definition', 'This is a definition of a candidate object, not a physical existence claim.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'ALLOW-002', 'allowed_claim', 'The minimal Gram interpretation of K_ij implies Hermitian and PSD admissibility conditions.', 'released_formal_implication', 'This follows from the mathematical properties of Gram matrices.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'ALLOW-003', 'allowed_claim', 'PSD-pass means the minimal Gram interpretation is not formally excluded.', 'released_formal_interpretation', 'PSD-pass is only an admissibility result.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'BLOCK-001', 'blocked_claim', 'PBRs physically exist.', 'blocked_no_physics_claim', 'No empirical or theoretical derivation establishes existence.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'BLOCK-002', 'blocked_claim', 'Spacetime consists of PBRs.', 'blocked_no_physics_claim', 'Network-level emergence is not established.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'BLOCK-003', 'blocked_claim', 'PSD-pass validates QSB as a physical theory.', 'blocked_no_physics_claim', 'PSD-pass is a formal gate only.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'BLOCK-004', 'blocked_claim', 'PSD-fail refutes QSB as a whole.', 'blocked_no_physics_claim', 'PSD-fail rejects only the minimal Gram interpretation.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'BLOCK-005', 'blocked_claim', 'The PBR is an LQG spin-network link, a CDT simplex, a string or a space pixel.', 'blocked_no_equivalence_claim', 'External theory analogies are not identities.');

DELETE FROM qsb_planck_bridge.pbr_external_suggestion_triage WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_external_suggestion_triage (run_id, source_label, item, triage_status, rationale, qsb_action) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'phase_mode_dependent_coupling', 'keep_as_abstract_idea', 'Compatible with QSB if stripped of theory-specific imports.', 'Represent as K_ij(gamma)=<Phi_i,C_ij(gamma)Phi_j>.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'graph_nodes_phases_modes', 'toy_model_candidate', 'Potential later synthetic test structure.', 'Defer to QSB-PLANCK-BRIDGE-RESONATOR-TOYMODEL-01.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'LQG_spin_labels', 'reject_for_core_spec', 'Imports LQG-specific ontology and risks identity confusion.', 'Do not include in PBR core definition.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'LQG_area_formula', 'reject_for_core_spec', 'Unreleased LQG-specific area spectrum import.', 'Keep only as possible external analogy under claim boundary.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'CDT_simplices', 'reject_for_core_spec', 'Imports CDT-specific discretization assumptions.', 'Do not include in minimal object.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'metric_expectation_formula', 'reject_pending_dimensional_review', 'Dimensional, gauge and signature status not reviewed.', 'Place in virtual discard / rejected candidate registry.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'Einstein_Hilbert_limit_claim', 'reject_forbidden_claim', 'Would assert a major unproven continuum limit.', 'Blocked no physics claim.'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'Grok_sketch', 'reuse_beta_B_Xi_CS', 'reject_symbol_collision', 'beta_B and Xi_CS are reserved scale-mapping quantities in QSB.', 'Use b_i or A_i_bridge for amplitudes if needed.');

DELETE FROM qsb_planck_bridge.pbr_redteam_action_item WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01';
INSERT INTO qsb_planck_bridge.pbr_redteam_action_item (run_id, issue_id, issue_class, severity, redteam_finding, required_action, status) VALUES
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'RT-001', 'terminology_precision', 'high', 'PBR positive definition was softer than negative disclaimers.', 'Define phase-bearing, moded and coupling-capable formally.', 'addressed_in_state_spec'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'RT-002', 'formal_admissibility', 'high', 'PBR needs a fail-capable mathematical gate.', 'Introduce Gram hypothesis and PSD admissibility gate.', 'addressed_in_state_spec'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'RT-003', 'literature_scope', 'medium', 'External QG analogies can import unsupported meaning.', 'Keep PBR definition independent from LQG/CDT/String identifiers.', 'addressed_in_state_spec'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'RT-004', 'dwh_content_enforcement', 'medium', 'DWH should record claim boundaries and downstream use.', 'Create claim boundary and gate registry; downstream usage log reserved for next integration.', 'partially_addressed'),
('QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01', 'RT-005', 'matrix_test_next_step', 'high', 'PSD gate should be run against existing K candidate matrix.', 'Prepare QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01 using confirmed matrix source.', 'pending_next_work_package');
COMMIT;
