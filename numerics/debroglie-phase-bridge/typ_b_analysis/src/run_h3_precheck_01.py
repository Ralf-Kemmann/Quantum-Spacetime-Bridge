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
    parser = argparse.ArgumentParser(description="Run H3 precheck 01.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def get_tie_density(payload: dict[str, Any]) -> float | None:
    gs = payload.get("global_summary", {})
    if not isinstance(gs, dict):
        return None
    keys = ["negative_advantage_count", "abs_advantage_count", "tie_count", "not_applicable_count"]
    vals = {k: int(gs.get(k, 0) or 0) for k in keys}
    total = vals["negative_advantage_count"] + vals["abs_advantage_count"] + vals["tie_count"] + vals["not_applicable_count"]
    if total <= 0:
        return None
    return vals["tie_count"] / total


def get_launchability_signal(payload: dict[str, Any]) -> str:
    if "per_class" in payload:
        per_class = payload.get("per_class", {})
        launchables = []
        for class_payload in per_class.values():
            if not isinstance(class_payload, dict):
                continue
            for mode in ("baseline", "alternative"):
                mp = class_payload.get(mode, {})
                if isinstance(mp, dict):
                    val = mp.get("launchable")
                    if val is not None:
                        launchables.append(bool(val))
        if not launchables:
            return "unknown"
        if any(launchables):
            return "present"
        return "absent"

    per_dataset = payload.get("per_dataset", {})
    launchables = []
    for ds_payload in per_dataset.values():
        if not isinstance(ds_payload, dict):
            continue
        for mode in ("baseline", "alternative"):
            mp = ds_payload.get(mode, {})
            if isinstance(mp, dict):
                for key in ("negative_launchable", "abs_launchable", "positive_launchable"):
                    if key in mp:
                        launchables.append(bool(mp.get(key)))
    if not launchables:
        return "unknown"
    if any(launchables):
        return "present"
    return "absent"


def get_structure_signal(payload: dict[str, Any]) -> str:
    if "per_class" in payload:
        per_class = payload.get("per_class", {})
        shell_counts = []
        pair_counts = []
        for class_payload in per_class.values():
            if not isinstance(class_payload, dict):
                continue
            for mode in ("baseline", "alternative"):
                mp = class_payload.get(mode, {})
                if isinstance(mp, dict):
                    sc = mp.get("shell_count")
                    pc = mp.get("pair_unit_count")
                    if sc is not None:
                        shell_counts.append(float(sc))
                    if pc is not None:
                        pair_counts.append(float(pc))
        if any(x > 0 for x in shell_counts) and any(x > 0 for x in pair_counts):
            return "present"
        if pair_counts and any(x > 0 for x in pair_counts):
            return "boundary_only"
        return "absent"

    return "unknown"


def readiness_from_signals(tie_density: float | None, launchability: str, structure: str) -> str:
    if structure == "absent":
        return "not_ready"
    if structure == "boundary_only":
        return "boundary_limited"
    if tie_density is not None and tie_density >= 0.7:
        return "weakly_ready_at_best"
    if launchability == "absent":
        return "not_ready"
    return "conditionally_ready"


def build_block_readout(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# H3 Precheck 01",
        "",
        "## Ziel",
        "Prüfen, ob die aktuelle Typ-B/N1-Lage bereits genug Differenzierung und lokale Struktur für H3-Paketurteile trägt.",
        "",
        "## Blockübersicht",
    ]
    for row in rows:
        lines.append(
            f"- {row['source_block']}: block_judgement=`{row['block_judgement']}`, "
            f"tie_density=`{row['tie_density']}`, "
            f"launchability_signal=`{row['launchability_signal']}`, "
            f"structure_signal=`{row['structure_signal']}`, "
            f"readiness_contribution=`{row['readiness_contribution']}`"
        )
    lines += [
        "",
        "## Globalurteil",
        f"- differentiation_status: `{summary['differentiation_status']}`",
        f"- launchability_status: `{summary['launchability_status']}`",
        f"- structure_readiness_status: `{summary['structure_readiness_status']}`",
        f"- h3_package_readiness: `{summary['h3_package_readiness']}`",
        f"- primary_blocker: `{summary['primary_blocker']}`",
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

    rows: list[dict[str, Any]] = []
    tie_values = []
    launchability_values = []
    structure_values = []

    for src in cfg["inputs"]["summaries"]:
        path = Path(src).resolve()
        payload = load_json(path)

        source_block = str(payload.get("block", path.stem))
        block_judgement = str(payload.get("decision", {}).get("block_judgement", "unknown"))
        tie_density = get_tie_density(payload)
        launchability_signal = get_launchability_signal(payload)
        structure_signal = get_structure_signal(payload)
        readiness_contribution = readiness_from_signals(tie_density, launchability_signal, structure_signal)

        row = {
            "source_file": str(path),
            "source_block": source_block,
            "block_judgement": block_judgement,
            "tie_density": round(tie_density, 6) if tie_density is not None else None,
            "launchability_signal": launchability_signal,
            "structure_signal": structure_signal,
            "readiness_contribution": readiness_contribution,
            "comment": "",
        }
        rows.append(row)

        if tie_density is not None:
            tie_values.append(tie_density)
        launchability_values.append(launchability_signal)
        structure_values.append(structure_signal)

    avg_tie = sum(tie_values) / len(tie_values) if tie_values else None

    differentiation_status = "weak" if (avg_tie is not None and avg_tie >= 0.7) else "unclear_or_mixed"

    if all(x == "absent" for x in launchability_values if x != "unknown"):
        launchability_status = "weak"
    elif any(x == "present" for x in launchability_values):
        launchability_status = "mixed"
    else:
        launchability_status = "unclear"

    if "absent" in structure_values:
        structure_readiness_status = "weak"
    elif "boundary_only" in structure_values:
        structure_readiness_status = "weak_to_boundary_limited"
    else:
        structure_readiness_status = "mixed"

    if structure_readiness_status in {"weak", "weak_to_boundary_limited"} and differentiation_status == "weak":
        h3_package_readiness = "not_ready_yet"
        primary_blocker = "insufficient internal differentiation and boundary-dominated local structure"
    else:
        h3_package_readiness = "partially_ready_only"
        primary_blocker = "readiness remains limited and context-dependent"

    summary = {
        "run_id": cfg["run_id"],
        "created_at_utc": now_utc_iso(),
        "differentiation_status": differentiation_status,
        "launchability_status": launchability_status,
        "structure_readiness_status": structure_readiness_status,
        "h3_package_readiness": h3_package_readiness,
        "primary_blocker": primary_blocker,
        "summary_text": (
            "Current data do not yet provide a strong enough internal differentiation and local structure basis for a clean H3 package-role hierarchy test."
            if h3_package_readiness == "not_ready_yet"
            else "Current data provide at best a partial basis for H3 package-role testing."
        ),
        "block_rows": rows,
    }

    write_json(output_dir / "summary.json", summary)
    write_csv(output_dir / "precheck_table.csv", rows)
    write_md(output_dir / "block_readout.md", build_block_readout(summary, rows))

    print(json.dumps({
        "run_id": summary["run_id"],
        "h3_package_readiness": summary["h3_package_readiness"],
        "primary_blocker": summary["primary_blocker"],
        "output_dir": str(output_dir),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
