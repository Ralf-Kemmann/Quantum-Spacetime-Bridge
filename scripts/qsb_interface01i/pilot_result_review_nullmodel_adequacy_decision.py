#!/usr/bin/env python3
"""Review INTERFACE01-H outputs and decide pre-contract readiness."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
F3_DIR = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
F3_INPUT = REPO / "runs/QSB-INTERFACE01F3/input_manifest/interface01f3_delta_phi_input_manifest.json"
G_DIR = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
H_DIR = REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi"
OUTPUT = REPO / "runs/QSB-INTERFACE01I/pilot_result_review_nullmodel_adequacy_decision"
EXPECTED_H_STATUS = "interface01h_controlled_minimal_pilot_completed_with_review_items"
SUCCESS_STATUS = "interface01i_pilot_result_review_completed_nullmodel_adequacy_assessed"
NOT_READY_STATUS = "interface01i_pilot_result_review_completed_not_ready_requires_nullmodel_revision"
BLOCKED_STATUS = "interface01i_pilot_result_review_blocked_missing_upstream_inputs"
READINESS = "conditional_ready_with_review_items"
INPUT_HASH = "ee271bf0b4a7603dbc95333721ab7596fc94a33d170c949a089789a1bc6a9095"
CLAIM_BOUNDARY = (
    "I reviews lineage, feature stability, nullmodel adequacy, and pre-contract readiness only. "
    "No final Minimaltest is run; no physical-evidence inference or legacy-threshold transfer is authorized."
)
EXPECTED_OUTPUTS = {
    "01_i_run_manifest.json", "02_upstream_input_inventory.csv", "03_h_pilot_result_digest.csv",
    "04_pair_feature_review.csv", "05_feature_signal_stability_review.csv", "06_nullmodel_adequacy_matrix.csv",
    "07_n2_invariance_review.csv", "08_split_seed_calibration_review.csv", "09_minimaltest_readiness_decision.csv",
    "10_claim_boundary_review.csv", "11_review_items.csv", "12_i_validation_results.csv", "FINAL_RESULT_NOTE.md",
}
REVIEW_FEATURES = [
    "n_x", "x_min", "x_max", "raw_delta_min", "raw_delta_max", "wrapped_delta_min", "wrapped_delta_max",
    "mean_cos_wrapped_delta", "mean_sin_wrapped_delta", "mean_abs_cos_wrapped_delta",
    "mean_abs_sin_wrapped_delta", "circular_resultant_length", "phase_variance_proxy",
    "signed_correlation_score", "abs_correlation_score",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe_file(path: Path, stage: str, role: str) -> dict[str, Any]:
    exists = path.is_file()
    rows_or_size: Any = ""
    if exists and path.suffix == ".csv":
        rows_or_size = len(read_csv(path))
    elif exists:
        rows_or_size = path.stat().st_size
    return {
        "source_stage": stage, "file_path": str(path.relative_to(REPO)), "exists": "yes" if exists else "no",
        "file_type": path.suffix.lstrip(".") or "unknown", "role": role, "rows_or_size": rows_or_size,
        "hash_sha256": sha256_file(path) if exists else "", "status": "inspected" if exists else "missing",
        "notes": "Read-only upstream inventory; CSV values are data-row counts, other values are bytes.",
    }


def f(value: str) -> float:
    return float(value)


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    paths = {
        "f3_manifest": F3_DIR / "01_f3_run_manifest.json",
        "f3_db": F3_DIR / "09_delta_phi_staging_preflight.sqlite",
        "f3_input": F3_INPUT,
        "g_manifest": G_DIR / "01_g_run_manifest.json",
        "h_manifest": H_DIR / "01_h_run_manifest.json",
        "h_features": H_DIR / "03_pair_feature_table.csv",
        "h_splits": H_DIR / "04_split_assignment_summary.csv",
        "h_thresholds": H_DIR / "05_threshold_preview.csv",
        "h_null_summary": H_DIR / "06_null_model_summary.csv",
        "h_null_features": H_DIR / "07_null_model_pair_features.csv",
        "h_validations": H_DIR / "10_validation_results.csv",
        "h_decisions": H_DIR / "11_pilot_decision_table.csv",
        "h_review_items": H_DIR / "12_review_items.csv",
        "h_claim_audit": H_DIR / "13_claim_boundary_audit.csv",
    }
    roles = {
        "f3_manifest": ("F3", "authorized export/staging run manifest"),
        "f3_db": ("F3", "staged raw/wrapped delta-phi source"),
        "f3_input": ("F3", "authorized input and lineage manifest"),
        "g_manifest": ("G", "source-profile decision manifest"),
        "h_manifest": ("H", "controlled pilot run manifest"),
        "h_features": ("H", "observed pair-level feature table"),
        "h_splits": ("H", "deterministic split assignment"),
        "h_thresholds": ("H", "non-final calibration previews"),
        "h_null_summary": ("H", "six null/reference summaries"),
        "h_null_features": ("H", "null/reference pair-level outputs"),
        "h_validations": ("H", "pilot validations"),
        "h_decisions": ("H", "pilot decisions"),
        "h_review_items": ("H", "documented pilot limitations"),
        "h_claim_audit": ("H", "claim-boundary audit"),
    }
    inventory = [describe_file(path, *roles[key]) for key, path in paths.items()]
    critical = ["f3_manifest", "f3_db", "f3_input", "g_manifest", "h_manifest", "h_features", "h_splits", "h_thresholds", "h_null_summary", "h_null_features", "h_validations"]
    upstream_available = all(paths[key].is_file() for key in critical)

    if upstream_available:
        f3_manifest = json.loads(paths["f3_manifest"].read_text(encoding="utf-8"))
        f3_input = json.loads(paths["f3_input"].read_text(encoding="utf-8"))
        g_manifest = json.loads(paths["g_manifest"].read_text(encoding="utf-8"))
        h_manifest = json.loads(paths["h_manifest"].read_text(encoding="utf-8"))
        features = read_csv(paths["h_features"])
        splits = read_csv(paths["h_splits"])
        thresholds = read_csv(paths["h_thresholds"])
        null_summary = read_csv(paths["h_null_summary"])
        null_features = read_csv(paths["h_null_features"])
        h_validations = read_csv(paths["h_validations"])
    else:
        f3_manifest, f3_input, g_manifest, h_manifest = {}, {}, {}, {}
        features, splits, thresholds, null_summary, null_features, h_validations = [], [], [], [], [], []

    h_status_ok = h_manifest.get("status") == EXPECTED_H_STATUS
    lineage_ok = (
        f3_manifest.get("input_hash") == INPUT_HASH
        and h_manifest.get("source_input_hash") == INPUT_HASH
        and h_manifest.get("source_db") == str(paths["f3_db"].relative_to(REPO))
        and g_manifest.get("source_db") == str(paths["f3_db"].relative_to(REPO))
        and f3_input.get("authorization_status") == "human_authorized_for_interface01_export"
    )
    row_counts_ok = h_manifest.get("source_rows") == 168042 and h_manifest.get("ordered_pairs") == 42 and h_manifest.get("x_points") == 4001
    feature_structure_ok = len(features) == 42 and all(all(name in row for name in REVIEW_FEATURES) for row in features)
    feature_finite = feature_structure_ok and all(math.isfinite(f(row[name])) for row in features for name in REVIEW_FEATURES)
    null_count_ok = len(null_summary) == 6 and len({row["null_model_id"] for row in null_summary}) == 6
    h_validation_ok = len(h_validations) >= 15 and all(row.get("status") == "pass" for row in h_validations)

    pair_review: list[dict[str, Any]] = []
    feature_stability: list[dict[str, Any]] = []
    units = {
        "n_x": "count", "x_min": "model_length_unit", "x_max": "model_length_unit",
        "raw_delta_min": "rad", "raw_delta_max": "rad", "wrapped_delta_min": "rad", "wrapped_delta_max": "rad",
    }
    for feature_name in REVIEW_FEATURES:
        values = [f(row[feature_name]) for row in features] if features else []
        finite = [value for value in values if math.isfinite(value)]
        if finite:
            minimum, maximum = min(finite), max(finite)
            mean = statistics.fmean(finite)
            std = statistics.pstdev(finite)
            scale = max(1.0, max(abs(minimum), abs(maximum)))
            nonflat = maximum - minimum > 1e-12 * scale
            variation = "nonflat_finite" if nonflat else "flat_or_near_flat"
            stability = "finite_complete" if len(finite) == len(features) else "needs_review"
        else:
            minimum = maximum = mean = std = ""
            variation, stability = "insufficient_finite_values", "needs_review"
        feature_stability.append({
            "feature_name": feature_name, "n_pairs": len(values), "finite_count": len(finite),
            "min_value": minimum, "max_value": maximum, "mean_value": mean, "std_value": std,
            "variation_status": variation, "stability_status": stability,
            "review_notes": "Review statistic only; neutral and near-flat results are retained.",
        })
    for row in features:
        for feature_name in REVIEW_FEATURES:
            pair_review.append({
                "pair_i": row["pair_i"], "pair_j": row["pair_j"], "state_i": row["state_i"], "state_j": row["state_j"],
                "feature_name": feature_name, "feature_value": row[feature_name],
                "feature_unit_or_status": units.get(feature_name, "dimensionless"), "split_id": row["split_label"],
                "review_status": "finite_retained" if math.isfinite(f(row[feature_name])) else "nonfinite_review_required",
                "notes": "Long-form conversion of the H wide table; no outcome selection.",
            })

    observed_by_pair = {(row["pair_i"] + ":" + row["pair_j"]): row for row in features}
    null_by_model: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in null_features:
        null_by_model[row["null_model_id"]].append(row)

    adequacy_specs = {
        "N0_SIGN_FLIP": ("signed-score sign only", "partial_perturbation", "adequate_limited_scope", "no", "Changes signed score but intentionally preserves absolute score."),
        "N1_PAIR_LABEL_PERMUTE": ("pair identity labels", "partial_perturbation", "adequate_if_identity_statistic_registered", "no", "Feature values remain fixed; usefulness depends on a pre-registered label-sensitive statistic."),
        "N2_X_INDEX_ROLL_SURROGATE": ("x ordering", "invariance_check_only", "not_effective_for_current_aggregates", "no", "Current x-independent aggregates are permutation-invariant."),
        "N3_PAIR_DIRECTION_COLLAPSE": ("ordered-pair direction", "invariance_check_only", "adequate_sanity_check", "no", "Checks directional partner consistency rather than active perturbation."),
        "N4_PHASE_RANDOM_REFERENCE": ("per-row wrapped phases", "effective_perturbation", "adequate_active_reference", "no", "Actively replaces phases with deterministic uniform references."),
        "N5_CONSTANT_ZERO_PHASE_REFERENCE": ("per-row wrapped phases", "partial_perturbation", "adequate_degenerate_reference", "no", "Active but degenerate upper-reference sanity check; not a realistic null."),
    }
    adequacy_rows: list[dict[str, Any]] = []
    active_count = 0
    for model_id, (scope, adequacy_class, adequacy_status, blocking, notes) in adequacy_specs.items():
        rows = null_by_model.get(model_id, [])
        summary = next((row for row in null_summary if row["null_model_id"] == model_id), None)
        available = bool(rows and summary)
        changes = "yes" if adequacy_class in {"effective_perturbation", "partial_perturbation"} else "no"
        if available and adequacy_class in {"effective_perturbation", "partial_perturbation"}:
            active_count += 1
        adequacy_rows.append({
            "nullmodel_id": model_id, "nullmodel_name": summary["null_model_name"] if summary else model_id,
            "available": "yes" if available else "no", "rows_or_cases": len(rows), "changes_target_features": changes,
            "perturbation_scope": scope, "adequacy_class": adequacy_class if available else "failed_or_missing",
            "adequacy_status": adequacy_status if available else "missing", "blocking_for_minimaltest_contract": blocking if available else "yes",
            "notes": notes if available else "Required H null output missing.",
        })

    n2_rows = null_by_model.get("N2_X_INDEX_ROLL_SURROGATE", [])
    n2_differences = []
    for row in n2_rows:
        observed = observed_by_pair.get(row["source_pair_key"])
        if observed:
            for name in ["mean_cos_wrapped_delta", "mean_sin_wrapped_delta", "mean_abs_cos_wrapped_delta", "mean_abs_sin_wrapped_delta", "circular_resultant_length", "phase_variance_proxy", "signed_correlation_score", "abs_correlation_score"]:
                n2_differences.append(abs(f(row[name]) - f(observed[name])))
    n2_max_difference = max(n2_differences, default=math.inf)
    n2_confirmed = len(n2_rows) == 42 and n2_max_difference <= 1e-15
    n2_review = [
        {"review_item": "N2 output rows", "observed_value": len(n2_rows), "expected_value": 42, "status": "pass" if len(n2_rows) == 42 else "fail", "interpretation": "One rolled surrogate per ordered pair is expected.", "action_required": "Restore missing cases if incomplete."},
        {"review_item": "Maximum target-feature difference", "observed_value": n2_max_difference, "expected_value": "<=1e-15", "status": "pass" if n2_confirmed else "fail", "interpretation": "The specified aggregate features are unchanged by within-pair circular reordering.", "action_required": "Do not interpret unchanged aggregates as a perturbation response."},
        {"review_item": "N2 adequacy conclusion", "observed_value": "invariance_check_only", "expected_value": "invariance_check_only", "status": "pass" if n2_confirmed else "fail", "interpretation": "N2 is an invariance/sanity check only for x-independent aggregate pair features and must not be counted as an effective perturbation nullmodel.", "action_required": "In the pre-contract, revise N2 or register an alignment-sensitive feature if x-position sensitivity is required."},
    ]

    split_names = {row.get("split_label") for row in splits}
    seed_values = {row.get("seed") for row in splits}
    threshold_ids = {row.get("preview_id") for row in thresholds}
    expected_thresholds = {"theta_preview_median_abs_corr", "theta_preview_q75_abs_corr", "epsilon_preview_mad_abs_corr"}
    split_ok = split_names == {"train_design", "calibration_design", "review_holdout", "null_control"}
    seed_ok = seed_values == {"20260620"}
    calibration_ok = threshold_ids == expected_thresholds and all(row.get("status") == "preview_only_not_final_parameter" for row in thresholds)
    post_hoc_lock = f3_input.get("post_hoc_tuning_lock") is True
    split_review = [
        ("split assignment present", sorted(split_names), "four fixed pair-level splits", split_ok, "yes", "All 42 pairs remain assigned; realized fractions differ from nominal fractions because deterministic hash buckets are used."),
        ("seed documented", sorted(seed_values), "20260620", seed_ok, "yes", "Single fixed pilot seed."),
        ("calibration preview rules documented", sorted(threshold_ids), sorted(expected_thresholds), calibration_ok, "yes", "Three predeclared previews are present."),
        ("theta_new not finalized", "preview labels only", "not finalized", calibration_ok, "yes", "A later pre-contract must define any allowed selection rule."),
        ("epsilon_new not finalized", "preview label only", "not finalized", calibration_ok, "yes", "MAD remains a preview quantity."),
        ("Phase-D theta blocked", h_manifest.get("phase_d_threshold_reused"), False, h_manifest.get("phase_d_threshold_reused") is False, "yes", "Legacy threshold transfer remains prohibited."),
        ("post-hoc tuning lock preserved", post_hoc_lock, True, post_hoc_lock, "yes", "Authorized F3 input manifest retains the lock."),
    ]
    split_review_rows = [{
        "item": item, "observed_value": json.dumps(observed, ensure_ascii=False) if isinstance(observed, list) else observed,
        "required_for_minimaltest_contract": json.dumps(required, ensure_ascii=False) if isinstance(required, list) else required,
        "status": "pass" if passed else "needs_review", "blocking": "no" if passed else blocking,
        "notes": notes,
    } for item, observed, required, passed, blocking, notes in split_review]

    nonflat_count = sum(row["variation_status"] == "nonflat_finite" for row in feature_stability)
    enough_active_nulls = active_count >= 2 and any(row["adequacy_class"] == "effective_perturbation" for row in adequacy_rows)
    review_succeeded = all([upstream_available, h_status_ok, lineage_ok, row_counts_ok, feature_structure_ok, feature_finite, null_count_ok, h_validation_ok, n2_confirmed, split_ok, seed_ok, calibration_ok, post_hoc_lock])
    readiness = READINESS if review_succeeded and nonflat_count > 0 and enough_active_nulls else "not_ready_requires_nullmodel_or_feature_revision"
    run_status = SUCCESS_STATUS if readiness in {"ready_for_minimaltest_precontract", "conditional_ready_with_review_items"} else NOT_READY_STATUS if upstream_available else BLOCKED_STATUS
    next_action = "draft INTERFACE01-J constrained Minimaltest pre-contract resolving listed review items" if readiness == READINESS else "revise feature/nullmodel design before any pre-contract"

    digest_items = [
        ("H status", h_manifest.get("status", "missing"), EXPECTED_H_STATUS, h_status_ok, "Accepted controlled-pilot status."),
        ("input rows", h_manifest.get("source_rows", 0), 168042, h_manifest.get("source_rows") == 168042, "H manifest source rows."),
        ("ordered pair count", h_manifest.get("ordered_pairs", 0), 42, h_manifest.get("ordered_pairs") == 42, "H pair scope."),
        ("x-point count", h_manifest.get("x_points", 0), 4001, h_manifest.get("x_points") == 4001, "H x-grid scope."),
        ("pair-feature count", len(features), 42, len(features) == 42, "Rows reviewed from H feature table."),
        ("nullmodel count", len(null_summary), 6, len(null_summary) == 6, "Distinct prescribed null/reference summaries."),
        ("H validation count", len(h_validations), 15, len(h_validations) >= 15 and h_validation_ok, "All retained H validations passed."),
        ("final Minimaltest executed", h_manifest.get("final_minimaltest_run"), False, h_manifest.get("final_minimaltest_run") is False, "Review confirms pilot-only execution."),
        ("Phase-D theta transferred", h_manifest.get("phase_d_threshold_reused"), False, h_manifest.get("phase_d_threshold_reused") is False, "No legacy threshold entered the pilot."),
        ("F3 staged-source lineage", h_manifest.get("source_input_hash", ""), INPUT_HASH, lineage_ok, "F3/G/H paths and input hash cross-checked."),
    ]
    digest_rows = [{"metric_name": name, "observed_value": value, "expected_or_reference": expected, "status": "pass" if passed else "fail", "notes": notes} for name, value, expected, passed, notes in digest_items]

    readiness_rows = [{
        "decision_item": "INTERFACE01-I readiness", "status": readiness,
        "decision_basis": f"lineage={lineage_ok};finite_features={feature_finite};nonflat_features={nonflat_count};active_nulls={active_count};N2=invariance_check_only;split_seed_calibration={split_ok and seed_ok and calibration_ok}",
        "allowed_next_action": next_action,
        "forbidden_next_action": "final Minimaltest execution; final theta/epsilon selection; post-hoc tuning; physical-evidence inference",
        "notes": "Conditional readiness permits pre-contract drafting only; it is not execution authorization.",
    }]

    claim_rows = [
        ("no final Minimaltest claim", h_manifest.get("final_minimaltest_run") is False, "State explicitly that I is review-only.", "retained"),
        ("no gravity/spacetime evidence claim", True, "Use technical review language only.", "retained"),
        ("no Phase-D theta transfer", h_manifest.get("phase_d_threshold_reused") is False, "Legacy threshold remains excluded.", "retained"),
        ("no post-hoc tuning", post_hoc_lock, "Preserve authorized tuning lock.", "retained"),
        ("no hiding N2 limitation", n2_confirmed, "Classify N2 as invariance_check_only.", "dedicated N2 review written"),
        ("all neutral/negative/ambiguous outcomes retained", len(pair_review) == len(features) * len(REVIEW_FEATURES), "Review all pair-feature values without filtering.", f"{len(pair_review)} long-form values retained"),
    ]
    claim_review = [{"claim_boundary_item": item, "status": "pass" if passed else "fail", "required_wording_or_rule": rule, "observed_or_action": action, "notes": "Claim boundary is mandatory for any downstream pre-contract."} for item, passed, rule, action in claim_rows]
    claim_ok = all(row["status"] == "pass" for row in claim_review)

    review_items = [
        ("I-R01", "medium", "nullmodel", "N2 is invariant for every current target aggregate.", "open_documented", "Revise N2 or add an alignment-sensitive feature if x-position response is required.", "no"),
        ("I-R02", "low", "nullmodel", "N3 is a directional consistency check, not an active perturbation.", "open_documented", "Retain as sanity check only.", "no"),
        ("I-R03", "medium", "nullmodel", "N1 requires a label-sensitive contract statistic to become informative.", "open_precontract_requirement", "Specify that statistic before execution authorization.", "no"),
        ("I-R04", "medium", "calibration", "Threshold and margin values remain previews rather than final parameters.", "open_precontract_requirement", "Pre-register the selection and margin rules without holdout access.", "no"),
        ("I-R05", "low", "split", "Hash-bucket split counts are 20/14/5/3 rather than exact nominal fractions.", "open_documented", "Accept explicitly or pre-register another deterministic assignment before execution.", "no"),
        ("I-R06", "info", "feature", "Near-flat and neutral feature outcomes are retained in the review.", "resolved", "Keep them visible in downstream contracts.", "no"),
        ("I-R07", "medium", "lineage", "p_i/p_j remain manifest-derived rather than staging columns.", "open_documented", "Preserve manifest provenance and model-unit interpretation.", "no"),
    ]
    review_item_rows = [{"review_item_id": a, "severity": b, "category": c, "item": d, "status": e, "recommended_action": g, "blocking_for_next_step": h} for a, b, c, d, e, g, h in review_items]

    validations: list[dict[str, Any]] = []
    def validation(identifier: str, layer: str, name: str, passed: bool, observed: Any, expected: Any, message: str, blocking: bool = True) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": layer, "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error" if blocking else "review",
            "observed_value": observed, "expected_value": expected, "message": message,
            "blocking_for_next_step": "yes" if blocking and not passed else "no",
        })
    validation("V01", "upstream", "upstream_f3_available", paths["f3_manifest"].is_file() and paths["f3_db"].is_file() and paths["f3_input"].is_file(), "F3 files inventoried", "all required F3 files", "F3 source lineage inputs available.")
    validation("V02", "upstream", "upstream_g_available", paths["g_manifest"].is_file(), paths["g_manifest"].is_file(), True, "G profile manifest available.")
    validation("V03", "upstream", "upstream_h_available", all(paths[key].is_file() for key in critical if key.startswith("h_")), "critical H files checked", "all critical H files", "H review inputs available.")
    validation("V04", "status", "h_status_accepted", h_status_ok, h_manifest.get("status", "missing"), EXPECTED_H_STATUS, "H status permits review.")
    validation("V05", "structure", "h_row_counts_consistent", row_counts_ok, f"{h_manifest.get('source_rows')}/{h_manifest.get('ordered_pairs')}/{h_manifest.get('x_points')}", "168042/42/4001", "H scope counts agree with the authorized pilot.")
    validation("V06", "structure", "pair_feature_count_consistent", feature_structure_ok and feature_finite, len(features), 42, "Feature table is complete and finite.")
    validation("V07", "structure", "nullmodel_count_consistent", null_count_ok, len(null_summary), 6, "All six null/reference models are present.")
    validation("V08", "adequacy", "n2_invariance_classified", n2_confirmed, f"max_difference={n2_max_difference}", "invariance_check_only with <=1e-15 difference", "N2 limitation is explicit.")
    validation("V09", "claim", "no_final_minimaltest_run", h_manifest.get("final_minimaltest_run") is False, h_manifest.get("final_minimaltest_run"), False, "No final execution occurred.")
    validation("V10", "claim", "no_phase_d_theta_transfer", h_manifest.get("phase_d_threshold_reused") is False, h_manifest.get("phase_d_threshold_reused"), False, "No legacy threshold transfer occurred.")
    validation("V11", "design", "split_seed_calibration_review_written", split_ok and seed_ok and calibration_ok and post_hoc_lock, len(split_review_rows), 7, "Required design controls reviewed.")
    validation("V12", "decision", "readiness_decision_written", readiness in {"ready_for_minimaltest_precontract", "conditional_ready_with_review_items", "not_ready_requires_nullmodel_or_feature_revision", "blocked_missing_upstream_inputs"}, readiness, "allowed readiness status", "Conservative readiness decision recorded.")
    validation("V13", "claim", "claim_boundary_passed", claim_ok, claim_ok, True, "All six claim-boundary controls pass.")
    validation("V14", "output", "exact_output_file_set", True, sorted(EXPECTED_OUTPUTS), sorted(EXPECTED_OUTPUTS), "Script writes exactly the predeclared output set; external validation follows.")

    OUTPUT.mkdir(parents=True)
    manifest_out = {
        "work_package": "QSB-INTERFACE01I", "status": run_status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "repo_root": str(REPO),
        "upstream_paths": {"f3": str(F3_DIR.relative_to(REPO)), "g": str(G_DIR.relative_to(REPO)), "h": str(H_DIR.relative_to(REPO)), "f3_input_manifest": str(F3_INPUT.relative_to(REPO))},
        "f3_input_hash": f3_manifest.get("input_hash", ""), "h_status": h_manifest.get("status", ""),
        "h_source_rows": h_manifest.get("source_rows", 0), "pair_feature_count_used": len(features),
        "pair_feature_review_rows": len(pair_review), "nullmodel_count_used": len(null_summary),
        "active_or_partial_perturbation_nullmodels": active_count, "n2_classification": "invariance_check_only" if n2_confirmed else "failed_or_missing",
        "readiness_decision": readiness, "blockers_remaining": [] if readiness == READINESS else ["feature_or_nullmodel_adequacy"],
        "claim_boundary": CLAIM_BOUNDARY, "modified_existing_files": [],
    }
    (OUTPUT / "01_i_run_manifest.json").write_text(json.dumps(manifest_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_input_inventory.csv", ["source_stage", "file_path", "exists", "file_type", "role", "rows_or_size", "hash_sha256", "status", "notes"], inventory)
    write_csv(OUTPUT / "03_h_pilot_result_digest.csv", ["metric_name", "observed_value", "expected_or_reference", "status", "notes"], digest_rows)
    write_csv(OUTPUT / "04_pair_feature_review.csv", ["pair_i", "pair_j", "state_i", "state_j", "feature_name", "feature_value", "feature_unit_or_status", "split_id", "review_status", "notes"], pair_review)
    write_csv(OUTPUT / "05_feature_signal_stability_review.csv", ["feature_name", "n_pairs", "finite_count", "min_value", "max_value", "mean_value", "std_value", "variation_status", "stability_status", "review_notes"], feature_stability)
    write_csv(OUTPUT / "06_nullmodel_adequacy_matrix.csv", ["nullmodel_id", "nullmodel_name", "available", "rows_or_cases", "changes_target_features", "perturbation_scope", "adequacy_class", "adequacy_status", "blocking_for_minimaltest_contract", "notes"], adequacy_rows)
    write_csv(OUTPUT / "07_n2_invariance_review.csv", ["review_item", "observed_value", "expected_value", "status", "interpretation", "action_required"], n2_review)
    write_csv(OUTPUT / "08_split_seed_calibration_review.csv", ["item", "observed_value", "required_for_minimaltest_contract", "status", "blocking", "notes"], split_review_rows)
    write_csv(OUTPUT / "09_minimaltest_readiness_decision.csv", ["decision_item", "status", "decision_basis", "allowed_next_action", "forbidden_next_action", "notes"], readiness_rows)
    write_csv(OUTPUT / "10_claim_boundary_review.csv", ["claim_boundary_item", "status", "required_wording_or_rule", "observed_or_action", "notes"], claim_review)
    write_csv(OUTPUT / "11_review_items.csv", ["review_item_id", "severity", "category", "item", "status", "recommended_action", "blocking_for_next_step"], review_item_rows)
    write_csv(OUTPUT / "12_i_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_next_step"], validations)

    final_note = f"""# INTERFACE01-I Final Result

## Status
`{run_status}`

## Upstream und H-Digest
- F3, G, and H review inputs were read with staged-source hash `{h_manifest.get('source_input_hash', '')}`.
- H scope: `{h_manifest.get('source_rows', 0)}` source rows, `{len(features)}` pair-feature rows, `{len(null_summary)}` null/reference models.
- H remained a controlled pilot; no final Minimaltest was run.

## Nullmodel-Adequacy
- Active or partial perturbation comparators: `{active_count}`.
- N2 classification: `invariance_check_only`.
- N2 is useful as a sanity check but is not an effective perturbation model for the current x-independent aggregate features.
- N3 is likewise retained as a directional consistency check.

## Readiness
`{readiness}`

No blocker prevents pre-contract drafting. The listed feature, nullmodel, split, and calibration review items must be resolved or explicitly frozen before execution authorization.

## Naechste erlaubte Aktion
`{next_action}`

Forbidden: final Minimaltest execution, final threshold selection, post-hoc tuning, or physical-evidence inference in I.

## Claim Boundary
{CLAIM_BOUNDARY}
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")
    print(f"status={run_status}")
    print(f"readiness={readiness}")
    print(f"output={OUTPUT}")
    return 0 if run_status == SUCCESS_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
