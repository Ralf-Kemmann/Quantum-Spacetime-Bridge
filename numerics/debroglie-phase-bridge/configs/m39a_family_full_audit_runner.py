cat > src/m39a_family_full_audit_runner.py <<'EOF'
#!/usr/bin/env python3
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
class FamilySelection:
    include_families: list[str]
    family_roles: dict[str, str]


@dataclass(frozen=True)
class AuditSwitches:
    run_pair_identity_audit: bool
    run_delta_p_audit: bool
    run_delta_p2_audit: bool
    run_diversity_control: bool
    run_sigma_light: bool
    run_matched_pair_analysis: bool
    run_f5_falsification_check: bool
    run_alpha_interpretation_block: bool


@dataclass(frozen=True)
class DiversityConfig:
    enabled: bool
    modes: list[str]


@dataclass(frozen=True)
class SigmaLightConfig:
    enabled: bool
    sigma_p_values: list[float]


@dataclass(frozen=True)
class MatchedPairsConfig:
    enabled: bool
    source_families: list[str]
    target_families: list[str]
    relative_delta_p2_tolerance: float
    absolute_delta_p2_tolerance: float
    require_same_sign_delta_p2: bool
    choose_best_match_only: bool
    min_matches_required: int


@dataclass(frozen=True)
class FalsificationConfig:
    enabled: bool
    family_id: str
    max_branch_match_frac: float
    max_identity_strength: float
    max_delta_p2_dominance: float
    require_weaker_than_f2: bool
    require_weaker_than_f3: bool
    require_weaker_than_f4: bool


@dataclass(frozen=True)
class AlphaInterpretationConfig:
    enabled: bool
    reference_alpha: float
    interpretation_mode: dict[str, str]


@dataclass(frozen=True)
class Thresholds:
    min_family_pass_confidence: float
    min_global_pass_fraction: float
    control_max_branch_strength: float
    delta_p2_min_dominance_margin: float


@dataclass(frozen=True)
class OutputSpec:
    root: str
    family_audit_case_table: str
    family_audit_pair_summary: str
    family_audit_class_summary: str
    family_audit_global_summary: str
    family_audit_branch_summary: str
    family_matched_pair_summary: str
    family_matched_pair_branch_compare: str
    family_f5_falsification_summary: str
    family_alpha_interpretation_notes: str
    family_audit_report: str


@dataclass(frozen=True)
class Config:
    family_definitions_path: str
    family_selection: FamilySelection
    audit: AuditSwitches
    diversity: DiversityConfig
    sigma_light: SigmaLightConfig
    matched_pairs: MatchedPairsConfig
    falsification: FalsificationConfig
    alpha_interpretation: AlphaInterpretationConfig
    thresholds: Thresholds
    outputs: OutputSpec


class ConfigError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="M.3.9a.2 family full audit")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
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
    block = ensure_dict(raw.get("m39a_family_full_audit"), "m39a_family_full_audit")

    input_block = ensure_dict(block.get("input"), "input")
    family_selection_block = ensure_dict(block.get("family_selection"), "family_selection")
    audit_block = ensure_dict(block.get("audit"), "audit")
    diversity_block = ensure_dict(block.get("diversity"), "diversity")
    sigma_light_block = ensure_dict(block.get("sigma_light"), "sigma_light")
    matched_pairs_block = ensure_dict(block.get("matched_pairs"), "matched_pairs")
    falsification_block = ensure_dict(block.get("falsification"), "falsification")
    alpha_block = ensure_dict(block.get("alpha_interpretation"), "alpha_interpretation")
    thresholds_block = ensure_dict(block.get("thresholds"), "thresholds")
    outputs_block = ensure_dict(block.get("outputs"), "outputs")

    family_selection = FamilySelection(
        include_families=[str(x) for x in ensure_list(family_selection_block.get("include_families"), "family_selection.include_families")],
        family_roles={str(k): str(v) for k, v in ensure_dict(family_selection_block.get("family_roles"), "family_selection.family_roles").items()},
    )

    audit = AuditSwitches(
        run_pair_identity_audit=bool(audit_block.get("run_pair_identity_audit", True)),
        run_delta_p_audit=bool(audit_block.get("run_delta_p_audit", True)),
        run_delta_p2_audit=bool(audit_block.get("run_delta_p2_audit", True)),
        run_diversity_control=bool(audit_block.get("run_diversity_control", True)),
        run_sigma_light=bool(audit_block.get("run_sigma_light", True)),
        run_matched_pair_analysis=bool(audit_block.get("run_matched_pair_analysis", True)),
        run_f5_falsification_check=bool(audit_block.get("run_f5_falsification_check", True)),
        run_alpha_interpretation_block=bool(audit_block.get("run_alpha_interpretation_block", True)),
    )

    diversity = DiversityConfig(
        enabled=bool(diversity_block.get("enabled", True)),
        modes=[str(x) for x in ensure_list(diversity_block.get("modes"), "diversity.modes")],
    )

    sigma_light = SigmaLightConfig(
        enabled=bool(sigma_light_block.get("enabled", True)),
        sigma_p_values=[stable_float(x, "sigma_light.sigma_p_values") for x in ensure_list(sigma_light_block.get("sigma_p_values"), "sigma_light.sigma_p_values")],
    )

    matched_pairs = MatchedPairsConfig(
        enabled=bool(matched_pairs_block.get("enabled", True)),
        source_families=[str(x) for x in ensure_list(matched_pairs_block.get("source_families"), "matched_pairs.source_families")],
        target_families=[str(x) for x in ensure_list(matched_pairs_block.get("target_families"), "matched_pairs.target_families")],
        relative_delta_p2_tolerance=stable_float(matched_pairs_block.get("relative_delta_p2_tolerance"), "matched_pairs.relative_delta_p2_tolerance"),
        absolute_delta_p2_tolerance=stable_float(matched_pairs_block.get("absolute_delta_p2_tolerance"), "matched_pairs.absolute_delta_p2_tolerance"),
        require_same_sign_delta_p2=bool(matched_pairs_block.get("require_same_sign_delta_p2", True)),
        choose_best_match_only=bool(matched_pairs_block.get("choose_best_match_only", True)),
        min_matches_required=stable_int(matched_pairs_block.get("min_matches_required", 3), "matched_pairs.min_matches_required"),
    )

    falsification = FalsificationConfig(
        enabled=bool(falsification_block.get("enabled", True)),
        family_id=str(falsification_block.get("family_id")),
        max_branch_match_frac=stable_float(falsification_block.get("max_branch_match_frac"), "falsification.max_branch_match_frac"),
        max_identity_strength=stable_float(falsification_block.get("max_identity_strength"), "falsification.max_identity_strength"),
        max_delta_p2_dominance=stable_float(falsification_block.get("max_delta_p2_dominance"), "falsification.max_delta_p2_dominance"),
        require_weaker_than_f2=bool(falsification_block.get("require_weaker_than_f2", True)),
        require_weaker_than_f3=bool(falsification_block.get("require_weaker_than_f3", True)),
        require_weaker_than_f4=bool(falsification_block.get("require_weaker_than_f4", True)),
    )

    alpha_interpretation = AlphaInterpretationConfig(
        enabled=bool(alpha_block.get("enabled", True)),
        reference_alpha=stable_float(alpha_block.get("reference_alpha", 1.0), "alpha_interpretation.reference_alpha"),
        interpretation_mode={str(k): str(v) for k, v in ensure_dict(alpha_block.get("interpretation_mode"), "alpha_interpretation.interpretation_mode").items()},
    )

    thresholds = Thresholds(
        min_family_pass_confidence=stable_float(thresholds_block.get("min_family_pass_confidence", 0.5), "thresholds.min_family_pass_confidence"),
        min_global_pass_fraction=stable_float(thresholds_block.get("min_global_pass_fraction", 0.75), "thresholds.min_global_pass_fraction"),
        control_max_branch_strength=stable_float(thresholds_block.get("control_max_branch_strength", 0.55), "thresholds.control_max_branch_strength"),
        delta_p2_min_dominance_margin=stable_float(thresholds_block.get("delta_p2_min_dominance_margin", 0.05), "thresholds.delta_p2_min_dominance_margin"),
    )

    outputs = OutputSpec(
        root=str(outputs_block.get("root")),
        family_audit_case_table=str(outputs_block.get("family_audit_case_table")),
        family_audit_pair_summary=str(outputs_block.get("family_audit_pair_summary")),
        family_audit_class_summary=str(outputs_block.get("family_audit_class_summary")),
        family_audit_global_summary=str(outputs_block.get("family_audit_global_summary")),
        family_audit_branch_summary=str(outputs_block.get("family_audit_branch_summary")),
        family_matched_pair_summary=str(outputs_block.get("family_matched_pair_summary")),
        family_matched_pair_branch_compare=str(outputs_block.get("family_matched_pair_branch_compare")),
        family_f5_falsification_summary=str(outputs_block.get("family_f5_falsification_summary")),
        family_alpha_interpretation_notes=str(outputs_block.get("family_alpha_interpretation_notes")),
        family_audit_report=str(outputs_block.get("family_audit_report")),
    )

    family_definitions_path = str(input_block.get("family_definitions"))
    if not family_definitions_path:
        raise ConfigError("input.family_definitions must be provided")

    return Config(
        family_definitions_path=family_definitions_path,
        family_selection=family_selection,
        audit=audit,
        diversity=diversity,
        sigma_light=sigma_light,
        matched_pairs=matched_pairs,
        falsification=falsification,
        alpha_interpretation=alpha_interpretation,
        thresholds=thresholds,
        outputs=outputs,
    )


def load_family_definitions(path: Path, include_families: list[str]) -> list[FamilyDefinition]:
    raw = ensure_dict(load_yaml(path), f"family definitions file {path}")
    raw_families = ensure_list(raw.get("families"), "families")
    result: list[FamilyDefinition] = []
    seen_ids: set[str] = set()

    for index, raw_family in enumerate(raw_families, start=1):
        family = ensure_dict(raw_family, f"families[{index}]")
        family_id = str(family.get("family_id", "")).strip()
        if not family_id:
            raise ConfigError(f"families[{index}] is missing family_id")
        if family_id in seen_ids:
            raise ConfigError(f"Duplicate family_id detected: {family_id}")
        seen_ids.add(family_id)
        if family_id not in include_families:
            continue

        p_values_raw = ensure_list(family.get("p_values"), f"families[{index}].p_values")
        p_values = tuple(sorted(stable_float(v, f"families[{index}].p_values") for v in p_values_raw))
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
        raise ConfigError("No included families were found in the family definition file")

    return result


def classify_delta_p2_bucket(delta_p2: float) -> str:
    if delta_p2 < -10:
        return "large_negative"
    if -10 < delta_p2 < 0:
        return "compact_negative"
    if delta_p2 == 0:
        return "zero"
    return "positive"


def generate_pair_rows(family: FamilyDefinition, family_role: str, sigma_values: list[float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    p_vals = family.p_values
    sigma_mean = mean(sigma_values) if sigma_values else 1.0
    for i in range(len(p_vals)):
        for j in range(i + 1, len(p_vals)):
            p_i = p_vals[i]
            p_j = p_vals[j]
            delta_p = p_i - p_j
            delta_p2 = p_i**2 - p_j**2

            branch_identity = classify_delta_p2_bucket(delta_p2)
            if branch_identity == "zero":
                branch_identity = "control_like"

            identity_strength = min(1.0, abs(delta_p2) / 20.0)
            branch_match_frac = min(1.0, 0.35 + 0.5 * identity_strength)
            sigma_light_score = max(0.0, identity_strength / max(sigma_mean, 1e-12))

            rows.append(
                {
                    "family_id": family.family_id,
                    "family_role": family_role,
                    "pair_i": i,
                    "pair_j": j,
                    "p_i": p_i,
                    "p_j": p_j,
                    "delta_p": delta_p,
                    "delta_p_abs": abs(delta_p),
                    "delta_p2": delta_p2,
                    "delta_p2_abs": abs(delta_p2),
                    "sum_p": p_i + p_j,
                    "mean_p": (p_i + p_j) / 2.0,
                    "delta_p2_bucket": classify_delta_p2_bucket(delta_p2),
                    "branch_identity": branch_identity,
                    "identity_strength": identity_strength,
                    "branch_match_frac": branch_match_frac,
                    "sigma_light_score": sigma_light_score,
                }
            )
    return rows


def summarize_family_pairs(family: FamilyDefinition, family_role: str, pair_rows: list[dict[str, Any]], thresholds: Thresholds) -> dict[str, Any]:
    total = len(pair_rows)
    delta_p2_values = [float(r["delta_p2"]) for r in pair_rows]
    identity_strength_values = [float(r["identity_strength"]) for r in pair_rows]
    branch_match_values = [float(r["branch_match_frac"]) for r in pair_rows]

    pair_strength = mean([min(1.0, abs(float(r["delta_p"])) / 6.0) for r in pair_rows]) if pair_rows else 0.0
    delta_p_strength = mean([min(1.0, abs(float(r["delta_p"])) / 8.0) for r in pair_rows]) if pair_rows else 0.0
    delta_p2_strength = mean(identity_strength_values) if identity_strength_values else 0.0

    dominance_margin = delta_p2_strength - max(pair_strength, delta_p_strength)
    dominant_level = "delta_p2" if dominance_margin >= thresholds.delta_p2_min_dominance_margin else (
        "pair" if pair_strength >= delta_p_strength else "delta_p"
    )

    control_alert = int(family_role == "control" and mean(branch_match_values) > thresholds.control_max_branch_strength)

    return {
        "family_id": family.family_id,
        "family_role": family_role,
        "description": family.description,
        "expected_type": family.expected_type,
        "n_pairs_total": total,
        "min_delta_p2": min(delta_p2_values) if delta_p2_values else 0.0,
        "max_delta_p2": max(delta_p2_values) if delta_p2_values else 0.0,
        "mean_delta_p2": mean(delta_p2_values) if delta_p2_values else 0.0,
        "median_delta_p2": median(delta_p2_values) if delta_p2_values else 0.0,
        "mean_identity_strength": mean(identity_strength_values) if identity_strength_values else 0.0,
        "mean_branch_match_frac": mean(branch_match_values) if branch_match_values else 0.0,
        "pair_strength": pair_strength,
        "delta_p_strength": delta_p_strength,
        "delta_p2_strength": delta_p2_strength,
        "delta_p2_dominance_margin": dominance_margin,
        "dominant_level": dominant_level,
        "control_alert_flag": control_alert,
        "family_pass_flag": int(dominant_level == "delta_p2" and control_alert == 0),
    }


def build_class_summary(family_summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in family_summary_rows:
        rows.extend([
            {
                "family_id": row["family_id"],
                "family_role": row["family_role"],
                "measure_level": "pair",
                "strength": row["pair_strength"],
                "rank_score": row["pair_strength"],
                "dominant_flag": int(row["dominant_level"] == "pair"),
            },
            {
                "family_id": row["family_id"],
                "family_role": row["family_role"],
                "measure_level": "delta_p",
                "strength": row["delta_p_strength"],
                "rank_score": row["delta_p_strength"],
                "dominant_flag": int(row["dominant_level"] == "delta_p"),
            },
            {
                "family_id": row["family_id"],
                "family_role": row["family_role"],
                "measure_level": "delta_p2",
                "strength": row["delta_p2_strength"],
                "rank_score": row["delta_p2_strength"],
                "dominant_flag": int(row["dominant_level"] == "delta_p2"),
            },
        ])
    return rows


def sign_of(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def find_best_matches(
    source_rows: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    cfg: MatchedPairsConfig,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []

    for src in source_rows:
        src_val = float(src["delta_p2"])
        src_abs = abs(src_val)
        candidates: list[dict[str, Any]] = []

        for tgt in target_rows:
            tgt_val = float(tgt["delta_p2"])
            tgt_abs = abs(tgt_val)

            if cfg.require_same_sign_delta_p2 and sign_of(src_val) != sign_of(tgt_val):
                continue

            abs_diff = abs(src_val - tgt_val)
            rel_diff = abs_diff / max(src_abs, tgt_abs, 1e-12)

            if rel_diff <= cfg.relative_delta_p2_tolerance or abs_diff <= cfg.absolute_delta_p2_tolerance:
                candidates.append(
                    {
                        "source_family": src["family_id"],
                        "target_family": tgt["family_id"],
                        "source_pair": f"{src['pair_i']}-{src['pair_j']}",
                        "target_pair": f"{tgt['pair_i']}-{tgt['pair_j']}",
                        "source_delta_p2": src_val,
                        "target_delta_p2": tgt_val,
                        "relative_delta_p2_diff": rel_diff,
                        "absolute_delta_p2_diff": abs_diff,
                        "source_branch_identity": src["branch_identity"],
                        "target_branch_identity": tgt["branch_identity"],
                        "same_branch_flag": int(src["branch_identity"] == tgt["branch_identity"]),
                    }
                )

        if not candidates:
            continue

        candidates.sort(key=lambda row: (row["relative_delta_p2_diff"], row["absolute_delta_p2_diff"]))
        if cfg.choose_best_match_only:
            matches.append(candidates[0])
        else:
            matches.extend(candidates)

    return matches


def aggregate_matched_pairs(matches: list[dict[str, Any]], min_matches_required: int) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in matches:
        key = (str(row["source_family"]), str(row["target_family"]))
        grouped.setdefault(key, []).append(row)

    out: list[dict[str, Any]] = []
    for (source_family, target_family), rows in grouped.items():
        n = len(rows)
        same_frac = mean([float(r["same_branch_flag"]) for r in rows]) if rows else 0.0
        different_frac = 1.0 - same_frac
        if n < min_matches_required:
            label = "insufficient_matches"
        elif same_frac >= 0.7:
            label = "same_branch_dominance"
        elif different_frac >= 0.7:
            label = "different_branch_dominance"
        else:
            label = "mixed_or_unclear"

        out.append(
            {
                "source_family": source_family,
                "target_family": target_family,
                "n_matched_pairs": n,
                "same_branch_fraction": same_frac,
                "different_branch_fraction": different_frac,
                "interpretive_label": label,
            }
        )

    return out


def build_f5_falsification_summary(
    family_summary_rows: list[dict[str, Any]],
    cfg: FalsificationConfig,
) -> list[dict[str, Any]]:
    target = next((r for r in family_summary_rows if r["family_id"] == cfg.family_id), None)
    if target is None:
        raise ConfigError(f"Falsification family {cfg.family_id} was not found in family summaries")

    weaker_refs = []
    for family_id in ("F2", "F3", "F4"):
        ref = next((r for r in family_summary_rows if r["family_id"] == family_id), None)
        if ref is not None:
            weaker_refs.append(float(target["mean_branch_match_frac"]) < float(ref["mean_branch_match_frac"]))

    weaker_than_refs = all(weaker_refs) if weaker_refs else True
    alert_flag = int(
        float(target["mean_branch_match_frac"]) > cfg.max_branch_match_frac
        or float(target["mean_identity_strength"]) > cfg.max_identity_strength
        or float(target["delta_p2_strength"]) > cfg.max_delta_p2_dominance
        or not weaker_than_refs
    )

    return [{
        "family_id": target["family_id"],
        "predicted_weak_flag": 1,
        "observed_branch_match_frac": target["mean_branch_match_frac"],
        "observed_identity_strength": target["mean_identity_strength"],
        "observed_delta_p2_dominance": target["delta_p2_strength"],
        "weaker_than_f2_f3_f4_flag": int(weaker_than_refs),
        "falsification_alert_flag": alert_flag,
    }]


def build_alpha_notes(cfg: AlphaInterpretationConfig) -> str:
    lines = [
        "# Alpha interpretation notes",
        "",
        f"- reference_alpha: {cfg.reference_alpha}",
        f"- alpha_eq_1 interpretation: {cfg.interpretation_mode.get('alpha_eq_1', 'not specified')}",
        f"- alpha_ne_1 interpretation: {cfg.interpretation_mode.get('alpha_ne_1', 'not specified')}",
        "",
        "Interpretation rule:",
        "",
        "- For alpha = 1, delta_p2 may be read as directly proportional to a kinetic-energy difference in the free quadratic reference picture.",
        "- For alpha != 1, delta_p2 remains a quadratic momentum-space difference, but the direct energy reading no longer transfers naively unchanged.",
        "",
    ]
    return "\n".join(lines)


def build_global_summary(
    family_summary_rows: list[dict[str, Any]],
    matched_pair_compare_rows: list[dict[str, Any]],
    f5_rows: list[dict[str, Any]],
    thresholds: Thresholds,
) -> dict[str, Any]:
    pass_flags = [int(r["family_pass_flag"]) for r in family_summary_rows]
    pass_fraction = mean(pass_flags) if pass_flags else 0.0
    delta_p2_dominant_count = sum(1 for r in family_summary_rows if r["dominant_level"] == "delta_p2")
    control_alerts = [r["family_id"] for r in family_summary_rows if int(r["control_alert_flag"]) == 1]
    f5_alert = int(f5_rows[0]["falsification_alert_flag"]) if f5_rows else 0
    matched_interpretations = [r["interpretive_label"] for r in matched_pair_compare_rows]

    global_pass_flag = int(
        pass_fraction >= thresholds.min_global_pass_fraction
        and f5_alert == 0
        and not control_alerts
    )

    return {
        "n_families_total": len(family_summary_rows),
        "n_families_passed": sum(pass_flags),
        "family_pass_fraction": pass_fraction,
        "delta_p2_dominant_count": delta_p2_dominant_count,
        "control_alert_families": control_alerts,
        "matched_pair_interpretations": matched_interpretations,
        "f5_falsification_alert_flag": f5_alert,
        "global_pass_flag": global_pass_flag,
        "notes": "M.3.9a.2 evaluates family-wise dominance, matched-pair comparison, and F5 falsification behavior.",
    }


def build_case_table(family_summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in family_summary_rows:
        rows.append({
            "family_id": row["family_id"],
            "family_role": row["family_role"],
            "expected_type": row["expected_type"],
            "audit_mode": "full_audit",
            "dominant_level": row["dominant_level"],
            "mean_branch_match_frac": row["mean_branch_match_frac"],
            "mean_identity_strength": row["mean_identity_strength"],
            "family_pass_flag": row["family_pass_flag"],
        })
    return rows


def build_report(
    family_summary_rows: list[dict[str, Any]],
    matched_pair_compare_rows: list[dict[str, Any]],
    f5_rows: list[dict[str, Any]],
    global_summary: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.append("# M.3.9a.2 — Family Full Audit Report")
    lines.append("")
    lines.append("## Global summary")
    lines.append("")
    lines.append(f"- Families total: {global_summary['n_families_total']}")
    lines.append(f"- Families passed: {global_summary['n_families_passed']}")
    lines.append(f"- Family pass fraction: {global_summary['family_pass_fraction']:.3f}")
    lines.append(f"- delta_p2-dominant families: {global_summary['delta_p2_dominant_count']}")
    lines.append(f"- F5 falsification alert: {global_summary['f5_falsification_alert_flag']}")
    lines.append(f"- Global pass flag: {global_summary['global_pass_flag']}")
    lines.append("")
    lines.append("## Family summaries")
    lines.append("")
    for row in family_summary_rows:
        lines.append(f"### {row['family_id']} ({row['family_role']})")
        lines.append(f"- expected_type: {row['expected_type']}")
        lines.append(f"- dominant_level: {row['dominant_level']}")
        lines.append(f"- mean_branch_match_frac: {row['mean_branch_match_frac']:.3f}")
        lines.append(f"- mean_identity_strength: {row['mean_identity_strength']:.3f}")
        lines.append(f"- delta_p2_strength: {row['delta_p2_strength']:.3f}")
        lines.append(f"- family_pass_flag: {row['family_pass_flag']}")
        lines.append("")
    lines.append("## Matched-pair comparison")
    lines.append("")
    if matched_pair_compare_rows:
        for row in matched_pair_compare_rows:
            lines.append(f"- {row['source_family']} vs {row['target_family']}: n={row['n_matched_pairs']}, same_branch_fraction={row['same_branch_fraction']:.3f}, label={row['interpretive_label']}")
    else:
        lines.append("- No matched-pair results available.")
    lines.append("")
    lines.append("## F5 falsification")
    lines.append("")
    if f5_rows:
        row = f5_rows[0]
        lines.append(f"- family_id: {row['family_id']}")
        lines.append(f"- observed_branch_match_frac: {float(row['observed_branch_match_frac']):.3f}")
        lines.append(f"- observed_identity_strength: {float(row['observed_identity_strength']):.3f}")
        lines.append(f"- falsification_alert_flag: {row['falsification_alert_flag']}")
    else:
        lines.append("- No F5 falsification output available.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    config_path = (project_root / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config)

    cfg = load_config(config_path)
    family_definitions_path = (project_root / cfg.family_definitions_path).resolve()
    families = load_family_definitions(family_definitions_path, cfg.family_selection.include_families)

    output_root = (project_root / cfg.outputs.root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    all_pair_rows: list[dict[str, Any]] = []
    family_summary_rows: list[dict[str, Any]] = []

    for family in families:
        family_role = cfg.family_selection.family_roles.get(family.family_id, "unclassified")
        pair_rows = generate_pair_rows(family, family_role, cfg.sigma_light.sigma_p_values)
        all_pair_rows.extend(pair_rows)
        family_summary_rows.append(summarize_family_pairs(family, family_role, pair_rows, cfg.thresholds))

    class_summary_rows = build_class_summary(family_summary_rows)
    case_table_rows = build_case_table(family_summary_rows)
    branch_summary_rows = [
        {
            "family_id": r["family_id"],
            "family_role": r["family_role"],
            "mean_branch_match_frac": r["mean_branch_match_frac"],
            "mean_identity_strength": r["mean_identity_strength"],
            "delta_p2_strength": r["delta_p2_strength"],
            "dominant_level": r["dominant_level"],
            "family_pass_flag": r["family_pass_flag"],
        }
        for r in family_summary_rows
    ]

    matched_pair_rows: list[dict[str, Any]] = []
    if cfg.audit.run_matched_pair_analysis and cfg.matched_pairs.enabled:
        for source_family in cfg.matched_pairs.source_families:
            source_rows = [r for r in all_pair_rows if r["family_id"] == source_family]
            for target_family in cfg.matched_pairs.target_families:
                target_rows = [r for r in all_pair_rows if r["family_id"] == target_family]
                matched_pair_rows.extend(find_best_matches(source_rows, target_rows, cfg.matched_pairs))

    matched_pair_compare_rows = aggregate_matched_pairs(matched_pair_rows, cfg.matched_pairs.min_matches_required)

    f5_rows: list[dict[str, Any]] = []
    if cfg.audit.run_f5_falsification_check and cfg.falsification.enabled:
        f5_rows = build_f5_falsification_summary(family_summary_rows, cfg.falsification)

    alpha_notes = build_alpha_notes(cfg.alpha_interpretation)
    global_summary = build_global_summary(family_summary_rows, matched_pair_compare_rows, f5_rows, cfg.thresholds)
    report = build_report(family_summary_rows, matched_pair_compare_rows, f5_rows, global_summary)

    write_csv(
        output_root / cfg.outputs.family_audit_case_table,
        case_table_rows,
        fieldnames=[
            "family_id",
            "family_role",
            "expected_type",
            "audit_mode",
            "dominant_level",
            "mean_branch_match_frac",
            "mean_identity_strength",
            "family_pass_flag",
        ],
    )

    write_csv(
        output_root / cfg.outputs.family_audit_pair_summary,
        all_pair_rows,
        fieldnames=[
            "family_id",
            "family_role",
            "pair_i",
            "pair_j",
            "p_i",
            "p_j",
            "delta_p",
            "delta_p_abs",
            "delta_p2",
            "delta_p2_abs",
            "sum_p",
            "mean_p",
            "delta_p2_bucket",
            "branch_identity",
            "identity_strength",
            "branch_match_frac",
            "sigma_light_score",
        ],
    )

    write_csv(
        output_root / cfg.outputs.family_audit_class_summary,
        class_summary_rows,
        fieldnames=[
            "family_id",
            "family_role",
            "measure_level",
            "strength",
            "rank_score",
            "dominant_flag",
        ],
    )

    write_json(output_root / cfg.outputs.family_audit_global_summary, global_summary)

    write_csv(
        output_root / cfg.outputs.family_audit_branch_summary,
        branch_summary_rows,
        fieldnames=[
            "family_id",
            "family_role",
            "mean_branch_match_frac",
            "mean_identity_strength",
            "delta_p2_strength",
            "dominant_level",
            "family_pass_flag",
        ],
    )

    write_csv(
        output_root / cfg.outputs.family_matched_pair_summary,
        matched_pair_rows,
        fieldnames=[
            "source_family",
            "target_family",
            "source_pair",
            "target_pair",
            "source_delta_p2",
            "target_delta_p2",
            "relative_delta_p2_diff",
            "absolute_delta_p2_diff",
            "source_branch_identity",
            "target_branch_identity",
            "same_branch_flag",
        ],
    )

    write_csv(
        output_root / cfg.outputs.family_matched_pair_branch_compare,
        matched_pair_compare_rows,
        fieldnames=[
            "source_family",
            "target_family",
            "n_matched_pairs",
            "same_branch_fraction",
            "different_branch_fraction",
            "interpretive_label",
        ],
    )

    write_csv(
        output_root / cfg.outputs.family_f5_falsification_summary,
        f5_rows,
        fieldnames=[
            "family_id",
            "predicted_weak_flag",
            "observed_branch_match_frac",
            "observed_identity_strength",
            "observed_delta_p2_dominance",
            "weaker_than_f2_f3_f4_flag",
            "falsification_alert_flag",
        ],
    )

    write_text(output_root / cfg.outputs.family_alpha_interpretation_notes, alpha_notes)
    write_text(output_root / cfg.outputs.family_audit_report, report)

    print(f"M.3.9a.2 completed. Output written to: {output_root}")


if __name__ == "__main__":
    main()
EOF