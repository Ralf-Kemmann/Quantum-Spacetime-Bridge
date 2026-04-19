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
    parser = argparse.ArgumentParser(description="Run H3 support side-by-side probe 01.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def as_float(x: Any) -> float | None:
    if x in (None, ""):
        return None
    try:
        return float(x)
    except Exception:
        return None


def read_comparison_signals(rows: list[dict[str, Any]]) -> tuple[str, str, str, str]:
    if not rows:
        return "unknown", "unknown", "unknown", "unknown"

    combined_unchanged = 0
    a1_strengthened = 0
    b1_unchanged = 0
    neighbor_positive = 0
    total = 0

    for row in rows:
        total += 1
        if str(row.get("delta_combined_status", "")).strip().lower() == "unchanged":
            combined_unchanged += 1
        if str(row.get("delta_a1_status", "")).strip().lower() in {"strengthened", "improved"}:
            a1_strengthened += 1
        if str(row.get("delta_b1_status", "")).strip().lower() == "unchanged":
            b1_unchanged += 1
        dn = as_float(row.get("delta_mean_neighbor_count"))
        if dn is not None and dn > 0:
            neighbor_positive += 1

    combined_status_stability = "stable" if combined_unchanged == total else ("mixed" if combined_unchanged > 0 else "unstable")
    a1_shift_signal = "positive_low_level_shift" if a1_strengthened > 0 else "flat"
    b1_shift_signal = "stable" if b1_unchanged == total else ("mixed" if b1_unchanged > 0 else "shifted")
    neighbor_shift_signal = "positive_shift" if neighbor_positive > 0 else "flat"

    return combined_status_stability, neighbor_shift_signal, a1_shift_signal, b1_shift_signal


def class_level_readout(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append({
            "export_class": row.get("export_class"),
            "baseline_launchable": row.get("baseline_launchable"),
            "alternative_launchable": row.get("alternative_launchable"),
            "baseline_combined_status": row.get("baseline_combined_status"),
            "alternative_combined_status": row.get("alternative_combined_status"),
            "delta_combined_status": row.get("delta_combined_status"),
            "delta_mean_neighbor_count": row.get("delta_mean_neighbor_count"),
            "delta_a1_status": row.get("delta_a1_status"),
            "delta_b1_status": row.get("delta_b1_status"),
            "interpretation_flag": row.get("interpretation_flag"),
        })
    return out


def decide_outcome(combined_status_stability: str, neighbor_shift_signal: str, a1_shift_signal: str, b1_shift_signal: str) -> tuple[str, str, str]:
    baseline_anchor_status = "primary_retained"
    auxiliary_compatibility = "compatible_but_bounded"

    if combined_status_stability == "stable":
        if neighbor_shift_signal == "positive_shift" or a1_shift_signal == "positive_low_level_shift":
            expected_gain_profile = "low_but_readable"
            outcome = "support_side_by_side_admissible_low_gain"
        else:
            expected_gain_profile = "flat_to_low"
            outcome = "support_side_by_side_admissible_but_flat"
    elif combined_status_stability == "mixed":
        expected_gain_profile = "low_and_fragile"
        outcome = "support_side_by_side_too_weak"
    else:
        auxiliary_compatibility = "not_interpretable"
        expected_gain_profile = "none"
        outcome = "support_side_by_side_not_interpretable"

    return baseline_anchor_status, auxiliary_compatibility, expected_gain_profile, outcome


def build_block_readout(summary: dict[str, Any]) -> str:
    lines = [
        "# H3 Support Side-by-Side Probe 01",
        "",
        "## Ziel",
        "Erster kleiner support-seitiger baseline-versus-auxiliary Vergleich auf N1_A1_B1_DECOUPLING.",
        "",
        "## Probeurteil",
        f"- source_block: `{summary['source_block']}`",
        f"- baseline_anchor_status: `{summary['baseline_anchor_status']}`",
        f"- combined_status_stability: `{summary['combined_status_stability']}`",
        f"- auxiliary_compatibility: `{summary['auxiliary_compatibility']}`",
        f"- neighbor_shift_signal: `{summary['neighbor_shift_signal']}`",
        f"- a1_shift_signal: `{summary['a1_shift_signal']}`",
        f"- b1_shift_signal: `{summary['b1_shift_signal']}`",
        f"- expected_gain_profile: `{summary['expected_gain_profile']}`",
        f"- support_side_by_side_outcome: `{summary['support_side_by_side_outcome']}`",
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

    summary_json = load_json(Path(cfg["inputs"]["summary_json"]).resolve())
    comparison_rows = load_csv_rows(Path(cfg["inputs"]["comparison_csv"]).resolve())

    source_block = str(summary_json.get("block", summary_json.get("run_id", "unknown")))
    combined_status_stability, neighbor_shift_signal, a1_shift_signal, b1_shift_signal = read_comparison_signals(comparison_rows)
    baseline_anchor_status, auxiliary_compatibility, expected_gain_profile, outcome = decide_outcome(
        combined_status_stability, neighbor_shift_signal, a1_shift_signal, b1_shift_signal
    )

    if outcome == "support_side_by_side_admissible_low_gain":
        next_step = "document_as_limited_support_side_h3_entry"
        summary_text = "The support-side decoupling block permits a first bounded side-by-side H3 reading: baseline remains primary, while the auxiliary reading contributes only a low but readable additional contrast."
    elif outcome == "support_side_by_side_admissible_but_flat":
        next_step = "retain_as_flat_support_side_candidate"
        summary_text = "The support-side decoupling block remains admissible for side-by-side reading, but the additional gain stays very flat and clearly secondary."
    elif outcome == "support_side_by_side_too_weak":
        next_step = "do_not_extend_beyond_probe"
        summary_text = "The support-side block is not yet strong enough for a meaningful bounded side-by-side H3 readout."
    else:
        next_step = "exclude_from_side_by_side_use"
        summary_text = "The current support-side block is not interpretable enough for side-by-side H3 use."

    summary = {
        "run_id": cfg["run_id"],
        "created_at_utc": now_utc_iso(),
        "source_block": source_block,
        "baseline_anchor_status": baseline_anchor_status,
        "combined_status_stability": combined_status_stability,
        "auxiliary_compatibility": auxiliary_compatibility,
        "neighbor_shift_signal": neighbor_shift_signal,
        "a1_shift_signal": a1_shift_signal,
        "b1_shift_signal": b1_shift_signal,
        "expected_gain_profile": expected_gain_profile,
        "support_side_by_side_outcome": outcome,
        "recommended_next_step": next_step,
        "summary_text": summary_text,
        "class_level_readout": class_level_readout(comparison_rows),
    }

    write_json(output_dir / "summary.json", summary)
    write_csv(output_dir / "probe_table.csv", [summary])
    write_md(output_dir / "block_readout.md", build_block_readout(summary))

    print(json.dumps({
        "run_id": summary["run_id"],
        "support_side_by_side_outcome": summary["support_side_by_side_outcome"],
        "recommended_next_step": summary["recommended_next_step"],
        "output_dir": str(output_dir),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
