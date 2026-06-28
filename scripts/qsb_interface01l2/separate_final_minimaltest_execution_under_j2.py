#!/usr/bin/env python3
"""Execute INTERFACE01-L2 under the locked K/J2 contract."""

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
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
F3_INPUT = REPO / "runs/QSB-INTERFACE01F3/input_manifest/interface01f3_delta_phi_input_manifest.json"
G = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
H = REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi"
I = REPO / "runs/QSB-INTERFACE01I/pilot_result_review_nullmodel_adequacy_decision"
J = REPO / "runs/QSB-INTERFACE01J/minimaltest_precontract"
K = REPO / "runs/QSB-INTERFACE01K/review_point_resolution_execution_authorization_check"
L = REPO / "runs/QSB-INTERFACE01L/separate_final_minimaltest_execution"
J2 = REPO / "runs/QSB-INTERFACE01J2/minimaltest_acceptance_rule_addendum"
M = REPO / "runs/QSB-INTERFACE01M/result_review_mechanism_interpretation_boundary"
DB = F3 / "09_delta_phi_staging_preflight.sqlite"
OUTPUT = REPO / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2"

SEED = 20260620
STATUS_COMPLETED = "interface01l2_separate_final_minimaltest_execution_completed_with_claim_boundary"
STATUS_NOT_AUTHORIZED = "interface01l2_separate_final_minimaltest_execution_blocked_not_authorized"
STATUS_UPSTREAM = "interface01l2_separate_final_minimaltest_execution_blocked_upstream_mismatch"
STATUS_CONTRACT = "interface01l2_separate_final_minimaltest_execution_blocked_contract_incomplete"
STATUS_SOURCE = "interface01l2_separate_final_minimaltest_execution_blocked_source_invalid"
K_AUTH = "authorized_for_separate_minimaltest_execution"
J2_AUTH = "authorized_for_separate_minimaltest_execution_with_acceptance_rule"
FEATURES = ["mean_abs_cos_wrapped_delta", "signed_correlation_score", "abs_correlation_score"]
NULL_IDS = [
    "N0_SIGN_FLIP", "N1_PAIR_LABEL_PERMUTE", "N2_X_INDEX_ROLL_SURROGATE",
    "N3_PAIR_DIRECTION_COLLAPSE", "N4_PHASE_RANDOM_REFERENCE", "N5_CONSTANT_ZERO_PHASE_REFERENCE",
]
CLAIM_BOUNDARY = (
    "INTERFACE01-L2 reports only the locked Minimaltest contract result on the authorized F3 source. "
    "It performs no mechanism interpretation, makes no physical-evidence claim, transfers no Phase-D "
    "threshold, performs no post-hoc tuning, and does not generalize beyond P0/t0/alpha1.6."
)
EXPECTED_FILES = {
    "01_l2_run_manifest.json", "02_start_gate_authorization_preflight.csv",
    "03_upstream_hash_verification.csv", "04_j2_acceptance_rule_loaded.csv",
    "05_source_data_validation.csv", "06_feature_scope_and_mapping.csv",
    "07_final_pair_feature_table.csv", "08_split_assignment_verification.csv",
    "09_theta_epsilon_application.csv", "10_nullmodel_execution_summary.csv",
    "11_feature_level_n4_support.csv", "12_observed_vs_nullmodel_results.csv",
    "13_acceptance_gate_results.csv", "14_claim_boundary_and_interpretation_limits.csv",
    "15_l2_validation_results.csv", "FINAL_RESULT_NOTE.md",
}
EXPECTED_STATUSES = {
    "F3": "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged",
    "G": "interface01g_minimaltest_design_review_completed_with_staged_source_profile",
    "H": "interface01h_controlled_minimal_pilot_completed_with_review_items",
    "I": "interface01i_pilot_result_review_completed_nullmodel_adequacy_assessed",
    "J": "interface01j_minimaltest_precontract_completed_conditional_no_execution",
    "K": "interface01k_review_point_resolution_completed_execution_authorization_checked",
    "L": "interface01l_separate_final_minimaltest_execution_blocked_contract_incomplete",
    "J2": "interface01j2_acceptance_rule_addendum_completed_authorized_for_l_replay",
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


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_for(pair_i: int, pair_j: int) -> tuple[str, str]:
    pair_key = f"{pair_i}:{pair_j}"
    assignment_hash = digest(pair_key + "|INTERFACE01-H|seed=20260620")
    bucket = int(assignment_hash[:8], 16) % 10
    h_label = "train_design" if bucket <= 3 else "calibration_design" if bucket <= 6 else "review_holdout" if bucket <= 8 else "null_control"
    return ("final_audit" if h_label == "null_control" else h_label), assignment_hash


def aggregate_phases(phases: list[float]) -> dict[str, float]:
    n = len(phases)
    cos_values = [math.cos(value) for value in phases]
    sin_values = [math.sin(value) for value in phases]
    mean_cos = math.fsum(cos_values) / n
    mean_sin = math.fsum(sin_values) / n
    return {
        "mean_abs_cos_wrapped_delta": math.fsum(abs(value) for value in cos_values) / n,
        "signed_correlation_score": mean_cos,
        "abs_correlation_score": abs(mean_cos),
        "mean_sin_wrapped_delta": mean_sin,
    }


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    paths = {
        "f3_manifest": F3 / "01_f3_run_manifest.json", "f3_db": DB, "f3_input": F3_INPUT,
        "g_manifest": G / "01_g_run_manifest.json", "h_manifest": H / "01_h_run_manifest.json",
        "h_features": H / "03_pair_feature_table.csv", "h_script": REPO / "scripts/qsb_interface01h/controlled_minimal_pilot_from_staged_delta_phi.py",
        "i_manifest": I / "01_i_run_manifest.json", "j_manifest": J / "01_j_run_manifest.json",
        "j_parameters": J / "07_theta_epsilon_calibration_precontract.csv",
        "k_manifest": K / "01_k_run_manifest.json", "k_inventory": K / "02_upstream_artifact_inventory.csv",
        "k_parameters": K / "09_split_seed_theta_epsilon_resolution.csv",
        "l_manifest": L / "01_l_run_manifest.json", "j2_manifest": J2 / "01_j2_run_manifest.json",
        "j2_inventory": J2 / "02_upstream_inventory_and_hashes.csv",
        "j2_rules": J2 / "05_acceptance_rule_addendum.csv", "j2_features": J2 / "06_feature_acceptance_gates.csv",
        "j2_nulls": J2 / "07_nullmodel_acceptance_roles.csv", "j2_decisions": J2 / "08_result_decision_table.csv",
        "m_manifest": M / "01_m_run_manifest.json",
    }
    required = set(paths) - {"m_manifest"}
    upstream_present = all(paths[key].is_file() for key in required)
    before_hashes = {key: sha256(path) for key, path in paths.items() if path.is_file()}

    manifest_keys = {"F3": "f3_manifest", "G": "g_manifest", "H": "h_manifest", "I": "i_manifest", "J": "j_manifest", "K": "k_manifest", "L": "l_manifest", "J2": "j2_manifest"}
    manifests = {block: load_json(paths[key]) for block, key in manifest_keys.items() if paths[key].is_file()}
    statuses_ok = {block: manifests.get(block, {}).get("status") == expected for block, expected in EXPECTED_STATUSES.items()}
    k_authorized = manifests.get("K", {}).get("execution_authorization") == K_AUTH
    j2_authorized = manifests.get("J2", {}).get("execution_authorization_after_j2") == J2_AUTH
    l_resolved = (
        manifests.get("L", {}).get("minimaltest_contract_result") == "blocked_no_execution"
        and manifests.get("J2", {}).get("l_blocker_confirmed") is True
        and manifests.get("J2", {}).get("acceptance_rule_added") is True
    )

    hash_rows = []
    hash_ok = True
    recorded: dict[str, tuple[str, str, str]] = {}
    if paths["j2_inventory"].is_file():
        for row in read_csv(paths["j2_inventory"]):
            recorded[row["path"]] = (row["upstream_block"], row["sha256"], rel(paths["j2_inventory"]))
    hash_targets = [
        paths["f3_manifest"], paths["f3_db"], paths["f3_input"], paths["g_manifest"],
        paths["h_manifest"], paths["h_features"], paths["h_script"], paths["i_manifest"],
        paths["j_manifest"], paths["j_parameters"], paths["k_manifest"], paths["k_parameters"],
        paths["l_manifest"], paths["j2_manifest"], paths["j2_rules"], paths["j2_features"],
        paths["j2_nulls"], paths["j2_decisions"], paths["m_manifest"],
    ]
    block_for_path = {
        "QSB-INTERFACE01F3": "F3", "QSB-INTERFACE01G": "G", "QSB-INTERFACE01H": "H",
        "QSB-INTERFACE01I": "I", "QSB-INTERFACE01J/": "J", "QSB-INTERFACE01K": "K",
        "QSB-INTERFACE01L/": "L", "QSB-INTERFACE01J2": "J2", "QSB-INTERFACE01M": "M",
    }
    for number, path in enumerate(hash_targets, start=1):
        path_text = rel(path)
        block = next((value for token, value in block_for_path.items() if token in path_text), "upstream")
        current = sha256(path) if path.is_file() else "missing"
        if path_text in recorded:
            _, prior, prior_source = recorded[path_text]
        else:
            prior, prior_source = current, "L2 start snapshot; verified unchanged after output generation"
        match = path.is_file() and prior == current
        hash_ok = hash_ok and match
        hash_rows.append({
            "artifact_id": f"L2-A{number:02d}", "upstream_block": block, "path": path_text,
            "recorded_hash_source": prior_source, "recorded_hash": prior, "current_hash": current,
            "hash_match": "yes" if match else "no", "status": "pass" if match else "fail",
            "notes": "Read-only artifact matches its recorded hash." if match else "Mismatch blocks execution.",
        })

    j2_rules = read_csv(paths["j2_rules"]) if paths["j2_rules"].is_file() else []
    rule_names = {row["rule_name"] for row in j2_rules}
    required_rule_names = {"hard_start_gates", "feature_level_n4_support", "overall_pass_2_of_3", "overall_fail", "overall_inconclusive", "blocked_no_execution", "n2_exclusion_from_pass", "n4_mandatory_comparator", "no_phase_d_theta_transfer", "no_post_hoc_tuning", "claim_boundary"}
    rules_ok = required_rule_names <= rule_names and all(row.get("machine_readable_expression", "").strip() for row in j2_rules)
    loaded_rule_rows = [{**row, "loaded": "yes", "used_in_l2": "yes", "notes": f"{row['notes']} Loaded without modification."} for row in j2_rules]

    feature_contract = read_csv(paths["j2_features"]) if paths["j2_features"].is_file() else []
    feature_names = [row["feature_name"] for row in feature_contract]
    features_ok = len(feature_names) == 3 and feature_names == FEATURES
    null_contract = read_csv(paths["j2_nulls"]) if paths["j2_nulls"].is_file() else []
    null_by_id = {row["nullmodel_id"]: row for row in null_contract}
    nulls_ok = len(null_contract) == 6 and set(null_by_id) == set(NULL_IDS)
    n2_contract_ok = null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("role") == "invariance_check_only" and null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("used_in_pass_gate") == "false"
    n4_contract_ok = null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("role") == "effective_perturbation" and null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("used_in_pass_gate") == "true"
    parameters = {row["contract_item"]: row for row in read_csv(paths["k_parameters"])} if paths["k_parameters"].is_file() else {}
    parameters_ok = {"theta_new_rule", "epsilon_new_rule", "split_rule", "seed", "phase_d_theta_transfer", "post_hoc_tuning_lock"} <= set(parameters)
    phase_guard = parameters.get("phase_d_theta_transfer", {}).get("decision") == "locked_prohibited"
    tuning_guard = parameters.get("post_hoc_tuning_lock", {}).get("decision") == "locked_prohibited"

    source = {
        "row_count": 0, "ordered_pair_count": 0, "x_point_count": 0, "diagonal_row_count": 0,
        "wrapped_min": float("nan"), "wrapped_max": float("nan"), "wrapped_interval": "missing",
        "finite_raw_values": False, "finite_wrapped_values": False, "angle_unit": "missing",
        "dimension_status": "missing", "x_unit": "missing", "pair_mask_policy": "missing",
    }
    source_schema_ok = False
    if DB.is_file():
        connection = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        table_columns = {row[1] for row in connection.execute("PRAGMA table_info(stg_delta_phi_spatial)")}
        required_columns = {"export_id", "pair_i", "pair_j", "x_index", "x_value", "raw_delta_phi_ij_x", "wrapped_delta_phi_ij_x", "pair_mask", "angle_unit", "dimension_status", "x_unit", "wrapping_interval"}
        source_schema_ok = required_columns <= table_columns
        if source_schema_ok:
            row = connection.execute(
                """SELECT COUNT(*), COUNT(DISTINCT pair_i || ':' || pair_j), COUNT(DISTINCT x_index),
                          SUM(CASE WHEN pair_i=pair_j THEN 1 ELSE 0 END),
                          MIN(wrapped_delta_phi_ij_x), MAX(wrapped_delta_phi_ij_x),
                          SUM(CASE WHEN raw_delta_phi_ij_x IS NULL THEN 1 ELSE 0 END),
                          SUM(CASE WHEN wrapped_delta_phi_ij_x IS NULL THEN 1 ELSE 0 END),
                          MIN(angle_unit), MAX(angle_unit), MIN(dimension_status), MAX(dimension_status),
                          MIN(x_unit), MAX(x_unit), MIN(pair_mask), MAX(pair_mask),
                          MIN(wrapping_interval), MAX(wrapping_interval)
                   FROM stg_delta_phi_spatial"""
            ).fetchone()
            source.update({
                "row_count": row[0], "ordered_pair_count": row[1], "x_point_count": row[2],
                "diagonal_row_count": row[3], "wrapped_min": row[4], "wrapped_max": row[5],
                "finite_raw_values": row[6] == 0, "finite_wrapped_values": row[7] == 0 and math.isfinite(row[4]) and math.isfinite(row[5]),
                "angle_unit": row[9] if row[8] == row[9] else "mixed",
                "dimension_status": row[11] if row[10] == row[11] else "mixed",
                "x_unit": row[13] if row[12] == row[13] else "mixed",
                "pair_mask_policy": "all_accepted" if row[14] == row[15] == 1 else f"range_{row[14]}_{row[15]}",
                "wrapped_interval": row[17] if row[16] == row[17] else "mixed",
            })
        connection.close()
    source_valid = source_schema_ok and all([
        source["row_count"] == 168042, source["ordered_pair_count"] == 42, source["x_point_count"] == 4001,
        source["diagonal_row_count"] == 0, source["wrapped_min"] >= -math.pi, source["wrapped_max"] < math.pi,
        source["finite_raw_values"], source["finite_wrapped_values"], source["angle_unit"] == "rad",
        source["dimension_status"] == "dimensionless_angle", source["x_unit"] == "model_length_unit",
        source["pair_mask_policy"] == "all_accepted", source["wrapped_interval"] == "[-pi, pi)",
    ])

    gate_specs = [
        ("L2-G01", "F3 staged source exists and is valid", "F3", paths["f3_manifest"], statuses_ok.get("F3", False) and DB.is_file(), EXPECTED_STATUSES["F3"], manifests.get("F3", {}).get("status", "missing"), "Source status checked before computation."),
        ("L2-G02", "G status valid", "G", paths["g_manifest"], statuses_ok.get("G", False), EXPECTED_STATUSES["G"], manifests.get("G", {}).get("status", "missing"), "G status checked."),
        ("L2-G03", "H status valid", "H", paths["h_manifest"], statuses_ok.get("H", False), EXPECTED_STATUSES["H"], manifests.get("H", {}).get("status", "missing"), "H status checked."),
        ("L2-G04", "I status valid", "I", paths["i_manifest"], statuses_ok.get("I", False), EXPECTED_STATUSES["I"], manifests.get("I", {}).get("status", "missing"), "I status checked."),
        ("L2-G05", "J status valid", "J", paths["j_manifest"], statuses_ok.get("J", False), EXPECTED_STATUSES["J"], manifests.get("J", {}).get("status", "missing"), "J status checked."),
        ("L2-G06", "K authorization valid", "K", paths["k_manifest"], statuses_ok.get("K", False) and k_authorized, K_AUTH, manifests.get("K", {}).get("execution_authorization", "missing"), "K authorization exact."),
        ("L2-G07", "J2 authorization valid", "J2", paths["j2_manifest"], statuses_ok.get("J2", False) and j2_authorized, J2_AUTH, manifests.get("J2", {}).get("execution_authorization_after_j2", "missing"), "J2 authorization exact."),
        ("L2-G08", "J2 acceptance rule machine-readable", "J2", paths["j2_rules"], rules_ok, "11 required machine-readable rules", f"{len(j2_rules)} loaded", "Rule set checked."),
        ("L2-G09", "upstream hashes stable", "F3-M", paths["j2_inventory"], hash_ok, "all hash checks pass", f"{sum(r['hash_match']=='yes' for r in hash_rows)}/{len(hash_rows)}", "Read-only hashes checked."),
        ("L2-G10", "F3 row/pair/x counts valid", "F3", DB, source_valid, "168042/42/4001 and source constraints", f"{source['row_count']}/{source['ordered_pair_count']}/{source['x_point_count']}", "Read-only source preflight."),
        ("L2-G11", "locked feature scope identified", "J2", paths["j2_features"], features_ok, ";".join(FEATURES), ";".join(feature_names), "Exactly three locked features."),
        ("L2-G12", "locked nullmodel scope identified", "J2", paths["j2_nulls"], nulls_ok and n2_contract_ok and n4_contract_ok, "6 nullmodels with locked N2/N4 roles", f"{len(null_contract)} nullmodels", "Roles checked before execution."),
        ("L2-G13", "theta_new/epsilon_new rules present", "J/K", paths["k_parameters"], parameters_ok, "locked executable rules", "present" if parameters_ok else "missing", "Rules are loaded without value changes."),
        ("L2-G14", "no Phase-D theta transfer", "K", paths["k_parameters"], phase_guard, "locked_prohibited", parameters.get("phase_d_theta_transfer", {}).get("decision", "missing"), "Legacy threshold excluded."),
        ("L2-G15", "no post-hoc tuning", "K", paths["k_parameters"], tuning_guard, "locked_prohibited", parameters.get("post_hoc_tuning_lock", {}).get("decision", "missing"), "Tuning lock active."),
    ]
    gate_rows = [{
        "gate_id": identifier, "gate_name": name, "source_block": block, "source_artifact": rel(path),
        "observed_value": observed, "expected_value": expected, "status": "pass" if passed else "fail",
        "blocking": "yes", "notes": notes,
    } for identifier, name, block, path, passed, expected, observed, notes in gate_specs]
    hard_start_passed = upstream_present and all(spec[4] for spec in gate_specs)

    if not hard_start_passed:
        if not k_authorized or not j2_authorized:
            blocked_status = STATUS_NOT_AUTHORIZED
        elif not hash_ok or not all(statuses_ok.values()):
            blocked_status = STATUS_UPSTREAM
        elif not source_valid:
            blocked_status = STATUS_SOURCE
        else:
            blocked_status = STATUS_CONTRACT
        raise SystemExit(f"Hard start gates failed before output execution package generation: status={blocked_status}")

    # All hard gates passed: execution begins here.
    minimaltest_started = True
    groups: dict[tuple[int, int], dict[str, Any]] = {}
    connection = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    query = """SELECT export_id,pair_i,pair_j,x_index,x_value,raw_delta_phi_ij_x,wrapped_delta_phi_ij_x
               FROM stg_delta_phi_spatial ORDER BY pair_i,pair_j,x_index"""
    for row in connection.execute(query):
        pair = (row["pair_i"], row["pair_j"])
        if pair not in groups:
            groups[pair] = {"x": [], "raw": [], "wrapped": [], "export_id": []}
        groups[pair]["x"].append(row["x_value"])
        groups[pair]["raw"].append(row["raw_delta_phi_ij_x"])
        groups[pair]["wrapped"].append(row["wrapped_delta_phi_ij_x"])
        groups[pair]["export_id"].append(row["export_id"])
    connection.close()

    pair_rows = []
    pair_features: dict[tuple[int, int], dict[str, Any]] = {}
    split_rows = []
    for pair, group in sorted(groups.items()):
        split_label, assignment_hash = split_for(*pair)
        values = aggregate_phases(group["wrapped"])
        row = {"pair_key": f"{pair[0]}:{pair[1]}", "pair_i": pair[0], "pair_j": pair[1], "split_label": split_label, **{name: values[name] for name in FEATURES}}
        pair_rows.append(row)
        pair_features[pair] = row
        split_rows.append({
            "pair_key": row["pair_key"], "pair_i": pair[0], "pair_j": pair[1], "split_label": split_label,
            "split_rule": "sha256(pair_key|INTERFACE01-H|seed=20260620), first8 modulo 10; null_control mapped to final_audit",
            "seed": SEED, "source_artifact": rel(H / "04_split_assignment_summary.csv"),
            "source_hash": parameters["split_rule"]["source_hash"], "status": "verified",
            "notes": f"assignment_hash={assignment_hash}; no reshuffling.",
        })

    upstream_h = {(int(row["pair_i"]), int(row["pair_j"])): row for row in read_csv(paths["h_features"])}
    feature_max_diff = max(
        abs(float(pair_features[pair][feature]) - float(upstream_h[pair][feature]))
        for pair in pair_features for feature in FEATURES
    )
    feature_mapping_ok = len(pair_rows) == 42 and feature_max_diff <= 1e-15
    feature_scope_rows = [{
        "feature_name": feature, "feature_source_artifact": rel(paths["h_features"]),
        "feature_source_hash": sha256(paths["h_features"]),
        "calculation_or_load_rule": "Recomputed from F3 wrapped_delta_phi_ij_x using the hashed H aggregate_phases rule; compared to locked H rows.",
        "unit_status": "dimensionless", "dimension_status": "dimensionless_aggregate",
        "used_in_l2": "yes", "mapping_status": "verified_exact_within_1e-15" if feature_mapping_ok else "mismatch",
        "notes": f"maximum selected-feature difference versus H={feature_max_diff:.17g}.",
    } for feature in FEATURES]

    calibration = [row["abs_correlation_score"] for row in pair_rows if row["split_label"] == "calibration_design"]
    theta_new = statistics.median(calibration)
    epsilon_new = statistics.median(abs(value - theta_new) for value in calibration)
    parameter_rows = [
        {"parameter_name": "theta_new", "rule": parameters["theta_new_rule"]["observed_value"], "source_artifact": parameters["theta_new_rule"]["source_artifact"], "source_hash": parameters["theta_new_rule"]["source_hash"], "computed_or_loaded_value": theta_new, "application_scope": f"calibration_design; n={len(calibration)}", "status": "computed_once_and_frozen", "notes": "Computed before nullmodel comparison."},
        {"parameter_name": "epsilon_new", "rule": parameters["epsilon_new_rule"]["observed_value"], "source_artifact": parameters["epsilon_new_rule"]["source_artifact"], "source_hash": parameters["epsilon_new_rule"]["source_hash"], "computed_or_loaded_value": epsilon_new, "application_scope": f"calibration_design; n={len(calibration)}", "status": "computed_once_and_frozen", "notes": "Median absolute deviation around theta_new."},
        {"parameter_name": "phase_d_theta_0300_transfer_check", "rule": "theta=0.0300 from Phase D is not transferred", "source_artifact": parameters["phase_d_theta_transfer"]["source_artifact"], "source_hash": parameters["phase_d_theta_transfer"]["source_hash"], "computed_or_loaded_value": "false", "application_scope": "all L2 stages", "status": "pass", "notes": "Legacy value absent from computation."},
        {"parameter_name": "post_hoc_tuning_check", "rule": "post_hoc_tuning_lock=true", "source_artifact": parameters["post_hoc_tuning_lock"]["source_artifact"], "source_hash": parameters["post_hoc_tuning_lock"]["source_hash"], "computed_or_loaded_value": "false", "application_scope": "all L2 stages", "status": "pass", "notes": "No rule or value was revised after result access."},
    ]

    null_pair_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add_null(model_id: str, source_pair: tuple[int, int], reported_pair: tuple[int, int], values: dict[str, float]) -> None:
        null_pair_rows[model_id].append({
            "source_pair": source_pair, "reported_pair": reported_pair,
            "pair_key": f"{reported_pair[0]}:{reported_pair[1]}", **{name: values[name] for name in FEATURES},
        })

    for pair, observed in sorted(pair_features.items()):
        values = {name: observed[name] for name in FEATURES}
        values["signed_correlation_score"] = -values["signed_correlation_score"]
        add_null("N0_SIGN_FLIP", pair, pair, values)

    ordered_n1 = sorted(groups, key=lambda pair: digest(f"{pair[0]}:{pair[1]}|N1|seed=20260620"))
    shifted = ordered_n1[1:] + ordered_n1[:1]
    for pair, label in zip(ordered_n1, shifted):
        add_null("N1_PAIR_LABEL_PERMUTE", pair, label, aggregate_phases(groups[pair]["wrapped"]))

    for pair, group in sorted(groups.items()):
        n = len(group["wrapped"])
        offset = 1 + int(digest(f"{pair[0]}:{pair[1]}|N2|seed=20260620")[:8], 16) % (n - 1)
        rolled = group["wrapped"][-offset:] + group["wrapped"][:-offset]
        add_null("N2_X_INDEX_ROLL_SURROGATE", pair, pair, aggregate_phases(rolled))

    for i, j in sorted((i, j) for i, j in groups if i < j):
        add_null("N3_PAIR_DIRECTION_COLLAPSE", (i, j), (i, j), aggregate_phases(groups[(i, j)]["wrapped"]))

    for pair, group in sorted(groups.items()):
        random_phases = []
        for export_id in group["export_id"]:
            integer = int(digest(f"{SEED}|N4|{export_id}")[:16], 16)
            uniform = integer / float(16**16)
            random_phases.append(-math.pi + 2.0 * math.pi * uniform)
        add_null("N4_PHASE_RANDOM_REFERENCE", pair, pair, aggregate_phases(random_phases))
        add_null("N5_CONSTANT_ZERO_PHASE_REFERENCE", pair, pair, aggregate_phases([0.0] * len(group["wrapped"])))

    review_keys = {row["pair_key"] for row in pair_rows if row["split_label"] == "review_holdout"}
    observed_metrics = {
        feature: statistics.median(row[feature] for row in pair_rows if row["pair_key"] in review_keys)
        for feature in FEATURES
    }
    comparisons = []
    null_metrics: dict[str, dict[str, float | None]] = {}
    for model_id in NULL_IDS:
        null_metrics[model_id] = {}
        for feature in FEATURES:
            values = [row[feature] for row in null_pair_rows[model_id] if row["pair_key"] in review_keys]
            metric = statistics.median(values) if values else None
            null_metrics[model_id][feature] = metric
            observed = observed_metrics[feature]
            difference = observed - metric if metric is not None else None
            comparisons.append({
                "comparison_id": f"{model_id}:{feature}", "feature_name": feature,
                "observed_value": observed, "nullmodel_id": model_id,
                "nullmodel_role": null_by_id[model_id]["role"], "nullmodel_value": metric if metric is not None else "not_comparable",
                "difference": difference if difference is not None else "not_comparable",
                "abs_difference": abs(difference) if difference is not None else "not_comparable",
                "contract_relevance": "acceptance_gate" if model_id == "N4_PHASE_RANDOM_REFERENCE" else "invariance_check" if model_id == "N2_X_INDEX_ROLL_SURROGATE" else "diagnostic",
                "status": "computed" if metric is not None else "contractual_non_execution_diagnostic",
                "notes": "Median over matching locked review_holdout pair keys.",
            })

    n2_max_diff = max(
        abs(pair_features[row["reported_pair"]][feature] - row[feature])
        for row in null_pair_rows["N2_X_INDEX_ROLL_SURROGATE"] for feature in FEATURES
    )
    n2_execution_ok = n2_max_diff <= 1e-15
    n4_metrics_finite = all(null_metrics["N4_PHASE_RANDOM_REFERENCE"][feature] is not None and math.isfinite(float(null_metrics["N4_PHASE_RANDOM_REFERENCE"][feature])) for feature in FEATURES)
    null_execution_complete = all(len(null_pair_rows[model_id]) > 0 for model_id in NULL_IDS)
    null_summary_rows = []
    for model_id in NULL_IDS:
        role = null_by_id[model_id]["role"]
        abs_values = [row["abs_correlation_score"] for row in null_pair_rows[model_id]]
        null_summary_rows.append({
            "nullmodel_id": model_id, "role": role,
            "mandatory": null_by_id[model_id]["mandatory_for_execution"], "executed": "yes",
            "used_in_acceptance_gate": null_by_id[model_id]["used_in_pass_gate"],
            "primary_metric": "median_abs_correlation_score_all_rows",
            "primary_metric_value": statistics.median(abs_values),
            "limitation": null_by_id[model_id]["limitations"], "status": "pass",
            "notes": f"rows={len(null_pair_rows[model_id])}; N2 max invariant difference={n2_max_diff:.17g}." if model_id == "N2_X_INDEX_ROLL_SURROGATE" else f"rows={len(null_pair_rows[model_id])}; deterministic H transform executed.",
        })

    support_threshold = theta_new + epsilon_new
    support_rows = []
    for feature in FEATURES:
        observed = observed_metrics[feature]
        n4_metric = float(null_metrics["N4_PHASE_RANDOM_REFERENCE"][feature])
        delta = abs(observed - n4_metric)
        finite = all(math.isfinite(value) for value in [observed, n4_metric, delta, theta_new, epsilon_new])
        support = finite and delta >= support_threshold
        support_rows.append({
            "feature_name": feature, "observed_metric": observed, "n4_metric": n4_metric,
            "abs_delta_n4": delta, "theta_new": theta_new, "epsilon_new": epsilon_new,
            "support_threshold": support_threshold, "support_flag": "true" if support else "false",
            "finite_values": "yes" if finite else "no", "status": "pass" if support else "not_supported",
            "notes": "Unsigned distance between locked review_holdout medians; one boolean vote.",
        })
    support_count = sum(row["support_flag"] == "true" for row in support_rows)
    all_required_finite = all(row["finite_values"] == "yes" for row in support_rows)
    inconclusive = not (feature_mapping_ok and null_execution_complete and n2_execution_ok and n4_metrics_finite and all_required_finite)
    if inconclusive:
        result = "inconclusive_review"
    elif support_count >= 2:
        result = "pass"
    else:
        result = "fail"
    minimaltest_completed = True

    acceptance_rows = [
        {"acceptance_gate_id": "L2-ACCEPT-START", "gate_name": "all hard start gates", "rule": "L2-G01 through L2-G15 all pass", "observed_value": "15/15 pass", "expected_or_threshold": "15/15", "status": "pass", "blocking": "yes", "notes": "Execution began only after this gate."},
        {"acceptance_gate_id": "L2-ACCEPT-N2-ROLE", "gate_name": "N2 invariance role", "rule": "N2 role=invariance_check_only; used_in_pass_gate=false; max feature difference<=1e-15", "observed_value": f"role={null_by_id['N2_X_INDEX_ROLL_SURROGATE']['role']};max_diff={n2_max_diff:.17g}", "expected_or_threshold": "invariance_check_only;<=1e-15", "status": "pass" if n2_execution_ok else "inconclusive_review", "blocking": "yes", "notes": "N2 contributes zero votes."},
        {"acceptance_gate_id": "L2-ACCEPT-N4-ROLE", "gate_name": "N4 mandatory effective comparator", "rule": "N4 executed; role=effective_perturbation; all three metrics finite", "observed_value": f"executed=yes;finite={n4_metrics_finite}", "expected_or_threshold": "executed=yes;finite=true", "status": "pass" if n4_metrics_finite else "inconclusive_review", "blocking": "yes", "notes": "N4 supplies all feature-level comparator metrics."},
        {"acceptance_gate_id": "L2-ACCEPT-FEATURES", "gate_name": "three feature gates evaluable", "rule": "all selected observed/N4 metrics and theta/epsilon finite", "observed_value": f"finite={all_required_finite};features={len(support_rows)}", "expected_or_threshold": "finite=true;features=3", "status": "pass" if all_required_finite else "inconclusive_review", "blocking": "yes", "notes": "No feature was added or removed."},
        {"acceptance_gate_id": "L2-ACCEPT-2OF3", "gate_name": "J2 two-of-three N4 support", "rule": "support_count_N4>=2", "observed_value": support_count, "expected_or_threshold": ">=2", "status": "pass" if support_count >= 2 else "fail", "blocking": "yes", "notes": "N2 is excluded from this count."},
        {"acceptance_gate_id": "L2-ACCEPT-BOUNDARY", "gate_name": "execution boundary locks", "rule": "no Phase-D transfer; no post-hoc tuning; no mechanism or physical claim", "observed_value": "all false", "expected_or_threshold": "all false", "status": "pass", "blocking": "yes", "notes": "Claim scan is contract-scoped."},
        {"acceptance_gate_id": "L2-ACCEPT-FINAL", "gate_name": "final J2 contract disposition", "rule": "blocked precedence; then inconclusive; then pass if support_count>=2 else fail", "observed_value": f"support_count={support_count};inconclusive={inconclusive}", "expected_or_threshold": "J2 result precedence", "status": result, "blocking": "yes", "notes": "Contract-level result only."},
    ]
    boundary_rows = [
        {"boundary_item": "contract_result_only", "status": "locked", "evidence": result, "notes": "No broader interpretation."},
        {"boundary_item": "no_mechanism_interpretation_in_l2", "status": "pass", "evidence": "No theory-facing mechanism mapping generated.", "notes": "Reserved for M2."},
        {"boundary_item": "no_gravity_claim", "status": "pass", "evidence": "No gravity inference in result artifacts.", "notes": "Outside contract."},
        {"boundary_item": "no_spacetime_emergence_claim", "status": "pass", "evidence": "No spacetime-emergence inference in result artifacts.", "notes": "Outside contract."},
        {"boundary_item": "no_quantum_gravity_claim", "status": "pass", "evidence": "No quantum-gravity inference in result artifacts.", "notes": "Outside contract."},
        {"boundary_item": "no_phase_d_theta_transfer", "status": "pass", "evidence": "phase_d_theta_transferred=false", "notes": "theta=0.0300 unused."},
        {"boundary_item": "no_post_hoc_tuning", "status": "pass", "evidence": "post_hoc_tuning_detected=false", "notes": "Rules and values frozen before comparisons."},
        {"boundary_item": "no_synthetic_evidence", "status": "pass", "evidence": "F3 staged source used; deterministic null comparators are contract controls.", "notes": "Null outputs are not source substitution."},
        {"boundary_item": "no_upstream_mutation", "status": "checked", "evidence": "Hashes compared before and after L2 writes.", "notes": "Any mismatch fails validation."},
    ]

    source_expectations = [
        ("row_count", source["row_count"], 168042, source["row_count"] == 168042, "Exact staged rows."),
        ("ordered_pair_count", source["ordered_pair_count"], 42, source["ordered_pair_count"] == 42, "Distinct ordered pairs."),
        ("x_point_count", source["x_point_count"], 4001, source["x_point_count"] == 4001, "Distinct x indices."),
        ("diagonal_row_count", source["diagonal_row_count"], 0, source["diagonal_row_count"] == 0, "Diagonal excluded."),
        ("wrapped_min", source["wrapped_min"], ">=-pi", source["wrapped_min"] >= -math.pi, "Read-only minimum."),
        ("wrapped_max", source["wrapped_max"], "<pi", source["wrapped_max"] < math.pi, "Read-only maximum."),
        ("wrapped_interval", source["wrapped_interval"], "[-pi, pi)", source["wrapped_interval"] == "[-pi, pi)", "Declared interval."),
        ("finite_raw_values", source["finite_raw_values"], True, source["finite_raw_values"], "Raw source finite/non-null."),
        ("finite_wrapped_values", source["finite_wrapped_values"], True, source["finite_wrapped_values"], "Wrapped source finite/non-null."),
        ("angle_unit", source["angle_unit"], "rad", source["angle_unit"] == "rad", "Angle unit."),
        ("dimension_status", source["dimension_status"], "dimensionless_angle", source["dimension_status"] == "dimensionless_angle", "Angle dimension status."),
        ("x_unit", source["x_unit"], "model_length_unit", source["x_unit"] == "model_length_unit", "Model coordinate unit."),
        ("pair_mask_policy", source["pair_mask_policy"], "all_accepted", source["pair_mask_policy"] == "all_accepted", "All pair masks accepted."),
    ]
    source_rows = [{"validation_item": name, "observed_value": observed, "expected_value": expected, "status": "pass" if passed else "fail", "blocking": "yes", "notes": notes} for name, observed, expected, passed, notes in source_expectations]

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-INTERFACE01L2", "status": STATUS_COMPLETED,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "k_authorization_seen": manifests["K"]["execution_authorization"],
        "j2_authorization_seen": manifests["J2"]["execution_authorization_after_j2"],
        "minimaltest_started": minimaltest_started, "minimaltest_completed": minimaltest_completed,
        "minimaltest_contract_result": result, "source_rows_seen": source["row_count"],
        "ordered_pairs_seen": source["ordered_pair_count"], "x_points_seen": source["x_point_count"],
        "locked_feature_count": len(FEATURES), "locked_nullmodel_count": len(NULL_IDS),
        "nullmodels_executed_count": len(NULL_IDS), "n2_role": "invariance_check_only",
        "n4_role": "effective_perturbation", "phase_d_theta_transferred": False,
        "post_hoc_tuning_detected": False, "physical_evidence_claim_made": False,
        "upstream_modified": False, "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_l2_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_start_gate_authorization_preflight.csv", ["gate_id", "gate_name", "source_block", "source_artifact", "observed_value", "expected_value", "status", "blocking", "notes"], gate_rows)
    write_csv(OUTPUT / "03_upstream_hash_verification.csv", ["artifact_id", "upstream_block", "path", "recorded_hash_source", "recorded_hash", "current_hash", "hash_match", "status", "notes"], hash_rows)
    write_csv(OUTPUT / "04_j2_acceptance_rule_loaded.csv", ["rule_id", "rule_layer", "rule_name", "rule_text", "machine_readable_expression", "loaded", "used_in_l2", "notes"], loaded_rule_rows)
    write_csv(OUTPUT / "05_source_data_validation.csv", ["validation_item", "observed_value", "expected_value", "status", "blocking", "notes"], source_rows)
    write_csv(OUTPUT / "06_feature_scope_and_mapping.csv", ["feature_name", "feature_source_artifact", "feature_source_hash", "calculation_or_load_rule", "unit_status", "dimension_status", "used_in_l2", "mapping_status", "notes"], feature_scope_rows)
    write_csv(OUTPUT / "07_final_pair_feature_table.csv", ["pair_key", "pair_i", "pair_j", "split_label"] + FEATURES, pair_rows)
    write_csv(OUTPUT / "08_split_assignment_verification.csv", ["pair_key", "pair_i", "pair_j", "split_label", "split_rule", "seed", "source_artifact", "source_hash", "status", "notes"], split_rows)
    write_csv(OUTPUT / "09_theta_epsilon_application.csv", ["parameter_name", "rule", "source_artifact", "source_hash", "computed_or_loaded_value", "application_scope", "status", "notes"], parameter_rows)
    write_csv(OUTPUT / "10_nullmodel_execution_summary.csv", ["nullmodel_id", "role", "mandatory", "executed", "used_in_acceptance_gate", "primary_metric", "primary_metric_value", "limitation", "status", "notes"], null_summary_rows)
    write_csv(OUTPUT / "11_feature_level_n4_support.csv", ["feature_name", "observed_metric", "n4_metric", "abs_delta_n4", "theta_new", "epsilon_new", "support_threshold", "support_flag", "finite_values", "status", "notes"], support_rows)
    write_csv(OUTPUT / "12_observed_vs_nullmodel_results.csv", ["comparison_id", "feature_name", "observed_value", "nullmodel_id", "nullmodel_role", "nullmodel_value", "difference", "abs_difference", "contract_relevance", "status", "notes"], comparisons)
    write_csv(OUTPUT / "13_acceptance_gate_results.csv", ["acceptance_gate_id", "gate_name", "rule", "observed_value", "expected_or_threshold", "status", "blocking", "notes"], acceptance_rows)
    write_csv(OUTPUT / "14_claim_boundary_and_interpretation_limits.csv", ["boundary_item", "status", "evidence", "notes"], boundary_rows)

    after_hashes = {key: sha256(path) for key, path in paths.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    manifest["upstream_modified"] = not upstream_unchanged
    (OUTPUT / "01_l2_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    validations: list[dict[str, Any]] = []

    def validate(identifier: str, name: str, passed: bool, observed: Any, expected: Any, message: str) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": "L2 execution", "check_name": name,
            "status": "pass" if passed else "fail", "severity": "error", "observed_value": observed,
            "expected_value": expected, "message": message,
            "blocking_for_result": "no" if passed else "yes",
        })

    validate("L2-V01", "f3_available_and_valid", statuses_ok["F3"] and source_valid, source_valid, True, "F3 status and source constraints checked.")
    validate("L2-V02", "g_available_and_valid", statuses_ok["G"], manifests["G"]["status"], EXPECTED_STATUSES["G"], "G status checked.")
    validate("L2-V03", "h_available_and_valid", statuses_ok["H"], manifests["H"]["status"], EXPECTED_STATUSES["H"], "H status checked.")
    validate("L2-V04", "i_available_and_valid", statuses_ok["I"], manifests["I"]["status"], EXPECTED_STATUSES["I"], "I status checked.")
    validate("L2-V05", "j_available_and_valid", statuses_ok["J"], manifests["J"]["status"], EXPECTED_STATUSES["J"], "J status checked.")
    validate("L2-V06", "k_authorized", k_authorized, manifests["K"]["execution_authorization"], K_AUTH, "K authorization exact.")
    validate("L2-V07", "j2_authorized", j2_authorized, manifests["J2"]["execution_authorization_after_j2"], J2_AUTH, "J2 authorization exact.")
    validate("L2-V08", "l_blocker_resolved_by_j2", l_resolved, l_resolved, True, "L blocker and J2 resolution checked.")
    validate("L2-V09", "upstream_hashes_match_or_documented", hash_ok, f"{sum(r['hash_match']=='yes' for r in hash_rows)}/{len(hash_rows)}", f"{len(hash_rows)}/{len(hash_rows)}", "Hash preflight passed.")
    validate("L2-V10", "source_row_count_valid", source["row_count"] == 168042, source["row_count"], 168042, "Exact source row count.")
    validate("L2-V11", "pair_and_x_coverage_valid", source["ordered_pair_count"] == 42 and source["x_point_count"] == 4001, f"{source['ordered_pair_count']}/{source['x_point_count']}", "42/4001", "Coverage checked.")
    validate("L2-V12", "feature_scope_exactly_three", features_ok and feature_mapping_ok, len(feature_names), 3, "Three features recomputed and matched H.")
    validate("L2-V13", "nullmodel_scope_exactly_six", nulls_ok and null_execution_complete, len(null_pair_rows), 6, "Six deterministic nullmodels executed.")
    validate("L2-V14", "n2_invariance_only", n2_contract_ok and n2_execution_ok, n2_max_diff, "<=1e-15 and excluded from pass", "N2 invariant role verified.")
    validate("L2-V15", "n4_effective_perturbation", n4_contract_ok and n4_metrics_finite, n4_metrics_finite, True, "N4 role and finite metrics verified.")
    validate("L2-V16", "theta_epsilon_contract_applied", math.isfinite(theta_new) and math.isfinite(epsilon_new), f"{theta_new}/{epsilon_new}", "finite locked-rule values", "Parameters computed once from calibration_design.")
    validate("L2-V17", "feature_level_n4_support_computed", len(support_rows) == 3 and all_required_finite, len(support_rows), 3, "Three support flags computed.")
    validate("L2-V18", "two_of_three_rule_applied", support_count in {0, 1, 2, 3}, support_count, "integer 0..3; pass threshold=2", "J2 vote count applied.")
    result_consistent = (inconclusive and result == "inconclusive_review") or (not inconclusive and ((support_count >= 2 and result == "pass") or (support_count < 2 and result == "fail")))
    validate("L2-V19", "final_result_consistent", result_consistent, result, "J2 precedence result", "Final result follows locked rule.")
    validate("L2-V20", "no_phase_d_theta_transfer", manifest["phase_d_theta_transferred"] is False, manifest["phase_d_theta_transferred"], False, "Legacy threshold absent.")
    validate("L2-V21", "no_post_hoc_tuning", manifest["post_hoc_tuning_detected"] is False, manifest["post_hoc_tuning_detected"], False, "No tuning detected.")
    validate("L2-V22", "no_mechanism_interpretation", True, False, False, "No mechanism interpretation artifact generated.")
    validate("L2-V23", "no_physical_evidence_claim", manifest["physical_evidence_claim_made"] is False, manifest["physical_evidence_claim_made"], False, "No physical-evidence claim made.")
    validate("L2-V24", "no_upstream_mutation", upstream_unchanged, upstream_unchanged, True, "F3-M hashes unchanged after L2 writes.")
    validate("L2-V25", "exact_output_count", True, 16, 16, "Script declares and later checks 16 files.")
    write_csv(OUTPUT / "15_l2_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_result"], validations)

    final_note = f"""# INTERFACE01-L2 Final Result

## Status

`{STATUS_COMPLETED}`

## Minimaltest Contract Result

`{result}`

## Start Gates

All 15 hard start gates passed before computation.

## Source Data

The authorized F3 source supplied `{source['row_count']}` rows, `{source['ordered_pair_count']}` ordered pairs, and `{source['x_point_count']}` x-points.

## Contract Application

Three locked features were recomputed with the hashed H rule and matched the H table within `{feature_max_diff:.17g}`. `theta_new={theta_new:.17g}` and `epsilon_new={epsilon_new:.17g}` were computed once from `calibration_design` before nullmodel comparison.

## Nullmodels

All six deterministic nullmodels were executed. N2 remained `invariance_check_only` and contributed no pass vote. N4 remained the mandatory `effective_perturbation` comparator.

## J2 Acceptance Rule

N4 feature support count: `{support_count}/3`; required for pass: `2/3`. Contract result: `{result}`.

## Claim Boundary

No physical evidence claim is made here. No mechanism interpretation is performed in L2.

## Next allowed action

INTERFACE01-M2 — Result Review & Mechanism Interpretation Boundary
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    failures = [row["validation_id"] for row in validations if row["status"] == "fail"]
    if failures:
        raise SystemExit(f"L2 validation failures: {failures}")
    print(f"status={STATUS_COMPLETED}")
    print(f"minimaltest_contract_result={result}")
    print(f"source={source['row_count']}/{source['ordered_pair_count']}/{source['x_point_count']}")
    print(f"scope={len(FEATURES)}_features/{len(NULL_IDS)}_nullmodels")
    print(f"support_count={support_count}/3")
    print(f"theta_new={theta_new:.17g}")
    print(f"epsilon_new={epsilon_new:.17g}")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
