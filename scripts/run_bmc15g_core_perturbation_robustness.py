#!/usr/bin/env python3
"""
BMC-15g Core Perturbation Robustness Runner.

Robustness diagnostic only. No physical-geometry, causal, Lorentzian,
uniqueness, or continuum-limit claim.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml

try:
    import networkx as nx
except Exception as exc:
    raise SystemExit("Missing dependency: networkx. Install with: pip install networkx") from exc


SOURCE_COLS = ["source", "src", "i", "node_i", "u", "from"]
TARGET_COLS = ["target", "dst", "j", "node_j", "v", "to"]
WEIGHT_COLS = ["weight", "w", "similarity", "strength", "edge_weight", "value"]
DISTANCE_COLS = ["distance", "dist", "dissimilarity", "cost"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config did not parse to a mapping: {path}")
    return data


def find_col(cols: Iterable[str], candidates: List[str]) -> Optional[str]:
    lower = {str(c).lower(): str(c) for c in cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def safe_float(x: Any, default: float = float("nan")) -> float:
    try:
        val = float(x)
        return val if math.isfinite(val) else default
    except Exception:
        return default


def edge_key(u: Any, v: Any) -> Tuple[str, str]:
    a, b = str(u), str(v)
    return (a, b) if a <= b else (b, a)


def edge_set(g: nx.Graph) -> set[Tuple[str, str]]:
    return {edge_key(u, v) for u, v in g.edges()}


def node_set(edges: Iterable[Tuple[str, str]]) -> set[str]:
    out: set[str] = set()
    for u, v in edges:
        out.add(str(u))
        out.add(str(v))
    return out


def jaccard(a: set, b: set) -> float:
    union = a | b
    return float(len(a & b) / len(union)) if union else float("nan")


def retention(candidate: set, reference: set) -> float:
    return float(len(candidate & reference) / len(reference)) if reference else float("nan")


def graph_summary(g: nx.Graph) -> Dict[str, Any]:
    n = g.number_of_nodes()
    e = g.number_of_edges()
    comps = nx.number_connected_components(g) if n else 0
    deg = np.array([d for _, d in g.degree()], dtype=float) if n else np.array([])
    return {
        "n_nodes": int(n),
        "n_edges": int(e),
        "n_components": int(comps),
        "is_connected": bool(comps == 1 and n > 0),
        "avg_degree": float(deg.mean()) if deg.size else float("nan"),
        "degree_std": float(deg.std(ddof=0)) if deg.size else float("nan"),
        "degree_max": float(deg.max()) if deg.size else float("nan"),
        "density": float(nx.density(g)) if n > 1 else float("nan"),
    }


def load_edge_graph(path: Path, graph_name: str) -> nx.Graph:
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    df = pd.read_csv(path, sep=sep)
    src_col = find_col(df.columns, SOURCE_COLS)
    dst_col = find_col(df.columns, TARGET_COLS)
    w_col = find_col(df.columns, WEIGHT_COLS)
    dist_col = find_col(df.columns, DISTANCE_COLS)

    if src_col is None or dst_col is None:
        raise ValueError(f"Could not identify source/target columns in {path}: {list(df.columns)}")

    g = nx.Graph(name=graph_name)
    for _, row in df.iterrows():
        u, v = str(row[src_col]), str(row[dst_col])
        if u == v:
            continue
        if w_col is not None:
            w = safe_float(row[w_col], 1.0)
        elif dist_col is not None:
            d = max(safe_float(row[dist_col], 1.0), 1e-12)
            w = 1.0 / d
        else:
            w = 1.0
        g.add_edge(u, v, weight=float(w if math.isfinite(w) else 1.0))
    return g


def strongest_edges(g: nx.Graph, n_edges: int) -> set[Tuple[str, str]]:
    rows = []
    for u, v, attrs in g.edges(data=True):
        rows.append((float(attrs.get("weight", 1.0)), edge_key(u, v)))
    rows.sort(key=lambda x: (-x[0], x[1]))
    return {e for _, e in rows[:max(0, min(n_edges, len(rows)))]}


def perturb_weight_jitter(g: nx.Graph, strength: float, rng: np.random.Generator) -> nx.Graph:
    out = g.copy()
    for _, _, attrs in out.edges(data=True):
        attrs["weight"] = max(float(attrs.get("weight", 1.0)) * float(np.exp(rng.normal(0.0, strength))), 0.0)
    return out


def perturb_edge_dropout(g: nx.Graph, strength: float, rng: np.random.Generator) -> nx.Graph:
    out = g.copy()
    edges = list(out.edges())
    n_remove = int(round(max(0.0, min(1.0, strength)) * len(edges)))
    if n_remove:
        for idx in rng.choice(len(edges), size=min(n_remove, len(edges)), replace=False):
            out.remove_edge(*edges[int(idx)])
    return out


def perturb_edge_swap(g: nx.Graph, strength: float, rng: np.random.Generator) -> nx.Graph:
    out = g.copy()
    edges = list(out.edges(data=True))
    nodes = [str(n) for n in out.nodes()]
    n_remove = int(round(max(0.0, min(1.0, strength)) * len(edges)))
    if not n_remove or len(nodes) < 2:
        return out

    removed_weights = []
    for idx in rng.choice(len(edges), size=min(n_remove, len(edges)), replace=False):
        u, v, attrs = edges[int(idx)]
        if out.has_edge(u, v):
            removed_weights.append(float(attrs.get("weight", 1.0)))
            out.remove_edge(u, v)

    existing = edge_set(out)
    candidates = [
        edge_key(nodes[i], nodes[j])
        for i in range(len(nodes))
        for j in range(i + 1, len(nodes))
        if edge_key(nodes[i], nodes[j]) not in existing
    ]
    rng.shuffle(candidates)
    for k, (u, v) in enumerate(candidates[:len(removed_weights)]):
        out.add_edge(u, v, weight=float(removed_weights[k % len(removed_weights)]))
    return out


def perturb_graph(g: nx.Graph, perturbation_type: str, strength: float, rng: np.random.Generator) -> nx.Graph:
    if perturbation_type == "weight_jitter":
        return perturb_weight_jitter(g, strength, rng)
    if perturbation_type == "edge_dropout":
        return perturb_edge_dropout(g, strength, rng)
    if perturbation_type == "edge_swap":
        return perturb_edge_swap(g, strength, rng)
    raise ValueError(f"Unknown perturbation type: {perturbation_type}")


def label(frac: float, thresholds: Dict[str, float]) -> str:
    if not math.isfinite(frac):
        return "core_retention_undefined"
    if frac >= thresholds["high"]:
        return "core_retention_high"
    if frac >= thresholds["moderate"]:
        return "core_retention_moderate"
    if frac >= thresholds["low"]:
        return "core_retention_low"
    return "core_retention_weak"


def metric_row(g: nx.Graph, ptype: str, strength: float, seed: int, repeat: int,
               ref_core: set[Tuple[str, str]], thresholds: Dict[str, float]) -> Dict[str, Any]:
    cand_core = strongest_edges(g, len(ref_core))
    ref_nodes = node_set(ref_core)
    cand_nodes = node_set(cand_core)
    edge_ret = retention(cand_core, ref_core)
    return {
        "perturbation_type": ptype,
        "strength": float(strength),
        "seed": int(seed),
        "repeat_index": int(repeat),
        **graph_summary(g),
        "reference_core_edges": int(len(ref_core)),
        "candidate_core_edges": int(len(cand_core)),
        "core_edge_intersection": int(len(cand_core & ref_core)),
        "core_edge_retention_fraction": float(edge_ret),
        "core_edge_jaccard": float(jaccard(cand_core, ref_core)),
        "reference_core_nodes": int(len(ref_nodes)),
        "candidate_core_nodes": int(len(cand_nodes)),
        "core_node_intersection": int(len(cand_nodes & ref_nodes)),
        "core_node_retention_fraction": float(retention(cand_nodes, ref_nodes)),
        "containment_label": label(edge_ret, thresholds),
    }


def envelope_rows(g: nx.Graph, ptype: str, strength: float, seed: int, repeat: int,
                  refs: Dict[str, set[Tuple[str, str]]]) -> List[Dict[str, Any]]:
    out = []
    for name, ref_edges in refs.items():
        cand = strongest_edges(g, len(ref_edges))
        out.append({
            "perturbation_type": ptype,
            "strength": float(strength),
            "seed": int(seed),
            "repeat_index": int(repeat),
            "reference_name": name,
            "reference_edges": int(len(ref_edges)),
            "candidate_edges": int(len(cand)),
            "edge_intersection": int(len(cand & ref_edges)),
            "edge_retention_fraction": float(retention(cand, ref_edges)),
            "edge_jaccard": float(jaccard(cand, ref_edges)),
        })
    return out


def write_readout(path: Path, summary: Dict[str, Any], metrics: pd.DataFrame, family: pd.DataFrame) -> None:
    lines = [
        "# BMC-15g Core Perturbation Robustness Readout",
        "",
        "This is a robustness diagnostic for a local graph-core proxy, not a physical-geometry claim.",
        "",
        "## Summary",
        "",
        f"- created_at: `{summary['created_at']}`",
        f"- metric rows: `{summary['n_metric_rows']}`",
        f"- envelope rows: `{summary['n_envelope_rows']}`",
        f"- warnings: `{summary['n_warnings']}`",
        "",
        "## Containment-label counts",
        "",
    ]
    if metrics.empty:
        lines.append("- no metric rows")
    else:
        for k, v in metrics["containment_label"].value_counts().sort_index().items():
            lines.append(f"- `{k}`: {int(v)}")
    lines += ["", "## Family summary", ""]
    if family.empty:
        lines.append("No family summary rows.")
    else:
        cols = ["perturbation_type", "strength", "n", "core_edge_retention_fraction_mean",
                "core_edge_retention_fraction_min", "core_edge_jaccard_mean",
                "core_node_retention_fraction_mean", "connected_fraction"]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
        for _, row in family[cols].iterrows():
            vals = []
            for c in cols:
                x = row[c]
                vals.append(f"{x:.6g}" if isinstance(x, float) else str(x))
            lines.append("| " + " | ".join(vals) + " |")
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "Favorable retention can support a construction-qualified robustness statement for the local graph-core proxy. It cannot establish physical spacetime, a metric manifold, causal structure, Lorentzian behavior, or uniqueness.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run(config_path: Path) -> None:
    cfg = load_yaml(config_path)
    input_cfg = cfg["input"]
    output_dir = Path(cfg.get("output", {}).get("output_dir", "runs/BMC-15g/core_perturbation_robustness_open"))
    ensure_dir(output_dir)

    source_path = Path(input_cfg["source_graph_edges_csv"])
    core_path = Path(input_cfg["reference_core_edges_csv"])
    source = load_edge_graph(source_path, "source_graph")
    ref_core = edge_set(load_edge_graph(core_path, "reference_core"))

    warnings = []
    ref_envs: Dict[str, set[Tuple[str, str]]] = {}
    for item in input_cfg.get("reference_envelopes", []):
        p = Path(item["edges_csv"])
        if p.exists():
            ref_envs[str(item["name"])] = edge_set(load_edge_graph(p, str(item["name"])))
        else:
            warnings.append(f"missing reference envelope skipped: {item}")

    run_cfg = cfg.get("run", {})
    repeats = int(run_cfg.get("repeats", 50))
    seeds = [int(x) for x in run_cfg.get("seeds", [101, 202, 303])]
    thresholds = {
        "high": float(cfg.get("readout", {}).get("high_retention_threshold", 0.80)),
        "moderate": float(cfg.get("readout", {}).get("moderate_retention_threshold", 0.60)),
        "low": float(cfg.get("readout", {}).get("low_retention_threshold", 0.40)),
    }

    metrics, env_rows = [], []
    for ptype, pcfg in cfg.get("perturbations", {}).items():
        if not bool(pcfg.get("enabled", True)):
            continue
        for strength in [float(x) for x in pcfg.get("strengths", [])]:
            for seed in seeds:
                for repeat in range(repeats):
                    combined_seed = int(seed + 1000003 * repeat + 9176 * int(round(strength * 10000)))
                    rng = np.random.default_rng(combined_seed)
                    perturbed = perturb_graph(source, ptype, strength, rng)
                    metrics.append(metric_row(perturbed, ptype, strength, seed, repeat, ref_core, thresholds))
                    env_rows.extend(envelope_rows(perturbed, ptype, strength, seed, repeat, ref_envs))

    metrics_df = pd.DataFrame(metrics)
    env_df = pd.DataFrame(env_rows)

    if metrics_df.empty:
        family_df = pd.DataFrame()
        core_summary_df = pd.DataFrame()
    else:
        family_df = metrics_df.groupby(["perturbation_type", "strength"], dropna=False).agg(
            n=("core_edge_retention_fraction", "size"),
            core_edge_retention_fraction_mean=("core_edge_retention_fraction", "mean"),
            core_edge_retention_fraction_min=("core_edge_retention_fraction", "min"),
            core_edge_retention_fraction_max=("core_edge_retention_fraction", "max"),
            core_edge_jaccard_mean=("core_edge_jaccard", "mean"),
            core_node_retention_fraction_mean=("core_node_retention_fraction", "mean"),
            connected_fraction=("is_connected", "mean"),
        ).reset_index()
        core_summary_df = metrics_df.groupby(
            ["perturbation_type", "strength", "containment_label"], dropna=False
        ).size().reset_index(name="count")

    summary = {
        "created_at": now_iso(),
        "config_path": str(config_path),
        "source_graph_edges_csv": str(source_path),
        "reference_core_edges_csv": str(core_path),
        "output_dir": str(output_dir),
        "source_graph_summary": graph_summary(source),
        "reference_core_edges": int(len(ref_core)),
        "reference_envelopes": {k: int(len(v)) for k, v in ref_envs.items()},
        "repeats": repeats,
        "seeds": seeds,
        "n_metric_rows": int(len(metrics_df)),
        "n_envelope_rows": int(len(env_df)),
        "n_warnings": int(len(warnings)),
        "warnings": warnings,
        "interpretation_boundary": "Robustness diagnostic only; no physical spacetime, causal, Lorentzian, uniqueness, or continuum-limit claim.",
    }

    metrics_df.to_csv(output_dir / "perturbation_metrics.csv", index=False)
    env_df.to_csv(output_dir / "envelope_overlap_summary.csv", index=False)
    family_df.to_csv(output_dir / "family_summary.csv", index=False)
    core_summary_df.to_csv(output_dir / "core_retention_summary.csv", index=False)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    write_readout(output_dir / "readout.md", summary, metrics_df, family_df)

    print(f"Wrote BMC-15g outputs to: {output_dir}")
    print(f"Metric rows: {len(metrics_df)}")
    print(f"Envelope rows: {len(env_df)}")
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="data/bmc15g_core_perturbation_robustness_config.yaml")
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
