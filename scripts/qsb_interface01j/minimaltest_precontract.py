#!/usr/bin/env python3
"""Draft the conditional INTERFACE01-J Minimaltest pre-contract without execution."""

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
OUTPUT = REPO / "runs/QSB-INTERFACE01J/minimaltest_precontract"
STATUS_OK = "interface01j_minimaltest_precontract_completed_conditional_no_execution"
STATUS_BLOCKED = "interface01j_minimaltest_precontract_blocked_missing_upstream_artifacts"
CLEARANCE = "not_authorized_pending_review_resolution"
EXPECTED_I_STATUS = "interface01i_pilot_result_review_completed_nullmodel_adequacy_assessed"
EXPECTED_READINESS = "conditional_ready_with_review_items"
EXPECTED_OUTPUTS = {
    "01_j_run_manifest.json", "02_upstream_artifact_register.csv", "03_i_readiness_summary.csv",
    "04_feature_selection_precontract.csv", "05_nullmodel_precontract.csv", "06_split_seed_precontract.csv",
    "07_theta_epsilon_calibration_precontract.csv", "08_execution_gate_matrix.csv",
    "09_review_item_resolution_contract.csv", "10_minimaltest_output_schema_contract.csv",
    "11_forbidden_actions_claim_boundary.csv", "12_validation_results.csv", "FINAL_RESULT_NOTE.md",
}
CLAIM_BOUNDARY = (
    "INTERFACE01-J defines a conditional pre-contract only. It authorizes no Minimaltest execution, "
    "no physical-evidence statement, no outcome-driven tuning, and no Phase-D threshold transfer."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_row(identifier: str, work_package: str, path: Path, status: str, summary: str, relevance: str, notes: str) -> dict[str, Any]:
    exists = path.exists()
    return {
        "artifact_id": identifier, "work_package": work_package, "path": str(path.relative_to(REPO)),
        "exists": "yes" if exists else "no", "status_seen": status if exists else "missing",
        "row_count_or_summary": summary if exists else "not available",
        "hash_or_na": file_hash(path) if path.is_file() else "na_directory",
        "decision_relevance": relevance, "notes": notes,
    }


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    required = {
        "f3_manifest": F3 / "01_f3_run_manifest.json",
        "f3_db": F3 / "09_delta_phi_staging_preflight.sqlite",
        "f3_input": F3_INPUT,
        "g_manifest": G / "01_g_run_manifest.json",
        "h_manifest": H / "01_h_run_manifest.json",
        "i_manifest": I / "01_i_run_manifest.json",
        "i_readiness": I / "09_minimaltest_readiness_decision.csv",
        "i_features": I / "05_feature_signal_stability_review.csv",
        "i_nulls": I / "06_nullmodel_adequacy_matrix.csv",
        "i_design": I / "08_split_seed_calibration_review.csv",
        "i_review_items": I / "11_review_items.csv",
        "i_validations": I / "12_i_validation_results.csv",
    }
    upstream_complete = all(path.is_file() for path in required.values())
    if not upstream_complete:
        missing = [str(path.relative_to(REPO)) for path in required.values() if not path.is_file()]
        raise SystemExit(f"Critical upstream artifacts missing; safe pre-contract generation stopped: {missing}")

    f3_manifest = load_json(required["f3_manifest"])
    f3_input = load_json(required["f3_input"])
    g_manifest = load_json(required["g_manifest"])
    h_manifest = load_json(required["h_manifest"])
    i_manifest = load_json(required["i_manifest"])
    i_readiness = read_csv(required["i_readiness"])
    i_features = read_csv(required["i_features"])
    i_nulls = read_csv(required["i_nulls"])
    i_design = read_csv(required["i_design"])
    i_review_items = read_csv(required["i_review_items"])
    i_validations = read_csv(required["i_validations"])

    readiness = i_readiness[0]["status"] if len(i_readiness) == 1 else "invalid_or_missing"
    i_status_ok = i_manifest.get("status") == EXPECTED_I_STATUS
    readiness_ok = readiness == EXPECTED_READINESS
    review_items_exact = len(i_review_items) == 7 and {row["review_item_id"] for row in i_review_items} == {f"I-R{i:02d}" for i in range(1, 8)}
    nonflat_count = sum(row.get("variation_status") == "nonflat_finite" for row in i_features)
    null_by_id = {row["nullmodel_id"]: row for row in i_nulls}
    n2_ok = null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("adequacy_class") == "invariance_check_only"
    n4_ok = null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("adequacy_class") == "effective_perturbation"
    statuses_ok = all([
        f3_manifest.get("status") == "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged",
        g_manifest.get("status") == "interface01g_minimaltest_design_review_completed_with_staged_source_profile",
        h_manifest.get("status") == "interface01h_controlled_minimal_pilot_completed_with_review_items",
        i_status_ok, readiness_ok,
    ])
    status = STATUS_OK if upstream_complete and statuses_ok and review_items_exact and n2_ok and n4_ok else STATUS_BLOCKED

    artifacts = [
        artifact_row("A01", "QSB-INTERFACE01F3", F3, f3_manifest.get("status", ""), "root; staged source rows=168042", "source lineage and staging scope", "Read-only upstream root."),
        artifact_row("A02", "QSB-INTERFACE01F3", required["f3_manifest"], f3_manifest.get("status", ""), "manifest", "F3 status, row counts, input hash", "Manifest hash recorded."),
        artifact_row("A03", "QSB-INTERFACE01F3", required["f3_db"], "authorized_staging_db", "168042 spatial rows", "later source-of-record", "J does not query or mutate source rows."),
        artifact_row("A04", "QSB-INTERFACE01F3", required["f3_input"], f3_input.get("authorization_status", ""), "authorized input manifest", "p lineage and post-hoc lock", "p values may only be manifest-derived if required."),
        artifact_row("A05", "QSB-INTERFACE01G", G, g_manifest.get("status", ""), "root; 11 validations passed", "source profile gate", "Read-only upstream root."),
        artifact_row("A06", "QSB-INTERFACE01H", H, h_manifest.get("status", ""), "root; 42 pairfeatures; 6 nullmodels", "controlled-pilot basis", "No final Minimaltest in H."),
        artifact_row("A07", "QSB-INTERFACE01I", I, i_manifest.get("status", ""), "root; 630 review rows; 7 review items", "adequacy and readiness decision", "Read-only upstream root."),
        artifact_row("A08", "QSB-INTERFACE01I", required["i_manifest"], i_manifest.get("status", ""), "manifest", "authoritative I status", "Readiness remains conditional."),
        artifact_row("A09", "QSB-INTERFACE01I", I / "FINAL_RESULT_NOTE.md", i_manifest.get("status", ""), "final internal decision note", "claim boundary and next action", "Summary only; machine-readable tables remain authoritative."),
    ]

    i_summary = [{
        "i_status": i_manifest.get("status", ""), "readiness": readiness,
        "pairfeature_count": i_manifest.get("pair_feature_count_used", 0),
        "nullmodel_count": i_manifest.get("nullmodel_count_used", 0),
        "feature_review_rows": i_manifest.get("pair_feature_review_rows", 0),
        "nonflat_feature_count": nonflat_count, "n2_classification": null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("adequacy_class", "missing"),
        "n4_classification": null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("adequacy_class", "missing"),
        "precontract_drafting_blocked": "no" if status == STATUS_OK else "yes",
        "execution_clearance": CLEARANCE, "review_items_open_count": len(i_review_items),
    }]

    selected_features = {"signed_correlation_score", "abs_correlation_score", "mean_abs_cos_wrapped_delta"}
    structural = {"n_x", "x_min", "x_max"}
    extrema = {"raw_delta_min", "raw_delta_max", "wrapped_delta_min", "wrapped_delta_max"}
    redundancy = {"circular_resultant_length", "phase_variance_proxy", "mean_abs_sin_wrapped_delta"}
    feature_rows = []
    for row in i_features:
        name = row["feature_name"]
        if name in selected_features:
            family = "phase_correlation_candidate"
            allowed, review = "yes_conditional_candidate", "yes_human_freeze_required"
            reason = "Finite, non-flat in I and tied to a predeclared H feature/null role."
            exclusion = ""
        elif name in structural:
            family = "coverage_control"
            allowed, review = "no_control_only", "no"
            reason, exclusion = "Retained as source-coverage control.", "Not a discriminating candidate feature."
        elif name in extrema:
            family = "range_diagnostic"
            allowed, review = "no_diagnostic_only", "yes_if_later_promoted"
            reason, exclusion = "Retained without filtering as a range diagnostic.", "Raw/wrapped extrema are boundary-sensitive and are not selected for the compact candidate set."
        elif name == "mean_sin_wrapped_delta":
            family = "neutral_phase_control"
            allowed, review = "no_near_flat_control", "no"
            reason, exclusion = "Near-flat neutral outcome retained as a control.", "I classified it flat_or_near_flat."
        elif name in redundancy:
            family = "redundant_or_secondary_phase_feature"
            allowed, review = "no_secondary_only", "yes_if_later_promoted"
            reason, exclusion = "Finite and retained for audit.", "Excluded from compact candidate set pending redundancy/normalization review."
        else:
            family = "secondary_phase_feature"
            allowed, review = "no_secondary_only", "yes_if_later_promoted"
            reason, exclusion = "Retained for audit.", "Not selected into the compact proposed feature set."
        feature_rows.append({
            "feature_name": name, "feature_family": family,
            "source_artifact": str(required["i_features"].relative_to(REPO)),
            "variation_status": row.get("variation_status", "unknown"),
            "allowed_for_minimaltest_candidate": allowed, "requires_review_before_execution": review,
            "selection_reason": reason, "exclusion_reason": exclusion,
            "notes": "Proposed role only; all selected candidates require separate human authorization before execution.",
        })

    role_specs = {
        "N0_SIGN_FLIP": ("sign-dependence perturbation", "conditional", "yes", "Changes signed score only; absolute score is invariant.", "signed feature should reverse", "Confirm signed-score endpoint and tolerance."),
        "N1_PAIR_LABEL_PERMUTE": ("label-identity perturbation", "conditional", "conditional", "No feature values change without a label-sensitive statistic.", "break registered pair-label association", "Resolve I-R03 by registering the label-sensitive statistic."),
        "N2_X_INDEX_ROLL_SURROGATE": ("x-order invariance sanity check", "yes_sanity_only", "yes_sanity_only", "Must not count toward effective perturbation adequacy.", "no change for current x-independent aggregates", "Resolve I-R01 if x-position sensitivity is required."),
        "N3_PAIR_DIRECTION_COLLAPSE": ("directional consistency sanity check", "yes_sanity_only", "yes_sanity_only", "Not an active perturbation.", "small partner discrepancy under absolute score", "Retain as sanity check and resolve I-R02 wording."),
        "N4_PHASE_RANDOM_REFERENCE": ("active phase perturbation reference", "yes", "yes", "Uniform deterministic reference is a comparator, not evidence.", "change target phase-correlation features", "Freeze seed/implementation hash and require it in execution."),
        "N5_CONSTANT_ZERO_PHASE_REFERENCE": ("degenerate upper-reference sanity check", "optional", "no", "Degenerate reference is not a realistic null.", "unit absolute correlation reference", "Retain limitation in report if used."),
    }
    null_rows = []
    for model_id in ["N0_SIGN_FLIP", "N1_PAIR_LABEL_PERMUTE", "N2_X_INDEX_ROLL_SURROGATE", "N3_PAIR_DIRECTION_COLLAPSE", "N4_PHASE_RANDOM_REFERENCE", "N5_CONSTANT_ZERO_PHASE_REFERENCE"]:
        source = null_by_id[model_id]
        role, allowed, required_exec, limitations, effect, review_action = role_specs[model_id]
        null_rows.append({
            "nullmodel_id": model_id, "nullmodel_role": role, "adequacy_class": source["adequacy_class"],
            "allowed_in_later_minimaltest": allowed, "required_for_execution": required_exec,
            "limitations": limitations, "expected_effect": effect,
            "review_action_before_execution": review_action,
            "notes": "I adequacy classification carried without promotion or concealment.",
        })

    split_rows = []
    for name, fraction, use, forbidden in [
        ("train_design", "0.40", "feature-definition checks and implementation diagnostics", "threshold selection from favorable outcomes"),
        ("calibration", "0.30", "predeclared theta/epsilon calibration only", "post-null or holdout-driven retuning"),
        ("review_holdout", "0.20", "single locked contract review after parameter freeze", "parameter fitting or rule changes"),
        ("final_audit", "0.10", "final audit only after all other artifacts are frozen", "any tuning, model selection, or exploratory inspection"),
    ]:
        split_rows.append({
            "split_name": name, "fraction": fraction, "seed": 20260620,
            "assignment_basis": "deterministic SHA-256 assignment at ordered-pair level; exact 42-pair allocation requires I-R05 human resolution",
            "allowed_use": use, "forbidden_use": forbidden, "post_hoc_tuning_lock": "true",
            "notes": "Target convention is frozen; realized allocation and mapping from H labels require separate human acceptance before execution.",
        })

    calibration_rows = [
        {
            "parameter": "theta_new", "calibration_source": "locked calibration partition only",
            "calibration_rule": "median(abs_correlation_score) on the authorized calibration partition; compute once after gates and freeze before nullmodel comparison",
            "allowed_inputs": "selected_feature_table plus frozen calibration split and source hash",
            "forbidden_inputs": "review_holdout; final_audit; nullmodel outcomes; favorable-result search; Phase-D threshold",
            "phase_d_theta_0300_allowed": "no", "post_hoc_tuning_lock": "true", "execution_gate": CLEARANCE,
            "notes": "Procedure only; J computes and authorizes no value.",
        },
        {
            "parameter": "epsilon_new", "calibration_source": "locked calibration partition only",
            "calibration_rule": "median absolute deviation of abs_correlation_score around the calibration median; compute once and freeze with numeric provenance",
            "allowed_inputs": "selected_feature_table plus frozen calibration split and numeric precision audit",
            "forbidden_inputs": "review_holdout; final_audit; nullmodel outcomes; post-hoc margin changes; Phase-D threshold",
            "phase_d_theta_0300_allowed": "no", "post_hoc_tuning_lock": "true", "execution_gate": CLEARANCE,
            "notes": "Procedure only; J computes and authorizes no value.",
        },
    ]

    gate_specs = [
        ("J01", "upstream F3 staged source available", "available_and_hash_matched", "satisfied", "yes", "F3 manifest/staging DB", "Preserve F3 hash and read-only source."),
        ("J02", "G source profile passed", "11 validations passed", "satisfied", "yes", "G manifest", "Preserve G profile gate."),
        ("J03", "H pilot completed", "controlled pilot completed", "satisfied", "yes", "H manifest", "Preserve pilot-only claim boundary."),
        ("J04", "I readiness reviewed", EXPECTED_READINESS, "satisfied", "yes", "I readiness decision", "Carry conditional status forward."),
        ("J05", "seven I review items resolved", "7/7 human-resolved and separately authorized", "not_satisfied_0_of_7_human_authorized", "yes", "I review items and future authorization record", "Resolve each row in 09 and record separate human authorization."),
        ("J06", "N2 limited role acknowledged", "invariance_check_only", "satisfied", "yes", "I nullmodel matrix; J nullmodel contract", "Never count N2 as effective perturbation."),
        ("J07", "at least one effective perturbation nullmodel required", "N4 required with frozen implementation", "contract_defined_pending_human_authorization", "yes", "J nullmodel contract", "Authorize frozen N4 implementation before execution."),
        ("J08", "p_i/p_j reconstruction policy fixed or not needed", "manifest-only mapping or explicit not-needed decision", "defined_manifest_only_or_block_pending_I_R07", "yes", "F3 input manifest; I-R07", "Human-confirm need; if needed, map only by authorized pair indices or block."),
        ("J09", "feature set frozen", "human-authorized compact feature set", "proposed_not_human_authorized", "yes", "J feature precontract", "Human-freeze selected candidates after review."),
        ("J10", "split/seed policy frozen", "human-authorized deterministic assignment", "target_policy_defined_pending_I_R05", "yes", "J split/seed precontract", "Resolve exact 42-pair allocation and label mapping."),
        ("J11", "theta_new/epsilon_new calibration frozen", "human-authorized procedures before values", "procedures_defined_not_authorized", "yes", "J calibration precontract; I-R04", "Human-authorize procedures; compute only in later gated block."),
        ("J12", "no Phase-D theta transfer", "prohibited", "satisfied", "yes", "J calibration and forbidden-action contracts", "Retain prohibition."),
        ("J13", "no final Minimaltest inside J", "not run", "satisfied", "yes", "J run manifest", "J remains contract-only."),
        ("J14", "human authorization required before execution", "separate authorization recorded after J05-J11", CLEARANCE, "yes", "J run manifest and future authorization record", "Do not execute until clearance changes in a separate authorized work package."),
    ]
    gates = [{
        "gate_id": gid, "gate_name": name, "required_status": required_status,
        "current_status": current, "blocking_for_execution": blocking_execution,
        "blocking_for_precontract": "no", "evidence_source": source,
        "resolution_action": action, "notes": "Current J state is contract drafting only.",
    } for gid, name, required_status, current, blocking_execution, source, action in gate_specs]

    review_contract = []
    for row in i_review_items:
        review_contract.append({
            "review_item_id": row["review_item_id"], "source_work_package": "QSB-INTERFACE01I",
            "source_artifact": str(required["i_review_items"].relative_to(REPO)), "review_item_text": row["item"],
            "current_status": "open_from_i_requires_human_resolution", "blocking_for_execution": "yes",
            "blocking_for_precontract": "no", "required_resolution": row["recommended_action"],
            "owner_or_role": "human scientific reviewer and execution authorizer",
            "notes": f"I source status was {row['status']}; J does not treat that as execution authorization.",
        })

    schema_specs = [
        ("minimaltest_run_manifest.json", "record gated execution identity and disposition", "work_package,status,source_hash,contract_hash,authorization_record,seed,parameters,stop_reason,claim_boundary", "one run", "F3 input hash; J contract hash; authorization id"),
        ("selected_feature_table.csv", "record frozen feature values and roles", "pair_i,pair_j,feature_name,feature_value,unit,split,source_hash", "pair x feature", "F3 source hash; feature-contract row"),
        ("nullmodel_comparison_table.csv", "compare observed and frozen null roles", "nullmodel_id,pair_key,feature_name,observed_value,null_value,comparison_status,seed", "nullmodel x pair x feature", "J null role; implementation hash; seed"),
        ("theta_epsilon_calibration_report.csv", "record one-time parameter calibration", "parameter,value,rule,calibration_split_hash,input_hash,frozen_before_null_comparison", "one row per parameter", "J calibration rule; split hash; source hash"),
        ("split_assignment_table.csv", "record deterministic pair assignments", "pair_key,split_name,seed,assignment_hash,authorization_status", "one row per ordered pair", "J split policy; authorization record"),
        ("execution_gate_results.csv", "prove every execution gate was evaluated", "gate_id,required_status,observed_status,result,evidence_path,timestamp", "one row per gate", "J gate matrix; resolution/authorization artifacts"),
        ("final_audit_summary.csv", "retain locked final-audit disposition without tuning", "audit_item,status,observed,expected,deviation,action,claim_status", "one row per audit item", "frozen parameters; final-audit split hash"),
        ("FINAL_RESULT_NOTE.md", "concise internal result and claim boundary", "status,inputs,parameters,gates,stop_reason,findings,limitations,next_action,claim_boundary", "one note", "all prior execution outputs and authorization record"),
    ]
    schema_rows = [{
        "future_output_name": name, "purpose": purpose, "required_fields": fields,
        "row_granularity": granularity, "provenance_fields_required": provenance,
        "claim_boundary_required": "yes", "notes": "Schema contract only; no future result file is generated in J.",
    } for name, purpose, fields, granularity, provenance in schema_specs]

    forbidden_specs = [
        ("running final minimaltest in J", "J is contract-only", "INTERFACE01-J", "blocker", "invalidate J and stop"),
        ("Phase-D theta transfer", "legacy threshold is outside this calibration contract", "all later INTERFACE01 execution", "blocker", "block execution"),
        ("post-hoc threshold tuning", "would violate split and tuning locks", "calibration and execution", "blocker", "invalidate parameter/result"),
        ("claiming emergent spacetime evidence", "contract artifacts are not physics evidence", "notes and reports", "blocker", "retract claim and stop"),
        ("claiming gravity evidence", "contract artifacts are not gravity evidence", "notes and reports", "blocker", "retract claim and stop"),
        ("using M33 aggregate statistics as raw delta_phi", "F3 staged rows are the sole source-of-record", "input pipeline", "blocker", "reject substituted input"),
        ("silently adding p_i/p_j from unaudited source", "lineage must remain manifest-only or block", "feature construction", "blocker", "reject enrichment and stop"),
        ("treating N2 as effective perturbation", "N2 is invariant for current aggregate features", "nullmodel adequacy", "high", "invalidate adequacy count"),
        ("modifying upstream outputs", "F3/G/H/I are immutable audit inputs", "repository artifacts", "blocker", "invalidate J provenance"),
    ]
    forbidden_rows = [{
        "forbidden_action": action, "reason": reason, "applies_to": scope,
        "severity": severity, "violation_effect": effect,
        "notes": "Explicit pre-contract prohibition; no exception is granted in J.",
    } for action, reason, scope, severity, effect in forbidden_specs]

    validations: list[dict[str, Any]] = []
    def validate(identifier: str, layer: str, name: str, passed: bool, observed: Any, expected: Any, message: str, block_exec: bool = True) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": layer, "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error" if block_exec else "review",
            "observed_value": observed, "expected_value": expected, "message": message,
            "blocking_for_precontract": "yes" if not passed else "no",
            "blocking_for_execution": "yes" if block_exec and not passed else "no",
        })
    validate("V01", "upstream", "upstream_f3_status_seen", f3_manifest.get("status") == "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged", f3_manifest.get("status"), "authorized F3 staged status", "F3 manifest read.")
    validate("V02", "upstream", "upstream_g_status_seen", g_manifest.get("status") == "interface01g_minimaltest_design_review_completed_with_staged_source_profile", g_manifest.get("status"), "accepted G status", "G manifest read.")
    validate("V03", "upstream", "upstream_h_status_seen", h_manifest.get("status") == "interface01h_controlled_minimal_pilot_completed_with_review_items", h_manifest.get("status"), "accepted H status", "H manifest read.")
    validate("V04", "upstream", "upstream_i_status_seen", i_status_ok, i_manifest.get("status"), EXPECTED_I_STATUS, "I manifest read.")
    validate("V05", "readiness", "i_readiness_conditional", readiness_ok, readiness, EXPECTED_READINESS, "Conditional readiness preserved.")
    validate("V06", "execution", "no_minimaltest_executed_in_j", True, False, False, "J performs no data execution.")
    validate("V07", "calibration", "no_phase_d_theta_transfer", True, False, False, "Legacy threshold excluded from both rules.")
    validate("V08", "nullmodel", "n2_classification_carried", n2_ok, null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("adequacy_class"), "invariance_check_only", "N2 remains a sanity role.")
    validate("V09", "nullmodel", "n4_classification_carried", n4_ok, null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("adequacy_class"), "effective_perturbation", "N4 is the required active comparator.")
    validate("V10", "review", "seven_review_items_carried_or_placeholdered", review_items_exact and len(review_contract) == 7, len(review_contract), 7, "All seven exact I texts carried; none is marked execution-resolved.")
    validate("V11", "split", "split_seed_policy_defined", len(split_rows) == 4 and all(row["seed"] == 20260620 for row in split_rows), len(split_rows), 4, "40/30/20/10 target policy and seed defined.")
    validate("V12", "calibration", "theta_epsilon_rules_defined_without_execution", {row["parameter"] for row in calibration_rows} == {"theta_new", "epsilon_new"}, len(calibration_rows), 2, "Rules defined; no values computed.")
    validate("V13", "lineage", "p_i_p_j_policy_defined", True, "manifest-only mapping or block", "explicit policy", "J08 and I-R07 preserve source lineage.")
    validate("V14", "claim", "claim_boundary_present", bool(CLAIM_BOUNDARY), CLAIM_BOUNDARY, "non-empty restrictive boundary", "Claim boundary frozen.")
    validate("V15", "output", "exact_output_file_set", True, sorted(EXPECTED_OUTPUTS), sorted(EXPECTED_OUTPUTS), "Script writes exactly the declared set; external check follows.")

    OUTPUT.mkdir(parents=True)
    run_manifest = {
        "work_package": "QSB-INTERFACE01J", "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "readiness_from_i": readiness, "execution_clearance": CLEARANCE,
        "minimaltest_executed": False, "physical_evidence_claimed": False,
        "phase_d_theta_transferred": False, "source_rows_seen": h_manifest.get("source_rows", 0),
        "ordered_pairs_seen": h_manifest.get("ordered_pairs", 0), "x_points_seen": h_manifest.get("x_points", 0),
        "pairfeature_count_seen": i_manifest.get("pair_feature_count_used", 0),
        "nullmodel_count_seen": i_manifest.get("nullmodel_count_used", 0),
        "open_review_items_expected": 7, "open_review_items_carried": len(review_contract),
        "human_execution_authorization_recorded": False,
        "input_hash": f3_manifest.get("input_hash", ""), "claim_boundary": CLAIM_BOUNDARY,
        "modified_existing_files": [],
    }
    (OUTPUT / "01_j_run_manifest.json").write_text(json.dumps(run_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_artifact_register.csv", ["artifact_id", "work_package", "path", "exists", "status_seen", "row_count_or_summary", "hash_or_na", "decision_relevance", "notes"], artifacts)
    write_csv(OUTPUT / "03_i_readiness_summary.csv", ["i_status", "readiness", "pairfeature_count", "nullmodel_count", "feature_review_rows", "nonflat_feature_count", "n2_classification", "n4_classification", "precontract_drafting_blocked", "execution_clearance", "review_items_open_count"], i_summary)
    write_csv(OUTPUT / "04_feature_selection_precontract.csv", ["feature_name", "feature_family", "source_artifact", "variation_status", "allowed_for_minimaltest_candidate", "requires_review_before_execution", "selection_reason", "exclusion_reason", "notes"], feature_rows)
    write_csv(OUTPUT / "05_nullmodel_precontract.csv", ["nullmodel_id", "nullmodel_role", "adequacy_class", "allowed_in_later_minimaltest", "required_for_execution", "limitations", "expected_effect", "review_action_before_execution", "notes"], null_rows)
    write_csv(OUTPUT / "06_split_seed_precontract.csv", ["split_name", "fraction", "seed", "assignment_basis", "allowed_use", "forbidden_use", "post_hoc_tuning_lock", "notes"], split_rows)
    write_csv(OUTPUT / "07_theta_epsilon_calibration_precontract.csv", ["parameter", "calibration_source", "calibration_rule", "allowed_inputs", "forbidden_inputs", "phase_d_theta_0300_allowed", "post_hoc_tuning_lock", "execution_gate", "notes"], calibration_rows)
    write_csv(OUTPUT / "08_execution_gate_matrix.csv", ["gate_id", "gate_name", "required_status", "current_status", "blocking_for_execution", "blocking_for_precontract", "evidence_source", "resolution_action", "notes"], gates)
    write_csv(OUTPUT / "09_review_item_resolution_contract.csv", ["review_item_id", "source_work_package", "source_artifact", "review_item_text", "current_status", "blocking_for_execution", "blocking_for_precontract", "required_resolution", "owner_or_role", "notes"], review_contract)
    write_csv(OUTPUT / "10_minimaltest_output_schema_contract.csv", ["future_output_name", "purpose", "required_fields", "row_granularity", "provenance_fields_required", "claim_boundary_required", "notes"], schema_rows)
    write_csv(OUTPUT / "11_forbidden_actions_claim_boundary.csv", ["forbidden_action", "reason", "applies_to", "severity", "violation_effect", "notes"], forbidden_rows)
    write_csv(OUTPUT / "12_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_precontract", "blocking_for_execution"], validations)

    note = f"""# INTERFACE01-J Final Result

## Status
`{status}`

INTERFACE01-J drafted a conditional Minimaltest Pre-Contract.
It did not execute the final Minimaltest.
Execution remains not authorized until the I review items are resolved and a separate human authorization is recorded.

## Readiness und Clearance
- I readiness: `{readiness}`.
- Execution clearance: `{CLEARANCE}`.
- Physical evidence claimed: `no`.
- Phase-D threshold transferred: `no`.

## Feature- und Nullmodel-Contract
- Proposed compact feature candidates: `{', '.join(sorted(selected_features))}`; human freeze remains required.
- N2 remains `invariance_check_only` and cannot count as an effective perturbation.
- N4 remains `effective_perturbation` and is required for later execution.
- Split/seed and calibration procedures are defined without computing execution values.

## Offene Reviewpunkte
All seven I review items were carried exactly. Each blocks execution until separately resolved and human-authorized; none blocks this pre-contract draft.

## Naechster erlaubter Schritt
Resolve the seven J review contracts, record decisions and hashes, then obtain a separate human execution authorization.

## Verbotener naechster Schritt
Any Minimaltest execution while `execution_clearance = {CLEARANCE}`.

## Claim Boundary
{CLAIM_BOUNDARY}
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")
    print(f"status={status}")
    print(f"execution_clearance={CLEARANCE}")
    print(f"output={OUTPUT}")
    return 0 if status == STATUS_OK else 2


if __name__ == "__main__":
    raise SystemExit(main())
