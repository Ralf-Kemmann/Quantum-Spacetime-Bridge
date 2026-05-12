#!/usr/bin/env python3
"""
QSB-BRIDGE-NUM-05B phase / gauge / flux stress test.

This script tests gauge-equivalent and loop-flux phase families on a fixed
synthetic magnitude matrix. It is a method-level toy diagnostic, not real
quantum dynamics and not physical validation.
"""

from __future__ import annotations

import csv
import json
import math
import random
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/qsb_bridge_num_05b_phase_gauge_flux_config.yaml"

Matrix = List[List[float]]
Pair = Tuple[int, int]


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
    if abs(value) < 0.5 * 10 ** (-digits):
        return 0.0
    return round(float(value), digits)


def pairs(n: int) -> List[Pair]:
    return list(combinations(range(n), 2))


def matrix(n: int, fill: float = 0.0) -> Matrix:
    return [[fill for _ in range(n)] for _ in range(n)]


def angle_wrap(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


def circular_distance(i: int, j: int, n: int) -> int:
    d = abs(i - j)
    return min(d, n - d)


def magnitude_matrix(n: int, l0: float) -> Matrix:
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = math.exp(-circular_distance(i, j, n) / l0)
        out[i][j] = value
        out[j][i] = value
    return out


def distance_matrix(mag: Matrix, l0: float, epsilon: float) -> Matrix:
    n = len(mag)
    out = matrix(n)
    for i, j in pairs(n):
        value = -l0 * math.log(max(mag[i][j], epsilon))
        out[i][j] = value
        out[j][i] = value
    return out


def threshold_edges(mag: Matrix, tau: float) -> set[Pair]:
    return {(i, j) for i, j in pairs(len(mag)) if mag[i][j] >= tau}


def jaccard(a: set[Pair], b: set[Pair]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def theta_difference(theta: Sequence[float]) -> Matrix:
    n = len(theta)
    out = matrix(n)
    for i, j in pairs(n):
        value = angle_wrap(theta[i] - theta[j])
        out[i][j] = value
        out[j][i] = -value
    return out


def random_antisymmetric(n: int, seed: int, sigma: float) -> Matrix:
    rng = random.Random(seed)
    out = matrix(n)
    for i, j in pairs(n):
        value = angle_wrap(rng.gauss(0.0, sigma))
        out[i][j] = value
        out[j][i] = -value
    return out


def phase_family(family_id: str, n: int, params: Dict[str, Any]) -> Tuple[Matrix, bool]:
    if family_id == "phase_zero_reference":
        return matrix(n), True
    if family_id == "global_phase_transformation":
        alpha = float(params["global_phase_alpha"])
        return theta_difference([alpha for _ in range(n)]), True
    if family_id == "local_gauge_transformation_theta_i_minus_theta_j":
        rng = random.Random(int(params["local_gauge_seed"]))
        amp = float(params["local_gauge_amplitude"])
        return theta_difference([rng.uniform(-amp, amp) for _ in range(n)]), True
    if family_id == "random_low_amplitude_phase_noise":
        return random_antisymmetric(n, int(params["random_low_seed"]), float(params["random_low_sigma"])), False
    if family_id == "random_high_amplitude_phase_noise":
        return random_antisymmetric(n, int(params["random_high_seed"]), float(params["random_high_sigma"])), False
    if family_id == "correlated_phase_field":
        amp = float(params["correlated_amplitude"])
        theta = [amp * math.sin(2.0 * math.pi * i / n) for i in range(n)]
        return theta_difference(theta), True
    if family_id == "loop_flux_vortex_like_phase_family":
        amp = float(params["vortex_flux_strength"])
        angles = [2.0 * math.pi * i / n for i in range(n)]
        out = matrix(n)
        for i, j in pairs(n):
            value = angle_wrap(amp * angle_wrap(angles[j] - angles[i]))
            out[i][j] = value
            out[j][i] = -value
        return out, False
    if family_id == "adversarial_high_frequency_phase_family":
        amp = float(params["adversarial_amplitude"])
        freq = int(params["adversarial_frequency"])
        out = matrix(n)
        for i, j in pairs(n):
            value = angle_wrap(amp * math.sin(freq * (i + 1) * (j + 2)))
            out[i][j] = value
            out[j][i] = -value
        return out, False
    raise ValueError(f"Unknown phase family: {family_id}")


def loop_fluxes(phi: Matrix) -> List[Tuple[int, int, int, float]]:
    vals: List[Tuple[int, int, int, float]] = []
    for i, j, k in combinations(range(len(phi)), 3):
        vals.append((i, j, k, angle_wrap(phi[i][j] + phi[j][k] + phi[k][i])))
    return vals


def node_interference(mag: Matrix, phi: Matrix) -> List[float]:
    out = []
    n = len(mag)
    for i in range(n):
        real = 0.0
        imag = 0.0
        for j in range(n):
            if i == j:
                continue
            real += mag[i][j] * math.cos(phi[i][j])
            imag += mag[i][j] * math.sin(phi[i][j])
        out.append(math.hypot(real, imag))
    return out


def magnetic_laplacian_eigenvalues(mag: Matrix, phi: Matrix) -> List[float]:
    n = len(mag)
    adj = np.zeros((n, n), dtype=complex)
    degree = np.zeros((n, n), dtype=complex)
    for i in range(n):
        degree[i, i] = sum(mag[i][j] for j in range(n) if j != i)
    for i, j in pairs(n):
        value = mag[i][j] * complex(math.cos(phi[i][j]), math.sin(phi[i][j]))
        adj[i, j] = value
        adj[j, i] = value.conjugate()
    lap = degree - adj
    return [float(x) for x in np.linalg.eigvalsh(lap)]


def spectrum_summary(eigs: Sequence[float], zero_eigs: Sequence[float], count: int) -> Dict[str, Any]:
    low_count = min(count, len(eigs))
    low_shift = max(abs(eigs[i] - zero_eigs[i]) for i in range(low_count))
    gap = eigs[1] if len(eigs) > 1 else 0.0
    zero_gap = zero_eigs[1] if len(zero_eigs) > 1 else 0.0
    return {
        "lowest_eigenvalue": round_float(eigs[0]),
        "spectral_gap": round_float(gap),
        "spectral_gap_shift": round_float(gap - zero_gap),
        "low_eigenvalue_shift_vs_phase_zero": round_float(low_shift),
        "low_eigenvalues": ";".join(str(round_float(x)) for x in eigs[:low_count]),
    }


def phase_metrics(mag: Matrix, phi: Matrix, zero_dist: Matrix, zero_edges: set[Pair], l0: float, tau: float, epsilon: float) -> Dict[str, Any]:
    dist = distance_matrix(mag, l0, epsilon)
    ps = pairs(len(mag))
    max_dist_diff = max(abs(dist[i][j] - zero_dist[i][j]) for i, j in ps)
    edge_j = jaccard(threshold_edges(mag, tau), zero_edges)
    flux_vals = [x[3] for x in loop_fluxes(phi)]
    abs_flux = [abs(x) for x in flux_vals]
    phase_vals = [abs(phi[i][j]) for i, j in ps]
    sin_vals = [abs(math.sin(phi[i][j])) for i, j in ps]
    inter = node_interference(mag, phi)
    return {
        "magnitude_distance_invariance": max_dist_diff <= 1.0e-12,
        "threshold_graph_invariance": abs(edge_j - 1.0) <= 1.0e-12,
        "distance_matrix_max_abs_diff_vs_phase_zero": round_float(max_dist_diff),
        "threshold_graph_jaccard_vs_phase_zero": round_float(edge_j),
        "phase_diagnostic_response": round_float(mean(sin_vals) + pstdev(inter)),
        "mean_node_interference": round_float(mean(inter)),
        "std_node_interference": round_float(pstdev(inter)),
        "gauge_invariant_loop_flux_rms": round_float(math.sqrt(mean(x * x for x in flux_vals))),
        "max_abs_loop_flux": round_float(max(abs_flux)),
        "gauge_variant_phase_score": round_float(mean(phase_vals)),
        "mean_abs_sin_phase": round_float(mean(sin_vals)),
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


def intuition_section() -> str:
    return """## Human-readable Interpretation / Bauchbild

A global phase is like changing the overall phase convention of the whole toy system. In this run it cancels from pairwise phase differences, so it should not create loop flux.

A local gauge phase assigns a phase label `theta_i` to each node and uses only differences `theta_i - theta_j`. Individual edges can look phase-shifted, but closed loops cancel. That is why local gauge phase can have a nonzero gauge-variant phase score while still carrying near-zero loop flux.

Loop flux is different. It is what remains when phases are summed around a closed triangle. If that loop sum does not cancel, the phase pattern is not just a relabeling of node phases in this toy diagnostic.

Confusing gauge with flux would be a negative finding. It would mean the diagnostic cannot tell a harmless phase convention from a loop-sensitive phase structure.

The magnetic/Hermitian Laplacian adds a method-level spectral readout: it keeps the complex edge phases instead of discarding them. It is useful here because gauge-equivalent cases should be spectrally close to the zero-phase case, while non-gauge flux cases can shift low eigenvalues or the spectral gap.

This remains non-physical and toy-level. The phase diagnostics are not real quantum dynamics, and the spectral shifts are not evidence for physical geometry or de-Broglie physics.
"""


def write_readout(path: Path, summary: Dict[str, Any], families: Sequence[Dict[str, Any]], spectra: Sequence[Dict[str, Any]]) -> None:
    family_cols = [
        "phase_family_id",
        "expected_gauge_equivalent",
        "observed_gauge_equivalent",
        "gauge_invariant_loop_flux_rms",
        "gauge_variant_phase_score",
        "phase_diagnostic_response",
    ]
    spectrum_cols = [
        "phase_family_id",
        "spectral_gap",
        "spectral_gap_shift",
        "low_eigenvalue_shift_vs_phase_zero",
    ]
    text = f"""# QSB-BRIDGE-NUM-05B Run Readout

## Run

```text
block_id: {summary["block_id"]}
run_id: {summary["run_id"]}
phase_family_count: {summary["phase_family_count"]}
gauge_flux_distinction_passed: {summary["gauge_flux_distinction_passed"]}
stop_go_outcome: {summary["stop_go_outcome"]}
```

{intuition_section()}

## Phase Family Summary

{table(families, family_cols)}

## Magnetic / Hermitian Laplacian Summary

{table(spectra, spectrum_cols)}

## Main Findings

""" + "\n".join(f"- {item}" for item in summary["main_findings"]) + """

## Claim Boundary

05B is a synthetic method-level phase/gauge/flux stress test. Phase diagnostics are toy diagnostics, not real quantum dynamics. No physical validation claim follows.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_result_note(path: Path, summary: Dict[str, Any], families: Sequence[Dict[str, Any]]) -> None:
    cols = [
        "phase_family_id",
        "expected_gauge_equivalent",
        "observed_gauge_equivalent",
        "gauge_invariant_loop_flux_rms",
        "low_eigenvalue_shift_vs_phase_zero",
    ]
    text = f"""# QSB-BRIDGE-NUM-05B Result Note

## 1. Purpose

QSB-BRIDGE-NUM-05B tests synthetic phase, gauge, and loop-flux families on one fixed magnitude matrix. It is a method-level toy stress test.

{intuition_section()}

## 2. Result

```text
gauge_flux_distinction_passed: {summary["gauge_flux_distinction_passed"]}
magnitude_distance_invariance_all_passed: {summary["magnitude_distance_invariance_all_passed"]}
threshold_graph_invariance_all_passed: {summary["threshold_graph_invariance_all_passed"]}
max_low_eigenvalue_shift_non_gauge: {summary["max_low_eigenvalue_shift_non_gauge"]}
stop_go_outcome: {summary["stop_go_outcome"]}
```

## 3. Phase Families

{table(families, cols)}

## 4. Interpretation

Gauge-equivalent phase changes are expected to cancel on closed loops. Loop-flux and adversarial non-gauge families are expected to produce nonzero loop closure and spectral response. Failure to separate those cases would be a negative method-level finding.

## 5. Claim Boundary

05B does not physically validate QSB. It does not show spacetime emergence, physical metric recovery, causal structure, physical geometry reconstruction, de-Broglie confirmation, or real quantum dynamics.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    config = load_simple_yaml(CONFIG_PATH)
    params = dict(config["parameters"])
    phase_params = dict(config["phase_parameters"])
    outputs = dict(config["outputs"])
    noise = dict(config["noise_sweep"])

    n = int(params["n_nodes"])
    l0 = float(params["l0"])
    tau = float(params["tau"])
    epsilon = float(params["epsilon"])
    flux_tol = float(params["loop_flux_tolerance"])
    low_count = int(params["low_eigenvalue_count"])

    mag = magnitude_matrix(n, l0)
    zero_dist = distance_matrix(mag, l0, epsilon)
    zero_edges = threshold_edges(mag, tau)
    zero_phi = matrix(n)
    zero_eigs = magnetic_laplacian_eigenvalues(mag, zero_phi)

    phase_rows: List[Dict[str, Any]] = []
    flux_rows: List[Dict[str, Any]] = []
    spectrum_rows: List[Dict[str, Any]] = []

    for family_id in config["phase_families"]:
        phi, expected_gauge = phase_family(family_id, n, phase_params)
        metrics = phase_metrics(mag, phi, zero_dist, zero_edges, l0, tau, epsilon)
        observed_gauge = metrics["gauge_invariant_loop_flux_rms"] <= flux_tol
        eigs = magnetic_laplacian_eigenvalues(mag, phi)
        spec = spectrum_summary(eigs, zero_eigs, low_count)
        row = {
            "phase_family_id": family_id,
            "expected_gauge_equivalent": expected_gauge,
            "observed_gauge_equivalent": observed_gauge,
            "gauge_flux_classification_correct": expected_gauge == observed_gauge,
            **metrics,
            **spec,
        }
        phase_rows.append(row)
        spectrum_rows.append(
            {
                "phase_family_id": family_id,
                "expected_gauge_equivalent": expected_gauge,
                **spec,
            }
        )
        for i, j, k, flux in loop_fluxes(phi):
            flux_rows.append(
                {
                    "phase_family_id": family_id,
                    "i": i,
                    "j": j,
                    "k": k,
                    "loop_flux": round_float(flux),
                    "abs_loop_flux": round_float(abs(flux)),
                    "expected_gauge_equivalent": expected_gauge,
                }
            )

    noise_rows: List[Dict[str, Any]] = []
    for sigma in noise["sigmas"]:
        phi = random_antisymmetric(n, int(noise["seed"]) + int(float(sigma) * 1000), float(sigma))
        metrics = phase_metrics(mag, phi, zero_dist, zero_edges, l0, tau, epsilon)
        eigs = magnetic_laplacian_eigenvalues(mag, phi)
        spec = spectrum_summary(eigs, zero_eigs, low_count)
        noise_rows.append(
            {
                "sigma": sigma,
                "gauge_invariant_loop_flux_rms": metrics["gauge_invariant_loop_flux_rms"],
                "phase_diagnostic_response": metrics["phase_diagnostic_response"],
                "low_eigenvalue_shift_vs_phase_zero": spec["low_eigenvalue_shift_vs_phase_zero"],
                "spectral_gap_shift": spec["spectral_gap_shift"],
                "phase_noise_breakdown_curve": spec["low_eigenvalue_shift_vs_phase_zero"],
            }
        )

    gauge_flux_distinction = all(row["gauge_flux_classification_correct"] for row in phase_rows)
    magnitude_all = all(row["magnitude_distance_invariance"] for row in phase_rows)
    threshold_all = all(row["threshold_graph_invariance"] for row in phase_rows)
    non_gauge_shifts = [
        float(row["low_eigenvalue_shift_vs_phase_zero"])
        for row in phase_rows
        if not row["expected_gauge_equivalent"]
    ]
    stop_go = "go_with_documented_boundaries" if gauge_flux_distinction else "revise_gauge_flux_diagnostics"

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "phase_family_count": len(phase_rows),
        "gauge_flux_distinction_passed": gauge_flux_distinction,
        "magnitude_distance_invariance_all_passed": magnitude_all,
        "threshold_graph_invariance_all_passed": threshold_all,
        "max_low_eigenvalue_shift_non_gauge": round_float(max(non_gauge_shifts)),
        "max_noise_sweep_low_eigenvalue_shift": round_float(max(float(r["low_eigenvalue_shift_vs_phase_zero"]) for r in noise_rows)),
        "stop_go_outcome": stop_go,
        "main_findings": [
            "Gauge-equivalent and loop-flux phase families are reported separately.",
            "Magnitude-only distance and threshold graph readouts remain invariant because |K_ij| is fixed.",
            "Loop-flux and adversarial phase families produce nonzero loop closure in this toy setting.",
            "Magnetic/Hermitian Laplacian spectra provide a phase-aware method-level readout.",
            "All claims remain toy-level and non-physical.",
        ],
        "claim_boundary": config["claim_boundary"],
        "output_files": outputs,
    }

    write_csv(project_path(outputs["phase_family_summary_csv"]), phase_rows, list(phase_rows[0].keys()))
    write_csv(project_path(outputs["gauge_flux_summary_csv"]), flux_rows, list(flux_rows[0].keys()))
    write_csv(project_path(outputs["laplacian_spectrum_summary_csv"]), spectrum_rows, list(spectrum_rows[0].keys()))
    write_csv(project_path(outputs["phase_noise_sweep_summary_csv"]), noise_rows, list(noise_rows[0].keys()))
    write_json(project_path(outputs["summary_json"]), summary)
    resolved = dict(config)
    resolved["repo_root"] = str(ROOT)
    resolved["triangle_loop_count_per_family"] = math.comb(n, 3)
    write_json(project_path(outputs["resolved_config_json"]), resolved)
    write_readout(project_path(outputs["readout_md"]), summary, phase_rows, spectrum_rows)
    write_result_note(project_path(outputs["result_note_md"]), summary, phase_rows)

    for key in [
        "summary_json",
        "readout_md",
        "phase_family_summary_csv",
        "gauge_flux_summary_csv",
        "laplacian_spectrum_summary_csv",
        "phase_noise_sweep_summary_csv",
        "resolved_config_json",
        "result_note_md",
    ]:
        print(f"wrote: {outputs[key]}")


if __name__ == "__main__":
    main()
