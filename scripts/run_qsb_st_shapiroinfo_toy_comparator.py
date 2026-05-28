#!/usr/bin/env python3
"""QSB-ST-SHAPIROINFO04 minimal synthetic toy comparator.

This runner reads a YAML-compatible JSON config, computes transparent
synthetic A/B residual diagnostics, and writes a bounded set of run outputs.
It does not read real Shapiro data and does not perform physical validation.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = "data/QSB-ST-SHAPIROINFO/toy_comparator_config.yaml"
COMPONENT_FIELDS = ("timing_s", "phase_rad", "frequency_hz", "fingerprint_score")
A_FIELD_BY_COMPONENT = {
    "timing_s": "arrival_time_s",
    "phase_rad": "phase_rad",
    "frequency_hz": "frequency_shift_hz",
    "fingerprint_score": "fingerprint_score",
}
CSV_FIELDNAMES = [
    "variant_id",
    "variant_name",
    "signal_class",
    "A_timing_s",
    "B_timing_s",
    "corrected_B_timing_s",
    "residual_timing_s",
    "timing_uncertainty_s",
    "residual_phase_rad",
    "phase_uncertainty_rad",
    "residual_frequency_hz",
    "frequency_uncertainty_hz",
    "residual_fingerprint_score",
    "fingerprint_uncertainty",
    "normalized_residual_score",
    "correction_budget_summary",
    "artifact_or_control_explains",
    "reproducible_count",
    "resolution_ok",
    "comparison_stability",
    "residual_status",
    "expected_residual_status",
    "expected_match",
    "warnings",
    "claim_boundary_flag",
]
STATUS_SUMMARY_FIELDNAMES = ["residual_status", "count", "variant_ids"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the QSB-ST-SHAPIROINFO04 synthetic toy comparator."
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Path to the YAML-compatible JSON toy comparator config.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> dict[str, Any]:
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Config must be YAML-compatible JSON parseable by stdlib json: {config_path}"
        ) from exc
    if not isinstance(config, dict):
        raise SystemExit(f"Config root must be an object: {config_path}")
    return config


def as_float(value: Any, field_name: str, warnings: list[str]) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        warnings.append(f"missing_or_non_numeric_{field_name}")
        return 0.0
    if math.isnan(number) or math.isinf(number):
        warnings.append(f"non_finite_{field_name}")
        return 0.0
    return number


def component_value(mapping: dict[str, Any], field_name: str, warnings: list[str]) -> float:
    return as_float(mapping.get(field_name, 0.0), field_name, warnings)


def expected_statuses(raw_expected: Any) -> list[str]:
    if isinstance(raw_expected, list):
        return [str(item) for item in raw_expected]
    if raw_expected is None:
        return []
    return [str(raw_expected)]


def build_correction_summary(correction_applied: dict[str, Any]) -> str:
    labels = []
    for layer in ("known_delay_component", "standard_artifact", "bounded_noise"):
        state = "applied" if bool(correction_applied.get(layer, False)) else "not_applied"
        labels.append(f"{layer}:{state}")
    return ";".join(labels)


def corrected_component_residual(
    variant: dict[str, Any],
    component_name: str,
    warnings: list[str],
) -> tuple[float, float, float]:
    a_reference = variant.get("A_reference", {})
    if not isinstance(a_reference, dict):
        warnings.append("A_reference_not_mapping")
        a_reference = {}

    a_field = A_FIELD_BY_COMPONENT[component_name]
    a_value = as_float(a_reference.get(a_field, 0.0), a_field, warnings)

    component_total = 0.0
    for layer in (
        "known_delay_component",
        "standard_artifact",
        "bounded_noise",
        "candidate_residual",
    ):
        raw_layer = variant.get(layer, {})
        if not isinstance(raw_layer, dict):
            warnings.append(f"{layer}_not_mapping")
            raw_layer = {}
        component_total += component_value(raw_layer, component_name, warnings)

    b_value = a_value + component_total
    corrected_b = b_value
    correction_applied = variant.get("correction_applied", {})
    if not isinstance(correction_applied, dict):
        warnings.append("correction_applied_not_mapping")
        correction_applied = {}

    for layer in ("known_delay_component", "standard_artifact", "bounded_noise"):
        if bool(correction_applied.get(layer, False)):
            raw_layer = variant.get(layer, {})
            if not isinstance(raw_layer, dict):
                raw_layer = {}
            corrected_b -= component_value(raw_layer, component_name, warnings)

    residual = corrected_b - a_value
    return a_value, b_value, residual


def uncertainty_value(
    variant: dict[str, Any],
    component_name: str,
    warnings: list[str],
) -> float:
    uncertainty = variant.get("uncertainty", {})
    if not isinstance(uncertainty, dict):
        warnings.append("uncertainty_not_mapping")
        uncertainty = {}
    value = component_value(uncertainty, component_name, warnings)
    if value <= 0.0:
        warnings.append(f"non_positive_uncertainty_{component_name}")
        return 1.0
    return value


def decide_status(
    max_normalized_residual: float,
    variant: dict[str, Any],
    thresholds: dict[str, Any],
    warnings: list[str],
) -> str:
    control = variant.get("control_assessment", {})
    if not isinstance(control, dict):
        warnings.append("control_assessment_not_mapping")
        control = {}

    resolution_ok = bool(control.get("resolution_ok", False))
    comparison_stability = str(control.get("comparison_stability", "unstable"))
    if not resolution_ok or comparison_stability != "stable":
        warnings.append("comparison_resolution_or_stability_limit")
        return "inconclusive"

    within_limit = as_float(
        thresholds.get("normalized_within_uncertainty_max", 1.0),
        "normalized_within_uncertainty_max",
        warnings,
    )
    if max_normalized_residual <= within_limit:
        return "no_residual"

    if bool(control.get("artifact_or_control_explains", False)):
        return "artifact_likely"

    reproducible_count = int(control.get("reproducible_count", 0))
    candidate_min_repeat_count = int(thresholds.get("candidate_min_repeat_count", 2))
    if reproducible_count >= candidate_min_repeat_count:
        return "candidate_residual"

    warnings.append("residual_unexplained_but_not_reproducible_enough")
    return "inconclusive"


def compute_variant_row(
    variant: dict[str, Any],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    warnings: list[str] = []
    residuals: dict[str, float] = {}
    a_values: dict[str, float] = {}
    b_values: dict[str, float] = {}
    uncertainties: dict[str, float] = {}

    for component_name in COMPONENT_FIELDS:
        a_value, b_value, residual = corrected_component_residual(
            variant, component_name, warnings
        )
        a_values[component_name] = a_value
        b_values[component_name] = b_value
        residuals[component_name] = residual
        uncertainties[component_name] = uncertainty_value(variant, component_name, warnings)

    normalized_components = [
        abs(residuals[name]) / uncertainties[name] for name in COMPONENT_FIELDS
    ]
    normalized_residual_score = max(normalized_components)
    residual_status = decide_status(
        normalized_residual_score, variant, thresholds, warnings
    )

    control = variant.get("control_assessment", {})
    if not isinstance(control, dict):
        control = {}
    correction_applied = variant.get("correction_applied", {})
    if not isinstance(correction_applied, dict):
        correction_applied = {}

    expected = expected_statuses(variant.get("expected_residual_status"))
    expected_match = residual_status in expected

    return {
        "variant_id": str(variant.get("variant_id", "")),
        "variant_name": str(variant.get("variant_name", "")),
        "signal_class": str(variant.get("signal_class", "")),
        "A_timing_s": a_values["timing_s"],
        "B_timing_s": b_values["timing_s"],
        "corrected_B_timing_s": a_values["timing_s"] + residuals["timing_s"],
        "residual_timing_s": residuals["timing_s"],
        "timing_uncertainty_s": uncertainties["timing_s"],
        "residual_phase_rad": residuals["phase_rad"],
        "phase_uncertainty_rad": uncertainties["phase_rad"],
        "residual_frequency_hz": residuals["frequency_hz"],
        "frequency_uncertainty_hz": uncertainties["frequency_hz"],
        "residual_fingerprint_score": residuals["fingerprint_score"],
        "fingerprint_uncertainty": uncertainties["fingerprint_score"],
        "normalized_residual_score": normalized_residual_score,
        "correction_budget_summary": build_correction_summary(correction_applied),
        "artifact_or_control_explains": bool(control.get("artifact_or_control_explains", False)),
        "reproducible_count": int(control.get("reproducible_count", 0)),
        "resolution_ok": bool(control.get("resolution_ok", False)),
        "comparison_stability": str(control.get("comparison_stability", "")),
        "residual_status": residual_status,
        "expected_residual_status": "|".join(expected),
        "expected_match": expected_match,
        "warnings": "|".join(sorted(set(warnings))),
        "claim_boundary_flag": True,
    }


def format_cell(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_cell(row.get(key, "")) for key in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def build_status_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ids_by_status: dict[str, list[str]] = {}
    for row in rows:
        status = str(row["residual_status"])
        ids_by_status.setdefault(status, []).append(str(row["variant_id"]))
    return [
        {
            "residual_status": status,
            "count": len(ids_by_status[status]),
            "variant_ids": "|".join(ids_by_status[status]),
        }
        for status in sorted(ids_by_status)
    ]


def write_readout(path: Path, config: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    status_counts = Counter(str(row["residual_status"]) for row in rows)
    expected_ok = all(bool(row["expected_match"]) for row in rows)
    status_text = ", ".join(f"{status}: {count}" for status, count in sorted(status_counts.items()))
    lines = [
        "# QSB-ST-SHAPIROINFO04 Toy Comparator Minimal Run Readout",
        "",
        "## Befund",
        "",
        "Der synthetische Toy-Comparator wurde auf den konfigurierten V0-V5-Varianten ausgefuehrt.",
        f"Statusverteilung: {status_text}.",
        f"Expected-status check: {'passed' if expected_ok else 'failed'}.",
        "",
        "## Interpretation",
        "",
        "Der Lauf prueft nur, ob die technische Residual-Logik zwischen no_residual, "
        "artifact_likely, inconclusive und candidate_residual unterscheidbar formuliert ist.",
        "",
        "## Hypothese",
        "",
        "Ein spaeter ausgebauter synthetischer Comparator koennte als Vorpruefung fuer "
        "Record-Schema, Korrekturbudget und Kontrollsprache dienen.",
        "",
        "## Offene Luecke",
        "",
        "Keine echten Shapiro-Daten, keine empirische Pruefung, keine physikalische Validierung, "
        "keine Spezifitaet.",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in config.get("claim_boundary", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `toy_comparator_variant_results.csv`",
            "- `toy_comparator_status_summary.csv`",
            "- `summary.json`",
            "- `resolved_config.json`",
            "- `readout.md`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_output_paths_clear(output_dir: Path, output_names: list[str]) -> None:
    existing = [output_dir / name for name in output_names if (output_dir / name).exists()]
    if existing:
        formatted = "\n".join(str(path) for path in existing)
        raise SystemExit(f"Refusing to overwrite existing output files:\n{formatted}")


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    config = load_config(config_path)

    toy_variants = config.get("toy_variants", [])
    if not isinstance(toy_variants, list) or not toy_variants:
        raise SystemExit("Config must contain a non-empty toy_variants list.")

    thresholds = config.get("decision_thresholds", {})
    if not isinstance(thresholds, dict):
        raise SystemExit("decision_thresholds must be a mapping.")

    output_dir = Path(str(config.get("output_dir", "")))
    if not str(output_dir):
        raise SystemExit("Config must define output_dir.")

    output_names = [
        "toy_comparator_variant_results.csv",
        "toy_comparator_status_summary.csv",
        "summary.json",
        "resolved_config.json",
        "readout.md",
    ]
    ensure_output_paths_clear(output_dir, output_names)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = [compute_variant_row(variant, thresholds) for variant in toy_variants]
    status_rows = build_status_summary(rows)
    expected_ok = all(bool(row["expected_match"]) for row in rows)
    all_warnings = sorted(
        {
            warning
            for row in rows
            for warning in str(row.get("warnings", "")).split("|")
            if warning
        }
    )

    write_csv(output_dir / "toy_comparator_variant_results.csv", CSV_FIELDNAMES, rows)
    write_csv(
        output_dir / "toy_comparator_status_summary.csv",
        STATUS_SUMMARY_FIELDNAMES,
        status_rows,
    )
    write_json(output_dir / "resolved_config.json", config)
    summary = {
        "block_id": config.get("block_id"),
        "run_id": config.get("run_id"),
        "config_path": str(config_path),
        "output_dir": str(output_dir),
        "variant_count": len(rows),
        "residual_status_counts": dict(Counter(row["residual_status"] for row in rows)),
        "expected_status_check_passed": expected_ok,
        "warnings": all_warnings,
        "claim_boundary": config.get("claim_boundary", []),
        "limitations": [
            "synthetic toy data only",
            "no real Shapiro data",
            "no empirical claim",
            "no physical validation",
            "no Shapiro modification claim",
        ],
        "output_files": output_names,
    }
    write_json(output_dir / "summary.json", summary)
    write_readout(output_dir / "readout.md", config, rows)

    print(f"wrote_output_dir={output_dir}")
    print(f"variant_count={len(rows)}")
    print(f"expected_status_check_passed={str(expected_ok).lower()}")
    if all_warnings:
        print(f"warnings={'|'.join(all_warnings)}")
    return 0 if expected_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
