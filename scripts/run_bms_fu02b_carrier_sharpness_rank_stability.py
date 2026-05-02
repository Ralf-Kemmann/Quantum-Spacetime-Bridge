#!/usr/bin/env python3
"""
BMS-FU02b — Carrier Sharpness and Rank-Stability Runner

Purpose:
  Sharpen FU02-v0's broad carrier-positive result by applying:
    - decoy-penalized scoring
    - top-k sets
    - motif enrichment
    - rank stability
    - node/neighborhood aggregation

Scope:
  FU02b-v0 reads FU02 outputs. It does not fully reconstruct FU01c
  representation-specific contexts. Therefore topology-sensitive score is based
  on FU02 persistence fields, not full per-context recomputation.

Interpretation boundary:
  Sharp carriers are methodological relational structure-carrier candidates.
  They are not physical spacetime atoms and not proof of emergent spacetime.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import pstdev
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


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


def parse_json_field(x: str) -> Dict[str, float]:
    if not x:
        return {}
    try:
        raw = json.loads(x)
        return {str(k): as_float(v) for k, v in raw.items()}
    except Exception:
        return {}


def split_semicolon(x: str) -> List[str]:
    if not x:
        return []
    return [p for p in x.split(";") if p]


def rank_desc(rows: List[Dict[str, Any]], score_name: str, rank_name: str) -> None:
    # Dense stable rank by score descending, tie-broken by edge_key.
    ordered = sorted(rows, key=lambda r: (-as_float(r.get(score_name, 0.0)), str(r.get("edge_key", ""))))
    for idx, r in enumerate(ordered, start=1):
        r[rank_name] = idx


def rank_norm(rank: int, n: int) -> float:
    if n <= 1:
        return 1.0
    return 1.0 - ((rank - 1) / (n - 1))


def topk_label(score_name: str, k: int) -> str:
    return f"{score_name}__top_{k}"


def motif_signature(row: Dict[str, Any]) -> str:
    sft = str(row.get("shared_face_types", ""))
    if sft:
        return sft
    return str(row.get("edge_type", "unknown"))


def classify_edge(row: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    top_cut = int(cfg["labeling"]["sharp_top_rank_cutoff"])
    survivor_cut = int(cfg["labeling"]["survivor_top_rank_cutoff"])
    min_topo = int(cfg["labeling"]["min_positive_topology_representation_count"])
    min_decoy = float(cfg["labeling"]["min_decoy_penalized_score"])

    edge_type = row.get("edge_type", "")
    shared = row.get("shared_face_types", "")
    sharp_rank = as_int(row.get("sharpness_rank", 9999), 9999)
    decoy_rank = as_int(row.get("rank_decoy_penalized", 9999), 9999)
    topo_rank = as_int(row.get("rank_topology_sensitive", 9999), 9999)
    topo_count = as_int(row.get("positive_topology_representation_count", 0))
    decoy_score = as_float(row.get("score_decoy_penalized", 0.0))

    if sharp_rank <= top_cut and topo_count >= min_topo and decoy_score > min_decoy:
        if edge_type == "6_6" and shared == "H,H":
            return "sharp_hh_seam_carrier"
        if edge_type == "5_6" and shared == "H,P":
            return "sharp_hp_boundary_carrier"
        return "sharp_cross_representation_carrier"

    if topo_rank <= top_cut and topo_count >= min_topo:
        return "sharp_topology_carrier"

    if decoy_score > min_decoy and decoy_rank <= survivor_cut:
        return "decoy_penalized_survivor"

    if decoy_score <= 0 and as_float(row.get("score_fu02_mean_null", 0.0)) > 0:
        return "decoy_reproduced_candidate"

    if sharp_rank <= 30:
        return "motif_enriched_candidate"

    if as_float(row.get("score_fu02_mean_null", 0.0)) > 0:
        return "broad_positive_only"

    return "inconclusive_or_tie_sensitive"


def compute_edge_sharpness(edge_rows: List[Dict[str, str]], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for r in edge_rows:
        null_rates = parse_json_field(r.get("null_retention_rates_json", ""))
        max_null = max(null_rates.values()) if null_rates else as_float(r.get("mean_null_retention_rate", 0.0))
        real = as_float(r.get("real_retention_rate", 0.0))
        fu02_score = as_float(r.get("load_bearing_score", 0.0))
        decoy_penalized = real - max_null

        topo_count = as_int(r.get("positive_topology_representation_count", 0))
        pos_reps = set(split_semicolon(r.get("positive_representations", "")))
        topo_reps = set(cfg["sharpness"]["topology_sensitive_representations"])
        topo_hits = len(pos_reps & topo_reps)
        # v0 topology score proxy: FU02 score scaled by topology persistence.
        # Full context-level topology deltas are deferred to FU02c.
        topo_scale = topo_hits / max(1, len(topo_reps))
        topology_sensitive = fu02_score * topo_scale

        core_count = as_int(r.get("positive_core_variant_count", 0))
        core_stability = core_count / 4.0

        row = {
            "edge_key": r.get("edge_key", ""),
            "source": r.get("source", ""),
            "target": r.get("target", ""),
            "edge_type": r.get("edge_type", ""),
            "shared_face_types": r.get("shared_face_types", ""),
            "score_fu02_mean_null": fu02_score,
            "score_decoy_penalized": decoy_penalized,
            "score_topology_sensitive": topology_sensitive,
            "score_core_variant_stability": core_stability,
            "real_retention_rate": real,
            "mean_null_retention_rate": as_float(r.get("mean_null_retention_rate", 0.0)),
            "max_null_retention_rate": max_null,
            "positive_representation_count": as_int(r.get("positive_representation_count", 0)),
            "positive_representations": r.get("positive_representations", ""),
            "positive_topology_representation_count": topo_count,
            "positive_topology_representations": r.get("positive_topology_representations", ""),
            "positive_core_variant_count": core_count,
            "positive_core_variants": r.get("positive_core_variants", ""),
            "fu02_candidate_label": r.get("candidate_label", ""),
            "null_retention_rates_json": json.dumps(null_rates, sort_keys=True),
        }
        rows.append(row)

    for score, rank in [
        ("score_fu02_mean_null", "rank_fu02_mean_null"),
        ("score_decoy_penalized", "rank_decoy_penalized"),
        ("score_topology_sensitive", "rank_topology_sensitive"),
        ("score_core_variant_stability", "rank_core_variant_stability"),
    ]:
        rank_desc(rows, score, rank)

    n = len(rows)
    weights = cfg["sharpness"]["composite_weights"]

    for r in rows:
        sharp = (
            float(weights["decoy_penalized_rank"]) * rank_norm(as_int(r["rank_decoy_penalized"]), n)
            + float(weights["topology_sensitive_rank"]) * rank_norm(as_int(r["rank_topology_sensitive"]), n)
            + float(weights["core_variant_stability_rank"]) * rank_norm(as_int(r["rank_core_variant_stability"]), n)
            + float(weights["fu02_mean_null_rank"]) * rank_norm(as_int(r["rank_fu02_mean_null"]), n)
        )
        r["sharpness_score"] = sharp

    rank_desc(rows, "sharpness_score", "sharpness_rank")

    topk_values = [int(k) for k in cfg["sharpness"]["topk_values"]]
    score_names = [
        "score_fu02_mean_null",
        "score_decoy_penalized",
        "score_topology_sensitive",
        "score_core_variant_stability",
        "sharpness_score",
    ]
    rank_names = {
        "score_fu02_mean_null": "rank_fu02_mean_null",
        "score_decoy_penalized": "rank_decoy_penalized",
        "score_topology_sensitive": "rank_topology_sensitive",
        "score_core_variant_stability": "rank_core_variant_stability",
        "sharpness_score": "sharpness_rank",
    }

    for r in rows:
        memberships = []
        vote_count = 0
        for score_name in score_names:
            rank_value = as_int(r[rank_names[score_name]])
            for k in topk_values:
                if rank_value <= k:
                    memberships.append(topk_label(score_name, k))
            if rank_value <= min(topk_values):
                vote_count += 1
        r["topk_memberships"] = ";".join(memberships)
        r["sharpness_vote_count"] = vote_count

    for r in rows:
        ranks = [
            as_int(r["rank_fu02_mean_null"]),
            as_int(r["rank_decoy_penalized"]),
            as_int(r["rank_topology_sensitive"]),
            as_int(r["rank_core_variant_stability"]),
            as_int(r["sharpness_rank"]),
        ]
        r["rank_std"] = pstdev(ranks) if len(ranks) > 1 else 0.0
        r["best_rank"] = min(ranks)
        r["worst_rank"] = max(ranks)
        r["top10_count"] = sum(1 for x in ranks if x <= 10)
        r["top20_count"] = sum(1 for x in ranks if x <= 20)
        r["top30_count"] = sum(1 for x in ranks if x <= 30)
        r["candidate_label"] = classify_edge(r, cfg)

    return sorted(rows, key=lambda r: as_int(r["sharpness_rank"]))


def compute_topk_sets(rows: List[Dict[str, Any]], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    score_to_rank = {
        "score_fu02_mean_null": "rank_fu02_mean_null",
        "score_decoy_penalized": "rank_decoy_penalized",
        "score_topology_sensitive": "rank_topology_sensitive",
        "score_core_variant_stability": "rank_core_variant_stability",
        "sharpness_score": "sharpness_rank",
    }
    for score, rank_name in score_to_rank.items():
        for k in cfg["sharpness"]["topk_values"]:
            selected = sorted([r for r in rows if as_int(r[rank_name]) <= int(k)], key=lambda r: as_int(r[rank_name]))
            out.append({
                "score_name": score,
                "topk_label": f"top_{int(k)}",
                "k": int(k),
                "edge_count": len(selected),
                "edges": ";".join(r["edge_key"] for r in selected),
            })
    return out


def compute_motif_enrichment(rows: List[Dict[str, Any]], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    baseline_hh = 30 / 90
    baseline_hp = 60 / 90
    score_to_rank = {
        "score_fu02_mean_null": "rank_fu02_mean_null",
        "score_decoy_penalized": "rank_decoy_penalized",
        "score_topology_sensitive": "rank_topology_sensitive",
        "score_core_variant_stability": "rank_core_variant_stability",
        "sharpness_score": "sharpness_rank",
    }
    for score, rank_name in score_to_rank.items():
        for k in cfg["sharpness"]["topk_values"]:
            selected = sorted([r for r in rows if as_int(r[rank_name]) <= int(k)], key=lambda r: as_int(r[rank_name]))
            hh = sum(1 for r in selected if motif_signature(r) == "H,H")
            hp = sum(1 for r in selected if motif_signature(r) == "H,P")
            kk = len(selected)
            hh_frac = hh / kk if kk else 0.0
            hp_frac = hp / kk if kk else 0.0
            out.append({
                "score_name": score,
                "topk_label": f"top_{int(k)}",
                "k": int(k),
                "hh_count": hh,
                "hp_count": hp,
                "hh_fraction": hh_frac,
                "hp_fraction": hp_frac,
                "hh_enrichment_ratio": hh_frac / baseline_hh if baseline_hh else 0.0,
                "hp_enrichment_ratio": hp_frac / baseline_hp if baseline_hp else 0.0,
                "top_edges": ";".join(r["edge_key"] for r in selected[:20]),
            })
    return out


def compute_decoy_profiles(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        rates = parse_json_field(r.get("null_retention_rates_json", ""))
        out.append({
            "edge_key": r["edge_key"],
            "real_retention_rate": r["real_retention_rate"],
            "mean_null_retention_rate": r["mean_null_retention_rate"],
            "max_null_retention_rate": r["max_null_retention_rate"],
            "score_fu02_mean_null": r["score_fu02_mean_null"],
            "score_decoy_penalized": r["score_decoy_penalized"],
            "degree_preserving_rewire_retention": rates.get("degree_preserving_rewire", ""),
            "edge_class_shuffle_retention": rates.get("edge_class_shuffle", ""),
            "motif_class_preserving_edge_swap_proxy_retention": rates.get("motif_class_preserving_edge_swap_proxy", ""),
            "core_seeded_decoy_retention": rates.get("core_seeded_decoy", ""),
        })
    return out


def compute_node_sharpness(node_rows: List[Dict[str, str]], edge_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    incident = defaultdict(list)
    for e in edge_rows:
        incident[e["source"]].append(e)
        incident[e["target"]].append(e)

    out = []
    for n in node_rows:
        node_id = n["node_id"]
        inc = incident.get(node_id, [])
        sharp_scores = [as_float(e["sharpness_score"]) for e in inc]
        decoy_scores = [as_float(e["score_decoy_penalized"]) for e in inc]
        top_edges = sorted(inc, key=lambda e: as_float(e["sharpness_score"]), reverse=True)
        labels = Counter(e["candidate_label"] for e in inc)
        row = {
            "node_id": node_id,
            "degree": n.get("degree", ""),
            "incident_6_6_count": n.get("incident_6_6_count", ""),
            "incident_5_6_count": n.get("incident_5_6_count", ""),
            "fu02_node_load_bearing_score": n.get("load_bearing_score", ""),
            "incident_edge_count": len(inc),
            "mean_incident_sharpness_score": sum(sharp_scores) / len(sharp_scores) if sharp_scores else 0.0,
            "max_incident_sharpness_score": max(sharp_scores) if sharp_scores else 0.0,
            "mean_incident_decoy_penalized_score": sum(decoy_scores) / len(decoy_scores) if decoy_scores else 0.0,
            "sharp_incident_edge_count_top20": sum(1 for e in inc if as_int(e["sharpness_rank"]) <= 20),
            "sharp_incident_edge_count_top30": sum(1 for e in inc if as_int(e["sharpness_rank"]) <= 30),
            "incident_candidate_label_counts": json.dumps(dict(sorted(labels.items())), sort_keys=True),
            "top_incident_edges": ";".join(e["edge_key"] for e in top_edges),
        }
        out.append(row)

    out.sort(key=lambda r: (-as_float(r["mean_incident_sharpness_score"]), r["node_id"]))
    for idx, r in enumerate(out, start=1):
        r["node_sharpness_rank"] = idx
    return out


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)
    warnings = []

    fu02_dir = root / cfg["inputs"]["fu02_output_dir"]
    fu02_manifest_path = fu02_dir / "bms_fu02_run_manifest.json"
    fu02_warnings_path = fu02_dir / "bms_fu02_warnings.json"

    if not fu02_manifest_path.exists():
        raise SystemExit(f"Missing FU02 manifest: {fu02_manifest_path}")

    fu02_manifest = read_json(fu02_manifest_path)
    fu02_warnings = read_json(fu02_warnings_path) if fu02_warnings_path.exists() else []
    if fu02_warnings:
        warnings.append({
            "severity": "info",
            "message": f"FU02 warnings carried forward: {len(fu02_warnings)}. See FU02 warnings for skipped shell contexts.",
        })

    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])
    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 graph manifest does not report c60_valid=true."})

    edge_scores_in = read_csv(fu02_dir / "bms_fu02_edge_load_bearing_scores.csv")
    node_scores_in = read_csv(fu02_dir / "bms_fu02_node_load_bearing_scores.csv")

    edge_rows = compute_edge_sharpness(edge_scores_in, cfg)
    topk_rows = compute_topk_sets(edge_rows, cfg)
    motif_rows = compute_motif_enrichment(edge_rows, cfg)
    profile_rows = compute_decoy_profiles(edge_rows)
    node_rows = compute_node_sharpness(node_scores_in, edge_rows)

    sharp_candidates = [
        r for r in edge_rows
        if r["candidate_label"] not in {"broad_positive_only", "inconclusive_or_tie_sensitive", "decoy_reproduced_candidate"}
    ]

    sharp_neighborhoods = [
        r for r in node_rows
        if as_int(r["sharp_incident_edge_count_top20"]) > 0 or as_int(r["sharp_incident_edge_count_top30"]) >= 2
    ]

    rank_rows = []
    for r in edge_rows:
        rank_rows.append({
            "edge_key": r["edge_key"],
            "rank_fu02_mean_null": r["rank_fu02_mean_null"],
            "rank_decoy_penalized": r["rank_decoy_penalized"],
            "rank_topology_sensitive": r["rank_topology_sensitive"],
            "rank_core_variant_stability": r["rank_core_variant_stability"],
            "sharpness_rank": r["sharpness_rank"],
            "rank_std": r["rank_std"],
            "best_rank": r["best_rank"],
            "worst_rank": r["worst_rank"],
            "top10_count": r["top10_count"],
            "top20_count": r["top20_count"],
            "top30_count": r["top30_count"],
        })

    edge_fields = [
        "edge_key", "source", "target", "edge_type", "shared_face_types",
        "score_fu02_mean_null", "score_decoy_penalized", "score_topology_sensitive",
        "score_core_variant_stability", "real_retention_rate",
        "mean_null_retention_rate", "max_null_retention_rate",
        "rank_fu02_mean_null", "rank_decoy_penalized",
        "rank_topology_sensitive", "rank_core_variant_stability",
        "sharpness_score", "sharpness_rank", "sharpness_vote_count",
        "topk_memberships", "rank_std", "best_rank", "worst_rank",
        "top10_count", "top20_count", "top30_count",
        "positive_representation_count", "positive_representations",
        "positive_topology_representation_count", "positive_topology_representations",
        "positive_core_variant_count", "positive_core_variants",
        "fu02_candidate_label", "candidate_label", "null_retention_rates_json",
    ]

    node_fields = [
        "node_id", "degree", "incident_6_6_count", "incident_5_6_count",
        "fu02_node_load_bearing_score", "incident_edge_count",
        "mean_incident_sharpness_score", "max_incident_sharpness_score",
        "mean_incident_decoy_penalized_score",
        "sharp_incident_edge_count_top20", "sharp_incident_edge_count_top30",
        "incident_candidate_label_counts", "top_incident_edges",
        "node_sharpness_rank",
    ]

    topk_fields = ["score_name", "topk_label", "k", "edge_count", "edges"]
    motif_fields = [
        "score_name", "topk_label", "k", "hh_count", "hp_count",
        "hh_fraction", "hp_fraction", "hh_enrichment_ratio",
        "hp_enrichment_ratio", "top_edges",
    ]
    rank_fields = [
        "edge_key", "rank_fu02_mean_null", "rank_decoy_penalized",
        "rank_topology_sensitive", "rank_core_variant_stability",
        "sharpness_rank", "rank_std", "best_rank", "worst_rank",
        "top10_count", "top20_count", "top30_count",
    ]
    profile_fields = [
        "edge_key", "real_retention_rate", "mean_null_retention_rate",
        "max_null_retention_rate", "score_fu02_mean_null",
        "score_decoy_penalized", "degree_preserving_rewire_retention",
        "edge_class_shuffle_retention",
        "motif_class_preserving_edge_swap_proxy_retention",
        "core_seeded_decoy_retention",
    ]

    out = cfg["outputs"]
    write_csv(outdir / out["edge_sharpness_scores_csv"], edge_rows, edge_fields)
    write_csv(outdir / out["node_sharpness_scores_csv"], node_rows, node_fields)
    write_csv(outdir / out["topk_edge_sets_csv"], topk_rows, topk_fields)
    write_csv(outdir / out["motif_enrichment_csv"], motif_rows, motif_fields)
    write_csv(outdir / out["rank_stability_matrix_csv"], rank_rows, rank_fields)
    write_csv(outdir / out["decoy_penalty_profiles_csv"], profile_rows, profile_fields)
    write_csv(outdir / out["sharp_candidate_carriers_csv"], sharp_candidates, edge_fields)
    write_csv(outdir / out["sharp_candidate_neighborhoods_csv"], sharp_neighborhoods, node_fields)

    label_counts = Counter(r["candidate_label"] for r in edge_rows)
    sharp_label_counts = Counter(r["candidate_label"] for r in sharp_candidates)
    top20_sharpness = [r for r in edge_rows if as_int(r["sharpness_rank"]) <= 20]
    top20_motifs = Counter(motif_signature(r) for r in top20_sharpness)

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "input_fu02_output_dir": cfg["inputs"]["fu02_output_dir"],
        "fu02_run_id": fu02_manifest.get("run_id", ""),
        "fu02_warning_count": len(fu02_warnings),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "edge_count": len(edge_rows),
        "node_count": len(node_rows),
        "sharp_candidate_count": len(sharp_candidates),
        "sharp_neighborhood_count": len(sharp_neighborhoods),
        "candidate_label_counts": dict(sorted(label_counts.items())),
        "sharp_candidate_label_counts": dict(sorted(sharp_label_counts.items())),
        "top20_sharpness_motif_counts": dict(sorted(top20_motifs.items())),
        "row_counts": {
            "edge_sharpness_scores": len(edge_rows),
            "node_sharpness_scores": len(node_rows),
            "topk_edge_sets": len(topk_rows),
            "motif_enrichment": len(motif_rows),
            "rank_stability_matrix": len(rank_rows),
            "decoy_penalty_profiles": len(profile_rows),
            "sharp_candidate_carriers": len(sharp_candidates),
            "sharp_candidate_neighborhoods": len(sharp_neighborhoods),
            "warnings": len(warnings),
        },
        "scope_note": "FU02b-v0 topology-sensitive score uses FU02 persistence fields, not full context-level FU01c recomputation.",
    }

    with (outdir / out["run_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    with (outdir / out["warnings_json"]).open("w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, sort_keys=True)
    with (outdir / out["resolved_config_yaml"]).open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02b carrier sharpness and rank-stability extension.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
