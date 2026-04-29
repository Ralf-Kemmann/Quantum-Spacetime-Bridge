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
        description="Open BMC-07c runner for backbone-definition variation."
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


def same_shell_incidence(node_meta: Dict[NodeId, dict], edges: Sequence[Edge]) -> Dict[NodeId, float]:
    values: Dict[NodeId, float] = defaultdict(float)
    for u, v, w in edges:
        if get_shell_index(node_meta, u) == get_shell_index(node_meta, v):
            values[u] += w
            values[v] += w
    return dict(values)


def same_shell_fraction_per_node(node_meta: Dict[NodeId, dict], edges: Sequence[Edge]) -> Dict[NodeId, float]:
    total = incidence_strength(edges)
    same = same_shell_incidence(node_meta, edges)
    out: Dict[NodeId, float] = {}
    all_nodes = sorted({u for u, _, _ in edges} | {v for _, v, _ in edges})
    for node in all_nodes:
        denom = total.get(node, 0.0)
        out[node] = (same.get(node, 0.0) / denom) if denom > 0 else 0.0
    return out


def get_shell_index(node_meta: Dict[NodeId, dict], node_id: NodeId) -> int:
    row = node_meta.get(node_id, {})
    value = row.get("shell_index", 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_scores(values: Dict[NodeId, float]) -> Dict[NodeId, float]:
    if not values:
        return {}
    xs = list(values.values())
    lo = min(xs)
    hi = max(xs)
    if hi <= lo:
        return {k: 0.0 for k in values}
    return {k: (v - lo) / (hi - lo) for k, v in values.items()}


def choose_topk(all_nodes: List[NodeId], score_map: Dict[NodeId, float], top_k: int) -> List[NodeId]:
    k = max(1, min(top_k, len(all_nodes)))
    ranked = sorted(all_nodes, key=lambda n: (-score_map.get(n, 0.0), n))
    return ranked[:k]


def choose_topalpha(all_nodes: List[NodeId], score_map: Dict[NodeId, float], alpha: float) -> List[NodeId]:
    k = max(1, math.ceil(alpha * len(all_nodes)))
    return choose_topk(all_nodes, score_map, k)


def derive_backbone_nodes(
    variant: dict,
    edges: Sequence[Edge],
    node_meta: Dict[NodeId, dict],
    reference_backbone_count: int,
) -> List[NodeId]:
    method = variant.get("method", "hint_reference")
    all_nodes = sorted({u for u, _, _ in edges} | {v for _, v, _ in edges})
    hint_column = variant.get("hint_column", "backbone_hint")

    if method == "hint_reference":
        hinted = sorted(
            node_id for node_id, row in node_meta.items()
            if str(row.get(hint_column, "")).strip() in {"1", "true", "True", "yes", "YES"}
        )
        return hinted

    strengths = incidence_strength(edges)
    same_shell_fraction = same_shell_fraction_per_node(node_meta, edges)

    if method == "strength_topk":
        top_k = int(variant.get("top_k", reference_backbone_count))
        return choose_topk(all_nodes, strengths, top_k)

    if method == "strength_topalpha":
        alpha = float(variant.get("alpha", 0.25))
        return choose_topalpha(all_nodes, strengths, alpha)

    if method == "same_shell_core":
        if "top_k" in variant:
            return choose_topk(all_nodes, same_shell_fraction, int(variant["top_k"]))
        alpha = float(variant.get("alpha", 0.25))
        return choose_topalpha(all_nodes, same_shell_fraction, alpha)

    if method == "hybrid_strength_shell":
        lam = float(variant.get("lambda", 0.5))
        norm_strength = normalize_scores(strengths)
        norm_shell = normalize_scores(same_shell_fraction)
        hybrid = {
            node: lam * norm_strength.get(node, 0.0) + (1.0 - lam) * norm_shell.get(node, 0.0)
            for node in all_nodes
        }
        if "top_k" in variant:
            return choose_topk(all_nodes, hybrid, int(variant["top_k"]))
        alpha = float(variant.get("alpha", 0.25))
        return choose_topalpha(all_nodes, hybrid, alpha)

    raise ValueError(f"Unknown backbone variant method: {method}")


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
    same_weight = sum(w for u, v, w in edges if get_shell_index(node_meta, u) == get_shell_index(node_meta, v))
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
        repeat_rows.append({
            "arm_name": arm_name,
            "repeat_index": repeat_index,
            "shuffle_weighted_shell_gap": gap,
        })

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


def render_readout(overall_summary: dict) -> str:
    lines = [
        f"# BMC-07c Variant Readout – {overall_summary['run_id']}",
        "",
        "## Befund",
        "",
        f"- Number of variants: `{overall_summary['variant_count']}`",
        f"- Overall status: `{overall_summary['overall_status']}`",
        "",
        "## Variant summary",
        "",
        "| variant_name | method | decision_label | dominant_arm | backbone_node_count | coupling_edge_count |",
        "|---|---|---|---|---:|---:|",
    ]
    for row in overall_summary["variant_rows"]:
        lines.append(
            f"| `{row['variant_name']}` | `{row['method']}` | `{row['decision_label']}` | "
            f"`{row['dominant_arm']}` | {row['backbone_node_count']} | {row['coupling_edge_count']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "BMC-07c checks whether the current localization pattern is sensitive to backbone construction. "
        "It does not by itself establish a general theory result.",
        "",
        "## Hypothese",
        "",
        "If off-backbone localization survives multiple simple backbone variants, the current minimal result becomes more robust.",
        "",
        "## Offene Lücke",
        "",
        "This block still works on a minimal dataset; robustness on real project inputs remains open.",
        "",
    ])
    return "\n".join(lines)


def compute_overall_status(variant_rows: List[dict]) -> str:
    labels = [row["decision_label"] for row in variant_rows]
    if not labels:
        return "no_variants"
    if all(label == "off_backbone_localization_supported" for label in labels):
        return "off_backbone_result_robust"
    if any(label == "backbone_localization_supported" for label in labels):
        return "backbone_result_recovered"
    unique = set(labels)
    if len(unique) > 1:
        return "backbone_definition_sensitive"
    return "still_weak_or_mixed"


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_yaml(config_path)
    project_root = config_path.parent.parent

    run_cfg = config.get("run", {})
    inputs_cfg = config.get("inputs", {})
    graph_cfg = config.get("graph", {})
    perturb_cfg = config.get("perturbation", {})
    decision_cfg = config.get("decision", {})
    variants_cfg = config.get("backbone_variants", {})

    edges = load_edge_table(
        project_root / inputs_cfg["baseline_relational_table"],
        graph_cfg.get("source_column", "source"),
        graph_cfg.get("target_column", "target"),
        graph_cfg.get("weight_column", "weight"),
    )
    node_meta = load_node_metadata(project_root / inputs_cfg["node_metadata"])

    reference_backbone_nodes = sorted(
        node_id for node_id, row in node_meta.items()
        if str(row.get("backbone_hint", "")).strip() in {"1", "true", "True", "yes", "YES"}
    )
    reference_backbone_count = len(reference_backbone_nodes)

    output_dir = project_root / run_cfg.get("output_dir", "runs/BMC-07/BMC07c_backbone_variation_open")
    output_dir.mkdir(parents=True, exist_ok=True)

    repeats = int(perturb_cfg.get("repeats", 20))
    seed = int(run_cfg.get("seed", 101))

    diffusion_reference = load_optional_npz_matrix(
        project_root / inputs_cfg["diffusion_distance_matrix"]
        if inputs_cfg.get("diffusion_distance_matrix") else None
    )
    pair_reference = load_optional_npz_matrix(
        project_root / inputs_cfg["pair_neighborhood_matrix"]
        if inputs_cfg.get("pair_neighborhood_matrix") else None
    )

    variant_rows: List[dict] = []
    overall_repeat_rows: List[dict] = []
    variant_details: Dict[str, dict] = {}

    for variant_index, variant in enumerate(variants_cfg.get("variants", [])):
        variant_name = variant["variant_name"]
        method = variant["method"]
        rng = random.Random(seed + variant_index)

        backbone_nodes = derive_backbone_nodes(
            variant=variant,
            edges=edges,
            node_meta=node_meta,
            reference_backbone_count=reference_backbone_count,
        )
        backbone_set = set(backbone_nodes)
        all_nodes = sorted({u for u, _, _ in edges} | {v for _, v, _ in edges})
        off_backbone_nodes = [n for n in all_nodes if n not in backbone_set]

        arms = {}
        arm_rows = []
        for arm_name in ["full_graph", "backbone_only", "off_backbone_only", "coupling_only"]:
            arm_edges = select_arm_edges(edges, backbone_set, arm_name)
            arm_summary, repeat_rows = summarize_arm(
                arm_name=arm_name,
                edges=arm_edges,
                node_meta=node_meta,
                repeats=repeats,
                rng=rng,
                diffusion_reference=diffusion_reference,
                pair_reference=pair_reference,
            )
            arms[arm_name] = arm_summary
            arm_rows.append(arm_summary)
            for row in repeat_rows:
                row["variant_name"] = variant_name
            overall_repeat_rows.extend(repeat_rows)

        label, dominant_arm, ranking = decision_label(
            arms=arms,
            arrangement_min=float(decision_cfg.get("arrangement_signal_min", 0.05)),
            dominance_gap_min=float(decision_cfg.get("dominance_gap_min", 0.03)),
            minimum_arm_edge_count=int(decision_cfg.get("minimum_arm_edge_count", 2)),
        )
        coupling_edge_count = len(select_arm_edges(edges, backbone_set, "coupling_only"))
        variant_summary = {
            "variant_name": variant_name,
            "method": method,
            "variant_parameters": json.dumps(
                {k: v for k, v in variant.items() if k not in {"variant_name", "method"}},
                sort_keys=True
            ),
            "backbone_node_count": len(backbone_nodes),
            "off_backbone_node_count": len(off_backbone_nodes),
            "coupling_edge_count": coupling_edge_count,
            "decision_label": label,
            "dominant_arm": dominant_arm,
            "full_graph_arrangement_signal": arms["full_graph"]["arrangement_signal"],
            "backbone_only_arrangement_signal": arms["backbone_only"]["arrangement_signal"],
            "off_backbone_only_arrangement_signal": arms["off_backbone_only"]["arrangement_signal"],
            "coupling_only_arrangement_signal": arms["coupling_only"]["arrangement_signal"],
        }
        variant_rows.append(variant_summary)
        variant_details[variant_name] = {
            "variant_name": variant_name,
            "method": method,
            "variant_parameters": {k: v for k, v in variant.items() if k not in {"variant_name", "method"}},
            "backbone_nodes": backbone_nodes,
            "backbone_node_count": len(backbone_nodes),
            "off_backbone_node_count": len(off_backbone_nodes),
            "coupling_edge_count": coupling_edge_count,
            "decision_label": label,
            "dominant_arm": dominant_arm,
            "arm_signal_ranking": [
                {"arm_name": arm_name, "arrangement_signal": arrangement_signal}
                for arm_name, arrangement_signal in ranking
            ],
            "arms": arms,
        }

        variant_dir = output_dir / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        (variant_dir / "summary.json").write_text(json.dumps(variant_details[variant_name], indent=2), encoding="utf-8")
        write_csv(
            variant_dir / "arm_metrics.csv",
            arm_rows,
            fieldnames=[
                "arm_name", "edge_count", "node_count", "total_weight",
                "same_shell_weight_fraction", "weighted_shell_gap",
                "shuffle_mean_gap", "shuffle_std_gap", "arrangement_signal",
                "shell_order_drift", "diffusion_shift", "pair_neighborhood_shift",
            ],
        )

    overall_status = compute_overall_status(variant_rows)
    overall_summary = {
        "run_id": run_cfg.get("run_id", "BMC07c_backbone_variation_open"),
        "variant_count": len(variant_rows),
        "overall_status": overall_status,
        "variant_rows": variant_rows,
    }

    validation = {
        "baseline_edge_count": len(edges),
        "baseline_node_count": len({u for u, _, _ in edges} | {v for _, v, _ in edges}),
        "variant_count": len(variant_rows),
        "repeat_count_configured": repeats,
        "minimum_arm_edge_count": int(decision_cfg.get("minimum_arm_edge_count", 2)),
        "optional_diffusion_reference_present": diffusion_reference is not None,
        "optional_pair_reference_present": pair_reference is not None,
    }

    metadata = {
        "runner_name": Path(__file__).name,
        "config_path": str(config_path),
        "seed": seed,
        "notes": [
            "Open BMC-07c backbone-variation runner.",
            "No hidden calculations.",
            "Only backbone definition varies across variants.",
            "Readouts and arm logic remain constant across variants.",
        ],
    }

    (output_dir / "summary.json").write_text(json.dumps(overall_summary, indent=2), encoding="utf-8")
    (output_dir / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_csv(
        output_dir / "backbone_variant_summary.csv",
        variant_rows,
        fieldnames=[
            "variant_name", "method", "variant_parameters",
            "backbone_node_count", "off_backbone_node_count",
            "coupling_edge_count", "decision_label", "dominant_arm",
            "full_graph_arrangement_signal", "backbone_only_arrangement_signal",
            "off_backbone_only_arrangement_signal", "coupling_only_arrangement_signal",
        ],
    )
    write_csv(
        output_dir / "repeat_metrics.csv",
        overall_repeat_rows,
        fieldnames=["variant_name", "arm_name", "repeat_index", "shuffle_weighted_shell_gap"],
    )
    (output_dir / "readout.md").write_text(render_readout(overall_summary), encoding="utf-8")
    print(f"Wrote outputs to: {output_dir}")


if __name__ == "__main__":
    main()
