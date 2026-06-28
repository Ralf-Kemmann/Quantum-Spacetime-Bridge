#!/usr/bin/env python3
"""Build the read-only QSB-INTERFACE01-B candidate bridge-form comparison."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INTERFACE01B/candidate_bridge_forms"
CLAIM = "Candidate bridge-form comparison only; not a proof of emergent spacetime or gravitation."
I01A = "runs/QSB-INTERFACE01A/minimal_mechanism_skeleton"
D0X = "runs/QSB-D0X/phase_d_local_threshold_motif_summary"
MAT = "runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake"
INV = "runs/QSB-INVENTORY01/legacy_to_interface_alignment_map"


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def input_anchor(anchor_id: str, label: str, cls: str, path_text: str, summary: str,
                 unit: str, usable: str, note: str) -> dict[str, str]:
    path = REPO / path_text
    return {
        "anchor_id": anchor_id, "anchor_label": label, "anchor_class": cls,
        "source_path": path_text, "read_status": "read_ok" if path.is_file() else "missing",
        "key_content_summary": summary, "unit_status": unit,
        "usable_for_interface01b": usable if path.is_file() else "review",
        "review_note": note if path.is_file() else f"Missing input; {note}",
    }


def candidate(cid: str, group: str, label: str, definition: str, input_q: str,
              output_q: str, value_range: str, dimension: str, normalization: str,
              loss: str, support: str, boundary: str, note: str) -> dict[str, str]:
    return {
        "candidate_id": cid, "candidate_group": group, "candidate_label": label,
        "formal_definition": definition, "input_quantity": input_q,
        "output_quantity": output_q, "expected_range": value_range,
        "dimension_status": dimension, "normalization_need": normalization,
        "information_loss_risk": loss, "source_support": support,
        "claim_boundary": boundary, "review_note": note,
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT.relative_to(REPO)}")
    OUTPUT.mkdir(parents=True)

    anchors = [
        input_anchor("IB-IN-01", "INTERFACE01-A quantity/dimension contract", "interface01a", f"{I01A}/02_interface01a_quantity_dimension_contract.csv", "Declares delta_phi, K, G, theta, adjacency, graph distance, and SI/model-space separation.", "mixed explicit contract", "yes", "Primary dimension boundary."),
        input_anchor("IB-IN-02", "INTERFACE01-A mechanism arrows", "interface01a", f"{I01A}/03_interface01a_mechanism_arrow_map.csv", "Marks delta_phi -> K -> G -> theta as review gaps and downstream Phase-D arrows as internal toy-model support.", "dimensionless/model-defined bridge", "yes", "Primary arrow-status input."),
        input_anchor("IB-IN-03", "INTERFACE01-A link requirements", "interface01a", f"{I01A}/04_interface01a_phase_to_threshold_link_requirements.csv", "Defines P0 requirements for F, C, threshold calibration, edge flips, and graph/metric separation.", "explicit requirements", "yes", "Primary acceptance input."),
        input_anchor("IB-IN-04", "INTERFACE01-A material link map", "interface01a", f"{I01A}/05_interface01a_material_sensitivity_link_map.csv", "Nine bounded material/species series links with downstream inference excluded.", "mixed_review", "partial", "Used only to define information-retention and shuffle controls."),
        input_anchor("IB-IN-05", "INTERFACE01-A acceptance tests", "interface01a", f"{I01A}/06_interface01a_acceptance_tests.csv", "Documentation gates for dimensions, claims, bridge visibility, and null tests.", "metadata/test design", "yes", "Not prior physical validation."),
        input_anchor("IB-IN-06", "INTERFACE01-A review items", "interface01a", f"{I01A}/07_interface01a_open_review_items.csv", "Carries formal bridge, geometry readout, legacy-source, unit, and material-injection gaps.", "mixed", "yes", "Open items remain open."),
        input_anchor("IB-IN-07", "INTERFACE01-A run manifest", "interface01a", f"{I01A}/10_interface01a_run_manifest.json", "Records completed skeleton with review items and no new physics run.", "metadata_only", "yes", "Status does not validate candidate physics."),
        input_anchor("IB-IN-08", "Phase-D near-threshold entries", "phase_d", "runs/QSB-D07/local_adjacency_kernel_signature_review_theta_0300/05_d07_near_threshold_entries.csv", "Readable columns show signed K, G=absolute K in rows, theta, margins, adjacency, and a near-threshold band.", "model_units / dimensionless toy-model units", "yes", "Supports Phase-D-local C/R forms only."),
        input_anchor("IB-IN-09", "Phase-D K/margin review", "phase_d", "runs/QSB-D08/analytic_edge_threshold_motif_review_theta_0300/05_d08_k_margin_review.csv", "Readable K, G, theta, and G-minus-theta margin records for selected motifs.", "model_units / dimensionless toy-model units", "yes", "No de-Broglie phase input is present."),
        input_anchor("IB-IN-10", "Phase-D margin function register", "phase_d", "runs/QSB-D09/local_theta_crossing_isolation_primary_edges_theta_0300/05_d09_margin_function_register.csv", "States G_ij(F)=abs(K_ij(F)), theta=0.0300, and absolute-value kink limitations.", "model_units / dimensionless toy-model units", "yes", "F denotes force in this source, not phase-map F(delta_phi)."),
        input_anchor("IB-IN-11", "Phase-D summary manifest", "phase_d", f"{D0X}/12_d0x_run_manifest.json", "Declares theta=0.0300 and model/dimensionless toy-model units without SI conversion.", "not_SI_converted", "yes", "Workpoint is model-bound."),
        input_anchor("IB-IN-12", "MATERIAL01 result anchors", "material01", f"{MAT}/csv/06_result_material_sensitivity_anchor.csv", "Bounded internal material-sensitive phase/wave/signature anchors.", "mixed_review; SI wavelength/energy; mass_u review", "partial", "No numerical mixing with Phase D."),
        input_anchor("IB-IN-13", "INVENTORY01 gap map", "inventory01", f"{INV}/05_legacy_to_interface_gap_map.csv", "Identifies the formal phase-to-threshold and SI/model-unit gaps.", "mixed", "yes", "Gap map is not evidence."),
    ]
    write_csv("01_interface01b_input_anchor_register.csv", ["anchor_id","anchor_label","anchor_class","source_path","read_status","key_content_summary","unit_status","usable_for_interface01b","review_note"], anchors)

    candidates = [
        candidate("F01", "F_phase_map", "complex_phase", "K_ij = exp(i * delta_phi_ij)", "delta_phi_ij", "complex K_ij", "unit circle; |K|=1", "dimensionless", "wrap delta_phi modulo 2*pi", "low before later magnitude; high if followed by |K| alone", "hypothesis_only", "Mathematical working form only.", "Retains phase on the unit circle, but C01 would collapse every value to one."),
        candidate("F02", "F_phase_map", "cosine_projection", "K_ij = cos(delta_phi_ij)", "delta_phi_ij", "real K_ij", "[-1, 1]", "dimensionless", "wrap delta_phi modulo 2*pi; no scale normalization", "medium", "hypothesis_only", "Candidate for later controlled testing, not a selected law.", "Even projection loses orientation under delta_phi -> -delta_phi but retains sign across phase sectors."),
        candidate("F03", "F_phase_map", "absolute_cosine_projection", "K_ij = abs(cos(delta_phi_ij))", "delta_phi_ij", "nonnegative K_ij", "[0, 1]", "dimensionless", "wrap modulo 2*pi", "high", "hypothesis_only", "Review comparator only.", "Absolute value erases cosine sign and merges additional phase classes."),
        candidate("F04", "F_phase_map", "phase_distance_mod", "K_ij = min(d, 2*pi-d)/pi, d=abs(delta_phi_ij mod 2*pi)", "delta_phi_ij", "normalized phase distance", "[0, 1]", "dimensionless", "canonical modulo and distance convention required", "high", "hypothesis_only", "Distance candidate, not automatically a similarity.", "Order is inverted relative to similarity unless a declared 1-K transform is used."),
        candidate("F05", "F_phase_map", "existing_phase_d_kernel_review", "Review existing Phase-D K_ij logic for possible structural analogy; no delta_phi formula found", "delta_phi_ij (not present in Phase-D source)", "K_ij", "source-model range", "model-defined", "requires source-level variable map", "unknown", "review_gap", "Phase-D K cannot be relabeled as a phase kernel.", "Readable Phase-D logic uses a force-dependent theoretical kernel, not delta_phi."),
        candidate("C01", "C_correlation_form", "kernel_magnitude", "G_ij = abs(K_ij)", "K_ij", "G_ij", "[0, infinity) generally; source-bounded in Phase D", "dimensionless if K is dimensionless", "none for bounded K; otherwise scale required", "high for sign/complex phase", "internal_supported", "Internally supported only in the Phase-D toy-model kernel chain.", "Explicitly present in D07-D09; unsuitable after F01 alone because it becomes constant one."),
        candidate("C02", "C_correlation_form", "bounded_similarity", "G_ij = N(K_ij), with N explicitly mapping to [0,1]", "K_ij", "G_ij", "[0, 1]", "dimensionless", "normalizer N, calibration domain, clipping policy", "medium", "hypothesis_only", "Working family until N is fixed and tested.", "For F02, N(K)=(K+1)/2 is a minimal candidate; this is not validated here."),
        candidate("C03", "C_correlation_form", "margin_ready_correlation", "M_ij = G_ij - theta", "G_ij and theta", "signed margin M_ij", "model-dependent around zero", "dimensionless only if G and theta share a scale", "G and theta must share normalization", "low beyond upstream losses", "internal_supported", "Supported as Phase-D margin bookkeeping only.", "Readable Phase-D tables contain G-minus-theta and absolute margins."),
        candidate("C04", "C_correlation_form", "rank_or_knn_relation_support", "rank neighbors by G_ij and retain k or a declared local rank", "G_ij neighborhood", "rank/relation support", "integer rank or binary selection", "dimensionless relation", "tie rule and k selection required", "high for absolute scale", "hypothesis_only", "Alternative review family, not a correlation magnitude replacement by default.", "Can hide threshold-scale instability and requires sensitivity across k."),
        candidate("C05", "C_correlation_form", "existing_phase_d_correlation_review", "G_ij = abs(K_ij) in readable Phase-D D07-D09 artifacts", "Phase-D K_ij(F)", "Phase-D G_ij", "observed model-space nonnegative values", "model-defined/dimensionless toy-model", "source-defined absolute value", "high for K sign", "internal_supported", "Local Phase-D support does not establish a phase-to-correlation rule.", "Useful as downstream compatibility anchor; upstream delta_phi mapping remains absent."),
        candidate("R01", "R_threshold_relation", "hard_threshold", "A_ij = 1 if G_ij >= theta else 0", "G_ij and theta", "A_ij", "{0,1}", "dimensionless relation", "G and theta must share model space; tie rule fixed as inclusive", "high near threshold", "internal_supported", "Supported as a Phase-D toy-model relation only.", "Must be paired with sensitivity and review-band reporting."),
        candidate("R02", "R_threshold_relation", "margin_band", "review if abs(G_ij - theta) <= epsilon", "G_ij, theta, epsilon", "review class / margin flag", "binary flag plus signed margin", "dimensionless in one model space", "epsilon preregistered on same scale", "low; preserves margin", "internal_supported", "Review guard, not an independent physical relation.", "D07 uses a near-threshold band; epsilon selection still needs justification."),
        candidate("R03", "R_threshold_relation", "soft_threshold_review", "S_ij = sigmoid((G_ij-theta)/tau)", "G_ij, theta, tau", "soft relation weight", "(0,1)", "dimensionless", "tau > 0 on same scale as G and theta", "medium", "hypothesis_only", "Review-only smooth alternative.", "Tau adds a free scale and must not be tuned post hoc."),
        candidate("R04", "R_threshold_relation", "rank_threshold_review", "A_ij = 1 for declared k-nearest/rank-selected neighbors", "G_ij neighborhood and k", "A_ij", "{0,1}", "dimensionless relation", "k and tie rule preregistered", "high for magnitude/margin", "hypothesis_only", "Review-only topology-control alternative.", "Not directly equivalent to the Phase-D theta motifs."),
        candidate("R05", "R_threshold_relation", "existing_phase_d_threshold", "theta = 0.0300; A_ij = 1[G_ij >= theta] in Phase-D workpoint", "Phase-D G_ij", "Phase-D A_ij", "{0,1}", "dimensionless/model-space threshold", "source workpoint only", "high near threshold", "internal_supported", "Calibrated toy-model workpoint, not universal and not SI.", "Compatibility anchor only; no transfer to a new phase-derived G scale without calibration."),
    ]
    write_csv("02_interface01b_bridge_candidate_registry.csv", ["candidate_id","candidate_group","candidate_label","formal_definition","input_quantity","output_quantity","expected_range","dimension_status","normalization_need","information_loss_risk","source_support","claim_boundary","review_note"], candidates)

    checks = []
    for index, row in enumerate(candidates, 1):
        cid = row["candidate_id"]
        if cid.startswith("F"):
            periodicity = "Explicit 2*pi periodicity or canonical modulo handling required."
            expected_unit, expected_dim = "dimensionless angle input; dimensionless output", "1"
        else:
            periodicity = "Inherited from upstream F; candidate itself does not repair phase handling."
            expected_unit, expected_dim = "dimensionless/model-space quantities", "1 or declared model dimension"
        status = "review" if cid == "F05" else "partial" if cid in {"C02","C04","R03","R04","R05"} else "pass"
        checks.append({
            "check_id": f"ND-{index:02d}", "candidate_id": cid,
            "quantity_or_relation": f"{row['input_quantity']} -> {row['output_quantity']}",
            "required_normalization": row["normalization_need"], "expected_unit": expected_unit,
            "expected_dimension": expected_dim, "phase_periodicity_handling": periodicity,
            "range_check": row["expected_range"],
            "allowed_operation": "Evaluate only inside one declared dimension/normalization space.",
            "forbidden_operation": "No direct numerical mixing of MATERIAL01 SI/mass fields with Phase-D model-space values.",
            "status": status, "review_note": row["review_note"],
        })
    checks.extend([
        {"check_id":"ND-16","candidate_id":"PIPELINE-CROSS","quantity_or_relation":"MATERIAL01 quantities versus Phase-D G/theta","required_normalization":"An explicit dimension-safe bridge would be required before any numerical contact.","expected_unit":"separate SI, atomic-mass-review, and model-space channels","expected_dimension":"separate declared dimensions","phase_periodicity_handling":"Not applicable until an operational phase map is defined.","range_check":"No shared range is assumed.","allowed_operation":"Use MATERIAL01 as a bounded material-sensitivity anchor and Phase D as a structural compatibility anchor.","forbidden_operation":"Do not insert lambda_db, energy_j, or mass_u directly into Phase-D theta comparisons.","status":"pass","review_note":"Separation rule is explicit; no bridge is supplied."},
        {"check_id":"ND-17","candidate_id":"GEOMETRY-GUARD","quantity_or_relation":"A_ij or graph distance versus physical metric","required_normalization":"No conversion defined.","expected_unit":"binary relation / graph or model distance","expected_dimension":"dimensionless or model-defined","phase_periodicity_handling":"Not applicable.","range_check":"Model-specific only.","allowed_operation":"Evaluate graph and neighborhood diagnostics as model structures.","forbidden_operation":"Do not report graph distance as an SI spacetime interval or physical metric.","status":"pass","review_note":"Geometric readout remains outside this candidate comparison."},
    ])
    write_csv("03_interface01b_normalization_dimension_checks.csv", ["check_id","candidate_id","quantity_or_relation","required_normalization","expected_unit","expected_dimension","phase_periodicity_handling","range_check","allowed_operation","forbidden_operation","status","review_note"], checks)

    nulls = [
        {"null_model_id":"N01","null_model_label":"trivial_uniform_phase","purpose":"Detect candidates that create nontrivial structure from identical phases alone.","target_candidate_group":"F_phase_map; C_correlation_form; R_threshold_relation","required_input":"Uniform phi_i under preregistered phase value and graph size.","expected_failure_or_control_behavior":"Pipeline should yield the analytically expected uniform K/G pattern; any nontrivial edges must be explained by declared weights, not phase variation.","risk_if_not_tested":"Trivial coherence may be mistaken for informative relational structure.","priority":"P0","can_run_now":"design_only","review_note":"No new data generated in INTERFACE01-B."},
        {"null_model_id":"N02","null_model_label":"random_phase_shuffle","purpose":"Test whether candidate structure exceeds randomized phase assignment under preserved marginals.","target_candidate_group":"F_phase_map; C_correlation_form; R_threshold_relation","required_input":"A future real or declared phase vector and fixed permutation protocol.","expected_failure_or_control_behavior":"Recommended pipeline must predeclare a statistic and distinguish structured input from shuffle distribution without post-hoc threshold selection.","risk_if_not_tested":"Random phase patterns may produce similar threshold graphs.","priority":"P0","can_run_now":"design_only","review_note":"No suitable operational phase input exists in current anchors."},
        {"null_model_id":"N03","null_model_label":"material_label_shuffle","purpose":"Test whether materialsensitive retention depends on physical records rather than labels.","target_candidate_group":"full pipeline material injection","required_input":"Reviewed MATERIAL01 records plus an explicit material-to-phase/weight map.","expected_failure_or_control_behavior":"Material-linked statistic should degrade under label permutation if the map carries nontrivial material information.","risk_if_not_tested":"Label association may masquerade as material sensitivity.","priority":"P0","can_run_now":"design_only","review_note":"Injection map is currently absent."},
        {"null_model_id":"N04","null_model_label":"mass_order_only_control","purpose":"Separate mass ordering from wave/signature information.","target_candidate_group":"material-conditioned F or weights","required_input":"Reviewed isotope series and a preregistered mass-only baseline.","expected_failure_or_control_behavior":"Candidate must report whether it adds information beyond mass rank; no automatic downstream geometry inference.","risk_if_not_tested":"A trivial monotonic mass proxy may be misread as phase/interface structure.","priority":"P0","can_run_now":"design_only","review_note":"mass_u conversion and derived-row review remain active."},
        {"null_model_id":"N05","null_model_label":"threshold_randomization_or_sweep_guard","purpose":"Detect conclusions driven by arbitrary or post-hoc theta choice.","target_candidate_group":"R_threshold_relation","required_input":"Fixed G matrix plus preregistered theta/epsilon grid and stability statistic.","expected_failure_or_control_behavior":"Recommendation fails if the claimed motif exists only at an isolated tuned threshold without a justified stability window.","risk_if_not_tested":"Threshold artifacts may be called mechanism signatures.","priority":"P0","can_run_now":"design_only","review_note":"Phase D has local threshold artifacts, but no new sweep is run here."},
        {"null_model_id":"N06","null_model_label":"pipeline_identity_control","purpose":"Audit information loss at each F/C/R transformation.","target_candidate_group":"F_phase_map; C_correlation_form; R_threshold_relation","required_input":"Future declared phase inputs with identity labels retained only for audit.","expected_failure_or_control_behavior":"Each merge of distinct phase classes must be enumerated; F01+C01 must flag total collapse to G=1.","risk_if_not_tested":"Absolute values, projection, normalization, or rank may silently erase the target signal.","priority":"P0","can_run_now":"design_only","review_note":"Analytic design check; no evidence dataset produced."},
    ]
    write_csv("04_interface01b_null_model_designs.csv", ["null_model_id","null_model_label","purpose","target_candidate_group","required_input","expected_failure_or_control_behavior","risk_if_not_tested","priority","can_run_now","review_note"], nulls)

    criteria = [
        ("AC01","Dimensions contract satisfied?"), ("AC02","Range and normalization explicit?"),
        ("AC03","Can distinguish coherent from random/trivial in principle?"),
        ("AC04","Retains material-sensitive information or marks loss?"),
        ("AC05","Can connect to Phase-D threshold/edge motifs?"),
        ("AC06","Avoids SI/model-unit mixing?"), ("AC07","Has an explicit null model?"),
        ("AC08","Has an explicit abort criterion?"), ("AC09","Remains inside claim boundary?"),
    ]
    acceptance = []
    range_review = {"F05","C02","C04","R03","R04","R05"}
    phase_risk = {"F03","F04","F05","C01","C04","C05","R04","R05"}
    phase_connect = {"C01","C03","C05","R01","R02","R05"}
    for cid_row in candidates:
        cid = cid_row["candidate_id"]
        for criterion_id, label in criteria:
            status = "pass"
            note = "Candidate is bounded by the registry and explicit future-test requirements."
            if criterion_id == "AC01" and cid in {"F05","C02","R03","R05"}:
                status, note = "partial", "Model scale or free normalization parameter remains unresolved."
            elif criterion_id == "AC02" and cid in range_review:
                status, note = "partial", "Normalizer, free scale, rank choice, or transfer calibration is not fixed."
            elif criterion_id == "AC03":
                status = "partial" if cid not in phase_risk else "review_gap"
                note = "Requires N01/N02; information-loss risks in the registry must be tested in combination."
            elif criterion_id == "AC04":
                status, note = "not_tested", "No material-to-phase/kernel injection map exists; N03/N04 are design-only."
            elif criterion_id == "AC05":
                status = "partial" if cid in phase_connect else "review_gap"
                note = "Phase-D compatibility is local/model-bound and does not supply the upstream phase map."
            elif criterion_id == "AC06":
                status, note = "pass", "Candidate use is restricted to a declared dimensionless/model space; cross-space insertion is forbidden."
            elif criterion_id == "AC07":
                status, note = "partial", "A matching null-model design exists but has not been executed."
            elif criterion_id == "AC08":
                status, note = "pass", "Applicable abort criteria are registered; execution remains future work."
            elif criterion_id == "AC09":
                status, note = "pass", "Candidate is labeled as a working/review form, not a confirmed physical law."
            acceptance.append({
                "criterion_id": criterion_id, "criterion_label": label, "candidate_id": cid,
                "test_question": label, "pass_condition": "Declared requirement is met under preregistered inputs and controls.",
                "fail_condition": "Requirement is violated, unresolved without review marking, or only met by post-hoc tuning.",
                "current_status": status, "evidence_anchor": cid_row["source_support"],
                "blocks_recommendation": "yes" if status in {"fail","review_gap"} and criterion_id in {"AC01","AC02","AC06","AC09"} else "partial" if status in {"partial","review_gap","not_tested"} else "no",
                "review_note": note,
            })
    write_csv("05_interface01b_candidate_acceptance_matrix.csv", ["criterion_id","criterion_label","candidate_id","test_question","pass_condition","fail_condition","current_status","evidence_anchor","blocks_recommendation","review_note"], acceptance)

    aborts = [
        {"abort_id":"AB01","abort_label":"Undeclared SI/model-space mixing","trigger_condition":"A candidate inserts MATERIAL01 wavelength, energy, or mass fields directly into Phase-D K, G, theta, or distance operations.","why_it_matters":"The quantities do not share a validated dimensional map.","recommended_action":"Stop the candidate path and require an explicit dimension-safe transformation and validation plan.","severity":"high","review_note":"No such bridge is provided here."},
        {"abort_id":"AB02","abort_label":"Post-hoc threshold dependence","trigger_condition":"The target motif appears only after outcome-driven theta, epsilon, tau, or k tuning and lacks a preregistered stability window.","why_it_matters":"An arbitrary threshold can manufacture edges and flips.","recommended_action":"Reject the tuned result; rerun only under a preregistered sweep and null comparison.","severity":"high","review_note":"R01-R05 all require parameter discipline."},
        {"abort_id":"AB03","abort_label":"Material information destroyed","trigger_condition":"Distinct reviewed material/isotope inputs become indistinguishable before the declared target statistic without an intentional loss analysis.","why_it_matters":"The candidate cannot carry the materialsensitive side of the hypothesis.","recommended_action":"Reject for the material bridge or retain only as a documented control.","severity":"high","review_note":"F03/F04 and magnitude/rank operations need special audit."},
        {"abort_id":"AB04","abort_label":"Trivial/random phase indistinguishability","trigger_condition":"The pipeline cannot distinguish its preregistered structured-phase statistic from uniform or shuffled-phase controls.","why_it_matters":"Threshold structure may be generic or trivial rather than phase-informative.","recommended_action":"Reject the candidate combination for mechanism testing.","severity":"high","review_note":"F01+C01 analytically collapses to constant magnitude and is rejected for now."},
        {"abort_id":"AB05","abort_label":"Graph-to-metric identity leap","trigger_condition":"Adjacency, rank, or graph distance is interpreted as a physical spacetime metric without independent validation.","why_it_matters":"Relational structure and physical metric identity are different claims.","recommended_action":"Stop geometric interpretation; return to model-level graph diagnostics.","severity":"high","review_note":"Geometry is outside INTERFACE01-B candidate validation."},
        {"abort_id":"AB06","abort_label":"Unsupported spacetime/gravity conclusion","trigger_condition":"Candidate output is presented as establishing physical spacetime emergence, gravity, or a completed theory bridge.","why_it_matters":"No current input supports those conclusions.","recommended_action":"Fail claim-boundary check and correct the interpretation before continuation.","severity":"high","review_note":"Working forms are not confirmed laws."},
        {"abort_id":"AB07","abort_label":"Unavailable legacy dependency","trigger_condition":"Recommendation depends on a missing manuscript/archive formula without explicit review-gap status and source verification.","why_it_matters":"The candidate would not be auditable or reproducible from available inputs.","recommended_action":"Set insufficient_input or review_gap until the authoritative source is inspected.","severity":"medium","review_note":"F05 remains review_gap."},
    ]
    write_csv("06_interface01b_abort_criteria.csv", ["abort_id","abort_label","trigger_condition","why_it_matters","recommended_action","severity","review_note"], aborts)

    recommendations = [
        {"recommendation_id":"REC-01","candidate_combination":"Cosine -> affine bounded similarity -> hard threshold with mandatory margin-band audit","F_candidate":"F02","C_candidate":"C02","R_candidate":"R01","recommendation_status":"recommended_for_next_test","why":"Small real-valued periodic chain with explicit sign sectors, bounded G=(K+1)/2 candidate, and direct threshold compatibility; no physical preference is established.","normalization_summary":"delta_phi modulo 2*pi; K in [-1,1]; candidate N(K)=(K+1)/2 gives G in [0,1]; theta must be calibrated in that new G space and is not inherited numerically from Phase D.","null_model_requirements":"N01, N02, N03, N04, N05, N06; R02 margin-band reporting is mandatory.","claim_boundary":"Working hypothesis for a future controlled test only.","next_step":"INTERFACE01-C may preregister a tiny analytic/toy test design with fixed phase inputs, theta protocol, epsilon, and abort rules; do not use synthetic output as evidence.","review_note":"Material injection point remains unspecified; recommendation is conditional."},
        {"recommendation_id":"REC-02","candidate_combination":"Normalized phase distance -> reviewed similarity transform -> hard threshold plus margin band","F_candidate":"F04","C_candidate":"C02","R_candidate":"R01","recommendation_status":"keep_as_review","why":"Offers an explicit circular distance but discards orientation and requires inversion such as G=1-F before it behaves as similarity.","normalization_summary":"F04 in [0,1]; candidate G=1-F04 must be declared; theta requires new calibration.","null_model_requirements":"N01, N02, N03, N05, N06.","claim_boundary":"Comparator only; no preferred physical interpretation.","next_step":"Retain as one orientation-blind control in a future preregistered comparison.","review_note":"High information-loss risk blocks primary recommendation."},
        {"recommendation_id":"REC-03","candidate_combination":"Existing Phase-D K -> absolute magnitude -> theta=0.0300","F_candidate":"F05","C_candidate":"C05","R_candidate":"R05","recommendation_status":"insufficient_input","why":"C and R are internally readable in Phase D, but the upstream Phase-D kernel is force-dependent and no delta_phi-to-K map is available.","normalization_summary":"Valid only inside the existing Phase-D toy-model space; no transfer to MATERIAL01 or a phase-derived K scale.","null_model_requirements":"N01, N02, N05, N06 after an operational phase map exists.","claim_boundary":"Structural compatibility anchor only.","next_step":"Do not promote until the upstream variable map and source semantics are explicitly established.","review_note":"Phase-D F denotes force; it is not F(delta_phi)."},
        {"recommendation_id":"REC-04","candidate_combination":"Complex phase -> kernel magnitude -> hard threshold","F_candidate":"F01","C_candidate":"C01","R_candidate":"R01","recommendation_status":"reject_for_now","why":"For unit-amplitude exp(i*delta_phi), G=abs(K)=1 for every pair, so phase distinctions collapse before thresholding.","normalization_summary":"No normalization repairs the lost phase after magnitude-only C01.","null_model_requirements":"N01 and N06 expose the collapse analytically.","claim_boundary":"Rejection concerns this combination, not complex-phase representations generally.","next_step":"Only reconsider with a correlation operator that retains relative complex information across samples or paths.","review_note":"No data run is needed to identify the definitional collapse."},
    ]
    write_csv("07_interface01b_recommended_candidate_set.csv", ["recommendation_id","candidate_combination","F_candidate","C_candidate","R_candidate","recommendation_status","why","normalization_summary","null_model_requirements","claim_boundary","next_step","review_note"], recommendations)

    reviews = [
        {"review_id":"IB-R01","source_path":"runs/QSB-D09/local_theta_crossing_isolation_primary_edges_theta_0300/05_d09_margin_function_register.csv","issue_type":"upstream_variable_mismatch","description":"Readable Phase-D kernel is force-dependent; no delta_phi-to-K relation is supplied.","severity":"high","recommended_resolution":"Keep F05 as review_gap and define a separate operational phase map.","blocks_interface01_next":"yes"},
        {"review_id":"IB-R02","source_path":f"{I01A}/02_interface01a_quantity_dimension_contract.csv","issue_type":"phase_input_absent","description":"No reviewed operational phase dataset or material-to-phase map is available for candidate execution.","severity":"high","recommended_resolution":"Define source, indices, modulo convention, and material injection before testing.","blocks_interface01_next":"yes"},
        {"review_id":"IB-R03","source_path":f"{MAT}/csv/06_result_material_sensitivity_anchor.csv","issue_type":"material_injection_gap","description":"Material-sensitive anchors do not identify whether dependence enters phi, weights, K, G, or calibration.","severity":"high","recommended_resolution":"Predeclare competing injection points and label/mass controls.","blocks_interface01_next":"partial"},
        {"review_id":"IB-R04","source_path":f"{D0X}/12_d0x_run_manifest.json","issue_type":"theta_transfer_gap","description":"theta=0.0300 belongs to the Phase-D toy-model scale and cannot be transferred to a newly normalized G.","severity":"high","recommended_resolution":"Calibrate any future theta only within the new preregistered G space and report sensitivity.","blocks_interface01_next":"yes"},
        {"review_id":"IB-R05","source_path":"02_interface01b_bridge_candidate_registry.csv#C02","issue_type":"normalizer_selection","description":"Bounded-similarity normalizer N is a family until its domain and clipping policy are fixed.","severity":"medium","recommended_resolution":"For F02, test the minimal affine map (K+1)/2 against preregistered alternatives only if justified.","blocks_interface01_next":"partial"},
        {"review_id":"IB-R06","source_path":"02_interface01b_bridge_candidate_registry.csv#R02-R04","issue_type":"free_parameter_control","description":"epsilon, tau, and k can become post-hoc tuning parameters.","severity":"high","recommended_resolution":"Preregister parameter rules and trigger AB02 on outcome-driven tuning.","blocks_interface01_next":"yes"},
        {"review_id":"IB-R07","source_path":"04_interface01b_null_model_designs.csv","issue_type":"null_models_not_executed","description":"All six null models are designs because no operational phase input is available.","severity":"high","recommended_resolution":"Execute only in a later authorized test block with fixed inputs and statistics.","blocks_interface01_next":"yes"},
        {"review_id":"IB-R08","source_path":"07_interface01b_recommended_candidate_set.csv#REC-01","issue_type":"conditional_recommendation","description":"Primary recommendation is based on minimality and auditability, not empirical superiority.","severity":"medium","recommended_resolution":"Treat REC-01 as one small preregistered candidate set, not a winner.","blocks_interface01_next":"no"},
    ]
    write_csv("08_interface01b_open_review_items.csv", ["review_id","source_path","issue_type","description","severity","recommended_resolution","blocks_interface01_next"], reviews)

    assessment = f"""# QSB-INTERFACE01-B Final Assessment

## Zweck
INTERFACE01-B ordnet Arbeitsformen fuer die offene interne Bruecke `delta_phi_ij -> K_ij -> G_ij -> theta -> A_ij`. Es wurden keine neuen Evidenzdaten und keine Simulation erzeugt.

## Input-Sufficiency
Status: `sufficient_for_candidate_comparison_not_execution`

INTERFACE01-A liefert Dimensionsvertrag, Pfeil-Gaps und Akzeptanzanforderungen. Phase D liefert lesbar `G_ij=abs(K_ij)`, Margins, harte Adjazenz und `theta=0.0300` im eigenen Toy-Modellraum. Ein operationaler Phaseninput und eine Material-zu-Phase-/Kernel-Abbildung fehlen; Kandidaten koennen deshalb geordnet, aber nicht empirisch bewertet werden.

## Kandidatengruppen
- F: komplexe Phase, Kosinusprojektion, absolute Kosinusprojektion, normierte Kreisdistanz und Phase-D-Kernel-Review.
- C: Kernelbetrag, explizit normierte Aehnlichkeit, Margin, Rang/kNN und Phase-D-Korrelationsreview.
- R: harte Schwelle, Review-Band, weiche Schwelle, Rangregel und Phase-D-Arbeitspunkt.

F05 ist kein vorhandener `delta_phi`-Kandidat: Der lesbare Phase-D-Kernel ist force-abhaengig. C05/R05 sind nur innerhalb der Phase-D-Kette intern anschlussfaehig.

## Normalisierung und Dimensionen
`delta_phi`, K, G, theta und A muessen dimensionslos oder explizit modellraumdefiniert bleiben. MATERIAL01-SI-/Massengroessen werden nicht numerisch in Phase-D-Modelleinheiten eingesetzt. Ein neues normiertes G braucht eine eigene theta-Kalibrierung; `0.0300` wird nicht uebertragen.

F02 liefert K in `[-1,1]`; die affine Arbeitsform `(K+1)/2` waere ein minimaler C02-Kandidat in `[0,1]`. Diese Wahl ist noch nicht validiert. F03/F04 sowie Betrag-/Rangformen besitzen erhoehtes Informationsverlustrisiko.

## Nullmodelle
Sechs P0-Designs decken uniforme Phase, Phasen-Shuffle, Materiallabel-Shuffle, Mass-order-only, Threshold-Sweep-Guard und Pipeline-Identitaet ab. Sie wurden nicht ausgefuehrt, weil kein operationaler Phaseninput autorisiert oder vorhanden ist.

## Abbruchkriterien
Abbruch erfolgt bei undeklarierter SI/Modellraum-Mischung, Post-hoc-Schwellentuning, Verlust der Materialsensitivitaet, fehlender Trennung von trivialer/zufaelliger Phase, Graph-zu-Metrik-Identitaetssprung, ungestuetzten Raumzeit-/Gravitationsschluessen oder ungepruefter Legacy-Abhaengigkeit.

## Empfohlenes kleines Kandidatenset
`F02 -> C02 -> R01` wird fuer einen spaeteren kleinen Test empfohlen, mit `R02` als verpflichtender Margin-Auditspur. Empfehlung bedeutet hier: geringe Komplexitaet, expliziter Wertebereich und gute Auditierbarkeit. Sie bedeutet weder empirischen Sieg noch physikalische Bestaetigung.

F04/C02/R01 bleibt ein orientierungsblinder Review-Komparator. F05/C05/R05 hat unzureichenden Upstream-Input. F01/C01/R01 wird vorerst verworfen, weil `abs(exp(i*delta_phi))=1` alle Phasenunterschiede vor der Schwelle beseitigt.

## Zentrale Gaps
- operationaler und provenance-gesicherter Phaseninput,
- materialabhaengige Injektionsstelle,
- Auswahl/Validierung des Normalisierers,
- theta-/epsilon-Protokoll im neuen G-Raum,
- ausgefuehrte Nullmodelle und vorab definierte Zielstatistik.

## Claim-Grenze
{CLAIM}

MATERIAL01 und Phase D sind komplementaere interne Anker. Keine Kandidatenform ist hier als physikalisches Gesetz bestaetigt.

## Naechster Schritt
INTERFACE01-C sollte nur als preregistrierter Minimaltest geplant werden: feste kleine Phaseneingaenge, klarer Material-Injektionsstatus, F02/C02/R01 plus F04-Komparator, R02-Audit, alle sechs Nullmodelle, feste Statistik und die sieben Abbruchkriterien. Ob synthetische Kontrolldaten erzeugt werden duerfen, muss ein spaeterer Auftrag ausdruecklich festlegen.
"""
    (OUTPUT / "09_interface01b_final_assessment.md").write_text(assessment, encoding="utf-8")

    required_missing = sum(row["read_status"] == "missing" for row in anchors)
    status = "interface01b_candidate_bridge_forms_completed_with_review_items"
    sufficiency = "sufficient_for_candidate_comparison_not_execution"
    if required_missing:
        status = "interface01b_candidate_bridge_forms_partial_inputs"
        sufficiency = "partial_inputs"
    manifest = {
        "run_id": "QSB-INTERFACE01B", "status": status,
        "output_dir": "runs/QSB-INTERFACE01B/candidate_bridge_forms",
        "input_sufficiency": sufficiency, "input_anchors": len(anchors),
        "bridge_candidates": len(candidates), "normalization_checks": len(checks),
        "null_models": len(nulls), "acceptance_matrix_rows": len(acceptance),
        "abort_criteria": len(aborts), "recommended_candidate_sets": len(recommendations),
        "review_items": len(reviews), "mutated_existing_files": False,
        "generated_synthetic_evidence": False, "new_simulation_performed": False,
        "phase_d_rescan_performed": False, "deep_research_performed": False,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CLAIM,
    }
    (OUTPUT / "10_interface01b_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
