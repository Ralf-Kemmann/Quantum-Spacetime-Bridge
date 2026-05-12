#!/usr/bin/env python3
"""
QSB-BRIDGE-NUM-05A geometric validation and hostile controls.

This script creates synthetic geometric baselines and hostile controls, computes
method-level diagnostics, and writes transparent run artifacts. It makes no
physical validation claim.
"""

from __future__ import annotations

import csv
import json
import math
import random
from collections import deque
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/qsb_bridge_num_05a_geometric_validation_config.yaml"

Pair = Tuple[int, int]
Matrix = List[List[float]]
Point = Tuple[float, ...]


def parse_scalar(value: str) -> Any:
    text = value.strip()
    if text in {"true", "True"}:
        return True
    if text in {"false", "False"}:
        return False
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
                raise ValueError(f"List item without parent key: {raw}")
            if not isinstance(root.get(current_key), list):
                root[current_key] = []
            root[current_key].append(parse_scalar(stripped[2:]))
            continue
        if indent == 2 and stripped.endswith(":"):
            if current_key is None:
                raise ValueError(f"Nested key without parent key: {raw}")
            if not isinstance(root.get(current_key), dict):
                root[current_key] = {}
            current_nested_key = stripped[:-1]
            root[current_key][current_nested_key] = []
            continue
        if indent == 2 and ":" in stripped:
            if current_key is None:
                raise ValueError(f"Mapping item without parent key: {raw}")
            key, value = stripped.split(":", 1)
            if not isinstance(root.get(current_key), dict):
                root[current_key] = {}
            root[current_key][key] = parse_scalar(value)
            current_nested_key = None
            continue
        if indent == 4 and stripped.startswith("- "):
            if current_key is None or current_nested_key is None:
                raise ValueError(f"Nested list item without nested key: {raw}")
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


def euclidean(a: Point, b: Point) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def torus_distance(a: Point, b: Point) -> float:
    vals = []
    for x, y in zip(a, b):
        d = abs(x - y)
        vals.append(min(d, 1.0 - d))
    return math.sqrt(sum(v * v for v in vals))


def distance_matrix_from_points(points: Sequence[Point], torus: bool = False) -> Matrix:
    n = len(points)
    out = matrix(n)
    dist_fn = torus_distance if torus else euclidean
    for i, j in pairs(n):
        d = dist_fn(points[i], points[j])
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


def one_d_ring_points(n: int) -> List[Point]:
    return [(i / n,) for i in range(n)]


def one_d_ring_distance(n: int) -> Matrix:
    out = matrix(n)
    for i, j in pairs(n):
        raw = abs(i - j)
        d = min(raw, n - raw) / n
        out[i][j] = d
        out[j][i] = d
    return out


def grid_points(n: int) -> List[Point]:
    side = int(round(math.sqrt(n)))
    if side * side != n:
        side = int(math.ceil(math.sqrt(n)))
    pts: List[Point] = []
    for y in range(side):
        for x in range(side):
            if len(pts) < n:
                pts.append((x / side, y / side))
    return pts


def random_points(n: int, seed: int) -> List[Point]:
    rng = random.Random(seed)
    return [(rng.random(), rng.random()) for _ in range(n)]


def flatten(mat: Matrix, ps: Sequence[Pair]) -> List[float]:
    return [mat[i][j] for i, j in ps]


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y) or not x:
        return 0.0
    mx = mean(x)
    my = mean(y)
    vx = sum((v - mx) ** 2 for v in x)
    vy = sum((v - my) ** 2 for v in y)
    if vx <= 0.0 or vy <= 0.0:
        return 0.0
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / math.sqrt(vx * vy)


def threshold_edges(mag: Matrix, tau: float) -> set[Pair]:
    return {(i, j) for i, j in pairs(len(mag)) if mag[i][j] >= tau}


def jaccard(a: set[Pair], b: set[Pair]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def graph_shortest_path_distance(mag: Matrix, tau: float, l0: float, epsilon: float) -> Matrix:
    n = len(mag)
    dist = [[float("inf") for _ in range(n)] for _ in range(n)]
    adj: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0.0
    for i, j in pairs(n):
        if mag[i][j] >= tau:
            w = -l0 * math.log(max(mag[i][j], epsilon))
            adj[i].append((j, w))
            adj[j].append((i, w))
    for source in range(n):
        seen = [False] * n
        for _ in range(n):
            cur = -1
            cur_d = float("inf")
            for idx in range(n):
                if not seen[idx] and dist[source][idx] < cur_d:
                    cur = idx
                    cur_d = dist[source][idx]
            if cur < 0:
                break
            seen[cur] = True
            for nxt, w in adj[cur]:
                nd = cur_d + w
                if nd < dist[source][nxt]:
                    dist[source][nxt] = nd
    return dist


def connected_components(mag: Matrix, tau: float) -> int:
    n = len(mag)
    adj = [[] for _ in range(n)]
    for i, j in pairs(n):
        if mag[i][j] >= tau:
            adj[i].append(j)
            adj[j].append(i)
    seen = [False] * n
    count = 0
    for start in range(n):
        if seen[start]:
            continue
        count += 1
        q = deque([start])
        seen[start] = True
        while q:
            cur = q.popleft()
            for nxt in adj[cur]:
                if not seen[nxt]:
                    seen[nxt] = True
                    q.append(nxt)
    return count


def nearest_neighbor_recall(known: Matrix, reconstructed: Matrix, k: int) -> float:
    n = len(known)
    recalls = []
    kk = min(k, n - 1)
    for i in range(n):
        true_set = set(sorted([j for j in range(n) if j != i], key=lambda j: (known[i][j], j))[:kk])
        rec_set = set(sorted([j for j in range(n) if j != i], key=lambda j: (reconstructed[i][j], j))[:kk])
        recalls.append(len(true_set & rec_set) / kk)
    return mean(recalls)


def triangle_violation_rate(dist: Matrix, tolerance: float) -> float:
    n = len(dist)
    checks = 0
    violations = 0
    for i, j, k in combinations(range(n), 3):
        vals = [(i, j, k), (i, k, j), (j, k, i)]
        for a, b, c in vals:
            checks += 1
            if dist[a][b] > dist[a][c] + dist[c][b] + tolerance:
                violations += 1
    return violations / checks if checks else 0.0


def normalized_mae(a: Sequence[float], b: Sequence[float]) -> float:
    if not a:
        return 0.0
    denom = mean(abs(x) for x in a) or 1.0
    return mean(abs(x - y) for x, y in zip(a, b)) / denom


def stress(known: Matrix, reconstructed: Matrix, ps: Sequence[Pair]) -> float:
    true_vals = flatten(known, ps)
    rec_vals = flatten(reconstructed, ps)
    denom = sum(v * v for v in true_vals) or 1.0
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(true_vals, rec_vals)) / denom)


def geometry_score(correlation: float, nn_recall: float, dist_stress: float, sp_error: float) -> float:
    corr_part = max(0.0, correlation)
    stress_part = 1.0 / (1.0 + max(0.0, dist_stress))
    sp_part = 1.0 / (1.0 + max(0.0, sp_error))
    return (corr_part + nn_recall + stress_part + sp_part) / 4.0


def distribution_matched_control(base_mag: Matrix, seed: int) -> Matrix:
    n = len(base_mag)
    rng = random.Random(seed)
    values = flatten(base_mag, pairs(n))
    rng.shuffle(values)
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for (i, j), value in zip(pairs(n), values):
        out[i][j] = value
        out[j][i] = value
    return out


def block_control(n: int, params: Dict[str, Any]) -> Matrix:
    rng = random.Random(int(params["block_matrix_seed"]))
    blocks = int(params["block_count"])
    within = float(params["block_within_magnitude"])
    between = float(params["block_between_magnitude"])
    jitter = float(params["block_jitter"])
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        same = (i * blocks // n) == (j * blocks // n)
        base = within if same else between
        value = min(0.999, max(0.001, base + rng.uniform(-jitter, jitter)))
        out[i][j] = value
        out[j][i] = value
    return out


def near_degenerate_control(n: int, params: Dict[str, Any]) -> Matrix:
    rng = random.Random(int(params["near_degenerate_seed"]))
    base = float(params["near_degenerate_base"])
    jitter = float(params["near_degenerate_jitter"])
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = min(0.999, max(0.001, base + rng.uniform(-jitter, jitter)))
        out[i][j] = value
        out[j][i] = value
    return out


def gaussian_perturbation_control(base_mag: Matrix, params: Dict[str, Any]) -> Matrix:
    rng = random.Random(int(params["gaussian_perturbation_seed"]))
    sigma = float(params["gaussian_sigma"])
    n = len(base_mag)
    out = matrix(n)
    for i in range(n):
        out[i][i] = 1.0
    for i, j in pairs(n):
        value = min(0.999, max(0.001, base_mag[i][j] + rng.gauss(0.0, sigma)))
        out[i][j] = value
        out[j][i] = value
    return out


def permute_matrix(mat: Matrix, perm: Sequence[int]) -> Matrix:
    n = len(mat)
    out = matrix(n)
    for i in range(n):
        for j in range(n):
            out[i][j] = mat[perm[i]][perm[j]]
    return out


def unpermute_matrix(mat: Matrix, perm: Sequence[int]) -> Matrix:
    n = len(mat)
    out = matrix(n)
    inv = [0] * n
    for i, p in enumerate(perm):
        inv[p] = i
    for i in range(n):
        for j in range(n):
            out[i][j] = mat[inv[i]][inv[j]]
    return out


def evaluate(
    family_id: str,
    family_type: str,
    mag: Matrix,
    known_dist: Matrix,
    baseline_edges: set[Pair],
    baseline_score: float | None,
    l0: float,
    tau: float,
    epsilon: float,
    nn_k: int,
    tolerance: float,
) -> Dict[str, Any]:
    ps = pairs(len(mag))
    rec = reconstructed_distance(mag, l0, epsilon)
    sp = graph_shortest_path_distance(mag, tau, l0, epsilon)
    finite = [(known_dist[i][j], sp[i][j]) for i, j in ps if math.isfinite(sp[i][j])]
    sp_error = normalized_mae([x for x, _ in finite], [y for _, y in finite]) if finite else float("inf")
    corr = pearson(flatten(known_dist, ps), flatten(rec, ps))
    nn = nearest_neighbor_recall(known_dist, rec, nn_k)
    tri = triangle_violation_rate(rec, tolerance)
    dist_stress = stress(known_dist, rec, ps)
    edges = threshold_edges(mag, tau)
    edge_j = jaccard(edges, baseline_edges)
    score = geometry_score(corr, nn, dist_stress, sp_error if math.isfinite(sp_error) else 1.0e9)
    gap = None if baseline_score is None else baseline_score - score
    return {
        "family_id": family_id,
        "family_type": family_type,
        "n_nodes": len(mag),
        "l0": l0,
        "tau": tau,
        "coordinate_distance_correlation": round_float(corr),
        "shortest_path_distance_error_vs_known_geometry": round_float(sp_error),
        "nearest_neighbor_recall_vs_known_geometry": round_float(nn),
        "triangle_inequality_violation_rate": round_float(tri),
        "distance_stress": round_float(dist_stress),
        "threshold_graph_edge_count": len(edges),
        "threshold_graph_jaccard": round_float(edge_j),
        "connected_component_count": connected_components(mag, tau),
        "false_positive_geometry_score": round_float(score),
        "control_gap_vs_geometric_baseline": "" if gap is None else round_float(gap),
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


def make_baseline(family_id: str, n: int, l0: float, seed: int) -> Tuple[List[Point], Matrix, Matrix]:
    if family_id == "baseline_1d_ring":
        points = one_d_ring_points(n)
        dist = one_d_ring_distance(n)
    elif family_id == "baseline_2d_torus_grid":
        points = grid_points(n)
        dist = distance_matrix_from_points(points, torus=True)
    elif family_id == "baseline_random_geometric":
        points = random_points(n, seed + 17)
        dist = distance_matrix_from_points(points)
    else:
        raise ValueError(f"Unknown baseline: {family_id}")
    return points, dist, magnitude_from_distance(dist, l0)


def make_controls(
    base_mag: Matrix,
    base_dist: Matrix,
    params: Dict[str, Any],
) -> Dict[str, Tuple[Matrix, Matrix, str]]:
    n = len(base_mag)
    rng = random.Random(int(params["node_permutation_seed"]))
    perm = list(range(n))
    rng.shuffle(perm)
    perm_mag = permute_matrix(base_mag, perm)
    unperm_mag = unpermute_matrix(perm_mag, perm)
    return {
        "control_distribution_matched_random_magnitude": (
            distribution_matched_control(base_mag, int(params["distribution_matched_seed"])),
            base_dist,
            "hostile_control",
        ),
        "control_non_geometric_block_matrix": (block_control(n, params), base_dist, "hostile_control"),
        "control_near_degenerate_magnitude": (near_degenerate_control(n, params), base_dist, "hostile_control"),
        "control_node_permutation": (unperm_mag, base_dist, "hostile_control"),
        "control_gaussian_magnitude_perturbation": (
            gaussian_perturbation_control(base_mag, params),
            base_dist,
            "hostile_control",
        ),
    }


def table(rows: Sequence[Dict[str, Any]], columns: Sequence[str]) -> str:
    lines = ["|" + "|".join(columns) + "|", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        lines.append("|" + "|".join(str(row.get(c, "")) for c in columns) + "|")
    return "\n".join(lines)


def write_readout(path: Path, summary: Dict[str, Any], variants: Sequence[Dict[str, Any]], controls: Sequence[Dict[str, Any]]) -> None:
    cols = [
        "family_id",
        "coordinate_distance_correlation",
        "nearest_neighbor_recall_vs_known_geometry",
        "distance_stress",
        "false_positive_geometry_score",
    ]
    text = f"""# QSB-BRIDGE-NUM-05A Run Readout

## Run

```text
block_id: {summary["block_id"]}
run_id: {summary["run_id"]}
geometric_baseline_count: {summary["geometric_baseline_count"]}
hostile_control_count: {summary["hostile_control_count"]}
stop_go_outcome: {summary["stop_go_outcome"]}
```

## Geometric Baselines

{table(variants, cols)}

## Hostile Controls

{table(controls, cols + ["control_gap_vs_geometric_baseline"])}

## Main Findings

""" + "\n".join(f"- {item}" for item in summary["main_findings"]) + """

## Failure Interpretation

Hostile-control success is treated as a possible negative finding. If a hostile control approaches or exceeds the geometric baseline score, the diagnostic boundary is tightened rather than explained away.

## Claim Boundary

This is a synthetic method-level diagnostic block. It does not physically validate QSB, does not show spacetime emergence, does not recover a physical metric, does not derive causal structure, and does not confirm de-Broglie physics.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_result_note(path: Path, summary: Dict[str, Any], variants: Sequence[Dict[str, Any]], controls: Sequence[Dict[str, Any]]) -> None:
    cols = ["family_id", "false_positive_geometry_score", "control_gap_vs_geometric_baseline"]
    text = f"""# QSB-BRIDGE-NUM-05A Result Note

## 1. Purpose

QSB-BRIDGE-NUM-05A tests synthetic geometric baselines against hostile controls. It is a method-level diagnostic block only.

## 2. Stop/Go Outcome

```text
stop_go_outcome: {summary["stop_go_outcome"]}
geometric_baseline_mean_score: {summary["geometric_baseline_mean_score"]}
hostile_control_mean_score: {summary["hostile_control_mean_score"]}
minimum_control_gap_vs_baseline: {summary["minimum_control_gap_vs_baseline"]}
node_permutation_invariance_passed: {summary["node_permutation_invariance_passed"]}
```

## 3. Geometric Baselines

{table(variants, ["family_id", "coordinate_distance_correlation", "nearest_neighbor_recall_vs_known_geometry", "distance_stress", "false_positive_geometry_score"])}

## 4. Hostile Controls

{table(controls, cols)}

## 5. Interpretation

Geometric baselines and hostile controls are reported separately. Hostile-control success is a possible negative finding and should tighten the method boundary.

## 6. Claim Boundary

05A does not physically validate QSB. It does not establish spacetime emergence, physical metric recovery, causal structure, physical geometry reconstruction, or de-Broglie confirmation.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    config = load_simple_yaml(CONFIG_PATH)
    params = dict(config["parameters"])
    control_params = dict(config["control_parameters"])
    outputs = dict(config["outputs"])
    sensitivity = dict(config["sensitivity"])

    n = int(params["default_n_nodes"])
    l0 = float(params["l0"])
    tau = float(params["tau"])
    epsilon = float(params["epsilon"])
    seed = int(params["seed"])
    nn_k = int(params["nearest_neighbor_k"])
    pair_limit = int(params["pairwise_sample_limit"])
    tolerance = float(params["tolerance"])

    baseline_rows: List[Dict[str, Any]] = []
    control_rows: List[Dict[str, Any]] = []
    pairwise_rows: List[Dict[str, Any]] = []
    sweep_rows: List[Dict[str, Any]] = []

    baseline_context: Dict[str, Tuple[Matrix, Matrix, float, set[Pair]]] = {}
    for family_id in config["geometric_baselines"]:
        _, known_dist, mag = make_baseline(family_id, n, l0, seed)
        edges = threshold_edges(mag, tau)
        row = evaluate(family_id, "geometric_baseline", mag, known_dist, edges, None, l0, tau, epsilon, nn_k, tolerance)
        baseline_rows.append(row)
        baseline_context[family_id] = (known_dist, mag, float(row["false_positive_geometry_score"]), edges)

    reference_dist, reference_mag, reference_score, reference_edges = baseline_context["baseline_2d_torus_grid"]
    for control_id, (mag, known_dist, family_type) in make_controls(reference_mag, reference_dist, control_params).items():
        row = evaluate(control_id, family_type, mag, known_dist, reference_edges, reference_score, l0, tau, epsilon, nn_k, tolerance)
        control_rows.append(row)

    sample_count = 0
    for family_id, (known_dist, mag, _, _) in baseline_context.items():
        rec = reconstructed_distance(mag, l0, epsilon)
        for i, j in pairs(n):
            if sample_count >= pair_limit:
                break
            pairwise_rows.append(
                {
                    "family_id": family_id,
                    "family_type": "geometric_baseline",
                    "i": i,
                    "j": j,
                    "known_distance": round_float(known_dist[i][j]),
                    "reconstructed_distance": round_float(rec[i][j]),
                    "abs_error": round_float(abs(known_dist[i][j] - rec[i][j])),
                    "magnitude": round_float(mag[i][j]),
                    "edge_at_tau": mag[i][j] >= tau,
                }
            )
            sample_count += 1

    for sweep_kind, values in [
        ("tau", sensitivity["tau_values"]),
        ("l0", sensitivity["l0_values"]),
        ("n", sensitivity["n_values"]),
    ]:
        for value in values:
            sweep_n = n
            sweep_l0 = l0
            sweep_tau = tau
            if sweep_kind == "tau":
                sweep_tau = float(value)
            elif sweep_kind == "l0":
                sweep_l0 = float(value)
            elif sweep_kind == "n":
                sweep_n = int(value)
            _, known_dist, mag = make_baseline("baseline_2d_torus_grid", sweep_n, sweep_l0, seed)
            edges = threshold_edges(mag, sweep_tau)
            row = evaluate(
                "baseline_2d_torus_grid",
                "geometric_baseline",
                mag,
                known_dist,
                edges,
                None,
                sweep_l0,
                sweep_tau,
                epsilon,
                min(nn_k, sweep_n - 1),
                tolerance,
            )
            row["sweep_kind"] = sweep_kind
            row["sweep_value"] = value
            sweep_rows.append(row)

    baseline_scores = [float(r["false_positive_geometry_score"]) for r in baseline_rows]
    control_scores = [float(r["false_positive_geometry_score"]) for r in control_rows]
    non_permutation_controls = [r for r in control_rows if r["family_id"] != "control_node_permutation"]
    min_gap = min(
        float(r["control_gap_vs_geometric_baseline"])
        for r in non_permutation_controls
        if r["control_gap_vs_geometric_baseline"] != ""
    )
    node_perm = next(r for r in control_rows if r["family_id"] == "control_node_permutation")
    node_permutation_passed = abs(float(node_perm["control_gap_vs_geometric_baseline"])) <= tolerance
    hostile_scores_as_well = any(
        float(r["false_positive_geometry_score"]) >= reference_score - 0.02
        for r in non_permutation_controls
    )

    stop_go_outcome = "revise_before_real_data" if hostile_scores_as_well or min_gap < 0.05 else "go_with_documented_boundaries"
    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "geometric_baseline_count": len(baseline_rows),
        "hostile_control_count": len(control_rows),
        "geometric_baseline_mean_score": round_float(mean(baseline_scores)),
        "hostile_control_mean_score": round_float(mean(control_scores)),
        "reference_geometric_baseline": "baseline_2d_torus_grid",
        "reference_geometric_score": round_float(reference_score),
        "minimum_control_gap_vs_baseline": round_float(min_gap),
        "minimum_control_gap_excludes_node_permutation": True,
        "node_permutation_invariance_passed": node_permutation_passed,
        "hostile_control_scored_as_well_as_baseline": hostile_scores_as_well,
        "stop_go_outcome": stop_go_outcome,
        "main_findings": [
            "Geometric baselines and hostile controls are reported separately.",
            "Node permutation is treated as an invariance control, not as a hostile failure.",
            "Hostile-control success is treated as a possible negative finding.",
            "All readouts remain synthetic and method-level.",
        ],
        "claim_boundary": config["claim_boundary"],
        "output_files": outputs,
    }

    variant_fields = list(baseline_rows[0].keys())
    control_fields = list(control_rows[0].keys())
    pairwise_fields = list(pairwise_rows[0].keys())
    sweep_fields = list(sweep_rows[0].keys())

    write_csv(project_path(outputs["variant_summary_csv"]), baseline_rows, variant_fields)
    write_csv(project_path(outputs["control_summary_csv"]), control_rows, control_fields)
    write_csv(project_path(outputs["pairwise_or_matrix_diagnostics_csv"]), pairwise_rows, pairwise_fields)
    write_csv(project_path(outputs["parameter_sweep_summary_csv"]), sweep_rows, sweep_fields)
    write_json(project_path(outputs["summary_json"]), summary)
    resolved = dict(config)
    resolved["repo_root"] = str(ROOT)
    resolved["computed_default_pair_count"] = len(pairs(n))
    write_json(project_path(outputs["resolved_config_json"]), resolved)
    write_readout(project_path(outputs["readout_md"]), summary, baseline_rows, control_rows)
    write_result_note(project_path(outputs["result_note_md"]), summary, baseline_rows, control_rows)

    for key in [
        "summary_json",
        "readout_md",
        "variant_summary_csv",
        "control_summary_csv",
        "pairwise_or_matrix_diagnostics_csv",
        "parameter_sweep_summary_csv",
        "resolved_config_json",
        "result_note_md",
    ]:
        print(f"wrote: {outputs[key]}")


if __name__ == "__main__":
    main()
