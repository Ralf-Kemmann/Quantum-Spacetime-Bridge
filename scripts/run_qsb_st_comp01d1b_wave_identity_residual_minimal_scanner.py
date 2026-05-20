#!/usr/bin/env python3
"""QSB-ST-COMP01-D1b minimal wave identity residual scanner.

This runner is intentionally synthetic and local: it reads a small YAML
configuration, computes transparent diagnostic residual fields, and writes a
bounded set of CSV/JSON/Markdown outputs. It does not read real data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit(
        "PyYAML is required for this scanner. Install PyYAML or run in the "
        "project environment where yaml is available."
    ) from exc


PAIR_FIELDNAMES = [
    "pair_id",
    "wave_id_i",
    "wave_id_j",
    "control_family",
    "control_seed",
    "k_i",
    "k_j",
    "delta_k",
    "relative_k_shift",
    "k_ratio",
    "phase_i",
    "phase_j",
    "relative_phase_drift",
    "phase_gradient_delta",
    "A_i",
    "A_j",
    "B_i",
    "B_j",
    "intercept_i",
    "intercept_j",
    "delta_intercept_ij",
    "intercept_similarity",
    "slope_i",
    "slope_j",
    "delta_slope_ij",
    "slope_similarity",
    "slope_intercept_balance",
    "local_linear_response_overlap",
    "spectral_component",
    "phase_component",
    "local_component",
    "spectral_identity_distance",
    "wave_identity_residual",
    "duplicate_sanity_distance",
    "near_duplicate_decoy_distance",
    "control_reference_ratio",
    "decision_status",
    "warning_flags",
    "interpretation_note",
]

CONTROL_FAMILY_FIELDNAMES = [
    "control_family",
    "pair_count",
    "min_wave_identity_residual",
    "max_wave_identity_residual",
    "mean_wave_identity_residual",
    "decision_statuses",
    "warning_flags",
]

DECISION_FIELDNAMES = [
    "decision_status",
    "count",
    "control_families",
]

NEAR_DUPLICATE_FAMILIES = {
    "small_delta_k_decoy",
    "small_phase_drift_decoy",
    "amplitude_preserved_perturbation",
    "combined_near_duplicate_decoy",
}

CONTROL_FAMILIES = {
    "label_shuffle",
    "kernel_node_label_shuffle_proxy",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the QSB-ST-COMP01-D1b wave identity residual scanner."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1b_wave_identity_residual_minimal_config.yaml",
        help="Path to the D1b YAML config.",
    )
    return parser.parse_args()


def read_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise SystemExit(f"Config must be a YAML mapping: {config_path}")
    return config


def as_float(value: Any, field_name: str, warnings: list[str]) -> float:
    if value is None or value == "":
        warnings.append("missing_value")
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        warnings.append("missing_value")
        return math.nan


def finite_or_zero(value: float, warnings: list[str]) -> float:
    if math.isnan(value) or math.isinf(value):
        warnings.append("missing_value")
        return 0.0
    return value


def wrap_minus_pi_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def similarity_from_delta(delta: float, similarity_scale: float, epsilon: float, warnings: list[str]) -> float:
    scale = abs(similarity_scale)
    if scale <= epsilon:
        warnings.append("near_zero_denominator")
        scale = epsilon
    return 1.0 / (1.0 + abs(delta) / scale)


def normalized_fraction(value: float) -> float:
    return value / (1.0 + value)


def resolve_weights(config: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    raw_weights = config.get("weights", {})
    warnings: list[str] = []
    weights = {
        "spectral_component": float(raw_weights.get("spectral_component", 0.0)),
        "phase_component": float(raw_weights.get("phase_component", 0.0)),
        "local_component": float(raw_weights.get("local_component", 0.0)),
    }
    weight_sum = sum(weights.values())
    if weight_sum <= 0.0:
        warnings.append("weight_sum_not_positive")
        weights = {
            "spectral_component": 1.0 / 3.0,
            "phase_component": 1.0 / 3.0,
            "local_component": 1.0 / 3.0,
        }
        return weights, warnings
    return {key: value / weight_sum for key, value in weights.items()}, warnings


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    return str(value)


def compute_pair_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    normalization = config.get("normalization", {})
    epsilon = float(normalization.get("epsilon", 1.0e-12))
    similarity_scale = float(normalization.get("similarity_scale", 1.0))
    thresholds = config.get("decision_thresholds", {})
    near_zero_residual_max = float(thresholds.get("near_zero_residual_max", 1.0e-9))
    control_mimicry_ratio_warning = float(
        thresholds.get("control_mimicry_ratio_warning", 0.85)
    )
    weights, weight_warnings = resolve_weights(config)

    rows: list[dict[str, Any]] = []
    for pair in config.get("synthetic_wave_pairs", []):
        warnings = list(weight_warnings)
        wave_i = pair.get("wave_i", {})
        wave_j = pair.get("wave_j", {})
        control_family = pair.get("control_family", "")

        k_i = finite_or_zero(as_float(wave_i.get("k"), "k_i", warnings), warnings)
        k_j = finite_or_zero(as_float(wave_j.get("k"), "k_j", warnings), warnings)
        phase_i = finite_or_zero(as_float(wave_i.get("phase"), "phase_i", warnings), warnings)
        phase_j = finite_or_zero(as_float(wave_j.get("phase"), "phase_j", warnings), warnings)
        a_i = finite_or_zero(as_float(wave_i.get("A"), "A_i", warnings), warnings)
        a_j = finite_or_zero(as_float(wave_j.get("A"), "A_j", warnings), warnings)
        b_i = finite_or_zero(as_float(wave_i.get("B"), "B_i", warnings), warnings)
        b_j = finite_or_zero(as_float(wave_j.get("B"), "B_j", warnings), warnings)

        delta_k = abs(k_i - k_j)
        relative_k_shift = delta_k / max(abs(k_i), abs(k_j), epsilon)
        if abs(k_j) <= epsilon:
            k_ratio = None
            warnings.append("k_ratio_undefined")
        else:
            k_ratio = k_i / k_j

        phase_delta_raw = phase_i - phase_j
        phase_delta_wrapped = wrap_minus_pi_pi(phase_delta_raw)
        if abs(phase_delta_wrapped - phase_delta_raw) > epsilon:
            warnings.append("phase_wrapped")
        relative_phase_drift = abs(phase_delta_wrapped)
        phase_gradient_delta = abs((phase_i * k_i) - (phase_j * k_j))

        intercept_i = a_i
        intercept_j = a_j
        delta_intercept_ij = abs(intercept_i - intercept_j)
        slope_i = b_i * k_i
        slope_j = b_j * k_j
        delta_slope_ij = abs(slope_i - slope_j)

        intercept_similarity = similarity_from_delta(
            delta_intercept_ij, similarity_scale, epsilon, warnings
        )
        slope_similarity = similarity_from_delta(
            delta_slope_ij, similarity_scale, epsilon, warnings
        )
        slope_intercept_balance = abs(delta_slope_ij - delta_intercept_ij)
        local_linear_response_overlap = (intercept_similarity + slope_similarity) / 2.0

        spectral_component = relative_k_shift
        phase_component = (
            (relative_phase_drift / math.pi)
            + (phase_gradient_delta / (1.0 + phase_gradient_delta))
        ) / 2.0
        local_component = (
            normalized_fraction(delta_intercept_ij)
            + normalized_fraction(delta_slope_ij)
        ) / 2.0
        spectral_identity_distance = spectral_component
        wave_identity_residual = (
            weights["spectral_component"] * spectral_component
            + weights["phase_component"] * phase_component
            + weights["local_component"] * local_component
        )

        duplicate_sanity_distance = (
            wave_identity_residual if control_family == "exact_duplicate" else None
        )
        near_duplicate_decoy_distance = (
            wave_identity_residual if control_family in NEAR_DUPLICATE_FAMILIES else None
        )

        rows.append(
            {
                "pair_id": pair.get("pair_id", ""),
                "wave_id_i": wave_i.get("wave_id", ""),
                "wave_id_j": wave_j.get("wave_id", ""),
                "control_family": control_family,
                "control_seed": pair.get("control_seed", ""),
                "k_i": k_i,
                "k_j": k_j,
                "delta_k": delta_k,
                "relative_k_shift": relative_k_shift,
                "k_ratio": k_ratio,
                "phase_i": phase_i,
                "phase_j": phase_j,
                "relative_phase_drift": relative_phase_drift,
                "phase_gradient_delta": phase_gradient_delta,
                "A_i": a_i,
                "A_j": a_j,
                "B_i": b_i,
                "B_j": b_j,
                "intercept_i": intercept_i,
                "intercept_j": intercept_j,
                "delta_intercept_ij": delta_intercept_ij,
                "intercept_similarity": intercept_similarity,
                "slope_i": slope_i,
                "slope_j": slope_j,
                "delta_slope_ij": delta_slope_ij,
                "slope_similarity": slope_similarity,
                "slope_intercept_balance": slope_intercept_balance,
                "local_linear_response_overlap": local_linear_response_overlap,
                "spectral_component": spectral_component,
                "phase_component": phase_component,
                "local_component": local_component,
                "spectral_identity_distance": spectral_identity_distance,
                "wave_identity_residual": wave_identity_residual,
                "duplicate_sanity_distance": duplicate_sanity_distance,
                "near_duplicate_decoy_distance": near_duplicate_decoy_distance,
                "control_reference_ratio": None,
                "decision_status": "",
                "warning_flags": sorted(set(warnings)),
                "interpretation_note": "",
            }
        )

    non_control_residuals = [
        row["wave_identity_residual"]
        for row in rows
        if row["control_family"] not in CONTROL_FAMILIES
    ]
    mean_non_control_residual = (
        mean(non_control_residuals) if non_control_residuals else 0.0
    )
    ratio_denominator = max(mean_non_control_residual, epsilon)

    for row in rows:
        control_family = row["control_family"]
        residual = row["wave_identity_residual"]
        if control_family in CONTROL_FAMILIES:
            row["control_reference_ratio"] = residual / ratio_denominator

        if control_family == "exact_duplicate":
            if residual <= near_zero_residual_max:
                row["decision_status"] = "duplicate_sanity_pass"
                row["interpretation_note"] = "Exact duplicate residual is near zero."
            else:
                row["decision_status"] = "duplicate_sanity_fail"
                row["interpretation_note"] = "Exact duplicate residual is not near zero."
        elif control_family in NEAR_DUPLICATE_FAMILIES:
            if residual > near_zero_residual_max:
                row["decision_status"] = "near_duplicate_decoy_detected"
                row["interpretation_note"] = (
                    "Near-duplicate diagnostic difference is detectable."
                )
            else:
                row["decision_status"] = "inconclusive"
                row["interpretation_note"] = (
                    "Near-duplicate residual is not separated from zero."
                )
        elif control_family in CONTROL_FAMILIES:
            ratio = row["control_reference_ratio"] or 0.0
            if ratio >= control_mimicry_ratio_warning:
                row["decision_status"] = "control_mimicry_warning"
                row["interpretation_note"] = (
                    "Control residual is comparable to or stronger than the "
                    "non-control residual reference."
                )
            else:
                row["decision_status"] = "structured_reference_exceeds_tested_controls"
                row["interpretation_note"] = (
                    "Control residual is below the configured mimicry warning ratio."
                )
        else:
            row["decision_status"] = "inconclusive"
            row["interpretation_note"] = "No decision rule matched this control family."

    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fieldnames})


def build_control_family_rows(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        grouped[row["control_family"]].append(row)

    summary_rows: list[dict[str, Any]] = []
    for control_family in sorted(grouped):
        rows = grouped[control_family]
        residuals = [row["wave_identity_residual"] for row in rows]
        statuses = sorted({row["decision_status"] for row in rows})
        warning_flags = sorted(
            {
                warning
                for row in rows
                for warning in row.get("warning_flags", [])
                if warning
            }
        )
        summary_rows.append(
            {
                "control_family": control_family,
                "pair_count": len(rows),
                "min_wave_identity_residual": min(residuals),
                "max_wave_identity_residual": max(residuals),
                "mean_wave_identity_residual": mean(residuals),
                "decision_statuses": ";".join(statuses),
                "warning_flags": ";".join(warning_flags),
            }
        )
    return summary_rows


def build_decision_rows(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    status_counts = Counter(row["decision_status"] for row in pair_rows)
    families_by_status: dict[str, set[str]] = defaultdict(set)
    for row in pair_rows:
        families_by_status[row["decision_status"]].add(row["control_family"])
    return [
        {
            "decision_status": status,
            "count": status_counts[status],
            "control_families": ";".join(sorted(families_by_status[status])),
        }
        for status in sorted(status_counts)
    ]


def build_summary(
    config: dict[str, Any],
    pair_rows: list[dict[str, Any]],
    generated_files: list[str],
) -> dict[str, Any]:
    residuals = [row["wave_identity_residual"] for row in pair_rows]
    decision_status_counts = Counter(row["decision_status"] for row in pair_rows)
    exact_rows = [row for row in pair_rows if row["control_family"] == "exact_duplicate"]
    exact_duplicate_sanity_passed = bool(
        exact_rows and exact_rows[0]["decision_status"] == "duplicate_sanity_pass"
    )

    return {
        "block_id": config.get("block_id", "QSB-ST-COMP01D1B"),
        "run_id": config.get("run_id", "wave_identity_residual_minimal_open"),
        "output_dir": config.get(
            "output_dir",
            "runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open",
        ),
        "pair_count": len(pair_rows),
        "control_families": sorted({row["control_family"] for row in pair_rows}),
        "specificity_established": False,
        "stable_candidate_metrics": [],
        "claim_boundary": (
            "synthetic diagnostic minimal scanner only; wave_identity_residual is "
            "a diagnostic residual, not a physical observable; no physical time, "
            "no Pauli claim, no Lorentzian metric, and no physical Bridge validation."
        ),
        "decision_status_counts": dict(sorted(decision_status_counts.items())),
        "max_wave_identity_residual": max(residuals) if residuals else None,
        "min_wave_identity_residual": min(residuals) if residuals else None,
        "mean_wave_identity_residual": mean(residuals) if residuals else None,
        "exact_duplicate_sanity_passed": exact_duplicate_sanity_passed,
        "control_mimicry_warnings_count": decision_status_counts.get(
            "control_mimicry_warning", 0
        ),
        "generated_files": generated_files,
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# QSB-ST-COMP01-D1b Wave Identity Residual Minimal Scanner Readout",
        "",
        "## Befund",
        "",
        "D1b is a synthetic diagnostic minimal scanner. It computes a transparent "
        "wave_identity_residual for configured synthetic wave-pair families.",
        "",
        f"- pair_count: {summary['pair_count']}",
        f"- specificity_established: {summary['specificity_established']}",
        f"- exact_duplicate_sanity_passed: {summary['exact_duplicate_sanity_passed']}",
        f"- min_wave_identity_residual: {summary['min_wave_identity_residual']}",
        f"- mean_wave_identity_residual: {summary['mean_wave_identity_residual']}",
        f"- max_wave_identity_residual: {summary['max_wave_identity_residual']}",
        f"- control_mimicry_warnings_count: {summary['control_mimicry_warnings_count']}",
        "",
        "## Interpretation",
        "",
        "The wave_identity_residual is a diagnostic residual, not a physical observable. "
        "The exact duplicate sanity check reports whether the configured duplicate "
        "pair stays near zero under the transparent aggregation rule. The "
        "phase_gradient_delta field uses a simple synthetic proxy rule: "
        "abs((phase_i * k_i) - (phase_j * k_j)).",
        "",
        "## Hypothese",
        "",
        "If later controlled runs keep exact duplicates near zero while detecting "
        "near-duplicate decoys, the residual may become useful as a diagnostic "
        "design object for wave identity inspection.",
        "",
        "## Offene Lücke",
        "",
        "This run uses synthetic pairs only. It does not validate a physical Bridge. "
        "It does not make a Pauli claim. It does not derive a Lorentzian metric. "
        "It does not introduce physical time. It does not use real data.",
        "",
        "## Claim Boundary",
        "",
        "- psi is a diagnostic pattern object here, not automatically a physical wavefunction.",
        "- wave_identity_residual is a diagnostic distinguishability construct, not a physical observable by itself.",
        "- wave-Pauli is a heuristic internal analogy only.",
        "- It does not claim fermionic Pauli exclusion.",
        "- It does not invoke quantum spin-statistics.",
        "- It does not assert a physical exclusion principle.",
        "- type-like similarity is not the same as relational identity.",
        "- spectral shift is used here as a diagnostic analogy, not as cosmological redshift.",
        "- phase drift is used here as a structure-internal pattern marker, not as physical time delay.",
        "- tau is not physical time.",
        "- tau is not proper time.",
        "- tau is not a universal clock.",
        "- COMP01-D1b does not attach D(A,B).",
        "- COMP01-D1b does not construct S_rel2.",
        "- COMP01-D1b does not validate a physical Bridge.",
        "- COMP01-D1b does not establish diagnostic specificity yet.",
        "- This is synthetic diagnostic implementation work only.",
        "",
        "## Machine-readable status",
        "",
        "```json",
        json.dumps(
            {
                "block_id": summary["block_id"],
                "run_id": summary["run_id"],
                "specificity_established": summary["specificity_established"],
                "exact_duplicate_sanity_passed": summary[
                    "exact_duplicate_sanity_passed"
                ],
                "control_mimicry_warnings_count": summary[
                    "control_mimicry_warnings_count"
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = read_config(config_path)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    pair_rows = compute_pair_rows(config)
    control_family_rows = build_control_family_rows(pair_rows)
    decision_rows = build_decision_rows(pair_rows)

    generated_files = [
        "summary.json",
        "readout.md",
        "wave_identity_pair_summary.csv",
        "control_family_summary.csv",
        "decision_summary.csv",
        "resolved_config.json",
    ]
    summary = build_summary(config, pair_rows, generated_files)

    write_csv(
        output_dir / "wave_identity_pair_summary.csv",
        pair_rows,
        PAIR_FIELDNAMES,
    )
    write_csv(
        output_dir / "control_family_summary.csv",
        control_family_rows,
        CONTROL_FAMILY_FIELDNAMES,
    )
    write_csv(
        output_dir / "decision_summary.csv",
        decision_rows,
        DECISION_FIELDNAMES,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / "readout.md", summary)

    print(
        "QSB-ST-COMP01D1B minimal scanner complete: "
        f"{len(pair_rows)} pairs, output_dir={output_dir}"
    )


if __name__ == "__main__":
    main()
