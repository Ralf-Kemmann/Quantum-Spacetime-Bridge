#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Tuple

CandidateStatus = Literal["materially_active", "weak_ambiguous", "collapsed"]

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

def get_local_context(units: Dict[str, AdaptedUnit], focal_unit_id: str) -> Tuple[AdaptedUnit, List[AdaptedUnit]]:
    focal = units[focal_unit_id]
    neighborhood = [units[nid] for nid in focal.adjacent_ids if nid in units]
    return focal, neighborhood

def compute_a1(focal: AdaptedUnit, neighborhood: List[AdaptedUnit], params: Dict[str, Any]) -> Dict[str, Any]:
    lam = float(params.get("a1_lambda", 1.0))
    active_threshold = float(params.get("a1_active_threshold", 0.20))
    overlap_margin = float(params.get("a1_overlap_margin", 0.08))
    stabilization_ceiling = float(params.get("a1_stabilization_ceiling", 0.85))
    neighbor_min = int(params.get("a1_neighbor_min", 3))

    total_neighbor_abs = sum(abs(u.support_value) for u in neighborhood)
    same_sector = sum(abs(u.support_value) for u in neighborhood if u.support_sector == focal.support_sector)
    opposite_sector = sum(abs(u.support_value) for u in neighborhood if u.support_sector != focal.support_sector)

    agreement = same_sector / total_neighbor_abs if total_neighbor_abs else 0.0
    conflict = opposite_sector / total_neighbor_abs if total_neighbor_abs else 0.0
    score = agreement - lam * conflict
    neighbor_count = len(neighborhood)

    denom = abs(focal.support_value) + total_neighbor_abs
    focal_overlap_proxy = abs(focal.support_value) / denom if denom > 0 else 0.0
    anti_overlap_delta = abs(score - focal_overlap_proxy)

    if score >= active_threshold:
        internal_activity = "active"
    elif score > 0.0:
        internal_activity = "weak"
    else:
        internal_activity = "unclear"

    anti_overlap = "passes" if anti_overlap_delta >= overlap_margin else "borderline"
    late_stage = (score >= stabilization_ceiling) and (neighbor_count >= neighbor_min)
    anti_stabilization = "fails" if late_stage else "passes"

    if internal_activity == "active" and anti_overlap == "passes" and anti_stabilization == "passes":
        derived_status: CandidateStatus = "materially_active"
    elif anti_stabilization == "fails":
        derived_status = "collapsed"
    else:
        derived_status = "weak_ambiguous"

    return {
        "agreement_local": agreement,
        "conflict_local": conflict,
        "a1_score": score,
        "neighbor_count": neighbor_count,
        "anti_overlap_delta": anti_overlap_delta,
        "internal_activity": internal_activity,
        "anti_overlap": anti_overlap,
        "anti_stabilization": anti_stabilization,
        "derived_status": derived_status,
    }

def apply_perturbation(value: float, mode: str, strength: float) -> float:
    if mode == "scale_down":
        return value * strength
    if mode == "zero_out":
        return 0.0
    raise SystemExit(f"Unsupported perturbation mode: {mode!r}")

def support_proxy(focal_value: float, focal_sector: int, neighborhood: List[AdaptedUnit], conflict_penalty: float) -> float:
    same_sector = sum(abs(u.support_value) for u in neighborhood if u.support_sector == focal_sector)
    opposite_sector = sum(abs(u.support_value) for u in neighborhood if u.support_sector != focal_sector)
    return max(abs(focal_value) + same_sector - conflict_penalty * opposite_sector, 0.0)

def compute_b1(focal: AdaptedUnit, neighborhood: List[AdaptedUnit], params: Dict[str, Any], perturbation_mapping: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(perturbation_mapping.get("mode", "scale_down"))
    strength = float(perturbation_mapping.get("strength", 0.5))
    active_threshold = float(params.get("b1_active_threshold", 0.12))
    overlap_margin = float(params.get("b1_overlap_margin", 0.05))
    conflict_penalty = float(params.get("b1_conflict_penalty", 1.0))
    stabilization_ceiling = float(params.get("b1_stabilization_ceiling", 0.70))

    baseline_support = support_proxy(focal.support_value, focal.support_sector, neighborhood, conflict_penalty)
    perturbed_support = support_proxy(apply_perturbation(focal.support_value, mode, strength), focal.support_sector, neighborhood, conflict_penalty)
    fragility = baseline_support - perturbed_support
    relative_fragility = fragility / baseline_support if baseline_support > 0 else 0.0

    denom = abs(focal.support_value) + sum(abs(u.support_value) for u in neighborhood)
    focal_overlap_proxy = abs(focal.support_value) / denom if denom > 0 else 0.0
    anti_overlap_delta = abs(relative_fragility - focal_overlap_proxy)

    if relative_fragility >= active_threshold:
        internal_activity = "active"
    elif relative_fragility > 0.0:
        internal_activity = "weak"
    else:
        internal_activity = "unclear"

    anti_overlap = "passes" if anti_overlap_delta >= overlap_margin else "borderline"
    anti_stabilization = "passes" if relative_fragility < stabilization_ceiling else "fails"

    if internal_activity == "active" and anti_overlap == "passes" and anti_stabilization == "passes":
        derived_status: CandidateStatus = "materially_active"
    elif anti_stabilization == "fails":
        derived_status = "collapsed"
    else:
        derived_status = "weak_ambiguous"

    return {
        "baseline_support_local": baseline_support,
        "perturbed_support_local": perturbed_support,
        "relative_fragility": relative_fragility,
        "anti_overlap_delta": anti_overlap_delta,
        "internal_activity": internal_activity,
        "anti_overlap": anti_overlap,
        "anti_stabilization": anti_stabilization,
        "derived_status": derived_status,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Focal-unit sweep diagnostics with reformed A1 anti-stabilization.")
    parser.add_argument("--export", required=True)
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--params")
    args = parser.parse_args()

    export = load_json(Path(args.export))
    mapping_cfg = load_json(Path(args.mapping))
    params = load_json(Path(args.params)) if args.params else {
        "a1_lambda": 1.0,
        "a1_active_threshold": 0.20,
        "a1_overlap_margin": 0.08,
        "a1_stabilization_ceiling": 0.85,
        "a1_neighbor_min": 3,
        "b1_active_threshold": 0.12,
        "b1_overlap_margin": 0.05,
        "b1_conflict_penalty": 1.0,
        "b1_stabilization_ceiling": 0.70,
    }

    raw_units = read_path(export, mapping_cfg["unit_collection_path"])
    units = adapt_units(raw_units, mapping_cfg["unit_mapping"])
    idx = build_unit_index(units)

    rows: List[Dict[str, Any]] = []
    for focal_id in sorted(idx.keys()):
        focal, neighborhood = get_local_context(idx, focal_id)
        a1 = compute_a1(focal, neighborhood, params)
        b1 = compute_b1(focal, neighborhood, params, mapping_cfg["perturbation_mapping"])
        rows.append({
            "focal_unit_id": focal_id,
            "support_sector": focal.support_sector,
            "support_value": round(focal.support_value, 6),
            "neighbor_count": len(neighborhood),
            "neighbors": ",".join(u.unit_id for u in neighborhood),
            "a1_status": a1["derived_status"],
            "a1_score": round(a1["a1_score"], 6),
            "a1_agreement": round(a1["agreement_local"], 6),
            "a1_conflict": round(a1["conflict_local"], 6),
            "a1_anti_stabilization": a1["anti_stabilization"],
            "b1_status": b1["derived_status"],
            "b1_relative_fragility": round(b1["relative_fragility"], 6),
            "b1_baseline_support": round(b1["baseline_support_local"], 6),
            "b1_anti_stabilization": b1["anti_stabilization"],
        })

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    with (outdir / "focal_unit_sweep.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["focal_unit_id"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary = {
        "generated_at": now_iso(),
        "export_path": args.export,
        "mapping_path": args.mapping,
        "n_units": len(rows),
        "a1_status_counts": {
            status: sum(1 for r in rows if r["a1_status"] == status)
            for status in ["materially_active", "weak_ambiguous", "collapsed"]
        },
        "b1_status_counts": {
            status: sum(1 for r in rows if r["b1_status"] == status)
            for status in ["materially_active", "weak_ambiguous", "collapsed"]
        },
        "rows": rows,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote: {outdir / 'focal_unit_sweep.csv'}")
    print(f"Wrote: {outdir / 'summary.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
