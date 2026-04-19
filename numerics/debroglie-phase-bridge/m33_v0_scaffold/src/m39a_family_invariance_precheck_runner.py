#!/usr/bin/env python3
"""
M.3.9a.1 — Family Invariance Precheck Runner

Purpose
-------
This runner performs a lightweight structural precheck over newly defined
spectral families. It does *not* run the full branch identity audit.
Instead, it computes pairwise delta_p / delta_p2 structures and assigns a
first-pass asymmetry type to each family.

Design goals
------------
- stand-alone and easy to run
- explicit CLI interface
- defensive error handling
- readable, well-commented code
- outputs simple CSV/JSON/Markdown artifacts for later inspection

Typical usage
-------------
python src/m39a_family_invariance_precheck_runner.py \
  --project-root . \
  --config configs/config_m39a_family_invariance_precheck.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable

import yaml


@dataclass(frozen=True)
class FamilyDefinition:
    family_id: str
    description: str
    expected_type: str
    notes: str
    p_values: tuple[float, ...]


@dataclass(frozen=True)
class Thresholds:
    min_modes_required: int
    preferred_modes: int
    large_negative_threshold: float
    compact_negative_lower: float
    compact_negative_upper: float
    symmetry_mean_tolerance: float
    symmetry_balance_tolerance: float
    min_large_negative_fraction: float
    min_compact_negative_fraction: float
    min_positive_fraction: float
    min_type_confidence: float
    compact_dominance_margin: float
    compact_extreme_guard: float
    large_negative_extreme_guard: float


@dataclass(frozen=True)
class SelectionRules:
    require_control_family: bool
    require_large_negative_family: bool
    require_compact_negative_family: bool
    max_failed_families_for_pass: int


@dataclass(frozen=True)
class OutputSpec:
    root: str
    family_definitions_expanded: str
    family_pair_class_screen: str
    family_type_summary: str
    family_type_precheck: str
    family_invariance_precheck_report: str


@dataclass(frozen=True)
class Config:
    family_definitions_path: str
    thresholds: Thresholds
    labels: dict[str, str]
    selection: SelectionRules
    output: OutputSpec


class ConfigError(ValueError):
    """Raised when a config or family definition is invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="M.3.9a family invariance precheck")
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    return parser.parse_args()


def load_yaml(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def ensure_dict(obj: Any, context: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise ConfigError(f"Expected mapping for {context}, got {type(obj).__name__}")
    return obj


def ensure_list(obj: Any, context: str) -> list[Any]:
    if not isinstance(obj, list):
        raise ConfigError(f"Expected list for {context}, got {type(obj).__name__}")
    return obj


def stable_float(value: Any, context: str) -> float:
    try:
        return float(value)
    except Exception as exc:
        raise ConfigError(f"Invalid numeric value in {context}: {value!r}") from exc


def stable_int(value: Any, context: str) -> int:
    try:
        return int(value)
    except Exception as exc:
        raise ConfigError(f"Invalid integer value in {context}: {value!r}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_config(config_path: Path) -> Config:
    raw = ensure_dict(load_yaml(config_path), f"config file {config_path}")
    block = ensure_dict(raw.get("m39a_family_invariance_precheck"), "m39a_family_invariance_precheck")

    input_block = ensure_dict(block.get("input"), "input")
    screening = ensure_dict(block.get("screening"), "screening")
    typing_block = ensure_dict(block.get("typing"), "typing")
    labels = ensure_dict(typing_block.get("candidate_labels"), "typing.candidate_labels")
    selection_block = ensure_dict(block.get("selection"), "selection")
    output_block = ensure_dict(block.get("output"), "output")

    thresholds = Thresholds(
        min_modes_required=stable_int(screening.get("min_modes_required"), "screening.min_modes_required"),
        preferred_modes=stable_int(screening.get("preferred_modes"), "screening.preferred_modes"),
        large_negative_threshold=stable_float(screening.get("large_negative_threshold"), "screening.large_negative_threshold"),
        compact_negative_lower=stable_float(screening.get("compact_negative_lower"), "screening.compact_negative_lower"),
        compact_negative_upper=stable_float(screening.get("compact_negative_upper"), "screening.compact_negative_upper"),
        symmetry_mean_tolerance=stable_float(screening.get("symmetry_mean_tolerance"), "screening.symmetry_mean_tolerance"),
        symmetry_balance_tolerance=stable_float(screening.get("symmetry_balance_tolerance"), "screening.symmetry_balance_tolerance"),
        min_large_negative_fraction=stable_float(screening.get("min_large_negative_fraction"), "screening.min_large_negative_fraction"),
        min_compact_negative_fraction=stable_float(screening.get("min_compact_negative_fraction"), "screening.min_compact_negative_fraction"),
        min_positive_fraction=stable_float(screening.get("min_positive_fraction"), "screening.min_positive_fraction"),
        min_type_confidence=stable_float(screening.get("min_type_confidence"), "screening.min_type_confidence"),
        compact_dominance_margin=stable_float(screening.get("compact_dominance_margin", 0.05), "screening.compact_dominance_margin"),
        compact_extreme_guard=stable_float(screening.get("compact_extreme_guard", 20.0), "screening.compact_extreme_guard"),
        large_negative_extreme_guard=stable_float(screening.get("large_negative_extreme_guard", 20.0), "screening.large_negative_extreme_guard"),
    )

    selection = SelectionRules(
        require_control_family=bool(selection_block.get("require_control_family", True)),
        require_large_negative_family=bool(selection_block.get("require_large_negative_family", True)),
        require_compact_negative_family=bool(selection_block.get("require_compact_negative_family", True)),
        max_failed_families_for_pass=stable_int(selection_block.get("max_failed_families_for_pass", 2), "selection.max_failed_families_for_pass"),
    )

    output = OutputSpec(
        root=str(output_block.get("root")),
        family_definitions_expanded=str(output_block.get("family_definitions_expanded")),
        family_pair_class_screen=str(output_block.get("family_pair_class_screen")),
        family_type_summary=str(output_block.get("family_type_summary")),
        family_type_precheck=str(output_block.get("family_type_precheck")),
        family_invariance_precheck_report=str(output_block.get("family_invariance_precheck_report")),
    )

    family_definitions_path = str(input_block.get("family_definitions"))
    if not family_definitions_path:
        raise ConfigError("input.family_definitions must be provided")

    return Config(
        family_definitions_path=family_definitions_path,
        thresholds=thresholds,
        labels=labels,
        selection=selection,
        output=output,
    )


def load_family_definitions(path: Path, thresholds: Thresholds) -> list[FamilyDefinition]:
    raw = ensure_dict(load_yaml(path), f"family definitions file {path}")
    raw_families = ensure_list(raw.get("families"), "families")

    seen_ids: set[str] = set()
    result: list[FamilyDefinition] = []

    for index, raw_family in enumerate(raw_families, start=1):
        family = ensure_dict(raw_family, f"families[{index}]")
        family_id = str(family.get("family_id", "")).strip()
        if not family_id:
            raise ConfigError(f"families[{index}] is missing family_id")
        if family_id in seen_ids:
            raise ConfigError(f"Duplicate family_id detected: {family_id}")
        seen_ids.add(family_id)

        p_values_raw = ensure_list(family.get("p_values"), f"families[{index}].p_values")
        p_values = tuple(sorted(stable_float(v, f"families[{index}].p_values") for v in p_values_raw))

        if len(p_values) < thresholds.min_modes_required:
            raise ConfigError(
                f"Family {family_id} has too few modes: {len(p_values)} < {thresholds.min_modes_required}"
            )
        if len(set(p_values)) != len(p_values):
            raise ConfigError(f"Family {family_id} contains duplicate p_values: {p_values}")

        result.append(
            FamilyDefinition(
                family_id=family_id,
                description=str(family.get("description", "")).strip(),
                expected_type=str(family.get("expected_type", "")).strip(),
                notes=str(family.get("notes", "")).strip(),
                p_values=p_values,
            )
        )

    if not result:
        raise ConfigError("No families were defined in the family definition file")

    return result


def classify_delta_p2_bucket(delta_p2: float, thresholds: Thresholds) -> str:
    if delta_p2 <= thresholds.large_negative_threshold:
        return "large_negative"
    if thresholds.compact_negative_lower < delta_p2 < thresholds.compact_negative_upper:
        return "compact_negative"
    if delta_p2 == 0:
        return "zero"
    if delta_p2 > 0:
        return "positive"
    return "other_negative"


def generate_pair_rows(family: FamilyDefinition, thresholds: Thresholds) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    p_vals = family.p_values
    for i in range(len(p_vals)):
        for j in range(i + 1, len(p_vals)):
            p_i = p_vals[i]
            p_j = p_vals[j]
            delta_p = p_i - p_j
            delta_p2 = p_i**2 - p_j**2
            rows.append(
                {
                    "family_id": family.family_id,
                    "pair_i": i,
                    "pair_j": j,
                    "p_i": p_i,
                    "p_j": p_j,
                    "delta_p": delta_p,
                    "delta_p_abs": abs(delta_p),
                    "delta_p2": delta_p2,
                    "sum_p": p_i + p_j,
                    "mean_p": (p_i + p_j) / 2.0,
                    "delta_p2_bucket": classify_delta_p2_bucket(delta_p2, thresholds),
                }
            )
    return rows


def safe_fraction(count: int, total: int) -> float:
    return float(count) / float(total) if total else 0.0


def suggest_type(rows: list[dict[str, Any]], thresholds: Thresholds, labels: dict[str, str]) -> tuple[str, float]:
    total = len(rows)
    delta_p2_values = [float(row["delta_p2"]) for row in rows]

    neg_count = sum(1 for x in delta_p2_values if x < 0)
    pos_count = sum(1 for x in delta_p2_values if x > 0)
    large_neg_count = sum(1 for x in delta_p2_values if x <= thresholds.large_negative_threshold)
    compact_neg_count = sum(
        1 for x in delta_p2_values
        if thresholds.compact_negative_lower < x < thresholds.compact_negative_upper
    )

    neg_frac = safe_fraction(neg_count, total)
    pos_frac = safe_fraction(pos_count, total)
    large_neg_frac = safe_fraction(large_neg_count, total)
    compact_neg_frac = safe_fraction(compact_neg_count, total)
    mean_delta_p2 = mean(delta_p2_values) if delta_p2_values else 0.0
    min_delta_p2 = min(delta_p2_values) if delta_p2_values else 0.0
    abs_min_delta_p2 = abs(min_delta_p2)

    if (
        abs(mean_delta_p2) <= thresholds.symmetry_mean_tolerance
        and abs(neg_frac - pos_frac) <= thresholds.symmetry_balance_tolerance
    ):
        confidence = 1.0 - min(
            1.0,
            abs(neg_frac - pos_frac)
            + abs(mean_delta_p2) / max(thresholds.symmetry_mean_tolerance, 1e-12),
        )
        return labels["control_symmetric"], max(0.0, confidence)

    if (
        compact_neg_frac >= thresholds.min_compact_negative_fraction
        and (compact_neg_frac - large_neg_frac) >= thresholds.compact_dominance_margin
        and abs_min_delta_p2 < thresholds.compact_extreme_guard
        and neg_frac > pos_frac
    ):
        confidence = min(1.0, 0.55 + compact_neg_frac)
        return labels["compact_negative_candidate"], confidence

    if (
        large_neg_frac >= thresholds.min_large_negative_fraction
        and abs_min_delta_p2 >= thresholds.large_negative_extreme_guard
        and neg_frac > pos_frac
    ):
        confidence = min(1.0, 0.55 + large_neg_frac)
        return labels["large_negative_candidate"], confidence

    if pos_frac >= thresholds.min_positive_fraction and pos_frac > neg_frac:
        confidence = min(1.0, 0.5 + pos_frac)
        return labels["positive_mixed_candidate"], confidence

    return labels["weak_or_ambiguous"], 0.25


def summarize_family(
    family: FamilyDefinition,
    pair_rows: list[dict[str, Any]],
    thresholds: Thresholds,
    labels: dict[str, str],
) -> dict[str, Any]:
    delta_p2_values = [float(row["delta_p2"]) for row in pair_rows]
    total = len(pair_rows)

    neg_count = sum(1 for x in delta_p2_values if x < 0)
    pos_count = sum(1 for x in delta_p2_values if x > 0)
    zero_count = sum(1 for x in delta_p2_values if x == 0)
    large_neg_count = sum(1 for x in delta_p2_values if x <= thresholds.large_negative_threshold)
    compact_neg_count = sum(1 for x in delta_p2_values if thresholds.compact_negative_lower < x < thresholds.compact_negative_upper)

    suggested_type, confidence = suggest_type(pair_rows, thresholds, labels)
    screen_pass_flag = int(
        suggested_type in {
            labels["control_symmetric"],
            labels["large_negative_candidate"],
            labels["compact_negative_candidate"],
        }
        and confidence >= thresholds.min_type_confidence
    )

    return {
        "family_id": family.family_id,
        "description": family.description,
        "expected_type": family.expected_type,
        "n_pairs_total": total,
        "delta_p2_negative_fraction": safe_fraction(neg_count, total),
        "delta_p2_positive_fraction": safe_fraction(pos_count, total),
        "delta_p2_zero_fraction": safe_fraction(zero_count, total),
        "min_delta_p2": min(delta_p2_values) if delta_p2_values else 0.0,
        "max_delta_p2": max(delta_p2_values) if delta_p2_values else 0.0,
        "mean_delta_p2": mean(delta_p2_values) if delta_p2_values else 0.0,
        "median_delta_p2": median(delta_p2_values) if delta_p2_values else 0.0,
        "large_negative_fraction": safe_fraction(large_neg_count, total),
        "compact_negative_fraction": safe_fraction(compact_neg_count, total),
        "positive_fraction": safe_fraction(pos_count, total),
        "suggested_type": suggested_type,
        "type_confidence": confidence,
        "screen_pass_flag": screen_pass_flag,
    }


def build_expanded_definition_rows(families: list[FamilyDefinition]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in families:
        p_values = list(family.p_values)
        rows.append(
            {
                "family_id": family.family_id,
                "description": family.description,
                "expected_type": family.expected_type,
                "n_modes": len(p_values),
                "p_min": min(p_values),
                "p_max": max(p_values),
                "p_span": max(p_values) - min(p_values),
                "p_values_serialized": json.dumps(p_values, ensure_ascii=False),
                "notes": family.notes,
            }
        )
    return rows


def build_global_summary(
    family_summaries: list[dict[str, Any]],
    labels: dict[str, str],
    selection: SelectionRules,
) -> dict[str, Any]:
    passed = [row for row in family_summaries if int(row["screen_pass_flag"]) == 1]
    failed = [row for row in family_summaries if int(row["screen_pass_flag"]) == 0]

    def best_of(label: str) -> str | None:
        matches = [row for row in family_summaries if row["suggested_type"] == label]
        if not matches:
            return None
        matches.sort(key=lambda row: float(row["type_confidence"]), reverse=True)
        return str(matches[0]["family_id"])

    required_ok = True
    if selection.require_control_family:
        required_ok = required_ok and best_of(labels["control_symmetric"]) is not None
    if selection.require_large_negative_family:
        required_ok = required_ok and best_of(labels["large_negative_candidate"]) is not None
    if selection.require_compact_negative_family:
        required_ok = required_ok and best_of(labels["compact_negative_candidate"]) is not None

    pass_flag = int(required_ok and len(failed) <= selection.max_failed_families_for_pass)

    return {
        "n_families_total": len(family_summaries),
        "n_screen_pass": len(passed),
        "n_screen_failed": len(failed),
        "family_ids_passed": [row["family_id"] for row in passed],
        "family_ids_failed": [row["family_id"] for row in failed],
        "best_control_family": best_of(labels["control_symmetric"]),
        "best_large_negative_candidate": best_of(labels["large_negative_candidate"]),
        "best_compact_negative_candidate": best_of(labels["compact_negative_candidate"]),
        "best_positive_mixed_candidate": best_of(labels["positive_mixed_candidate"]),
        "precheck_pass_flag": pass_flag,
        "notes": "Precheck evaluates asymmetry-type suitability, not full mechanism proof.",
    }


def build_report(
    family_summaries: list[dict[str, Any]],
    global_summary: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.append("# M.3.9a.1 — Family Invariance Precheck Report")
    lines.append("")
    lines.append("## Global summary")
    lines.append("")
    lines.append(f"- Families total: {global_summary['n_families_total']}")
    lines.append(f"- Screen pass: {global_summary['n_screen_pass']}")
    lines.append(f"- Screen failed: {global_summary['n_screen_failed']}")
    lines.append(f"- Best control family: {global_summary['best_control_family']}")
    lines.append(f"- Best large-negative candidate: {global_summary['best_large_negative_candidate']}")
    lines.append(f"- Best compact-negative candidate: {global_summary['best_compact_negative_candidate']}")
    lines.append(f"- Precheck pass flag: {global_summary['precheck_pass_flag']}")
    lines.append("")
    lines.append("## Family summaries")
    lines.append("")
    for row in family_summaries:
        lines.append(f"### {row['family_id']}")
        lines.append(f"- expected_type: {row['expected_type']}")
        lines.append(f"- suggested_type: {row['suggested_type']}")
        lines.append(f"- type_confidence: {row['type_confidence']:.3f}")
        lines.append(f"- negative_fraction: {row['delta_p2_negative_fraction']:.3f}")
        lines.append(f"- positive_fraction: {row['delta_p2_positive_fraction']:.3f}")
        lines.append(f"- large_negative_fraction: {row['large_negative_fraction']:.3f}")
        lines.append(f"- compact_negative_fraction: {row['compact_negative_fraction']:.3f}")
        lines.append(f"- min_delta_p2: {row['min_delta_p2']}")
        lines.append(f"- max_delta_p2: {row['max_delta_p2']}")
        lines.append(f"- screen_pass_flag: {row['screen_pass_flag']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    config_path = (project_root / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config)

    cfg = load_config(config_path)
    family_path = (project_root / cfg.family_definitions_path).resolve()
    families = load_family_definitions(family_path, cfg.thresholds)

    output_root = (project_root / cfg.output.root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    expanded_rows = build_expanded_definition_rows(families)

    all_pair_rows: list[dict[str, Any]] = []
    family_summaries: list[dict[str, Any]] = []

    for family in families:
        pair_rows = generate_pair_rows(family, cfg.thresholds)
        all_pair_rows.extend(pair_rows)
        family_summaries.append(summarize_family(family, pair_rows, cfg.thresholds, cfg.labels))

    global_summary = build_global_summary(family_summaries, cfg.labels, cfg.selection)
    report = build_report(family_summaries, global_summary)

    write_csv(
        output_root / cfg.output.family_definitions_expanded,
        expanded_rows,
        fieldnames=[
            "family_id",
            "description",
            "expected_type",
            "n_modes",
            "p_min",
            "p_max",
            "p_span",
            "p_values_serialized",
            "notes",
        ],
    )

    write_csv(
        output_root / cfg.output.family_pair_class_screen,
        all_pair_rows,
        fieldnames=[
            "family_id",
            "pair_i",
            "pair_j",
            "p_i",
            "p_j",
            "delta_p",
            "delta_p_abs",
            "delta_p2",
            "sum_p",
            "mean_p",
            "delta_p2_bucket",
        ],
    )

    write_csv(
        output_root / cfg.output.family_type_summary,
        family_summaries,
        fieldnames=[
            "family_id",
            "description",
            "expected_type",
            "n_pairs_total",
            "delta_p2_negative_fraction",
            "delta_p2_positive_fraction",
            "delta_p2_zero_fraction",
            "min_delta_p2",
            "max_delta_p2",
            "mean_delta_p2",
            "median_delta_p2",
            "large_negative_fraction",
            "compact_negative_fraction",
            "positive_fraction",
            "suggested_type",
            "type_confidence",
            "screen_pass_flag",
        ],
    )

    write_json(output_root / cfg.output.family_type_precheck, global_summary)
    write_text(output_root / cfg.output.family_invariance_precheck_report, report)

    print(f"M.3.9a.1 completed. Output written to: {output_root}")


if __name__ == "__main__":
    main()
