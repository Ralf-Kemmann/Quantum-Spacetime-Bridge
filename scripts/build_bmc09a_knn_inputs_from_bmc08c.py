#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


FEATURE_COLUMNS = [
    "feature_mode_frequency",
    "feature_length_scale",
    "feature_shape_factor",
    "feature_spectral_index",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build BMC-09a symmetric k-NN graph inputs from a BMC-08c-style feature table."
    )
    parser.add_argument(
        "--config",
        default="data/bmc09a_knn_config.yaml",
        help="Path to YAML config.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_feature_rows(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(r) for r in reader]
    if not rows:
        raise ValueError("Feature table is empty.")
    required = {
        "node_id", "node_family", "node_label",
        "feature_mode_frequency", "feature_length_scale",
        "L_major_raw", "L_minor_raw", "m_ref_raw", "origin_tag"
    }
    missing = required - set(rows[0].keys())
    if missing:
        raise ValueError(f"Missing required feature columns: {sorted(missing)}")
    return rows


def require_float(v: str, ctx: str) -> float:
    x = float(v)
    if not math.isfinite(x):
        raise ValueError(f"Non-finite value in {ctx}: {v}")
    return x


def zscore_features(rows: List[dict]) -> Dict[str, Dict[str, float]]:
    vals = defaultdict(list)
    for r in rows:
        for col in FEATURE_COLUMNS:
            if col == "feature_shape_factor":
                # derive from raw fields
                major = require_float(r["L_major_raw"], f"{r['node_id']} L_major_raw")
                minor = require_float(r["L_minor_raw"], f"{r['node_id']} L_minor_raw")
                if major <= 0 or minor <= 0:
                    raise ValueError(f"Non-positive shape fields for {r['node_id']}")
                x = max(major, minor) / min(major, minor)
            elif col == "feature_spectral_index":
                x = require_float(r["m_ref_raw"], f"{r['node_id']} m_ref_raw")
            else:
                x = require_float(r[col], f"{r['node_id']} {col}")
            vals[col].append(x)

    means = {c: sum(v)/len(v) for c, v in vals.items()}
    stds = {}
    for c, v in vals.items():
        mu = means[c]
        var = sum((x-mu)**2 for x in v) / len(v)
        std = math.sqrt(var)
        stds[c] = std if std > 0 else 1.0

    z = {}
    for r in rows:
        node_id = r["node_id"]
        z[node_id] = {}
        for col in FEATURE_COLUMNS:
            if col == "feature_shape_factor":
                major = require_float(r["L_major_raw"], f"{r['node_id']} L_major_raw")
                minor = require_float(r["L_minor_raw"], f"{r['node_id']} L_minor_raw")
                x = max(major, minor) / min(major, minor)
            elif col == "feature_spectral_index":
                x = require_float(r["m_ref_raw"], f"{r['node_id']} m_ref_raw")
            else:
                x = require_float(r[col], f"{r['node_id']} {col}")
            z[node_id][col] = (x - means[col]) / stds[col]
    return z


def euclidean(a: Dict[str, float], b: Dict[str, float]) -> float:
    return math.sqrt(sum((a[c] - b[c])**2 for c in FEATURE_COLUMNS))


def build_knn_edges(rows: List[dict], z: Dict[str, Dict[str, float]], k: int) -> List[Tuple[str, str, float]]:
    node_ids = [r["node_id"] for r in rows]
    neighbors = {}
    for i in node_ids:
        dists = []
        for j in node_ids:
            if i == j:
                continue
            d = euclidean(z[i], z[j])
            dists.append((d, j))
        dists.sort(key=lambda x: (x[0], x[1]))
        neighbors[i] = [j for _, j in dists[:k]]

    edge_map = {}
    for i in node_ids:
        for j in neighbors[i]:
            a, b = sorted((i, j))
            d = euclidean(z[a], z[b])
            edge_map[(a, b)] = 1.0 / (1.0 + d)
    return [(a, b, w) for (a, b), w in sorted(edge_map.items())]


def build_node_metadata(rows: List[dict]) -> List[dict]:
    family_to_shell = {"RING": 0, "CAVITY": 1, "MEMBRANE": 2}
    out = []
    for r in rows:
        fam = r["node_family"].strip().upper()
        major = require_float(r["L_major_raw"], f"{r['node_id']} L_major_raw")
        minor = require_float(r["L_minor_raw"], f"{r['node_id']} L_minor_raw")
        shape = max(major, minor) / min(major, minor)
        spectral = require_float(r["m_ref_raw"], f"{r['node_id']} m_ref_raw")
        out.append({
            "node_id": r["node_id"],
            "shell_index": family_to_shell[fam],
            "node_label": r["node_label"],
            "node_family": fam,
            "origin_tag": r["origin_tag"],
            "comment": r.get("comment", ""),
            "feature_shape_factor": f"{shape:.12g}",
            "feature_spectral_index": f"{spectral:.12g}",
        })
    return out


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
        q = deque([n])
        seen.add(n)
        comp = []
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

    feature_table = Path(cfg["input"]["feature_table_csv"])
    output_dir = Path(cfg["output"]["output_dir"])
    k_values = list(cfg["graph"]["k_values"])

    rows = load_feature_rows(feature_table)
    z = zscore_features(rows)
    node_meta = build_node_metadata(rows)
    nodes = [r["node_id"] for r in rows]
    family_by_id = {r["node_id"]: r["node_family"].strip().upper() for r in rows}

    output_dir.mkdir(parents=True, exist_ok=True)

    diagnostics_rows = []
    for k in k_values:
        edges = build_knn_edges(rows, z, int(k))
        baseline_rows = []
        for a, b, w in edges:
            fa, fb = family_by_id[a], family_by_id[b]
            baseline_rows.append({
                "source": a,
                "target": b,
                "weight": f"{w:.12g}",
                "edge_family": "intra_family" if fa == fb else "cross_family",
                "relation_type": "symmetric_knn_euclidean_similarity",
                "source_family": fa,
                "target_family": fb,
                "evidence_tag": f"bmc09a_knn_k_{k}",
                "comment": f"symmetric k-NN similarity edge with k={k}",
            })

        k_dir = output_dir / f"k_{k}"
        k_dir.mkdir(parents=True, exist_ok=True)
        write_csv(
            k_dir / "baseline_relational_table_real.csv",
            baseline_rows,
            ["source","target","weight","edge_family","relation_type","source_family","target_family","evidence_tag","comment"]
        )
        write_csv(
            k_dir / "node_metadata_real.csv",
            node_meta,
            ["node_id","shell_index","node_label","node_family","origin_tag","comment","feature_shape_factor","feature_spectral_index"]
        )

        comps = connected_components(nodes, edges)
        n = len(nodes)
        m = len(edges)
        density = (2*m)/(n*(n-1)) if n > 1 else 0.0
        mean_degree = (2*m)/n if n > 0 else 0.0
        summary = {
            "graph_construction_method": "symmetric_knn",
            "graph_construction_parameters": {"k": int(k)},
            "graph_node_count": n,
            "graph_edge_count": m,
            "connected_component_count": len(comps),
            "largest_component_size": max(len(c) for c in comps) if comps else 0,
            "mean_degree": mean_degree,
            "graph_density": density,
        }
        (k_dir / "graph_build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        diagnostics_rows.append({
            "k": int(k),
            **summary
        })

    write_csv(
        output_dir / "graph_build_diagnostics.csv",
        diagnostics_rows,
        ["k","graph_construction_method","graph_construction_parameters","graph_node_count","graph_edge_count","connected_component_count","largest_component_size","mean_degree","graph_density"]
    )
    print(f"Wrote k-NN graph inputs to: {output_dir}")


if __name__ == "__main__":
    main()
