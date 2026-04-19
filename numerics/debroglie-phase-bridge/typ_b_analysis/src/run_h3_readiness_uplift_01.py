#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from reporting import write_csv, write_json


def now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_md(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be a mapping: {path}")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run H3 readiness uplift 01.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def infer_block_type(payload: dict[str, Any], source_block: str) -> str:
    if source_block.startswith("N1_NEGATIVE_VS_ABS_MARKERS"):
        return "marker_comparison"
    if source_block.startswith("N1_NEGATIVE_VS_ABS"):
        return "class_specificity"
    if source_block == "N1":
        return "alt_neighborhood"
    if "decoupling" in str(payload.get("run_id", "")).lower():
        return "decoupling"
    return "other"


def tie_density_from_global_summary(payload: dict[str, Any]) -> float | None:
    gs = payload.get("global_summary", {})
    if not isinstance(gs, dict):
        return None
    neg = int(gs.get("negative_advantage_count", 0) or 0)
    absv = int(gs.get("abs_advantage_count", 0) or 0)
    ties = int(gs.get("tie_count", 0) or 0)
    na = int(gs.get("not_applicable_count", 0) or 0)
    total = neg + absv + ties + na
    if total <= 0:
        return None
    return ties / total


def launchability_signal(payload: dict[str, Any]) -> str:
    if "per_class" in payload:
        vals = []
        for class_payload in payload["per_class"].values():
            if not isinstance(class_payload, dict):
                continue
            for mode in ("baseline", "alternative"):
                mp = class_payload.get(mode, {})
                if isinstance(mp, dict) and "launchable" in mp:
                    vals.append(bool(mp["launchable"]))
        if not vals:
            return "unknown"
        return "present" if any(vals) else "absent"

    if "per_dataset" in payload:
        vals = []
        for ds_payload in payload["per_dataset"].values():
            if not isinstance(ds_payload, dict):
                continue
            for mode in ("baseline", "alternative"):
                mp = ds_payload.get(mode, {})
                if isinstance(mp, dict):
                    for key in ("negative_launchable", "abs_launchable", "positive_launchable"):
                        if key in mp:
                            vals.append(bool(mp[key]))
        if not vals:
            return "unknown"
        return "present" if any(vals) else "absent"

    return "unknown"


def structure_signal(payload: dict[str, Any]) -> str:
    if "per_class" in payload:
        shells = []
        pairs = []
        neighbors = []
        for class_payload in payload["per_class"].values():
            if not isinstance(class_payload, dict):
                continue
            for mode in ("baseline", "alternative"):
                mp = class_payload.get(mode, {})
                if isinstance(mp, dict):
                    if "shell_count" in mp and mp["shell_count"] is not None:
                        shells.append(float(mp["shell_count"]))
                    if "pair_unit_count" in mp and mp["pair_unit_count"] is not None:
                        pairs.append(float(mp["pair_unit_count"]))
                    if "mean_neighbor_count" in mp and mp["mean_neighbor_count"] is not None:
                        neighbors.append(float(mp["mean_neighbor_count"]))
        if any(x > 0 for x in shells) and any(x > 0 for x in pairs):
            return "present"
        if any(x > 0 for x in pairs) or any(x > 0 for x in neighbors):
            return "boundary_only"
        return "absent"

    return "unknown"


def differentiation_signal(payload: dict[str, Any], tie_warn: float) -> str:
    td = tie_density_from_global_summary(payload)
    if td is None:
        return "unknown"
    if td >= tie_warn:
        return "weak"
    if td >= 0.4:
        return "mixed"
    return "present"


def candidate_role(launch: str, structure: str, diff: str) -> tuple[str, str]:
    if launch == "present" and structure == "present" and diff in {"present", "mixed"}:
        return "reference_candidate", "strongest_available"
    if launch == "present" and structure in {"present", "boundary_only"}:
        return "support_candidate", "usable_but_limited"
    if structure == "boundary_only" or diff == "weak":
        return "not_ready", "restricted"
    return "reject_for_h3_now", "excluded"


def build_block_readout(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# H3 Readiness Uplift 01",
        "",
        "## Ziel",
        "Identifikation der tragfähigsten aktuellen Quellblöcke für spätere H3-Paketeingänge.",
        "",
        "## Kandidatenübersicht",
    ]
    for row in rows:
        lines.append(
            f"- {row['source_block']}: role=`{row['h3_candidate_role']}`, "
            f"readiness=`{row['readiness_level']}`, "
            f"launchability=`{row['launchability_signal']}`, "
            f"structure=`{row['structure_signal']}`, "
            f"differentiation=`{row['differentiation_signal']}`"
        )
    lines += [
        "",
        "## Globalurteil",
        f"- overall_uplift_status: `{summary['overall_uplift_status']}`",
        f"- best_reference_candidates: `{summary['best_reference_candidates']}`",
        f"- best_support_candidates: `{summary['best_support_candidates']}`",
        f"- excluded_sources: `{summary['excluded_sources']}`",
        f"- recommended_next_h3_input_set: `{summary['recommended_next_h3_input_set']}`",
        "",
        "## Kurzlesart",
        f"- {summary['summary_text']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    cfg = load_yaml(Path(args.config).resolve())
    output_dir = Path(cfg["output_dir"]).resolve()
    ensure_dir(output_dir)

    tie_warn = float(cfg["policy"]["tie_warning_threshold"])
    rows: list[dict[str, Any]] = []

    for src in cfg["inputs"]["summaries"]:
        path = Path(src).resolve()
        payload = load_json(path)

        source_block = str(payload.get("block", path.stem))
        block_type = infer_block_type(payload, source_block)
        launch = launchability_signal(payload)
        struct = structure_signal(payload)
        diff = differentiation_signal(payload, tie_warn)
        role, readiness = candidate_role(launch, struct, diff)

        row = {
            "source_file": str(path),
            "source_block": source_block,
            "block_type": block_type,
            "launchability_signal": launch,
            "structure_signal": struct,
            "differentiation_signal": diff,
            "h3_candidate_role": role,
            "readiness_level": readiness,
            "comment": "",
        }
        rows.append(row)

    best_reference = [r["source_block"] for r in rows if r["h3_candidate_role"] == "reference_candidate"]
    best_support = [r["source_block"] for r in rows if r["h3_candidate_role"] == "support_candidate"]
    excluded = [r["source_block"] for r in rows if r["h3_candidate_role"] in {"not_ready", "reject_for_h3_now"}]

    if best_reference or best_support:
        overall = "partial_readiness_uplift_achieved"
    else:
        overall = "no_meaningful_uplift_yet"

    if best_reference:
        next_input = best_reference
    elif best_support:
        next_input = best_support
    else:
        next_input = []

    summary = {
        "run_id": cfg["run_id"],
        "created_at_utc": now_utc_iso(),
        "best_reference_candidates": best_reference,
        "best_support_candidates": best_support,
        "excluded_sources": excluded,
        "overall_uplift_status": overall,
        "recommended_next_h3_input_set": next_input,
        "summary_text": (
            "Some blocks can be retained as limited H3 input candidates, but readiness remains partial and selective."
            if overall == "partial_readiness_uplift_achieved"
            else "No current source block provides a strong enough basis for a clean next-stage H3 package test."
        ),
        "candidate_rows": rows,
    }

    write_json(output_dir / "summary.json", summary)
    write_csv(output_dir / "candidate_table.csv", rows)
    write_md(output_dir / "block_readout.md", build_block_readout(summary, rows))

    print(json.dumps({
        "run_id": summary["run_id"],
        "overall_uplift_status": summary["overall_uplift_status"],
        "recommended_next_h3_input_set": summary["recommended_next_h3_input_set"],
        "output_dir": str(output_dir),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
