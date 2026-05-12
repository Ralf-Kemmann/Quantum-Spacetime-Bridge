#!/usr/bin/env python3
"""
QSB-BRIDGE-NUM-05C perturbation / noise boundary map.

This script maps synthetic method-level breakdown thresholds. It does not make
physical validation claims.
"""

from __future__ import annotations

import csv
import json
import math
import random
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/qsb_bridge_num_05c_perturbation_noise_boundary_config.yaml"

Matrix = List[List[float]]
Pair = Tuple[int, int]
Point = Tuple[float, float]


def parse_scalar(value: str) -> Any:
    text = value.strip()
    if not text:
        return ""
    try:
        if any(ch in text for ch in ".eE"):
            return float(text)
        return int(text)
    except ValueError:
        return text


def load_simple_yaml(path: Path) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    current_key: str | None = None
    current_nested_key: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0 and stripped.endswith(":"):
            current_key = stripped[:-1]
            root[current_key] = {}
            current_nested_key = None
            continue
        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            root[key] = parse_scalar(value)
            current_key = None
            current_nested_key = None
            continue
        if indent == 2 and stripped.startswith("- "):
            if current_key is None:
                raise ValueError(f"List item without parent: {raw}")
            if not isinstance(root.get(current_key), list):
                root[current_key] = []
            root[current_key].append(parse_scalar(stripped[2:]))
            continue
        if indent == 2 and stripped.endswith(":"):
            if current_key is None:
                raise ValueError(f"Nested key without parent: {raw}")
            if not isinstance(root.get(current_key), dict):
                root[current_key] = {}
            current_nested_key = stripped[:-1]
            root[current_key][current_nested_key] = []
            continue
        if indent == 2 and ":" in stripped:
            if current_key is None:
                raise ValueError(f"Mapping item without parent: {raw}")
            key, value = stripped.split(":", 1)
            if not isinstance(root.get(current_key), dict):
                root[current_key] = {}
            root[current_key][key] = parse_scalar(value)
            current_nested_key = None
            continue
        if indent == 4 and stripped.startswith("- "):
            if current_key is None or current_nested_key is None:
                raise ValueError(f"Nested list item without key: {raw}")
            root[current_key][current_nested_key].append(parse_scalar(stripped[2:]))
            continue
        raise ValueError(f"Unsupported config line: {raw}")
    return root


def project_path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def round_float(value: float, digits: int = 12) -> float:
    if not math.isfinite(value):
        return value
    if abs(value) < 0.5 * 10 ** (-digits):
        return 0.0
    return round(float(value), digits)


def pairs(n: int) -> List[Pair]:
    return list(combinations(range(n), 2))


def matrix(n: int, fill: float = 0.0) -> Matrix:
    return [[fill for _ in range(n)] for _ in range(n)]


def angle_wrap(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


def grid_points(n: int) -> List[Point]:
    side = int(round(math.sqrt(n)))
    return [(x / side, y / side) for y in range(side) for x in range(side)][:n]


def torus_distance(a: Point, b: Point) -> float:
    dx = min(abs(a[0] - b[0]), 1.0 - abs(a[0] - b[0]))
    dy = min(abs(a[1] - b[1]), 1.0 - abs(a[1] - b[1]))
    return math.sqrt(dx * dx + dy * dy)


def distance_from_points(points: Sequence[Point]) -> Matrix:
    n = len(points)
    out = matrix(n)
    for i, j in pairs(n):
        d = torus_distance(points[i], points[j])
        out[i][j] = d
        out[j][i] = d
    return out


def magnitude_from_distance(dist: Matrix, l0: float) -> Matrix:
    n = len(dist)
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = math.exp(-dist[i][j] / l0)
        out[i][j] = value
        out[j][i] = value
    return out


def reconstructed_distance(mag: Matrix, l0: float, epsilon: float) -> Matrix:
    n = len(mag)
    out = matrix(n)
    for i, j in pairs(n):
        value = -l0 * math.log(max(mag[i][j], epsilon))
        out[i][j] = value
        out[j][i] = value
    return out


def flatten(mat: Matrix, ps: Sequence[Pair]) -> List[float]:
    return [mat[i][j] for i, j in ps]


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    mx = mean(x)
    my = mean(y)
    vx = sum((v - mx) ** 2 for v in x)
    vy = sum((v - my) ** 2 for v in y)
    if vx <= 0.0 or vy <= 0.0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(vx * vy)


def threshold_edges(mag: Matrix, tau: float) -> set[Pair]:
    return {(i, j) for i, j in pairs(len(mag)) if mag[i][j] >= tau}


def jaccard(a: set[Pair], b: set[Pair]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def nearest_neighbor_recall(known: Matrix, rec: Matrix, k: int) -> float:
    n = len(known)
    kk = min(k, n - 1)
    vals = []
    for i in range(n):
        true = set(sorted([j for j in range(n) if j != i], key=lambda j: (known[i][j], j))[:kk])
        got = set(sorted([j for j in range(n) if j != i], key=lambda j: (rec[i][j], j))[:kk])
        vals.append(len(true & got) / kk)
    return mean(vals)


def distance_stress(known: Matrix, rec: Matrix, ps: Sequence[Pair]) -> float:
    a = flatten(known, ps)
    b = flatten(rec, ps)
    denom = sum(x * x for x in a) or 1.0
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / denom)


def rank_order_stability(base: Matrix, rec: Matrix, ps: Sequence[Pair]) -> float:
    base_order = sorted(range(len(ps)), key=lambda idx: (base[ps[idx][0]][ps[idx][1]], idx))
    rec_order = sorted(range(len(ps)), key=lambda idx: (rec[ps[idx][0]][ps[idx][1]], idx))
    base_rank = {idx: rank for rank, idx in enumerate(base_order)}
    rec_rank = {idx: rank for rank, idx in enumerate(rec_order)}
    diffs = [abs(base_rank[i] - rec_rank[i]) for i in range(len(ps))]
    max_diff = len(ps) - 1 or 1
    return 1.0 - (mean(diffs) / max_diff)


def geometry_score(corr: float, nn: float, stress: float) -> float:
    return (max(0.0, corr) + nn + (1.0 / (1.0 + max(0.0, stress)))) / 3.0


def loop_flux_rms(phi: Matrix) -> float:
    vals = []
    for i, j, k in combinations(range(len(phi)), 3):
        vals.append(angle_wrap(phi[i][j] + phi[j][k] + phi[k][i]))
    return math.sqrt(mean(v * v for v in vals)) if vals else 0.0


def magnetic_laplacian_eigs(mag: Matrix, phi: Matrix) -> List[float]:
    n = len(mag)
    adj = np.zeros((n, n), dtype=complex)
    deg = np.zeros((n, n), dtype=complex)
    for i in range(n):
        deg[i, i] = sum(mag[i][j] for j in range(n) if j != i)
    for i, j in pairs(n):
        value = mag[i][j] * complex(math.cos(phi[i][j]), math.sin(phi[i][j]))
        adj[i, j] = value
        adj[j, i] = value.conjugate()
    return [float(x) for x in np.linalg.eigvalsh(deg - adj)]


def gaussian_mag(base: Matrix, level: float, seed: int) -> Matrix:
    rng = random.Random(seed)
    n = len(base)
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = min(0.999, max(0.001, base[i][j] + rng.gauss(0.0, level)))
        out[i][j] = value
        out[j][i] = value
    return out


def multiplicative_mag(base: Matrix, level: float, seed: int) -> Matrix:
    rng = random.Random(seed)
    n = len(base)
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = min(0.999, max(0.001, base[i][j] * math.exp(rng.gauss(0.0, level))))
        out[i][j] = value
        out[j][i] = value
    return out


def near_degenerate_mag(base: Matrix, level: float, seed: int) -> Matrix:
    rng = random.Random(seed)
    n = len(base)
    values = flatten(base, pairs(n))
    center = mean(values)
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = (1.0 - level) * base[i][j] + level * (center + rng.uniform(-0.02, 0.02))
        value = min(0.999, max(0.001, value))
        out[i][j] = value
        out[j][i] = value
    return out


def dropout_mag(base: Matrix, level: float, seed: int) -> Matrix:
    rng = random.Random(seed)
    n = len(base)
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = 0.001 if rng.random() < level else base[i][j]
        out[i][j] = value
        out[j][i] = value
    return out


def phase_noise(n: int, level: float, seed: int, correlated: bool = False) -> Matrix:
    rng = random.Random(seed)
    out = matrix(n)
    if correlated:
        theta = [level * math.sin(2.0 * math.pi * i / n) + 0.25 * level * math.sin(4.0 * math.pi * i / n) for i in range(n)]
        for i, j in pairs(n):
            value = angle_wrap(theta[i] - theta[j] + 0.15 * level * math.sin((i + 1) * (j + 1)))
            out[i][j] = value
            out[j][i] = -value
        return out
    for i, j in pairs(n):
        value = angle_wrap(rng.gauss(0.0, level))
        out[i][j] = value
        out[j][i] = -value
    return out


def evaluate(
    family_id: str,
    noise_level: float,
    mag: Matrix,
    phi: Matrix,
    known_dist: Matrix,
    base_dist: Matrix,
    base_edges: set[Pair],
    zero_eigs: Sequence[float],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    params = cfg["parameters"]
    thresholds = cfg["breakdown_thresholds"]
    l0 = float(params["l0"])
    tau = float(params["tau"])
    epsilon = float(params["epsilon"])
    k = int(params["nearest_neighbor_k"])
    ps = pairs(len(mag))
    rec = reconstructed_distance(mag, l0, epsilon)
    corr = pearson(flatten(known_dist, ps), flatten(rec, ps))
    nn = nearest_neighbor_recall(known_dist, rec, k)
    stress = distance_stress(known_dist, rec, ps)
    rank_stability = rank_order_stability(base_dist, rec, ps)
    edge_j = jaccard(threshold_edges(mag, tau), base_edges)
    score = geometry_score(corr, nn, stress)
    hostile_gap = score - float(params["reference_hostile_score"])
    eigs = magnetic_laplacian_eigs(mag, phi)
    low_shift = max(abs(eigs[i] - zero_eigs[i]) for i in range(min(int(params["low_eigenvalue_count"]), len(eigs))))
    spectral_gap_shift = eigs[1] - zero_eigs[1]
    flux = loop_flux_rms(phi)
    broken_reasons = []
    if score <= float(thresholds["minimum_geometry_score"]):
        broken_reasons.append("geometry_score")
    if nn <= float(thresholds["minimum_nearest_neighbor_recall"]):
        broken_reasons.append("nearest_neighbor_recall")
    if rank_stability <= float(thresholds["minimum_rank_order_stability"]):
        broken_reasons.append("rank_order_stability")
    if edge_j <= float(thresholds["minimum_threshold_graph_jaccard"]):
        broken_reasons.append("threshold_graph_jaccard")
    if stress >= float(thresholds["maximum_distance_stress"]):
        broken_reasons.append("distance_stress")
    if flux >= float(thresholds["maximum_loop_flux_rms"]):
        broken_reasons.append("loop_flux_rms")
    if low_shift >= float(thresholds["maximum_low_eigenvalue_shift"]):
        broken_reasons.append("magnetic_low_eigenvalue_shift")
    if hostile_gap <= float(thresholds["minimum_hostile_control_gap"]):
        broken_reasons.append("hostile_control_gap")
    return {
        "perturbation_family": family_id,
        "noise_level": noise_level,
        "geometry_score_vs_noise": round_float(score),
        "hostile_control_gap_vs_noise": round_float(hostile_gap),
        "nearest_neighbor_recall_vs_noise": round_float(nn),
        "rank_order_stability_vs_noise": round_float(rank_stability),
        "threshold_graph_jaccard_vs_noise": round_float(edge_j),
        "distance_stress_vs_noise": round_float(stress),
        "loop_flux_rms_vs_phase_noise": round_float(flux),
        "magnetic_laplacian_low_eigenvalue_shift_vs_noise": round_float(low_shift),
        "spectral_gap_shift_vs_noise": round_float(spectral_gap_shift),
        "breakdown_condition_met": bool(broken_reasons),
        "breakdown_reasons": ";".join(broken_reasons),
    }


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def table(rows: Sequence[Dict[str, Any]], columns: Sequence[str]) -> str:
    lines = ["|" + "|".join(columns) + "|", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        lines.append("|" + "|".join(str(row.get(c, "")) for c in columns) + "|")
    return "\n".join(lines)


def breakdown_summary(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for family in sorted({str(r["perturbation_family"]) for r in rows}):
        family_rows = [r for r in rows if r["perturbation_family"] == family]
        broken = [r for r in family_rows if r["breakdown_condition_met"]]
        first = min(broken, key=lambda r: float(r["noise_level"])) if broken else None
        out.append(
            {
                "perturbation_family": family,
                "breakdown_threshold_estimate": "" if first is None else first["noise_level"],
                "breakdown_condition_met": first is not None,
                "breakdown_reasons": "" if first is None else first["breakdown_reasons"],
                "earliest_sensitive_breakdown_family": False,
            }
        )
    broken_out = [r for r in out if r["breakdown_condition_met"]]
    if broken_out:
        earliest_level = min(float(r["breakdown_threshold_estimate"]) for r in broken_out)
        earliest = [r for r in broken_out if float(r["breakdown_threshold_estimate"]) == earliest_level]
        for row in earliest:
            row["earliest_sensitive_breakdown_family"] = True
    return out


def write_readout(path: Path, summary: Dict[str, Any], breakdown_rows: Sequence[Dict[str, Any]]) -> None:
    cols = [
        "perturbation_family",
        "breakdown_threshold_estimate",
        "breakdown_condition_met",
        "breakdown_reasons",
        "earliest_sensitive_breakdown_family",
    ]
    text = f"""# QSB-BRIDGE-NUM-05C Run Readout

## Run

```text
block_id: {summary["block_id"]}
run_id: {summary["run_id"]}
earliest_sensitive_breakdown_family: {summary["earliest_sensitive_breakdown_family"]}
earliest_sensitive_breakdown_noise_level: {summary["earliest_sensitive_breakdown_noise_level"]}
stop_go_outcome: {summary["stop_go_outcome"]}
```

## Boundary Map Intuition

05C does not try to prove the scanner. It pushes the synthetic magnitude and phase readouts until they bend, wobble, or break. A breakdown is not an embarrassment in this block; it is the boundary being mapped.

The earliest sensitive family is the first warning light. It marks the perturbation type that reaches a configured failure condition at the lowest noise level.

## Breakdown Threshold Summary

{table(breakdown_rows, cols)}

## Main Findings

""" + "\n".join(f"- {item}" for item in summary["main_findings"]) + """

## Future Result Discussion Requirement

A separate 05C result discussion should add a human-readable Bauchbild explaining the boundary map in project language.

## Claim Boundary

05C is synthetic and method-level. It does not physically validate QSB or claim spacetime emergence, physical metric recovery, causal structure, de-Broglie confirmation, or real quantum dynamics.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_result_note(path: Path, summary: Dict[str, Any], breakdown_rows: Sequence[Dict[str, Any]]) -> None:
    text = f"""# QSB-BRIDGE-NUM-05C Result Note

## 1. Purpose

QSB-BRIDGE-NUM-05C maps synthetic perturbation and noise boundaries for magnitude-derived and phase-aware diagnostics.

## 2. Result

```text
earliest_sensitive_breakdown_family: {summary["earliest_sensitive_breakdown_family"]}
earliest_sensitive_breakdown_noise_level: {summary["earliest_sensitive_breakdown_noise_level"]}
families_with_breakdown: {summary["families_with_breakdown"]}
stop_go_outcome: {summary["stop_go_outcome"]}
```

## 3. Interpretation

Breakdown or instability is a valid negative finding. The run identifies where configured synthetic diagnostics first cross configured method-level thresholds.

## 4. Earliest Breakdown

The earliest / most sensitive breakdown family is:

```text
{summary["earliest_sensitive_breakdown_family"]}
```

## 5. Claim Boundary

05C does not physically validate QSB. It does not show spacetime emergence, physical metric recovery, causal structure, de-Broglie confirmation, or real quantum dynamics.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    config = load_simple_yaml(CONFIG_PATH)
    params = dict(config["parameters"])
    outputs = dict(config["outputs"])
    seed = int(params["seed"])
    n = int(params["n_nodes"])
    l0 = float(params["l0"])
    tau = float(params["tau"])

    points = grid_points(n)
    known_dist = distance_from_points(points)
    base_mag = magnitude_from_distance(known_dist, l0)
    base_dist = reconstructed_distance(base_mag, l0, float(params["epsilon"]))
    base_edges = threshold_edges(base_mag, tau)
    zero_phi = matrix(n)
    zero_eigs = magnetic_laplacian_eigs(base_mag, zero_phi)

    mag_rows: List[Dict[str, Any]] = []
    phase_rows: List[Dict[str, Any]] = []
    combined_rows: List[Dict[str, Any]] = []

    for level in config["noise_levels"]:
        lv = float(level)
        for family, mag in [
            ("magnitude_gaussian_noise_sweep", gaussian_mag(base_mag, lv, seed + int(lv * 1000) + 1)),
            ("magnitude_multiplicative_noise_sweep", multiplicative_mag(base_mag, lv, seed + int(lv * 1000) + 2)),
            ("rank_order_near_degeneracy_perturbation", near_degenerate_mag(base_mag, lv, seed + int(lv * 1000) + 3)),
        ]:
            mag_rows.append(evaluate(family, lv, mag, zero_phi, known_dist, base_dist, base_edges, zero_eigs, config))
        for family, phi in [
            ("phase_gaussian_noise_sweep", phase_noise(n, lv, seed + int(lv * 1000) + 4, correlated=False)),
            ("correlated_phase_noise_sweep", phase_noise(n, lv, seed + int(lv * 1000) + 5, correlated=True)),
        ]:
            phase_rows.append(evaluate(family, lv, base_mag, phi, known_dist, base_dist, base_edges, zero_eigs, config))
        combined_mag = gaussian_mag(base_mag, lv, seed + int(lv * 1000) + 6)
        combined_phi = phase_noise(n, lv, seed + int(lv * 1000) + 7, correlated=False)
        combined_rows.append(
            evaluate(
                "combined_magnitude_phase_perturbation",
                lv,
                combined_mag,
                combined_phi,
                known_dist,
                base_dist,
                base_edges,
                zero_eigs,
                config,
            )
        )

    for level in config["dropout_levels"]:
        lv = float(level)
        mag_rows.append(
            evaluate(
                "edge_dropout_missing_correlation_perturbation",
                lv,
                dropout_mag(base_mag, lv, seed + int(lv * 1000) + 8),
                zero_phi,
                known_dist,
                base_dist,
                base_edges,
                zero_eigs,
                config,
            )
        )

    all_rows = mag_rows + phase_rows + combined_rows
    breakdown_rows = breakdown_summary(all_rows)
    earliest_rows = [r for r in breakdown_rows if r["earliest_sensitive_breakdown_family"]]
    earliest_family = ";".join(r["perturbation_family"] for r in earliest_rows) if earliest_rows else ""
    earliest_level = earliest_rows[0]["breakdown_threshold_estimate"] if earliest_rows else ""
    families_with_breakdown = sum(1 for r in breakdown_rows if r["breakdown_condition_met"])
    stop_go = "revise_or_bound_before_real_data" if earliest_rows else "go_with_no_configured_breakdown_observed"

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "magnitude_sweep_rows": len(mag_rows),
        "phase_sweep_rows": len(phase_rows),
        "combined_sweep_rows": len(combined_rows),
        "breakdown_family_count": len(breakdown_rows),
        "families_with_breakdown": families_with_breakdown,
        "earliest_sensitive_breakdown_family": earliest_family,
        "earliest_sensitive_breakdown_noise_level": earliest_level,
        "stop_go_outcome": stop_go,
        "main_findings": [
            "Breakdown or instability is treated as a valid negative finding.",
            "The earliest sensitive breakdown family is explicitly reported.",
            "Magnitude, phase, and combined perturbation families are reported separately.",
            "All thresholds are synthetic method-level thresholds, not physical constants.",
        ],
        "future_result_discussion_requirement": "Create a separate 05C result discussion with a human-readable Bauchbild.",
        "claim_boundary": config["claim_boundary"],
        "output_files": outputs,
    }

    write_csv(project_path(outputs["magnitude_noise_sweep_summary_csv"]), mag_rows, list(mag_rows[0].keys()))
    write_csv(project_path(outputs["phase_noise_sweep_summary_csv"]), phase_rows, list(phase_rows[0].keys()))
    write_csv(project_path(outputs["combined_noise_sweep_summary_csv"]), combined_rows, list(combined_rows[0].keys()))
    write_csv(project_path(outputs["breakdown_threshold_summary_csv"]), breakdown_rows, list(breakdown_rows[0].keys()))
    write_json(project_path(outputs["summary_json"]), summary)
    resolved = dict(config)
    resolved["repo_root"] = str(ROOT)
    write_json(project_path(outputs["resolved_config_json"]), resolved)
    write_readout(project_path(outputs["readout_md"]), summary, breakdown_rows)
    write_result_note(project_path(outputs["result_note_md"]), summary, breakdown_rows)

    for key in [
        "summary_json",
        "readout_md",
        "magnitude_noise_sweep_summary_csv",
        "phase_noise_sweep_summary_csv",
        "combined_noise_sweep_summary_csv",
        "breakdown_threshold_summary_csv",
        "resolved_config_json",
        "result_note_md",
    ]:
        print(f"wrote: {outputs[key]}")


if __name__ == "__main__":
    main()
