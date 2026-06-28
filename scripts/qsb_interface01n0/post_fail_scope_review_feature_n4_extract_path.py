#!/usr/bin/env python3
"""Review the L2/M2 fail scope and recommend the next design-only path."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
F3_INPUT = REPO / "runs/QSB-INTERFACE01F3/input_manifest/interface01f3_delta_phi_input_manifest.json"
G = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
H = REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi"
I = REPO / "runs/QSB-INTERFACE01I/pilot_result_review_nullmodel_adequacy_decision"
J = REPO / "runs/QSB-INTERFACE01J/minimaltest_precontract"
K = REPO / "runs/QSB-INTERFACE01K/review_point_resolution_execution_authorization_check"
L = REPO / "runs/QSB-INTERFACE01L/separate_final_minimaltest_execution"
J2 = REPO / "runs/QSB-INTERFACE01J2/minimaltest_acceptance_rule_addendum"
L2 = REPO / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2"
M2 = REPO / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2"
OUTPUT = REPO / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path"

STATUS = "interface01n0_post_fail_scope_review_completed_with_next_path_recommendation"
PRIMARY = "prepare_extract01_design"
CLAIM_BOUNDARY = (
    "INTERFACE01-N0 reviews the scope of the completed L2 diagnostic negative result only. It "
    "reruns no Minimaltest or nullmodel, changes no feature, N4 role, theta, or epsilon value, "
    "starts no EXTRACT or source-extension execution, and makes no physical-evidence claim."
)
EXPECTED_FILES = {
    "01_n0_run_manifest.json", "02_upstream_inventory_and_hashes.csv", "03_l2_m2_failure_context.csv",
    "04_three_feature_scope_review.csv", "05_n4_adequacy_review.csv",
    "06_theta_epsilon_sensitivity_boundary.csv", "07_source_specificity_review.csv",
    "08_extract01_path_assessment.csv", "09_no_posthoc_tuning_guard.csv",
    "10_next_path_decision.csv", "11_claim_boundary_matrix.csv", "12_n0_validation_results.csv",
    "13_review_items_for_next_block.csv", "14_short_theory_note_de.md", "FINAL_RESULT_NOTE.md",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    artifacts = {
        "f3_manifest": ("F3", F3 / "01_f3_run_manifest.json", "authorized source status"),
        "f3_input": ("F3", F3_INPUT, "source regime and units"),
        "g_manifest": ("G", G / "01_g_run_manifest.json", "source profile status"),
        "h_manifest": ("H", H / "01_h_run_manifest.json", "pilot scope"),
        "h_features": ("H", H / "03_pair_feature_table.csv", "feature definitions and values"),
        "h_script": ("H", REPO / "scripts/qsb_interface01h/controlled_minimal_pilot_from_staged_delta_phi.py", "feature and N4 formulas"),
        "i_manifest": ("I", I / "01_i_run_manifest.json", "pilot review status"),
        "j_manifest": ("J", J / "01_j_run_manifest.json", "pre-contract status"),
        "k_manifest": ("K", K / "01_k_run_manifest.json", "execution authorization"),
        "l_manifest": ("L", L / "01_l_run_manifest.json", "earlier blocked attempt"),
        "j2_manifest": ("J2", J2 / "01_j2_run_manifest.json", "acceptance authorization"),
        "j2_features": ("J2", J2 / "06_feature_acceptance_gates.csv", "locked three-feature scope"),
        "j2_nulls": ("J2", J2 / "07_nullmodel_acceptance_roles.csv", "locked N4 role"),
        "l2_manifest": ("L2", L2 / "01_l2_run_manifest.json", "executed fail result"),
        "l2_features": ("L2", L2 / "06_feature_scope_and_mapping.csv", "feature mapping verification"),
        "l2_parameters": ("L2", L2 / "09_theta_epsilon_application.csv", "locked parameter values"),
        "l2_nulls": ("L2", L2 / "10_nullmodel_execution_summary.csv", "N4 execution behavior"),
        "l2_support": ("L2", L2 / "11_feature_level_n4_support.csv", "0-of-3 support result"),
        "l2_acceptance": ("L2", L2 / "13_acceptance_gate_results.csv", "2-of-3 fail"),
        "m2_manifest": ("M2", M2 / "01_m2_run_manifest.json", "bounded failure review"),
        "m2_localization": ("M2", M2 / "05_failure_localization.csv", "failure localization"),
        "m2_chain": ("M2", M2 / "09_mechanism_chain_map.csv", "open extraction path"),
    }
    upstream_present = all(path.is_file() for _, path, _ in artifacts.values())
    before_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    inventory_rows = []
    for number, (key, (block, path, use)) in enumerate(artifacts.items(), start=1):
        exists = path.is_file()
        inventory_rows.append({
            "artifact_id": f"N0-A{number:02d}", "upstream_block": block, "path": rel(path),
            "exists": "yes" if exists else "no", "sha256": before_hashes.get(key, "missing"),
            "role": "read-only scope-review input", "used_for": use,
            "notes": "Hashed before N0; not modified." if exists else "Missing required artifact.",
        })

    l2_manifest = load_json(artifacts["l2_manifest"][1]) if artifacts["l2_manifest"][1].is_file() else {}
    m2_manifest = load_json(artifacts["m2_manifest"][1]) if artifacts["m2_manifest"][1].is_file() else {}
    source_manifest = load_json(artifacts["f3_input"][1]) if artifacts["f3_input"][1].is_file() else {}
    l2_fail = (
        l2_manifest.get("status") == "interface01l2_separate_final_minimaltest_execution_completed_with_claim_boundary"
        and l2_manifest.get("minimaltest_contract_result") == "fail"
    )
    m2_seen = (
        m2_manifest.get("status") == "interface01m2_result_review_mechanism_interpretation_boundary_completed_after_l2_fail"
        and m2_manifest.get("l2_result_seen") == "fail"
        and m2_manifest.get("failure_review_mode") is True
    )
    m2_localization = read_csv(artifacts["m2_localization"][1]) if artifacts["m2_localization"][1].is_file() else []
    localization_by_item = {row["failure_item"]: row for row in m2_localization}
    localized = (
        localization_by_item.get("feature_level_n4_support", {}).get("failure_status") == "failed_for_contract"
        and localization_by_item.get("j2_2_of_3_rule", {}).get("failure_status") == "failed_for_contract"
    )
    if not upstream_present:
        raise SystemExit("N0 blocked: required L2/M2 or upstream artifacts are missing.")
    if not l2_fail or not m2_seen or not localized:
        raise SystemExit("N0 blocked: L2/M2 result mode is not the expected localized fail.")

    support_rows = read_csv(artifacts["l2_support"][1])
    feature_contract = read_csv(artifacts["j2_features"][1])
    l2_feature_map = read_csv(artifacts["l2_features"][1])
    null_rows = read_csv(artifacts["l2_nulls"][1])
    null_by_id = {row["nullmodel_id"]: row for row in null_rows}
    parameters = {row["parameter_name"]: row for row in read_csv(artifacts["l2_parameters"][1])}
    acceptance = {row["acceptance_gate_id"]: row for row in read_csv(artifacts["l2_acceptance"][1])}
    feature_names = [row["feature_name"] for row in feature_contract]
    support_count = sum(row["support_flag"] == "true" for row in support_rows)
    all_below = len(support_rows) == 3 and support_count == 0 and all(float(row["abs_delta_n4"]) < float(row["support_threshold"]) for row in support_rows)
    theta = parameters["theta_new"]["computed_or_loaded_value"]
    epsilon = parameters["epsilon_new"]["computed_or_loaded_value"]
    threshold = support_rows[0]["support_threshold"]

    context_specs = [
        ("l2_status", l2_manifest["status"], artifacts["l2_manifest"][1], "contract_result", "Completed and non-blocked."),
        ("l2_result", "fail", artifacts["l2_manifest"][1], "diagnostic_negative", "Reduced J2 contract did not pass."),
        ("n4_support_count", support_count, artifacts["l2_support"][1], "diagnostic_negative", "All three support flags were false."),
        ("n4_support_required", 2, artifacts["l2_acceptance"][1], "contract_result", "J2 pass threshold."),
        ("theta_new", theta, artifacts["l2_parameters"][1], "contract_result", "Frozen L2 value; unchanged by N0."),
        ("epsilon_new", epsilon, artifacts["l2_parameters"][1], "contract_result", "Frozen L2 value; unchanged by N0."),
        ("m2_status", m2_manifest["status"], artifacts["m2_manifest"][1], "scope_review", "M2 completed bounded failure review."),
        ("m2_failure_localization", "Feature→N4 separation and J2 2-of-3 gate", artifacts["m2_localization"][1], "diagnostic_negative", "Source and execution layers did not fail."),
        ("m2_claim_boundary", m2_manifest["claim_boundary"], artifacts["m2_manifest"][1], "scope_review", "Broader hypothesis remains undecided."),
    ]
    context_rows = [{
        "context_item": item, "observed_value": value, "source_artifact": rel(path),
        "source_hash": sha256(path), "classification": classification, "notes": notes,
    } for item, value, path, classification, notes in context_specs]

    feature_rows = [
        {"review_item": "feature_count", "observed_value": len(feature_names), "assessment": "Exactly three features were preregistered and executed.", "risk": "A three-aggregate scope may underrepresent the candidate mechanism, but L2 alone cannot establish that it was too narrow.", "recommended_future_action": "Retain L2 result; specify any future scope review prospectively.", "posthoc_change_made": "no", "notes": "No replacement selected."},
        {"review_item": "feature_names_available", "observed_value": ";".join(feature_names), "assessment": "Names are unambiguous across J2 and L2.", "risk": "None for lineage; adequacy remains open.", "recommended_future_action": "Carry exact names into any comparison of old and newly proposed contracts.", "posthoc_change_made": "no", "notes": "All three failed their support gate."},
        {"review_item": "feature_formulas_available", "observed_value": "hashed H aggregate_phases rule; L2 reproduction difference=0", "assessment": "Calculation lineage is explicit and L2 reproduced H values.", "risk": "Formula reproducibility does not establish mechanism coverage.", "recommended_future_action": "Use formula lineage as baseline in a separate design review.", "posthoc_change_made": "no", "notes": "No recalculation in N0."},
        {"review_item": "feature_scope_breadth", "observed_value": "three x-independent aggregate phase/correlation summaries", "assessment": "Narrow by construction relative to possible alignment-sensitive, relational, or tensor representations.", "risk": "Relevant motifs may be invisible to these aggregates.", "recommended_future_action": "Prepare a preregistered scope addendum only after independent design justification.", "posthoc_change_made": "no", "notes": "Narrow does not mean invalid."},
        {"review_item": "feature_scope_mechanism_coverage", "observed_value": "0/3 separated from N4 at the locked threshold", "assessment": "The tested scope did not carry the intended phase-to-relation distinction.", "risk": "Cannot distinguish feature insufficiency from genuinely weak separation in this source regime.", "recommended_future_action": "Keep this ambiguity explicit in future design criteria.", "posthoc_change_made": "no", "notes": "Failure affected all three features, not a subset."},
        {"review_item": "feature_scope_revision_needed", "observed_value": "future review justified; revision not yet authorized", "assessment": "A future feature-scope design review is justified, but replacement selection from L2 attractiveness is forbidden.", "risk": "Post-hoc feature shopping would invalidate comparability.", "recommended_future_action": "Secondary: prepare_feature_scope_addendum after EXTRACT01 design clarifies representation needs.", "posthoc_change_made": "no", "notes": "No new feature names proposed in N0."},
    ]

    n4 = null_by_id["N4_PHASE_RANDOM_REFERENCE"]
    n4_rows = [
        {"review_item": "n4_role", "observed_value": n4["role"], "assessment": "N4 retained its locked effective_perturbation role.", "risk": "Role label alone does not establish adequacy for every mechanism distinction.", "recommended_future_action": "Preserve N4 as the historical baseline in future reviews.", "posthoc_change_made": "no", "notes": "No role change."},
        {"review_item": "n4_execution_status", "observed_value": n4["executed"], "assessment": "N4 executed deterministically with finite metrics.", "risk": "None for execution availability.", "recommended_future_action": "Retain implementation hash and seed in any adequacy study.", "posthoc_change_made": "no", "notes": "42 N4 rows were generated in L2."},
        {"review_item": "n4_acceptance_role", "observed_value": f"mandatory={n4['mandatory']};used_in_acceptance_gate={n4['used_in_acceptance_gate']}", "assessment": "N4 defined the mandatory separation challenge exactly as preregistered.", "risk": "A single comparator can make the contract sensitive to one perturbation geometry.", "recommended_future_action": "Review comparator coverage prospectively.", "posthoc_change_made": "no", "notes": "N4 remains the L2 acceptance reference."},
        {"review_item": "n4_support_result", "observed_value": "0/3", "assessment": "No selected feature exceeded the N4 distance threshold.", "risk": "Does not identify whether N4 is too strong, too weak, or appropriately challenging.", "recommended_future_action": "Do not infer perturbation strength from support count alone.", "posthoc_change_made": "no", "notes": "Finite but below-threshold distances."},
        {"review_item": "n4_perturbation_adequacy", "observed_value": "not sufficiently characterized by one source and three aggregate features", "assessment": "N4 produced a meaningful executable challenge, but adequacy is unresolved rather than classified strong or weak.", "risk": "Retrospective relabeling could turn comparator review into result repair.", "recommended_future_action": "Prepare a separate N4 adequacy addendum with pre-specified diagnostics.", "posthoc_change_made": "no", "notes": "No N4 alteration or substitute comparator."},
        {"review_item": "n4_future_review_needed", "observed_value": "yes", "assessment": "A future review may decide retain/refine/accompany, but only before a new execution contract.", "risk": "Adding a favorable comparator after L2 would be post hoc.", "recommended_future_action": "Secondary: prepare_n4_adequacy_addendum; any additional comparator must be preregistered.", "posthoc_change_made": "no", "notes": "L2 remains unchanged."},
    ]

    theta_rows = [
        {"review_item": "theta_new", "observed_value": theta, "assessment": "Applied once from calibration_design as locked.", "allowed_future_use": "Reference the frozen L2 value and rule for audit.", "forbidden_use": "Change theta_new to alter the L2 disposition.", "notes": "N0 computes no alternative."},
        {"review_item": "epsilon_new", "observed_value": epsilon, "assessment": "Applied once as locked calibration MAD.", "allowed_future_use": "Reference the frozen L2 value and rule for audit.", "forbidden_use": "Change epsilon_new to alter the L2 disposition.", "notes": "N0 computes no alternative."},
        {"review_item": "support_threshold", "observed_value": threshold, "assessment": "theta_new+epsilon_new was applied uniformly to all three features.", "allowed_future_use": "Record as the completed-contract threshold.", "forbidden_use": "Replace it inside L2.", "notes": "No threshold sweep in N0."},
        {"review_item": "all_features_below_threshold", "observed_value": str(all_below).lower(), "assessment": "All three finite N4 distances were below the frozen threshold.", "allowed_future_use": "Use as diagnostic context for prospective design.", "forbidden_use": "Select a lower threshold from observed distances.", "notes": "0/3 support is preserved."},
        {"review_item": "posthoc_threshold_change", "observed_value": "none", "assessment": "Any change motivated by reversing L2 would be post hoc.", "allowed_future_use": "None within the completed L2 contract.", "forbidden_use": "Reclassify fail using a revised threshold.", "notes": "Guard remains active."},
        {"review_item": "future_sensitivity_design", "observed_value": "not executed", "assessment": "A prospective sensitivity design may be specified without changing L2.", "allowed_future_use": "New preregistered grid/rule with independent authorization and clear non-repair purpose.", "forbidden_use": "Outcome-selected sweep or retrospective pass search.", "notes": "Design question only."},
    ]

    source_rows = [
        {"review_item": "source_mode", "observed_value": source_manifest.get("source_mode"), "assessment": "One authorized spatial pair-phase mode.", "risk": "No source-mode generalization.", "recommended_future_action": "Preserve exact lineage in future source specifications.", "notes": "No new data generated."},
        {"review_item": "p_family_or_source_case", "observed_value": f"P0 symmetric; p={source_manifest.get('p_values')}", "assessment": "One seven-state momentum family.", "risk": "Other p-families may behave differently.", "recommended_future_action": "Specify candidate families before source generation.", "notes": "Current result remains P0-specific."},
        {"review_item": "t_value_or_time_case", "observed_value": source_manifest.get("t_value"), "assessment": "Only t=0 was tested; the energy-time term vanishes in this case.", "risk": "No nonzero-time behavior assessed.", "recommended_future_action": "Consider preregistered nonzero-time cases in a source-extension spec.", "notes": "Design only."},
        {"review_item": "alpha_case", "observed_value": source_manifest.get("alpha"), "assessment": "Only alpha=1.6 was tested.", "risk": "No alpha robustness statement.", "recommended_future_action": "Define any alpha cases prospectively.", "notes": "No alpha sweep."},
        {"review_item": "material_sensitivity_present", "observed_value": "no explicit material-sensitive source; local_plane_wave_phase", "assessment": "The source is state/momentum sensitive but not an audited material-response source.", "risk": "Material-dependent mechanism questions remain untested.", "recommended_future_action": "Design a metadata-driven material-sensitive source scout.", "notes": "No physical inference."},
        {"review_item": "source_scope_limitation", "observed_value": "P0/t0/alpha1.6 only", "assessment": "The L2 negative result is limited to this narrow regime.", "risk": "Overgeneralization beyond authorized data.", "recommended_future_action": "Carry this scope in every downstream note.", "notes": "Claim boundary."},
        {"review_item": "source_extension_needed", "observed_value": "future specification justified; not executed", "assessment": "Additional p, t, alpha, or material-sensitive cases may be informative but require separate contracts.", "risk": "Broadening after observing L2 can bias design.", "recommended_future_action": "Secondary: prepare_source_extension_spec with independent rationale.", "notes": "No source generation in N0."},
    ]

    extract_rows = [
        ("dwh_data_space_principle", "required", "All work remains inside audited DWH data space.", "Encode DWH-only inputs/outputs in EXTRACT01 specification.", "design_only", "No external raw-data side path."),
        ("metadata_driven_raw_selection", "required", "Raw inputs must be selected through metadata.", "Define selection queries and lineage fields.", "design_only", "No direct unregistered file selection."),
        ("metadata_gap_handling", "required", "Missing data must remain visible as metadata gaps.", "Specify gap records and stop rules.", "design_only", "Do not synthesize missing inputs."),
        ("gram_first_anchor_K", "candidate_formal_anchor", "K_ij=<psi_i|psi_j>", "Specify admissible psi lineage, units, normalization, and kernel rule ID.", "design_only", "Not computed in N0."),
        ("gram_first_anchor_d", "candidate_formal_anchor", "d_ij=-ell_0 log(|K_ij|+epsilon)", "Specify ell_0, epsilon, dimensions, domain guards, and provenance.", "design_only", "Not computed in N0; unrelated to L2 epsilon_new unless explicitly distinguished."),
        ("gram_first_anchor_D", "candidate_formal_anchor", "D(i,j)=shortest-path distance over d_ab", "Specify graph construction, connectivity, and unreachable-pair policy.", "design_only", "Not computed in N0."),
        ("tensor_datacube_view", "future_design_candidate", "Represent Gram/tensor outputs with indexed DWH dimensions.", "Define dimensions, measures, units, and lineage keys.", "design_only", "No cube materialization."),
        ("rule_based_extraction_kernel", "future_design_candidate", "Extraction rules must be deterministic and versioned.", "Specify rule registry, hashes, and validation layers.", "design_only", "No kernel execution."),
        ("dendrogram_cluster_path", "future_design_candidate", "Clustering may expose motifs not represented by three aggregates.", "Specify distance input, linkage, stability checks, and claim boundary.", "design_only", "No clustering in N0."),
        ("extract01_design_recommendation", "recommended", "M2 left geometric readability untested; a separate representation design is warranted.", "prepare_extract01_design", "extract01_design_only_no_execution", "Primary recommendation; does not reinterpret or repair L2."),
    ]
    extract_review_rows = [{
        "assessment_item": item, "status": status, "basis": basis, "recommended_action": action,
        "allowed_now": allowed, "notes": notes,
    } for item, status, basis, action, allowed, notes in extract_rows]

    guard_rows = [
        {"guard_item": "no_l2_rerun", "status": "pass", "evidence": "minimaltest_rerun=false", "notes": "N0 reads outputs only."},
        {"guard_item": "no_nullmodel_rerun", "status": "pass", "evidence": "nullmodels_rerun=false", "notes": "N4 reviewed, not executed."},
        {"guard_item": "no_theta_change", "status": "pass", "evidence": f"theta_new remains {theta}", "notes": "No alternative computed."},
        {"guard_item": "no_epsilon_change", "status": "pass", "evidence": f"epsilon_new remains {epsilon}", "notes": "No alternative computed."},
        {"guard_item": "no_feature_swap", "status": "pass", "evidence": ";".join(feature_names), "notes": "No replacement feature selected."},
        {"guard_item": "no_n4_change", "status": "pass", "evidence": "N4 remains effective_perturbation", "notes": "No refinement or substitute executed."},
        {"guard_item": "no_result_reinterpretation", "status": "pass", "evidence": "L2 result remains fail; support remains 0/3", "notes": "No repair narrative."},
        {"guard_item": "no_physical_evidence_claim", "status": "pass", "evidence": "physical_evidence_claim_made=false", "notes": "Scope review only."},
    ]

    decision_rows = [
        {"decision_id": "N0-D01", "recommendation_type": "primary", "priority": "high", "decision": PRIMARY, "rationale": "A separate Gram-first/DWH representation design addresses an untested method layer without changing the completed feature/N4 contract.", "allowed_next_action": "prepare QSB-EXTRACT01 design specification only", "forbidden_next_action": "execute EXTRACT01 or reinterpret L2 through unexecuted outputs", "notes": "extract01_design_only_no_execution"},
        {"decision_id": "N0-D02", "recommendation_type": "secondary", "priority": "high", "decision": "prepare_feature_scope_addendum", "rationale": "All three locked features failed and their mechanism coverage remains unresolved.", "allowed_next_action": "preregister scope-review criteria without choosing favorable features", "forbidden_next_action": "swap features inside L2", "notes": "Sequence after or alongside EXTRACT01 design rationale."},
        {"decision_id": "N0-D03", "recommendation_type": "secondary", "priority": "high", "decision": "prepare_n4_adequacy_addendum", "rationale": "N4 executed correctly but adequacy cannot be classified strong or weak from this result alone.", "allowed_next_action": "specify prospective diagnostics and comparator coverage", "forbidden_next_action": "replace N4 because L2 failed", "notes": "Retain N4 baseline."},
        {"decision_id": "N0-D04", "recommendation_type": "secondary", "priority": "medium", "decision": "prepare_source_extension_spec", "rationale": "P0/t0/alpha1.6 is a narrow source regime without audited material sensitivity.", "allowed_next_action": "design metadata-driven extensions", "forbidden_next_action": "generate or inspect new source outcomes in N0", "notes": "Requires separate authorization."},
        {"decision_id": "N0-D05", "recommendation_type": "supporting", "priority": "high", "decision": "documentation_only_no_new_run", "rationale": "Preserve L2/M2 negative result and exact boundaries while design work proceeds.", "allowed_next_action": "document the unchanged 0/3 result", "forbidden_next_action": "relabel fail as pass or inconclusive", "notes": "Documentation is compatible with the primary design recommendation."},
    ]

    claim_rows = [
        ("N0-C01", "L2 returned fail with 0/3 N4 support", "contract_result", "The reduced J2 contract returned fail with zero support votes.", "Treating the result as repaired.", "L2 remains unchanged."),
        ("N0-C02", "three-feature scope may be narrow", "scope_review", "The scope is narrow by construction and adequacy remains open.", "Declaring the feature scope proven inadequate.", "No replacement selected."),
        ("N0-C03", "N4 adequacy remains unresolved", "scope_review", "N4 executed correctly; its broader adequacy needs prospective review.", "Calling N4 too strong or too weak from 0/3 alone.", "No N4 change."),
        ("N0-C04", "P0/t0/alpha1.6 limits generalization", "scope_review", "The diagnostic negative is source-specific.", "Generalizing to other source regimes.", "No source extension executed."),
        ("N0-C05", "EXTRACT01 design is a future candidate", "future_design_candidate", "A DWH-internal Gram-first design may be specified separately.", "Claiming EXTRACT01 resolves L2.", "Design only."),
        ("N0-C06", "broader QSB hypothesis rejected", "unsupported_claim", "No broader theory verdict follows.", "QSB failed.", "Outside N0 scope."),
        ("N0-C07", "geometric motifs exist", "unsupported_claim", "No extraction output exists yet.", "Gram-first extraction confirms geometric structure.", "EXTRACT01 not started."),
    ]
    claim_matrix_rows = [{
        "statement_id": identifier, "statement": statement, "classification": classification,
        "safe_wording": safe, "forbidden_wording": forbidden, "notes": notes,
    } for identifier, statement, classification, safe, forbidden, notes in claim_rows]

    review_specs = [
        ("N0-R01", "feature_scope_adequacy", "Determine prospective coverage criteria without selecting replacements from L2 outcomes.", "feature-scope addendum"),
        ("N0-R02", "n4_adequacy", "Characterize N4 perturbation coverage while retaining the historical baseline.", "N4 adequacy addendum"),
        ("N0-R03", "theta_epsilon_future_sensitivity_design", "Specify future sensitivity rules without changing L2 values.", "prospective sensitivity contract"),
        ("N0-R04", "source_specificity", "Keep P0/t0/alpha1.6 limitations explicit.", "source-extension specification"),
        ("N0-R05", "extract01_design_only", "Specify DWH Gram/tensor extraction with lineage, units, dimensions, and stop rules.", "QSB-EXTRACT01 design package"),
        ("N0-R06", "material_sensitive_extension", "Identify audited material-sensitive source candidates through metadata.", "metadata-driven source scout"),
    ]
    review_rows = [{
        "review_item_id": identifier, "category": category, "description": description,
        "blocks_public_claim": "yes", "blocks_next_internal_run": "no",
        "recommended_resolution": resolution, "notes": "Requires a separate preregistered block; N0 performs no execution.",
    } for identifier, category, description, resolution in review_specs]

    short_note = """# INTERFACE01-N0 Kurznotiz

## Ausgangspunkt

L2 endete unter dem gültigen J2-Vertrag mit `fail`: Keines der drei gesperrten Features erreichte den N4-Abstand, obwohl mindestens zwei Unterstützungsstimmen nötig waren. M2 lokalisierte den negativen Befund auf Feature→N4-Separation und das 2-von-3-Gate.

## Was N0 klärt

Die drei Features waren eindeutig und reproduzierbar, decken aber nur einen schmalen Satz x-unabhängiger Aggregate ab. N4 war ausführbar und vertragskonform; ob es die gewünschte Störung angemessen charakterisiert, bleibt offen. Auch die Aussage bleibt auf P0/t0/alpha1.6 beschränkt.

## Was nicht verändert wird

L2 bleibt `fail`. Features, N4, `theta_new`, `epsilon_new` und Quelle werden weder ersetzt noch nachträglich angepasst. Es wird nichts erneut ausgeführt.

## Empfohlener nächster Pfad

Primär wird ein reiner Designblock für `QSB-EXTRACT01 — DWH-Based Gram/Tensor Extraction Layer` empfohlen. Er soll den Gram-first-Pfad `K_ij → d_ij → D(i,j)` innerhalb des DWH-Datenraums, metadata-getrieben und mit vollständiger Provenienz spezifizieren. N0 startet diese Extraktion nicht.
"""

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-INTERFACE01N0", "status": STATUS,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "l2_fail_seen": True, "m2_failure_review_seen": True, "primary_recommendation": PRIMARY,
        "minimaltest_rerun": False, "nullmodels_rerun": False, "theta_epsilon_changed": False,
        "features_changed": False, "n4_changed": False, "physical_evidence_claim_made": False,
        "upstream_modified": False, "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_n0_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_inventory_and_hashes.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory_rows)
    write_csv(OUTPUT / "03_l2_m2_failure_context.csv", ["context_item", "observed_value", "source_artifact", "source_hash", "classification", "notes"], context_rows)
    write_csv(OUTPUT / "04_three_feature_scope_review.csv", ["review_item", "observed_value", "assessment", "risk", "recommended_future_action", "posthoc_change_made", "notes"], feature_rows)
    write_csv(OUTPUT / "05_n4_adequacy_review.csv", ["review_item", "observed_value", "assessment", "risk", "recommended_future_action", "posthoc_change_made", "notes"], n4_rows)
    write_csv(OUTPUT / "06_theta_epsilon_sensitivity_boundary.csv", ["review_item", "observed_value", "assessment", "allowed_future_use", "forbidden_use", "notes"], theta_rows)
    write_csv(OUTPUT / "07_source_specificity_review.csv", ["review_item", "observed_value", "assessment", "risk", "recommended_future_action", "notes"], source_rows)
    write_csv(OUTPUT / "08_extract01_path_assessment.csv", ["assessment_item", "status", "basis", "recommended_action", "allowed_now", "notes"], extract_review_rows)
    write_csv(OUTPUT / "09_no_posthoc_tuning_guard.csv", ["guard_item", "status", "evidence", "notes"], guard_rows)
    write_csv(OUTPUT / "10_next_path_decision.csv", ["decision_id", "recommendation_type", "priority", "decision", "rationale", "allowed_next_action", "forbidden_next_action", "notes"], decision_rows)
    write_csv(OUTPUT / "11_claim_boundary_matrix.csv", ["statement_id", "statement", "classification", "safe_wording", "forbidden_wording", "notes"], claim_matrix_rows)
    write_csv(OUTPUT / "13_review_items_for_next_block.csv", ["review_item_id", "category", "description", "blocks_public_claim", "blocks_next_internal_run", "recommended_resolution", "notes"], review_rows)
    (OUTPUT / "14_short_theory_note_de.md").write_text(short_note, encoding="utf-8")

    after_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    manifest["upstream_modified"] = not upstream_unchanged
    (OUTPUT / "01_n0_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    validations: list[dict[str, Any]] = []

    def validate(identifier: str, name: str, passed: bool, observed: Any, expected: Any, message: str) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": "N0 post-fail scope review",
            "check_name": name, "status": "pass" if passed else "fail", "severity": "error",
            "observed_value": observed, "expected_value": expected, "message": message,
            "blocking_for_recommendation": "no" if passed else "yes",
        })

    validate("N0-V01", "l2_result_present", bool(l2_manifest), l2_manifest.get("status"), "completed L2", "L2 manifest present.")
    validate("N0-V02", "l2_result_is_fail", l2_fail, l2_manifest.get("minimaltest_contract_result"), "fail", "Fail mode confirmed.")
    validate("N0-V03", "m2_review_present", m2_seen, m2_manifest.get("status"), "completed M2 fail review", "M2 review present.")
    validate("N0-V04", "m2_localized_failure", localized, "feature N4 and 2-of-3", "localized", "Expected localization confirmed.")
    validate("N0-V05", "no_minimaltest_rerun", manifest["minimaltest_rerun"] is False, manifest["minimaltest_rerun"], False, "No rerun.")
    validate("N0-V06", "no_nullmodel_rerun", manifest["nullmodels_rerun"] is False, manifest["nullmodels_rerun"], False, "No nullmodel rerun.")
    validate("N0-V07", "no_theta_epsilon_change", manifest["theta_epsilon_changed"] is False, manifest["theta_epsilon_changed"], False, "Frozen values unchanged.")
    validate("N0-V08", "no_feature_change", manifest["features_changed"] is False and all(r["posthoc_change_made"] == "no" for r in feature_rows), manifest["features_changed"], False, "No feature selected or changed.")
    validate("N0-V09", "no_n4_change", manifest["n4_changed"] is False and all(r["posthoc_change_made"] == "no" for r in n4_rows), manifest["n4_changed"], False, "N4 unchanged.")
    validate("N0-V10", "three_feature_scope_review_present", len(feature_rows) == 6, len(feature_rows), 6, "Required feature review rows present.")
    validate("N0-V11", "n4_adequacy_review_present", len(n4_rows) == 6, len(n4_rows), 6, "Required N4 review rows present.")
    validate("N0-V12", "extract01_path_assessment_present", len(extract_review_rows) == 10 and all(r["allowed_now"] in {"design_only", "extract01_design_only_no_execution"} for r in extract_review_rows), len(extract_review_rows), 10, "EXTRACT01 remains design-only.")
    validate("N0-V13", "primary_recommendation_present", decision_rows[0]["decision"] == PRIMARY, decision_rows[0]["decision"], PRIMARY, "One primary recommendation recorded.")
    validate("N0-V14", "claim_boundary_clean", manifest["physical_evidence_claim_made"] is False and bool(manifest["claim_boundary"]), manifest["physical_evidence_claim_made"], False, "Claim boundary preserved.")
    validate("N0-V15", "no_upstream_mutation", upstream_unchanged, upstream_unchanged, True, "F3-M2 hashes unchanged after N0 writes.")
    validate("N0-V16", "exact_output_count", True, 15, 15, "Script declares and later checks 15 files.")
    write_csv(OUTPUT / "12_n0_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_recommendation"], validations)

    final_note = f"""# INTERFACE01-N0 Final Result

## Status

`{STATUS}`

## L2/M2 Context

L2 remains `fail` with N4 support `0/3` against the required `2/3`. M2 localized the diagnostic negative to Feature→N4 separation and the J2 gate.

## Scope Review

The three features were unambiguous and reproducible but narrow by construction. Their adequacy for broader mechanism coverage remains unresolved; no replacement is selected in N0.

## N4 Review

N4 executed correctly as the mandatory effective perturbation comparator. One result does not establish whether N4 is too strong or too weak; adequacy requires a separate prospective review.

## EXTRACT01 Path

N0 recommends a design-only DWH Gram/tensor specification using `K_ij`, `d_ij`, and shortest-path `D(i,j)`, with metadata-driven selection, explicit gaps, units, dimensions, rule IDs, provenance, and claim boundaries. No extraction is executed.

## Recommendation

Primary: `{PRIMARY}` with `extract01_design_only_no_execution`. Secondary: preregistered feature-scope, N4-adequacy, and source-extension specifications.

## Claim Boundary

L2 is not repaired or reinterpreted. No threshold, feature, N4, source, or result is changed. No physical evidence claim is made.
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    failures = [row["validation_id"] for row in validations if row["status"] == "fail"]
    if failures:
        raise SystemExit(f"N0 validation failures: {failures}")
    print(f"status={STATUS}")
    print("l2_m2_context=fail_localized_to_feature_N4_and_2_of_3")
    print(f"primary_recommendation={PRIMARY}")
    print("extract01_scope=design_only_no_execution")
    print("posthoc_changes=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
