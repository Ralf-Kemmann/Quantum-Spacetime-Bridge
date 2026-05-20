#!/usr/bin/env python3
"""QSB-ST-COMP01-D1d synthetic feature-manifold degeneracy audit."""

from __future__ import annotations

import argparse
import csv
import itertools
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
        "PyYAML is required for this audit. Install PyYAML or run in the "
        "project environment where yaml is available."
    ) from exc


COORDINATES = [
    "k",
    "A",
    "B",
    "R",
    "phi_wrapped",
    "slope",
    "intercept",
    "amplitude_balance",
    "normalized_amplitude_balance",
    "local_response_norm",
]

NEAR_DUPLICATE_FAMILIES = {
    "simple_near_duplicate",
    "small_delta_k_decoy",
    "small_phase_drift_decoy",
    "amplitude_preserved_perturbation",
    "combined_near_duplicate_decoy",
    "adversarial_near_duplicate",
    "residual_matched_decoy",
}

CONTROL_TERMS = ("control", "shuffle", "decoy")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run D1d manifold degeneracy audit.")
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1d_wave_identity_manifold_degeneracy_audit_config.yaml",
    )
    return parser.parse_args()


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a mapping: {path}")
    return data


def wrap_minus_pi_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def as_float(value: Any, warnings: list[str]) -> float:
    if value is None or value == "":
        warnings.append("missing_value")
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        warnings.append("missing_value")
        return 0.0


def std(values: list[float]) -> float:
    if not values:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((value - m) ** 2 for value in values) / len(values))


def pearson(xs: list[float], ys: list[float], epsilon: float) -> float | None:
    sx = std(xs)
    sy = std(ys)
    if sx <= epsilon or sy <= epsilon:
        return None
    mx = mean(xs)
    my = mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)
    return cov / (sx * sy)


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    return str(value)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fieldnames})


def build_wave_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    epsilon = float(config["normalization"]["epsilon"])
    rows = []
    for wave in config["synthetic_waves"]:
        warnings: list[str] = []
        k = as_float(wave.get("k"), warnings)
        a = as_float(wave.get("A"), warnings)
        b = as_float(wave.get("B"), warnings)
        r = math.sqrt(a * a + b * b)
        phi_base = math.atan2(b, a)
        phi = as_float(wave.get("phase_override", phi_base), warnings)
        phi_wrapped = wrap_minus_pi_pi(phi)
        if abs(phi - phi_wrapped) > epsilon:
            warnings.append("phi_wrapped")
        slope = b * k
        intercept = a
        amplitude_balance = a - b
        denom = max(abs(a) + abs(b), epsilon)
        if denom <= epsilon:
            warnings.append("near_zero_denominator")
        normalized_amplitude_balance = amplitude_balance / denom
        local_response_norm = math.sqrt(intercept * intercept + slope * slope)
        rows.append(
            {
                "wave_id": wave["wave_id"],
                "family": wave.get("family", ""),
                "k": k,
                "A": a,
                "B": b,
                "R": r,
                "phi": phi,
                "phi_wrapped": phi_wrapped,
                "slope": slope,
                "intercept": intercept,
                "amplitude_balance": amplitude_balance,
                "normalized_amplitude_balance": normalized_amplitude_balance,
                "local_response_norm": local_response_norm,
                "warning_flags": sorted(set(warnings)),
            }
        )
    return rows


def build_coordinate_audit_rows(wave_rows: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    norm = config["normalization"]
    threshold = float(norm["near_constant_std_threshold"])
    corr_threshold = float(norm["coordinate_dependency_correlation_threshold"])
    epsilon = float(norm["epsilon"])
    rows = []
    values_by_coord = {coord: [float(row[coord]) for row in wave_rows] for coord in COORDINATES}
    for coord in COORDINATES:
        values = values_by_coord[coord]
        coord_std = std(values)
        unique_values = len({round(value, 12) for value in values})
        near_constant = coord_std <= threshold
        collapse = unique_values <= 2 or near_constant
        dependency_warning = False
        dependency_partner = ""
        for other in COORDINATES:
            if other == coord:
                continue
            corr = pearson(values, values_by_coord[other], epsilon)
            if corr is not None and abs(corr) >= corr_threshold:
                dependency_warning = True
                dependency_partner = other
                break
        warnings = []
        if near_constant:
            warnings.append("near_constant_coordinate")
        if collapse:
            warnings.append("normalization_collapse_warning")
        if dependency_warning:
            warnings.append("coordinate_dependency_warning")
        rows.append(
            {
                "coordinate_name": coord,
                "coordinate_min": min(values),
                "coordinate_max": max(values),
                "coordinate_mean": mean(values),
                "coordinate_std": coord_std,
                "unique_value_count": unique_values,
                "near_constant_flag": near_constant,
                "normalization_collapse_warning": collapse,
                "coordinate_dependency_warning": dependency_warning,
                "dependency_partner": dependency_partner,
                "warning_flags": sorted(warnings),
            }
        )
    return rows


def vector_distance(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def residual_proxy(row: dict[str, Any], epsilon: float) -> float:
    return mean(
        [
            row["delta_k"] / max(1.0, row["delta_k"], epsilon),
            row["wrapped_delta_phi_abs"] / math.pi,
            row["delta_slope"] / (1.0 + row["delta_slope"]),
            row["delta_intercept"] / (1.0 + row["delta_intercept"]),
        ]
    )


def build_pair_specs(config: dict[str, Any], wave_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specs = []
    seen_ids = set()
    for pair in config["pair_definitions"]:
        specs.append({**pair, "source": "configured_pair"})
        seen_ids.add(pair["pair_id"])
    if config.get("audit", {}).get("include_all_pairwise_wave_pairs", False):
        waves = [row["wave_id"] for row in wave_rows]
        for i, j in itertools.combinations(waves, 2):
            pair_id = f"all_pairwise__{i}__{j}"
            if pair_id in seen_ids:
                continue
            specs.append(
                {
                    "pair_id": pair_id,
                    "control_family": "all_pairwise",
                    "wave_id_i": i,
                    "wave_id_j": j,
                    "source": "all_pairwise",
                }
            )
    return specs


def build_pair_rows(
    config: dict[str, Any],
    wave_rows: list[dict[str, Any]],
    coordinate_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    norm = config["normalization"]
    epsilon = float(norm["epsilon"])
    collision_threshold = float(norm["collision_distance_threshold"])
    residual_threshold = float(norm["residual_collision_threshold"])
    wave_by_id = {row["wave_id"]: row for row in wave_rows}
    collapsed_coordinate_count = sum(1 for row in coordinate_rows if row["near_constant_flag"])
    manifold_richness_score = (len(COORDINATES) - collapsed_coordinate_count) / len(COORDINATES)
    specs = build_pair_specs(config, wave_rows)
    rows = []
    for spec in specs:
        wi = wave_by_id[spec["wave_id_i"]]
        wj = wave_by_id[spec["wave_id_j"]]
        angle_delta = wrap_minus_pi_pi(wi["phi_wrapped"] - wj["phi_wrapped"])
        row = {
            "pair_id": spec["pair_id"],
            "source": spec.get("source", "configured_pair"),
            "wave_id_i": wi["wave_id"],
            "wave_id_j": wj["wave_id"],
            "control_family": spec.get("control_family", ""),
            "delta_k": abs(wi["k"] - wj["k"]),
            "delta_R": abs(wi["R"] - wj["R"]),
            "wrapped_delta_phi_abs": abs(angle_delta),
            "cos_delta_phi": math.cos(angle_delta),
            "sin_delta_phi": math.sin(angle_delta),
            "delta_A": abs(wi["A"] - wj["A"]),
            "delta_B": abs(wi["B"] - wj["B"]),
            "delta_slope": abs(wi["slope"] - wj["slope"]),
            "delta_intercept": abs(wi["intercept"] - wj["intercept"]),
            "delta_balance": abs(wi["normalized_amplitude_balance"] - wj["normalized_amplitude_balance"]),
            "manifold_richness_score": manifold_richness_score,
            "collapsed_coordinate_count": collapsed_coordinate_count,
        }
        row["delta_vector_norm"] = vector_distance(
            [
                row["delta_k"],
                row["delta_R"],
                row["wrapped_delta_phi_abs"],
                row["delta_A"],
                row["delta_B"],
                row["delta_slope"],
                row["delta_intercept"],
                row["delta_balance"],
            ]
        )
        row["profile_distance"] = row["delta_vector_norm"]
        row["wave_identity_residual"] = residual_proxy(row, epsilon)
        row["profile_collision"] = (
            row["control_family"] != "exact_duplicate"
            and row["profile_distance"] <= collision_threshold
        )
        row["delta_vector_collision"] = (
            row["control_family"] != "exact_duplicate"
            and row["delta_vector_norm"] <= collision_threshold
        )
        row["residual_collision"] = False
        row["collision_cluster_id"] = ""
        row["ambiguity_warning"] = False
        row["decision_status"] = "inconclusive"
        row["warning_flags"] = ["phi_wrapped"]
        row["interpretation_note"] = ""
        rows.append(row)

    exact_residuals = [
        row["wave_identity_residual"]
        for row in rows
        if row["control_family"] == "exact_duplicate"
    ]
    exact_residual = exact_residuals[0] if exact_residuals else 0.0
    cluster_counter = 1
    for row in rows:
        if row["control_family"] != "exact_duplicate" and abs(row["wave_identity_residual"] - exact_residual) <= residual_threshold:
            row["residual_collision"] = True
        if row["profile_collision"] or row["residual_collision"] or row["delta_vector_collision"]:
            row["ambiguity_warning"] = True
            row["collision_cluster_id"] = f"collision_cluster_{cluster_counter:03d}"
            cluster_counter += 1
    for i, first in enumerate(rows):
        for second in rows[i + 1 :]:
            if first["pair_id"] == second["pair_id"]:
                continue
            residual_match = abs(first["wave_identity_residual"] - second["wave_identity_residual"]) <= residual_threshold
            vector_match = abs(first["delta_vector_norm"] - second["delta_vector_norm"]) <= collision_threshold
            if residual_match:
                first["residual_collision"] = True
                second["residual_collision"] = True
            if vector_match:
                first["delta_vector_collision"] = True
                second["delta_vector_collision"] = True
            if residual_match or vector_match:
                cluster_id = first["collision_cluster_id"] or second["collision_cluster_id"] or f"collision_cluster_{cluster_counter:03d}"
                if not first["collision_cluster_id"] and not second["collision_cluster_id"]:
                    cluster_counter += 1
                first["collision_cluster_id"] = cluster_id
                second["collision_cluster_id"] = cluster_id
    add_control_flags_and_decisions(rows, collision_threshold)
    return rows


def add_control_flags_and_decisions(rows: list[dict[str, Any]], collision_threshold: float) -> None:
    near_distances = [
        row["profile_distance"]
        for row in rows
        if row["source"] == "configured_pair" and row["control_family"] in NEAR_DUPLICATE_FAMILIES
    ]
    near_max = max(near_distances) if near_distances else 0.0
    combined = next((row for row in rows if row["control_family"] == "combined_near_duplicate_decoy"), None)
    combined_profile = combined["profile_distance"] if combined else None
    combined_residual = combined["wave_identity_residual"] if combined else None
    for row in rows:
        family = row["control_family"]
        is_control_like = any(term in family for term in CONTROL_TERMS)
        row["control_profile_mimicry_warning"] = bool(
            is_control_like and row["profile_distance"] <= near_max
        )
        row["residual_matched_profile_warning"] = bool(
            family == "residual_matched_decoy"
            and combined_profile is not None
            and combined_residual is not None
            and (
                abs(row["profile_distance"] - combined_profile) <= 0.05
                or abs(row["wave_identity_residual"] - combined_residual) <= 0.02
            )
        )
        row["adversarial_profile_warning"] = bool(
            family == "adversarial_near_duplicate" and row["profile_distance"] <= near_max
        )
        if row["control_profile_mimicry_warning"] or row["residual_matched_profile_warning"] or row["adversarial_profile_warning"]:
            row["ambiguity_warning"] = True
        warnings = set(row["warning_flags"])
        for key in [
            "profile_collision",
            "residual_collision",
            "delta_vector_collision",
            "ambiguity_warning",
            "control_profile_mimicry_warning",
            "residual_matched_profile_warning",
            "adversarial_profile_warning",
        ]:
            if row.get(key):
                warnings.add(key)
        row["warning_flags"] = sorted(warnings)

        if family == "exact_duplicate":
            if row["profile_distance"] <= collision_threshold:
                row["decision_status"] = "duplicate_sanity_pass"
                row["interpretation_note"] = "Exact duplicate profile distance is near zero."
            else:
                row["decision_status"] = "failed_sanity_check"
                row["interpretation_note"] = "Exact duplicate profile distance is not near zero."
        elif row["profile_collision"]:
            row["decision_status"] = "profile_collision_warning"
            row["interpretation_note"] = "Profile collision detected."
        elif row["residual_collision"]:
            row["decision_status"] = "residual_collision_warning"
            row["interpretation_note"] = "Residual collision detected."
        elif row["delta_vector_collision"]:
            row["decision_status"] = "delta_vector_collision_warning"
            row["interpretation_note"] = "Delta-vector collision detected."
        elif row["control_profile_mimicry_warning"]:
            row["decision_status"] = "control_profile_mimicry_warning"
            row["interpretation_note"] = "Control profile overlaps near-duplicate range."
        elif row["collapsed_coordinate_count"] > 0:
            row["decision_status"] = "coordinate_collapse_warning"
            row["interpretation_note"] = "One or more coordinates are collapsed."
        else:
            row["decision_status"] = "manifold_audit_pass_minimal"
            row["interpretation_note"] = "No collision warning triggered in this minimal audit."


def build_collision_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for ctype in ["profile_collision", "residual_collision", "delta_vector_collision", "ambiguity_warning"]:
            if row.get(ctype):
                cluster = row["collision_cluster_id"] or f"{ctype}_unclustered"
                groups[(ctype, cluster)].append(row)
    if not groups:
        return [
            {
                "collision_type": "none",
                "collision_cluster_id": "",
                "pair_ids": "",
                "wave_ids": "",
                "control_families": "",
                "min_distance": 0.0,
                "max_distance": 0.0,
                "mean_distance": 0.0,
                "count": 0,
                "interpretation_note": "No collisions under configured thresholds.",
            }
        ]
    summary = []
    for (ctype, cluster), group in sorted(groups.items()):
        distances = [row["profile_distance"] for row in group]
        summary.append(
            {
                "collision_type": ctype,
                "collision_cluster_id": cluster,
                "pair_ids": ";".join(sorted(row["pair_id"] for row in group)),
                "wave_ids": ";".join(sorted({row["wave_id_i"] for row in group} | {row["wave_id_j"] for row in group})),
                "control_families": ";".join(sorted({row["control_family"] for row in group})),
                "min_distance": min(distances),
                "max_distance": max(distances),
                "mean_distance": mean(distances),
                "count": len(group),
                "interpretation_note": "Collision or ambiguity warning group.",
            }
        )
    return summary


def build_control_overlap_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    near_distances = [
        row["profile_distance"]
        for row in rows
        if row["source"] == "configured_pair" and row["control_family"] in NEAR_DUPLICATE_FAMILIES
    ]
    near_max = max(near_distances) if near_distances else 0.0
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["source"] == "configured_pair":
            grouped[row["control_family"]].append(row)
    result = []
    for family, group in sorted(grouped.items()):
        distances = [row["profile_distance"] for row in group]
        result.append(
            {
                "control_family": family,
                "pair_count": len(group),
                "mean_profile_distance": mean(distances),
                "min_profile_distance": min(distances),
                "max_profile_distance": max(distances),
                "near_duplicate_reference_max": near_max,
                "label_shuffle_profile_overlap": family in {"label_shuffle", "stronger_label_shuffle"} and min(distances) <= near_max,
                "kernel_shuffle_profile_overlap": family == "kernel_node_label_shuffle_proxy" and min(distances) <= near_max,
                "control_profile_mimicry_warning": any(row["control_profile_mimicry_warning"] for row in group),
                "residual_matched_profile_warning": any(row["residual_matched_profile_warning"] for row in group),
                "adversarial_profile_warning": any(row["adversarial_profile_warning"] for row in group),
                "warning_flags": sorted({warning for row in group for warning in row["warning_flags"]}),
            }
        )
    return result


def build_summary(config: dict[str, Any], wave_rows: list[dict[str, Any]], coordinate_rows: list[dict[str, Any]], pair_rows: list[dict[str, Any]], generated_files: list[str]) -> dict[str, Any]:
    configured_pair_count = len(config["pair_definitions"])
    all_pair_count = sum(1 for row in pair_rows if row["source"] == "all_pairwise")
    collapsed_coordinate_count = sum(1 for row in coordinate_rows if row["near_constant_flag"])
    manifold_richness_score = (len(COORDINATES) - collapsed_coordinate_count) / len(COORDINATES)
    decision_counts = Counter(row["decision_status"] for row in pair_rows)
    exact_rows = [row for row in pair_rows if row["control_family"] == "exact_duplicate"]
    return {
        "block_id": config.get("block_id", "QSB-ST-COMP01D1D"),
        "run_id": config.get("run_id", "wave_identity_manifold_degeneracy_audit_open"),
        "output_dir": config["output_dir"],
        "wave_count": len(wave_rows),
        "configured_pair_count": configured_pair_count,
        "all_pair_count": all_pair_count,
        "pair_delta_row_count": len(pair_rows),
        "coordinate_count": len(COORDINATES),
        "collapsed_coordinate_count": collapsed_coordinate_count,
        "manifold_richness_score": manifold_richness_score,
        "profile_collision_count": sum(1 for row in pair_rows if row["profile_collision"]),
        "residual_collision_count": sum(1 for row in pair_rows if row["residual_collision"]),
        "delta_vector_collision_count": sum(1 for row in pair_rows if row["delta_vector_collision"]),
        "ambiguity_warning_count": sum(1 for row in pair_rows if row["ambiguity_warning"]),
        "control_profile_mimicry_warnings_count": sum(1 for row in pair_rows if row["control_profile_mimicry_warning"]),
        "residual_matched_profile_warnings_count": sum(1 for row in pair_rows if row["residual_matched_profile_warning"]),
        "adversarial_profile_warnings_count": sum(1 for row in pair_rows if row["adversarial_profile_warning"]),
        "exact_duplicate_sanity_passed": bool(exact_rows and all(row["decision_status"] == "duplicate_sanity_pass" for row in exact_rows)),
        "specificity_established": False,
        "stable_candidate_metrics": [],
        "claim_boundary": "synthetic diagnostic manifold/feature-space audit only; manifold language is diagnostic, not physical spacetime; no physical time, no Hilbert-space reconstruction, no physical Bridge validation.",
        "decision_status_counts": dict(sorted(decision_counts.items())),
        "generated_files": generated_files,
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    text = f"""# QSB-ST-COMP01-D1d Wave Identity Manifold Degeneracy Audit Readout

## Befund

D1d is a synthetic diagnostic feature-manifold / degeneracy audit.

- wave_count: {summary['wave_count']}
- configured_pair_count: {summary['configured_pair_count']}
- all_pair_count: {summary['all_pair_count']}
- pair_delta_row_count: {summary['pair_delta_row_count']}
- coordinate_count: {summary['coordinate_count']}
- collapsed_coordinate_count: {summary['collapsed_coordinate_count']}
- manifold_richness_score: {summary['manifold_richness_score']}
- profile_collision_count: {summary['profile_collision_count']}
- residual_collision_count: {summary['residual_collision_count']}
- delta_vector_collision_count: {summary['delta_vector_collision_count']}
- ambiguity_warning_count: {summary['ambiguity_warning_count']}
- control_profile_mimicry_warnings_count: {summary['control_profile_mimicry_warnings_count']}
- residual_matched_profile_warnings_count: {summary['residual_matched_profile_warnings_count']}
- adversarial_profile_warnings_count: {summary['adversarial_profile_warnings_count']}
- exact_duplicate_sanity_passed: {summary['exact_duplicate_sanity_passed']}
- specificity_established: {summary['specificity_established']}

## Interpretation

The manifold language is diagnostic only, not physical spacetime. This audit checks coordinate richness, collapsed coordinates, profile collisions, residual collisions, delta-vector collisions, and control profile mimicry.

## Hypothese

If enough non-collapsed coordinates remain and collision warnings are limited, a later wave_identity_profile could be more useful than a single residual. This is a diagnostic hypothesis only.

## Offene Lücke

No physical validation, no real data, no specificity, no Lorentzian structure, no physical time, no Pauli claim, and no Hilbert-space reconstruction claim.

## Claim Boundary

- The manifold language denotes a diagnostic coordinate space of synthetic wave-pattern descriptors.
- It is not a physical spacetime manifold.
- It is not a Hilbert-space reconstruction.
- It is not a Lorentzian geometry.
- It is not a physical phase space.
- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- wave_identity_profile is a planned diagnostic profile concept, not a proof of physical identity.
- control mimicry warnings are methodological warnings, not failures of physics.
- wave-Pauli is a heuristic internal analogy only.
- It does not claim fermionic Pauli exclusion.
- It does not invoke quantum spin-statistics.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-D1d does not attach D(A,B).
- COMP01-D1d does not construct S_rel2.
- COMP01-D1d does not validate a physical Bridge.
- COMP01-D1d does not establish diagnostic specificity.

## Machine-readable status

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = read_config(Path(args.config))
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    wave_rows = build_wave_rows(config)
    coordinate_rows = build_coordinate_audit_rows(wave_rows, config)
    pair_rows = build_pair_rows(config, wave_rows, coordinate_rows)
    collision_rows = build_collision_summary(pair_rows)
    overlap_rows = build_control_overlap_summary(pair_rows)
    generated_files = [
        "summary.json",
        "readout.md",
        "wave_coordinate_summary.csv",
        "coordinate_audit_summary.csv",
        "pair_delta_vector_summary.csv",
        "collision_summary.csv",
        "control_profile_overlap_summary.csv",
        "resolved_config.json",
    ]
    summary = build_summary(config, wave_rows, coordinate_rows, pair_rows, generated_files)

    write_csv(output_dir / "wave_coordinate_summary.csv", wave_rows, ["wave_id", "family", "k", "A", "B", "R", "phi", "phi_wrapped", "slope", "intercept", "amplitude_balance", "normalized_amplitude_balance", "local_response_norm", "warning_flags"])
    write_csv(output_dir / "coordinate_audit_summary.csv", coordinate_rows, ["coordinate_name", "coordinate_min", "coordinate_max", "coordinate_mean", "coordinate_std", "unique_value_count", "near_constant_flag", "normalization_collapse_warning", "coordinate_dependency_warning", "dependency_partner", "warning_flags"])
    write_csv(output_dir / "pair_delta_vector_summary.csv", pair_rows, ["pair_id", "source", "wave_id_i", "wave_id_j", "control_family", "delta_k", "delta_R", "wrapped_delta_phi_abs", "cos_delta_phi", "sin_delta_phi", "delta_A", "delta_B", "delta_slope", "delta_intercept", "delta_balance", "delta_vector_norm", "profile_distance", "wave_identity_residual", "profile_collision", "residual_collision", "delta_vector_collision", "collision_cluster_id", "ambiguity_warning", "manifold_richness_score", "collapsed_coordinate_count", "decision_status", "warning_flags", "interpretation_note"])
    write_csv(output_dir / "collision_summary.csv", collision_rows, ["collision_type", "collision_cluster_id", "pair_ids", "wave_ids", "control_families", "min_distance", "max_distance", "mean_distance", "count", "interpretation_note"])
    write_csv(output_dir / "control_profile_overlap_summary.csv", overlap_rows, ["control_family", "pair_count", "mean_profile_distance", "min_profile_distance", "max_profile_distance", "near_duplicate_reference_max", "label_shuffle_profile_overlap", "kernel_shuffle_profile_overlap", "control_profile_mimicry_warning", "residual_matched_profile_warning", "adversarial_profile_warning", "warning_flags"])
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "resolved_config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_readout(output_dir / "readout.md", summary)

    print(f"QSB-ST-COMP01D1D manifold degeneracy audit complete: {len(pair_rows)} pair rows, output_dir={output_dir}")


if __name__ == "__main__":
    main()
