#!/usr/bin/env python3
"""QSB-ST-COMP01-D1k deterministic synthetic phase-field exposure."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required for this runner. Install PyYAML or run in the "
        "project environment where yaml is available."
    ) from exc


CASE_FIELDS = [
    "run_id",
    "case_id",
    "phase_source_label",
    "phase_exposure_mode",
    "phase_construction_rule",
    "phase_construction_inputs",
    "phase_is_synthetic_diagnostic",
    "phase_is_physical",
    "phi_i",
    "phi_j",
    "delta_phi_raw",
    "delta_phi_wrapped",
    "wrapped_delta_phi_abs",
    "normalized_angular_distance",
    "cos_phi_i",
    "sin_phi_i",
    "cos_phi_j",
    "sin_phi_j",
    "cos_delta_phi",
    "sin_delta_phi",
    "cyclic_distance_cos_sin",
    "angular_phase_distance",
    "baseline_cyclic_phase_proxy_distance",
    "exposed_phase_cyclic_distance",
    "proxy_vs_exposed_phase_distance_delta",
    "profile_distance_raw",
    "control_overlap_rate",
    "decoy_success_rate",
    "cyclic_acceptance_distance_proxy",
    "cyclic_acceptance_distance_exposed",
    "current_false_accept_warning",
    "false_accept_warning_proxy",
    "false_accept_warning_exposed",
    "exclusion_success_proxy",
    "exclusion_success_exposed",
    "stable_candidate_proxy",
    "stable_candidate_exposed",
    "fragile_candidate_proxy",
    "fragile_candidate_exposed",
    "spectrum_matched_null_intrusion_warning",
    "adversarial_near_duplicate_intrusion_warning",
    "local_response_dominant_warning",
    "kernel_size_8_artifact_warning",
    "remaining_intrusion_warning",
    "exposed_phase_overstrictness_warning",
    "mastermind_status",
    "decision_status",
    "warning_flags",
    "interpretation_note",
]

AUDIT_FIELDS = [
    "run_id",
    "component_name",
    "available",
    "source_table",
    "non_empty_count",
    "missing_count",
    "min_value",
    "max_value",
    "mean_value",
    "used_for_phi_i",
    "used_for_phi_j",
    "interpretation_note",
]

RECHECK_FIELDS = [
    "run_id",
    "case_count",
    "phase_source_label",
    "phase_exposure_mode",
    "false_accept_warning_proxy_count",
    "false_accept_warning_exposed_count",
    "exclusion_success_proxy_rate",
    "exclusion_success_exposed_rate",
    "stable_candidate_proxy_count",
    "stable_candidate_exposed_count",
    "fragile_candidate_proxy_count",
    "fragile_candidate_exposed_count",
    "stable_candidate_loss_rate_exposed",
    "exposed_phase_overstrictness_warning_count",
    "remaining_intrusion_warning_count",
    "spectrum_matched_null_intrusion_count",
    "adversarial_near_duplicate_intrusion_count",
    "kernel_size_8_artifact_warning_count",
    "decision_status",
    "interpretation_note",
]

COMPARISON_FIELDS = [
    "run_id",
    "comparison_axis",
    "case_count",
    "mean_baseline_cyclic_phase_proxy_distance",
    "mean_exposed_phase_cyclic_distance",
    "mean_proxy_vs_exposed_phase_distance_delta",
    "false_accept_warning_proxy_count",
    "false_accept_warning_exposed_count",
    "proxy_vs_exposed_phase_mismatch_count",
    "proxy_vs_exposed_phase_mismatch_rate",
    "stable_candidate_proxy_count",
    "stable_candidate_exposed_count",
    "decision_status",
    "interpretation_note",
]

OVERSTRICTNESS_FIELDS = [
    "run_id",
    "stable_candidate_current_count",
    "stable_candidate_proxy_count",
    "stable_candidate_exposed_count",
    "current_stable_and_exposed_phase_stable_count",
    "current_stable_but_exposed_phase_fragile_count",
    "current_fragile_but_exposed_phase_stable_count",
    "current_fragile_and_exposed_phase_fragile_count",
    "stable_candidate_loss_rate_exposed",
    "retained_stable_candidate_rate_exposed",
    "exposed_phase_overstrictness_warning",
    "decision_status",
    "interpretation_note",
]

INTRUSION_FIELDS = [
    "run_id",
    "intrusion_group",
    "baseline_proxy_count",
    "exposed_phase_count",
    "exposed_phase_intrusion_rate",
    "dominant_decoy_family",
    "dominant_null_family",
    "dominant_kernel_size_label",
    "decision_status",
    "interpretation_note",
]

GENERATED_FILES = [
    "summary.json",
    "readout.md",
    "phase_exposed_case_profile_summary.csv",
    "phase_construction_audit.csv",
    "exposed_phase_cyclic_recheck_summary.csv",
    "proxy_vs_exposed_phase_comparison.csv",
    "exposed_phase_overstrictness_summary.csv",
    "exposed_phase_remaining_intrusion_summary.csv",
    "resolved_config.json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D1k deterministic synthetic phase-field exposure."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1k_deterministic_synthetic_phase_field_exposure_config.yaml",
    )
    return parser.parse_args()


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a mapping: {path}")
    return data


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def bool_from_csv(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def finite_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def normalized(value: Any) -> float:
    number = finite_float(value)
    return number / (1.0 + abs(number))


def positive(value: Any) -> float:
    return max(0.0, finite_float(value))


def safe_mean(values: list[float]) -> float | None:
    return mean(values) if values else None


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fieldnames})


def count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if bool_from_csv(row.get(field)))


def rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def values_for(rows: list[dict[str, Any]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(field)
        if value in (None, ""):
            continue
        number = finite_float(value)
        if math.isfinite(number):
            values.append(number)
    return values


def dominant(rows: list[dict[str, Any]], field: str) -> str:
    counts = Counter(str(row.get(field, "")) for row in rows if row.get(field, ""))
    return counts.most_common(1)[0][0] if counts else ""


def build_failure_outputs(
    config: dict[str, Any],
    output_dir: Path,
    reason: str,
    case_count: int,
    input_consistency_passed: bool,
) -> None:
    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "output_dir": config["output_dir"],
        "case_count": case_count,
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1f_outputs": True,
        "does_not_modify_d1h_outputs": True,
        "does_not_modify_d1i_outputs": True,
        "does_not_modify_d1j_outputs": True,
        "does_not_introduce_physical_phase": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "does_not_implement_mastermind": True,
        "input_consistency_passed": input_consistency_passed,
        "phase_source_label": config["phase_exposure"]["phase_source_label"],
        "phase_exposure_mode": config["phase_exposure"]["phase_exposure_mode"],
        "phase_construction_rule": config["phase_exposure"]["phase_construction_rule"],
        "phase_is_synthetic_diagnostic": True,
        "phase_is_physical": False,
        "phase_field_exposure_supported": False,
        "input_component_missing_warning_count": 0,
        "phase_source_decision_status": "failed_input_consistency_check",
        "cyclic_geometry_recheck_decision_status": "failed_input_consistency_check",
        "mastermind_status": "parked_not_implemented",
        "generated_files": GENERATED_FILES,
        "claim_boundary": config["metadata"]["claim_boundary"],
        "abort_reason": reason,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "readout.md").write_text(
        "\n".join(
            [
                "# QSB-ST-COMP01-D1k Deterministic Synthetic Phase-Field Exposure Extension Readout",
                "",
                "## Befund",
                "",
                f"Run aborted defensively: {reason}",
                "specificity_established: false",
                "phase_is_synthetic_diagnostic: true",
                "phase_is_physical: false",
                "",
                "## Interpretation",
                "",
                "Input consistency failed, so no partial phase-field exposure was interpreted.",
                "",
                "## Hypothese",
                "",
                "A later consistent input set may allow deterministic synthetic phase-field exposure.",
                "",
                "## Offene Lücke",
                "",
                "- no physical phase",
                "- no physical manifold",
                "- no specificity",
                "",
                "## Claim Boundary",
                "",
                "D1k does not introduce a physical phase.",
                "D1k does not implement Mastermind.",
                "",
                "## Machine-readable status",
                "",
                "```yaml",
                "specificity_established: false",
                "phase_is_synthetic_diagnostic: true",
                "phase_is_physical: false",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_audit_rows(
    run_id: str,
    merged_rows: list[dict[str, str]],
    component_names: list[str],
    phi_i_inputs: set[str],
    phi_j_inputs: set[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in component_names:
        available = bool(merged_rows) and name in merged_rows[0]
        values = values_for(merged_rows, name) if available else []
        rows.append(
            {
                "run_id": run_id,
                "component_name": name,
                "available": available,
                "source_table": "d1h_d1f_joined_case_rows" if available else "",
                "non_empty_count": len(values),
                "missing_count": max(0, len(merged_rows) - len(values)) if available else len(merged_rows),
                "min_value": min(values) if values else None,
                "max_value": max(values) if values else None,
                "mean_value": safe_mean(values),
                "used_for_phi_i": name in phi_i_inputs,
                "used_for_phi_j": name in phi_j_inputs,
                "interpretation_note": (
                    "Diagnostic component used for deterministic synthetic phase exposure."
                    if name in phi_i_inputs or name in phi_j_inputs
                    else "Diagnostic component audited for availability."
                ),
            }
        )
    return rows


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# QSB-ST-COMP01-D1k Deterministic Synthetic Phase-Field Exposure Extension Readout",
        "",
        "## Befund",
        "",
        "D1k is a synthetic diagnostic deterministic phase-field exposure extension.",
        f"run_id: {summary['run_id']}",
        f"case_count: {summary['case_count']}",
        f"specificity_established: {str(summary['specificity_established']).lower()}",
        f"phase_source_label: {summary['phase_source_label']}",
        f"phase_exposure_mode: {summary['phase_exposure_mode']}",
        f"phase_construction_rule: {summary['phase_construction_rule']}",
        f"phase_is_synthetic_diagnostic: {str(summary['phase_is_synthetic_diagnostic']).lower()}",
        f"phase_is_physical: {str(summary['phase_is_physical']).lower()}",
        f"false_accept_warning_exposed_count: {summary['false_accept_warning_exposed_count']}",
        f"exclusion_success_exposed_rate: {summary['exclusion_success_exposed_rate']}",
        f"stable_candidate_exposed_count: {summary['stable_candidate_exposed_count']}",
        f"fragile_candidate_exposed_count: {summary['fragile_candidate_exposed_count']}",
        f"proxy_vs_exposed_phase_mismatch_count: {summary['proxy_vs_exposed_phase_mismatch_count']}",
        f"proxy_vs_exposed_phase_mismatch_rate: {summary['proxy_vs_exposed_phase_mismatch_rate']}",
        f"stable_candidate_loss_rate_exposed: {summary['stable_candidate_loss_rate_exposed']}",
        f"remaining_intrusion_warning_count: {summary['remaining_intrusion_warning_count']}",
        "",
        "D1k does not rerun D1f.",
        "D1k does not modify D1f/D1h/D1i/D1j outputs.",
        "D1k does not introduce a physical phase.",
        "D1k does not introduce a physical manifold.",
        "D1k does not introduce a new identity score.",
        "D1k does not implement Mastermind or Knuth role-permutation diagnostics.",
        "",
        "## Interpretation",
        "",
        "The exposed phase-like fields are deterministic synthetic diagnostic fields derived from existing diagnostic components.",
        "The exposed cyclic geometry recheck is a methodological comparison against the D1h proxy baseline.",
        "Overstrictness and remaining intrusions are reported as diagnostic audit quantities.",
        "",
        "## Hypothese",
        "",
        "Transparent diagnostic synthetic phase fields may allow a more meaningful cyclic-coordinate test than cyclic_phase_proxy alone.",
        "",
        "## Offene Lücke",
        "",
        "- no real data",
        "- no diagnostic specificity established",
        "- no physical phase reconstruction",
        "- no physical manifold",
        "- no Bridge validation",
        "- no Lorentz metric",
        "- no physical time",
        "- no Pauli claim",
        "- Mastermind / Knuth / role-permutation remains parked",
        "",
        "## Claim Boundary",
        "",
        "cyclic_phase_proxy is diagnostic only.",
        "Exposed phase-like fields are diagnostic synthetic fields.",
        "phase_is_physical remains false.",
        "They are not physical phase reconstruction.",
        "D1k does not validate a physical Bridge.",
        "D1k does not derive a Lorentz metric.",
        "D1k does not introduce physical time.",
        "D1k does not claim fermionic Pauli exclusion.",
        "D1k does not establish diagnostic specificity.",
        "",
        "## Machine-readable status",
        "",
        "```yaml",
        f"block_id: {summary['block_id']}",
        f"run_id: {summary['run_id']}",
        f"case_count: {summary['case_count']}",
        "specificity_established: false",
        "phase_is_synthetic_diagnostic: true",
        "phase_is_physical: false",
        f"phase_source_decision_status: {summary['phase_source_decision_status']}",
        f"cyclic_geometry_recheck_decision_status: {summary['cyclic_geometry_recheck_decision_status']}",
        "mastermind_status: parked_not_implemented",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = read_config(config_path)
    run_id = config["run_id"]
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = {name: Path(path) for name, path in config["input_files"].items()}
    d1f_summary = read_json(inputs["d1f_summary"])
    d1h_summary = read_json(inputs["d1h_summary"])
    d1i_summary = read_json(inputs["d1i_summary"])
    d1j_summary = read_json(inputs["d1j_summary"])
    d1f_rows = read_csv(inputs["d1f_case_profile_summary"])
    d1h_rows = read_csv(inputs["d1h_cyclic_region_case_summary"])

    d1f_by_case = {row["case_id"]: row for row in d1f_rows}
    d1h_by_case = {row["case_id"]: row for row in d1h_rows}
    matched_ids = sorted(set(d1f_by_case) & set(d1h_by_case))
    input_consistency_passed = (
        len(matched_ids) >= 9000
        and int(d1f_summary["case_count"]) == len(d1f_rows)
        and int(d1h_summary["case_count"]) == len(d1h_rows)
        and int(d1i_summary["case_count"]) == int(d1j_summary["case_count"])
    )
    if not input_consistency_passed:
        build_failure_outputs(
            config,
            output_dir,
            f"matched case count below threshold or summary mismatch: matched={len(matched_ids)}",
            len(matched_ids),
            False,
        )
        return

    merged_rows: list[dict[str, str]] = []
    for case_id in matched_ids:
        merged = dict(d1f_by_case[case_id])
        for key, value in d1h_by_case[case_id].items():
            merged[key] = value
        merged_rows.append(merged)

    phase_cfg = config["phase_exposure"]
    recheck_cfg = config["cyclic_recheck"]
    labels = config["decision_labels"]
    phase_source_label = phase_cfg["phase_source_label"]
    phase_exposure_mode = phase_cfg["phase_exposure_mode"]
    phase_construction_rule = phase_cfg["phase_construction_rule"]
    phase_inputs = [
        "profile_distance_raw",
        "control_overlap_rate",
        "profile_distance_collision_penalized",
        "decoy_success_rate",
        "penalty_gap",
    ]
    phi_i_inputs = {"profile_distance_raw", "control_overlap_rate"}
    phi_j_inputs = {"decoy_success_rate", "penalty_gap", "profile_distance_collision_penalized"}
    missing_components = [name for name in phase_inputs if name not in merged_rows[0]]
    input_component_missing_warning_count = len(missing_components)

    threshold = float(recheck_cfg["cyclic_acceptance_distance_threshold"])
    cyclic_phase_weight = float(recheck_cfg["cyclic_phase_weight"])
    profile_weight = float(recheck_cfg["profile_distance_weight"])
    control_weight = float(recheck_cfg["control_overlap_weight"])
    decoy_weight = float(recheck_cfg["decoy_success_weight"])

    case_rows: list[dict[str, Any]] = []
    for row in merged_rows:
        profile_distance_raw = finite_float(row.get("profile_distance_raw"))
        control_overlap_rate = finite_float(row.get("control_overlap_rate"))
        profile_distance_collision_penalized = finite_float(
            row.get("profile_distance_collision_penalized")
        )
        decoy_success_rate = finite_float(row.get("decoy_success_rate"))
        penalty_gap = finite_float(row.get("penalty_gap"))
        phi_i = math.atan2(normalized(control_overlap_rate), normalized(profile_distance_raw))
        phi_j = math.atan2(
            normalized(decoy_success_rate + positive(penalty_gap)),
            normalized(profile_distance_collision_penalized),
        )
        delta_phi_raw = phi_i - phi_j
        delta_phi_wrapped = math.atan2(math.sin(delta_phi_raw), math.cos(delta_phi_raw))
        wrapped_delta_phi_abs = abs(delta_phi_wrapped)
        normalized_angular_distance = wrapped_delta_phi_abs / math.pi
        cos_phi_i = math.cos(phi_i)
        sin_phi_i = math.sin(phi_i)
        cos_phi_j = math.cos(phi_j)
        sin_phi_j = math.sin(phi_j)
        cos_delta_phi = math.cos(delta_phi_wrapped)
        sin_delta_phi = math.sin(delta_phi_wrapped)
        cyclic_distance_cos_sin = (
            math.sqrt((cos_phi_i - cos_phi_j) ** 2 + (sin_phi_i - sin_phi_j) ** 2) / 2.0
        )
        exposed_phase_cyclic_distance = normalized_angular_distance
        cyclic_acceptance_distance_exposed = (
            cyclic_phase_weight * exposed_phase_cyclic_distance
            + profile_weight * profile_distance_raw
            + control_weight * control_overlap_rate
            + decoy_weight * decoy_success_rate
        )
        current_false_accept = bool_from_csv(row.get("current_false_accept_warning"))
        false_accept_proxy = bool_from_csv(row.get("cyclic_false_accept_warning"))
        false_accept_exposed = (
            current_false_accept and cyclic_acceptance_distance_exposed <= threshold
        )
        exclusion_success_proxy = bool_from_csv(row.get("exclusion_success_flag"))
        exclusion_success_exposed = current_false_accept and not false_accept_exposed
        stable_proxy = bool_from_csv(row.get("stable_candidate_cyclic"))
        fragile_proxy = bool_from_csv(row.get("fragile_candidate_cyclic"))
        spectrum_warning = (
            row.get("null_family") == config["targeted_intrusion_families"]["spectrum_matched_null"]
            and false_accept_exposed
        )
        adversarial_warning = (
            row.get("decoy_family")
            == config["targeted_intrusion_families"]["adversarial_near_duplicate"]
            and false_accept_exposed
        )
        local_response_warning = (
            row.get("profile_weight_set_id")
            == config["targeted_intrusion_families"]["local_response_dominant"]
            and false_accept_exposed
        )
        kernel_warning = (
            row.get("kernel_size_label") == config["targeted_intrusion_families"]["kernel_size_8"]
            and false_accept_exposed
        )
        remaining_warning = any(
            [spectrum_warning, adversarial_warning, local_response_warning, kernel_warning]
        )
        stable_exposed = not false_accept_exposed and not remaining_warning
        fragile_exposed = not stable_exposed
        proxy_distance = finite_float(row.get("cyclic_phase_distance"))
        distance_delta = exposed_phase_cyclic_distance - proxy_distance
        warning_flags = []
        if false_accept_exposed:
            warning_flags.append("false_accept_warning_exposed")
        if spectrum_warning:
            warning_flags.append("spectrum_matched_null_intrusion_warning")
        if adversarial_warning:
            warning_flags.append("adversarial_near_duplicate_intrusion_warning")
        if local_response_warning:
            warning_flags.append("local_response_dominant_warning")
        if kernel_warning:
            warning_flags.append("kernel_size_8_artifact_warning")
        if stable_exposed:
            decision_status = labels["stable_retention_supported_candidate"]
        elif remaining_warning:
            decision_status = labels["exposed_phase_remaining_intrusion_warning"]
        elif false_accept_exposed:
            decision_status = labels["exposed_phase_geometry_no_improvement_warning"]
        else:
            decision_status = labels["inconclusive"]
        case_rows.append(
            {
                "run_id": run_id,
                "case_id": row["case_id"],
                "phase_source_label": phase_source_label,
                "phase_exposure_mode": phase_exposure_mode,
                "phase_construction_rule": phase_construction_rule,
                "phase_construction_inputs": phase_inputs,
                "phase_is_synthetic_diagnostic": True,
                "phase_is_physical": False,
                "phi_i": phi_i,
                "phi_j": phi_j,
                "delta_phi_raw": delta_phi_raw,
                "delta_phi_wrapped": delta_phi_wrapped,
                "wrapped_delta_phi_abs": wrapped_delta_phi_abs,
                "normalized_angular_distance": normalized_angular_distance,
                "cos_phi_i": cos_phi_i,
                "sin_phi_i": sin_phi_i,
                "cos_phi_j": cos_phi_j,
                "sin_phi_j": sin_phi_j,
                "cos_delta_phi": cos_delta_phi,
                "sin_delta_phi": sin_delta_phi,
                "cyclic_distance_cos_sin": cyclic_distance_cos_sin,
                "angular_phase_distance": normalized_angular_distance,
                "baseline_cyclic_phase_proxy_distance": proxy_distance,
                "exposed_phase_cyclic_distance": exposed_phase_cyclic_distance,
                "proxy_vs_exposed_phase_distance_delta": distance_delta,
                "profile_distance_raw": profile_distance_raw,
                "control_overlap_rate": control_overlap_rate,
                "decoy_success_rate": decoy_success_rate,
                "cyclic_acceptance_distance_proxy": finite_float(
                    row.get("cyclic_acceptance_distance")
                ),
                "cyclic_acceptance_distance_exposed": cyclic_acceptance_distance_exposed,
                "current_false_accept_warning": current_false_accept,
                "false_accept_warning_proxy": false_accept_proxy,
                "false_accept_warning_exposed": false_accept_exposed,
                "exclusion_success_proxy": exclusion_success_proxy,
                "exclusion_success_exposed": exclusion_success_exposed,
                "stable_candidate_proxy": stable_proxy,
                "stable_candidate_exposed": stable_exposed,
                "fragile_candidate_proxy": fragile_proxy,
                "fragile_candidate_exposed": fragile_exposed,
                "spectrum_matched_null_intrusion_warning": spectrum_warning,
                "adversarial_near_duplicate_intrusion_warning": adversarial_warning,
                "local_response_dominant_warning": local_response_warning,
                "kernel_size_8_artifact_warning": kernel_warning,
                "remaining_intrusion_warning": remaining_warning,
                "exposed_phase_overstrictness_warning": False,
                "mastermind_status": "parked_not_implemented",
                "decision_status": decision_status,
                "warning_flags": warning_flags,
                "interpretation_note": (
                    "Synthetic diagnostic deterministic phase exposure only; no physical phase claim."
                ),
                "_current_stable": bool_from_csv(row.get("stable_candidate_current")),
                "_current_fragile": bool_from_csv(row.get("fragile_candidate_current")),
                "_decoy_family": row.get("decoy_family", ""),
                "_null_family": row.get("null_family", ""),
                "_kernel_size_label": row.get("kernel_size_label", ""),
                "_profile_weight_set_id": row.get("profile_weight_set_id", ""),
                "_penalty_weight_set_id": row.get("penalty_weight_set_id", ""),
            }
        )

    case_count = len(case_rows)
    current_stable_count = sum(1 for row in case_rows if row["_current_stable"])
    current_stable_exposed_stable = sum(
        1 for row in case_rows if row["_current_stable"] and row["stable_candidate_exposed"]
    )
    current_stable_exposed_fragile = sum(
        1 for row in case_rows if row["_current_stable"] and row["fragile_candidate_exposed"]
    )
    current_fragile_exposed_stable = sum(
        1 for row in case_rows if row["_current_fragile"] and row["stable_candidate_exposed"]
    )
    current_fragile_exposed_fragile = sum(
        1 for row in case_rows if row["_current_fragile"] and row["fragile_candidate_exposed"]
    )
    stable_candidate_loss_rate_exposed = rate(current_stable_exposed_fragile, current_stable_count)
    retained_stable_candidate_rate_exposed = rate(current_stable_exposed_stable, current_stable_count)
    overstrict_warning = bool(
        stable_candidate_loss_rate_exposed is not None
        and stable_candidate_loss_rate_exposed
        > float(recheck_cfg["stable_candidate_loss_warning_rate"])
    )
    for row in case_rows:
        row["exposed_phase_overstrictness_warning"] = overstrict_warning

    false_accept_proxy_count = count_true(case_rows, "false_accept_warning_proxy")
    false_accept_exposed_count = count_true(case_rows, "false_accept_warning_exposed")
    exclusion_success_proxy_count = count_true(case_rows, "exclusion_success_proxy")
    exclusion_success_exposed_count = count_true(case_rows, "exclusion_success_exposed")
    stable_proxy_count = count_true(case_rows, "stable_candidate_proxy")
    stable_exposed_count = count_true(case_rows, "stable_candidate_exposed")
    fragile_proxy_count = count_true(case_rows, "fragile_candidate_proxy")
    fragile_exposed_count = count_true(case_rows, "fragile_candidate_exposed")
    current_false_accept_count = count_true(case_rows, "current_false_accept_warning")
    exclusion_success_proxy_rate = rate(exclusion_success_proxy_count, current_false_accept_count)
    exclusion_success_exposed_rate = rate(exclusion_success_exposed_count, current_false_accept_count)
    remaining_intrusion_count = count_true(case_rows, "remaining_intrusion_warning")
    spectrum_intrusion_count = count_true(case_rows, "spectrum_matched_null_intrusion_warning")
    adversarial_intrusion_count = count_true(
        case_rows, "adversarial_near_duplicate_intrusion_warning"
    )
    kernel_intrusion_count = count_true(case_rows, "kernel_size_8_artifact_warning")
    mismatch_count = sum(
        1
        for row in case_rows
        if row["false_accept_warning_proxy"] != row["false_accept_warning_exposed"]
        or row["stable_candidate_proxy"] != row["stable_candidate_exposed"]
    )
    mismatch_rate = rate(mismatch_count, case_count)
    mean_proxy_distance = safe_mean(values_for(case_rows, "baseline_cyclic_phase_proxy_distance"))
    mean_exposed_distance = safe_mean(values_for(case_rows, "exposed_phase_cyclic_distance"))
    mean_distance_delta = safe_mean(values_for(case_rows, "proxy_vs_exposed_phase_distance_delta"))
    exposed_phase_overstrictness_warning_count = int(overstrict_warning)
    if false_accept_exposed_count < false_accept_proxy_count:
        cyclic_decision = labels["exposed_phase_geometry_reduces_false_accept_candidate"]
    else:
        cyclic_decision = labels["exposed_phase_geometry_no_improvement_warning"]
    if overstrict_warning:
        overstrict_decision = labels["exposed_phase_overstrictness_warning"]
    else:
        overstrict_decision = labels["stable_retention_supported_candidate"]
    phase_source_decision = labels["deterministic_synthetic_phase_extension_supported_candidate"]

    audit_rows = build_audit_rows(run_id, merged_rows, phase_inputs, phi_i_inputs, phi_j_inputs)
    recheck_rows = [
        {
            "run_id": run_id,
            "case_count": case_count,
            "phase_source_label": phase_source_label,
            "phase_exposure_mode": phase_exposure_mode,
            "false_accept_warning_proxy_count": false_accept_proxy_count,
            "false_accept_warning_exposed_count": false_accept_exposed_count,
            "exclusion_success_proxy_rate": exclusion_success_proxy_rate,
            "exclusion_success_exposed_rate": exclusion_success_exposed_rate,
            "stable_candidate_proxy_count": stable_proxy_count,
            "stable_candidate_exposed_count": stable_exposed_count,
            "fragile_candidate_proxy_count": fragile_proxy_count,
            "fragile_candidate_exposed_count": fragile_exposed_count,
            "stable_candidate_loss_rate_exposed": stable_candidate_loss_rate_exposed,
            "exposed_phase_overstrictness_warning_count": exposed_phase_overstrictness_warning_count,
            "remaining_intrusion_warning_count": remaining_intrusion_count,
            "spectrum_matched_null_intrusion_count": spectrum_intrusion_count,
            "adversarial_near_duplicate_intrusion_count": adversarial_intrusion_count,
            "kernel_size_8_artifact_warning_count": kernel_intrusion_count,
            "decision_status": cyclic_decision,
            "interpretation_note": (
                "Exposed phase recheck is synthetic diagnostic only; no physical phase claim."
            ),
        }
    ]
    comparison_rows = [
        {
            "run_id": run_id,
            "comparison_axis": "proxy_vs_exposed_phase",
            "case_count": case_count,
            "mean_baseline_cyclic_phase_proxy_distance": mean_proxy_distance,
            "mean_exposed_phase_cyclic_distance": mean_exposed_distance,
            "mean_proxy_vs_exposed_phase_distance_delta": mean_distance_delta,
            "false_accept_warning_proxy_count": false_accept_proxy_count,
            "false_accept_warning_exposed_count": false_accept_exposed_count,
            "proxy_vs_exposed_phase_mismatch_count": mismatch_count,
            "proxy_vs_exposed_phase_mismatch_rate": mismatch_rate,
            "stable_candidate_proxy_count": stable_proxy_count,
            "stable_candidate_exposed_count": stable_exposed_count,
            "decision_status": (
                labels["proxy_vs_exposed_phase_mismatch_warning"]
                if mismatch_count
                else labels["stable_retention_supported_candidate"]
            ),
            "interpretation_note": "Proxy-vs-exposed comparison is methodological only.",
        }
    ]
    overstrictness_rows = [
        {
            "run_id": run_id,
            "stable_candidate_current_count": current_stable_count,
            "stable_candidate_proxy_count": stable_proxy_count,
            "stable_candidate_exposed_count": stable_exposed_count,
            "current_stable_and_exposed_phase_stable_count": current_stable_exposed_stable,
            "current_stable_but_exposed_phase_fragile_count": current_stable_exposed_fragile,
            "current_fragile_but_exposed_phase_stable_count": current_fragile_exposed_stable,
            "current_fragile_and_exposed_phase_fragile_count": current_fragile_exposed_fragile,
            "stable_candidate_loss_rate_exposed": stable_candidate_loss_rate_exposed,
            "retained_stable_candidate_rate_exposed": retained_stable_candidate_rate_exposed,
            "exposed_phase_overstrictness_warning": overstrict_warning,
            "decision_status": overstrict_decision,
            "interpretation_note": "Stable retention audit for exposed synthetic phase only.",
        }
    ]
    intrusion_specs = [
        (
            "spectrum_matched_null",
            "spectrum_matched_null_intrusion_warning",
            int(d1h_summary["spectrum_matched_null_intrusion_count"]),
        ),
        (
            "adversarial_near_duplicate_sweep",
            "adversarial_near_duplicate_intrusion_warning",
            int(d1h_summary["adversarial_near_duplicate_intrusion_count"]),
        ),
        (
            "local_response_dominant",
            "local_response_dominant_warning",
            int(d1h_summary["local_response_dominant_warning_count"]),
        ),
        (
            "strong_collision_penalties",
            None,
            sum(
                1
                for row in d1h_rows
                if row.get("penalty_weight_set_id") == "strong_collision_penalties"
                and bool_from_csv(row.get("cyclic_false_accept_warning"))
            ),
        ),
        (
            "kernel_size_8",
            "kernel_size_8_artifact_warning",
            int(d1h_summary["kernel_size_8_artifact_warning_count"]),
        ),
    ]
    intrusion_rows: list[dict[str, Any]] = []
    for group, flag, baseline_count in intrusion_specs:
        if flag is None:
            group_rows = [
                row
                for row in case_rows
                if row["_penalty_weight_set_id"] == "strong_collision_penalties"
                and row["false_accept_warning_exposed"]
            ]
            exposed_count = len(group_rows)
        else:
            group_rows = [row for row in case_rows if row.get(flag)]
            exposed_count = len(group_rows)
        intrusion_rows.append(
            {
                "run_id": run_id,
                "intrusion_group": group,
                "baseline_proxy_count": baseline_count,
                "exposed_phase_count": exposed_count,
                "exposed_phase_intrusion_rate": rate(exposed_count, case_count),
                "dominant_decoy_family": dominant(group_rows, "_decoy_family"),
                "dominant_null_family": dominant(group_rows, "_null_family"),
                "dominant_kernel_size_label": dominant(group_rows, "_kernel_size_label"),
                "decision_status": (
                    labels["exposed_phase_remaining_intrusion_warning"]
                    if exposed_count
                    else labels["stable_retention_supported_candidate"]
                ),
                "interpretation_note": "Remaining intrusion audit under exposed synthetic phase.",
            }
        )

    summary = {
        "block_id": config["block_id"],
        "run_id": run_id,
        "output_dir": config["output_dir"],
        "case_count": case_count,
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1f_outputs": True,
        "does_not_modify_d1h_outputs": True,
        "does_not_modify_d1i_outputs": True,
        "does_not_modify_d1j_outputs": True,
        "does_not_introduce_physical_phase": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "does_not_implement_mastermind": True,
        "input_consistency_passed": True,
        "phase_source_label": phase_source_label,
        "phase_exposure_mode": phase_exposure_mode,
        "phase_construction_rule": phase_construction_rule,
        "phase_is_synthetic_diagnostic": True,
        "phase_is_physical": False,
        "phase_field_exposure_supported": True,
        "input_component_missing_warning_count": input_component_missing_warning_count,
        "baseline_cyclic_phase_source": d1h_summary["cyclic_phase_source"],
        "baseline_proxy_false_accept_warning_count": d1j_summary[
            "baseline_proxy_false_accept_warning_count"
        ],
        "baseline_proxy_exclusion_success_rate": d1j_summary[
            "baseline_proxy_exclusion_success_rate"
        ],
        "baseline_proxy_stable_candidate_count": d1j_summary[
            "baseline_proxy_stable_candidate_count"
        ],
        "false_accept_warning_exposed_count": false_accept_exposed_count,
        "exclusion_success_exposed_rate": exclusion_success_exposed_rate,
        "stable_candidate_exposed_count": stable_exposed_count,
        "fragile_candidate_exposed_count": fragile_exposed_count,
        "stable_candidate_loss_rate_exposed": stable_candidate_loss_rate_exposed,
        "exposed_phase_overstrictness_warning_count": exposed_phase_overstrictness_warning_count,
        "remaining_intrusion_warning_count": remaining_intrusion_count,
        "spectrum_matched_null_intrusion_count": spectrum_intrusion_count,
        "adversarial_near_duplicate_intrusion_count": adversarial_intrusion_count,
        "kernel_size_8_artifact_warning_count": kernel_intrusion_count,
        "proxy_vs_exposed_phase_mismatch_count": mismatch_count,
        "proxy_vs_exposed_phase_mismatch_rate": mismatch_rate,
        "phase_source_decision_status": phase_source_decision,
        "cyclic_geometry_recheck_decision_status": cyclic_decision,
        "mastermind_status": "parked_not_implemented",
        "generated_files": GENERATED_FILES,
        "claim_boundary": config["metadata"]["claim_boundary"],
    }

    public_case_rows = [
        {field: row.get(field) for field in CASE_FIELDS}
        for row in case_rows
    ]
    write_csv(output_dir / "phase_exposed_case_profile_summary.csv", public_case_rows, CASE_FIELDS)
    write_csv(output_dir / "phase_construction_audit.csv", audit_rows, AUDIT_FIELDS)
    write_csv(output_dir / "exposed_phase_cyclic_recheck_summary.csv", recheck_rows, RECHECK_FIELDS)
    write_csv(output_dir / "proxy_vs_exposed_phase_comparison.csv", comparison_rows, COMPARISON_FIELDS)
    write_csv(
        output_dir / "exposed_phase_overstrictness_summary.csv",
        overstrictness_rows,
        OVERSTRICTNESS_FIELDS,
    )
    write_csv(
        output_dir / "exposed_phase_remaining_intrusion_summary.csv",
        intrusion_rows,
        INTRUSION_FIELDS,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / "readout.md", summary)

    print(
        json.dumps(
            {
                "run_id": run_id,
                "output_dir": config["output_dir"],
                "case_count": case_count,
                "phase_field_exposure_supported": True,
                "phase_is_physical": False,
                "false_accept_warning_exposed_count": false_accept_exposed_count,
                "cyclic_geometry_recheck_decision_status": cyclic_decision,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
