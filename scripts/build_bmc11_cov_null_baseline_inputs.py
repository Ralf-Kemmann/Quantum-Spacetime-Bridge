#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import List, Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build BMC-11 baseline and node metadata from cov-null feature table for one seed.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def zscore(v: List[float]) -> List[float]:
    n = len(v)
    mu = sum(v) / n
    var = sum((x - mu) ** 2 for x in v) / n
    sd = math.sqrt(var) if var > 0 else 1.0
    return [(x - mu) / sd for x in v]


def main() -> None:
    args = parse_args()
    rows = [r for r in read_rows(Path(args.input)) if r.get("nullmodel_seed") == str(args.seed)]
    if not rows:
        raise SystemExit(f"No rows found for seed {args.seed}")

    f1 = [float(r["feature_mode_frequency"]) for r in rows]
    f2 = [float(r["feature_length_scale"]) for r in rows]
    f3 = [max(float(r["L_major_raw"]), float(r["L_minor_raw"])) / min(float(r["L_major_raw"]), float(r["L_minor_raw"])) for r in rows]
    f4 = [float(r["m_ref_raw"]) for r in rows]
    z1, z2, z3, z4 = map(zscore, [f1, f2, f3, f4])

    node_ids = [r["node_id"] for r in rows]
    fams = {r["node_id"]: r["node_family"] for r in rows}
    labels = {r["node_id"]: r["node_label"] for r in rows}
    origins = {r["node_id"]: r["origin_tag"] for r in rows}
    comments = {r["node_id"]: r["comment"] for r in rows}

    edge_rows = []
    for i, a in enumerate(node_ids):
        for j in range(i + 1, len(node_ids)):
            b = node_ids[j]
            d = math.sqrt((z1[i]-z1[j])**2 + (z2[i]-z2[j])**2 + (z3[i]-z3[j])**2 + (z4[i]-z4[j])**2)
            w = 1.0 / (1.0 + d)
            edge_rows.append({
                "source": a,
                "target": b,
                "weight": f"{w:.12g}",
                "edge_family": "intra_family" if fams[a] == fams[b] else "cross_family",
                "relation_type": "cov_null_euclidean_similarity",
                "source_family": fams[a],
                "target_family": fams[b],
                "evidence_tag": f"bmc11_cov_null_seed_{args.seed}",
                "comment": "Covariance-preserving nullmodel full similarity graph",
            })

    shell_map = {"RING": "0", "CAVITY": "1", "MEMBRANE": "2"}
    node_rows = []
    for r in rows:
        lmaj = float(r["L_major_raw"])
        lmin = float(r["L_minor_raw"])
        node_rows.append({
            "node_id": r["node_id"],
            "shell_index": shell_map[r["node_family"]],
            "node_label": labels[r["node_id"]],
            "node_family": r["node_family"],
            "origin_tag": origins[r["node_id"]],
            "comment": comments[r["node_id"]],
            "feature_shape_factor": f"{max(lmaj, lmin)/min(lmaj, lmin):.12g}",
            "feature_spectral_index": f"{float(r['m_ref_raw']):.12g}",
        })

    outdir = Path(args.output_dir)
    write_csv(
        outdir / f"bmc11_baseline_relational_table_seed_{args.seed}.csv",
        edge_rows,
        ["source","target","weight","edge_family","relation_type","source_family","target_family","evidence_tag","comment"]
    )
    write_csv(
        outdir / f"bmc11_node_metadata_seed_{args.seed}.csv",
        node_rows,
        ["node_id","shell_index","node_label","node_family","origin_tag","comment","feature_shape_factor","feature_spectral_index"]
    )

    print(f"Wrote: {outdir / f'bmc11_baseline_relational_table_seed_{args.seed}.csv'}")
    print(f"Wrote: {outdir / f'bmc11_node_metadata_seed_{args.seed}.csv'}")


if __name__ == "__main__":
    main()
