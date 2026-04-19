#!/usr/bin/env python3
"""
A1 stabilization-ceiling sweep diagnostics for one local export.

This script keeps the current export, mapping, and first-pass proxy logic fixed,
but sweeps the A1 stabilization ceiling over a user-specified grid.

Usage:
    python a1_stabilization_ceiling_sweep.py \
      --export ./real_local_export_from_npz_negative.json \
      --mapping ./compatibility_local_model_mapping_npz_negative_v1.json \
      --outdir ./results_a1_ceiling_sweep_negative

Optional:
    --ceilings 0.85 0.90 0.95 0.99 1.01
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List


@dataclass
class AdaptedUnit:
    unit_id: str
    support_value: float
    support_sector: int
    adjacent_ids: List[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_path(obj: Dict[str, Any], dotted_path: str) -> Any:
    cur: Any = obj
    for part in dotted_path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise SystemExit(f"Missing path '{dotted_path}' at segment '{part}'")
        cur = cur[part]
    return cur


def adapt_units(raw_units: Iterable[Dict[str, Any]], mapping: Dict[str, str]) -> List[AdaptedUnit]:
    out: List[AdaptedUnit] = []
    for raw in raw_units:
        out.append(
            AdaptedUnit(
                unit_id=str(read_path(raw, mapping["id_field"])),
                support_value=float(read_path(raw, mapping["support_value_field"])),
                support_sector=int(read_path(raw, mapping["support_sector_field"])),
                adjacent_ids=[str(x) for x in list(read_path(raw, mapping["adjacent_ids_field"]))],
            )
        )
    return out


def build_unit_index(units: List[AdaptedUnit]) -> Dict[str, AdaptedUnit]:
    return {u.unit_id: u for u in units}


def get_local_context(units: Dict[str, AdaptedUnit], focal_unit_id: str):
    focal = units[focal_unit_id]
    neighborhood = [units[nid] for nid in focal.adjacent_ids if nid in units]
    return focal, neighborhood


def compute_a1(focal: AdaptedUnit, neighborhood: List[AdaptedUnit], lam: float, active_threshold: float, overlap_margin: float, stabilization_ceiling: float) -> Dict[str, Any]:
    total_neighbor_abs = sum(abs(u.support_value) for u in neighborhood)
    same_sector = sum(abs(u.support_value) for u in neighborhood if u.support_sector == focal.support_sector)
    opposite_sector = sum(abs(u.support_value) for u in neighborhood if u.support_sector != focal.support_sector)

    agreement = same_sector / total_neighbor_abs if total_neighbor_abs else 0.0
    conflict = opposite_sector / total_neighbor_abs if total_neighbor_abs else 0.0
    score = agreement - lam * conflict

    focal_overlap_proxy = abs(focal.support_value) / (abs(focal.support_value) + total_neighbor_abs) if (abs(focal.support_value) + total_neighbor_abs) > 0 else 0.0
    anti_overlap_delta = abs(score - focal_overlap_proxy)

    if score >= active_threshold:
        internal_activity = "active"
    elif score > 0.0:
        internal_activity = "weak"
    else:
        internal_activity = "unclear"

    anti_overlap = "passes" if anti_overlap_delta >= overlap_margin else "borderline"
    anti_stabilization = "passes" if score < stabilization_ceiling else "fails"

    if internal_activity == "active" and anti_overlap == "passes" and anti_stabilization == "passes":
        derived_status = "materially_active"
    elif anti_stabilization == "fails":
        derived_status = "collapsed"
    else:
        derived_status = "weak_ambiguous"

    return {
        "agreement_local": agreement,
        "conflict_local": conflict,
        "a1_score": score,
        "anti_overlap_delta": anti_overlap_delta,
        "internal_activity": internal_activity,
        "anti_overlap": anti_overlap,
        "anti_stabilization": anti_stabilization,
        "derived_status": derived_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="A1 stabilization-ceiling sweep diagnostics.")
    parser.add_argument("--export", required=True, help="Path to local export JSON.")
    parser.add_argument("--mapping", required=True, help="Path to mapping JSON.")
    parser.add_argument("--outdir", required=True, help="Output directory.")
    parser.add_argument("--ceilings", nargs="*", type=float, default=[0.85, 0.90, 0.95, 0.99, 1.01], help="Ceiling values to test.")
    parser.add_argument("--a1-lambda", type=float, default=1.0)
    parser.add_argument("--a1-active-threshold", type=float, default=0.20)
    parser.add_argument("--a1-overlap-margin", type=float, default=0.08)
    args = parser.parse_args()

    export = load_json(Path(args.export))
    mapping_cfg = load_json(Path(args.mapping))

    raw_units = read_path(export, mapping_cfg["unit_collection_path"])
    units = adapt_units(raw_units, mapping_cfg["unit_mapping"])
    idx = build_unit_index(units)

    per_focal_rows: List[Dict[str, Any]] = []
    per_ceiling_rows: List[Dict[str, Any]] = []

    for ceiling in args.ceilings:
        statuses = []
        anti_stab_passes = 0
        scores = []
        for focal_id in sorted(idx.keys()):
            focal, neighborhood = get_local_context(idx, focal_id)
            res = compute_a1(
                focal,
                neighborhood,
                lam=args.a1_lambda,
                active_threshold=args.a1_active_threshold,
                overlap_margin=args.a1_overlap_margin,
                stabilization_ceiling=ceiling,
            )
            statuses.append(res["derived_status"])
            scores.append(res["a1_score"])
            if res["anti_stabilization"] == "passes":
                anti_stab_passes += 1
            per_focal_rows.append({
                "ceiling": ceiling,
                "focal_unit_id": focal_id,
                "support_sector": focal.support_sector,
                "support_value": round(focal.support_value, 6),
                "neighbor_count": len(neighborhood),
                "neighbors": ",".join(u.unit_id for u in neighborhood),
                "a1_status": res["derived_status"],
                "a1_score": round(res["a1_score"], 6),
                "a1_agreement": round(res["agreement_local"], 6),
                "a1_conflict": round(res["conflict_local"], 6),
                "a1_anti_overlap": res["anti_overlap"],
                "a1_anti_stabilization": res["anti_stabilization"],
            })

        per_ceiling_rows.append({
            "ceiling": ceiling,
            "n_units": len(idx),
            "materially_active_count": sum(1 for s in statuses if s == "materially_active"),
            "weak_ambiguous_count": sum(1 for s in statuses if s == "weak_ambiguous"),
            "collapsed_count": sum(1 for s in statuses if s == "collapsed"),
            "anti_stabilization_pass_count": anti_stab_passes,
            "mean_a1_score": round(mean(scores), 6) if scores else None,
        })

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    focal_csv = outdir / "a1_ceiling_sweep_focal_rows.csv"
    with focal_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(per_focal_rows[0].keys()) if per_focal_rows else ["ceiling", "focal_unit_id"])
        writer.writeheader()
        for row in per_focal_rows:
            writer.writerow(row)

    ceiling_csv = outdir / "a1_ceiling_sweep_summary.csv"
    with ceiling_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(per_ceiling_rows[0].keys()) if per_ceiling_rows else ["ceiling"])
        writer.writeheader()
        for row in per_ceiling_rows:
            writer.writerow(row)

    summary = {
        "generated_at": now_iso(),
        "export_path": args.export,
        "mapping_path": args.mapping,
        "tested_ceilings": args.ceilings,
        "n_units": len(idx),
        "per_ceiling": per_ceiling_rows,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote: {focal_csv}")
    print(f"Wrote: {ceiling_csv}")
    print(f"Wrote: {outdir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
