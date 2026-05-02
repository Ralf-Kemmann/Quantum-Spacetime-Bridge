#!/usr/bin/env python3
"""
BMS-FU02c — Representation-Resolved Carrier Delta Extension

Recomputes edge-level carrier deltas separately for each FU01c representation.

Scope:
  v0 reconstructs deterministic non-shell envelope selections:
    maximum_spanning_tree, mutual_knn, threshold, top_strength

  graph_distance_shells contexts are skipped by default. This avoids hidden
  shell-anchor assumptions.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

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


def parse_bool(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


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


def rank_desc(rows: List[Dict[str, Any]], score_name: str, rank_name: str) -> None:
    ordered = sorted(rows, key=lambda r: (-as_float(r.get(score_name, 0.0)), str(r.get("edge_key", ""))))
    for i, r in enumerate(ordered, start=1):
        r[rank_name] = i


def group_edge_rows(fu_edges: List[Dict[str, str]]) -> Dict[Tuple[str, str, str, str], List[Dict[str, str]]]:
    grouped: Dict[Tuple[str, str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for r in fu_edges:
        key = (r["representation_id"], r["core_variant_id"], r["object_id"], r["null_family"])
        grouped[key].append(r)
    return grouped


def object_index(fu_edges: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = {}
    for r in fu_edges:
        key = (r["representation_id"], r["core_variant_id"], r["object_id"], r["null_family"], r.get("repeat_index", ""))
        seen[key] = {
            "representation_id": r["representation_id"],
            "core_variant_id": r["core_variant_id"],
            "object_id": r["object_id"],
            "null_family": r["null_family"],
            "repeat_index": r.get("repeat_index", ""),
        }
    return list(seen.values())


def selected_edges(rows_by_object, obj_key, construction_family, construction_variant, bond_edge_keys: Set[str]) -> Set[Edge]:
    rows = rows_by_object.get(obj_key, [])
    if not rows:
        return set()

    def weight(row):
        return as_float(row.get("weight", ""), 0.0)

    def keep(row):
        return parse_bool(row.get("is_bond_edge", "true")) and edge_key_str(edge_key(row["source"], row["target"])) in bond_edge_keys

    if construction_family == "top_strength":
        n = int(str(construction_variant).split("_")[-1])
        chosen = sorted(rows, key=lambda r: (abs(weight(r)), edge_key(r["source"], r["target"])), reverse=True)[:n]
        return {edge_key(r["source"], r["target"]) for r in chosen if keep(r)}

    if construction_family == "threshold":
        t = float(str(construction_variant).split("_")[-1])
        return {edge_key(r["source"], r["target"]) for r in rows if abs(weight(r)) >= t and keep(r)}

    if construction_family == "mutual_knn":
        k = int(str(construction_variant).split("_")[-1])
        nodes = sorted({r["source"] for r in rows} | {r["target"] for r in rows})
        neigh = {n: [] for n in nodes}
        row_map = {}
        for r in rows:
            e = edge_key(r["source"], r["target"])
            row_map[e] = r
            neigh[e[0]].append((e[1], weight(r)))
            neigh[e[1]].append((e[0], weight(r)))
        topn = {}
        for n, vals in neigh.items():
            topn[n] = {x for x, _ in sorted(vals, key=lambda t: (abs(t[1]), t[0]), reverse=True)[:k]}
        return {e for e, r in row_map.items() if e[1] in topn.get(e[0], set()) and e[0] in topn.get(e[1], set()) and keep(r)}

    if construction_family == "maximum_spanning_tree":
        nodes = sorted({r["source"] for r in rows} | {r["target"] for r in rows})
        parent = {n: n for n in nodes}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            parent[rb] = ra
            return True

        selected = set()
        for r in sorted(rows, key=lambda rr: (abs(weight(rr)), edge_key(rr["source"], rr["target"])), reverse=True):
            e = edge_key(r["source"], r["target"])
            if union(e[0], e[1]) and keep(r):
                selected.add(e)
        return selected

    return set()


def compute_deltas(cfg, fu_summary, fu_edges, c60_edges, warnings):
    include = set(cfg["selection"]["include_construction_families"])
    reconstruct_shells = bool(cfg["selection"].get("reconstruct_graph_distance_shells", False))
    bond_edge_keys = {edge_key_str(edge_key(r["source"], r["target"])) for r in c60_edges}
    edge_meta = {edge_key_str(edge_key(r["source"], r["target"])): r for r in c60_edges}
    rows_by_object = group_edge_rows(fu_edges)

    objects = object_index(fu_edges)
    obj_by_rcn = defaultdict(list)
    for o in objects:
        obj_by_rcn[(o["representation_id"], o["core_variant_id"], o["null_family"])].append(o)

    context_rows = []
    skipped_shell = 0
    used_contexts = 0

    for s in fu_summary:
        if s.get("metric_name") != "envelope_core_edge_containment":
            continue
        rep = s.get("representation_id", "")
        core = s.get("core_variant_id", "")
        nfam = s.get("null_family", "")
        cfam = s.get("construction_family", "")
        cvar = s.get("construction_variant", "")

        if cfam not in include:
            continue
        if cfam == "graph_distance_shells":
            if not reconstruct_shells:
                skipped_shell += 1
                continue
            skipped_shell += 1
            continue

        real_key = (rep, core, f"{core}__real", "real")
        real_sel = selected_edges(rows_by_object, real_key, cfam, cvar, bond_edge_keys)

        null_sets = []
        for o in obj_by_rcn.get((rep, core, nfam), []):
            nkey = (rep, core, o["object_id"], nfam)
            null_sets.append(selected_edges(rows_by_object, nkey, cfam, cvar, bond_edge_keys))

        if not null_sets:
            continue
        used_contexts += 1
        n_null = len(null_sets)

        for edge_s in sorted(bond_edge_keys):
            e = parse_edge_key(edge_s)
            real_hit = 1 if e in real_sel else 0
            null_rate = sum(1 for ns in null_sets if e in ns) / n_null
            meta = edge_meta[edge_s]
            context_rows.append({
                "representation_id": rep,
                "core_variant_id": core,
                "construction_family": cfam,
                "construction_variant": cvar,
                "null_family": nfam,
                "edge_key": edge_s,
                "source": e[0],
                "target": e[1],
                "edge_type": meta.get("edge_type", ""),
                "shared_face_types": meta.get("shared_face_types", ""),
                "real_hit": real_hit,
                "null_hit_rate": null_rate,
                "delta_edge": real_hit - null_rate,
                "null_object_count": n_null,
            })

    if skipped_shell:
        warnings.append({"severity": "info", "message": f"FU02c-v0 skipped {skipped_shell} graph_distance_shells contexts; shell reconstruction is not enabled."})
    warnings.append({"severity": "info", "message": f"FU02c-v0 used {used_contexts} non-shell representation-resolved contexts."})

    by = defaultdict(list)
    for r in context_rows:
        by[(r["representation_id"], r["edge_key"], r["null_family"])].append(r)

    rep_edge_null_rows = []
    for (rep, edge_s, nfam), vals in sorted(by.items()):
        meta = edge_meta[edge_s]
        rep_edge_null_rows.append({
            "representation_id": rep,
            "edge_key": edge_s,
            "source": edge_s.split("--")[0],
            "target": edge_s.split("--")[1],
            "edge_type": meta.get("edge_type", ""),
            "shared_face_types": meta.get("shared_face_types", ""),
            "null_family": nfam,
            "mean_delta": sum(as_float(v["delta_edge"]) for v in vals)/len(vals),
            "mean_real_hit_rate": sum(as_float(v["real_hit"]) for v in vals)/len(vals),
            "mean_null_hit_rate": sum(as_float(v["null_hit_rate"]) for v in vals)/len(vals),
            "context_count": len(vals),
        })

    return context_rows, rep_edge_null_rows


def summarize(rep_edge_null_rows, reps):
    by = defaultdict(list)
    for r in rep_edge_null_rows:
        by[(r["representation_id"], r["edge_key"])].append(r)
    rows = []
    for (rep, edge_s), vals in sorted(by.items()):
        mean_delta = sum(as_float(v["mean_delta"]) for v in vals)/len(vals)
        min_delta = min(as_float(v["mean_delta"]) for v in vals)
        max_delta = max(as_float(v["mean_delta"]) for v in vals)
        meta = vals[0]
        rows.append({
            "representation_id": rep,
            "edge_key": edge_s,
            "source": meta["source"],
            "target": meta["target"],
            "edge_type": meta["edge_type"],
            "shared_face_types": meta["shared_face_types"],
            "mean_delta_all_nulls": mean_delta,
            "min_delta_across_nulls": min_delta,
            "max_delta_across_nulls": max_delta,
            "positive_null_family_count": sum(1 for v in vals if as_float(v["mean_delta"]) > 0),
            "null_family_count": len(vals),
            "decoy_penalized_positive": min_delta > 0,
        })
    for rep in reps:
        subset = [r for r in rows if r["representation_id"] == rep]
        rank_desc(subset, "mean_delta_all_nulls", "rank_mean_delta")
        rank_desc(subset, "min_delta_across_nulls", "rank_decoy_penalized_delta")
    return rows


def motif_enrichment(summary, reps, topks):
    out = []
    base_hh, base_hp = 30/90, 60/90
    for rep in reps:
        rep_rows = [r for r in summary if r["representation_id"] == rep]
        for score, rank in [("mean_delta_all_nulls", "rank_mean_delta"), ("min_delta_across_nulls", "rank_decoy_penalized_delta")]:
            for k in topks:
                sel = sorted([r for r in rep_rows if as_int(r.get(rank, 9999)) <= k], key=lambda r: as_int(r.get(rank, 9999)))
                hh = sum(1 for r in sel if r["shared_face_types"] == "H,H")
                hp = sum(1 for r in sel if r["shared_face_types"] == "H,P")
                n = len(sel)
                hhf = hh/n if n else 0
                hpf = hp/n if n else 0
                out.append({
                    "representation_id": rep,
                    "score_name": score,
                    "topk_label": f"top_{k}",
                    "k": k,
                    "edge_count": n,
                    "hh_count": hh,
                    "hp_count": hp,
                    "hh_fraction": hhf,
                    "hp_fraction": hpf,
                    "hh_enrichment_ratio": hhf/base_hh if base_hh else 0,
                    "hp_enrichment_ratio": hpf/base_hp if base_hp else 0,
                    "top_edges": ";".join(r["edge_key"] for r in sel[:20]),
                })
    return out


def consensus(summary, reps):
    by = defaultdict(list)
    for r in summary:
        by[r["edge_key"]].append(r)
    out = []
    for edge_s, vals in sorted(by.items()):
        meta = vals[0]
        top10 = [v["representation_id"] for v in vals if as_int(v.get("rank_mean_delta", 9999)) <= 10]
        top20 = [v["representation_id"] for v in vals if as_int(v.get("rank_mean_delta", 9999)) <= 20]
        top30 = [v["representation_id"] for v in vals if as_int(v.get("rank_mean_delta", 9999)) <= 30]
        pos = [v["representation_id"] for v in vals if as_float(v["mean_delta_all_nulls"]) > 0]
        decoy_pos = [v["representation_id"] for v in vals if v.get("decoy_penalized_positive") is True]
        mean_all = sum(as_float(v["mean_delta_all_nulls"]) for v in vals)/len(vals)
        min_all = min(as_float(v["min_delta_across_nulls"]) for v in vals)
        if meta["shared_face_types"] == "H,H" and len(top30) == len(reps):
            label = "hh_consensus_all_representations"
        elif meta["shared_face_types"] == "H,H" and len(top30) >= 2:
            label = "hh_consensus_two_representations"
        elif meta["shared_face_types"] == "H,P" and len(top30) >= 2:
            label = "hp_secondary_carrier"
        elif len(top30) == 1:
            label = "representation_specific_candidate"
        else:
            label = "decoy_reproduced_or_unstable"
        out.append({
            "edge_key": edge_s,
            "source": meta["source"],
            "target": meta["target"],
            "edge_type": meta["edge_type"],
            "shared_face_types": meta["shared_face_types"],
            "representations_present": ";".join(sorted(v["representation_id"] for v in vals)),
            "positive_representations": ";".join(sorted(pos)),
            "decoy_positive_representations": ";".join(sorted(decoy_pos)),
            "top10_representations": ";".join(sorted(top10)),
            "top20_representations": ";".join(sorted(top20)),
            "top30_representations": ";".join(sorted(top30)),
            "top30_representation_count": len(top30),
            "mean_delta_across_representations": mean_all,
            "min_decoy_delta_across_representations": min_all,
            "consensus_label": label,
        })
    out.sort(key=lambda r: (-as_int(r["top30_representation_count"]), -as_float(r["mean_delta_across_representations"]), r["edge_key"]))
    return out


def rank_matrix(summary, reps):
    by = defaultdict(dict)
    meta = {}
    for r in summary:
        by[r["edge_key"]][r["representation_id"]] = r
        meta[r["edge_key"]] = r
    rows = []
    for edge_s, rv in sorted(by.items()):
        row = {"edge_key": edge_s, "edge_type": meta[edge_s]["edge_type"], "shared_face_types": meta[edge_s]["shared_face_types"]}
        ranks = []
        for rep in reps:
            r = rv.get(rep, {})
            row[f"{rep}_rank_mean_delta"] = as_int(r.get("rank_mean_delta", 9999), 9999)
            row[f"{rep}_rank_decoy_penalized_delta"] = as_int(r.get("rank_decoy_penalized_delta", 9999), 9999)
            row[f"{rep}_mean_delta"] = as_float(r.get("mean_delta_all_nulls", 0), 0)
            row[f"{rep}_min_delta"] = as_float(r.get("min_delta_across_nulls", 0), 0)
            ranks.append(row[f"{rep}_rank_mean_delta"])
        row["best_representation_rank"] = min(ranks)
        row["worst_representation_rank"] = max(ranks)
        row["top10_representation_count"] = sum(1 for x in ranks if x <= 10)
        row["top20_representation_count"] = sum(1 for x in ranks if x <= 20)
        row["top30_representation_count"] = sum(1 for x in ranks if x <= 30)
        rows.append(row)
    rows.sort(key=lambda r: (-as_int(r["top30_representation_count"]), as_int(r["best_representation_rank"]), r["edge_key"]))
    return rows


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)
    warnings = []

    fu_dir = root / cfg["inputs"]["fu01c_output_dir"]
    fu_manifest = read_json(fu_dir / "bms_fu01c_run_manifest.json")
    fu_warn_path = fu_dir / "bms_fu01c_warnings.json"
    fu_warn = read_json(fu_warn_path) if fu_warn_path.exists() else []
    if fu_warn:
        warnings.append({"severity": "warning", "message": f"FU01c warnings carried forward: {len(fu_warn)}"})

    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])
    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 graph manifest does not report c60_valid=true."})

    fu_summary = read_csv(fu_dir / "bms_fu01c_real_vs_null_summary.csv")
    fu_edges = read_csv(fu_dir / "bms_fu01c_edges.csv")
    c60_edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    reps = cfg["representations"]["expected"]

    context_rows, rep_edge_null_rows = compute_deltas(cfg, fu_summary, fu_edges, c60_edges, warnings)
    summary_rows = summarize(rep_edge_null_rows, reps)
    motif_rows = motif_enrichment(summary_rows, reps, [int(k) for k in cfg["selection"]["topk_values"]])
    consensus_rows = consensus(summary_rows, reps)
    rank_rows = rank_matrix(summary_rows, reps)

    out = cfg["outputs"]
    context_fields = ["representation_id","core_variant_id","construction_family","construction_variant","null_family","edge_key","source","target","edge_type","shared_face_types","real_hit","null_hit_rate","delta_edge","null_object_count"]
    summary_fields = ["representation_id","edge_key","source","target","edge_type","shared_face_types","mean_delta_all_nulls","min_delta_across_nulls","max_delta_across_nulls","positive_null_family_count","null_family_count","decoy_penalized_positive","rank_mean_delta","rank_decoy_penalized_delta"]
    motif_fields = ["representation_id","score_name","topk_label","k","edge_count","hh_count","hp_count","hh_fraction","hp_fraction","hh_enrichment_ratio","hp_enrichment_ratio","top_edges"]
    consensus_fields = ["edge_key","source","target","edge_type","shared_face_types","representations_present","positive_representations","decoy_positive_representations","top10_representations","top20_representations","top30_representations","top30_representation_count","mean_delta_across_representations","min_decoy_delta_across_representations","consensus_label"]
    rank_fields = sorted({k for r in rank_rows for k in r.keys()})
    rank_fields = ["edge_key","edge_type","shared_face_types"] + [f for f in rank_fields if f not in {"edge_key","edge_type","shared_face_types"}]

    write_csv(outdir / out["representation_edge_deltas_csv"], context_rows, context_fields)
    write_csv(outdir / out["edge_representation_summary_csv"], summary_rows, summary_fields)
    write_csv(outdir / out["representation_motif_enrichment_csv"], motif_rows, motif_fields)
    write_csv(outdir / out["consensus_carriers_csv"], consensus_rows, consensus_fields)
    write_csv(outdir / out["representation_rank_matrix_csv"], rank_rows, rank_fields)

    labels = Counter(r["consensus_label"] for r in consensus_rows)
    top30_by_rep = {}
    for rep in reps:
        rows = [r for r in summary_rows if r["representation_id"] == rep and as_int(r.get("rank_mean_delta", 9999)) <= 30]
        top30_by_rep[rep] = dict(Counter(r["shared_face_types"] for r in rows))

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "fu01c_run_id": fu_manifest.get("run_id", ""),
        "fu01c_warning_count": len(fu_warn),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "representations": reps,
        "context_delta_row_count": len(context_rows),
        "edge_representation_summary_row_count": len(summary_rows),
        "consensus_carrier_count": len(consensus_rows),
        "consensus_label_counts": dict(sorted(labels.items())),
        "top30_mean_delta_motif_counts_by_representation": top30_by_rep,
        "row_counts": {
            "representation_edge_deltas": len(context_rows),
            "edge_representation_summary": len(summary_rows),
            "representation_motif_enrichment": len(motif_rows),
            "consensus_carriers": len(consensus_rows),
            "representation_rank_matrix": len(rank_rows),
            "warnings": len(warnings),
        },
        "scope_note": "FU02c-v0 computes representation-resolved non-shell carrier deltas; graph_distance_shells contexts are skipped unless explicitly implemented.",
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
    parser = argparse.ArgumentParser(description="Run BMS-FU02c representation-resolved carrier delta extension.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
