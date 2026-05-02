#!/usr/bin/env python3
"""
BMS-FU02e — Carrier Role Null Localization Test

Purpose:
  Test whether the FU02d1 connected 17-face carrier region is reproduced by
  null carrier-role assignments on the fixed validated C60 graph.

Interpretation:
  Empirical exceedance fractions are diagnostic comparisons, not formal
  physical p-values.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


Edge = Tuple[str, str]


def edge_key(a: str, b: str) -> Edge:
    return (a, b) if a <= b else (b, a)


def edge_key_str(e: Edge) -> str:
    return f"{e[0]}--{e[1]}"


def parse_edge_key(s: str) -> Edge:
    a, b = str(s).split("--", 1)
    return edge_key(a, b)


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def as_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def as_int(x: Any, default: int = 0) -> int:
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default


def parse_list_like(value: Any) -> List[str]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    s = s.strip("[](){}")
    parts = re.split(r"[;,|\\s]+", s)
    return [p.strip().strip("'\"") for p in parts if p.strip().strip("'\"")]


def face_type(face_id: str) -> str:
    if face_id.startswith("H"):
        return "H"
    if face_id.startswith("P"):
        return "P"
    return ""


def connected_components(nodes: Set[str], adj: Dict[str, Set[str]]) -> List[Set[str]]:
    seen = set()
    comps = []
    for n in sorted(nodes):
        if n in seen:
            continue
        q = deque([n])
        seen.add(n)
        comp = set()
        while q:
            x = q.popleft()
            comp.add(x)
            for y in adj.get(x, set()):
                if y in nodes and y not in seen:
                    seen.add(y)
                    q.append(y)
        comps.append(comp)
    comps.sort(key=lambda c: (-len(c), sorted(c)[0] if c else ""))
    return comps


def edge_adjacency(edge_keys: Iterable[str]) -> Dict[str, Set[str]]:
    node_to_edges: Dict[str, Set[str]] = defaultdict(set)
    edge_keys = list(edge_keys)
    for es in edge_keys:
        a, b = parse_edge_key(es)
        node_to_edges[a].add(es)
        node_to_edges[b].add(es)
    adj = {es: set() for es in edge_keys}
    for es in edge_keys:
        a, b = parse_edge_key(es)
        adj[es] |= node_to_edges[a]
        adj[es] |= node_to_edges[b]
        adj[es].discard(es)
    return adj


def build_face_maps(c60_edges: List[Dict[str, str]]) -> Tuple[Dict[str, List[str]], Dict[str, Set[str]], List[Dict[str, str]]]:
    edge_to_faces: Dict[str, List[str]] = {}
    face_adj: Dict[str, Set[str]] = defaultdict(set)
    face_adj_rows: List[Dict[str, str]] = []
    for r in c60_edges:
        es = edge_key_str(edge_key(r["source"], r["target"]))
        faces = parse_list_like(r.get("shared_faces", ""))
        edge_to_faces[es] = faces
        if len(faces) >= 2:
            for i, a in enumerate(faces):
                for b in faces[i + 1:]:
                    if a == b:
                        continue
                    face_adj[a].add(b)
                    face_adj[b].add(a)
                    face_adj_rows.append({"edge_key": es, "face_a": a, "face_b": b})
    return edge_to_faces, face_adj, face_adj_rows


def compute_face_metrics(
    hh_edges: Set[str],
    hp_edges: Set[str],
    edge_to_faces: Dict[str, List[str]],
    face_adj: Dict[str, Set[str]],
    all_faces: Set[str],
) -> Dict[str, Any]:
    carrier_edges = hh_edges | hp_edges

    face_hh = defaultdict(set)
    face_hp = defaultdict(set)
    face_car = defaultdict(set)

    for es in hh_edges:
        for f in edge_to_faces.get(es, []):
            face_hh[f].add(es)
            face_car[f].add(es)
    for es in hp_edges:
        for f in edge_to_faces.get(es, []):
            face_hp[f].add(es)
            face_car[f].add(es)

    carrier_faces = {f for f in all_faces if face_car.get(f)}
    hh_faces = {f for f in all_faces if face_hh.get(f)}
    hp_faces = {f for f in all_faces if face_hp.get(f)}
    mixed_faces = hh_faces & hp_faces

    comps = connected_components(carrier_faces, face_adj)
    hh_comps = connected_components(hh_faces, face_adj)
    hp_comps = connected_components(hp_faces, face_adj)
    mixed_comps = connected_components(mixed_faces, face_adj)

    label_counts = Counter()
    for f in all_faces:
        if f in mixed_faces:
            label_counts["mixed_seam_boundary_face"] += 1
        elif f in hh_faces:
            label_counts["hh_seam_face"] += 1
        elif f in hp_faces:
            label_counts["hp_boundary_face"] += 1
        elif any(nb in carrier_faces for nb in face_adj.get(f, set())):
            label_counts["carrier_adjacent_face"] += 1
        else:
            label_counts["noncarrier_face"] += 1

    metrics = {
        "carrier_face_count": len(carrier_faces),
        "carrier_face_fraction": len(carrier_faces) / len(all_faces) if all_faces else 0.0,
        "carrier_face_component_count": len(comps),
        "largest_carrier_face_component_count": max((len(c) for c in comps), default=0),
        "hh_face_count": len(hh_faces),
        "hp_face_count": len(hp_faces),
        "mixed_seam_boundary_face_count": len(mixed_faces),
        "hp_boundary_face_count": label_counts.get("hp_boundary_face", 0),
        "carrier_adjacent_face_count": label_counts.get("carrier_adjacent_face", 0),
        "noncarrier_face_count": label_counts.get("noncarrier_face", 0),
        "carrier_hexagon_face_count": sum(1 for f in carrier_faces if face_type(f) == "H"),
        "carrier_pentagon_face_count": sum(1 for f in carrier_faces if face_type(f) == "P"),
        "mixed_face_hexagon_count": sum(1 for f in mixed_faces if face_type(f) == "H"),
        "mixed_face_pentagon_count": sum(1 for f in mixed_faces if face_type(f) == "P"),
        "hh_face_component_count": len(hh_comps),
        "largest_hh_face_component_count": max((len(c) for c in hh_comps), default=0),
        "hp_face_component_count": len(hp_comps),
        "largest_hp_face_component_count": max((len(c) for c in hp_comps), default=0),
        "mixed_face_component_count": len(mixed_comps),
        "largest_mixed_face_component_count": max((len(c) for c in mixed_comps), default=0),
        "carrier_face_ids": ";".join(sorted(carrier_faces)),
        "hh_face_ids": ";".join(sorted(hh_faces)),
        "hp_face_ids": ";".join(sorted(hp_faces)),
        "mixed_face_ids": ";".join(sorted(mixed_faces)),
    }
    return metrics


def random_connected_subset(edge_pool: Set[str], size: int, edge_adj: Dict[str, Set[str]], rng: random.Random) -> Set[str]:
    if size <= 0:
        return set()
    if size >= len(edge_pool):
        return set(edge_pool)

    start = rng.choice(sorted(edge_pool))
    selected = {start}
    frontier = set(edge_adj.get(start, set())) & edge_pool
    attempts = 0
    while len(selected) < size and attempts < 2000:
        attempts += 1
        if frontier:
            nxt = rng.choice(sorted(frontier))
        else:
            # disconnected fallback; starts another local component if necessary
            remaining = sorted(edge_pool - selected)
            if not remaining:
                break
            nxt = rng.choice(remaining)
        selected.add(nxt)
        frontier |= (edge_adj.get(nxt, set()) & edge_pool)
        frontier -= selected
    if len(selected) < size:
        selected |= set(rng.sample(sorted(edge_pool - selected), min(size - len(selected), len(edge_pool - selected))))
    return selected


def assign_null_roles(
    null_family: str,
    real_hh: Set[str],
    real_hp: Set[str],
    hh_pool: Set[str],
    hp_pool: Set[str],
    all_edges: Set[str],
    edge_adj: Dict[str, Set[str]],
    rng: random.Random,
) -> Tuple[Set[str], Set[str]]:
    hh_n = len(real_hh)
    hp_n = len(real_hp)

    if null_family in {"edge_type_preserving_role_shuffle", "degree_spread_role_shuffle"}:
        hh = set(rng.sample(sorted(hh_pool), hh_n))
        hp = set(rng.sample(sorted(hp_pool), hp_n))
        return hh, hp

    if null_family == "component_size_preserving_hp_shuffle":
        hh = set(rng.sample(sorted(hh_pool), hh_n))
        component_sizes = [5, 5, 5, 4, 4]
        hp = set()
        for size in component_sizes:
            available = hp_pool - hp
            if not available:
                break
            comp = random_connected_subset(available, min(size, len(available)), edge_adj, rng)
            hp |= comp
        if len(hp) < hp_n:
            hp |= set(rng.sample(sorted(hp_pool - hp), min(hp_n - len(hp), len(hp_pool - hp))))
        if len(hp) > hp_n:
            hp = set(rng.sample(sorted(hp), hp_n))
        return hh, hp

    if null_family == "hh_anchor_neighborhood_decoy":
        hh = set(rng.sample(sorted(hh_pool), hh_n))
        near_hp = {e for h in hh for e in edge_adj.get(h, set()) if e in hp_pool}
        hp = set()
        if near_hp:
            hp |= set(rng.sample(sorted(near_hp), min(hp_n, len(near_hp))))
        if len(hp) < hp_n:
            second = {e for x in hp | near_hp for e in edge_adj.get(x, set()) if e in hp_pool and e not in hp}
            if second:
                hp |= set(rng.sample(sorted(second), min(hp_n - len(hp), len(second))))
        if len(hp) < hp_n:
            hp |= set(rng.sample(sorted(hp_pool - hp), min(hp_n - len(hp), len(hp_pool - hp))))
        return hh, hp

    raise ValueError(f"Unknown null family: {null_family}")


def summarize_nulls(real_metrics: Dict[str, Any], rows: List[Dict[str, Any]], null_family: str, metric_names: List[str]) -> List[Dict[str, Any]]:
    out = []
    n = len(rows)
    for m in metric_names:
        vals = [as_float(r[m]) for r in rows]
        if not vals:
            continue
        real = as_float(real_metrics[m])
        mean = statistics.mean(vals)
        std = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        median = statistics.median(vals)
        mn = min(vals)
        mx = max(vals)
        ge = sum(1 for v in vals if v >= real) / n
        le = sum(1 for v in vals if v <= real) / n
        rank = 1 + sum(1 for v in vals if v > real)

        # Conservative interpretation. Metric-specific direction is descriptive.
        if ge >= 0.1 and le >= 0.1:
            label = "null_reproduces_metric_behavior"
        elif ge < 0.1:
            label = "real_high_relative_to_null"
        elif le < 0.1:
            label = "real_low_relative_to_null"
        else:
            label = "mixed_or_metric_dependent"

        out.append({
            "null_family": null_family,
            "metric_name": m,
            "real_value": real,
            "null_mean": mean,
            "null_std": std,
            "null_min": mn,
            "null_median": median,
            "null_max": mx,
            "null_replicate_count": n,
            "empirical_ge_fraction": ge,
            "empirical_le_fraction": le,
            "rank_position_of_real": rank,
            "interpretation_label": label,
        })
    return out


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(int(cfg["run"]["random_seed"]))
    repeats = int(cfg["run"]["repeats_per_null_family"])
    warnings: List[Dict[str, str]] = []

    fu02d1_dir = root / cfg["inputs"]["fu02d1_output_dir"]
    fu02d_dir = root / cfg["inputs"]["fu02d_output_dir"]

    fu02d1_manifest = read_json(fu02d1_dir / "bms_fu02d1_run_manifest.json")
    fu02d1_warnings = read_json(fu02d1_dir / "bms_fu02d1_warnings.json") if (fu02d1_dir / "bms_fu02d1_warnings.json").exists() else []
    if fu02d1_warnings:
        warnings.append({"severity": "info", "message": f"FU02d1 warnings carried forward: {len(fu02d1_warnings)}"})

    fu02d_edges = read_csv(fu02d_dir / "bms_fu02d_carrier_edge_geometry.csv")
    c60_edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    c60_faces = read_csv(root / cfg["inputs"]["c60_faces_csv"])
    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])

    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 graph manifest does not report c60_valid=true."})

    edge_to_faces, face_adj, _ = build_face_maps(c60_edges)
    all_faces = {f for faces in edge_to_faces.values() for f in faces}
    all_edges = {edge_key_str(edge_key(r["source"], r["target"])) for r in c60_edges}
    edge_adj = edge_adjacency(all_edges)

    hh_pool = {edge_key_str(edge_key(r["source"], r["target"])) for r in c60_edges if r.get("edge_type") == "6_6" or r.get("shared_face_types") == "H,H"}
    hp_pool = {edge_key_str(edge_key(r["source"], r["target"])) for r in c60_edges if r.get("edge_type") == "5_6" or r.get("shared_face_types") == "H,P"}

    real_hh = {r["edge_key"] for r in fu02d_edges if r.get("role_group") == cfg["real_roles"]["hh_consensus_role_group"]}
    real_hp = {r["edge_key"] for r in fu02d_edges if r.get("role_group") == cfg["real_roles"]["hp_secondary_role_group"]}

    real_metrics = compute_face_metrics(real_hh, real_hp, edge_to_faces, face_adj, all_faces)

    metric_names = [
        "carrier_face_count",
        "carrier_face_fraction",
        "carrier_face_component_count",
        "largest_carrier_face_component_count",
        "hh_face_count",
        "hp_face_count",
        "mixed_seam_boundary_face_count",
        "hp_boundary_face_count",
        "carrier_adjacent_face_count",
        "noncarrier_face_count",
        "carrier_hexagon_face_count",
        "carrier_pentagon_face_count",
        "mixed_face_hexagon_count",
        "mixed_face_pentagon_count",
        "hh_face_component_count",
        "largest_hh_face_component_count",
        "hp_face_component_count",
        "largest_hp_face_component_count",
        "mixed_face_component_count",
        "largest_mixed_face_component_count",
    ]

    null_rows: List[Dict[str, Any]] = []
    inventory_rows: List[Dict[str, Any]] = []
    sample_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []

    for nf in cfg["null_families"]["include"]:
        fam_rows = []
        for i in range(repeats):
            hh, hp = assign_null_roles(nf, real_hh, real_hp, hh_pool, hp_pool, all_edges, edge_adj, rng)
            metrics = compute_face_metrics(hh, hp, edge_to_faces, face_adj, all_faces)
            row = {
                "null_family": nf,
                "replicate_index": i,
                "hh_edge_count": len(hh),
                "hp_edge_count": len(hp),
            }
            for m in metric_names:
                row[m] = metrics.get(m, 0)
            null_rows.append(row)
            fam_rows.append(row)

            if i < 5:
                sample_rows.append({
                    "null_family": nf,
                    "replicate_index": i,
                    "hh_edges": ";".join(sorted(hh)),
                    "hp_edges": ";".join(sorted(hp)),
                    "carrier_face_ids": metrics.get("carrier_face_ids", ""),
                    "mixed_face_ids": metrics.get("mixed_face_ids", ""),
                })

        inventory_rows.append({
            "null_family": nf,
            "replicate_count": repeats,
            "hh_edge_count_per_replicate": len(real_hh),
            "hp_edge_count_per_replicate": len(real_hp),
            "description": {
                "edge_type_preserving_role_shuffle": "Shuffle H,H among H,H edges and H,P among H,P edges.",
                "degree_spread_role_shuffle": "Degree-spread explicit family; equivalent to edge-type preserving on 3-regular C60.",
                "component_size_preserving_hp_shuffle": "Preserve H,P component size multiset approximately by connected H,P subsets.",
                "hh_anchor_neighborhood_decoy": "Place H,P preferentially near shuffled H,H anchors.",
            }.get(nf, ""),
        })
        summary_rows.extend(summarize_nulls(real_metrics, fam_rows, nf, metric_names))

    # Save outputs
    out = cfg["outputs"]

    null_fields = ["null_family", "replicate_index", "hh_edge_count", "hp_edge_count"] + metric_names
    write_csv(outdir / out["null_localization_metrics_csv"], null_rows, null_fields)

    summary_fields = [
        "null_family", "metric_name", "real_value", "null_mean", "null_std", "null_min",
        "null_median", "null_max", "null_replicate_count", "empirical_ge_fraction",
        "empirical_le_fraction", "rank_position_of_real", "interpretation_label",
    ]
    write_csv(outdir / out["real_vs_null_summary_csv"], summary_rows, summary_fields)

    write_csv(outdir / out["null_family_inventory_csv"], inventory_rows, [
        "null_family", "replicate_count", "hh_edge_count_per_replicate",
        "hp_edge_count_per_replicate", "description",
    ])

    write_csv(outdir / out["null_carrier_assignments_sample_csv"], sample_rows, [
        "null_family", "replicate_index", "hh_edges", "hp_edges", "carrier_face_ids", "mixed_face_ids",
    ])

    with (outdir / out["real_face_metrics_json"]).open("w", encoding="utf-8") as f:
        json.dump(real_metrics, f, indent=2, sort_keys=True)

    # Manifest with selected high-value labels
    label_counts = Counter(r["interpretation_label"] for r in summary_rows)
    key_metrics = [
        "carrier_face_count",
        "carrier_face_component_count",
        "largest_carrier_face_component_count",
        "mixed_seam_boundary_face_count",
        "carrier_pentagon_face_count",
        "largest_mixed_face_component_count",
    ]
    key_summary = [
        r for r in summary_rows
        if r["metric_name"] in key_metrics
    ]

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "fu02d1_run_id": fu02d1_manifest.get("run_id", ""),
        "fu02d1_warning_count": len(fu02d1_warnings),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "face_count": len(all_faces),
        "edge_count": len(all_edges),
        "hh_pool_count": len(hh_pool),
        "hp_pool_count": len(hp_pool),
        "real_hh_edge_count": len(real_hh),
        "real_hp_edge_count": len(real_hp),
        "null_family_count": len(cfg["null_families"]["include"]),
        "repeats_per_null_family": repeats,
        "null_metric_row_count": len(null_rows),
        "summary_row_count": len(summary_rows),
        "interpretation_label_counts": dict(sorted(label_counts.items())),
        "real_key_metrics": {m: real_metrics.get(m, 0) for m in key_metrics},
        "key_summary": key_summary,
        "row_counts": {
            "null_localization_metrics": len(null_rows),
            "real_vs_null_summary": len(summary_rows),
            "null_family_inventory": len(inventory_rows),
            "null_carrier_assignments_sample": len(sample_rows),
            "warnings": len(warnings),
        },
        "scope_note": "FU02e-v0 uses role-assignment nulls on the fixed validated C60 graph; empirical fractions are diagnostics, not formal physical p-values.",
    }

    with (outdir / out["run_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    with (outdir / out["warnings_json"]).open("w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, sort_keys=True)
    with (outdir / out["resolved_config_yaml"]).open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02e carrier role null localization test.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
