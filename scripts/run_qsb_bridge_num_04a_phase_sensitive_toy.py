#!/usr/bin/env python3
"""
QSB-BRIDGE-NUM-04A phase-sensitive toy diagnostic.

This script creates a deterministic toy run that separates a magnitude-only
distance-like readout from phase-sensitive toy diagnostics. It makes no
physical claim beyond that toy construction.
"""

from __future__ import annotations

import csv
import json
import math
import random
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/qsb_bridge_num_04a_phase_sensitive_toy_config.yaml"


Pair = Tuple[int, int]
Matrix = List[List[float]]


def parse_scalar(value: str) -> Any:
    text = value.strip()
    if not text:
        return ""
    if text in {"true", "True"}:
        return True
    if text in {"false", "False"}:
        return False
    try:
        if any(ch in text for ch in ".eE"):
            return float(text)
        return int(text)
    except ValueError:
        return text


def load_simple_yaml(path: Path) -> Dict[str, Any]:
    """Parse the restricted YAML shape used by this config file."""
    root: Dict[str, Any] = {}
    current_key: str | None = None
    current_list_key: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0 and stripped.endswith(":"):
            key = stripped[:-1]
            root[key] = {}
            current_key = key
            current_list_key = None
            continue

        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            root[key] = parse_scalar(value)
            current_key = None
            current_list_key = None
            continue

        if indent == 2 and stripped.startswith("- "):
            if current_key is None:
                raise ValueError(f"List item without parent key in {path}: {raw}")
            if not isinstance(root.get(current_key), list):
                root[current_key] = []
            root[current_key].append(parse_scalar(stripped[2:]))
            current_list_key = current_key
            continue

        if indent == 2 and ":" in stripped:
            if current_key is None:
                raise ValueError(f"Nested mapping item without parent key in {path}: {raw}")
            key, value = stripped.split(":", 1)
            if not isinstance(root.get(current_key), dict):
                root[current_key] = {}
            root[current_key][key] = parse_scalar(value)
            current_list_key = None
            continue

        if current_list_key is not None and stripped.startswith("- "):
            root[current_list_key].append(parse_scalar(stripped[2:]))
            continue

        raise ValueError(f"Unsupported config line in {path}: {raw}")

    return root


def project_path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def round_float(value: float, digits: int = 12) -> float:
    if abs(value) < 0.5 * 10 ** (-digits):
        return 0.0
    return round(float(value), digits)


def angle_wrap(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


def circular_distance(i: int, j: int, n: int) -> int:
    d = abs(i - j)
    return min(d, n - d)


def build_magnitude_matrix(n: int, l0: float) -> Matrix:
    matrix: Matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(1.0)
            else:
                row.append(math.exp(-circular_distance(i, j, n) / l0))
        matrix.append(row)
    return matrix


def zero_matrix(n: int) -> Matrix:
    return [[0.0 for _ in range(n)] for _ in range(n)]


def phase_matrix(variant: str, n: int, params: Dict[str, Any]) -> Matrix:
    phi = zero_matrix(n)
    if variant == "phase_zero":
        return phi

    if variant == "phase_linear_gradient":
        step = float(params["phase_linear_gradient_step"])
        for i, j in combinations(range(n), 2):
            value = angle_wrap(step * (i - j))
            phi[i][j] = value
            phi[j][i] = -value
        return phi

    if variant in {"phase_random_low", "phase_random_high"}:
        seed = int(params[f"{variant}_seed"])
        amplitude = float(params[f"{variant}_amplitude"])
        rng = random.Random(seed)
        for i, j in combinations(range(n), 2):
            value = rng.uniform(-amplitude, amplitude)
            phi[i][j] = value
            phi[j][i] = -value
        return phi

    if variant == "phase_vortex_like":
        winding = float(params["phase_vortex_winding"])
        sine_amp = float(params["phase_vortex_sine_amplitude"])
        theta = [2.0 * math.pi * i / n for i in range(n)]
        for i, j in combinations(range(n), 2):
            delta = theta[i] - theta[j]
            value = angle_wrap(winding * delta + sine_amp * math.sin(delta))
            phi[i][j] = value
            phi[j][i] = -value
        return phi

    raise ValueError(f"Unknown phase variant: {variant}")


def pair_values(n: int) -> List[Pair]:
    return list(combinations(range(n), 2))


def distance_matrix(abs_k: Matrix, l0: float, epsilon: float) -> Matrix:
    return [[-l0 * math.log(max(abs_k[i][j], epsilon)) for j in range(len(abs_k))] for i in range(len(abs_k))]


def flatten_pairs(matrix: Matrix, pairs: Sequence[Pair]) -> List[float]:
    return [matrix[i][j] for i, j in pairs]


def rank_order(values: Sequence[float]) -> List[int]:
    return sorted(range(len(values)), key=lambda idx: (values[idx], idx))


def edge_set(abs_k: Matrix, pairs: Sequence[Pair], tau: float) -> set[Pair]:
    return {(i, j) for i, j in pairs if abs_k[i][j] >= tau}


def jaccard(a: set[Pair], b: set[Pair]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def hermitian_check(phi: Matrix, tolerance: float) -> bool:
    n = len(phi)
    for i in range(n):
        if abs(phi[i][i]) > tolerance:
            return False
        for j in range(n):
            if abs(phi[i][j] + phi[j][i]) > tolerance:
                return False
    return True


def node_interference(abs_k: Matrix, phi: Matrix) -> List[float]:
    out = []
    n = len(abs_k)
    for i in range(n):
        real = 0.0
        imag = 0.0
        for j in range(n):
            if i == j:
                continue
            real += abs_k[i][j] * math.cos(phi[i][j])
            imag += abs_k[i][j] * math.sin(phi[i][j])
        out.append(math.hypot(real, imag))
    return out


def closure_values(phi: Matrix) -> List[float]:
    values = []
    for i, j, k in combinations(range(len(phi)), 3):
        values.append(angle_wrap(phi[i][j] + phi[j][k] + phi[k][i]))
    return values


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


def format_variant_table(rows: Sequence[Dict[str, Any]]) -> str:
    columns = [
        "variant_id",
        "mean_distance",
        "distance_matrix_max_abs_diff_vs_phase_zero",
        "magnitude_graph_edge_jaccard_vs_phase_zero",
        "mean_node_interference",
        "mean_abs_closure",
        "mean_cos_phase",
        "mean_abs_sin_phase",
    ]
    lines = ["|" + "|".join(columns) + "|", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        lines.append("|" + "|".join(str(row[c]) for c in columns) + "|")
    return "\n".join(lines)


def write_readout(path: Path, summary: Dict[str, Any], variant_rows: Sequence[Dict[str, Any]]) -> None:
    text = f"""# QSB-BRIDGE-NUM-04A Run Readout

## Run

```text
block_id: {summary["block_id"]}
run_id: {summary["run_id"]}
n_nodes: {summary["n_nodes"]}
l0: {summary["l0"]}
tau: {summary["tau"]}
```

## Purpose

This run is a deterministic toy diagnostic for the methodological separation between a magnitude-only distance-like readout and phase-sensitive toy diagnostics.

It uses one fixed magnitude matrix `A_ij` across all variants and changes only `phi_ij`.

## Main Readout

```text
magnitude_invariance_passed: {summary["magnitude_invariance_passed"]}
all_hermitian_checks_passed: {summary["all_hermitian_checks_passed"]}
phase_sensitive_diagnostics_changed: {summary["phase_sensitive_diagnostics_changed"]}
max_distance_diff_across_phase_variants: {summary["max_distance_diff_across_phase_variants"]}
max_graph_jaccard_loss: {summary["max_graph_jaccard_loss"]}
```

## Variant Summary

{format_variant_table(variant_rows)}

## Main Findings

""" + "\n".join(f"- {item}" for item in summary["main_findings"]) + """

## Claim Boundary

This is a toy diagnostic. `K_ij` and `D_ij` are toy objects in this run. `D_ij` is a distance-like construction, not a spacetime metric. The phase-sensitive diagnostics are interference-like toy diagnostics, not real quantum dynamics. The magnitude invariance readout and phase response readout do not establish physical emergence, metric recovery, causal structure, or de-Broglie confirmation.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_result_note(path: Path, summary: Dict[str, Any], variant_rows: Sequence[Dict[str, Any]]) -> None:
    text = f"""# QSB-BRIDGE-NUM-04A Result Note

## 1. Purpose

QSB-BRIDGE-NUM-04A records a small deterministic toy diagnostic for the magnitude/phase separation described in QSB-BRIDGE-SYNTH-02E.

The run keeps `|K_ij|` fixed and varies only `phi_ij`.

## 2. Files

```text
data/qsb_bridge_num_04a_phase_sensitive_toy_config.yaml
scripts/run_qsb_bridge_num_04a_phase_sensitive_toy.py
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/summary.json
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/readout.md
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_variant_summary.csv
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_pairwise_diagnostics.csv
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_config_resolved.json
```

## 3. Result

```text
magnitude_invariance_passed: {summary["magnitude_invariance_passed"]}
all_hermitian_checks_passed: {summary["all_hermitian_checks_passed"]}
phase_sensitive_diagnostics_changed: {summary["phase_sensitive_diagnostics_changed"]}
max_distance_diff_across_phase_variants: {summary["max_distance_diff_across_phase_variants"]}
max_graph_jaccard_loss: {summary["max_graph_jaccard_loss"]}
```

The magnitude-only distance-like diagnostics remain invariant across the tested phase variants because the magnitude matrix is unchanged. The phase-sensitive toy diagnostics vary across phase patterns.

## 4. Variant Summary

{format_variant_table(variant_rows)}

## 5. Claim Boundary

04A is a toy diagnostic. It does not make a physical proof claim. `K_ij` and `D_ij` are toy objects here. `D_ij` is distance-like only. Phase-sensitive readouts are toy interference-like readouts, not real quantum dynamics. Magnitude invariance does not support a physical emergence claim. Phase response does not support a de-Broglie confirmation claim. Geometry Proxy remains Proxy. The integrated bridge map remains methodological.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    config = load_simple_yaml(CONFIG_PATH)
    params = dict(config["parameters"])
    phase_params = dict(config["phase_parameters"])
    outputs = dict(config["outputs"])
    variants = list(config["phase_variants"])

    n = int(params["n_nodes"])
    l0 = float(params["l0"])
    tau = float(params["tau"])
    epsilon = float(params["epsilon"])
    tolerance = float(params["tolerance"])

    abs_k = build_magnitude_matrix(n, l0)
    pairs = pair_values(n)
    zero_distances: Matrix | None = None
    zero_distance_order: List[int] | None = None
    zero_edges: set[Pair] | None = None
    variant_rows: List[Dict[str, Any]] = []
    pairwise_rows: List[Dict[str, Any]] = []
    hermitian_results: Dict[str, bool] = {}

    for variant in variants:
        phi = phase_matrix(variant, n, phase_params)
        hermitian_results[variant] = hermitian_check(phi, tolerance)
        distances = distance_matrix(abs_k, l0, epsilon)
        flat_distances = flatten_pairs(distances, pairs)
        flat_abs = flatten_pairs(abs_k, pairs)
        edges = edge_set(abs_k, pairs, tau)

        if variant == "phase_zero":
            zero_distances = distances
            zero_distance_order = rank_order(flat_distances)
            zero_edges = edges

        assert zero_distances is not None
        assert zero_distance_order is not None
        assert zero_edges is not None

        max_distance_diff = max(
            abs(distances[i][j] - zero_distances[i][j]) for i, j in pairs
        )
        edge_jaccard = jaccard(edges, zero_edges)
        node_i = node_interference(abs_k, phi)
        closures = closure_values(phi)
        cos_values = [math.cos(phi[i][j]) for i, j in pairs]
        abs_sin_values = [abs(math.sin(phi[i][j])) for i, j in pairs]

        variant_rows.append(
            {
                "variant_id": variant,
                "mean_abs_K": round_float(mean(flat_abs)),
                "mean_distance": round_float(mean(flat_distances)),
                "std_distance": round_float(pstdev(flat_distances)),
                "distance_matrix_max_abs_diff_vs_phase_zero": round_float(max_distance_diff),
                "distance_rank_order_changed_vs_phase_zero": rank_order(flat_distances) != zero_distance_order,
                "magnitude_graph_edge_count_at_tau": len(edges),
                "magnitude_graph_edge_jaccard_vs_phase_zero": round_float(edge_jaccard),
                "mean_node_interference": round_float(mean(node_i)),
                "std_node_interference": round_float(pstdev(node_i)),
                "mean_abs_closure": round_float(mean(abs(x) for x in closures)),
                "max_abs_closure": round_float(max(abs(x) for x in closures)),
                "mean_cos_phase": round_float(mean(cos_values)),
                "mean_abs_sin_phase": round_float(mean(abs_sin_values)),
                "hermitian_check_passed": hermitian_results[variant],
            }
        )

        for i, j in pairs:
            pairwise_rows.append(
                {
                    "variant_id": variant,
                    "i": i,
                    "j": j,
                    "base_distance": circular_distance(i, j, n),
                    "abs_K": round_float(abs_k[i][j]),
                    "phi_ij": round_float(phi[i][j]),
                    "cos_phi": round_float(math.cos(phi[i][j])),
                    "sin_phi": round_float(math.sin(phi[i][j])),
                    "distance_like_D": round_float(distances[i][j]),
                    "magnitude_edge_at_tau": abs_k[i][j] >= tau,
                }
            )

    max_distance_diff_across = max(
        float(row["distance_matrix_max_abs_diff_vs_phase_zero"]) for row in variant_rows
    )
    max_graph_jaccard_loss = max(
        1.0 - float(row["magnitude_graph_edge_jaccard_vs_phase_zero"]) for row in variant_rows
    )
    phase_reference = variant_rows[0]
    phase_sensitive_changed = any(
        abs(float(row["mean_node_interference"]) - float(phase_reference["mean_node_interference"])) > 1.0e-9
        or abs(float(row["mean_abs_sin_phase"]) - float(phase_reference["mean_abs_sin_phase"])) > 1.0e-9
        or abs(float(row["mean_abs_closure"]) - float(phase_reference["mean_abs_closure"])) > 1.0e-9
        for row in variant_rows[1:]
    )

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "variant_count": len(variants),
        "variants": variants,
        "n_nodes": n,
        "tau": tau,
        "l0": l0,
        "epsilon": epsilon,
        "magnitude_invariance_passed": max_distance_diff_across <= tolerance
        and max_graph_jaccard_loss <= tolerance
        and not any(row["distance_rank_order_changed_vs_phase_zero"] for row in variant_rows),
        "all_hermitian_checks_passed": all(hermitian_results.values()),
        "max_distance_diff_across_phase_variants": round_float(max_distance_diff_across),
        "max_graph_jaccard_loss": round_float(max_graph_jaccard_loss),
        "phase_sensitive_diagnostics_changed": phase_sensitive_changed,
        "main_findings": [
            "All variants share the same magnitude matrix A_ij, so the distance-like diagnostics are invariant within the configured tolerance.",
            "The threshold graph at tau=0.35 is unchanged across phase variants.",
            "The phase-sensitive toy diagnostics change across the tested phase patterns.",
            "The readout is methodological and toy-level only.",
        ],
        "hermitian_checks": hermitian_results,
        "output_files": outputs,
    }

    resolved_config = dict(config)
    resolved_config["repo_root"] = str(ROOT)
    resolved_config["computed_pair_count"] = len(pairs)
    resolved_config["computed_triangle_count"] = math.comb(n, 3)

    variant_fields = [
        "variant_id",
        "mean_abs_K",
        "mean_distance",
        "std_distance",
        "distance_matrix_max_abs_diff_vs_phase_zero",
        "distance_rank_order_changed_vs_phase_zero",
        "magnitude_graph_edge_count_at_tau",
        "magnitude_graph_edge_jaccard_vs_phase_zero",
        "mean_node_interference",
        "std_node_interference",
        "mean_abs_closure",
        "max_abs_closure",
        "mean_cos_phase",
        "mean_abs_sin_phase",
        "hermitian_check_passed",
    ]
    pairwise_fields = [
        "variant_id",
        "i",
        "j",
        "base_distance",
        "abs_K",
        "phi_ij",
        "cos_phi",
        "sin_phi",
        "distance_like_D",
        "magnitude_edge_at_tau",
    ]

    write_csv(project_path(outputs["variant_summary_csv"]), variant_rows, variant_fields)
    write_csv(project_path(outputs["pairwise_diagnostics_csv"]), pairwise_rows, pairwise_fields)
    write_json(project_path(outputs["summary_json"]), summary)
    write_json(project_path(outputs["resolved_config_json"]), resolved_config)
    write_readout(project_path(outputs["readout_md"]), summary, variant_rows)
    write_result_note(project_path(outputs["result_note_md"]), summary, variant_rows)

    print(f"wrote: {outputs['summary_json']}")
    print(f"wrote: {outputs['readout_md']}")
    print(f"wrote: {outputs['variant_summary_csv']}")
    print(f"wrote: {outputs['pairwise_diagnostics_csv']}")
    print(f"wrote: {outputs['resolved_config_json']}")
    print(f"wrote: {outputs['result_note_md']}")


if __name__ == "__main__":
    main()
