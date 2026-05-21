#!/usr/bin/env python3
"""QSB-ST COMP01-D1n output audit for existing D1m artifacts.

The runner reads D1m outputs, classifies warning origin/granularity, audits
channel and dominance semantics, and writes D1n review artifacts. It does not
modify D1m outputs and does not rerun D1m.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "PyYAML is required to read the D1n config. Activate the project environment or install PyYAML."
    ) from exc


WARNING_ORIGIN_FIELDS = [
    "warning_id",
    "warning_label",
    "warning_origin",
    "warning_granularity",
    "active_count",
    "affected_case_count",
    "affected_family_count",
    "inherited_from",
    "severity_label",
    "interpretation_boundary",
]

CHANNEL_SEMANTICS_FIELDS = [
    "channel_id",
    "channel_name",
    "score_granularity",
    "warning_granularity",
    "mean_score_present",
    "warning_count_interpretation",
    "broadcast_warning_flag",
    "interpretation_role",
    "refinement_needed",
    "recommended_change",
]

DOMINANCE_SEMANTICS_FIELDS = [
    "dominance_field",
    "current_meaning",
    "possible_confusion",
    "recommended_clarification",
    "runner_change_needed",
    "readout_change_needed",
]

D1L_INHERITED_WARNINGS = {
    "overclean_result_warning",
    "direct_feature_leakage_warning",
    "construction_feedback_leakage_warning",
    "tautology_warning",
    "construction_dependence_warning",
    "component_ablation_failure_warning",
}

D1M_CASE_OR_FAMILY_WARNINGS = {
    "near_duplicate_intrusion_warning",
    "residual_mimicry_warning",
}

D1M_INTERPRETATION_POLICY_WARNINGS = {
    "family_blind_interpretation_warning",
    "threshold_weight_instability_warning",
    "single_channel_dominance_warning",
    "profile_aggregate_untrusted_warning",
}

D1M_INPUT_JOIN_WARNINGS = {
    "input_join_warning",
    "missing_required_input_warning",
    "missing_optional_input_warning",
    "missing_family_or_variant_warning",
}

CLAIM_BOUNDARY_WARNINGS = {
    "phase_physical_claim_warning",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit existing QSB-ST COMP01-D1m output semantics without rerunning D1m."
    )
    parser.add_argument("--config", required=True, help="Path to the D1n YAML config.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing config file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Config did not parse to a mapping: {path}")
    return data


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), reader.fieldnames or []


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
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def safe_int(value: Any) -> int:
    number = safe_float(value)
    if number is None:
        return 0
    return int(number)


def artifact_status(path: Path) -> dict[str, Any]:
    status: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }
    if path.exists() and path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            status["row_count"] = sum(1 for _ in reader)
            status["field_count"] = len(reader.fieldnames or [])
    return status


def ensure_inputs_exist(input_paths: dict[str, Path]) -> None:
    missing = [str(path) for path in input_paths.values() if not path.exists()]
    if missing:
        joined = "\n".join(missing)
        raise SystemExit(f"Missing required input artifacts; D1m will not be rerun:\n{joined}")


def active_family_count(
    warning_id: str,
    profile_rows: list[dict[str, str]],
    control_rows: list[dict[str, str]],
    active_count: int,
) -> int:
    if active_count <= 0:
        return 0
    if warning_id == "near_duplicate_intrusion_warning":
        families = {
            row.get("family", "unknown")
            for row in profile_rows
            if safe_bool(row.get("near_duplicate_intrusion_flag"))
        }
        return len(families)
    if warning_id == "single_channel_dominance_warning":
        families = {
            row.get("family", "unknown")
            for row in profile_rows
            if safe_bool(row.get("single_channel_dominance_warning"))
        }
        return len(families)
    return len(control_rows) if control_rows else 0


def classify_warning_origin(warning_id: str) -> tuple[str, str, str]:
    if warning_id in D1L_INHERITED_WARNINGS:
        return "inherited_d1l_global", "global_broadcast", "D1l"
    if warning_id in D1M_CASE_OR_FAMILY_WARNINGS:
        return "d1m_case_or_family_logic", "case_level", "D1m"
    if warning_id in D1M_INTERPRETATION_POLICY_WARNINGS:
        if warning_id == "single_channel_dominance_warning":
            return "d1m_interpretation_policy", "channel_level", "D1m"
        return "d1m_interpretation_policy", "global_broadcast", "D1m"
    if warning_id in D1M_INPUT_JOIN_WARNINGS:
        return "d1m_input_join", "input_level", "D1m"
    if warning_id in CLAIM_BOUNDARY_WARNINGS:
        return "claim_boundary_guard", "claim_boundary", "D1m"
    return "d1m_output_warning", "channel_level", "D1m"


def build_warning_origin_rows(
    warning_rows: list[dict[str, str]],
    profile_rows: list[dict[str, str]],
    control_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    rows = []
    for warning in warning_rows:
        warning_id = warning.get("warning_id", "")
        origin, granularity, inherited_from = classify_warning_origin(warning_id)
        active_count = safe_int(warning.get("active_count"))
        rows.append(
            {
                "warning_id": warning_id,
                "warning_label": warning.get("warning_label", warning_id),
                "warning_origin": origin,
                "warning_granularity": granularity,
                "active_count": active_count,
                "affected_case_count": active_count,
                "affected_family_count": active_family_count(warning_id, profile_rows, control_rows, active_count),
                "inherited_from": inherited_from,
                "severity_label": warning.get("severity_label", "warning" if active_count else "info"),
                "interpretation_boundary": "Warning qualifies D1m output semantics only; no physical claim.",
            }
        )
    return rows


def channel_role(channel_id: str) -> str:
    roles = {
        "phase_exposure": "signal_channel",
        "phase_leakage": "qualifier_channel",
        "residual_mimicry": "ambiguity_channel",
        "duplicate_sanity": "control_channel",
        "near_duplicate_control": "ambiguity_control_channel",
        "component_ablation": "construction_sensitivity_channel",
        "shuffled_input_sanity": "control_channel",
        "family_blind_sanity": "qualifier_channel",
        "threshold_weight_robustness": "robustness_channel",
        "channel_specific_separability": "summary_channel",
    }
    return roles.get(channel_id, "diagnostic_channel")


def channel_score_granularity(channel_id: str, mean_score_present: bool) -> str:
    if channel_id in {"phase_leakage", "duplicate_sanity", "near_duplicate_control", "shuffled_input_sanity", "family_blind_sanity"}:
        return "none_or_aggregate" if not mean_score_present else "aggregate_or_case"
    if channel_id in {"component_ablation", "threshold_weight_robustness"}:
        return "aggregate_broadcast"
    if channel_id in {"phase_exposure", "residual_mimicry"}:
        return "case_level" if mean_score_present else "missing"
    if channel_id == "channel_specific_separability":
        return "derived_summary"
    return "unknown"


def channel_warning_granularity(channel_id: str, warning_count: int, case_count: int) -> str:
    if warning_count == 0:
        return "none"
    if warning_count == case_count:
        if channel_id in {"phase_leakage", "family_blind_sanity"}:
            return "global_broadcast"
        return "case_or_global_broadcast"
    if channel_id == "near_duplicate_control":
        return "case_or_family_level"
    return "channel_level"


def build_channel_semantics_rows(channel_rows: list[dict[str, str]], case_count: int) -> list[dict[str, Any]]:
    rows = []
    for channel in channel_rows:
        channel_id = channel.get("channel_id", "")
        mean_score = channel.get("mean_score", "")
        mean_score_present = str(mean_score).strip() != ""
        warning_count = safe_int(channel.get("warning_count"))
        broadcast_warning = warning_count == case_count and warning_count > 0
        score_granularity = channel_score_granularity(channel_id, mean_score_present)
        warning_granularity = channel_warning_granularity(channel_id, warning_count, case_count)
        role = channel_role(channel_id)
        refinement_needed = False
        recommended_change = "No immediate schema change required; keep interpretation boundary visible."

        if channel_id == "phase_exposure":
            dominance_share = safe_float(channel.get("dominance_share"))
            if safe_float(mean_score) == 1.0 and (dominance_share is None or dominance_share >= 0.9):
                refinement_needed = True
                recommended_change = "Clarify dominant-channel reporting and emit dominance share per row."
        elif channel_id == "phase_leakage":
            refinement_needed = broadcast_warning
            recommended_change = "Mark as global qualifier when warning_count is broadcast to all cases."
        elif channel_id == "near_duplicate_control":
            refinement_needed = warning_count > 0
            recommended_change = "Separate case-level near-duplicate warning from family-level ambiguity summary."
        elif channel_id == "component_ablation":
            refinement_needed = True
            recommended_change = "Mark aggregate-broadcast score origin explicitly."
        elif channel_id == "family_blind_sanity":
            refinement_needed = broadcast_warning
            recommended_change = "Separate family-blind survival flag from warning semantics."
        elif channel_id == "threshold_weight_robustness":
            refinement_needed = True
            recommended_change = "Expose threshold instability reason and score component count."
        elif channel_id == "residual_mimicry":
            refinement_needed = warning_count > 0
            recommended_change = "Document residual mimicry score source and ambiguity threshold."
        elif channel_id == "channel_specific_separability":
            refinement_needed = True
            recommended_change = "Clarify that this is a derived summary channel, not an independent channel."

        rows.append(
            {
                "channel_id": channel_id,
                "channel_name": channel.get("channel_name", channel_id),
                "score_granularity": score_granularity,
                "warning_granularity": warning_granularity,
                "mean_score_present": mean_score_present,
                "warning_count_interpretation": (
                    "broadcast to all cases"
                    if broadcast_warning
                    else "case or channel count"
                    if warning_count
                    else "no warning count"
                ),
                "broadcast_warning_flag": broadcast_warning,
                "interpretation_role": role,
                "refinement_needed": refinement_needed,
                "recommended_change": recommended_change,
            }
        )
    return rows


def build_dominance_rows(summary: dict[str, Any], profile_rows: list[dict[str, str]], channel_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    dominant_counts = Counter(row.get("dominant_channel_id", "") for row in profile_rows)
    dominant_text = ", ".join(f"{key}:{value}" for key, value in sorted(dominant_counts.items())) or "unavailable"
    single_channel_warning = safe_bool(summary.get("single_channel_dominance_warning"))
    channel_dominance_share = ""
    for row in channel_rows:
        if row.get("channel_id") == "phase_exposure":
            channel_dominance_share = row.get("dominance_share", "")
            break
    clarification = (
        "dominant_channel_id identifies the largest contributing numeric channel; "
        "it does not by itself imply single-channel failure. "
        "single_channel_dominance_warning is threshold-based."
    )
    return [
        {
            "dominance_field": "dominant_channel_id",
            "current_meaning": f"Largest numeric channel per profile row; observed counts: {dominant_text}.",
            "possible_confusion": "May be read as a failure condition even when no dominance warning is active.",
            "recommended_clarification": clarification,
            "runner_change_needed": True,
            "readout_change_needed": True,
        },
        {
            "dominance_field": "dominance_share",
            "current_meaning": "Internal or aggregate share used to compare contribution size.",
            "possible_confusion": "Not emitted per case in D1m profile_case_summary.csv.",
            "recommended_clarification": "Emit dominant_channel_share per row in a future refinement.",
            "runner_change_needed": True,
            "readout_change_needed": True,
        },
        {
            "dominance_field": "single_channel_dominance_warning",
            "current_meaning": f"Threshold-based warning; current summary value is {str(single_channel_warning).lower()}.",
            "possible_confusion": "May be conflated with dominant_channel_id.",
            "recommended_clarification": "State that this warning depends on a threshold, not just the channel label.",
            "runner_change_needed": False,
            "readout_change_needed": True,
        },
        {
            "dominance_field": "single_channel_dominance_threshold",
            "current_meaning": "Threshold exists in logic but is not emitted as a summary field.",
            "possible_confusion": "Reviewer cannot see why a dominant channel did not trigger the warning.",
            "recommended_clarification": "Emit single_channel_dominance_threshold in summary.json.",
            "runner_change_needed": True,
            "readout_change_needed": True,
        },
        {
            "dominance_field": "channel_summary.dominance_share",
            "current_meaning": f"Channel-level dominance share field; phase_exposure value is {channel_dominance_share or 'blank'}.",
            "possible_confusion": "May look like a profile failure without the warning threshold context.",
            "recommended_clarification": "Add dominance_interpretation_note to channel summary/readout.",
            "runner_change_needed": True,
            "readout_change_needed": True,
        },
        {
            "dominance_field": "profile_case_summary.dominant_channel_id",
            "current_meaning": "Per-row label for largest numeric contributor.",
            "possible_confusion": "May be mistaken for a decision label.",
            "recommended_clarification": "Add dominance_warning_reason when single_channel_dominance_warning is active.",
            "runner_change_needed": True,
            "readout_change_needed": True,
        },
    ]


def write_output_tracking_policy(path: Path) -> str:
    recommendation = "keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default"
    text = "\n".join(
        [
            "# QSB-ST COMP01-D1n Output Tracking Policy",
            "",
            "This policy note covers D1m/D1n run outputs only. It does not change repository state.",
            "",
            "## Options",
            "",
            "A. Do not track `runs/` outputs; keep them reproducible from config plus runner.",
            "",
            "B. Track only `summary.json` and `readout.md` with `git add -f`.",
            "",
            "C. Track the full D1m/D1n run output set with `git add -f`.",
            "",
            "D. Track no `runs/` outputs but create a docs-side output digest.",
            "",
            "## Conservative Recommendation",
            "",
            "- Keep config plus runner and result notes tracked.",
            "- Do not force-add full `runs/` outputs by default.",
            "- For public review or reproducibility bundles, create a docs-side digest or force-add selected summary/readout outputs with an explicit commit message.",
            "- Do not silently rely on ignored outputs.",
            "",
            "## Claim Boundary",
            "",
            "This is an output tracking policy note, not a physical-model validation step.",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")
    return recommendation


def write_readout(
    path: Path,
    summary: dict[str, Any],
    warning_origin_rows: list[dict[str, Any]],
    channel_rows: list[dict[str, Any]],
    dominance_rows: list[dict[str, Any]],
    output_files: dict[str, str],
) -> None:
    origin_counts = summary["warning_origin_counts"]
    granularity_counts = summary["warning_granularity_counts"]
    origin_lines = [f"- {key}: {value}" for key, value in sorted(origin_counts.items())]
    granularity_lines = [f"- {key}: {value}" for key, value in sorted(granularity_counts.items())]
    channel_lines = [
        f"- {row['channel_id']}: role={row['interpretation_role']}, refinement_needed={format_cell(row['refinement_needed'])}"
        for row in channel_rows
    ]
    dominance_lines = [
        f"- {row['dominance_field']}: runner_change_needed={format_cell(row['runner_change_needed'])}, readout_change_needed={format_cell(row['readout_change_needed'])}"
        for row in dominance_rows
    ]
    file_lines = [f"- {name}" for name in output_files.values()]
    text = "\n".join(
        [
            "# QSB-ST COMP01-D1n D1m Output Audit and Runner Refinement \u2014 Readout",
            "",
            "## 1. Purpose",
            "D1n audits existing D1m outputs. D1n does not modify D1m and does not rerun D1m.",
            "",
            "## 2. Inputs",
            f"- input artifacts inspected: {len(summary['input_artifacts'])}",
            f"- D1m profile rows: {summary['d1m_case_count']}",
            "",
            "## 3. D1m anchor values",
            f"- d1m_case_count: {summary['d1m_case_count']}",
            f"- d1m_joined_case_count: {summary['d1m_joined_case_count']}",
            f"- d1m_active_warning_count: {summary['d1m_active_warning_count']}",
            f"- d1m_warning_qualified_case_count: {summary['d1m_warning_qualified_case_count']}",
            f"- d1m_single_channel_dominance_warning: {str(summary['d1m_single_channel_dominance_warning']).lower()}",
            "",
            "## 4. Warning-origin summary",
            *origin_lines,
            *granularity_lines,
            "",
            "## 5. Channel-semantics summary",
            *channel_lines,
            "",
            "## 6. Dominance-semantics summary",
            *dominance_lines,
            "",
            "## 7. Output-tracking recommendation",
            f"- {summary['output_tracking_recommendation']}",
            "",
            "## 8. Befund",
            "D1n produced warning-origin, channel-semantics, dominance-semantics, and output-tracking review artifacts from the existing D1m outputs. Warning-qualified output is not failure; it is a review signal.",
            "",
            "## 9. Interpretation",
            "The high warning load is partly a semantics/audit object. D1n separates inherited/global warnings, case/family warnings, interpretation-policy warnings, input warnings, and claim-boundary guards.",
            "",
            "## 10. Hypothese",
            "A D1m refinement can become clearer if warning origin, warning granularity, and dominance semantics are made explicit before any scoring changes.",
            "",
            "## 11. Offene L\u00fccke",
            "- no real data",
            "- no physical-model validation",
            "- no physical phase",
            "- no physical wavefunction",
            "- no physical spacetime geometry",
            "- no diagnostic specificity",
            "- no Bridge confirmation",
            "- Mastermind/Knuth/manifold remain parked",
            "",
            "## 12. Claim Boundary",
            "- specificity_established: false",
            "- phase_is_physical: false",
            "- phase_is_synthetic_diagnostic: true",
            "- Mastermind status: parked_not_implemented",
            "- Knuth status: parked_not_implemented",
            "- manifold status: parked_not_implemented",
            "",
            "## 13. Files created",
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

    input_paths = {
        key: resolve_path(root, value)
        for key, value in (config.get("input_paths") or {}).items()
    }
    resolved_inputs = {key: value for key, value in input_paths.items() if value is not None}
    ensure_inputs_exist(resolved_inputs)

    d1m_summary = read_json(resolved_inputs["d1m_summary"])
    d1m_readout = resolved_inputs["d1m_readout"].read_text(encoding="utf-8")
    profile_rows, _ = read_csv_rows(resolved_inputs["d1m_profile_case_summary"])
    channel_rows, _ = read_csv_rows(resolved_inputs["d1m_channel_summary"])
    control_rows, _ = read_csv_rows(resolved_inputs["d1m_control_family_summary"])
    warning_rows, _ = read_csv_rows(resolved_inputs["d1m_warning_taxonomy_summary"])
    _ = d1m_readout  # explicit read; content is inspected but not transformed.

    case_count = int(d1m_summary.get("case_count", len(profile_rows)))
    joined_case_count = int(d1m_summary.get("joined_case_count", len(profile_rows)))
    active_warning_count = int(d1m_summary.get("active_warning_count", 0))
    warning_qualified_case_count = sum(
        1
        for row in profile_rows
        if row.get("profile_decision_label") == "diagnostic_profile_candidate_with_warnings"
    )
    single_channel_warning = safe_bool(d1m_summary.get("single_channel_dominance_warning"))

    warning_origin_rows = build_warning_origin_rows(warning_rows, profile_rows, control_rows)
    channel_semantics_rows = build_channel_semantics_rows(channel_rows, case_count)
    dominance_semantics_rows = build_dominance_rows(d1m_summary, profile_rows, channel_rows)

    output_dir = resolve_path(root, config.get("output_dir"))
    if output_dir is None:
        raise SystemExit("Config output_dir is required.")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_config = config.get("output_files") or {}
    output_files = {
        "summary_json": output_config.get("summary_json", "summary.json"),
        "readout_md": output_config.get("readout_md", "readout.md"),
        "warning_origin_summary_csv": output_config.get("warning_origin_summary_csv", "warning_origin_summary.csv"),
        "channel_semantics_audit_csv": output_config.get("channel_semantics_audit_csv", "channel_semantics_audit.csv"),
        "dominance_semantics_audit_csv": output_config.get("dominance_semantics_audit_csv", "dominance_semantics_audit.csv"),
        "output_tracking_policy_md": output_config.get("output_tracking_policy_md", "output_tracking_policy.md"),
        "resolved_config_json": output_config.get("resolved_config_json", "resolved_config.json"),
    }

    write_csv(output_dir / output_files["warning_origin_summary_csv"], WARNING_ORIGIN_FIELDS, warning_origin_rows)
    write_csv(output_dir / output_files["channel_semantics_audit_csv"], CHANNEL_SEMANTICS_FIELDS, channel_semantics_rows)
    write_csv(output_dir / output_files["dominance_semantics_audit_csv"], DOMINANCE_SEMANTICS_FIELDS, dominance_semantics_rows)
    output_tracking_recommendation = write_output_tracking_policy(output_dir / output_files["output_tracking_policy_md"])

    warning_origin_counts = Counter(row["warning_origin"] for row in warning_origin_rows)
    warning_granularity_counts = Counter(row["warning_granularity"] for row in warning_origin_rows)
    broadcast_warning_count = sum(1 for row in warning_origin_rows if row["warning_granularity"] == "global_broadcast" and int(row["active_count"]) > 0)
    case_level_warning_count = sum(1 for row in warning_origin_rows if row["warning_granularity"] == "case_level" and int(row["active_count"]) > 0)

    artifact_map = {key: artifact_status(path) for key, path in resolved_inputs.items()}
    claim_boundary = dict(config.get("claim_boundary") or {})
    summary = {
        "block_id": config.get("block_id", "QSB-ST-COMP01D1N"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_artifacts": artifact_map,
        "d1m_case_count": case_count,
        "d1m_joined_case_count": joined_case_count,
        "d1m_active_warning_count": active_warning_count,
        "d1m_warning_qualified_case_count": warning_qualified_case_count,
        "d1m_single_channel_dominance_warning": single_channel_warning,
        "warning_origin_counts": dict(warning_origin_counts),
        "warning_granularity_counts": dict(warning_granularity_counts),
        "broadcast_warning_count": broadcast_warning_count,
        "case_level_warning_count": case_level_warning_count,
        "channel_semantics_rows": len(channel_semantics_rows),
        "dominance_audit_rows": len(dominance_semantics_rows),
        "output_tracking_recommendation": output_tracking_recommendation,
        "specificity_established": False,
        "phase_is_physical": False,
        "phase_is_synthetic_diagnostic": True,
        "mastermind_status": claim_boundary.get("mastermind_status", "parked_not_implemented"),
        "knuth_status": claim_boundary.get("knuth_status", "parked_not_implemented"),
        "manifold_status": claim_boundary.get("manifold_status", "parked_not_implemented"),
        "runner_scope": "synthetic diagnostic D1m output audit and runner refinement review",
        "claim_boundary": claim_boundary,
        "output_files": {key: str(output_dir / name) for key, name in output_files.items()},
    }

    (output_dir / output_files["summary_json"]).write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    resolved_config = {
        "config": config,
        "config_path": str(config_path),
        "repo_root": str(root),
        "resolved_input_paths": {key: str(value) for key, value in resolved_inputs.items()},
    }
    (output_dir / output_files["resolved_config_json"]).write_text(
        json.dumps(resolved_config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    write_readout(
        output_dir / output_files["readout_md"],
        summary=summary,
        warning_origin_rows=warning_origin_rows,
        channel_rows=channel_semantics_rows,
        dominance_rows=dominance_semantics_rows,
        output_files=output_files,
    )

    print("QSB-ST COMP01-D1n output audit complete")
    print(f"output_dir: {output_dir}")
    print(f"d1m_case_count: {case_count}")
    print(f"d1m_active_warning_count: {active_warning_count}")
    print(f"warning_origin_rows: {len(warning_origin_rows)}")
    print(f"channel_semantics_rows: {len(channel_semantics_rows)}")
    print(f"dominance_audit_rows: {len(dominance_semantics_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
