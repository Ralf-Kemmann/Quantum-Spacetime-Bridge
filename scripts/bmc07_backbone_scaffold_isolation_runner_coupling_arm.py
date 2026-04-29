#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise SystemExit("NumPy is required: pip install numpy") from exc


NodeId = str
Edge = Tuple[NodeId, NodeId, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open BMC-07b runner with explicit coupling arm."
    )
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_edge_table(path: Path, source_col: str, target_col: str, weight_col: str) -> List[Edge]:
    edges: List[Edge] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {source_col, target_col, weight_col}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing edge columns: {sorted(missing)}")
        for row in reader:
            u = str(row[source_col]).strip()
            v = str(row[target_col]).strip()
            if not u or not v or u == v:
                continue
            w = float(row[weight_col])
            a, b = sorted((u, v))
            edges.append((a, b, w))
    merged: Dict[Tuple[str, str], float] = defaultdict(float)
    for u, v, w in edges:
        merged[(u, v)] += w
    return [(u, v, w) for (u, v), w in sorted(merged.items())]


def load_node_metadata(path: Path) -> Dict[NodeId, dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if "node_id" not in (reader.fieldnames or []):
            raise ValueError("node_metadata.csv must contain 'node_id'")
        result: Dict[NodeId, dict] = {}
        for row in reader:
            node_id = str(row["node_id"]).strip()
            if node_id:
                result[node_id] = row
    return result


def incidence_strength(edges: Sequence[Edge]) -> Dict[NodeId, float]:
    strength: Dict[NodeId, float] = defaultdict(float)
    for u, v, w in edges:
        strength[u] += w
        strength[v] += w
    return dict(strength)


def derive_backbone_nodes(
    edges: Sequence[Edge],
    node_meta: Dict[NodeId, dict],
    hint_column: Optional[str],
    alpha: float,
) -> List[NodeId]:
    if hint_column and node_meta and all(hint_column in row for row in node_meta.values()):
        hinted = sorted(
            node_id for node_id, row in node_meta.items()
            if str(row.get(hint_column, "")).strip() in {"1", "true", "True", "yes", "YES"}
        )
        if hinted:
            return hinted

    strengths = incidence_strength(edges)
    all_nodes = sorted({u for u, _, _ in edges} | {v for _, v, _ in edges})
    if not all_nodes:
        return []
    n_keep = max(1, math.ceil(alpha * len(all_nodes)))
    ranked = sorted(all_nodes, key=lambda n: (-strengths.get(n, 0.0), n))
    return ranked[:n_keep]


def get_shell_index(node_meta: Dict[NodeId, dict], node_id: NodeId) -> int:
    row = node_meta.get(node_id, {})
    value = row.get("shell_index", 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def is_coupling_edge(u: str, v: str, backbone_nodes: set[str]) -> bool:
    return (u in backbone_nodes) ^ (v in backbone_nodes)


def select_arm_edges(edges: Sequence[Edge], backbone_nodes: set[str], arm_name: str) -> List[Edge]:
    if arm_name == "full_graph":
        return list(edges)
    if arm_name == "backbone_only":
        return [(u, v, w) for u, v, w in edges if u in backbone_nodes and v in backbone_nodes]
    if arm_name == "off_backbone_only":
        return [(u, v, w) for u, v, w in edges if u not in backbone_nodes and v not in backbone_nodes]
    if arm_name == "coupling_only":
        return [(u, v, w) for u, v, w in edges if is_coupling_edge(u, v, backbone_nodes)]
    raise ValueError(f"Unknown arm: {arm_name}")


def edge_nodes(edges: Sequence[Edge]) -> List[NodeId]:
    return sorted({u for u, _, _ in edges} | {v for _, v, _ in edges})


def weighted_shell_gap(edges: Sequence[Edge], node_meta: Dict[NodeId, dict]) -> float:
    total_weight = sum(w for _, _, w in edges)
    if total_weight <= 0.0:
        return 0.0
    value = 0.0
    for u, v, w in edges:
        gap = abs(get_shell_index(node_meta, u) - get_shell_index(node_meta, v))
        value += w * gap
    return value / total_weight


def same_shell_weight_fraction(edges: Sequence[Edge], node_meta: Dict[NodeId, dict]) -> float:
    total_weight = sum(w for _, _, w in edges)
    if total_weight <= 0.0:
        return 0.0
    same_weight = sum(
        w for u, v, w in edges
        if get_shell_index(node_meta, u) == get_shell_index(node_meta, v)
    )
    return same_weight / total_weight


def shuffle_weights_only(edges: Sequence[Edge], rng: random.Random) -> List[Edge]:
    weights = [w for _, _, w in edges]
    rng.shuffle(weights)
    return [(u, v, weights[i]) for i, (u, v, _) in enumerate(edges)]


def build_adjacency(edges: Sequence[Edge], nodes: Sequence[NodeId]) -> np.ndarray:
    index = {node: i for i, node in enumerate(nodes)}
    matrix = np.zeros((len(nodes), len(nodes)), dtype=float)
    for u, v, w in edges:
        i = index[u]
        j = index[v]
        matrix[i, j] += w
        matrix[j, i] += w
    return matrix


def normalized_adjacency(edges: Sequence[Edge], nodes: Sequence[NodeId]) -> np.ndarray:
    adj = build_adjacency(edges, nodes)
    total = adj.sum()
    if total > 0:
        adj = adj / total
    return adj


def shortest_path_distance_matrix(edges: Sequence[Edge], nodes: Sequence[NodeId]) -> np.ndarray:
    index = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)
    inf = float("inf")
    dist = np.full((n, n), inf, dtype=float)
    for i in range(n):
        dist[i, i] = 0.0
    for u, v, w in edges:
        if w <= 0:
            continue
        i = index[u]
        j = index[v]
        d = 1.0 / w
        if d < dist[i, j]:
            dist[i, j] = d
            dist[j, i] = d
    for k in range(n):
        dist = np.minimum(dist, dist[:, [k]] + dist[[k], :])
    finite = np.isfinite(dist)
    if finite.any():
        max_finite = float(np.max(dist[finite]))
        dist[~finite] = max_finite
    else:
        dist[:] = 0.0
    return dist


def load_optional_npz_matrix(path: Optional[Path]) -> Optional[np.ndarray]:
    if path is None or not path.exists():
        return None
    data = np.load(path, allow_pickle=False)
    if "matrix" in data:
        return np.asarray(data["matrix"], dtype=float)
    first_key = sorted(data.files)[0]
    return np.asarray(data[first_key], dtype=float)


def mean_abs_matrix_difference(a: Optional[np.ndarray], b: Optional[np.ndarray]) -> Optional[float]:
    if a is None or b is None or a.shape != b.shape:
        return None
    return float(np.mean(np.abs(a - b)))


def summarize_arm(
    arm_name: str,
    edges: Sequence[Edge],
    node_meta: Dict[NodeId, dict],
    repeats: int,
    rng: random.Random,
    diffusion_reference: Optional[np.ndarray],
    pair_reference: Optional[np.ndarray],
) -> Tuple[dict, List[dict]]:
    nodes = edge_nodes(edges)
    total_weight = sum(w for _, _, w in edges)
    observed_gap = weighted_shell_gap(edges, node_meta)
    same_shell_fraction = same_shell_weight_fraction(edges, node_meta)

    repeat_rows: List[dict] = []
    shuffled_gaps: List[float] = []
    for repeat_index in range(repeats):
        shuffled = shuffle_weights_only(edges, rng)
        gap = weighted_shell_gap(shuffled, node_meta)
        shuffled_gaps.append(gap)
        repeat_rows.append(
            {
                "arm_name": arm_name,
                "repeat_index": repeat_index,
                "shuffle_weighted_shell_gap": gap,
            }
        )

    shuffle_mean = float(np.mean(shuffled_gaps)) if shuffled_gaps else 0.0
    shuffle_std = float(np.std(shuffled_gaps)) if shuffled_gaps else 0.0
    arrangement_signal = shuffle_mean - observed_gap
    shell_order_drift = abs(arrangement_signal)

    adjacency = normalized_adjacency(edges, nodes) if nodes else np.zeros((0, 0))
    distances = shortest_path_distance_matrix(edges, nodes) if nodes else np.zeros((0, 0))
    pair_shift = mean_abs_matrix_difference(adjacency, pair_reference)
    diffusion_shift = mean_abs_matrix_difference(distances, diffusion_reference)

    summary = {
        "arm_name": arm_name,
        "edge_count": len(edges),
        "node_count": len(nodes),
        "total_weight": total_weight,
        "same_shell_weight_fraction": same_shell_fraction,
        "weighted_shell_gap": observed_gap,
        "shuffle_mean_gap": shuffle_mean,
        "shuffle_std_gap": shuffle_std,
        "arrangement_signal": arrangement_signal,
        "shell_order_drift": shell_order_drift,
        "diffusion_shift": diffusion_shift,
        "pair_neighborhood_shift": pair_shift,
    }
    return summary, repeat_rows


def write_csv(path: Path, rows: List[dict], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def rank_arms_by_signal(arms: Dict[str, dict]) -> List[Tuple[str, float]]:
    ranking = [(name, values["arrangement_signal"]) for name, values in arms.items()]
    ranking.sort(key=lambda x: (-x[1], x[0]))
    return ranking


def decision_label(
    arms: Dict[str, dict],
    arrangement_min: float,
    dominance_gap_min: float,
    minimum_arm_edge_count: int,
) -> Tuple[str, Optional[str], List[Tuple[str, float]]]:
    ranking = rank_arms_by_signal(arms)
    dominant_arm = ranking[0][0] if ranking else None

    def eligible(name: str) -> bool:
        arm = arms.get(name)
        return bool(arm) and arm["edge_count"] >= minimum_arm_edge_count

    def dominates(name: str, others: List[str]) -> bool:
        if not eligible(name):
            return False
        base = arms[name]["arrangement_signal"]
        if base < arrangement_min:
            return False
        for other in others:
            other_signal = arms.get(other, {}).get("arrangement_signal", float("-inf"))
            if base - other_signal < dominance_gap_min:
                return False
        return True

    if dominates("coupling_only", ["backbone_only", "off_backbone_only"]):
        return "coupling_localization_supported", dominant_arm, ranking
    if dominates("backbone_only", ["off_backbone_only", "coupling_only"]):
        return "backbone_localization_supported", dominant_arm, ranking
    if dominates("off_backbone_only", ["backbone_only", "coupling_only"]):
        return "off_backbone_localization_supported", dominant_arm, ranking

    full = arms.get("full_graph")
    if full and full["arrangement_signal"] >= arrangement_min:
        return "full_only_or_mixed", dominant_arm, ranking

    return "weak_or_inconclusive", dominant_arm, ranking


def render_readout(summary: dict) -> str:
    lines = [
        f"# BMC-07b Minimal Readout – {summary['run_id']}",
        "",
        "## Befund",
        "",
        f"- Decision label: `{summary['decision_label']}`",
        f"- Dominant arm: `{summary.get('dominant_arm')}`",
        f"- Backbone nodes: `{summary['backbone_node_count']}`",
        f"- Off-backbone nodes: `{summary['off_backbone_node_count']}`",
        f"- Coupling edges: `{summary['coupling_edge_count']}`",
        "",
        "## Arm summary",
        "",
        "| arm | edge_count | node_count | total_weight | arrangement_signal | shell_order_drift |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm_name in ["full_graph", "backbone_only", "off_backbone_only", "coupling_only"]:
        arm = summary["arms"].get(arm_name)
        if not arm:
            continue
        lines.append(
            f"| `{arm_name}` | {arm['edge_count']} | {arm['node_count']} | "
            f"{arm['total_weight']:.6f} | {arm['arrangement_signal']:.6f} | "
            f"{arm['shell_order_drift']:.6f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "BMC-07b remains a minimal defensive localization block. "
        "A clear claim requires a dominant arm above threshold and above the other partial arms.",
        "",
        "## Hypothese",
        "",
        "If coupling edges are the relevant local interface, the coupling arm should dominate backbone-only and off-backbone-only.",
        "",
        "## Offene Lücke",
        "",
        "Backbone construction and the dataset itself remain minimal; neither should be over-read as structural proof.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_yaml(config_path)
    project_root = config_path.parent.parent

    run_cfg = config.get("run", {})
    inputs_cfg = config.get("inputs", {})
    graph_cfg = config.get("graph", {})
    backbone_cfg = config.get("backbone", {})
    arms_cfg = config.get("arms", {})
    perturb_cfg = config.get("perturbation", {})
    decision_cfg = config.get("decision", {})

    edges = load_edge_table(
        project_root / inputs_cfg["baseline_relational_table"],
        graph_cfg.get("source_column", "source"),
        graph_cfg.get("target_column", "target"),
        graph_cfg.get("weight_column", "weight"),
    )
    node_meta = load_node_metadata(project_root / inputs_cfg["node_metadata"])

    backbone_nodes = derive_backbone_nodes(
        edges=edges,
        node_meta=node_meta,
        hint_column=backbone_cfg.get("hint_column"),
        alpha=float(backbone_cfg.get("alpha", 0.2)),
    )
    backbone_set = set(backbone_nodes)
    all_nodes = sorted({u for u, _, _ in edges} | {v for _, v, _ in edges})
    off_backbone_nodes = [n for n in all_nodes if n not in backbone_set]

    output_dir = project_root / run_cfg.get("output_dir", "runs/BMC-07/BMC07b_coupling_arm_open")
    output_dir.mkdir(parents=True, exist_ok=True)

    repeats = int(perturb_cfg.get("repeats", 20))
    seed = int(run_cfg.get("seed", 101))
    rng = random.Random(seed)

    diffusion_reference = load_optional_npz_matrix(
        project_root / inputs_cfg["diffusion_distance_matrix"]
        if inputs_cfg.get("diffusion_distance_matrix") else None
    )
    pair_reference = load_optional_npz_matrix(
        project_root / inputs_cfg["pair_neighborhood_matrix"]
        if inputs_cfg.get("pair_neighborhood_matrix") else None
    )

    arm_names: List[str] = []
    if arms_cfg.get("evaluate_full_graph", True):
        arm_names.append("full_graph")
    if arms_cfg.get("evaluate_backbone_only", True):
        arm_names.append("backbone_only")
    if arms_cfg.get("evaluate_off_backbone_only", True):
        arm_names.append("off_backbone_only")
    if arms_cfg.get("evaluate_coupling_only", True):
        arm_names.append("coupling_only")

    arm_rows: List[dict] = []
    repeat_rows: List[dict] = []
    arm_map: Dict[str, dict] = {}

    for arm_name in arm_names:
        arm_edges = select_arm_edges(edges, backbone_set, arm_name)
        summary, repeats_for_arm = summarize_arm(
            arm_name=arm_name,
            edges=arm_edges,
            node_meta=node_meta,
            repeats=repeats,
            rng=rng,
            diffusion_reference=diffusion_reference,
            pair_reference=pair_reference,
        )
        arm_rows.append(summary)
        repeat_rows.extend(repeats_for_arm)
        arm_map[arm_name] = summary

    label, dominant_arm, arm_signal_ranking = decision_label(
        arm_map,
        arrangement_min=float(decision_cfg.get("arrangement_signal_min", 0.05)),
        dominance_gap_min=float(decision_cfg.get("dominance_gap_min", 0.03)),
        minimum_arm_edge_count=int(decision_cfg.get("minimum_arm_edge_count", 2)),
    )

    summary = {
        "run_id": run_cfg.get("run_id", "BMC07b_coupling_arm_open"),
        "decision_label": label,
        "dominant_arm": dominant_arm,
        "arm_signal_ranking": [
            {"arm_name": arm_name, "arrangement_signal": arrangement_signal}
            for arm_name, arrangement_signal in arm_signal_ranking
        ],
        "backbone_node_count": len(backbone_nodes),
        "off_backbone_node_count": len(off_backbone_nodes),
        "coupling_edge_count": len(select_arm_edges(edges, backbone_set, "coupling_only")),
        "arms": arm_map,
    }

    validation = {
        "baseline_edge_count": len(edges),
        "baseline_node_count": len(all_nodes),
        "backbone_fraction": (len(backbone_nodes) / len(all_nodes)) if all_nodes else 0.0,
        "backbone_has_nodes": len(backbone_nodes) > 0,
        "off_backbone_has_nodes": len(off_backbone_nodes) > 0,
        "coupling_edge_count_positive": summary["coupling_edge_count"] > 0,
        "minimum_arm_edge_count": int(decision_cfg.get("minimum_arm_edge_count", 2)),
        "repeat_count_configured": repeats,
        "optional_diffusion_reference_present": diffusion_reference is not None,
        "optional_pair_reference_present": pair_reference is not None,
    }

    metadata = {
        "runner_name": Path(__file__).name,
        "config_path": str(config_path),
        "seed": seed,
        "notes": [
            "Open BMC-07b coupling-arm runner.",
            "No hidden calculations.",
            "Arrangement signal is defined against weight-shuffle reference on fixed topology.",
            "Coupling-only arm is defined by XOR backbone membership of edge endpoints.",
        ],
    }

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (output_dir / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_csv(
        output_dir / "arm_metrics.csv",
        arm_rows,
        fieldnames=[
            "arm_name", "edge_count", "node_count", "total_weight",
            "same_shell_weight_fraction", "weighted_shell_gap",
            "shuffle_mean_gap", "shuffle_std_gap", "arrangement_signal",
            "shell_order_drift", "diffusion_shift", "pair_neighborhood_shift",
        ],
    )
    write_csv(
        output_dir / "repeat_metrics.csv",
        repeat_rows,
        fieldnames=["arm_name", "repeat_index", "shuffle_weighted_shell_gap"],
    )
    (output_dir / "readout.md").write_text(render_readout(summary), encoding="utf-8")
    print(f"Wrote outputs to: {output_dir}")


if __name__ == "__main__":
    main()
