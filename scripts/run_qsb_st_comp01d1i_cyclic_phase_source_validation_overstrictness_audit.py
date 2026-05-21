#!/usr/bin/env python3
"""QSB-ST-COMP01-D1i cyclic-phase source validation and overstrictness audit.

This runner reads existing D1f, D1g, and D1h outputs. It does not rerun D1f,
does not modify D1g or D1h outputs, and does not introduce a physical phase,
physical manifold, or new identity score.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required for this D1i runner. Install PyYAML or run in the "
        "project environment where yaml is available."
    ) from exc


PHASE_COLUMNS = [
    "phi_i",
    "phi_j",
    "delta_phi_wrapped",
    "wrapped_delta_phi_abs",
    "cos_delta_phi",
    "sin_delta_phi",
    "angular_phase_profile",
    "phase_source_label",
]

PROXY_FIELDS = [
    "run_id",
    "proxy_variant_id",
    "row_count",
    "phase_source_label",
    "cyclic_false_accept_warning_count",
    "cyclic_false_accept_warning_rate",
    "exclusion_success_count",
    "exclusion_failure_count",
    "exclusion_success_rate",
    "exclusion_failure_rate",
    "stable_candidate_cyclic_count",
    "fragile_candidate_cyclic_count",
    "stable_candidate_loss_count",
    "stable_candidate_loss_rate",
    "mean_cyclic_acceptance_distance",
    "mean_warning_count_variant",
    "delta_false_accept_count_vs_baseline",
    "delta_exclusion_success_rate_vs_baseline",
    "delta_stable_candidate_count_vs_baseline",
    "proxy_dependence_warning",
    "phase_source_validation_status",
    "decision_status",
    "interpretation_note",
]

THRESHOLD_FIELDS = [
    "run_id",
    "proxy_variant_id",
    "threshold_variant_id",
    "row_count",
    "cyclic_acceptance_distance_threshold",
    "cyclic_phase_small",
    "profile_distance_low",
    "cyclic_false_accept_warning_count",
    "cyclic_false_accept_warning_rate",
    "exclusion_success_rate",
    "exclusion_failure_rate",
    "stable_candidate_loss_count",
    "stable_candidate_loss_rate",
    "threshold_sensitivity_warning",
    "overstrictness_warning",
    "decision_status",
    "interpretation_note",
]

STABLE_FIELDS = [
    "run_id",
    "proxy_variant_id",
    "threshold_variant_id",
    "stable_candidate_current_count",
    "stable_candidate_cyclic_variant_count",
    "fragile_candidate_current_count",
    "fragile_candidate_cyclic_variant_count",
    "current_stable_and_cyclic_stable_count",
    "current_stable_but_cyclic_fragile_count",
    "current_fragile_but_cyclic_stable_count",
    "current_fragile_and_cyclic_fragile_count",
    "stable_candidate_loss_rate",
    "retained_stable_candidate_rate",
    "overstrictness_warning",
    "decision_status",
    "interpretation_note",
]

INTRUSION_FIELDS = [
    "run_id",
    "proxy_variant_id",
    "threshold_variant_id",
    "intrusion_type",
    "row_count",
    "intrusion_warning_count",
    "intrusion_warning_rate",
    "mean_cyclic_acceptance_distance",
    "dominant_decoy_family",
    "dominant_null_family",
    "dominant_profile_weight_set_id",
    "dominant_penalty_weight_set_id",
    "dominant_kernel_size_label",
    "decision_status",
    "interpretation_note",
]

PHASE_SOURCE_FIELDS = [
    "run_id",
    "phase_source_label",
    "explicit_phase_source_available",
    "detected_phase_columns",
    "proxy_variant_count",
    "baseline_proxy_variant_id",
    "proxy_dependence_warning_count",
    "threshold_sensitivity_warning_count",
    "overstrictness_warning_count",
    "phase_source_validation_status",
    "decision_status",
    "interpretation_note",
]

OUTPUT_FILES = [
    "summary.json",
    "readout.md",
    "proxy_variant_summary.csv",
    "threshold_sensitivity_summary.csv",
    "stable_retention_summary.csv",
    "remaining_intrusion_summary.csv",
    "phase_source_comparison_summary.csv",
    "resolved_config.json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the QSB-ST-COMP01-D1i cyclic-phase source validation and "
            "overstrictness audit."
        )
    )
    parser.add_argument(
        "--config",
        default=(
            "data/"
            "qsb_st_comp01d1i_cyclic_phase_source_validation_overstrictness_config.yaml"
        ),
    )
    return parser.parse_args()


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a mapping: {path}")
    return data


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"JSON must be a mapping: {path}")
    return data


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def to_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_rate(count: int, total: int) -> float:
    return count / total if total else 0.0


def safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


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


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fields})


def stable_unit_interval(seed_text: str) -> float:
    digest = hashlib.md5(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def stable_angle(seed_text: str) -> float:
    return 2.0 * math.pi * stable_unit_interval(seed_text)


def wrap_principal(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def phase_distance_from_angle(angle: float) -> float:
    return min(abs(wrap_principal(angle)) / math.pi, 1.0)


def dominant(rows: list[dict[str, Any]], field: str) -> str:
    values = [str(row.get(field, "")) for row in rows if row.get(field, "") != ""]
    if not values:
        return ""
    return Counter(values).most_common(1)[0][0]


def detect_phase_columns(field_sets: list[list[str]]) -> list[str]:
    available: set[str] = set()
    for fields in field_sets:
        available.update(fields)
    return [field for field in PHASE_COLUMNS if field in available]


def join_optional_sources(
    d1h_rows: list[dict[str, str]],
    d1f_rows: list[dict[str, str]],
    d1g_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    d1f_by_case = {row.get("case_id", ""): row for row in d1f_rows}
    d1g_by_case = {row.get("case_id", ""): row for row in d1g_rows}
    joined: list[dict[str, Any]] = []

    for row in d1h_rows:
        merged: dict[str, Any] = dict(row)
        case_id = row.get("case_id", "")
        d1f = d1f_by_case.get(case_id, {})
        d1g = d1g_by_case.get(case_id, {})
        for key, value in d1f.items():
            merged.setdefault(f"d1f_{key}", value)
        for key, value in d1g.items():
            merged.setdefault(f"d1g_{key}", value)
        joined.append(merged)

    return joined


def proxy_phase_distance(row: dict[str, Any], proxy_variant: dict[str, Any]) -> float:
    mode = str(proxy_variant.get("mode", ""))
    if mode == "reuse_d1h":
        return min(max(to_float(row.get("cyclic_phase_distance")), 0.0), 1.0)

    case_id = str(row.get("case_id", ""))
    decoy_family = str(row.get("decoy_family", ""))
    null_family = str(row.get("null_family", ""))
    profile_weight_set_id = str(row.get("profile_weight_set_id", ""))
    penalty_weight_set_id = str(row.get("penalty_weight_set_id", ""))
    kernel_size_label = str(row.get("kernel_size_label", ""))
    profile_distance_raw = to_float(row.get("profile_distance_raw"))

    seed = "|".join(
        [
            mode,
            case_id,
            decoy_family,
            null_family,
            profile_weight_set_id,
            penalty_weight_set_id,
            kernel_size_label,
        ]
    )
    hash_angle = stable_angle(seed)

    if mode == "hash_only":
        angle = hash_angle
    elif mode == "distance_modulated":
        angle = hash_angle + (2.0 * math.pi * profile_distance_raw)
    elif mode == "decoy_family_modulated":
        angle = hash_angle + stable_angle(f"decoy|{decoy_family}") * 0.5
    elif mode == "null_family_modulated":
        angle = hash_angle + stable_angle(f"null|{null_family}") * 0.5
    elif mode == "seeded_control":
        angle = stable_angle(f"seeded_control|{case_id}")
    else:
        angle = hash_angle

    return phase_distance_from_angle(angle)


def acceptance_distance(row: dict[str, Any], phase_distance: float) -> float:
    return (
        0.45 * phase_distance
        + 0.35 * to_float(row.get("profile_distance_raw"))
        + 0.10 * to_float(row.get("control_overlap_rate"))
        + 0.10 * to_float(row.get("decoy_success_rate"))
    )


def compute_case_variant(
    row: dict[str, Any],
    proxy_variant: dict[str, Any],
    threshold_variant: dict[str, Any],
    targeted: dict[str, Any],
) -> dict[str, Any]:
    phase_distance = proxy_phase_distance(row, proxy_variant)
    if str(proxy_variant.get("mode")) == "reuse_d1h":
        acceptance = to_float(row.get("cyclic_acceptance_distance"))
    else:
        acceptance = acceptance_distance(row, phase_distance)

    threshold = to_float(threshold_variant.get("cyclic_acceptance_distance_threshold"))
    member = acceptance <= threshold
    current_false_accept = parse_bool(row.get("current_false_accept_warning"))
    cyclic_false_accept = current_false_accept and member
    exclusion_success = current_false_accept and not member
    exclusion_failure = current_false_accept and member

    decoy_family = str(row.get("decoy_family", ""))
    null_family = str(row.get("null_family", ""))
    profile_weight_set_id = str(row.get("profile_weight_set_id", ""))
    penalty_weight_set_id = str(row.get("penalty_weight_set_id", ""))
    kernel_size_label = str(row.get("kernel_size_label", ""))

    spectrum_warning = (
        null_family == targeted.get("spectrum_matched_null")
        and cyclic_false_accept
    )
    adversarial_warning = (
        decoy_family == targeted.get("adversarial_near_duplicate")
        and cyclic_false_accept
    )
    local_warning = (
        profile_weight_set_id == targeted.get("local_response_dominant")
        and cyclic_false_accept
    )
    cosmetic_warning = to_float(row.get("penalty_gap")) > 0 and cyclic_false_accept
    kernel_warning = (
        kernel_size_label == targeted.get("kernel_size_8")
        and cyclic_false_accept
    )
    impostor_overlap = decoy_family != "exact_duplicate" and member
    targeted_intrusion = any(
        [
            spectrum_warning,
            adversarial_warning,
            local_warning,
            cosmetic_warning,
            kernel_warning,
            impostor_overlap,
        ]
    )

    stable_current = parse_bool(row.get("stable_candidate_current"))
    fragile_current = parse_bool(row.get("fragile_candidate_current"))
    stable_cyclic = (
        not cyclic_false_accept
        and not impostor_overlap
        and not targeted_intrusion
    )
    fragile_cyclic = not stable_cyclic
    current_stable_but_cyclic_fragile = stable_current and fragile_cyclic
    current_fragile_but_cyclic_stable = fragile_current and stable_cyclic

    warning_count = sum(
        bool(flag)
        for flag in [
            cyclic_false_accept,
            impostor_overlap,
            spectrum_warning,
            adversarial_warning,
            local_warning,
            cosmetic_warning,
            kernel_warning,
        ]
    )

    return {
        "case_id": row.get("case_id", ""),
        "decoy_family": decoy_family,
        "null_family": null_family,
        "profile_weight_set_id": profile_weight_set_id,
        "penalty_weight_set_id": penalty_weight_set_id,
        "kernel_size_label": kernel_size_label,
        "cyclic_phase_distance_variant": phase_distance,
        "cyclic_acceptance_distance_variant": acceptance,
        "cyclic_acceptance_region_member_variant": member,
        "current_false_accept_warning": current_false_accept,
        "cyclic_false_accept_warning_variant": cyclic_false_accept,
        "exclusion_success_variant": exclusion_success,
        "exclusion_failure_variant": exclusion_failure,
        "stable_candidate_current": stable_current,
        "fragile_candidate_current": fragile_current,
        "stable_candidate_cyclic_variant": stable_cyclic,
        "fragile_candidate_cyclic_variant": fragile_cyclic,
        "current_stable_but_cyclic_fragile": current_stable_but_cyclic_fragile,
        "current_fragile_but_cyclic_stable": current_fragile_but_cyclic_stable,
        "current_stable_and_cyclic_stable": stable_current and stable_cyclic,
        "current_fragile_and_cyclic_fragile": fragile_current and fragile_cyclic,
        "spectrum_matched_null_intrusion_warning_variant": spectrum_warning,
        "adversarial_near_duplicate_intrusion_warning_variant": adversarial_warning,
        "local_response_dominant_warning_variant": local_warning,
        "cosmetic_penalty_lock_warning_variant": cosmetic_warning,
        "kernel_size_8_artifact_warning_variant": kernel_warning,
        "impostor_overlap_warning_variant": impostor_overlap,
        "warning_count_variant": warning_count,
        "baseline_decision_status": row.get("decision_status", ""),
    }


def aggregate_cases(
    cases: list[dict[str, Any]],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    row_count = len(cases)
    stable_current_count = sum(case["stable_candidate_current"] for case in cases)
    stable_loss_count = sum(
        case["current_stable_but_cyclic_fragile"] for case in cases
    )
    retained_stable_count = sum(
        case["current_stable_and_cyclic_stable"] for case in cases
    )
    stable_loss_rate = safe_rate(stable_loss_count, stable_current_count)
    retained_stable_rate = safe_rate(retained_stable_count, stable_current_count)
    exclusion_success_count = sum(case["exclusion_success_variant"] for case in cases)
    exclusion_failure_count = sum(case["exclusion_failure_variant"] for case in cases)
    current_false_accept_count = sum(
        case["current_false_accept_warning"] for case in cases
    )
    overstrict = stable_loss_rate > to_float(
        thresholds.get("overstrict_stable_loss_rate_threshold")
    ) or any(
        case.get("baseline_decision_status") == "cyclic_region_overstrict_warning"
        for case in cases
    )

    return {
        "row_count": row_count,
        "cyclic_false_accept_warning_count": sum(
            case["cyclic_false_accept_warning_variant"] for case in cases
        ),
        "cyclic_false_accept_warning_rate": safe_rate(
            sum(case["cyclic_false_accept_warning_variant"] for case in cases),
            row_count,
        ),
        "exclusion_success_count": exclusion_success_count,
        "exclusion_failure_count": exclusion_failure_count,
        "exclusion_success_rate": safe_rate(
            exclusion_success_count,
            current_false_accept_count,
        ),
        "exclusion_failure_rate": safe_rate(
            exclusion_failure_count,
            current_false_accept_count,
        ),
        "stable_candidate_current_count": stable_current_count,
        "stable_candidate_cyclic_count": sum(
            case["stable_candidate_cyclic_variant"] for case in cases
        ),
        "fragile_candidate_current_count": sum(
            case["fragile_candidate_current"] for case in cases
        ),
        "fragile_candidate_cyclic_count": sum(
            case["fragile_candidate_cyclic_variant"] for case in cases
        ),
        "current_stable_and_cyclic_stable_count": sum(
            case["current_stable_and_cyclic_stable"] for case in cases
        ),
        "current_stable_but_cyclic_fragile_count": stable_loss_count,
        "current_fragile_but_cyclic_stable_count": sum(
            case["current_fragile_but_cyclic_stable"] for case in cases
        ),
        "current_fragile_and_cyclic_fragile_count": sum(
            case["current_fragile_and_cyclic_fragile"] for case in cases
        ),
        "stable_candidate_loss_count": stable_loss_count,
        "stable_candidate_loss_rate": stable_loss_rate,
        "retained_stable_candidate_count": retained_stable_count,
        "retained_stable_candidate_rate": retained_stable_rate,
        "mean_cyclic_acceptance_distance": safe_mean(
            [case["cyclic_acceptance_distance_variant"] for case in cases]
        ),
        "mean_warning_count_variant": safe_mean(
            [case["warning_count_variant"] for case in cases]
        ),
        "overstrictness_warning": overstrict,
    }


def decision_for_aggregate(
    proxy_warning: bool,
    threshold_warning: bool,
    overstrictness_warning: bool,
    stable_loss_rate: float,
    intrusion_warning_count: int,
    phase_source_status: str,
) -> str:
    if phase_source_status == "failed_input_consistency_check":
        return "failed_input_consistency_check"
    if overstrictness_warning:
        return "cyclic_overstrictness_warning"
    if stable_loss_rate > 0:
        return "stable_candidate_loss_warning"
    if proxy_warning:
        return "cyclic_phase_proxy_dependence_warning"
    if threshold_warning:
        return "cyclic_threshold_sensitivity_warning"
    if intrusion_warning_count > 0:
        return "remaining_intrusion_warning"
    if phase_source_status == "explicit_phase_source_available_candidate":
        return "explicit_phase_source_available_candidate"
    if phase_source_status == "explicit_phase_source_missing":
        return "explicit_phase_source_needed"
    return "stable_retention_supported_candidate"


def build_intrusion_rows(
    run_id: str,
    proxy_id: str,
    threshold_id: str,
    cases: list[dict[str, Any]],
    audit_thresholds: dict[str, Any],
) -> list[dict[str, Any]]:
    intrusion_defs = [
        (
            "spectrum_matched_null_intrusion",
            "spectrum_matched_null_intrusion_warning_variant",
        ),
        (
            "adversarial_near_duplicate_intrusion",
            "adversarial_near_duplicate_intrusion_warning_variant",
        ),
        ("local_response_dominant", "local_response_dominant_warning_variant"),
        ("cosmetic_penalty_lock", "cosmetic_penalty_lock_warning_variant"),
        ("kernel_size_8_artifact", "kernel_size_8_artifact_warning_variant"),
        ("impostor_overlap", "impostor_overlap_warning_variant"),
    ]
    rows: list[dict[str, Any]] = []
    warning_rate_limit = to_float(
        audit_thresholds.get("remaining_intrusion_warning_rate")
    )

    for intrusion_type, flag in intrusion_defs:
        matched = [case for case in cases if case[flag]]
        count = len(matched)
        rate = safe_rate(count, len(cases))
        warning = rate > warning_rate_limit
        decision = "remaining_intrusion_warning" if warning else "inconclusive"
        rows.append(
            {
                "run_id": run_id,
                "proxy_variant_id": proxy_id,
                "threshold_variant_id": threshold_id,
                "intrusion_type": intrusion_type,
                "row_count": len(cases),
                "intrusion_warning_count": count,
                "intrusion_warning_rate": rate,
                "mean_cyclic_acceptance_distance": safe_mean(
                    [case["cyclic_acceptance_distance_variant"] for case in matched]
                ),
                "dominant_decoy_family": dominant(matched, "decoy_family"),
                "dominant_null_family": dominant(matched, "null_family"),
                "dominant_profile_weight_set_id": dominant(
                    matched,
                    "profile_weight_set_id",
                ),
                "dominant_penalty_weight_set_id": dominant(
                    matched,
                    "penalty_weight_set_id",
                ),
                "dominant_kernel_size_label": dominant(matched, "kernel_size_label"),
                "decision_status": decision,
                "interpretation_note": (
                    "Remaining intrusion group for diagnostic review; this is not "
                    "a physical particle population claim."
                ),
            }
        )
    return rows


def write_failure_outputs(
    output_dir: Path,
    config: dict[str, Any],
    row_count: int,
    detected_phase_columns: list[str],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "input_run_id_d1h": Path(config["input_dir_d1h"]).name,
        "output_dir": str(output_dir),
        "case_count": row_count,
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1g_outputs": True,
        "does_not_modify_d1h_outputs": True,
        "does_not_introduce_physical_phase": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "input_consistency_passed": False,
        "baseline_cyclic_phase_source": "cyclic_phase_proxy",
        "explicit_phase_source_available": bool(detected_phase_columns),
        "detected_phase_columns": detected_phase_columns,
        "proxy_variant_count": len(config.get("proxy_variants", [])),
        "threshold_variant_count": len(config.get("threshold_variants", [])),
        "baseline_cyclic_false_accept_warning_count": None,
        "baseline_exclusion_success_rate": None,
        "baseline_stable_candidate_cyclic_count": None,
        "proxy_dependence_warning_count": 0,
        "threshold_sensitivity_warning_count": 0,
        "overstrictness_warning_count": 0,
        "stable_candidate_loss_warning_count": 0,
        "remaining_intrusion_warning_count": 0,
        "phase_source_validation_status": "failed_input_consistency_check",
        "dominant_proxy_variant_decision_status": "failed_input_consistency_check",
        "dominant_threshold_decision_status": "failed_input_consistency_check",
        "mean_delta_false_accept_count_vs_baseline": 0.0,
        "mean_delta_exclusion_success_rate_vs_baseline": 0.0,
        "mean_stable_candidate_loss_rate": 0.0,
        "decision_status_counts": {"failed_input_consistency_check": 1},
        "generated_files": OUTPUT_FILES,
        "claim_boundary": config["metadata"]["claim_boundary"],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "readout.md").write_text(
        "# QSB-ST-COMP01-D1i Cyclic-Phase Source Validation and Overstrictness Audit Readout\n\n"
        "## Befund\n\n"
        "Input consistency failed before the audit could be interpreted.\n\n"
        "## Interpretation\n\n"
        "No D1i interpretation is available because the joined case count is below the configured minimum.\n\n"
        "## Hypothese\n\n"
        "No hypothesis update is made.\n\n"
        "## Offene Luecke\n\n"
        "No physical validation, no real data, no specificity, and no physical phase reconstruction.\n\n"
        "## Claim Boundary\n\n"
        "D1i does not rerun D1f and does not modify D1g/D1h outputs. "
        "It does not introduce a physical phase, physical manifold, or new identity score.\n\n"
        "## Machine-readable status\n\n"
        "```yaml\n"
        "decision_status: failed_input_consistency_check\n"
        "specificity_established: false\n"
        "```\n",
        encoding="utf-8",
    )
    write_csv(output_dir / "proxy_variant_summary.csv", [], PROXY_FIELDS)
    write_csv(output_dir / "threshold_sensitivity_summary.csv", [], THRESHOLD_FIELDS)
    write_csv(output_dir / "stable_retention_summary.csv", [], STABLE_FIELDS)
    write_csv(output_dir / "remaining_intrusion_summary.csv", [], INTRUSION_FIELDS)
    write_csv(
        output_dir / "phase_source_comparison_summary.csv",
        [],
        PHASE_SOURCE_FIELDS,
    )
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    detected = ", ".join(summary["detected_phase_columns"]) or "none"
    text = f"""# QSB-ST-COMP01-D1i Cyclic-Phase Source Validation and Overstrictness Audit Readout

## Befund

D1i is a synthetic diagnostic cyclic-phase source validation and overstrictness audit.

D1i does not rerun D1f.

D1i does not modify D1g/D1h outputs.

D1i does not introduce a physical phase.

D1i does not introduce a physical manifold.

D1i does not introduce a new identity score.

`case_count`: {summary["case_count"]}
`specificity_established`: false
`baseline_cyclic_phase_source`: {summary["baseline_cyclic_phase_source"]}
`baseline_cyclic_false_accept_warning_count`: {summary["baseline_cyclic_false_accept_warning_count"]}
`baseline_exclusion_success_rate`: {summary["baseline_exclusion_success_rate"]}
`baseline_stable_candidate_cyclic_count`: {summary["baseline_stable_candidate_cyclic_count"]}
`proxy_variant_count`: {summary["proxy_variant_count"]}
`threshold_variant_count`: {summary["threshold_variant_count"]}
`explicit_phase_source_available`: {str(summary["explicit_phase_source_available"]).lower()}
`detected_phase_columns`: {detected}

## Interpretation

The audit recomputes deterministic diagnostic proxy variants and threshold variants against the D1h baseline. It reports proxy-dependence warnings, threshold-sensitivity warnings, overstrictness warnings, stable-candidate loss, and remaining intrusion groups.

`proxy_dependence_warning_count`: {summary["proxy_dependence_warning_count"]}
`threshold_sensitivity_warning_count`: {summary["threshold_sensitivity_warning_count"]}
`overstrictness_warning_count`: {summary["overstrictness_warning_count"]}
`stable_candidate_loss_warning_count`: {summary["stable_candidate_loss_warning_count"]}
`remaining_intrusion_warning_count`: {summary["remaining_intrusion_warning_count"]}

## Hypothese

Explicit phase-like synthetic fields may be needed if proxy variants or threshold perturbations materially change the D1h result. This remains a diagnostic hypothesis, not a physical phase claim.

`phase_source_validation_status`: {summary["phase_source_validation_status"]}
`mean_delta_false_accept_count_vs_baseline`: {summary["mean_delta_false_accept_count_vs_baseline"]}
`mean_delta_exclusion_success_rate_vs_baseline`: {summary["mean_delta_exclusion_success_rate_vs_baseline"]}
`mean_stable_candidate_loss_rate`: {summary["mean_stable_candidate_loss_rate"]}

## Offene Luecke

- no physical phase
- no physical manifold
- no Bridge validation
- no Lorentz metric
- no physical time
- no Pauli claim
- no diagnostic specificity established
- no real-data validation

## Claim Boundary

cyclic_phase_proxy is diagnostic only.

D1i does not introduce a physical phase.

D1i does not introduce a physical manifold.

D1i does not introduce a new identity score.

D1i does not validate a physical Bridge.

D1i does not derive a Lorentz metric.

D1i does not introduce physical time.

D1i does not claim fermionic Pauli exclusion.

specificity_established remains false.

## Machine-readable status

```yaml
block_id: "{summary["block_id"]}"
run_id: "{summary["run_id"]}"
input_run_id_d1h: "{summary["input_run_id_d1h"]}"
output_dir: "{summary["output_dir"]}"
case_count: {summary["case_count"]}
specificity_established: false
does_not_rerun_d1f: true
does_not_modify_d1g_outputs: true
does_not_modify_d1h_outputs: true
does_not_introduce_physical_phase: true
does_not_introduce_physical_manifold: true
does_not_introduce_new_identity_score: true
input_consistency_passed: {str(summary["input_consistency_passed"]).lower()}
baseline_cyclic_phase_source: "{summary["baseline_cyclic_phase_source"]}"
explicit_phase_source_available: {str(summary["explicit_phase_source_available"]).lower()}
phase_source_validation_status: "{summary["phase_source_validation_status"]}"
claim_boundary: "{summary["claim_boundary"]}"
```
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = read_config(Path(args.config))
    input_files = config["input_files"]
    output_dir = Path(config["output_dir"])

    d1f_summary = read_json(Path(input_files["d1f_summary"]))
    d1g_summary = read_json(Path(input_files["d1g_summary"]))
    d1h_summary = read_json(Path(input_files["d1h_summary"]))
    d1f_rows, d1f_fields = read_csv_rows(Path(input_files["d1f_case_profile_summary"]))
    d1g_rows, d1g_fields = read_csv_rows(
        Path(input_files["d1g_decision_table_case_classification"])
    )
    d1h_rows, d1h_fields = read_csv_rows(
        Path(input_files["d1h_cyclic_region_case_summary"])
    )
    # These D1h files are read as input consistency guards, not modified.
    read_csv_rows(Path(input_files["d1h_cyclic_vs_current_region_summary"]))
    read_csv_rows(Path(input_files["d1h_impostor_exclusion_summary"]))
    read_csv_rows(Path(input_files["d1h_decision_table_cyclic_summary"]))
    read_csv_rows(Path(input_files["d1h_kernel_size_cyclic_sensitivity_summary"]))

    detected_phase_columns = detect_phase_columns([d1f_fields, d1g_fields, d1h_fields])
    minimum_count = int(config["audit_thresholds"]["minimum_joined_case_count"])
    joined = join_optional_sources(d1h_rows, d1f_rows, d1g_rows)

    if len(joined) < minimum_count:
        write_failure_outputs(output_dir, config, len(joined), detected_phase_columns)
        raise SystemExit(
            "failed_input_consistency_check: D1h cyclic_region_case_summary.csv "
            f"has {len(joined)} rows, below minimum {minimum_count}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    proxy_variants = list(config["proxy_variants"])
    threshold_variants = list(config["threshold_variants"])
    targeted = dict(config["targeted_intrusion_families"])
    audit_thresholds = dict(config["audit_thresholds"])
    run_id = str(config["run_id"])
    baseline_proxy_id = "baseline_d1h_proxy"
    baseline_threshold_id = "baseline_d1h_threshold"
    phase_source_status = (
        "explicit_phase_source_available_candidate"
        if detected_phase_columns
        else "explicit_phase_source_missing"
    )

    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = {}
    pair_aggregates: dict[tuple[str, str], dict[str, Any]] = {}
    for proxy_variant in proxy_variants:
        proxy_id = str(proxy_variant["proxy_variant_id"])
        for threshold_variant in threshold_variants:
            threshold_id = str(threshold_variant["threshold_variant_id"])
            cases = [
                compute_case_variant(row, proxy_variant, threshold_variant, targeted)
                for row in joined
            ]
            by_pair[(proxy_id, threshold_id)] = cases
            pair_aggregates[(proxy_id, threshold_id)] = aggregate_cases(
                cases,
                threshold_variant,
            )

    baseline = pair_aggregates[(baseline_proxy_id, baseline_threshold_id)]
    baseline_false_accept = int(d1h_summary["cyclic_false_accept_warning_count"])
    baseline_exclusion_rate = float(d1h_summary["exclusion_success_rate"])
    baseline_stable_count = int(d1h_summary["stable_candidate_cyclic_count"])

    proxy_rows: list[dict[str, Any]] = []
    for proxy_variant in proxy_variants:
        proxy_id = str(proxy_variant["proxy_variant_id"])
        aggregate = pair_aggregates[(proxy_id, baseline_threshold_id)]
        delta_false_accept = (
            aggregate["cyclic_false_accept_warning_count"] - baseline_false_accept
        )
        delta_exclusion = aggregate["exclusion_success_rate"] - baseline_exclusion_rate
        delta_stable = aggregate["stable_candidate_cyclic_count"] - baseline_stable_count
        proxy_warning = (
            abs(delta_false_accept) / max(baseline_false_accept, 1)
            > to_float(audit_thresholds["proxy_dependence_warning_delta_rate"])
            or abs(delta_exclusion)
            > to_float(audit_thresholds["proxy_dependence_warning_delta_rate"])
            or abs(delta_stable) / max(baseline_stable_count, 1)
            > to_float(audit_thresholds["proxy_dependence_warning_delta_rate"])
        )
        stable_loss_warning = (
            aggregate["stable_candidate_loss_rate"]
            > to_float(audit_thresholds["stable_candidate_loss_warning_rate"])
        )
        decision = decision_for_aggregate(
            proxy_warning,
            False,
            aggregate["overstrictness_warning"],
            aggregate["stable_candidate_loss_rate"] if stable_loss_warning else 0.0,
            0,
            phase_source_status,
        )
        proxy_rows.append(
            {
                "run_id": run_id,
                "proxy_variant_id": proxy_id,
                "row_count": aggregate["row_count"],
                "phase_source_label": (
                    "cyclic_phase_proxy"
                    if proxy_id == baseline_proxy_id
                    else proxy_id
                ),
                "cyclic_false_accept_warning_count": aggregate[
                    "cyclic_false_accept_warning_count"
                ],
                "cyclic_false_accept_warning_rate": aggregate[
                    "cyclic_false_accept_warning_rate"
                ],
                "exclusion_success_count": aggregate["exclusion_success_count"],
                "exclusion_failure_count": aggregate["exclusion_failure_count"],
                "exclusion_success_rate": aggregate["exclusion_success_rate"],
                "exclusion_failure_rate": aggregate["exclusion_failure_rate"],
                "stable_candidate_cyclic_count": aggregate[
                    "stable_candidate_cyclic_count"
                ],
                "fragile_candidate_cyclic_count": aggregate[
                    "fragile_candidate_cyclic_count"
                ],
                "stable_candidate_loss_count": aggregate[
                    "stable_candidate_loss_count"
                ],
                "stable_candidate_loss_rate": aggregate["stable_candidate_loss_rate"],
                "mean_cyclic_acceptance_distance": aggregate[
                    "mean_cyclic_acceptance_distance"
                ],
                "mean_warning_count_variant": aggregate["mean_warning_count_variant"],
                "delta_false_accept_count_vs_baseline": delta_false_accept,
                "delta_exclusion_success_rate_vs_baseline": delta_exclusion,
                "delta_stable_candidate_count_vs_baseline": delta_stable,
                "proxy_dependence_warning": proxy_warning,
                "phase_source_validation_status": phase_source_status,
                "decision_status": decision,
                "interpretation_note": (
                    "Proxy variant audit compares synthetic diagnostic cyclic "
                    "behavior against the D1h proxy baseline."
                ),
            }
        )

    threshold_rows: list[dict[str, Any]] = []
    stable_rows: list[dict[str, Any]] = []
    intrusion_rows: list[dict[str, Any]] = []
    for proxy_variant in proxy_variants:
        proxy_id = str(proxy_variant["proxy_variant_id"])
        proxy_baseline = pair_aggregates[(proxy_id, baseline_threshold_id)]
        for threshold_variant in threshold_variants:
            threshold_id = str(threshold_variant["threshold_variant_id"])
            aggregate = pair_aggregates[(proxy_id, threshold_id)]
            cases = by_pair[(proxy_id, threshold_id)]
            threshold_warning = (
                abs(
                    aggregate["cyclic_false_accept_warning_count"]
                    - proxy_baseline["cyclic_false_accept_warning_count"]
                )
                / max(proxy_baseline["cyclic_false_accept_warning_count"], 1)
                > to_float(
                    audit_thresholds["threshold_sensitivity_warning_delta_rate"]
                )
                or abs(
                    aggregate["exclusion_success_rate"]
                    - proxy_baseline["exclusion_success_rate"]
                )
                > to_float(
                    audit_thresholds["threshold_sensitivity_warning_delta_rate"]
                )
            )
            stable_loss_warning = (
                aggregate["stable_candidate_loss_rate"]
                > to_float(audit_thresholds["stable_candidate_loss_warning_rate"])
            )
            decision = decision_for_aggregate(
                False,
                threshold_warning,
                aggregate["overstrictness_warning"],
                aggregate["stable_candidate_loss_rate"]
                if stable_loss_warning
                else 0.0,
                0,
                phase_source_status,
            )
            threshold_rows.append(
                {
                    "run_id": run_id,
                    "proxy_variant_id": proxy_id,
                    "threshold_variant_id": threshold_id,
                    "row_count": aggregate["row_count"],
                    "cyclic_acceptance_distance_threshold": threshold_variant[
                        "cyclic_acceptance_distance_threshold"
                    ],
                    "cyclic_phase_small": threshold_variant["cyclic_phase_small"],
                    "profile_distance_low": threshold_variant["profile_distance_low"],
                    "cyclic_false_accept_warning_count": aggregate[
                        "cyclic_false_accept_warning_count"
                    ],
                    "cyclic_false_accept_warning_rate": aggregate[
                        "cyclic_false_accept_warning_rate"
                    ],
                    "exclusion_success_rate": aggregate["exclusion_success_rate"],
                    "exclusion_failure_rate": aggregate["exclusion_failure_rate"],
                    "stable_candidate_loss_count": aggregate[
                        "stable_candidate_loss_count"
                    ],
                    "stable_candidate_loss_rate": aggregate[
                        "stable_candidate_loss_rate"
                    ],
                    "threshold_sensitivity_warning": threshold_warning,
                    "overstrictness_warning": aggregate["overstrictness_warning"],
                    "decision_status": decision,
                    "interpretation_note": (
                        "Threshold variant audit checks whether the D1h reduction "
                        "persists under configured perturbations."
                    ),
                }
            )
            stable_rows.append(
                {
                    "run_id": run_id,
                    "proxy_variant_id": proxy_id,
                    "threshold_variant_id": threshold_id,
                    "stable_candidate_current_count": aggregate[
                        "stable_candidate_current_count"
                    ],
                    "stable_candidate_cyclic_variant_count": aggregate[
                        "stable_candidate_cyclic_count"
                    ],
                    "fragile_candidate_current_count": aggregate[
                        "fragile_candidate_current_count"
                    ],
                    "fragile_candidate_cyclic_variant_count": aggregate[
                        "fragile_candidate_cyclic_count"
                    ],
                    "current_stable_and_cyclic_stable_count": aggregate[
                        "current_stable_and_cyclic_stable_count"
                    ],
                    "current_stable_but_cyclic_fragile_count": aggregate[
                        "current_stable_but_cyclic_fragile_count"
                    ],
                    "current_fragile_but_cyclic_stable_count": aggregate[
                        "current_fragile_but_cyclic_stable_count"
                    ],
                    "current_fragile_and_cyclic_fragile_count": aggregate[
                        "current_fragile_and_cyclic_fragile_count"
                    ],
                    "stable_candidate_loss_rate": aggregate[
                        "stable_candidate_loss_rate"
                    ],
                    "retained_stable_candidate_rate": aggregate[
                        "retained_stable_candidate_rate"
                    ],
                    "overstrictness_warning": aggregate["overstrictness_warning"],
                    "decision_status": (
                        "cyclic_overstrictness_warning"
                        if aggregate["overstrictness_warning"]
                        else "stable_retention_supported_candidate"
                    ),
                    "interpretation_note": (
                        "Stable-retention audit tracks current stable cases that "
                        "become cyclic-fragile and current fragile cases that "
                        "become cyclic-stable."
                    ),
                }
            )
            intrusion_rows.extend(
                build_intrusion_rows(
                    run_id,
                    proxy_id,
                    threshold_id,
                    cases,
                    audit_thresholds,
                )
            )

    proxy_dependence_warning_count = sum(
        parse_bool(row["proxy_dependence_warning"]) for row in proxy_rows
    )
    threshold_sensitivity_warning_count = sum(
        parse_bool(row["threshold_sensitivity_warning"]) for row in threshold_rows
    )
    overstrictness_warning_count = sum(
        parse_bool(row["overstrictness_warning"]) for row in threshold_rows
    )
    stable_candidate_loss_warning_count = sum(
        to_float(row["stable_candidate_loss_rate"])
        > to_float(audit_thresholds["stable_candidate_loss_warning_rate"])
        for row in stable_rows
    )
    remaining_intrusion_warning_count = sum(
        row["decision_status"] == "remaining_intrusion_warning"
        for row in intrusion_rows
    )

    phase_decision = (
        "explicit_phase_source_available_candidate"
        if detected_phase_columns
        else "explicit_phase_source_needed"
    )
    phase_source_rows = [
        {
            "run_id": run_id,
            "phase_source_label": str(d1h_summary.get("cyclic_phase_source", "")),
            "explicit_phase_source_available": bool(detected_phase_columns),
            "detected_phase_columns": ";".join(detected_phase_columns),
            "proxy_variant_count": len(proxy_variants),
            "baseline_proxy_variant_id": baseline_proxy_id,
            "proxy_dependence_warning_count": proxy_dependence_warning_count,
            "threshold_sensitivity_warning_count": threshold_sensitivity_warning_count,
            "overstrictness_warning_count": overstrictness_warning_count,
            "phase_source_validation_status": phase_source_status,
            "decision_status": phase_decision,
            "interpretation_note": (
                "cyclic_phase_proxy remains diagnostic only; explicit source "
                "availability would not imply physical phase validation."
            ),
        }
    ]

    all_decisions = [
        row["decision_status"]
        for row in proxy_rows + threshold_rows + stable_rows + intrusion_rows
    ] + [phase_decision]
    decision_status_counts = dict(Counter(all_decisions))

    summary = {
        "block_id": config["block_id"],
        "run_id": run_id,
        "input_run_id_d1h": str(d1h_summary.get("run_id", Path(config["input_dir_d1h"]).name)),
        "output_dir": str(output_dir),
        "case_count": len(joined),
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1g_outputs": True,
        "does_not_modify_d1h_outputs": True,
        "does_not_introduce_physical_phase": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "input_consistency_passed": (
            len(joined) >= minimum_count
            and bool(d1f_summary)
            and bool(d1g_summary)
            and bool(d1h_summary)
        ),
        "baseline_cyclic_phase_source": str(d1h_summary.get("cyclic_phase_source", "")),
        "explicit_phase_source_available": bool(detected_phase_columns),
        "detected_phase_columns": detected_phase_columns,
        "proxy_variant_count": len(proxy_variants),
        "threshold_variant_count": len(threshold_variants),
        "baseline_cyclic_false_accept_warning_count": baseline_false_accept,
        "baseline_exclusion_success_rate": baseline_exclusion_rate,
        "baseline_stable_candidate_cyclic_count": baseline_stable_count,
        "proxy_dependence_warning_count": proxy_dependence_warning_count,
        "threshold_sensitivity_warning_count": threshold_sensitivity_warning_count,
        "overstrictness_warning_count": overstrictness_warning_count,
        "stable_candidate_loss_warning_count": stable_candidate_loss_warning_count,
        "remaining_intrusion_warning_count": remaining_intrusion_warning_count,
        "phase_source_validation_status": phase_source_status,
        "dominant_proxy_variant_decision_status": Counter(
            row["decision_status"] for row in proxy_rows
        ).most_common(1)[0][0],
        "dominant_threshold_decision_status": Counter(
            row["decision_status"] for row in threshold_rows
        ).most_common(1)[0][0],
        "mean_delta_false_accept_count_vs_baseline": safe_mean(
            [to_float(row["delta_false_accept_count_vs_baseline"]) for row in proxy_rows]
        ),
        "mean_delta_exclusion_success_rate_vs_baseline": safe_mean(
            [
                to_float(row["delta_exclusion_success_rate_vs_baseline"])
                for row in proxy_rows
            ]
        ),
        "mean_stable_candidate_loss_rate": safe_mean(
            [to_float(row["stable_candidate_loss_rate"]) for row in stable_rows]
        ),
        "decision_status_counts": decision_status_counts,
        "generated_files": OUTPUT_FILES,
        "claim_boundary": config["metadata"]["claim_boundary"],
    }

    write_csv(output_dir / "proxy_variant_summary.csv", proxy_rows, PROXY_FIELDS)
    write_csv(
        output_dir / "threshold_sensitivity_summary.csv",
        threshold_rows,
        THRESHOLD_FIELDS,
    )
    write_csv(output_dir / "stable_retention_summary.csv", stable_rows, STABLE_FIELDS)
    write_csv(
        output_dir / "remaining_intrusion_summary.csv",
        intrusion_rows,
        INTRUSION_FIELDS,
    )
    write_csv(
        output_dir / "phase_source_comparison_summary.csv",
        phase_source_rows,
        PHASE_SOURCE_FIELDS,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / "readout.md", summary)
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        "D1i cyclic-phase source validation and overstrictness audit complete: "
        f"{output_dir}"
    )


if __name__ == "__main__":
    main()
