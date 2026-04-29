#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

FEATURE_COLUMNS = [
    "feature_mode_frequency",
    "feature_length_scale",
    "feature_shape_factor",
    "feature_spectral_index",
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build BMC-10 nullmodel graph inputs from synthetic Gaussian-like features using the BMC-08c node contract."
    )
    parser.add_argument("--config", default="data/bmc10_nullmodel_config.yaml")
    return parser.parse_args()

def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)

def load_feature_rows(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [dict(r) for r in csv.DictReader(handle)]
    if not rows:
        raise ValueError("Feature table is empty.")
    return rows

def require_float(v: str, ctx: str) -> float:
    x = float(v)
    if not math.isfinite(x):
        raise ValueError(f"Non-finite value in {ctx}: {v}")
    return x

def feature_vectors(rows: List[dict]) -> Dict[str, Dict[str, float]]:
    out = {}
    for r in rows:
        major = require_float(r["L_major_raw"], f"{r['node_id']} L_major_raw")
        minor = require_float(r["L_minor_raw"], f"{r['node_id']} L_minor_raw")
        out[r["node_id"]] = {
            "feature_mode_frequency": require_float(r["feature_mode_frequency"], f"{r['node_id']} feature_mode_frequency"),
            "feature_length_scale": require_float(r["feature_length_scale"], f"{r['node_id']} feature_length_scale"),
            "feature_shape_factor": max(major, minor) / min(major, minor),
            "feature_spectral_index": require_float(r["m_ref_raw"], f"{r['node_id']} m_ref_raw"),
        }
    return out

def empirical_stats(vectors: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    stats = {}
    for col in FEATURE_COLUMNS:
        vals = [vec[col] for vec in vectors.values()]
        mu = sum(vals) / len(vals)
        var = sum((x - mu) ** 2 for x in vals) / len(vals)
        std = math.sqrt(var)
        stats[col] = {"mean": mu, "std": std if std > 0 else 1.0}
    return stats

def gaussian_feature_rows(template_rows: List[dict], seed: int) -> List[dict]:
    rnd = random.Random(seed)
    template_vectors = feature_vectors(template_rows)
    stats = empirical_stats(template_vectors)

    out = []
    for idx, row in enumerate(template_rows, start=1):
        fam = row["node_family"].strip().upper()
        if fam == "RING":
            shell_index = 0
        elif fam == "CAVITY":
            shell_index = 1
        elif fam == "MEMBRANE":
            shell_index = 2
        else:
            raise ValueError(f"Unsupported family: {fam}")

        sampled = {col: rnd.gauss(stats[col]["mean"], stats[col]["std"]) for col in FEATURE_COLUMNS}
        shape = max(1.0, sampled["feature_shape_factor"])
        major = shape
        minor = 1.0

        out.append({
            "node_id": row["node_id"],
            "node_family": fam,
            "node_label": f"nullmodel_{fam}_{idx}",
            "L_major_raw": f"{major:.12g}",
            "L_minor_raw": f"{minor:.12g}",
            "m_ref_raw": f"{max(1.0, sampled['feature_spectral_index']):.12g}",
            "feature_mode_frequency": f"{sampled['feature_mode_frequency']:.12g}",
            "feature_length_scale": f"{abs(sampled['feature_length_scale']) + 1e-9:.12g}",
            "origin_tag": f"BMC10_nullmodel_seed_{seed}",
            "comment": "Gaussian nullmodel feature row with BMC-08c node contract preserved",
            "shell_index": shell_index,
            "feature_shape_factor": f"{shape:.12g}",
            "feature_spectral_index": f"{max(1.0, sampled['feature_spectral_index']):.12g}",
        })
    return out

def zscore_feature_rows(rows: List[dict]) -> Dict[str, Dict[str, float]]:
    values = defaultdict(list)
    for r in rows:
        values["feature_mode_frequency"].append(float(r["feature_mode_frequency"]))
        values["feature_length_scale"].append(float(r["feature_length_scale"]))
        values["feature_shape_factor"].append(float(r["feature_shape_factor"]))
        values["feature_spectral_index"].append(float(r["feature_spectral_index"]))
    means = {k: sum(v) / len(v) for k, v in values.items()}
    stds = {}
    for k, v in values.items():
        mu = means[k]
        var = sum((x - mu) ** 2 for x in v) / len(v)
        std = math.sqrt(var)
        stds[k] = std if std > 0 else 1.0

    z = {}
    for r in rows:
        node_id = r["node_id"]
        z[node_id] = {}
        for col in FEATURE_COLUMNS:
            x = float(r[col])
            z[node_id][col] = (x - means[col]) / stds[col]
    return z

def euclidean(a: Dict[str, float], b: Dict[str, float]) -> float:
    return math.sqrt(sum((a[c] - b[c]) ** 2 for c in FEATURE_COLUMNS))

def build_threshold_edges(rows: List[dict], z: Dict[str, Dict[str, float]], tau: float) -> List[Tuple[str, str, float]]:
    node_ids = [r["node_id"] for r in rows]
    edges = []
    for i, a in enumerate(node_ids):
        for b in node_ids[i + 1:]:
            d = euclidean(z[a], z[b])
            w = 1.0 / (1.0 + d)
            if w >= tau:
                edges.append((a, b, w))
    return edges

def connected_components(nodes: List[str], edges: List[Tuple[str, str, float]]) -> List[List[str]]:
    adj = {n: set() for n in nodes}
    for a, b, _ in edges:
        adj[a].add(b)
        adj[b].add(a)
    comps = []
    seen = set()
    for n in nodes:
        if n in seen:
            continue
        q = deque([n]); seen.add(n); comp = []
        while q:
            x = q.popleft()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    q.append(y)
        comps.append(sorted(comp))
    return comps

def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main() -> None:
    args = parse_args()
    cfg = load_yaml(Path(args.config))
    template_rows = load_feature_rows(Path(cfg["input"]["template_feature_table_csv"]))
    tau_values = [float(x) for x in cfg["graph"]["tau_values"]]
    seeds = [int(x) for x in cfg["nullmodel"]["seeds"]]
    out_root = Path(cfg["output"]["output_dir"])
    out_root.mkdir(parents=True, exist_ok=True)

    diagnostics = []

    for seed in seeds:
        synthetic_rows = gaussian_feature_rows(template_rows, seed=seed)
        z = zscore_feature_rows(synthetic_rows)
        node_ids = [r["node_id"] for r in synthetic_rows]
        family_by_id = {r["node_id"]: r["node_family"] for r in synthetic_rows}

        seed_dir = out_root / f"seed_{seed}"
        seed_dir.mkdir(parents=True, exist_ok=True)

        feature_rows = []
        node_meta_rows = []
        for r in synthetic_rows:
            feature_rows.append({
                "node_id": r["node_id"],
                "node_family": r["node_family"],
                "node_label": r["node_label"],
                "L_major_raw": r["L_major_raw"],
                "L_minor_raw": r["L_minor_raw"],
                "m_ref_raw": r["m_ref_raw"],
                "feature_mode_frequency": r["feature_mode_frequency"],
                "feature_length_scale": r["feature_length_scale"],
                "origin_tag": r["origin_tag"],
                "comment": r["comment"],
            })
            node_meta_rows.append({
                "node_id": r["node_id"],
                "shell_index": r["shell_index"],
                "node_label": r["node_label"],
                "node_family": r["node_family"],
                "origin_tag": r["origin_tag"],
                "comment": r["comment"],
                "feature_shape_factor": r["feature_shape_factor"],
                "feature_spectral_index": r["feature_spectral_index"],
            })

        write_csv(seed_dir / "nullmodel_feature_table.csv", feature_rows,
                  ["node_id","node_family","node_label","L_major_raw","L_minor_raw","m_ref_raw","feature_mode_frequency","feature_length_scale","origin_tag","comment"])

        for tau in tau_values:
            edges = build_threshold_edges(synthetic_rows, z, tau=tau)
            case_id = f"threshold_tau_{str(tau).replace('.', '')}"
            case_dir = seed_dir / case_id
            case_dir.mkdir(parents=True, exist_ok=True)

            edge_rows = []
            for a, b, w in edges:
                fa, fb = family_by_id[a], family_by_id[b]
                edge_rows.append({
                    "source": a,
                    "target": b,
                    "weight": f"{w:.12g}",
                    "edge_family": "intra_family" if fa == fb else "cross_family",
                    "relation_type": "gaussian_nullmodel_threshold_similarity",
                    "source_family": fa,
                    "target_family": fb,
                    "evidence_tag": f"bmc10_nullmodel_seed_{seed}_tau_{tau}",
                    "comment": f"Gaussian nullmodel threshold graph with tau={tau}",
                })

            write_csv(case_dir / "baseline_relational_table_real.csv", edge_rows,
                      ["source","target","weight","edge_family","relation_type","source_family","target_family","evidence_tag","comment"])
            write_csv(case_dir / "node_metadata_real.csv", node_meta_rows,
                      ["node_id","shell_index","node_label","node_family","origin_tag","comment","feature_shape_factor","feature_spectral_index"])

            comps = connected_components(node_ids, edges)
            n = len(node_ids)
            m = len(edges)
            density = (2 * m) / (n * (n - 1)) if n > 1 else 0.0
            mean_degree = (2 * m) / n if n else 0.0
            comp_sizes = sorted((len(c) for c in comps), reverse=True)
            summary = {
                "seed": seed,
                "graph_construction_method": "gaussian_nullmodel_threshold",
                "graph_construction_parameters": {"tau": tau},
                "graph_node_count": n,
                "graph_edge_count": m,
                "connected_component_count": len(comps),
                "largest_component_size": comp_sizes[0] if comp_sizes else 0,
                "mean_degree": mean_degree,
                "graph_density": density,
                "isolated_node_count": sum(1 for c in comps if len(c) == 1),
                "component_size_profile": comp_sizes,
            }
            (case_dir / "graph_build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
            diagnostics.append({
                "seed": seed,
                "case_id": case_id,
                **summary,
            })

    write_csv(out_root / "graph_build_diagnostics.csv", diagnostics,
              ["seed","case_id","graph_construction_method","graph_construction_parameters","graph_node_count","graph_edge_count","connected_component_count","largest_component_size","mean_degree","graph_density","isolated_node_count","component_size_profile"])
    print(f"Wrote nullmodel graph inputs to: {out_root}")

if __name__ == "__main__":
    main()
