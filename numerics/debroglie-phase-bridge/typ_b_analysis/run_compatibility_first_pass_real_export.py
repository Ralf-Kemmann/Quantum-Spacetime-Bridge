#!/usr/bin/env python3
"""
Compatibility first-pass computed runner bound to a real local export format.

Reformed A1 anti-stabilization rule:
    late_stage iff (a1_score >= a1_stabilization_ceiling) AND (neighbor_count >= a1_neighbor_min)

This runner:
- loads a project-local raw export JSON
- loads a mapping spec
- adapts raw local units into the first-pass proxy model
- computes A1 and B1
- writes run.json and summary.json
"""
from __future__ import annotations

import argparse
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
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"JSON file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}")


def require_fields(cfg: Dict[str, Any], fields: List[str], label: str = "object") -> None:
    missing = [field for field in fields if field not in cfg]
    if missing:
        raise SystemExit(f"Missing required field(s) in {label}: {', '.join(missing)}")


def read_path(obj: Dict[str, Any], dotted_path: str) -> Any:
    cur: Any = obj
    for part in dotted_path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise SystemExit(f"Missing path '{dotted_path}' at segment '{part}'")
        cur = cur[part]
    return cur


def adapt_units(raw_units: Iterable[Dict[str, Any]], mapping: Dict[str, str]) -> List[AdaptedUnit]:
    required = [
        "id_field",
        "support_value_field",
        "support_sector_field",
        "adjacent_ids_field",
    ]
    missing = [k for k in required if k not in mapping]
    if missing:
        raise SystemExit(f"Missing unit mapping key(s): {', '.join(missing)}")

    out: List[AdaptedUnit] = []
    for raw in raw_units:
        unit_id = read_path(raw, mapping["id_field"])
        support_value = float(read_path(raw, mapping["support_value_field"]))
        support_sector = int(read_path(raw, mapping["support_sector_field"]))
        adjacent_ids = list(read_path(raw, mapping["adjacent_ids_field"]))

        if support_sector not in (-1, 1):
            raise SystemExit(
                f"Mapped support_sector must be -1 or +1 in first-pass proxy mode; got {support_sector!r} for unit {unit_id!r}"
            )

        out.append(
            AdaptedUnit(
                unit_id=str(unit_id),
                support_value=support_value,
                support_sector=support_sector,
                adjacent_ids=[str(x) for x in adjacent_ids],
            )
        )
    return out


def build_unit_index(units: List[AdaptedUnit]) -> Dict[str, AdaptedUnit]:
    idx = {u.unit_id: u for u in units}
    if len(idx) != len(units):
        raise SystemExit("Duplicate unit_id detected after mapping.")
    return idx


def get_local_context(units: Dict[str, AdaptedUnit], focal_unit_id: str) -> Tuple[AdaptedUnit, List[AdaptedUnit]]:
    if focal_unit_id not in units:
        raise SystemExit(f"Unknown focal_unit_id: {focal_unit_id}")
    focal = units[focal_unit_id]
    neighborhood: List[AdaptedUnit] = []
    for nid in focal.adjacent_ids:
        if nid not in units:
            raise SystemExit(f"Unknown adjacent unit '{nid}' referenced by focal unit '{focal_unit_id}'")
        neighborhood.append(units[nid])
    if not neighborhood:
        raise SystemExit("Focal unit must have at least one immediate adjacent unit.")
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

    focal_overlap_proxy = abs(focal.support_value) / (abs(focal.support_value) + total_neighbor_abs)
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
        "metrics": {
            "agreement_local": round(agreement, 6),
            "conflict_local": round(conflict, 6),
            "a1_score": round(score, 6),
            "neighbor_count": neighbor_count,
            "focal_overlap_proxy": round(focal_overlap_proxy, 6),
            "anti_overlap_delta": round(anti_overlap_delta, 6),
        },
        "judgment": {
            "internal_activity": internal_activity,
            "anti_overlap": anti_overlap,
            "anti_stabilization": anti_stabilization,
            "short_reason": (
                f"A1 score={score:.3f}, neighbor_count={neighbor_count}, "
                f"ceiling={stabilization_ceiling:.3f}, neighbor_min={neighbor_min}; "
                f"agreement={agreement:.3f}, conflict={conflict:.3f}, anti_overlap_delta={anti_overlap_delta:.3f}."
            ),
        },
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
    baseline = abs(focal_value) + same_sector - conflict_penalty * opposite_sector
    return max(baseline, 0.0)


def compute_b1(
    focal: AdaptedUnit,
    neighborhood: List[AdaptedUnit],
    params: Dict[str, Any],
    perturbation_mapping: Dict[str, Any],
) -> Dict[str, Any]:
    mode = str(perturbation_mapping.get("mode", "scale_down"))
    strength = float(perturbation_mapping.get("strength", 0.5))

    active_threshold = float(params.get("b1_active_threshold", 0.12))
    overlap_margin = float(params.get("b1_overlap_margin", 0.05))
    conflict_penalty = float(params.get("b1_conflict_penalty", 1.0))
    stabilization_ceiling = float(params.get("b1_stabilization_ceiling", 0.70))

    baseline_support = support_proxy(focal.support_value, focal.support_sector, neighborhood, conflict_penalty)
    perturbed_value = apply_perturbation(focal.support_value, mode, strength)
    perturbed_support = support_proxy(perturbed_value, focal.support_sector, neighborhood, conflict_penalty)
    fragility = baseline_support - perturbed_support
    relative_fragility = fragility / baseline_support if baseline_support > 0 else 0.0

    focal_overlap_proxy = abs(focal.support_value) / (abs(focal.support_value) + sum(abs(u.support_value) for u in neighborhood))
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
        "metrics": {
            "baseline_support_local": round(baseline_support, 6),
            "perturbed_support_local": round(perturbed_support, 6),
            "fragility_local": round(fragility, 6),
            "relative_fragility": round(relative_fragility, 6),
            "focal_overlap_proxy": round(focal_overlap_proxy, 6),
            "anti_overlap_delta": round(anti_overlap_delta, 6),
        },
        "judgment": {
            "internal_activity": internal_activity,
            "anti_overlap": anti_overlap,
            "anti_stabilization": anti_stabilization,
            "short_reason": (
                f"B1 relative_fragility={relative_fragility:.3f} from real local perturbation binding; "
                f"baseline_support={baseline_support:.3f}, perturbed_support={perturbed_support:.3f}, "
                f"anti_overlap_delta={anti_overlap_delta:.3f}."
            ),
        },
        "derived_status": derived_status,
    }


def derive_global_outcome(a1_status: CandidateStatus, b1_status: CandidateStatus) -> str:
    active_count = sum(1 for s in [a1_status, b1_status] if s == "materially_active")
    weak_count = sum(1 for s in [a1_status, b1_status] if s == "weak_ambiguous")

    if active_count >= 1:
        return "Outcome C — Promising pre-stabilization candidate found"
    if weak_count >= 1:
        return "Outcome B — Weak but non-tautological candidate found"
    return "Outcome A — No useful first-pass candidate"


def derive_promotion(a1_status: CandidateStatus, b1_status: CandidateStatus) -> Dict[str, Any]:
    if a1_status == "materially_active" and b1_status != "materially_active":
        return {
            "promotion_state": "one_candidate_promoted",
            "lead_candidate": "A1",
            "text": "A1 promoted for next sharpening step; B1 retained as secondary candidate.",
        }
    if b1_status == "materially_active" and a1_status != "materially_active":
        return {
            "promotion_state": "one_candidate_promoted",
            "lead_candidate": "B1",
            "text": "B1 promoted for next sharpening step; A1 retained as secondary candidate.",
        }
    if a1_status == "materially_active" and b1_status == "materially_active":
        return {
            "promotion_state": "both_candidates_promoted",
            "lead_candidate": "A1_and_B1",
            "text": "Both candidates promoted for next sharpening step.",
        }
    if a1_status == "weak_ambiguous" and b1_status in {"weak_ambiguous", "collapsed"}:
        return {
            "promotion_state": "deferred",
            "lead_candidate": "A1",
            "text": "Promotion deferred; A1 is the current practical front-runner.",
        }
    if b1_status == "weak_ambiguous" and a1_status == "collapsed":
        return {
            "promotion_state": "deferred",
            "lead_candidate": "B1",
            "text": "Promotion deferred; B1 is the current practical front-runner.",
        }
    return {
        "promotion_state": "deferred",
        "lead_candidate": None,
        "text": "No candidate promoted yet.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compatibility runner bound to a real local export format.")
    parser.add_argument("--config", required=True, help="Path to run config JSON.")
    parser.add_argument("--outdir", required=True, help="Output directory.")
    args = parser.parse_args()

    cfg = load_json(Path(args.config))
    require_fields(cfg, ["run_id", "context", "frame", "params", "raw_export_path", "mapping_path"], label="run config")

    raw_export = load_json(Path(cfg["raw_export_path"]))
    mapping_cfg = load_json(Path(cfg["mapping_path"]))

    require_fields(mapping_cfg, ["unit_mapping", "perturbation_mapping", "unit_collection_path"], label="mapping config")

    raw_units = read_path(raw_export, mapping_cfg["unit_collection_path"])
    if not isinstance(raw_units, list):
        raise SystemExit("Mapped unit_collection_path must resolve to a list.")

    adapted_units = adapt_units(raw_units, mapping_cfg["unit_mapping"])
    unit_index = build_unit_index(adapted_units)

    context = cfg["context"]
    require_fields(context, ["context_id", "focal_unit_id", "status"], label="context")

    focal, neighborhood = get_local_context(unit_index, context["focal_unit_id"])

    a1 = compute_a1(focal, neighborhood, cfg["params"])
    b1 = compute_b1(focal, neighborhood, cfg["params"], mapping_cfg["perturbation_mapping"])

    global_outcome = derive_global_outcome(a1["derived_status"], b1["derived_status"])
    promotion = derive_promotion(a1["derived_status"], b1["derived_status"])

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    run_obj = {
        "schema_version": "3.1.0",
        "generated_at": now_iso(),
        "run_id": cfg["run_id"],
        "runner": {
            "name": "run_compatibility_first_pass_real_export.py",
            "mode": "real_export_mapping_computed_proxies_reformed_a1_ceiling",
        },
        "raw_export_path": cfg["raw_export_path"],
        "mapping_path": cfg["mapping_path"],
        "context": {
            **context,
            "mapped_focal_support_value": focal.support_value,
            "mapped_focal_support_sector": focal.support_sector,
            "mapped_neighborhood_unit_ids": [u.unit_id for u in neighborhood],
        },
        "frame": cfg["frame"],
        "params": cfg["params"],
        "a1": {
            "candidate_id": "CLC-A-01",
            "candidate_name": "local_support_coherence",
            **a1,
        },
        "b1": {
            "candidate_id": "ERF-B-01",
            "candidate_name": "early_removal_fragility",
            **b1,
        },
        "global_outcome": global_outcome,
        "promotion": promotion,
        "notes": cfg.get("notes", []),
    }

    summary_obj = {
        "schema_version": "3.1.0",
        "generated_at": run_obj["generated_at"],
        "run_id": cfg["run_id"],
        "context_id": context["context_id"],
        "focal_unit_id": context["focal_unit_id"],
        "a1_status": a1["derived_status"],
        "b1_status": b1["derived_status"],
        "a1_score": a1["metrics"]["a1_score"],
        "a1_neighbor_count": a1["metrics"]["neighbor_count"],
        "b1_relative_fragility": b1["metrics"]["relative_fragility"],
        "global_outcome": global_outcome,
        "promotion_state": promotion["promotion_state"],
        "lead_candidate": promotion["lead_candidate"],
    }

    (outdir / "run.json").write_text(json.dumps(run_obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (outdir / "summary.json").write_text(json.dumps(summary_obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote: {outdir / 'run.json'}")
    print(f"Wrote: {outdir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
