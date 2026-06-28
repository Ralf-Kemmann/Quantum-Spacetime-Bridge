#!/usr/bin/env python3
"""Generate the design-only QSB-INTERFACE01-C minimal candidate test plan."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INTERFACE01C/minimal_candidate_test_design"
CLAIM = "Minimal candidate test design only; not an execution result and not a proof of emergent spacetime or gravitation."
I01B = "runs/QSB-INTERFACE01B/candidate_bridge_forms"
I01A = "runs/QSB-INTERFACE01A/minimal_mechanism_skeleton"
D0X = "runs/QSB-D0X/phase_d_local_threshold_motif_summary"
MAT = "runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake"


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def anchor(anchor_id: str, label: str, cls: str, path_text: str, summary: str,
           unit: str, usable: str, note: str) -> dict[str, str]:
    exists = (REPO / path_text).is_file()
    return {
        "anchor_id": anchor_id, "anchor_label": label, "anchor_class": cls,
        "source_path": path_text, "read_status": "read_ok" if exists else "missing",
        "key_content_summary": summary, "unit_status": unit,
        "usable_for_interface01c": usable if exists else "review",
        "review_note": note if exists else f"Not found locally; {note}",
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT.relative_to(REPO)}")
    OUTPUT.mkdir(parents=True)

    anchors = [
        anchor("IC-IN-01", "INTERFACE01-B input register", "interface01b", f"{I01B}/01_interface01b_input_anchor_register.csv", "Prior source and unit boundaries for the candidate comparison.", "mixed_by_anchor", "yes", "Read-only design provenance."),
        anchor("IC-IN-02", "INTERFACE01-B candidate registry", "interface01b", f"{I01B}/02_interface01b_bridge_candidate_registry.csv", "Defines F02 cosine, C02 bounded normalization, R01 hard threshold, and R02 margin band.", "dimensionless/model-space", "yes", "Formal candidates are not confirmed laws."),
        anchor("IC-IN-03", "INTERFACE01-B normalization checks", "interface01b", f"{I01B}/03_interface01b_normalization_dimension_checks.csv", "Requires one declared dimensionless/model space and forbids direct SI/Phase-D mixing.", "explicit dimension contract", "yes", "Primary cross-space guard."),
        anchor("IC-IN-04", "INTERFACE01-B null-model designs", "interface01b", f"{I01B}/04_interface01b_null_model_designs.csv", "Six mandatory design-only controls covering trivial/random phases, material labels, mass order, thresholds, and information loss.", "design_only", "yes", "No null model was executed."),
        anchor("IC-IN-05", "INTERFACE01-B acceptance matrix", "interface01b", f"{I01B}/05_interface01b_candidate_acceptance_matrix.csv", "Candidate-level documentation statuses; material retention and null behavior remain untested.", "mixed review", "yes", "Not empirical acceptance."),
        anchor("IC-IN-06", "INTERFACE01-B abort criteria", "interface01b", f"{I01B}/06_interface01b_abort_criteria.csv", "Seven stop conditions for units, tuning, information loss, controls, metric claims, claim boundaries, and legacy dependencies.", "not_applicable", "yes", "Transferred into an execution gate."),
        anchor("IC-IN-07", "INTERFACE01-B recommended candidate set", "interface01b", f"{I01B}/07_interface01b_recommended_candidate_set.csv", "Conditionally recommends F02 -> C02 -> R01 with mandatory R02 audit and six null models.", "normalized candidate space", "yes", "Minimality/auditability recommendation only."),
        anchor("IC-IN-08", "INTERFACE01-B final assessment", "interface01b", f"{I01B}/09_interface01b_final_assessment.md", "States candidate comparison is sufficient but execution input is absent.", "mixed", "yes", "Defines immediate design boundary."),
        anchor("IC-IN-09", "INTERFACE01-B manifest", "interface01b", f"{I01B}/10_interface01b_run_manifest.json", "Completed candidate comparison with no simulation or synthetic evidence.", "metadata_only", "yes", "Manifest is not physics validation."),
        anchor("IC-IN-10", "INTERFACE01-A quantity contract", "interface01a", f"{I01A}/02_interface01a_quantity_dimension_contract.csv", "Defines phase, kernel, correlation, threshold, relation, and graph/metric separation.", "mixed explicit contract", "yes", "Upstream unit boundary."),
        anchor("IC-IN-11", "INTERFACE01-A link requirements", "interface01a", f"{I01A}/04_interface01a_phase_to_threshold_link_requirements.csv", "Requires explicit maps, shared normalized scale, material injection rule, and graph/metric separation.", "dimensionless/model-defined", "yes", "Formal requirements remain open until tested."),
        anchor("IC-IN-12", "Phase-D summary manifest", "phase_d", f"{D0X}/12_d0x_run_manifest.json", "Records theta=0.0300 solely as a Phase-D toy-model workpoint.", "model_units / dimensionless toy-model units; not_SI_converted", "partial", "Comparison anchor only; direct transfer forbidden."),
        anchor("IC-IN-13", "MATERIAL01 result anchors", "material01", f"{MAT}/csv/06_result_material_sensitivity_anchor.csv", "Bounded internal material-sensitive phase/wave/signature anchors.", "mixed_review; lambda_db=m; energy=J; mass_u review", "partial", "No numeric contact with Phase-D model units."),
        anchor("IC-IN-14", "Legacy c/line-element bridge source", "legacy_c_bridge", "local_source_for_c_line_element_bridge", "No local source was found by repository text search; equations are carried from the task only as a review anchor.", "dphi dimensionless; ds length; coefficient dimensions require review", "review", "Must not be treated as locally validated."),
    ]
    write_csv("01_interface01c_input_anchor_register.csv", ["anchor_id","anchor_label","anchor_class","source_path","read_status","key_content_summary","unit_status","usable_for_interface01c","review_note"], anchors)

    test_plan = [
        {"plan_id":"TP-01","candidate_chain":"F02 -> C02 -> R01","F_candidate":"F02: K_ij=cos(delta_phi_ij)","C_candidate":"C02: C_ij=(K_ij+1)/2","R_candidate":"R01: A_ij=1[C_ij>=theta_new]","purpose":"Primary minimal chain for a later preregistered candidate test.","required_input_quantities":"operational phi_i or delta_phi_ij; pair IDs; explicit provenance; optional material labels only after injection rule","output_quantities":"K_ij in [-1,1]; C_ij in [0,1]; theta_new; binary A_ij","normalization_requirement":"delta_phi modulo 2*pi; affine C02 normalization fixed before evaluation","theta_policy":"recalibrate_theta_new_in_normalized_candidate_space","margin_audit_required":"yes","null_models_required":"all_six","run_scope":"design_only","claim_boundary":"Working candidate chain only; no physical mechanism confirmation.","review_note":"Execution blocked until operational phase input and frozen calibration protocol exist."},
        {"plan_id":"TP-02","candidate_chain":"F02 -> C02 -> R01 + R02 audit","F_candidate":"F02","C_candidate":"C02","R_candidate":"R01 with R02 near-threshold classification","purpose":"Preserve signed threshold margins and expose unstable edge assignments.","required_input_quantities":"C_ij; independently calibrated theta_new; preregistered epsilon_new","output_quantities":"margin_ij; absolute margin; near-threshold flag; edge status","normalization_requirement":"theta_new and epsilon_new live on the same [0,1] C02 scale","theta_policy":"theta_new frozen before held-out evaluation","margin_audit_required":"yes","null_models_required":"N01; N02; N05; N06 minimum, while all_six remain mandatory for full chain","run_scope":"design_only","claim_boundary":"Audit structure, not evidence of geometry.","review_note":"Every reported edge result must retain its margin row."},
        {"plan_id":"TP-03","candidate_chain":"F02 -> C02 -> R01 under material controls","F_candidate":"F02","C_candidate":"C02","R_candidate":"R01","purpose":"Test whether a future explicit material injection carries information beyond labels or mass rank.","required_input_quantities":"reviewed MATERIAL01 records; explicit dimension-safe material-to-phase/weight map; fixed phase inputs","output_quantities":"predeclared material-retention statistic plus chain outputs","normalization_requirement":"SI/material channel transformed explicitly before normalized candidate-space entry","theta_policy":"same frozen theta_new across primary and material-control comparisons","margin_audit_required":"yes","null_models_required":"N03; N04 plus all remaining mandatory controls","run_scope":"not_now","claim_boundary":"Material sensitivity at input does not imply downstream spacetime structure.","review_note":"Blocked because no material injection map exists."},
        {"plan_id":"TP-04","candidate_chain":"execution readiness gate for F02 -> C02 -> R01","F_candidate":"F02","C_candidate":"C02","R_candidate":"R01 + R02","purpose":"Prevent execution before inputs, calibration, controls, schemas, and abort rules are frozen.","required_input_quantities":"approved phase source; pair universe; calibration/evaluation split; random seeds where applicable; output paths","output_quantities":"signed readiness decision only","normalization_requirement":"all units and transformations declared before run","theta_policy":"no Phase-D theta reuse; theta_new calibration method preregistered","margin_audit_required":"yes","null_models_required":"all_six","run_scope":"design_only","claim_boundary":"Readiness decision cannot validate physics.","review_note":"Current readiness is no-go pending phase and injection inputs."},
    ]
    write_csv("02_interface01c_minimal_candidate_test_plan.csv", ["plan_id","candidate_chain","F_candidate","C_candidate","R_candidate","purpose","required_input_quantities","output_quantities","normalization_requirement","theta_policy","margin_audit_required","null_models_required","run_scope","claim_boundary","review_note"], test_plan)

    theta_design = [
        {"theta_design_id":"TH-00","theta_label":"direct Phase-D transfer guard","source_context":"Phase-D theta=0.0300 in its own toy-model space","allowed_source":"Phase-D may inform required audit fields and stability questions only.","forbidden_source":"The numeric value 0.0300 as theta_new or as a calibration prior.","calibration_goal":"Prevent cross-model threshold inheritance.","candidate_methods":"none; guard row","selection_rule":"Any direct reuse triggers abort B01.","unit_dimension_status":"Both may be dimensionless yet belong to different normalized/model spaces.","risk":"False continuity between unrelated scales.","recommended_policy":"forbid_direct_transfer","review_note":"Dimensionless does not mean interchangeable."},
        {"theta_design_id":"TH-01","theta_label":"quantile_based_threshold","source_context":"C02 values in a calibration-only partition of the new [0,1] space","allowed_source":"Predeclared calibration partition or control distribution.","forbidden_source":"Held-out target labels, desired edge pattern, or Phase-D theta value.","calibration_goal":"Choose a reproducible edge-density quantile without target-outcome tuning.","candidate_methods":"fixed quantile q declared before calculation","selection_rule":"Freeze q and tie rule before calibration; freeze resulting theta_new before evaluation.","unit_dimension_status":"theta_new dimensionless on C02 [0,1].","risk":"Chosen q may impose arbitrary graph density.","recommended_policy":"retain_as_secondary_method_and_report_density_sensitivity","review_note":"Quantile and partition must be justified before execution."},
        {"theta_design_id":"TH-02","theta_label":"control_separation_threshold","source_context":"Preregistered structured versus null calibration controls in normalized C02 space","allowed_source":"Calibration-only N01/N02 distributions and a predeclared separation statistic.","forbidden_source":"Evaluation outcomes or material labels reserved for testing.","calibration_goal":"Select theta_new by a fixed control-separation objective.","candidate_methods":"predeclared balanced error or fixed false-positive-rate rule","selection_rule":"Objective and tie break fixed before controls are generated; theta_new then frozen.","unit_dimension_status":"theta_new dimensionless on C02 [0,1].","risk":"Control construction may dominate the selected threshold.","recommended_policy":"primary_if_operational_phase_and_control_protocol_are_approved","review_note":"Requires independent calibration/evaluation split."},
        {"theta_design_id":"TH-03","theta_label":"stability_window_threshold","source_context":"Preregistered theta grid in new normalized space","allowed_source":"Calibration partition and fixed grid only.","forbidden_source":"Post-hoc narrowing around a desired motif.","calibration_goal":"Require a broad interval where predeclared graph/statistic behavior is stable.","candidate_methods":"largest qualifying contiguous stability window; fixed center/tie rule","selection_rule":"Window width, statistic tolerance, minimum width, and tie rule fixed before evaluation.","unit_dimension_status":"theta grid and theta_new dimensionless on C02 [0,1].","risk":"Flexible stability definitions can hide tuning.","recommended_policy":"mandatory_guard_for_any_selected_theta_new","review_note":"Failure to find a qualifying window is a valid stop result."},
        {"theta_design_id":"TH-04","theta_label":"pre_registered_threshold_grid","source_context":"Entire normalized C02 interval [0,1]","allowed_source":"Grid declared independently of candidate outcomes.","forbidden_source":"Outcome-dependent insertion/removal of grid points.","calibration_goal":"Expose threshold sensitivity and isolated effects.","candidate_methods":"fixed finite grid including boundary policy and exact decimals","selection_rule":"Report all grid outcomes; selection only via a separately preregistered TH-01/02/03 rule.","unit_dimension_status":"dimensionless C02 scale.","risk":"Grid search becomes implicit multiple testing if selectively reported.","recommended_policy":"mandatory_full_reporting_guard_not_standalone_selector","review_note":"No grid is evaluated in INTERFACE01-C."},
    ]
    write_csv("03_interface01c_theta_calibration_design.csv", ["theta_design_id","theta_label","source_context","allowed_source","forbidden_source","calibration_goal","candidate_methods","selection_rule","unit_dimension_status","risk","recommended_policy","review_note"], theta_design)

    required_columns = "pair_id;i;j;delta_phi_ij;F02_value;C02_value;theta_new;margin_ij;near_threshold_flag;edge_before;edge_after_or_edge_status;null_model_id;run_id;review_note"
    margins = [
        {"margin_audit_id":"MA-01","relation_rule":"R01: A_ij=1 if C02_value>=theta_new else 0","margin_definition":"margin_ij=C02_value-theta_new","epsilon_policy":"epsilon_new must be preregistered on the normalized C02 scale.","near_threshold_band":"near_threshold if abs(margin_ij)<=epsilon_new","required_columns":required_columns,"why_required":"Retains distance and sign relative to threshold instead of reporting edges alone.","pass_condition":"Every evaluated pair has a reproducible signed margin, edge status, provenance, and null-model context.","failure_condition":"Edges are reported without margins or theta_new is changed after viewing results.","review_note":"Core R02 audit row."},
        {"margin_audit_id":"MA-02","relation_rule":"R02 review-band policy","margin_definition":"signed margin plus abs_margin_ij=abs(margin_ij)","epsilon_policy":"Choose epsilon_new before evaluation as a fixed fraction of preregistered grid spacing or by calibration-only measurement resolution; freeze it.","near_threshold_band":"inside, outside, and exact-tie categories must be explicit","required_columns":required_columns,"why_required":"Prevents near-threshold flips from being presented as robust relations.","pass_condition":"Epsilon source, exact value, tie rule, and sensitivity companion values are registered before held-out evaluation.","failure_condition":"Epsilon is selected to include or exclude desired edges.","review_note":"If no defensible epsilon is available, execution remains blocked."},
        {"margin_audit_id":"MA-03","relation_rule":"Edge transition audit across fixed theta_new or declared control change","margin_definition":"pre/post signed margins where an edge change is claimed","epsilon_policy":"Use the same frozen epsilon_new for all primary and null runs.","near_threshold_band":"classify both pre and post records; do not infer mechanism relevance from a flip alone","required_columns":required_columns,"why_required":"Separates documented threshold proximity from classification or arbitrary-threshold artifacts.","pass_condition":"Any edge flip includes pre/post values, fixed parameters, run identity, and control/null label.","failure_condition":"Flip lacks paired margins, changes parameter policy, or appears only under isolated tuned theta.","review_note":"Phase-D fields inspire audit structure only; values are not transferred."},
    ]
    write_csv("04_interface01c_margin_audit_design.csv", ["margin_audit_id","relation_rule","margin_definition","epsilon_policy","near_threshold_band","required_columns","why_required","pass_condition","failure_condition","review_note"], margins)

    nulls = [
        {"null_model_id":"N01","null_model_label":"trivial_uniform_phase","purpose":"Detect nontrivial graph output generated from identical phase alone.","required_for_candidate_chain":"yes","expected_control_behavior":"Uniform delta_phi produces analytically uniform F02/C02 values; any heterogeneity requires an explicitly declared non-phase input.","failure_implication":"Candidate chain cannot attribute structure to phase differences.","priority":"P0","design_status":"needs_input","review_note":"Requires approved phase/pair universe; no run here."},
        {"null_model_id":"N02","null_model_label":"random_phase_shuffle","purpose":"Compare target statistic with fixed-protocol phase permutations.","required_for_candidate_chain":"yes","expected_control_behavior":"Preregistered structured-phase statistic should separate from shuffle distribution on held-out evaluation.","failure_implication":"Reject chain for the stated phase-structure target.","priority":"P0","design_status":"needs_input","review_note":"Statistic, permutation count/seed policy, and split must be frozen."},
        {"null_model_id":"N03","null_model_label":"material_label_shuffle","purpose":"Test whether retained material signal depends on reviewed records rather than labels.","required_for_candidate_chain":"yes","expected_control_behavior":"Material-retention statistic degrades under label permutation if an approved injection map carries material information.","failure_implication":"No supported materialsensitive propagation through the tested chain.","priority":"P0","design_status":"review_gap","review_note":"Blocked by absent material injection map."},
        {"null_model_id":"N04","null_model_label":"mass_order_only_control","purpose":"Separate phase/wave information from a mass-rank-only baseline.","required_for_candidate_chain":"yes","expected_control_behavior":"Primary material statistic must report incremental behavior relative to the frozen mass-order baseline.","failure_implication":"Candidate adds no demonstrated information beyond mass ordering.","priority":"P0","design_status":"review_gap","review_note":"mass_u and derived isotope ordering remain review-sensitive."},
        {"null_model_id":"N05","null_model_label":"threshold_randomization_or_sweep_guard","purpose":"Detect isolated or tuned theta_new effects.","required_for_candidate_chain":"yes","expected_control_behavior":"Reported behavior remains within a preregistered stability window and all grid outcomes are retained.","failure_implication":"Trigger post-hoc/instability abort; no mechanism interpretation.","priority":"P0","design_status":"ready_design","review_note":"Design ready; requires future normalized C02 values."},
        {"null_model_id":"N06","null_model_label":"pipeline_identity_control","purpose":"Audit phase-class merges and information loss at F02, C02, and R01.","required_for_candidate_chain":"yes","expected_control_behavior":"F02 even-symmetry merges are enumerated; affine C02 is invertible in K; R01 loss is quantified with margins retained.","failure_implication":"Untracked information loss blocks materialsensitive or phase-specific interpretation.","priority":"P0","design_status":"ready_design","review_note":"Analytic/schema design ready; execution input still absent."},
    ]
    write_csv("05_interface01c_required_null_models.csv", ["null_model_id","null_model_label","purpose","required_for_candidate_chain","expected_control_behavior","failure_implication","priority","design_status","review_note"], nulls)

    acceptance_specs = [
        ("A01","theta_new calibrated in normalized space","Was theta_new selected and frozen under TH-01/02/03 plus TH-04 reporting?","Calibration-only C02 data, full protocol, and frozen theta_new are recorded.","Direct Phase-D reuse or outcome-driven calibration.","calibration register and checksums","theta_new dimensionless on C02 [0,1]","No physical/universal threshold interpretation.","yes","Currently blocks execution."),
        ("A02","all six null models defined before execution","Are N01-N06 fully parameterized before primary evaluation?","All inputs, seeds/rules, statistics, and failure implications are frozen.","Any null model is missing or added after results.","six approved null-model configurations","No cross-space unit mixing in controls.","Null outcomes bound interpretation.","yes","N03/N04 remain review gaps."),
        ("A03","R02 margin audit specified","Does every relation/flip retain signed margin and near-threshold status?","MA-01 through MA-03 schema and epsilon policy are frozen.","Edge-only reporting or tuned epsilon.","complete margin audit rows","C02, theta_new, epsilon_new share scale.","Margins are model diagnostics only.","yes","Design exists; values not generated."),
        ("A04","SI/model_units separation preserved","Are MATERIAL01, Phase-D, and normalized candidate spaces kept distinct?","Every transformation has explicit source/target unit status; no direct Phase-D numeric transfer.","Any undeclared numerical cross-space operation.","unit/transform register","Explicit channel separation.","No implied physical calibration.","yes","Hard gate."),
        ("A05","material sensitivity not erased","Does the approved chain retain a preregistered material statistic beyond controls?","N03/N04 pass on held-out data under an explicit injection map.","Material labels collapse or no improvement beyond mass-only control.","reviewed material inputs and retention statistic","Dimension-safe injection transform.","Input sensitivity is not geometry evidence.","yes","Cannot be assessed yet."),
        ("A06","structured phase distinguishable from controls","Does the target statistic separate from N01/N02 under frozen rules?","Preregistered criterion passes on held-out evaluation and survives threshold guard.","Uniform/random controls are indistinguishable or outperform target.","phase input, control distributions, statistic","Dimensionless phase convention and fixed normalization.","Only candidate discrimination may be claimed.","yes","Cannot be assessed yet."),
        ("A07","graph relation not claimed as physical metric","Are A_ij and graph summaries kept at relation/model level?","Outputs and assessment contain no metric identity leap.","Graph distance/adjacency is identified with a physical spacetime metric.","claim-boundary audit","Binary/model relation only.","No physical metric conclusion.","yes","Hard interpretation gate."),
        ("A08","claim boundary passes","Are outputs restricted to the authorized candidate test?","Claims match registered evidence and limitations.","Any unsupported mechanism, spacetime, gravity, or theory-completion conclusion.","forbidden-claim scan and human review","All unresolved units remain visible.",CLAIM,"yes","Hard gate."),
    ]
    abort_specs = [
        ("B01","direct reuse of Phase-D theta","Is numeric 0.0300 assigned to theta_new?","No direct transfer occurs.","Any direct assignment or hidden calibration prior reuses 0.0300.","theta calibration manifest","Separate model spaces.","No universal threshold claim.","yes","Immediate abort."),
        ("B02","post-hoc threshold tuning","Were theta_new/epsilon_new/grid rules changed after target outcomes?","All policies frozen before held-out evaluation.","Outcome-driven parameter or grid modification.","timestamped/checksummed configuration","Single normalized C02 scale.","No selected-result storytelling.","yes","Immediate abort or independent rerun under a new preregistration."),
        ("B03","SI/model-unit numeric mixing","Does any undeclared MATERIAL01-to-Phase-D operation occur?","No such operation occurs.","Direct mixing without validated bridge.","unit lineage","Explicit dimensions and spaces.","No physical bridge inferred.","yes","Immediate abort."),
        ("B04","all material sensitivity destroyed","Do N03/N04 show no retained material information?","A preregistered retention condition passes.","Candidate collapses all target material distinctions.","material control results","Injection transform audited.","Failure is reported without geometry inference.","yes","Reject material-bridge use; retain only as control if useful."),
        ("B05","structured phase indistinguishable from controls","Do N01/N02 fail the separation criterion?","Structured input meets preregistered separation criterion.","Uniform/random controls are not distinguishable.","control results","Same phase convention and theta policy.","No mechanism interpretation after failure.","yes","Reject candidate for stated target."),
        ("B06","unsupported spacetime/gravity conclusion","Does reporting exceed registered evidence?","All text remains candidate-test bounded.","Reporting asserts physical emergence/gravity establishment.","claim audit","No unit laundering.",CLAIM,"yes","Fail checks and correct before release."),
        ("B07","missing null-model design","Is any of N01-N06 absent or incompletely frozen?","All six designs are execution-ready.","Any required control is absent, underspecified, or added after evaluation.","null-model configurations","Control units match primary path.","No selective control omission.","yes","Execution is no-go."),
    ]
    matrix = []
    for kind, specs in (("acceptance", acceptance_specs), ("abort", abort_specs)):
        for mid, label, question, pass_c, abort_c, evidence, unit_check, claim_check, blocks, note in specs:
            matrix.append({"matrix_id":mid,"criterion_type":kind,"criterion_label":label,"test_question":question,"pass_condition":pass_c,"abort_condition":abort_c,"required_evidence":evidence,"unit_dimension_check":unit_check,"claim_boundary_check":claim_check,"blocks_execution":blocks,"review_note":note})
    write_csv("06_interface01c_acceptance_abort_matrix.csv", ["matrix_id","criterion_type","criterion_label","test_question","pass_condition","abort_condition","required_evidence","unit_dimension_check","claim_boundary_check","blocks_execution","review_note"], matrix)

    legacy = [{
        "legacy_bridge_id":"LCB-01", "bridge_label":"Legacy c/line-element phase-increment mapping",
        "formal_mapping":"dphi_rel = -(m*c/hbar) ds_rel",
        "inverse_mapping":"ds_rel = -(hbar/(m*c)) dphi_rel",
        "source_status":"not_found_local",
        "role_in_interface_chain":"Potential upstream review mapping between a relational line-element increment and phase increment; not part of the F02/C02/R01 test input unless separately validated.",
        "unit_dimension_status":"dphi dimensionless; ds length; m*c/hbar has inverse-length dimension and hbar/(m*c) length, subject to convention/source review.",
        "what_it_can_support":"A source-review question about whether an operational relational phase increment can be defined consistently.",
        "what_it_cannot_support":"It cannot validate the candidate chain, supply phase data, transfer Phase-D theta, establish a physical metric, or establish spacetime/gravity conclusions.",
        "recommended_next_action":"Locate and inspect the authoritative local source; verify sign, action convention, timelike/null scope, relational definitions, and operational observables before any use.",
        "review_note":"The c/line-element bridge is carried as a legacy review anchor and must not be treated as validated by INTERFACE01-C unless a local source is inspected.",
    }]
    write_csv("07_interface01c_legacy_c_bridge_review.csv", ["legacy_bridge_id","bridge_label","formal_mapping","inverse_mapping","source_status","role_in_interface_chain","unit_dimension_status","what_it_can_support","what_it_cannot_support","recommended_next_action","review_note"], legacy)

    reviews = [
        {"review_id":"IC-R01","source_path":"operational phase input not yet identified","issue_type":"missing_phase_input","description":"No approved phi_i/delta_phi_ij dataset, pair universe, or provenance contract exists for execution.","severity":"high","recommended_resolution":"Provide and review an operational phase source with modulo, indexing, and split rules.","blocks_interface01c_execution":"yes"},
        {"review_id":"IC-R02","source_path":f"{MAT}/csv/06_result_material_sensitivity_anchor.csv","issue_type":"material_injection_gap","description":"No dimension-safe rule maps reviewed material anchors into phase, weights, or normalized candidate variables.","severity":"high","recommended_resolution":"Define and review competing injection maps before N03/N04 or primary material testing.","blocks_interface01c_execution":"yes"},
        {"review_id":"IC-R03","source_path":f"{D0X}/12_d0x_run_manifest.json","issue_type":"theta_transfer_guard","description":"Phase-D theta=0.0300 must remain isolated from theta_new calibration.","severity":"high","recommended_resolution":"Enforce TH-00 and B01 in any future configuration validator.","blocks_interface01c_execution":"yes"},
        {"review_id":"IC-R04","source_path":"03_interface01c_theta_calibration_design.csv","issue_type":"theta_method_selection","description":"Primary calibration method, split, statistic, grid, and tie rules are designed but not selected/frozen.","severity":"high","recommended_resolution":"Choose one primary rule and freeze all parameters before execution authorization.","blocks_interface01c_execution":"yes"},
        {"review_id":"IC-R05","source_path":"04_interface01c_margin_audit_design.csv","issue_type":"epsilon_selection","description":"epsilon_new requires a defensible calibration-only or resolution-based rule.","severity":"high","recommended_resolution":"Freeze epsilon policy and companion sensitivity values before evaluation.","blocks_interface01c_execution":"yes"},
        {"review_id":"IC-R06","source_path":"05_interface01c_required_null_models.csv","issue_type":"null_inputs_missing","description":"N01-N04 require phase/material inputs; no null model has been executed.","severity":"high","recommended_resolution":"Complete all six configurations and evidence schemas before primary run.","blocks_interface01c_execution":"yes"},
        {"review_id":"IC-R07","source_path":"local_source_for_c_line_element_bridge","issue_type":"legacy_source_missing","description":"No local source for the c/line-element equations was found by repository text search.","severity":"medium","recommended_resolution":"Locate authoritative source and conduct source/convention review; otherwise keep outside execution.","blocks_interface01c_execution":"no"},
        {"review_id":"IC-R08","source_path":"future execution configuration","issue_type":"reproducibility_contract_missing","description":"Random seeds, checksums, calibration/evaluation split, exact decimals, stop reason, and output schema are not yet instantiated.","severity":"high","recommended_resolution":"Create a separate approved execution config only after input review.","blocks_interface01c_execution":"yes"},
    ]
    write_csv("08_interface01c_open_review_items.csv", ["review_id","source_path","issue_type","description","severity","recommended_resolution","blocks_interface01c_execution"], reviews)

    assessment = f"""# QSB-INTERFACE01-C Final Assessment

## Zweck
INTERFACE01-C definiert ein minimales Testdesign fuer `F02 -> C02 -> R01` mit verpflichtendem R02-Margin-Audit, sechs Nullmodellen, neuer Schwellenkalibrierung und harten Abbruchkriterien. Es wurde nichts ausgefuehrt oder simuliert.

## Input-Sufficiency
Status: `sufficient_for_design_not_execution`

INTERFACE01-A/B, Phase D und MATERIAL01 reichen fuer das Design. Fuer eine Ausfuehrung fehlen operationaler Phaseninput, Material-Injektionsregel, eingefrorene Kalibrierparameter und vollstaendige Nullmodellkonfigurationen.

## Minimal-Kandidatenset
```text
F02: K_ij = cos(delta_phi_ij)
C02: C_ij = (K_ij + 1) / 2
R01: A_ij = 1[C_ij >= theta_new]
R02: margin_ij = C_ij - theta_new
```

Die Kette ist eine konditionale Arbeitsform. F02 verliert die Orientierung unter `delta_phi -> -delta_phi`; R01 verliert kontinuierliche Information. R02 und N06 muessen diese Verluste sichtbar halten.

## theta_new-Kalibrierpolitik
Der Phase-D-Wert `0.0300` wird weder direkt noch als Prior uebernommen. `theta_new` lebt dimensionslos im neu normierten C02-Raum `[0,1]`.

Vor Ausfuehrung ist eine primaere Kalibrierregel zu waehlen: vorab fixiertes Quantil, Kontrolltrennung oder Stabilitaetsfenster. Ein vollstaendig berichtetes, vorregistriertes Grid ist Pflichtwache. Kalibrierpartition, Zielstatistik, Tie-Regel und Auswahlregel werden vor der gehaltenen Evaluation eingefroren.

## R02-Margin-Audit
Jede Relation fuehrt den signierten Margin, Absolutmargin, `theta_new`, `epsilon_new`, Near-threshold-Flag, Edge-Status, Nullmodell- und Run-ID. `epsilon_new` muss im C02-Raum vorregistriert sein. Edge-Flips ohne gepaarte Margins gelten nicht als belastbare Mechanismussignatur.

## Nullmodelle
N01 bis N06 sind verpflichtend: uniforme Phase, Phase-Shuffle, Materiallabel-Shuffle, Mass-order-only, Threshold-Sweep-Guard und Pipeline-Identity. N03/N04 sind durch die fehlende Material-Injektionsregel blockiert; N01/N02 brauchen den operationalen Phaseninput. Kein Nullmodell wurde ausgefuehrt.

## Legacy-c-Bridge-Status
Die Zuordnungen `dphi_rel = -(m*c/hbar) ds_rel` und ihre Inverse werden nur als vom Auftrag vorgegebener Legacy-Review-Anker dokumentiert. Die Repo-Suche fand keine lokale Quelle. Der Strang bleibt vorgelagert, source-review- und operationalisierungspflichtig und ist kein Input des Minimaltests.

## Abbruchkriterien
Sofortiger Stopp bei direkter `0.0300`-Uebernahme, Post-hoc-Schwellentuning, SI/Modellraum-Mischung, totalem Verlust der Materialsensitivitaet, fehlender Trennung von strukturierten und trivialen/zufaelligen Kontrollen, ungestuetzten Raumzeit-/Gravitationsschluessen oder einem fehlenden Nullmodell.

## Ausfuehrbarkeit
Ein spaeterer Minimaltest ist derzeit `no-go`. Das Design ist ausreichend, aber die benoetigten Inputs und eingefrorenen Konfigurationen fehlen. Der Legacy-c-Strang blockiert den Minimaltest nicht, solange er ausserhalb der Ausfuehrung bleibt.

## Empfehlung
Als naechsten Block nur einen Input-/Preregistration-Gate ausfuehren: Phasenquelle und Paaruniversum festlegen, Material-Injektionsstatus entscheiden, Kalibrierregel und Split einfrieren, epsilon_new festlegen, sechs Nullconfigs vervollstaendigen und alle Outputs/Stopgruende spezifizieren. Erst danach darf separat ueber eine Minimal-Ausfuehrung entschieden werden.

## Claim-Grenze
{CLAIM}
"""
    (OUTPUT / "09_interface01c_final_assessment.md").write_text(assessment, encoding="utf-8")

    required_missing = sum(row["read_status"] == "missing" for row in anchors[:-1])
    status = "interface01c_minimal_candidate_test_design_completed_with_review_items"
    sufficiency = "sufficient_for_design_not_execution"
    if required_missing:
        status = "interface01c_minimal_candidate_test_design_partial_inputs"
        sufficiency = "partial_inputs"
    manifest = {
        "run_id": "QSB-INTERFACE01C", "status": status,
        "output_dir": "runs/QSB-INTERFACE01C/minimal_candidate_test_design",
        "input_sufficiency": sufficiency, "execution_readiness": "no_go",
        "input_anchors": len(anchors), "test_plan_rows": len(test_plan),
        "theta_design_rows": len(theta_design), "margin_audit_rows": len(margins),
        "required_null_models": len(nulls), "acceptance_abort_rows": len(matrix),
        "legacy_c_bridge_rows": len(legacy), "review_items": len(reviews),
        "legacy_c_bridge_source_status": "not_found_local",
        "phase_d_theta_direct_transfer_allowed": False,
        "mutated_existing_files": False, "generated_synthetic_evidence": False,
        "candidate_test_executed": False, "new_simulation_performed": False,
        "phase_d_rescan_performed": False, "deep_research_performed": False,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CLAIM,
    }
    (OUTPUT / "10_interface01c_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
