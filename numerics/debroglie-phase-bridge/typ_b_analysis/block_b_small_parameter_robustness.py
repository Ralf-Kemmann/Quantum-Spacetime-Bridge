#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal

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
    return [
        AdaptedUnit(
            unit_id=str(read_path(raw, mapping["id_field"])),
            support_value=float(read_path(raw, mapping["support_value_field"])),
            support_sector=int(read_path(raw, mapping["support_sector_field"])),
            adjacent_ids=[str(x) for x in list(read_path(raw, mapping["adjacent_ids_field"]))],
        )
        for raw in raw_units
    ]

def build_unit_index(units: List[AdaptedUnit]) -> Dict[str, AdaptedUnit]:
    return {u.unit_id: u for u in units}

def get_local_context(units: Dict[str, AdaptedUnit], focal_unit_id: str):
    focal = units[focal_unit_id]
    neighborhood = [units[nid] for nid in focal.adjacent_ids if nid in units]
    return focal, neighborhood

def compute_a1(focal: AdaptedUnit, neighborhood: List[AdaptedUnit], params: Dict[str, Any]) -> Dict[str, Any]:
    lam = float(params["a1_lambda"])
    active_threshold = float(params["a1_active_threshold"])
    overlap_margin = float(params["a1_overlap_margin"])
    stabilization_ceiling = float(params["a1_stabilization_ceiling"])
    neighbor_min = int(params["a1_neighbor_min"])
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
        status: CandidateStatus = "materially_active"
    elif anti_stabilization == "fails":
        status = "collapsed"
    else:
        status = "weak_ambiguous"
    return {
        "status": status,
        "score": score,
        "neighbor_count": neighbor_count,
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
    active_threshold = float(params["b1_active_threshold"])
    overlap_margin = float(params["b1_overlap_margin"])
    conflict_penalty = float(params["b1_conflict_penalty"])
    stabilization_ceiling = float(params["b1_stabilization_ceiling"])
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
        status: CandidateStatus = "materially_active"
    elif anti_stabilization == "fails":
        status = "collapsed"
    else:
        status = "weak_ambiguous"
    return {
        "status": status,
        "relative_fragility": relative_fragility,
    }

def derive_outcome(a1: str, b1: str) -> str:
    active = sum(1 for s in [a1, b1] if s == "materially_active")
    weak = sum(1 for s in [a1, b1] if s == "weak_ambiguous")
    if active >= 1:
        return "Outcome C"
    if weak >= 1:
        return "Outcome B"
    return "Outcome A"

def derive_promotion(a1: str, b1: str) -> str:
    if a1 == "materially_active" and b1 == "materially_active":
        return "A1_and_B1"
    if a1 == "materially_active":
        return "A1"
    if b1 == "materially_active":
        return "B1"
    if a1 == "weak_ambiguous":
        return "A1_deferred"
    if b1 == "weak_ambiguous":
        return "B1_deferred"
    return "none"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", required=True)
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--ceilings", nargs="*", type=float, default=[0.85, 0.95])
    parser.add_argument("--neighbor-mins", nargs="*", type=int, default=[3, 4])
    parser.add_argument("--b1-penalties", nargs="*", type=float, default=[1.0, 1.25])
    args = parser.parse_args()

    export = load_json(Path(args.export))
    mapping_cfg = load_json(Path(args.mapping))
    raw_units = read_path(export, mapping_cfg["unit_collection_path"])
    units = adapt_units(raw_units, mapping_cfg["unit_mapping"])
    idx = build_unit_index(units)

    params_base = {
        "a1_lambda": 1.0,
        "a1_active_threshold": 0.20,
        "a1_overlap_margin": 0.08,
        "b1_active_threshold": 0.12,
        "b1_overlap_margin": 0.05,
        "b1_stabilization_ceiling": 0.70,
    }

    focal_rows = []
    combo_rows = []

    for ceiling in args.ceilings:
        for neighbor_min in args.neighbor_mins:
            for penalty in args.b1_penalties:
                a1_statuses, b1_statuses, outcomes, promotions = [], [], [], []
                for focal_id in sorted(idx.keys()):
                    focal, neighborhood = get_local_context(idx, focal_id)
                    params = dict(params_base)
                    params["a1_stabilization_ceiling"] = ceiling
                    params["a1_neighbor_min"] = neighbor_min
                    params["b1_conflict_penalty"] = penalty
                    a1 = compute_a1(focal, neighborhood, params)
                    b1 = compute_b1(focal, neighborhood, params, mapping_cfg["perturbation_mapping"])
                    outcome = derive_outcome(a1["status"], b1["status"])
                    promotion = derive_promotion(a1["status"], b1["status"])
                    a1_statuses.append(a1["status"])
                    b1_statuses.append(b1["status"])
                    outcomes.append(outcome)
                    promotions.append(promotion)
                    focal_rows.append({
                        "export_label": args.label,
                        "ceiling": ceiling,
                        "neighbor_min": neighbor_min,
                        "b1_conflict_penalty": penalty,
                        "focal_unit_id": focal_id,
                        "a1_status": a1["status"],
                        "a1_score": round(a1["score"], 6),
                        "a1_neighbor_count": a1["neighbor_count"],
                        "b1_status": b1["status"],
                        "b1_relative_fragility": round(b1["relative_fragility"], 6),
                        "outcome": outcome,
                        "promotion": promotion,
                    })
                combo_rows.append({
                    "export_label": args.label,
                    "ceiling": ceiling,
                    "neighbor_min": neighbor_min,
                    "b1_conflict_penalty": penalty,
                    "n_focals": len(idx),
                    "a1_active_count": sum(1 for s in a1_statuses if s == "materially_active"),
                    "a1_weak_count": sum(1 for s in a1_statuses if s == "weak_ambiguous"),
                    "a1_collapsed_count": sum(1 for s in a1_statuses if s == "collapsed"),
                    "b1_active_count": sum(1 for s in b1_statuses if s == "materially_active"),
                    "b1_weak_count": sum(1 for s in b1_statuses if s == "weak_ambiguous"),
                    "b1_collapsed_count": sum(1 for s in b1_statuses if s == "collapsed"),
                    "outcome_C_count": sum(1 for o in outcomes if o == "Outcome C"),
                    "promotion_A1_and_B1_count": sum(1 for p in promotions if p == "A1_and_B1"),
                    "promotion_A1_count": sum(1 for p in promotions if p == "A1"),
                    "promotion_B1_count": sum(1 for p in promotions if p == "B1"),
                })

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "block_b_focal_rows.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(focal_rows[0].keys()))
        writer.writeheader()
        writer.writerows(focal_rows)
    with (outdir / "block_b_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(combo_rows[0].keys()))
        writer.writeheader()
        writer.writerows(combo_rows)
    summary = {
        "generated_at": now_iso(),
        "export_label": args.label,
        "export_path": args.export,
        "mapping_path": args.mapping,
        "tested_ceilings": args.ceilings,
        "tested_neighbor_mins": args.neighbor_mins,
        "tested_b1_penalties": args.b1_penalties,
        "n_focals": len(idx),
        "per_combination": combo_rows,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote: {outdir / 'block_b_focal_rows.csv'}")
    print(f"Wrote: {outdir / 'block_b_summary.csv'}")
    print(f"Wrote: {outdir / 'summary.json'}")

if __name__ == "__main__":
    main()
