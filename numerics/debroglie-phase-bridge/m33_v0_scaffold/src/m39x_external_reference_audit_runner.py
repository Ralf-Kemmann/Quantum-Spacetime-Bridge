#!/usr/bin/env python3
"""
M.3.9x — External Reference Audit Runner
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable

import yaml


@dataclass(frozen=True)
class FamilySelection:
    include_families: list[str]
    family_roles: dict[str, str]


@dataclass(frozen=True)
class OperationalizationConfig:
    direct_momentum_label: str
    proxy_momentum_label: str
    normalization_enabled: bool
    normalization_mode: str
    normalization_epsilon: float
    ordering_mode: str
    tie_break_rule: str
    default_pairing_mode: str
    allow_family_specific_override: bool


@dataclass(frozen=True)
class AuditSwitches:
    run_delta_p_audit: bool
    run_delta_p2_audit: bool
    run_branch_summary: bool
    run_bias_check: bool
    run_source_notes: bool
    run_external_matched_pairs: bool


@dataclass(frozen=True)
class Thresholds:
    delta_p2_min_dominance_margin: float
    control_max_branch_strength: float
    min_candidate_branch_strength: float
    min_candidate_identity_strength: float
    min_global_pass_fraction: float


@dataclass(frozen=True)
class FamilyPassLogic:
    external_control_allow_pass_if_delta_p2_dominant: bool
    external_control_require_branch_match_frac_leq: float
    external_main_test_require_delta_p2_dominant: bool
    external_main_test_require_branch_match_frac_geq: float
    external_main_test_require_identity_strength_geq: float
    external_hard_bias_test_require_delta_p2_dominant: bool
    external_hard_bias_test_interpretation_mode: str
    external_hard_bias_test_record_pass_flag: bool


@dataclass(frozen=True)
class OutputSpec:
    root: str
    external_family_definitions_expanded: str
    external_family_pair_summary: str
    external_family_branch_summary: str
    external_family_global_summary: str
    external_family_bias_check_report: str
    external_family_source_notes: str
    external_family_matched_pair_summary: str
    external_family_matched_pair_compare: str


@dataclass(frozen=True)
class Config:
    external_families_path: str
    family_selection: FamilySelection
    operationalization: OperationalizationConfig
    audit: AuditSwitches
    thresholds: Thresholds
    family_pass_logic: FamilyPassLogic
    outputs: OutputSpec


@dataclass(frozen=True)
class ExternalFamilyDefinition:
    family_id: str
    family_type: str
    source_model: str
    description: str
    role_hint: str
    notes: str
    parameters: dict[str, Any]
    generation: dict[str, Any]
    ordering: dict[str, Any]
    pairing: dict[str, Any]
    mode_labels: list[str]


@dataclass(frozen=True)
class FamilyModeRecord:
    family_id: str
    family_type: str
    source_model: str
    role_hint: str
    mode_label: str
    index_tuple: str
    p_value: float | None
    p2_value: float
    is_direct_momentum: bool


class ConfigError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="M.3.9x external reference audit")
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
    block = ensure_dict(raw.get("m39x_external_reference_audit"), "m39x_external_reference_audit")

    input_block = ensure_dict(block.get("input"), "input")
    family_selection_block = ensure_dict(block.get("family_selection"), "family_selection")
    operationalization_block = ensure_dict(block.get("operationalization"), "operationalization")
    p_mode_block = ensure_dict(operationalization_block.get("p_mode"), "operationalization.p_mode")
    normalization_block = ensure_dict(operationalization_block.get("normalization"), "operationalization.normalization")
    ordering_block = ensure_dict(operationalization_block.get("ordering"), "operationalization.ordering")
    pairing_block = ensure_dict(operationalization_block.get("pairing"), "operationalization.pairing")
    audit_block = ensure_dict(block.get("audit"), "audit")
    thresholds_block = ensure_dict(block.get("thresholds"), "thresholds")
    pass_logic_block = ensure_dict(block.get("family_pass_logic"), "family_pass_logic")
    control_logic = ensure_dict(pass_logic_block.get("external_control"), "family_pass_logic.external_control")
    main_logic = ensure_dict(pass_logic_block.get("external_main_test"), "family_pass_logic.external_main_test")
    hard_logic = ensure_dict(pass_logic_block.get("external_hard_bias_test"), "family_pass_logic.external_hard_bias_test")
    outputs_block = ensure_dict(block.get("outputs"), "outputs")

    family_selection = FamilySelection(
        include_families=[str(x) for x in ensure_list(family_selection_block.get("include_families"), "family_selection.include_families")],
        family_roles={str(k): str(v) for k, v in ensure_dict(family_selection_block.get("family_roles"), "family_selection.family_roles").items()},
    )

    operationalization = OperationalizationConfig(
        direct_momentum_label=str(p_mode_block.get("direct_momentum_label")),
        proxy_momentum_label=str(p_mode_block.get("proxy_momentum_label")),
        normalization_enabled=bool(normalization_block.get("enabled", True)),
        normalization_mode=str(normalization_block.get("mode")),
        normalization_epsilon=stable_float(normalization_block.get("epsilon", 1e-12), "operationalization.normalization.epsilon"),
        ordering_mode=str(ordering_block.get("mode")),
        tie_break_rule=str(ordering_block.get("tie_break_rule")),
        default_pairing_mode=str(pairing_block.get("default_mode")),
        allow_family_specific_override=bool(pairing_block.get("allow_family_specific_override", True)),
    )

    audit = AuditSwitches(
        run_delta_p_audit=bool(audit_block.get("run_delta_p_audit", True)),
        run_delta_p2_audit=bool(audit_block.get("run_delta_p2_audit", True)),
        run_branch_summary=bool(audit_block.get("run_branch_summary", True)),
        run_bias_check=bool(audit_block.get("run_bias_check", True)),
        run_source_notes=bool(audit_block.get("run_source_notes", True)),
        run_external_matched_pairs=bool(audit_block.get("run_external_matched_pairs", False)),
    )

    thresholds = Thresholds(
        delta_p2_min_dominance_margin=stable_float(thresholds_block.get("delta_p2_min_dominance_margin", 0.05), "thresholds.delta_p2_min_dominance_margin"),
        control_max_branch_strength=stable_float(thresholds_block.get("control_max_branch_strength", 0.55), "thresholds.control_max_branch_strength"),
        min_candidate_branch_strength=stable_float(thresholds_block.get("min_candidate_branch_strength", 0.50), "thresholds.min_candidate_branch_strength"),
        min_candidate_identity_strength=stable_float(thresholds_block.get("min_candidate_identity_strength", 0.30), "thresholds.min_candidate_identity_strength"),
        min_global_pass_fraction=stable_float(thresholds_block.get("min_global_pass_fraction", 0.66), "thresholds.min_global_pass_fraction"),
    )

    family_pass_logic = FamilyPassLogic(
        external_control_allow_pass_if_delta_p2_dominant=bool(control_logic.get("allow_pass_if_delta_p2_dominant", True)),
        external_control_require_branch_match_frac_leq=stable_float(control_logic.get("require_branch_match_frac_leq", 0.55), "family_pass_logic.external_control.require_branch_match_frac_leq"),
        external_main_test_require_delta_p2_dominant=bool(main_logic.get("require_delta_p2_dominant", True)),
        external_main_test_require_branch_match_frac_geq=stable_float(main_logic.get("require_branch_match_frac_geq", 0.50), "family_pass_logic.external_main_test.require_branch_match_frac_geq"),
        external_main_test_require_identity_strength_geq=stable_float(main_logic.get("require_identity_strength_geq", 0.30), "family_pass_logic.external_main_test.require_identity_strength_geq"),
        external_hard_bias_test_require_delta_p2_dominant=bool(hard_logic.get("require_delta_p2_dominant", False)),
        external_hard_bias_test_interpretation_mode=str(hard_logic.get("interpretation_mode", "stress_test")),
        external_hard_bias_test_record_pass_flag=bool(hard_logic.get("record_pass_flag", True)),
    )

    outputs = OutputSpec(
        root=str(outputs_block.get("root")),
        external_family_definitions_expanded=str(outputs_block.get("external_family_definitions_expanded")),
        external_family_pair_summary=str(outputs_block.get("external_family_pair_summary")),
        external_family_branch_summary=str(outputs_block.get("external_family_branch_summary")),
        external_family_global_summary=str(outputs_block.get("external_family_global_summary")),
        external_family_bias_check_report=str(outputs_block.get("external_family_bias_check_report")),
        external_family_source_notes=str(outputs_block.get("external_family_source_notes")),
        external_family_matched_pair_summary=str(outputs_block.get("external_family_matched_pair_summary")),
        external_family_matched_pair_compare=str(outputs_block.get("external_family_matched_pair_compare")),
    )

    external_families_path = str(input_block.get("external_families", "")).strip()
    if not external_families_path:
        raise ConfigError("input.external_families must be provided")

    return Config(
        external_families_path=external_families_path,
        family_selection=family_selection,
        operationalization=operationalization,
        audit=audit,
        thresholds=thresholds,
        family_pass_logic=family_pass_logic,
        outputs=outputs,
    )


def load_external_family_definitions(path: Path, include_families: list[str]) -> list[ExternalFamilyDefinition]:
    raw = ensure_dict(load_yaml(path), f"external family definitions file {path}")
    raw_families = ensure_list(raw.get("families"), "families")
    seen_ids: set[str] = set()
    result: list[ExternalFamilyDefinition] = []

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

        result.append(
            ExternalFamilyDefinition(
                family_id=family_id,
                family_type=str(family.get("family_type", "")).strip(),
                source_model=str(family.get("source_model", "")).strip(),
                description=str(family.get("description", "")).strip(),
                role_hint=str(family.get("role_hint", "")).strip(),
                notes=str(family.get("notes", "")).strip(),
                parameters=ensure_dict(family.get("parameters", {}), f"families[{index}].parameters"),
                generation=ensure_dict(family.get("generation", {}), f"families[{index}].generation"),
                ordering=ensure_dict(family.get("ordering", {}), f"families[{index}].ordering"),
                pairing=ensure_dict(family.get("pairing", {}), f"families[{index}].pairing"),
                mode_labels=[str(x) for x in ensure_list(family.get("mode_labels", []), f"families[{index}].mode_labels")],
            )
        )

    if not result:
        raise ConfigError("No included external families were found in the family definition file")

    return result


def parse_mode_label(mode_label: str) -> tuple[int, ...]:
    values: list[int] = []
    for token in mode_label.split(","):
        part = token.strip()
        if "=" not in part:
            raise ConfigError(f"Mode label has invalid format: {mode_label!r}")
        _, rhs = part.split("=", 1)
        values.append(int(rhs))
    return tuple(values)


def ring_modes(family: ExternalFamilyDefinition) -> list[FamilyModeRecord]:
    p = family.parameters
    hbar = stable_float(p.get("hbar", 1.0), f"{family.family_id}.parameters.hbar")
    L = stable_float(p.get("L"), f"{family.family_id}.parameters.L")
    m_min = stable_int(p.get("m_min"), f"{family.family_id}.parameters.m_min")
    m_max = stable_int(p.get("m_max"), f"{family.family_id}.parameters.m_max")
    exclude_zero_mode = bool(p.get("exclude_zero_mode", False))
    mode_labels = family.mode_labels or [f"m={m}" for m in range(m_min, m_max + 1)]
    out: list[FamilyModeRecord] = []
    for label in mode_labels:
        (m,) = parse_mode_label(label)
        if exclude_zero_mode and m == 0:
            continue
        p_value = hbar * 2.0 * math.pi * m / L
        out.append(FamilyModeRecord(family.family_id, family.family_type, family.source_model, family.role_hint, label, str((m,)), p_value, p_value * p_value, True))
    return out


def cavity_modes(family: ExternalFamilyDefinition) -> list[FamilyModeRecord]:
    p = family.parameters
    hbar = stable_float(p.get("hbar", 1.0), f"{family.family_id}.parameters.hbar")
    a = stable_float(p.get("a"), f"{family.family_id}.parameters.a")
    b = stable_float(p.get("b"), f"{family.family_id}.parameters.b")
    d = stable_float(p.get("d"), f"{family.family_id}.parameters.d")
    exclude_zero_triplet = bool(p.get("exclude_zero_triplet", True))
    out: list[FamilyModeRecord] = []
    for label in family.mode_labels:
        m, n, q = parse_mode_label(label)
        if exclude_zero_triplet and (m, n, q) == (0, 0, 0):
            continue
        k2 = (m * math.pi / a) ** 2 + (n * math.pi / b) ** 2 + (q * math.pi / d) ** 2
        p2 = (hbar ** 2) * k2
        out.append(FamilyModeRecord(family.family_id, family.family_type, family.source_model, family.role_hint, label, str((m, n, q)), math.sqrt(p2), p2, False))
    return out


def membrane_modes(family: ExternalFamilyDefinition) -> list[FamilyModeRecord]:
    p = family.parameters
    hbar = stable_float(p.get("hbar", 1.0), f"{family.family_id}.parameters.hbar")
    radius = stable_float(p.get("radius"), f"{family.family_id}.parameters.radius")
    zero_table = ensure_dict(family.generation.get("bessel_zero_table", {}), f"{family.family_id}.generation.bessel_zero_table")
    out: list[FamilyModeRecord] = []
    for label in family.mode_labels:
        m, n = parse_mode_label(label)
        key = f"m{m}"
        zeros = ensure_list(zero_table.get(key), f"{family.family_id}.generation.bessel_zero_table.{key}")
        if n < 1 or n > len(zeros):
            raise ConfigError(f"Mode {label!r} requests missing Bessel zero in {family.family_id}")
        x_mn = stable_float(zeros[n - 1], f"{family.family_id}.generation.bessel_zero_table.{key}[{n - 1}]")
        p2 = (hbar ** 2) * (x_mn ** 2) / (radius ** 2)
        out.append(FamilyModeRecord(family.family_id, family.family_type, family.source_model, family.role_hint, label, str((m, n)), math.sqrt(p2), p2, False))
    return out


def generate_family_modes(family: ExternalFamilyDefinition) -> list[FamilyModeRecord]:
    if family.family_type == "ring":
        return ring_modes(family)
    if family.family_type == "rectangular_cavity":
        return cavity_modes(family)
    if family.family_type == "circular_membrane":
        return membrane_modes(family)
    raise ConfigError(f"Unsupported family_type for {family.family_id}: {family.family_type}")


def normalize_modes(modes: list[FamilyModeRecord], cfg: OperationalizationConfig) -> list[FamilyModeRecord]:
    if not cfg.normalization_enabled:
        return modes
    if cfg.normalization_mode != "family_internal_first_mode":
        raise ConfigError(f"Unsupported normalization mode: {cfg.normalization_mode}")
    if not modes:
        return modes
    sorted_modes = sorted(modes, key=lambda row: (row.p2_value, row.mode_label))
    p2_ref = max(sorted_modes[0].p2_value, cfg.normalization_epsilon)
    out: list[FamilyModeRecord] = []
    for row in modes:
        p2_value = row.p2_value / p2_ref
        p_value = row.p_value / math.sqrt(p2_ref) if row.p_value is not None else None
        out.append(FamilyModeRecord(row.family_id, row.family_type, row.source_model, row.role_hint, row.mode_label, row.index_tuple, p_value, p2_value, row.is_direct_momentum))
    return out


def order_modes(modes: list[FamilyModeRecord], cfg: OperationalizationConfig) -> list[FamilyModeRecord]:
    return sorted(modes, key=lambda row: (row.p2_value, row.mode_label))


def pair_indices_index_rule(modes: list[FamilyModeRecord], family: ExternalFamilyDefinition) -> list[tuple[int, int]]:
    rule = str(family.pairing.get("index_rule", "")).strip()
    pairs: list[tuple[int, int]] = []
    if rule == "adjacent_m":
        groups = sorted([(parse_mode_label(m.mode_label)[0], idx) for idx, m in enumerate(modes)], key=lambda x: x[0])
        for left, right in zip(groups, groups[1:]):
            pairs.append((left[1], right[1]))
        return pairs
    if rule == "fixed_m_adjacent_n":
        grouped: dict[int, list[tuple[int, int]]] = {}
        for idx, mode in enumerate(modes):
            m, n = parse_mode_label(mode.mode_label)
            grouped.setdefault(m, []).append((n, idx))
        for _, values in grouped.items():
            values.sort(key=lambda x: x[0])
            for left, right in zip(values, values[1:]):
                pairs.append((left[1], right[1]))
        return pairs
    raise ConfigError(f"Unsupported index_rule for {family.family_id}: {rule}")


def build_pairs(modes: list[FamilyModeRecord], family: ExternalFamilyDefinition, cfg: OperationalizationConfig) -> list[tuple[int, int]]:
    pairing_mode = str(family.pairing.get("mode", cfg.default_pairing_mode)).strip()
    if pairing_mode == "sorted_neighbor":
        return [(i, i + 1) for i in range(len(modes) - 1)]
    if pairing_mode == "index_rule":
        return pair_indices_index_rule(modes, family)
    raise ConfigError(f"Unsupported pairing mode for {family.family_id}: {pairing_mode}")


def classify_delta_p2_bucket(delta_p2: float) -> str:
    if delta_p2 < -1.0:
        return "strong_negative"
    if -1.0 <= delta_p2 < 0.0:
        return "compact_negative"
    if delta_p2 == 0.0:
        return "zero"
    if 0.0 < delta_p2 <= 1.0:
        return "compact_positive"
    return "strong_positive"


def generate_pair_rows(modes: list[FamilyModeRecord], family: ExternalFamilyDefinition, cfg: Config) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left_idx, right_idx in build_pairs(modes, family, cfg.operationalization):
        left = modes[left_idx]
        right = modes[right_idx]
        delta_p = (left.p_value - right.p_value) if (left.p_value is not None and right.p_value is not None) else None
        delta_p2 = left.p2_value - right.p2_value
        identity_strength = min(1.0, abs(delta_p2) / 2.0)
        branch_match_frac = min(1.0, 0.35 + 0.5 * identity_strength)
        rows.append({
            "family_id": family.family_id,
            "family_role": family.role_hint,
            "family_type": family.family_type,
            "source_model": family.source_model,
            "left_mode_label": left.mode_label,
            "right_mode_label": right.mode_label,
            "left_index_tuple": left.index_tuple,
            "right_index_tuple": right.index_tuple,
            "left_p": left.p_value,
            "right_p": right.p_value,
            "left_p2": left.p2_value,
            "right_p2": right.p2_value,
            "delta_p": delta_p,
            "delta_p_abs": abs(delta_p) if delta_p is not None else None,
            "delta_p2": delta_p2,
            "delta_p2_abs": abs(delta_p2),
            "sum_p": (left.p_value + right.p_value) if (left.p_value is not None and right.p_value is not None) else None,
            "mean_p": ((left.p_value + right.p_value) / 2.0) if (left.p_value is not None and right.p_value is not None) else None,
            "delta_p2_bucket": classify_delta_p2_bucket(delta_p2),
            "identity_strength": identity_strength,
            "branch_match_frac": branch_match_frac,
            "is_direct_momentum": int(left.is_direct_momentum and right.is_direct_momentum),
        })
    return rows


def summarize_family(family: ExternalFamilyDefinition, pair_rows: list[dict[str, Any]], thresholds: Thresholds, pass_logic: FamilyPassLogic) -> dict[str, Any]:
    branch_values = [float(row["branch_match_frac"]) for row in pair_rows]
    identity_values = [float(row["identity_strength"]) for row in pair_rows]
    delta_p2_values = [float(row["delta_p2"]) for row in pair_rows]
    delta_p_values = [abs(float(row["delta_p"])) for row in pair_rows if row["delta_p"] is not None]
    mean_branch_match_frac = mean(branch_values) if branch_values else 0.0
    mean_identity_strength = mean(identity_values) if identity_values else 0.0
    pair_strength = mean([min(1.0, x / 12.0) for x in delta_p_values]) if delta_p_values else 0.0
    delta_p_strength = mean([min(1.0, x / 10.0) for x in delta_p_values]) if delta_p_values else 0.0
    delta_p2_strength = 0.5 * mean_identity_strength + 0.5 * mean_branch_match_frac

    if delta_p2_strength >= max(pair_strength, delta_p_strength) + thresholds.delta_p2_min_dominance_margin:
        dominant_level = "delta_p2"
    elif delta_p_strength >= pair_strength:
        dominant_level = "delta_p"
    else:
        dominant_level = "pair"

    if family.role_hint == "external_control":
        family_pass_flag = int(pass_logic.external_control_allow_pass_if_delta_p2_dominant and dominant_level == "delta_p2" and mean_branch_match_frac <= pass_logic.external_control_require_branch_match_frac_leq)
    elif family.role_hint == "external_main_test":
        family_pass_flag = int((not pass_logic.external_main_test_require_delta_p2_dominant or dominant_level == "delta_p2") and mean_branch_match_frac >= pass_logic.external_main_test_require_branch_match_frac_geq and mean_identity_strength >= pass_logic.external_main_test_require_identity_strength_geq)
    elif family.role_hint == "external_hard_bias_test":
        family_pass_flag = int(pass_logic.external_hard_bias_test_record_pass_flag and ((not pass_logic.external_hard_bias_test_require_delta_p2_dominant) or dominant_level == "delta_p2"))
    else:
        family_pass_flag = 0

    return {
        "family_id": family.family_id,
        "family_role": family.role_hint,
        "family_type": family.family_type,
        "source_model": family.source_model,
        "description": family.description,
        "n_pairs_total": len(pair_rows),
        "mean_branch_match_frac": mean_branch_match_frac,
        "mean_identity_strength": mean_identity_strength,
        "pair_strength": pair_strength,
        "delta_p_strength": delta_p_strength,
        "delta_p2_strength": delta_p2_strength,
        "delta_p2_dominance_margin": delta_p2_strength - max(pair_strength, delta_p_strength),
        "dominant_level": dominant_level,
        "family_pass_flag": family_pass_flag,
        "min_delta_p2": min(delta_p2_values) if delta_p2_values else 0.0,
        "max_delta_p2": max(delta_p2_values) if delta_p2_values else 0.0,
        "median_delta_p2": median(delta_p2_values) if delta_p2_values else 0.0,
    }


def build_expanded_definition_rows(families: list[ExternalFamilyDefinition], family_modes: dict[str, list[FamilyModeRecord]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in families:
        modes = family_modes.get(family.family_id, [])
        rows.append({
            "family_id": family.family_id,
            "family_role": family.role_hint,
            "family_type": family.family_type,
            "source_model": family.source_model,
            "description": family.description,
            "n_modes": len(modes),
            "is_direct_momentum": int(all(m.is_direct_momentum for m in modes)) if modes else 0,
            "ordering_mode": family.ordering.get("mode", ""),
            "pairing_mode": family.pairing.get("mode", ""),
            "mode_labels_serialized": json.dumps([m.mode_label for m in modes], ensure_ascii=False),
            "notes": family.notes,
        })
    return rows


def build_global_summary(family_summaries: list[dict[str, Any]], thresholds: Thresholds) -> dict[str, Any]:
    pass_flags = [int(row["family_pass_flag"]) for row in family_summaries]
    pass_fraction = mean(pass_flags) if pass_flags else 0.0
    return {
        "n_families_total": len(family_summaries),
        "n_families_passed": sum(pass_flags),
        "family_pass_fraction": pass_fraction,
        "delta_p2_dominant_count": sum(1 for row in family_summaries if row["dominant_level"] == "delta_p2"),
        "external_main_test_ids": [row["family_id"] for row in family_summaries if row["family_role"] == "external_main_test"],
        "external_control_ids": [row["family_id"] for row in family_summaries if row["family_role"] == "external_control"],
        "external_hard_bias_test_ids": [row["family_id"] for row in family_summaries if row["family_role"] == "external_hard_bias_test"],
        "global_pass_flag": int(pass_fraction >= thresholds.min_global_pass_fraction),
        "notes": "M.3.9x evaluates delta_p2 outside the internal family construction space under fixed logic.",
    }


def build_bias_check_report(families: list[ExternalFamilyDefinition], family_summaries: list[dict[str, Any]], global_summary: dict[str, Any]) -> str:
    by_id = {row["family_id"]: row for row in family_summaries}
    lines = [
        "# M.3.9x — External Reference Bias-Check Report",
        "",
        "## Global summary",
        "",
        f"- Families total: {global_summary['n_families_total']}",
        f"- Families passed: {global_summary['n_families_passed']}",
        f"- Family pass fraction: {global_summary['family_pass_fraction']:.3f}",
        f"- delta_p2-dominant families: {global_summary['delta_p2_dominant_count']}",
        f"- Global pass flag: {global_summary['global_pass_flag']}",
        "",
        "## Family summaries",
        "",
    ]
    for family in families:
        row = by_id[family.family_id]
        lines.extend([
            f"### {family.family_id}",
            f"- role: {row['family_role']}",
            f"- dominant_level: {row['dominant_level']}",
            f"- mean_branch_match_frac: {row['mean_branch_match_frac']:.3f}",
            f"- mean_identity_strength: {row['mean_identity_strength']:.3f}",
            f"- delta_p2_strength: {row['delta_p2_strength']:.3f}",
            f"- family_pass_flag: {row['family_pass_flag']}",
            "",
        ])
    return "\n".join(lines).strip() + "\n"


def build_source_notes(families: list[ExternalFamilyDefinition]) -> str:
    lines = ["# M.3.9x — External Family Source Notes", ""]
    for family in families:
        lines.extend([
            f"## {family.family_id}",
            "",
            f"- family_type: {family.family_type}",
            f"- source_model: {family.source_model}",
            f"- role_hint: {family.role_hint}",
            f"- description: {family.description}",
            f"- generation_mode: {family.generation.get('mode', '')}",
            f"- generation_formula: {family.generation.get('formula', '')}",
            f"- ordering_mode: {family.ordering.get('mode', '')}",
            f"- pairing_mode: {family.pairing.get('mode', '')}",
        ])
        if "index_rule" in family.pairing:
            lines.append(f"- index_rule: {family.pairing.get('index_rule')}")
        lines.extend(["", "### parameters", ""])
        for key, value in family.parameters.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    config_path = (project_root / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config)
    cfg = load_config(config_path)
    family_path = (project_root / cfg.external_families_path).resolve()
    families = load_external_family_definitions(family_path, cfg.family_selection.include_families)
    output_root = (project_root / cfg.outputs.root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    family_modes: dict[str, list[FamilyModeRecord]] = {}
    pair_rows_all: list[dict[str, Any]] = []
    family_summaries: list[dict[str, Any]] = []

    for family in families:
        modes = generate_family_modes(family)
        modes = normalize_modes(modes, cfg.operationalization)
        modes = order_modes(modes, cfg.operationalization)
        family_modes[family.family_id] = modes
        pair_rows = generate_pair_rows(modes, family, cfg)
        pair_rows_all.extend(pair_rows)
        family_summaries.append(summarize_family(family, pair_rows, cfg.thresholds, cfg.family_pass_logic))

    expanded_rows = build_expanded_definition_rows(families, family_modes)
    global_summary = build_global_summary(family_summaries, cfg.thresholds)
    bias_report = build_bias_check_report(families, family_summaries, global_summary)
    source_notes = build_source_notes(families)

    write_csv(output_root / cfg.outputs.external_family_definitions_expanded, expanded_rows, ["family_id", "family_role", "family_type", "source_model", "description", "n_modes", "is_direct_momentum", "ordering_mode", "pairing_mode", "mode_labels_serialized", "notes"])
    write_csv(output_root / cfg.outputs.external_family_pair_summary, pair_rows_all, ["family_id", "family_role", "family_type", "source_model", "left_mode_label", "right_mode_label", "left_index_tuple", "right_index_tuple", "left_p", "right_p", "left_p2", "right_p2", "delta_p", "delta_p_abs", "delta_p2", "delta_p2_abs", "sum_p", "mean_p", "delta_p2_bucket", "identity_strength", "branch_match_frac", "is_direct_momentum"])
    write_csv(output_root / cfg.outputs.external_family_branch_summary, family_summaries, ["family_id", "family_role", "family_type", "source_model", "description", "n_pairs_total", "mean_branch_match_frac", "mean_identity_strength", "pair_strength", "delta_p_strength", "delta_p2_strength", "delta_p2_dominance_margin", "dominant_level", "family_pass_flag", "min_delta_p2", "max_delta_p2", "median_delta_p2"])
    write_json(output_root / cfg.outputs.external_family_global_summary, global_summary)
    write_text(output_root / cfg.outputs.external_family_bias_check_report, bias_report)
    write_text(output_root / cfg.outputs.external_family_source_notes, source_notes)

    if cfg.audit.run_external_matched_pairs:
        write_csv(output_root / cfg.outputs.external_family_matched_pair_summary, [], ["left_family_id", "right_family_id", "note"])
        write_csv(output_root / cfg.outputs.external_family_matched_pair_compare, [], ["left_family_id", "right_family_id", "compare_note"])

    print(f"M.3.9x completed. Output written to: {output_root}")


if __name__ == "__main__":
    main()
