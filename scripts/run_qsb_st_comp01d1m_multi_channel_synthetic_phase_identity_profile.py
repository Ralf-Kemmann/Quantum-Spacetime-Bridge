#!/usr/bin/env python3
"""QSB-ST COMP01-D1m multi-channel synthetic phase identity profile runner.

This is a defensive synthetic diagnostic runner. It assembles existing D1j,
D1k, D1l, D1h, and D1f artifacts into a guarded multi-channel profile. It
does not rerun prior blocks and does not treat the profile as physical identity.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "PyYAML is required to read the D1m config. Install or activate the project environment."
    ) from exc


PROFILE_CASE_FIELDS = [
    "case_id",
    "family",
    "variant_id",
    "phase_exposure_score",
    "phase_leakage_flag",
    "residual_mimicry_score",
    "duplicate_sanity_passed",
    "near_duplicate_intrusion_flag",
    "component_ablation_stability_score",
    "shuffled_input_survival_flag",
    "family_blind_survival_flag",
    "threshold_weight_stability_score",
    "channel_specific_separability_score",
    "multi_channel_identity_profile_score",
    "profile_warning_count",
    "profile_decision_label",
    "profile_decision_reason",
    "dominant_channel_id",
    "single_channel_dominance_warning",
    "phase_is_physical",
    "phase_is_synthetic_diagnostic",
    "specificity_established",
]

CHANNEL_FIELDS = [
    "channel_id",
    "channel_name",
    "case_count",
    "available_input_count",
    "missing_input_count",
    "mean_score",
    "min_score",
    "max_score",
    "warning_count",
    "dominance_share",
    "interpretation_boundary",
]

CONTROL_FAMILY_FIELDS = [
    "control_family",
    "case_count",
    "intrusion_count",
    "intrusion_rate",
    "mean_profile_score",
    "warning_count",
    "profile_decision_label",
    "interpretation_boundary",
]

WARNING_FIELDS = [
    "warning_id",
    "warning_label",
    "warning_scope",
    "active_count",
    "active_rate",
    "severity_label",
    "interpretation_boundary",
]

MANDATORY_WARNING_IDS = [
    "input_join_warning",
    "missing_required_input_warning",
    "missing_optional_input_warning",
    "missing_family_or_variant_warning",
    "phase_physical_claim_warning",
    "single_channel_dominance_warning",
    "overclean_result_warning",
    "direct_feature_leakage_warning",
    "construction_feedback_leakage_warning",
    "tautology_warning",
    "construction_dependence_warning",
    "component_ablation_failure_warning",
    "shuffled_input_survival_warning",
    "family_blind_interpretation_warning",
    "near_duplicate_intrusion_warning",
    "residual_mimicry_warning",
    "threshold_weight_instability_warning",
    "profile_aggregate_untrusted_warning",
]

ALLOWED_DECISION_LABELS = {
    "diagnostic_profile_candidate",
    "diagnostic_profile_candidate_with_warnings",
    "untrusted_single_channel_profile",
    "input_incomplete_profile_only",
    "not_interpretable",
}

CHANNELS = [
    ("phase_exposure", "phase exposure channel"),
    ("phase_leakage", "phase leakage channel"),
    ("residual_mimicry", "residual mimicry channel"),
    ("duplicate_sanity", "duplicate sanity channel"),
    ("near_duplicate_control", "near-duplicate control channel"),
    ("component_ablation", "component ablation channel"),
    ("shuffled_input_sanity", "shuffled-input sanity channel"),
    ("family_blind_sanity", "family-blind sanity channel"),
    ("threshold_weight_robustness", "threshold-weight robustness channel"),
    ("channel_specific_separability", "channel-specific separability channel"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the QSB-ST COMP01-D1m multi-channel synthetic phase identity profile."
    )
    parser.add_argument("--config", required=True, help="Path to the D1m YAML config.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config did not parse to a mapping: {path}")
    return data


def read_json(path: Path | None) -> tuple[dict[str, Any], bool]:
    if path is None or not path.exists():
        return {}, False
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle), True


def read_csv_rows(path: Path | None) -> tuple[list[dict[str, str]], list[str], bool]:
    if path is None or not path.exists():
        return [], [], False
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, reader.fieldnames or [], True


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_cell(row.get(field, "")) for field in fields})


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    return str(value)


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n", ""}:
        return False
    return default


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def bounded(value: float | None) -> float | None:
    if value is None:
        return None
    return min(1.0, max(0.0, value))


def mean(values: list[float]) -> float | None:
    clean = [value for value in values if value is not None and not math.isnan(value)]
    if not clean:
        return None
    return sum(clean) / len(clean)


def first_value(row: dict[str, Any], names: list[str], default: str = "") -> str:
    for name in names:
        if name in row and str(row[name]).strip() != "":
            return str(row[name]).strip()
    return default


def index_by_key(rows: list[dict[str, str]], key: str) -> tuple[dict[str, dict[str, str]], bool]:
    if not rows:
        return {}, False
    if key not in rows[0]:
        return {}, False
    indexed = {}
    for row in rows:
        value = row.get(key, "")
        if value:
            indexed[value] = row
    return indexed, True


def fraction_true(rows: list[dict[str, str]], column: str) -> float | None:
    if not rows or column not in rows[0]:
        return None
    values = [safe_bool(row.get(column)) for row in rows]
    if not values:
        return None
    return sum(1 for value in values if value) / len(values)


def count_true(rows: list[dict[str, str]], column: str) -> int:
    if not rows or column not in rows[0]:
        return 0
    return sum(1 for row in rows if safe_bool(row.get(column)))


def field_exists(rows: list[dict[str, str]], field: str) -> bool:
    return bool(rows and field in rows[0])


def numeric_score_from_distance(value: Any) -> float | None:
    number = safe_float(value)
    if number is None:
        return None
    return bounded(1.0 - min(1.0, abs(number)))


def phase_exposure_score(row: dict[str, str]) -> float | None:
    stable_raw = first_value(row, ["stable_candidate_exposed"])
    false_accept_raw = first_value(row, ["false_accept_warning_exposed"])
    intrusion_raw = first_value(row, ["remaining_intrusion_warning"])
    if stable_raw == "" or false_accept_raw == "":
        return None
    stable = safe_bool(stable_raw)
    false_accept = safe_bool(false_accept_raw)
    intrusion = safe_bool(intrusion_raw)
    if stable and not false_accept and not intrusion:
        return 1.0
    if stable:
        return 0.5
    return 0.0


def aggregate_component_ablation_score(rows: list[dict[str, str]]) -> float | None:
    value = fraction_true(rows, "survives_ablation")
    if value is None:
        return None
    return bounded(value)


def aggregate_threshold_score(rows: list[dict[str, str]], case_count: int) -> float | None:
    if not rows:
        return None
    clean_count = 0
    usable_count = 0
    for row in rows:
        false_accepts = safe_float(row.get("false_accept_warning_exposed_count"))
        stable = safe_float(row.get("stable_candidate_exposed_count"))
        intrusions = safe_float(row.get("remaining_intrusion_warning_count"))
        if false_accepts is None or stable is None or intrusions is None:
            continue
        usable_count += 1
        if false_accepts == 0 and intrusions == 0 and int(stable) == case_count:
            clean_count += 1
    if usable_count == 0:
        return None
    return clean_count / usable_count


def artifact_status(key: str, path: Path | None, rows: list[dict[str, str]] | None, json_seen: bool) -> dict[str, Any]:
    exists = bool(path and path.exists())
    status = {
        "path": str(path) if path else "",
        "exists": exists,
    }
    if rows is not None:
        status["row_count"] = len(rows)
    if json_seen:
        status["type"] = "json"
    elif rows is not None:
        status["type"] = "csv"
    else:
        status["type"] = "unknown"
    return status


def build_profile_rows(
    config: dict[str, Any],
    d1k_rows: list[dict[str, str]],
    d1h_map: dict[str, dict[str, str]],
    d1f_map: dict[str, dict[str, str]],
    mismatch_map: dict[str, dict[str, str]],
    d1l_summary: dict[str, Any],
    component_score: float | None,
    shuffled_survival_flag: bool | None,
    family_blind_survival_flag: bool | None,
    threshold_score: float | None,
    global_warnings: dict[str, bool],
    missing_optional_input_warning: bool,
    input_incomplete: bool,
) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    profile = config.get("profile", {})
    phase_is_physical = safe_bool(profile.get("phase_is_physical"), False)
    phase_is_synthetic = safe_bool(profile.get("phase_is_synthetic_diagnostic"), True)
    specificity_established = safe_bool(profile.get("specificity_established"), False)

    case_rows: list[dict[str, Any]] = []
    aggregate_case_flags = {
        "near_duplicate_intrusion_warning": False,
        "residual_mimicry_warning": False,
        "missing_family_or_variant_warning": False,
        "single_channel_dominance_warning": False,
    }

    leakage_flag = any(
        safe_bool(d1l_summary.get(field))
        for field in [
            "direct_feature_leakage_warning",
            "construction_feedback_leakage_warning",
            "tautology_warning",
            "overclean_result_warning",
            "construction_dependence_warning",
            "component_ablation_failure_warning",
        ]
    )

    for d1k in d1k_rows:
        case_id = d1k.get("case_id", "")
        d1h = d1h_map.get(case_id, {})
        d1f = d1f_map.get(case_id, {})
        mismatch = mismatch_map.get(case_id, {})

        family = first_value(
            {**d1f, **d1h, **mismatch},
            ["decoy_family", "null_family", "parameter_sweep_family", "profile_weight_set_id"],
            "unknown",
        )
        variant_id = first_value(
            {**d1f, **d1h},
            ["profile_weight_set_id", "penalty_weight_set_id", "kernel_size_label"],
            "baseline_d1m_profile_v1",
        )
        if family == "unknown" or variant_id == "baseline_d1m_profile_v1":
            aggregate_case_flags["missing_family_or_variant_warning"] = True

        exposure = phase_exposure_score(d1k)
        residual = numeric_score_from_distance(
            first_value({**d1f, **d1h, **d1k}, ["profile_distance_raw", "wave_identity_residual"])
        )
        duplicate_raw = first_value({**d1f, **d1h}, ["exact_duplicate_sanity_passed", "duplicate_sanity_passed"])
        duplicate_passed = safe_bool(duplicate_raw) if duplicate_raw != "" else None

        family_text = " ".join(
            [
                family,
                first_value({**d1f, **d1h, **mismatch}, ["decoy_family"]),
                first_value({**d1f, **d1h, **mismatch}, ["null_family"]),
                first_value(mismatch, ["mismatch_type"]),
            ]
        ).lower()
        near_duplicate_intrusion = (
            any(token in family_text for token in ["near_duplicate", "adversarial", "mimic", "decoy", "intrusion"])
            and exposure is not None
            and exposure >= 0.75
        )
        residual_mimicry_warning = (
            any(token in family_text for token in ["near_duplicate", "adversarial", "mimic", "decoy"])
            and residual is not None
            and residual >= 0.80
        )
        aggregate_case_flags["near_duplicate_intrusion_warning"] |= near_duplicate_intrusion
        aggregate_case_flags["residual_mimicry_warning"] |= residual_mimicry_warning

        numeric_channels = {
            "phase_exposure": exposure,
            "residual_mimicry": residual,
            "component_ablation": component_score,
            "threshold_weight_robustness": threshold_score,
        }
        available_scores = [value for value in numeric_channels.values() if value is not None]
        separability = mean(available_scores)
        if separability is not None:
            numeric_channels["channel_specific_separability"] = separability
        profile_score_inputs = [value for value in numeric_channels.values() if value is not None]
        if leakage_flag and profile_score_inputs:
            profile_score_inputs.append(0.0)
        multi_channel_score = mean(profile_score_inputs)

        positive_sum = sum(value for value in numeric_channels.values() if value is not None and value > 0)
        dominant_channel_id = ""
        dominance_share = 0.0
        if positive_sum > 0:
            dominant_channel_id, dominant_value = max(
                ((name, value) for name, value in numeric_channels.items() if value is not None),
                key=lambda item: item[1],
            )
            dominance_share = dominant_value / positive_sum if positive_sum else 0.0
        single_channel_warning = dominance_share >= 0.80
        aggregate_case_flags["single_channel_dominance_warning"] |= single_channel_warning

        warning_booleans = {
            **global_warnings,
            "missing_optional_input_warning": missing_optional_input_warning,
            "missing_family_or_variant_warning": family == "unknown",
            "phase_physical_claim_warning": phase_is_physical,
            "single_channel_dominance_warning": single_channel_warning,
            "near_duplicate_intrusion_warning": near_duplicate_intrusion,
            "residual_mimicry_warning": residual_mimicry_warning,
        }
        profile_warning_count = sum(1 for active in warning_booleans.values() if active)

        if input_incomplete and not d1k_rows:
            decision_label = "not_interpretable"
            decision_reason = "required case-level input is unavailable"
        elif input_incomplete:
            decision_label = "input_incomplete_profile_only"
            decision_reason = "case-level profile is warning-qualified by incomplete inputs"
        elif single_channel_warning:
            decision_label = "untrusted_single_channel_profile"
            decision_reason = "profile is dominated by one channel"
        elif profile_warning_count > 0:
            decision_label = "diagnostic_profile_candidate_with_warnings"
            decision_reason = "profile assembled with active audit warnings"
        else:
            decision_label = "diagnostic_profile_candidate"
            decision_reason = "profile assembled without active warning flags"
        if decision_label not in ALLOWED_DECISION_LABELS:
            decision_label = "not_interpretable"

        case_rows.append(
            {
                "case_id": case_id,
                "family": family,
                "variant_id": variant_id,
                "phase_exposure_score": exposure,
                "phase_leakage_flag": leakage_flag,
                "residual_mimicry_score": residual,
                "duplicate_sanity_passed": duplicate_passed,
                "near_duplicate_intrusion_flag": near_duplicate_intrusion,
                "component_ablation_stability_score": component_score,
                "shuffled_input_survival_flag": shuffled_survival_flag,
                "family_blind_survival_flag": family_blind_survival_flag,
                "threshold_weight_stability_score": threshold_score,
                "channel_specific_separability_score": separability,
                "multi_channel_identity_profile_score": multi_channel_score,
                "profile_warning_count": profile_warning_count,
                "profile_decision_label": decision_label,
                "profile_decision_reason": decision_reason,
                "dominant_channel_id": dominant_channel_id,
                "single_channel_dominance_warning": single_channel_warning,
                "phase_is_physical": phase_is_physical,
                "phase_is_synthetic_diagnostic": phase_is_synthetic,
                "specificity_established": specificity_established,
            }
        )

    return case_rows, aggregate_case_flags


def summarize_channel(
    channel_id: str,
    channel_name: str,
    rows: list[dict[str, Any]],
    score_field: str | None,
    warning_field: str | None,
    interpretation_boundary: str,
) -> dict[str, Any]:
    scores = []
    available = 0
    for row in rows:
        value = safe_float(row.get(score_field)) if score_field else None
        if value is not None:
            available += 1
            scores.append(value)
    warning_count = 0
    if warning_field:
        warning_count = sum(1 for row in rows if safe_bool(row.get(warning_field)))
    mean_score = mean(scores)
    dominance_share = ""
    if channel_id == "phase_exposure" and rows:
        dominance_share = mean([1.0 if row.get("dominant_channel_id") == "phase_exposure" else 0.0 for row in rows])
    return {
        "channel_id": channel_id,
        "channel_name": channel_name,
        "case_count": len(rows),
        "available_input_count": available,
        "missing_input_count": max(0, len(rows) - available),
        "mean_score": mean_score,
        "min_score": min(scores) if scores else None,
        "max_score": max(scores) if scores else None,
        "warning_count": warning_count,
        "dominance_share": dominance_share,
        "interpretation_boundary": interpretation_boundary,
    }


def build_channel_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mapping = {
        "phase_exposure": ("phase_exposure_score", None),
        "phase_leakage": (None, "phase_leakage_flag"),
        "residual_mimicry": ("residual_mimicry_score", None),
        "duplicate_sanity": (None, None),
        "near_duplicate_control": (None, "near_duplicate_intrusion_flag"),
        "component_ablation": ("component_ablation_stability_score", None),
        "shuffled_input_sanity": (None, "shuffled_input_survival_flag"),
        "family_blind_sanity": (None, "family_blind_survival_flag"),
        "threshold_weight_robustness": ("threshold_weight_stability_score", None),
        "channel_specific_separability": ("channel_specific_separability_score", None),
    }
    boundary = "synthetic diagnostic channel; not physical identity evidence"
    return [
        summarize_channel(channel_id, channel_name, rows, *mapping[channel_id], boundary)
        for channel_id, channel_name in CHANNELS
    ]


def build_control_family_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("family") or "unknown")].append(row)
    summaries = []
    for family, group in sorted(grouped.items()):
        intrusion_count = sum(1 for row in group if safe_bool(row.get("near_duplicate_intrusion_flag")))
        scores = [safe_float(row.get("multi_channel_identity_profile_score")) for row in group]
        scores = [score for score in scores if score is not None]
        labels = Counter(str(row.get("profile_decision_label", "")) for row in group)
        summaries.append(
            {
                "control_family": family,
                "case_count": len(group),
                "intrusion_count": intrusion_count,
                "intrusion_rate": intrusion_count / len(group) if group else None,
                "mean_profile_score": mean(scores),
                "warning_count": sum(int(row.get("profile_warning_count") or 0) for row in group),
                "profile_decision_label": labels.most_common(1)[0][0] if labels else "not_interpretable",
                "interpretation_boundary": "control-family aggregate; not a physical population claim",
            }
        )
    if not summaries:
        summaries.append(
            {
                "control_family": "unknown",
                "case_count": 0,
                "intrusion_count": 0,
                "intrusion_rate": "",
                "mean_profile_score": "",
                "warning_count": 0,
                "profile_decision_label": "not_interpretable",
                "interpretation_boundary": "no case-level control-family rows available",
            }
        )
    return summaries


def build_warning_summary(rows: list[dict[str, Any]], aggregate_warnings: dict[str, bool]) -> list[dict[str, Any]]:
    count = len(rows)
    summaries = []
    for warning_id in MANDATORY_WARNING_IDS:
        if warning_id in {
            "single_channel_dominance_warning",
            "near_duplicate_intrusion_warning",
            "residual_mimicry_warning",
        }:
            field = (
                "single_channel_dominance_warning"
                if warning_id == "single_channel_dominance_warning"
                else "near_duplicate_intrusion_flag"
                if warning_id == "near_duplicate_intrusion_warning"
                else None
            )
            if field:
                active_count = sum(1 for row in rows if safe_bool(row.get(field)))
            else:
                active_count = 0
                if rows:
                    active_count = sum(1 for row in rows if safe_float(row.get("residual_mimicry_score")) is not None)
                    active_count = active_count if aggregate_warnings.get(warning_id, False) else 0
        else:
            active = aggregate_warnings.get(warning_id, False)
            active_count = count if active and count else int(active)
        active_rate = active_count / count if count else float(active_count)
        summaries.append(
            {
                "warning_id": warning_id,
                "warning_label": warning_id,
                "warning_scope": "case" if count else "aggregate",
                "active_count": active_count,
                "active_rate": active_rate,
                "severity_label": "warning" if active_count else "info",
                "interpretation_boundary": "warning flag qualifies diagnostic interpretation only",
            }
        )
    return summaries


def write_readout(
    path: Path,
    summary: dict[str, Any],
    channel_rows: list[dict[str, Any]],
    warning_rows: list[dict[str, Any]],
    output_files: list[str],
) -> None:
    active_warnings = [row["warning_id"] for row in warning_rows if int(row["active_count"]) > 0]
    channel_lines = [
        f"- {row['channel_id']}: mean_score={format_cell(row['mean_score'])}, warning_count={row['warning_count']}"
        for row in channel_rows
    ]
    warning_lines = [f"- {warning}" for warning in active_warnings] or ["- no active warning flags"]
    file_lines = [f"- {name}" for name in output_files]
    text = "\n".join(
        [
            "# QSB-ST COMP01-D1m Multi-Channel Synthetic Phase Identity Profile — Readout",
            "",
            "## 1. Purpose",
            "This readout documents a synthetic diagnostic runner only. It assembles D1j/D1k/D1l-derived artifacts into a guarded multi-channel profile and does not make a physical-model validation claim.",
            "",
            "## 2. Inputs",
            f"- input artifacts inspected: {len(summary['input_artifacts'])}",
            f"- missing_required_input_warning: {str(summary['missing_required_input_warning']).lower()}",
            f"- missing_optional_input_warning: {str(summary['missing_optional_input_warning']).lower()}",
            "",
            "## 3. Join status",
            f"- case_count: {summary['case_count']}",
            f"- joined_case_count: {summary['joined_case_count']}",
            f"- input_join_warning: {str(summary['input_join_warning']).lower()}",
            "",
            "## 4. Channel summary",
            *channel_lines,
            "",
            "## 5. Warning summary",
            *warning_lines,
            "",
            "## 6. Befund",
            "D1m produced a first guarded multi-channel synthetic diagnostic profile from available case-level and aggregate audit artifacts. Active warnings are reported rather than hidden.",
            "",
            "## 7. Interpretation",
            "The profile is warning-qualified if warnings are active. It is not independent physical evidence, not a physical phase result, not a physical wavefunction result, and not a physical spacetime geometry result.",
            "",
            "## 8. Hypothese",
            "A multi-feature synthetic phase identity profile may be more robust than a single residual or a single exposed-phase score for same-type but not-same relational wave cases.",
            "",
            "## 9. Offene Lücke",
            "- no real data",
            "- no physical-model validation",
            "- no physical phase",
            "- no physical wavefunction",
            "- no physical spacetime geometry",
            "- no diagnostic specificity",
            "- no Bridge confirmation",
            "- Mastermind/Knuth/manifold remain parked",
            "",
            "## 10. Claim Boundary",
            "- specificity_established: false",
            "- phase_is_physical: false",
            "- phase_is_synthetic_diagnostic: true",
            "- Mastermind status: parked_not_implemented",
            "- Knuth status: parked_not_implemented",
            "- manifold status: parked_not_implemented",
            "",
            "## 11. Files created",
            *file_lines,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = repo_root()
    config_path = resolve_path(root, args.config)
    if config_path is None:
        raise SystemExit("Config path is required.")
    config = read_yaml(config_path)

    input_paths = config.get("input_paths", {})
    resolved = {key: resolve_path(root, value) for key, value in input_paths.items()}

    d1j_summary, d1j_seen = read_json(resolved.get("d1j_summary"))
    d1k_summary, d1k_seen = read_json(resolved.get("d1k_summary"))
    d1l_summary, d1l_seen = read_json(resolved.get("d1l_summary"))

    d1k_rows, d1k_fields, d1k_case_seen = read_csv_rows(resolved.get("d1k_case_profile"))
    leakage_rows, _, leakage_seen = read_csv_rows(resolved.get("d1l_leakage_taxonomy"))
    construction_rows, _, construction_seen = read_csv_rows(resolved.get("d1l_construction_variants"))
    ablation_rows, _, ablation_seen = read_csv_rows(resolved.get("d1l_component_ablation"))
    shuffled_rows, _, shuffled_seen = read_csv_rows(resolved.get("d1l_shuffled_input"))
    family_blind_rows, _, family_blind_seen = read_csv_rows(resolved.get("d1l_family_blind"))
    threshold_rows, _, threshold_seen = read_csv_rows(resolved.get("d1l_threshold_weight_sweep"))
    mismatch_rows, _, mismatch_seen = read_csv_rows(resolved.get("d1l_proxy_exposed_mismatch"))
    d1h_rows, _, d1h_seen = read_csv_rows(resolved.get("d1h_cyclic_case_summary"))
    d1f_rows, _, d1f_seen = read_csv_rows(resolved.get("d1f_case_profile_summary"))

    primary_key = str(config.get("join", {}).get("primary_key", "case_id"))
    d1k_map, d1k_has_key = index_by_key(d1k_rows, primary_key)
    d1h_map, d1h_has_key = index_by_key(d1h_rows, primary_key)
    d1f_map, d1f_has_key = index_by_key(d1f_rows, primary_key)
    mismatch_map, mismatch_has_key = index_by_key(mismatch_rows, primary_key)

    missing_required_input_warning = not d1k_case_seen or not d1l_seen
    missing_optional_input_warning = not all(
        [
            d1j_seen,
            d1k_seen,
            leakage_seen,
            construction_seen,
            ablation_seen,
            shuffled_seen,
            family_blind_seen,
            threshold_seen,
            mismatch_seen,
            d1h_seen,
            d1f_seen,
        ]
    )
    input_join_warning = False
    if d1k_case_seen and not d1k_has_key:
        input_join_warning = True
        missing_required_input_warning = True
    for seen, has_key in [(d1h_seen, d1h_has_key), (d1f_seen, d1f_has_key), (mismatch_seen, mismatch_has_key)]:
        if seen and not has_key:
            input_join_warning = True
            missing_optional_input_warning = True

    case_count = int(
        safe_float(d1l_summary.get("case_count"))
        or safe_float(d1k_summary.get("case_count"))
        or len(d1k_rows)
        or 0
    )
    joined_case_count = len(d1k_map) if d1k_has_key else 0

    component_score = aggregate_component_ablation_score(ablation_rows)
    shuffled_survival_rate = fraction_true(shuffled_rows, "survives_shuffle")
    shuffled_survival_flag = None if shuffled_survival_rate is None else shuffled_survival_rate >= 0.95
    family_blind_rate = fraction_true(family_blind_rows, "survives_family_blindness")
    family_blind_survival_flag = None if family_blind_rate is None else family_blind_rate > 0
    threshold_score = aggregate_threshold_score(threshold_rows, case_count)

    direct_feature = safe_bool(d1l_summary.get("direct_feature_leakage_warning"))
    construction_feedback = safe_bool(d1l_summary.get("construction_feedback_leakage_warning"))
    tautology = safe_bool(d1l_summary.get("tautology_warning"))
    overclean = safe_bool(d1l_summary.get("overclean_result_warning"))
    construction_dependence = safe_bool(d1l_summary.get("construction_dependence_warning"))
    component_ablation_failure = safe_bool(d1l_summary.get("component_ablation_failure_warning"))
    threshold_instability = False
    if threshold_rows:
        false_accept_counts = {row.get("false_accept_warning_exposed_count", "") for row in threshold_rows}
        stable_counts = {row.get("stable_candidate_exposed_count", "") for row in threshold_rows}
        threshold_instability = len(false_accept_counts) > 1 or len(stable_counts) > 1

    global_warnings = {
        "input_join_warning": input_join_warning,
        "missing_required_input_warning": missing_required_input_warning,
        "missing_optional_input_warning": missing_optional_input_warning,
        "phase_physical_claim_warning": safe_bool(config.get("profile", {}).get("phase_is_physical"), False),
        "overclean_result_warning": overclean,
        "direct_feature_leakage_warning": direct_feature,
        "construction_feedback_leakage_warning": construction_feedback,
        "tautology_warning": tautology,
        "construction_dependence_warning": construction_dependence,
        "component_ablation_failure_warning": component_ablation_failure,
        "shuffled_input_survival_warning": bool(shuffled_survival_flag),
        "family_blind_interpretation_warning": bool(family_blind_survival_flag),
        "threshold_weight_instability_warning": threshold_instability,
        "profile_aggregate_untrusted_warning": bool(
            overclean and (direct_feature or construction_feedback or tautology or construction_dependence)
        ),
    }

    input_incomplete = missing_required_input_warning or input_join_warning
    profile_source_rows = list(d1k_map.values()) if d1k_has_key else []
    profile_rows, case_flags = build_profile_rows(
        config=config,
        d1k_rows=profile_source_rows,
        d1h_map=d1h_map,
        d1f_map=d1f_map,
        mismatch_map=mismatch_map if mismatch_has_key else {},
        d1l_summary=d1l_summary,
        component_score=component_score,
        shuffled_survival_flag=shuffled_survival_flag,
        family_blind_survival_flag=family_blind_survival_flag,
        threshold_score=threshold_score,
        global_warnings=global_warnings,
        missing_optional_input_warning=missing_optional_input_warning,
        input_incomplete=input_incomplete,
    )
    global_warnings.update(case_flags)
    warning_rows = build_warning_summary(profile_rows, global_warnings)
    channel_rows = build_channel_summary(profile_rows)
    control_rows = build_control_family_summary(profile_rows)

    decision_counts = Counter(str(row.get("profile_decision_label")) for row in profile_rows)
    active_warning_count = sum(1 for row in warning_rows if int(row["active_count"]) > 0)
    single_channel_dominance_warning = global_warnings.get("single_channel_dominance_warning", False)

    output_dir = resolve_path(root, config.get("output_dir"))
    if output_dir is None:
        raise SystemExit("Config output_dir is required.")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_names = config.get("output_files", {})
    output_files = {
        "summary_json": output_names.get("summary_json", "summary.json"),
        "readout_md": output_names.get("readout_md", "readout.md"),
        "profile_case_summary_csv": output_names.get("profile_case_summary_csv", "profile_case_summary.csv"),
        "channel_summary_csv": output_names.get("channel_summary_csv", "channel_summary.csv"),
        "control_family_summary_csv": output_names.get("control_family_summary_csv", "control_family_summary.csv"),
        "warning_taxonomy_summary_csv": output_names.get("warning_taxonomy_summary_csv", "warning_taxonomy_summary.csv"),
        "resolved_config_json": output_names.get("resolved_config_json", "resolved_config.json"),
    }

    input_artifacts = {
        "d1j_summary": artifact_status("d1j_summary", resolved.get("d1j_summary"), None, d1j_seen),
        "d1k_summary": artifact_status("d1k_summary", resolved.get("d1k_summary"), None, d1k_seen),
        "d1k_case_profile": artifact_status("d1k_case_profile", resolved.get("d1k_case_profile"), d1k_rows, False),
        "d1l_summary": artifact_status("d1l_summary", resolved.get("d1l_summary"), None, d1l_seen),
        "d1l_leakage_taxonomy": artifact_status("d1l_leakage_taxonomy", resolved.get("d1l_leakage_taxonomy"), leakage_rows, False),
        "d1l_construction_variants": artifact_status("d1l_construction_variants", resolved.get("d1l_construction_variants"), construction_rows, False),
        "d1l_component_ablation": artifact_status("d1l_component_ablation", resolved.get("d1l_component_ablation"), ablation_rows, False),
        "d1l_shuffled_input": artifact_status("d1l_shuffled_input", resolved.get("d1l_shuffled_input"), shuffled_rows, False),
        "d1l_family_blind": artifact_status("d1l_family_blind", resolved.get("d1l_family_blind"), family_blind_rows, False),
        "d1l_threshold_weight_sweep": artifact_status("d1l_threshold_weight_sweep", resolved.get("d1l_threshold_weight_sweep"), threshold_rows, False),
        "d1l_proxy_exposed_mismatch": artifact_status("d1l_proxy_exposed_mismatch", resolved.get("d1l_proxy_exposed_mismatch"), mismatch_rows, False),
        "d1h_cyclic_case_summary": artifact_status("d1h_cyclic_case_summary", resolved.get("d1h_cyclic_case_summary"), d1h_rows, False),
        "d1f_case_profile_summary": artifact_status("d1f_case_profile_summary", resolved.get("d1f_case_profile_summary"), d1f_rows, False),
    }

    summary = {
        "block_id": config.get("block_id", "QSB-ST-COMP01D1M"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_artifacts": input_artifacts,
        "case_count": case_count,
        "joined_case_count": joined_case_count,
        "missing_required_input_warning": missing_required_input_warning,
        "missing_optional_input_warning": missing_optional_input_warning,
        "input_join_warning": input_join_warning,
        "specificity_established": False,
        "phase_is_physical": False,
        "phase_is_synthetic_diagnostic": True,
        "profile_channel_count": len(CHANNELS),
        "active_warning_count": active_warning_count,
        "single_channel_dominance_warning": single_channel_dominance_warning,
        "profile_decision_label_counts": dict(decision_counts),
        "mastermind_status": config.get("profile", {}).get("mastermind_status", "parked_not_implemented"),
        "knuth_status": config.get("profile", {}).get("knuth_status", "parked_not_implemented"),
        "manifold_status": config.get("profile", {}).get("manifold_status", "parked_not_implemented"),
        "runner_scope": "synthetic diagnostic multi-channel profile skeleton",
        "claim_boundary": config.get("claim_boundary", {}),
        "output_files": {key: str(output_dir / name) for key, name in output_files.items()},
    }

    write_csv(output_dir / output_files["profile_case_summary_csv"], PROFILE_CASE_FIELDS, profile_rows)
    write_csv(output_dir / output_files["channel_summary_csv"], CHANNEL_FIELDS, channel_rows)
    write_csv(output_dir / output_files["control_family_summary_csv"], CONTROL_FAMILY_FIELDS, control_rows)
    write_csv(output_dir / output_files["warning_taxonomy_summary_csv"], WARNING_FIELDS, warning_rows)
    (output_dir / output_files["summary_json"]).write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    resolved_config = {
        "config": config,
        "config_path": str(config_path),
        "repo_root": str(root),
        "resolved_input_paths": {key: str(value) if value else "" for key, value in resolved.items()},
    }
    (output_dir / output_files["resolved_config_json"]).write_text(
        json.dumps(resolved_config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readout(
        output_dir / output_files["readout_md"],
        summary=summary,
        channel_rows=channel_rows,
        warning_rows=warning_rows,
        output_files=[name for name in output_files.values()],
    )

    print("QSB-ST COMP01-D1m profile run complete")
    print(f"output_dir: {output_dir}")
    print(f"case_count: {case_count}")
    print(f"joined_case_count: {joined_case_count}")
    print(f"active_warning_count: {active_warning_count}")
    print(f"profile_decision_label_counts: {dict(decision_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
