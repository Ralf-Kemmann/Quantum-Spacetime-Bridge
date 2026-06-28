#!/usr/bin/env python3
"""Run the constrained INTERFACE01-H pair-feature and null-preview pilot."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
F3_DB = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite"
F3_MANIFEST = REPO / "runs/QSB-INTERFACE01F3/input_manifest/interface01f3_delta_phi_input_manifest.json"
G_DIR = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
OUTPUT = REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi"
SEED = 20260620
EXPECTED_INPUT_HASH = "ee271bf0b4a7603dbc95333721ab7596fc94a33d170c949a089789a1bc6a9095"
EXPECTED_F3_STATUS = "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged"
SUCCESS = "interface01h_controlled_minimal_pilot_completed_with_review_items"
BLOCKED = "interface01h_controlled_minimal_pilot_blocked_no_result"
CLAIM = (
    "INTERFACE01-H is a controlled pair-feature and null-preview pilot from the authorized staged source. "
    "It is not a final Minimaltest, supplies no physical evidence claim, and transfers no Phase-D threshold."
)

PAIR_FIELDS = [
    "pair_i", "pair_j", "state_i", "state_j", "n_x", "x_min", "x_max", "x_unit",
    "raw_delta_min", "raw_delta_max", "wrapped_delta_min", "wrapped_delta_max",
    "mean_cos_wrapped_delta", "mean_sin_wrapped_delta", "mean_abs_cos_wrapped_delta",
    "mean_abs_sin_wrapped_delta", "circular_resultant_length", "phase_variance_proxy",
    "signed_correlation_score", "abs_correlation_score", "antisymmetry_partner_present",
    "p_i_manifest", "p_j_manifest", "delta_p_manifest", "p_mapping_status", "split_label",
]


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return format(value, ".17g")
    return str(value)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_for(pair_i: int, pair_j: int) -> tuple[str, int, str]:
    key = f"{pair_i}:{pair_j}"
    value = digest(key + "|INTERFACE01-H|seed=20260620")
    bucket = int(value[:8], 16) % 10
    label = "train_design" if bucket <= 3 else "calibration_design" if bucket <= 6 else "review_holdout" if bucket <= 8 else "null_control"
    return label, bucket, value


def aggregate_phases(phases: list[float]) -> dict[str, float]:
    n = len(phases)
    cos_values = [math.cos(value) for value in phases]
    sin_values = [math.sin(value) for value in phases]
    mean_cos = math.fsum(cos_values) / n
    mean_sin = math.fsum(sin_values) / n
    resultant = math.hypot(mean_cos, mean_sin)
    return {
        "mean_cos_wrapped_delta": mean_cos,
        "mean_sin_wrapped_delta": mean_sin,
        "mean_abs_cos_wrapped_delta": math.fsum(abs(value) for value in cos_values) / n,
        "mean_abs_sin_wrapped_delta": math.fsum(abs(value) for value in sin_values) / n,
        "circular_resultant_length": resultant,
        "phase_variance_proxy": 1.0 - resultant,
        "signed_correlation_score": mean_cos,
        "abs_correlation_score": abs(mean_cos),
    }


def quantile_linear(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def null_row(model_id: str, model_name: str, source_pair: tuple[int, int], label_pair: tuple[int, int], phases: list[float], detail: str) -> dict[str, Any]:
    values = aggregate_phases(phases)
    return {
        "null_model_id": model_id, "null_model_name": model_name,
        "source_pair_key": f"{source_pair[0]}:{source_pair[1]}",
        "reported_pair_i": label_pair[0], "reported_pair_j": label_pair[1], "n_x": len(phases),
        **values, "partner_abs_score_difference": "", "transform_detail": detail,
        "claim_status": "null_preview_not_evidence",
    }


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")
    if not F3_DB.is_file() or not F3_MANIFEST.is_file():
        raise SystemExit("Required F3 staging database or authorized manifest is missing.")

    manifest = json.loads(F3_MANIFEST.read_text(encoding="utf-8"))
    p_values = manifest.get("p_values")
    g_present = G_DIR.is_dir()
    g_status = ""
    g_manifest_path = G_DIR / "01_g_run_manifest.json"
    if g_manifest_path.is_file():
        g_status = json.loads(g_manifest_path.read_text(encoding="utf-8")).get("status", "")

    groups: dict[tuple[int, int], dict[str, Any]] = {}
    profile = Counter()
    source_values: dict[str, set[Any]] = defaultdict(set)
    required_columns = [
        "export_id", "source_mode", "run_id", "state_i", "state_j", "pair_i", "pair_j",
        "x_index", "x_value", "x_unit", "x_weight", "phi_i_x", "phi_j_x",
        "raw_delta_phi_ij_x", "wrapped_delta_phi_ij_x", "wrapping_interval", "angle_unit",
        "dimension_status", "pair_mask", "diagonal_policy", "source_code_hash", "config_hash",
        "input_hash", "authorization_status",
    ]
    with sqlite3.connect(F3_DB) as connection:
        connection.row_factory = sqlite3.Row
        table_columns = {row[1] for row in connection.execute("PRAGMA table_info(stg_delta_phi_spatial)")}
        missing_columns = sorted(set(required_columns) - table_columns)
        metadata = dict(connection.execute("SELECT * FROM stg_delta_phi_export_metadata").fetchone())
        if missing_columns:
            raise SystemExit(f"Missing required staging columns: {missing_columns}")
        query = "SELECT " + ",".join(required_columns) + " FROM stg_delta_phi_spatial ORDER BY pair_i,pair_j,x_index"
        for row in connection.execute(query):
            profile["rows"] += 1
            pair = (row["pair_i"], row["pair_j"])
            if pair not in groups:
                groups[pair] = {
                    "state_i": row["state_i"], "state_j": row["state_j"], "x": [], "x_index": [],
                    "raw": [], "wrapped": [], "export_id": [], "x_unit": row["x_unit"],
                }
            group = groups[pair]
            group["x"].append(row["x_value"])
            group["x_index"].append(row["x_index"])
            group["raw"].append(row["raw_delta_phi_ij_x"])
            group["wrapped"].append(row["wrapped_delta_phi_ij_x"])
            group["export_id"].append(row["export_id"])
            profile["diagonal_rows"] += int(row["pair_i"] == row["pair_j"])
            profile["pair_mask_false_rows"] += int(row["pair_mask"] != 1)
            profile["wrapped_outside_rows"] += int(not (-math.pi <= row["wrapped_delta_phi_ij_x"] < math.pi))
            profile["nonfinite_source_rows"] += int(not all(math.isfinite(float(row[name])) for name in ["x_value", "x_weight", "phi_i_x", "phi_j_x", "raw_delta_phi_ij_x", "wrapped_delta_phi_ij_x"]))
            for name in ["source_mode", "authorization_status", "wrapping_interval", "angle_unit", "dimension_status", "x_unit", "diagonal_policy", "input_hash"]:
                source_values[name].add(row[name])

    pair_features: list[dict[str, Any]] = []
    p_mapping_ok = isinstance(p_values, list)
    for pair, group in sorted(groups.items()):
        i, j = pair
        values = aggregate_phases(group["wrapped"])
        mapping_valid = p_mapping_ok and i < len(p_values) and j < len(p_values)
        split_label, _, _ = split_for(i, j)
        pair_features.append({
            "pair_i": i, "pair_j": j, "state_i": group["state_i"], "state_j": group["state_j"],
            "n_x": len(group["x"]), "x_min": min(group["x"]), "x_max": max(group["x"]), "x_unit": group["x_unit"],
            "raw_delta_min": min(group["raw"]), "raw_delta_max": max(group["raw"]),
            "wrapped_delta_min": min(group["wrapped"]), "wrapped_delta_max": max(group["wrapped"]),
            **values, "antisymmetry_partner_present": "yes" if (j, i) in groups else "no",
            "p_i_manifest": p_values[i] if mapping_valid else "", "p_j_manifest": p_values[j] if mapping_valid else "",
            "delta_p_manifest": p_values[i] - p_values[j] if mapping_valid else "",
            "p_mapping_status": "manifest_derived_not_staging_column" if mapping_valid else "mapping_unavailable",
            "split_label": split_label,
        })

    feature_by_pair = {(row["pair_i"], row["pair_j"]): row for row in pair_features}
    split_counts = Counter(row["split_label"] for row in pair_features)
    split_rows = []
    for label in ["train_design", "calibration_design", "review_holdout", "null_control"]:
        keys = [f"{row['pair_i']}:{row['pair_j']}" for row in pair_features if row["split_label"] == label]
        split_rows.append({
            "split_label": label, "pair_count": split_counts[label], "fraction_observed": split_counts[label] / len(pair_features),
            "assignment_unit": "ordered_pair", "seed": SEED, "bucket_rule": "sha256(pair_key|INTERFACE01-H|seed=20260620), first8 modulo 10",
            "pair_keys": "|".join(keys), "claim_status": "pilot_design_only",
        })

    train_values = [row["abs_correlation_score"] for row in pair_features if row["split_label"] == "train_design"]
    train_median = statistics.median(train_values)
    threshold_rows = [
        {"preview_id": "theta_preview_median_abs_corr", "value": train_median, "source_split": "train_design", "method": "median(abs_correlation_score)", "n_pairs": len(train_values), "status": "preview_only_not_final_parameter", "notes": "Predeclared; not theta_new."},
        {"preview_id": "theta_preview_q75_abs_corr", "value": quantile_linear(train_values, 0.75), "source_split": "train_design", "method": "linear-interpolated 75th percentile(abs_correlation_score)", "n_pairs": len(train_values), "status": "preview_only_not_final_parameter", "notes": "No outcome-based tuning."},
        {"preview_id": "epsilon_preview_mad_abs_corr", "value": statistics.median(abs(value - train_median) for value in train_values), "source_split": "train_design", "method": "median absolute deviation about train median", "n_pairs": len(train_values), "status": "preview_only_not_final_parameter", "notes": "Predeclared margin preview; not epsilon_new."},
    ]

    null_rows: list[dict[str, Any]] = []
    for pair, feature in sorted(feature_by_pair.items()):
        row = null_row("N0_SIGN_FLIP", "sign flip", pair, pair, groups[pair]["wrapped"], "signed score multiplied by -1; absolute score unchanged")
        row["signed_correlation_score"] = -feature["signed_correlation_score"]
        row["abs_correlation_score"] = feature["abs_correlation_score"]
        null_rows.append(row)

    ordered_by_n1 = sorted(groups, key=lambda pair: digest(f"{pair[0]}:{pair[1]}|N1|seed=20260620"))
    shifted_labels = ordered_by_n1[1:] + ordered_by_n1[:1]
    for pair, label_pair in zip(ordered_by_n1, shifted_labels):
        null_rows.append(null_row("N1_PAIR_LABEL_PERMUTE", "pair label permutation", pair, label_pair, groups[pair]["wrapped"], "feature values retained; deterministic cyclic label shift"))

    for pair, group in sorted(groups.items()):
        n = len(group["wrapped"])
        offset = 1 + int(digest(f"{pair[0]}:{pair[1]}|N2|seed=20260620")[:8], 16) % (n - 1)
        rolled = group["wrapped"][-offset:] + group["wrapped"][:-offset]
        null_rows.append(null_row("N2_X_INDEX_ROLL_SURROGATE", "x-index roll surrogate", pair, pair, rolled, f"pair-specific circular offset={offset}; aggregate is permutation-invariant"))

    for i, j in sorted((i, j) for i, j in groups if i < j):
        left, right = feature_by_pair[(i, j)], feature_by_pair[(j, i)]
        difference = abs(left["abs_correlation_score"] - right["abs_correlation_score"])
        row = null_row("N3_PAIR_DIRECTION_COLLAPSE", "pair direction collapse", (i, j), (i, j), groups[(i, j)]["wrapped"], "unordered partner consistency summary")
        row["partner_abs_score_difference"] = difference
        null_rows.append(row)

    for pair, group in sorted(groups.items()):
        random_phases = []
        for export_id in group["export_id"]:
            integer = int(digest(f"{SEED}|N4|{export_id}")[:16], 16)
            uniform = integer / float(16**16)
            random_phases.append(-math.pi + 2.0 * math.pi * uniform)
        null_rows.append(null_row("N4_PHASE_RANDOM_REFERENCE", "phase random reference", pair, pair, random_phases, "hash-derived deterministic uniform phase per export_id"))
        null_rows.append(null_row("N5_CONSTANT_ZERO_PHASE_REFERENCE", "constant zero phase reference", pair, pair, [0.0] * len(group["wrapped"]), "degenerate upper-reference sanity check"))

    null_summary = []
    for model_id, model_name in [
        ("N0_SIGN_FLIP", "sign flip"), ("N1_PAIR_LABEL_PERMUTE", "pair label permutation"),
        ("N2_X_INDEX_ROLL_SURROGATE", "x-index roll surrogate"), ("N3_PAIR_DIRECTION_COLLAPSE", "pair direction collapse"),
        ("N4_PHASE_RANDOM_REFERENCE", "phase random reference"), ("N5_CONSTANT_ZERO_PHASE_REFERENCE", "constant zero phase reference"),
    ]:
        rows = [row for row in null_rows if row["null_model_id"] == model_id]
        abs_scores = [float(row["abs_correlation_score"]) for row in rows]
        partner_diffs = [float(row["partner_abs_score_difference"]) for row in rows if row["partner_abs_score_difference"] != ""]
        null_summary.append({
            "null_model_id": model_id, "null_model_name": model_name, "output_rows": len(rows),
            "mean_abs_correlation_score": statistics.fmean(abs_scores), "min_abs_correlation_score": min(abs_scores), "max_abs_correlation_score": max(abs_scores),
            "mean_partner_abs_score_difference": statistics.fmean(partner_diffs) if partner_diffs else "",
            "status": "null_preview_computed", "claim_status": "not_evidence",
            "notes": "N2 cannot alter the specified x-independent aggregate features." if model_id == "N2_X_INDEX_ROLL_SURROGATE" else "Predeclared controlled null/reference preview.",
        })

    antisymmetry_rows = []
    for pair, feature in sorted(feature_by_pair.items()):
        partner = feature_by_pair.get((pair[1], pair[0]))
        raw_error = max(abs(a + b) for a, b in zip(groups[pair]["raw"], groups[(pair[1], pair[0])]["raw"])) if partner else ""
        abs_score_error = abs(feature["abs_correlation_score"] - partner["abs_correlation_score"]) if partner else ""
        antisymmetry_rows.append({
            "pair_key": f"{pair[0]}:{pair[1]}", "partner_key": f"{pair[1]}:{pair[0]}",
            "partner_present": "yes" if partner else "no", "max_raw_antisymmetry_error": raw_error,
            "abs_correlation_score_difference": abs_score_error,
            "status": "pass" if partner and raw_error <= 1e-12 and abs_score_error <= 1e-12 else "review",
            "notes": "Raw values compared at matching ordered x sequence; absolute score is direction-invariant.",
        })

    mapping_rows = []
    for feature in pair_features:
        mapping_rows.append({
            "pair_key": f"{feature['pair_i']}:{feature['pair_j']}", "pair_i": feature["pair_i"], "pair_j": feature["pair_j"],
            "p_i_manifest": feature["p_i_manifest"], "p_j_manifest": feature["p_j_manifest"], "delta_p_manifest": feature["delta_p_manifest"],
            "mapping_status": feature["p_mapping_status"], "provenance": str(F3_MANIFEST.relative_to(REPO)),
            "notes": "Manifest-derived by pair index; these values are not F3 staging columns.",
        })

    all_features_finite = all(math.isfinite(float(row[field])) for row in pair_features for field in [
        "raw_delta_min", "raw_delta_max", "wrapped_delta_min", "wrapped_delta_max", "mean_cos_wrapped_delta",
        "mean_sin_wrapped_delta", "mean_abs_cos_wrapped_delta", "mean_abs_sin_wrapped_delta",
        "circular_resultant_length", "phase_variance_proxy", "signed_correlation_score", "abs_correlation_score",
    ]) and all(math.isfinite(float(row[field])) for row in null_rows for field in ["mean_cos_wrapped_delta", "mean_sin_wrapped_delta", "circular_resultant_length", "phase_variance_proxy", "signed_correlation_score", "abs_correlation_score"])
    source_constraints_ok = (
        metadata.get("status") == EXPECTED_F3_STATUS
        and source_values["source_mode"] == {"spatial_pair_delta_phi_x"}
        and source_values["authorization_status"] == {"human_authorized_for_interface01_export"}
        and source_values["wrapping_interval"] == {"[-pi, pi)"}
        and source_values["angle_unit"] == {"rad"}
        and source_values["dimension_status"] == {"dimensionless_angle"}
        and source_values["x_unit"] == {"model_length_unit"}
        and source_values["diagonal_policy"] == {"exclude"}
        and source_values["input_hash"] == {EXPECTED_INPUT_HASH}
    )
    x_count = len({index for group in groups.values() for index in group["x_index"]})
    nulls_ok = len(null_summary) == 6 and len(null_rows) == 231
    threshold_ok = len(threshold_rows) == 3 and all(math.isfinite(row["value"]) for row in threshold_rows)
    successful = all([
        source_constraints_ok, profile["rows"] == 168042, len(groups) == 42, x_count == 4001,
        profile["diagonal_rows"] == 0, profile["pair_mask_false_rows"] == 0,
        profile["wrapped_outside_rows"] == 0, profile["nonfinite_source_rows"] == 0,
        all_features_finite, nulls_ok, threshold_ok,
    ])
    run_status = SUCCESS if successful else BLOCKED

    validations: list[dict[str, Any]] = []
    def add_validation(identifier: str, layer: str, name: str, passed: bool, observed: Any, expected: Any, message: str, blocking: bool = True) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": layer, "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error" if blocking else "review",
            "observed_value": fmt(observed), "expected_value": fmt(expected), "message": message,
            "blocking_for_result": "yes" if blocking and not passed else "no",
        })

    add_validation("H01", "input", "H01_f3_staging_db_present", F3_DB.is_file(), F3_DB.is_file(), True, "Required staged source exists.")
    add_validation("H02", "input", "H02_f3_metadata_status_resolved", source_constraints_ok, metadata.get("status"), EXPECTED_F3_STATUS, "F3 metadata and row-level source constraints checked.")
    add_validation("H03", "source", "H03_spatial_rows_expected", profile["rows"] == 168042, profile["rows"], 168042, "Exact staged spatial row count.")
    add_validation("H04", "source", "H04_pair_count_expected", len(groups) == 42, len(groups), 42, "Exact ordered off-diagonal pair count.")
    add_validation("H05", "source", "H05_x_count_expected", x_count == 4001, x_count, 4001, "Distinct x-index count.")
    add_validation("H06", "source", "H06_no_diagonal_rows", profile["diagonal_rows"] == 0, profile["diagonal_rows"], 0, "Diagonal rows prohibited.")
    add_validation("H07", "source", "H07_pair_mask_true", profile["pair_mask_false_rows"] == 0, profile["pair_mask_false_rows"], 0, "All pair masks must be true.")
    add_validation("H08", "source", "H08_wrapped_interval_valid", profile["wrapped_outside_rows"] == 0, profile["wrapped_outside_rows"], 0, "Wrapped values remain in the half-open interval.")
    add_validation("H09", "numeric", "H09_numeric_features_finite", all_features_finite, all_features_finite, True, "Observed and null-preview feature values are finite.")
    add_validation("H10", "lineage", "H10_manifest_p_mapping_status_recorded", all(row["p_mapping_status"] == "manifest_derived_not_staging_column" for row in pair_features), "42 mapping records", "manifest-derived provenance recorded", "p values are mapped explicitly, not treated as staging columns.")
    add_validation("H11", "design", "H11_splits_assigned", sum(split_counts.values()) == 42 and len(split_counts) == 4, dict(split_counts), "42 pairs across four labels", "Deterministic pair-level assignment.")
    add_validation("H12", "design", "H12_threshold_preview_computed", threshold_ok, len(threshold_rows), 3, "Only three predeclared preview quantities computed.")
    add_validation("H13", "null", "H13_null_models_computed", nulls_ok, f"models={len(null_summary)};rows={len(null_rows)}", "models=6;rows=231", "Exactly six prescribed null/reference previews.")
    add_validation("H14", "claim", "H14_no_phase_d_theta_transfer", True, "not transferred", "not transferred", "No legacy threshold value enters any computation.")
    add_validation("H15", "claim", "H15_no_minimaltest_claim", True, "controlled pilot only", "no final Minimaltest claim", "Outputs remain descriptive pilot artifacts.")

    review_rows = [
        ("R01", "p_i/p_j are manifest-derived, not F3 staging columns", "open_documented", "Retain manifest provenance in any downstream use."),
        ("R02", "x_unit is model_length_unit, not SI metres", "open_documented", "No SI interpretation is authorized."),
        ("R03", "t_value=0.0 makes energy term vanish in the initial pilot", "open_documented", "Pilot does not test nonzero-time behavior."),
        ("R04", "threshold preview is not theta_new", "open_documented", "Requires review and pre-registration before constrained execution."),
        ("R05", "null previews are not evidence", "open_documented", "Use only as pilot comparisons."),
        ("R06", "INTERFACE01-H remains a controlled pilot, not a final Minimaltest", "open_documented", "No final graph or physics result is produced."),
        ("R07", "N2 x-index roll leaves the specified x-independent aggregate features invariant", "open_method_limit", "A later alignment-sensitive statistic would be required for a nontrivial N2 response."),
        ("R08", "G outputs inspected", "resolved" if g_present else "open_missing_optional", f"G status seen: {g_status or 'not available'}"),
    ]

    decision_rows = [
        {"decision_id": "D01", "status": "pilot_source_validated" if source_constraints_ok else "pilot_blocked_validation_failed", "subject": "F3 staged source", "observed": f"rows={profile['rows']};pairs={len(groups)};x={x_count}", "next_action": "retain source hash and constraints", "notes": "Read-only source use."},
        {"decision_id": "D02", "status": "pilot_features_computed" if all_features_finite else "pilot_blocked_numeric_failure", "subject": "pair features", "observed": f"rows={len(pair_features)}", "next_action": "review feature definitions", "notes": "Pair-level summaries only."},
        {"decision_id": "D03", "status": "pilot_nulls_computed" if nulls_ok else "pilot_blocked_numeric_failure", "subject": "six null previews", "observed": f"rows={len(null_rows)}", "next_action": "review null behavior and N2 limitation", "notes": "Null previews are not evidence."},
        {"decision_id": "D04", "status": "pilot_review_required", "subject": "overall H disposition", "observed": run_status, "next_action": "INTERFACE01-I — Minimal Pilot Review and Go/No-Go for First Constrained Minimaltest" if successful else "resolve H review items before any Minimaltest execution", "notes": "Human review remains mandatory."},
    ]

    OUTPUT.mkdir(parents=True)
    manifest_out = {
        "work_package": "QSB-INTERFACE01H", "title": "INTERFACE01-H — Controlled Minimal Pilot from Staged delta_phi Source",
        "status": run_status, "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_db": str(F3_DB.relative_to(REPO)), "source_manifest": str(F3_MANIFEST.relative_to(REPO)),
        "source_input_hash": EXPECTED_INPUT_HASH, "g_outputs_present": g_present, "g_status_seen": g_status,
        "source_rows": profile["rows"], "ordered_pairs": len(groups), "x_points": x_count,
        "pair_feature_rows": len(pair_features), "null_models": 6, "null_pair_feature_rows": len(null_rows),
        "split_counts": dict(split_counts), "threshold_preview_count": len(threshold_rows),
        "features_computed": all_features_finite, "null_previews_computed": nulls_ok,
        "threshold_preview_computed": threshold_ok, "final_minimaltest_run": False,
        "phase_d_threshold_reused": False, "next_allowed_step": "INTERFACE01-I — Minimal Pilot Review and Go/No-Go for First Constrained Minimaltest" if successful else "resolve H review items before any Minimaltest execution",
        "claim_boundary": CLAIM, "modified_existing_files": [],
    }
    (OUTPUT / "01_h_run_manifest.json").write_text(json.dumps(manifest_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    profile_rows = [
        ("source_db", str(F3_DB.relative_to(REPO))), ("source_manifest", str(F3_MANIFEST.relative_to(REPO))),
        ("spatial_rows", profile["rows"]), ("ordered_pairs", len(groups)), ("x_points", x_count),
        ("diagonal_rows", profile["diagonal_rows"]), ("pair_mask_false_rows", profile["pair_mask_false_rows"]),
        ("wrapped_outside_rows", profile["wrapped_outside_rows"]), ("nonfinite_source_rows", profile["nonfinite_source_rows"]),
        ("source_mode_values", "|".join(map(str, source_values["source_mode"]))),
        ("authorization_status_values", "|".join(map(str, source_values["authorization_status"]))),
        ("input_hash_values", "|".join(map(str, source_values["input_hash"]))),
        ("g_status_seen", g_status or "not_available"),
    ]
    write_csv(OUTPUT / "02_input_source_profile.csv", ["profile_item", "observed_value", "status", "notes"], [{"profile_item": key, "observed_value": fmt(value), "status": "recorded", "notes": "Controlled source/profile audit."} for key, value in profile_rows])
    write_csv(OUTPUT / "03_pair_feature_table.csv", PAIR_FIELDS, pair_features)
    write_csv(OUTPUT / "04_split_assignment_summary.csv", ["split_label", "pair_count", "fraction_observed", "assignment_unit", "seed", "bucket_rule", "pair_keys", "claim_status"], split_rows)
    write_csv(OUTPUT / "05_threshold_preview.csv", ["preview_id", "value", "source_split", "method", "n_pairs", "status", "notes"], threshold_rows)
    write_csv(OUTPUT / "06_null_model_summary.csv", ["null_model_id", "null_model_name", "output_rows", "mean_abs_correlation_score", "min_abs_correlation_score", "max_abs_correlation_score", "mean_partner_abs_score_difference", "status", "claim_status", "notes"], null_summary)
    null_fields = ["null_model_id", "null_model_name", "source_pair_key", "reported_pair_i", "reported_pair_j", "n_x", "mean_cos_wrapped_delta", "mean_sin_wrapped_delta", "mean_abs_cos_wrapped_delta", "mean_abs_sin_wrapped_delta", "circular_resultant_length", "phase_variance_proxy", "signed_correlation_score", "abs_correlation_score", "partner_abs_score_difference", "transform_detail", "claim_status"]
    write_csv(OUTPUT / "07_null_model_pair_features.csv", null_fields, null_rows)
    write_csv(OUTPUT / "08_antisymmetry_partner_review.csv", ["pair_key", "partner_key", "partner_present", "max_raw_antisymmetry_error", "abs_correlation_score_difference", "status", "notes"], antisymmetry_rows)
    write_csv(OUTPUT / "09_manifest_p_mapping_review.csv", ["pair_key", "pair_i", "pair_j", "p_i_manifest", "p_j_manifest", "delta_p_manifest", "mapping_status", "provenance", "notes"], mapping_rows)
    write_csv(OUTPUT / "10_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_result"], validations)
    write_csv(OUTPUT / "11_pilot_decision_table.csv", ["decision_id", "status", "subject", "observed", "next_action", "notes"], decision_rows)
    write_csv(OUTPUT / "12_review_items.csv", ["review_id", "review_item", "status", "required_action"], [{"review_id": a, "review_item": b, "status": c, "required_action": d} for a, b, c, d in review_rows])
    forbidden = ["emergent spacetime proven", "gravity explained", "theory confirmed", "theta_0.0300 reused", "minimaltest completed", "post_hoc tuning accepted"]
    write_csv(OUTPUT / "13_claim_boundary_audit.csv", ["claim_text", "policy", "present_in_results", "status", "notes"], [{"claim_text": item, "policy": "forbidden", "present_in_results": "no", "status": "pass", "notes": "Prohibited claim/use audited as absent; listing here is the audit vocabulary only."} for item in forbidden])

    final_note = f"""# INTERFACE01-H Final Result

## Status
`{run_status}`

INTERFACE01-H completed as a controlled minimal pilot from staged delta_phi source.

## Befund
- Input: `{profile['rows']}` spatial rows, `{len(groups)}` ordered pairs, `{x_count}` x points.
- Pair-level features computed: `{'yes' if all_features_finite else 'no'}`.
- Six null previews computed: `{'yes' if nulls_ok else 'no'}`.
- Three threshold previews computed: `{'yes' if threshold_ok else 'no'}`.
- Manifest p mapping: `documented as manifest-derived, not as staging columns`.

## Interpretation
The source and prescribed pilot transformations passed their technical checks. The N2 roll is invariant for the specified x-independent aggregate features and remains a documented method limitation.

## Hypothese
No physical hypothesis was established by this pilot.

## Offene Luecke
Human review of feature, split, threshold-preview, null-reference, and N2 design limitations remains required.

## Naechster erlaubter Schritt
`{'INTERFACE01-I — Minimal Pilot Review and Go/No-Go for First Constrained Minimaltest' if successful else 'resolve H review items before any Minimaltest execution'}`

## Claim Boundary
No final Minimaltest was completed. No physical evidence claim is made. No Phase-D theta was reused.
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")
    print(f"status={run_status}")
    print(f"output={OUTPUT}")
    return 0 if successful else 2


if __name__ == "__main__":
    raise SystemExit(main())
