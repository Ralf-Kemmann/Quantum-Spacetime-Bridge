#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
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


def load_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run H3 support probe 01.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def as_bool(x: Any) -> bool | None:
    if x in (None, ""):
        return None
    s = str(x).strip().lower()
    if s == "true":
        return True
    if s == "false":
        return False
    return None


def as_float(x: Any) -> float | None:
    if x in (None, ""):
        return None
    try:
        return float(x)
    except Exception:
        return None


def infer_launchability_signal(per_class_rows: list[dict[str, Any]], comparison_rows: list[dict[str, Any]]) -> str:
    vals: list[bool] = []

    for row in per_class_rows:
        v = as_bool(row.get("launchable"))
        if v is not None:
            vals.append(v)

    for row in comparison_rows:
        for key in ("baseline_launchable", "alternative_launchable"):
            v = as_bool(row.get(key))
            if v is not None:
                vals.append(v)

    if not vals:
        return "unknown"
    return "present" if any(vals) else "absent"


def infer_structure_signal(per_class_rows: list[dict[str, Any]], comparison_rows: list[dict[str, Any]]) -> str:
    shells: list[float] = []
    neighbors: list[float] = []
    pairs: list[float] = []

    for row in per_class_rows:
        for key in ("shell_count", "mean_neighbor_count", "pair_unit_count"):
            v = as_float(row.get(key))
            if v is None:
                continue
            if key == "shell_count":
                shells.append(v)
            elif key == "mean_neighbor_count":
                neighbors.append(v)
            elif key == "pair_unit_count":
                pairs.append(v)

    for row in comparison_rows:
        for key in (
            "baseline_shell_count",
            "alternative_shell_count",
            "baseline_mean_neighbor_count",
            "alternative_mean_neighbor_count",
        ):
            v = as_float(row.get(key))
            if v is None:
                continue
            if "shell_count" in key:
                shells.append(v)
            elif "mean_neighbor_count" in key:
                neighbors.append(v)

    if any(x > 0 for x in shells) and any(x > 0 for x in neighbors) and any(x > 0 for x in pairs):
        return "present"
    if any(x > 0 for x in pairs) or any(x > 0 for x in neighbors):
        return "weak_present"
    return "unknown"


def infer_class_level_stability(per_class_rows: list[dict[str, Any]]) -> str:
    stable = 0
    total = 0

    by_class: dict[str, list[dict[str, Any]]] = {}
    for row in per_class_rows:
        by_class.setdefault(str(row.get("export_class", "unknown")), []).append(row)

    for _, rows in by_class.items():
        statuses = [str(r.get("combined_status", "")) for r in rows if r.get("combined_status") not in (None, "")]
        if len(statuses) >= 2:
            total += 1
            if len(set(statuses)) == 1:
                stable += 1

    if total == 0:
        return "unknown"
    frac = stable / total
    if frac >= 0.8:
        return "stable"
    if frac >= 0.5:
        return "mixed"
    return "unstable"


def infer_comparison_stability(comparison_rows: list[dict[str, Any]]) -> str:
    if not comparison_rows:
        return "unknown"

    stable = 0
    total = 0
    for row in comparison_rows:
        total += 1
        delta_combined = str(row.get("delta_combined_status", "")).strip().lower()
        interpretation_flag = str(row.get("interpretation_flag", "")).strip().lower()

        if delta_combined == "unchanged" and interpretation_flag in {"stable", "soft_shift", ""}:
            stable += 1

    frac = stable / total
    if frac >= 0.8:
        return "stable"
    if frac >= 0.5:
        return "mixed"
    return "unstable"


def decide_probe_outcome(launch: str, structure: str, class_stab: str, comp_stab: str) -> tuple[str, str, str, str]:
    baseline_anchor_status = "primary_retained"

    if launch == "present" and structure == "present" and class_stab in {"stable", "mixed"}:
        auxiliary_compatibility = "compatible_but_bounded"
        expected_auxiliary_gain_level = "low"
        if comp_stab == "stable":
            support_probe_outcome = "support_probe_promising_but_limited"
        else:
            support_probe_outcome = "support_probe_compatible_but_low_gain"
    elif launch == "present" and structure == "weak_present":
        auxiliary_compatibility = "compatible_but_fragile"
        expected_auxiliary_gain_level = "low"
        support_probe_outcome = "support_probe_compatible_but_low_gain"
    elif launch in {"present", "unknown"}:
        auxiliary_compatibility = "uncertain_or_fragile"
        expected_auxiliary_gain_level = "low"
        support_probe_outcome = "support_probe_too_weak"
    else:
        auxiliary_compatibility = "not_interpretable"
        expected_auxiliary_gain_level = "none"
        support_probe_outcome = "support_probe_not_interpretable"

    return baseline_anchor_status, auxiliary_compatibility, expected_auxiliary_gain_level, support_probe_outcome


def build_block_readout(summary: dict[str, Any]) -> str:
    lines = [
        "# H3 Support Probe 01",
        "",
        "## Ziel",
        "Kleiner support-seitiger Machbarkeitsfühler für baseline-first versus begrenzten auxiliary-Vergleich.",
        "",
        "## Probeurteil",
        f"- source_block: `{summary['source_block']}`",
        f"- launchability_signal: `{summary['launchability_signal']}`",
        f"- structure_signal: `{summary['structure_signal']}`",
        f"- class_level_stability_signal: `{summary['class_level_stability_signal']}`",
        f"- comparison_stability_signal: `{summary['comparison_stability_signal']}`",
        f"- baseline_anchor_status: `{summary['baseline_anchor_status']}`",
        f"- auxiliary_compatibility: `{summary['auxiliary_compatibility']}`",
        f"- expected_auxiliary_gain_level: `{summary['expected_auxiliary_gain_level']}`",
        f"- support_probe_outcome: `{summary['support_probe_outcome']}`",
        f"- recommended_next_step: `{summary['recommended_next_step']}`",
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

    summary_path = Path(cfg["inputs"]["summary_json"]).resolve()
    per_class_path = Path(cfg["inputs"]["per_class_csv"]).resolve()
    comparison_path = Path(cfg["inputs"]["comparison_csv"]).resolve()

    summary_json = load_json(summary_path)
    per_class_rows = load_csv_rows(per_class_path)
    comparison_rows = load_csv_rows(comparison_path)

    source_block = str(summary_json.get("block", summary_json.get("run_id", "unknown")))
    launch = infer_launchability_signal(per_class_rows, comparison_rows)
    structure = infer_structure_signal(per_class_rows, comparison_rows)
    class_stab = infer_class_level_stability(per_class_rows)
    comp_stab = infer_comparison_stability(comparison_rows)

    baseline_anchor_status, auxiliary_compatibility, expected_auxiliary_gain_level, support_probe_outcome = decide_probe_outcome(
        launch, structure, class_stab, comp_stab
    )

    if support_probe_outcome == "support_probe_promising_but_limited":
        next_step = "proceed_to_h3_support_side_by_side_probe"
        summary_text = "The decoupling block can serve as a limited support-side H3 probe input, with baseline-first retained and only bounded auxiliary expectations."
    elif support_probe_outcome == "support_probe_compatible_but_low_gain":
        next_step = "proceed_cautiously_with_support_only_test"
        summary_text = "The decoupling block appears support-compatible, but any auxiliary gain is expected to remain limited and clearly secondary."
    elif support_probe_outcome == "support_probe_too_weak":
        next_step = "do_not_open_full_h3_probe_yet"
        summary_text = "The current support-side candidate remains too weak for a meaningful baseline-versus-auxiliary probe."
    else:
        next_step = "exclude_from_h3_probe_for_now"
        summary_text = "The current candidate is not interpretable enough to support even a limited H3 support-side probe."

    summary = {
        "run_id": cfg["run_id"],
        "created_at_utc": now_utc_iso(),
        "source_block": source_block,
        "launchability_signal": launch,
        "structure_signal": structure,
        "class_level_stability_signal": class_stab,
        "comparison_stability_signal": comp_stab,
        "baseline_anchor_status": baseline_anchor_status,
        "auxiliary_compatibility": auxiliary_compatibility,
        "expected_auxiliary_gain_level": expected_auxiliary_gain_level,
        "support_probe_outcome": support_probe_outcome,
        "recommended_next_step": next_step,
        "summary_text": summary_text,
    }

    table_rows = [summary.copy()]
    write_json(output_dir / "summary.json", summary)
    write_csv(output_dir / "probe_table.csv", table_rows)
    write_md(output_dir / "block_readout.md", build_block_readout(summary))

    print(json.dumps({
        "run_id": summary["run_id"],
        "support_probe_outcome": summary["support_probe_outcome"],
        "recommended_next_step": summary["recommended_next_step"],
        "output_dir": str(output_dir),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
