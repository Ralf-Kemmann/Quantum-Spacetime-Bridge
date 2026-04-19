from __future__ import annotations

import argparse
import csv
import json
import math
import random
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any


PROJECT_ROOT = Path(
    "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/"
    "debroglie-phase-bridge/debroglie-phase-bridge/typ_b_analysis"
)

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "h3_mixed_like_sensitivity.yaml"
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "h3_mixed_like_sensitivity.schema.json"
DEFAULT_TEMPLATE_DIR = PROJECT_ROOT / "templates"


try:
    import yaml  # type: ignore
except Exception as exc:
    raise SystemExit(
        "PyYAML is required. Install it with:\n"
        "  python3 -m pip install pyyaml"
    ) from exc

try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None


@dataclass
class RunContext:
    run_id: str
    output_dir: Path
    config_path: Path
    schema_path: Path
    template_dir: Path
    config: dict[str, Any]


def now_run_id(prefix: str = "H3MLS01") -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def safe_float(value: Any, default: float = math.nan) -> float:
    try:
        return float(value)
    except Exception:
        return default


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must be an object: {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON schema must be an object: {path}")
    return data


def validate_config(config: dict[str, Any], schema: dict[str, Any]) -> None:
    if jsonschema is None:
        print("[WARN] jsonschema not installed; skipping schema validation.")
        return
    jsonschema.validate(instance=config, schema=schema)


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copy2(src, dst)


def median_from_values(values: list[float]) -> float:
    cleaned = [v for v in values if not math.isnan(v)]
    if not cleaned:
        return math.nan
    return float(median(cleaned))


def median_of(rows: list[dict[str, Any]], key: str) -> float:
    values = [safe_float(r.get(key)) for r in rows if not math.isnan(safe_float(r.get(key)))]
    return median_from_values(values)


def fraction_positive(rows: list[dict[str, Any]], key: str) -> float:
    values = [safe_float(r.get(key)) for r in rows if not math.isnan(safe_float(r.get(key)))]
    if not values:
        return 0.0
    return sum(1 for v in values if v > 0) / len(values)


def bool_to_yesno(value: bool) -> str:
    return "yes" if value else "no"


def build_run_context(
    config_path: Path,
    schema_path: Path,
    template_dir: Path,
    run_id: str | None = None,
) -> RunContext:
    config = load_yaml(config_path)
    schema = load_json(schema_path)
    validate_config(config, schema)

    final_run_id = run_id or now_run_id()
    output_dir = PROJECT_ROOT / str(config["outputs"]["root_dir"]).replace("{run_id}", final_run_id)
    ensure_dir(output_dir)

    return RunContext(
        run_id=final_run_id,
        output_dir=output_dir,
        config_path=config_path,
        schema_path=schema_path,
        template_dir=template_dir,
        config=config,
    )


def load_input_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    rel_path = config["data_inputs"]["support_score_table_path"]
    csv_path = PROJECT_ROOT / rel_path
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    required = {
        "unit_id",
        "baseline_score",
        "combined_score",
        "support_like",
        "boundary_like",
        "mixed_like",
    }

    rows: list[dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required input columns: {sorted(missing)}")

        for row in reader:
            rows.append(
                {
                    "unit_id": str(row["unit_id"]),
                    "baseline_score": safe_float(row["baseline_score"]),
                    "combined_score": safe_float(row["combined_score"]),
                    "support_like": int(row["support_like"]),
                    "boundary_like": int(row["boundary_like"]),
                    "mixed_like": int(row["mixed_like"]),
                    "export_class": row.get("export_class", ""),
                    "delta_score_g": safe_float(row.get("delta_score_g", math.nan)),
                    "pair_i": row.get("pair_i", ""),
                    "pair_j": row.get("pair_j", ""),
                }
            )
    return rows


def get_profile_factor(config: dict[str, Any], parameter_profile: str) -> float:
    profiles = config["replication"]["parameter_perturbations"]["perturbation_profiles"]
    return safe_float(profiles[parameter_profile]["factor"], 1.0)


def apply_mapping_mode(
    rows: list[dict[str, Any]],
    mapping_mode_name: str,
    mapping_mode_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    support_rule = mapping_mode_cfg["support_rule"]
    neighbor_rule = mapping_mode_cfg["neighbor_rule"]

    mapped_rows: list[dict[str, Any]] = []

    for row in rows:
        new_row = dict(row)

        if support_rule == "support_like":
            is_support = int(row["support_like"])
        elif support_rule == "support_like_or_mixed_like":
            is_support = int(row["support_like"] or row["mixed_like"])
        else:
            raise ValueError(f"Unknown support_rule for {mapping_mode_name}: {support_rule}")

        if neighbor_rule == "boundary_like":
            is_neighbor = int(row["boundary_like"])
        elif neighbor_rule == "boundary_like_or_mixed_like":
            is_neighbor = int(row["boundary_like"] or row["mixed_like"])
        else:
            raise ValueError(f"Unknown neighbor_rule for {mapping_mode_name}: {neighbor_rule}")

        new_row["is_support"] = is_support
        new_row["is_neighbor"] = is_neighbor
        new_row["mapping_mode"] = mapping_mode_name
        new_row["mapping_label"] = mapping_mode_cfg["label"]
        mapped_rows.append(new_row)

    return mapped_rows


def apply_state_scores(
    rows: list[dict[str, Any]],
    state_name: str,
    state_cfg: dict[str, Any],
    seed: int,
    profile_factor: float,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    sm_cfg = state_cfg.get("support_manipulation", {})
    level = safe_float(sm_cfg.get("level", 0.0), 0.0) * profile_factor

    if state_name == "D1":
        rng = random.Random(seed)
        support_flags = [int(r["is_support"]) for r in rows]
        rng.shuffle(support_flags)

        for row, shuffled_support in zip(rows, support_flags):
            new_row = dict(row)
            new_row["is_support_effective"] = int(shuffled_support)
            new_row["is_neighbor_effective"] = int(row["is_neighbor"])
            new_row["combined_score_effective"] = float(row["combined_score"])
            out.append(new_row)
        return out

    if state_name == "D2":
        rng = random.Random(seed + 10_000)
        n_support = sum(int(r["is_support"]) for r in rows)
        indices = list(range(len(rows)))
        chosen_support = set(rng.sample(indices, k=n_support))

        for idx, row in enumerate(rows):
            new_row = dict(row)
            new_row["is_support_effective"] = 1 if idx in chosen_support else 0
            new_row["is_neighbor_effective"] = int(row["is_neighbor"])
            new_row["combined_score_effective"] = float(row["combined_score"])
            out.append(new_row)
        return out

    for row in rows:
        new_row = dict(row)
        new_row["is_support_effective"] = int(row["is_support"])
        new_row["is_neighbor_effective"] = int(row["is_neighbor"])

        if state_name == "A":
            new_row["combined_score_effective"] = float(row["baseline_score"])
        elif state_name in {"B", "C"}:
            uplift = level if int(row["is_support"]) == 1 else 0.0
            new_row["combined_score_effective"] = float(row["combined_score"]) + uplift
        else:
            raise ValueError(f"Unknown state: {state_name}")

        out.append(new_row)

    return out


def compute_support_separation(rows: list[dict[str, Any]], score_key: str) -> float:
    support_vals = [safe_float(r[score_key]) for r in rows if int(r["is_support_effective"]) == 1]
    neighbor_vals = [
        safe_float(r[score_key])
        for r in rows
        if int(r["is_support_effective"]) == 0 and int(r["is_neighbor_effective"]) == 1
    ]

    support_med = median_from_values(support_vals)
    neighbor_med = median_from_values(neighbor_vals)

    if math.isnan(support_med) or math.isnan(neighbor_med):
        return math.nan
    return support_med - neighbor_med


def classify_shift_signal(gain_value: float, eps_low: float = 1e-12, eps_readable: float = 0.02) -> str:
    if math.isnan(gain_value):
        return "undefined"
    if gain_value <= eps_low:
        return "none_or_negative"
    if gain_value < eps_readable:
        return "positive_low_level_shift"
    return "positive_shift"


def compute_state_metrics(
    config: dict[str, Any],
    mapped_rows: list[dict[str, Any]],
    mapping_mode_name: str,
    mapping_mode_cfg: dict[str, Any],
    state_name: str,
    state_cfg: dict[str, Any],
    seed: int,
    parameter_profile: str,
) -> dict[str, Any]:
    profile_factor = get_profile_factor(config, parameter_profile)
    state_rows = apply_state_scores(
        rows=mapped_rows,
        state_name=state_name,
        state_cfg=state_cfg,
        seed=seed,
        profile_factor=profile_factor,
    )

    support_sep_baseline = compute_support_separation(state_rows, "baseline_score")
    support_sep_combined = compute_support_separation(state_rows, "combined_score_effective")

    gain_value = (
        support_sep_combined - support_sep_baseline
        if not (math.isnan(support_sep_baseline) or math.isnan(support_sep_combined))
        else math.nan
    )

    null_variant = state_cfg.get("support_manipulation", {}).get("variant")
    baseline_anchor_status = "primary_retained"

    if math.isnan(gain_value):
        combined_status_stability = "unstable"
        auxiliary_compatibility = "undefined"
    elif gain_value >= 0:
        combined_status_stability = "stable"
        auxiliary_compatibility = (
            "noise_compatible" if state_name in {"D1", "D2"} else "compatible_but_bounded"
        )
    else:
        combined_status_stability = "destabilized"
        auxiliary_compatibility = "not_compatible"

    sign_stability = 0.0 if math.isnan(gain_value) else (1.0 if gain_value > 0 else 0.0)
    replicate_consistency = sign_stability
    null_noise_margin = 0.02

    return {
        "mapping_mode": mapping_mode_name,
        "mapping_label": mapping_mode_cfg["label"],
        "seed": seed,
        "parameter_profile": parameter_profile,
        "state": state_name,
        "null_variant": null_variant,
        "profile_factor": round(profile_factor, 6),
        "baseline_anchor_status": baseline_anchor_status,
        "combined_status_stability": combined_status_stability,
        "auxiliary_compatibility": auxiliary_compatibility,
        "neighbor_shift_signal": classify_shift_signal(gain_value),
        "a1_shift_signal": classify_shift_signal(gain_value),
        "b1_shift_signal": "stable" if combined_status_stability == "stable" else "unstable",
        "gain_value": round(gain_value, 6) if not math.isnan(gain_value) else math.nan,
        "gain_vs_A": math.nan,
        "gain_vs_D": math.nan,
        "sign_stability": round(sign_stability, 6),
        "replicate_consistency": round(replicate_consistency, 6),
        "null_noise_margin": round(null_noise_margin, 6),
        "auxiliary_primary_takeover": False,
        "role_flip": False,
        "support_sep_baseline": round(support_sep_baseline, 6) if not math.isnan(support_sep_baseline) else math.nan,
        "support_sep_combined": round(support_sep_combined, 6) if not math.isnan(support_sep_combined) else math.nan,
    }


def group_by_mode_and_state(rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["mapping_mode"]), str(row["state"]))
        grouped.setdefault(key, []).append(row)
    return grouped


def group_by_mode_state_profile(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["mapping_mode"]), str(row["state"]), str(row["parameter_profile"]))
        grouped.setdefault(key, []).append(row)
    return grouped


def fill_reference_deltas(rows: list[dict[str, Any]]) -> None:
    modes = sorted({str(r["mapping_mode"]) for r in rows})
    for mode in modes:
        mode_rows = [r for r in rows if str(r["mapping_mode"]) == mode]
        rows_A = [r for r in mode_rows if str(r["state"]) == "A"]
        rows_D = [r for r in mode_rows if str(r["state"]) in {"D1", "D2"}]

        median_A = median_of(rows_A, "gain_value")
        median_D = median_of(rows_D, "gain_value")

        for row in mode_rows:
            gain_value = safe_float(row.get("gain_value"))
            row["gain_vs_A"] = (
                round(gain_value - median_A, 6)
                if not math.isnan(gain_value) and not math.isnan(median_A)
                else math.nan
            )
            row["gain_vs_D"] = (
                round(gain_value - median_D, 6)
                if not math.isnan(gain_value) and not math.isnan(median_D)
                else math.nan
            )


def update_replicate_consistency(rows: list[dict[str, Any]]) -> None:
    grouped = group_by_mode_and_state(rows)
    fractions = {key: fraction_positive(state_rows, "gain_value") for key, state_rows in grouped.items()}
    for row in rows:
        key = (str(row["mapping_mode"]), str(row["state"]))
        row["replicate_consistency"] = round(fractions.get(key, 0.0), 6)


def summarize_by_mode_and_state(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = group_by_mode_and_state(rows)
    out: list[dict[str, Any]] = []

    for (mapping_mode, state), state_rows in sorted(grouped.items()):
        out.append(
            {
                "mapping_mode": mapping_mode,
                "mapping_label": state_rows[0]["mapping_label"],
                "state": state,
                "n": len(state_rows),
                "median_gain_value": round(median_of(state_rows, "gain_value"), 6),
                "median_gain_vs_A": round(median_of(state_rows, "gain_vs_A"), 6),
                "median_gain_vs_D": round(median_of(state_rows, "gain_vs_D"), 6),
                "positive_direction_fraction": round(fraction_positive(state_rows, "gain_value"), 6),
                "median_sign_stability": round(median_of(state_rows, "sign_stability"), 6),
                "median_replicate_consistency": round(median_of(state_rows, "replicate_consistency"), 6),
                "median_null_noise_margin": round(median_of(state_rows, "null_noise_margin"), 6),
                "median_support_sep_baseline": round(median_of(state_rows, "support_sep_baseline"), 6),
                "median_support_sep_combined": round(median_of(state_rows, "support_sep_combined"), 6),
            }
        )

    return out


def summarize_by_mode_state_profile(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = group_by_mode_state_profile(rows)
    out: list[dict[str, Any]] = []

    for (mapping_mode, state, profile), state_rows in sorted(grouped.items()):
        out.append(
            {
                "mapping_mode": mapping_mode,
                "mapping_label": state_rows[0]["mapping_label"],
                "state": state,
                "parameter_profile": profile,
                "n": len(state_rows),
                "median_profile_factor": round(median_of(state_rows, "profile_factor"), 6),
                "median_gain_value": round(median_of(state_rows, "gain_value"), 6),
                "median_gain_vs_A": round(median_of(state_rows, "gain_vs_A"), 6),
                "median_gain_vs_D": round(median_of(state_rows, "gain_vs_D"), 6),
                "positive_direction_fraction": round(fraction_positive(state_rows, "gain_value"), 6),
                "median_sign_stability": round(median_of(state_rows, "sign_stability"), 6),
                "median_replicate_consistency": round(median_of(state_rows, "replicate_consistency"), 6),
                "median_null_noise_margin": round(median_of(state_rows, "null_noise_margin"), 6),
                "median_support_sep_baseline": round(median_of(state_rows, "support_sep_baseline"), 6),
                "median_support_sep_combined": round(median_of(state_rows, "support_sep_combined"), 6),
            }
        )

    return out


def build_decision_summary(ctx: RunContext, rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "block_id": ctx.config["block_id"],
        "source_block": ctx.config["source_block"],
        "mapping_modes_evaluated": [],
        "reference_mode": "M0",
        "overall_outcome_by_mode": {},
        "A_B_C_order_preserved_by_mode": {},
        "nullmodel_behavior_by_mode": {},
        "robustness_assessment": "",
    }

    mapping_modes = ctx.config["mapping_modes"]
    modes = list(mapping_modes.keys())
    result["mapping_modes_evaluated"] = modes

    robust_all = True

    for mode in modes:
        mode_rows = [r for r in rows if str(r["mapping_mode"]) == mode]
        rows_A = [r for r in mode_rows if str(r["state"]) == "A"]
        rows_B = [r for r in mode_rows if str(r["state"]) == "B"]
        rows_C = [r for r in mode_rows if str(r["state"]) == "C"]
        rows_D1 = [r for r in mode_rows if str(r["state"]) == "D1"]
        rows_D2 = [r for r in mode_rows if str(r["state"]) == "D2"]
        rows_D = rows_D1 + rows_D2

        gain_A = median_of(rows_A, "gain_value")
        gain_B = median_of(rows_B, "gain_value")
        gain_C = median_of(rows_C, "gain_value")
        gain_D1 = median_of(rows_D1, "gain_value")
        gain_D2 = median_of(rows_D2, "gain_value")
        gain_D = median_of(rows_D, "gain_value")

        baseline_first_preserved = (
            all(r["baseline_anchor_status"] == "primary_retained" for r in rows_B)
            and all(r["baseline_anchor_status"] == "primary_retained" for r in rows_C)
        )
        monotone_support_scaling = (
            not math.isnan(gain_A)
            and not math.isnan(gain_B)
            and not math.isnan(gain_C)
            and gain_A <= gain_B <= gain_C
        )
        null_model_suppression = (
            not math.isnan(gain_B)
            and not math.isnan(gain_C)
            and not math.isnan(gain_D)
            and gain_B > gain_D
            and gain_C > gain_D
        )
        boundedness_preserved = True

        aux_shift_detectable = (
            median_of(rows_B, "gain_vs_A") > 0.0
            and fraction_positive(rows_B, "gain_value") >= 0.60
        )
        readable_threshold_ok = (
            median_of(rows_B, "sign_stability") >= 0.80
            and median_of(rows_B, "replicate_consistency") >= 0.80
            and median_of(rows_B, "gain_vs_D") > median_of(rows_B, "null_noise_margin")
        )
        aux_shift_readable = aux_shift_detectable and readable_threshold_ok

        hard_fail = not baseline_first_preserved or not null_model_suppression

        if hard_fail:
            overall_outcome = "not_supported"
        elif aux_shift_readable and monotone_support_scaling and boundedness_preserved:
            overall_outcome = "limited_supported"
        elif aux_shift_detectable:
            overall_outcome = "limited_supported_but_fragile"
        else:
            overall_outcome = "noise_compatible"

        result["overall_outcome_by_mode"][mode] = {
            "label": mapping_modes[mode]["label"],
            "overall_outcome": overall_outcome,
            "gain_A": None if math.isnan(gain_A) else round(gain_A, 6),
            "gain_B": None if math.isnan(gain_B) else round(gain_B, 6),
            "gain_C": None if math.isnan(gain_C) else round(gain_C, 6),
            "gain_D1": None if math.isnan(gain_D1) else round(gain_D1, 6),
            "gain_D2": None if math.isnan(gain_D2) else round(gain_D2, 6),
        }

        result["A_B_C_order_preserved_by_mode"][mode] = monotone_support_scaling
        result["nullmodel_behavior_by_mode"][mode] = {
            "baseline_first_preserved": baseline_first_preserved,
            "null_model_suppression": null_model_suppression,
            "D1_negative_or_low": bool(not math.isnan(gain_D1) and gain_D1 <= 0.0),
            "D2_negative_or_low": bool(not math.isnan(gain_D2) and gain_D2 <= 0.0),
        }

        if overall_outcome not in {"limited_supported", "limited_supported_but_fragile"}:
            robust_all = False
        if not monotone_support_scaling:
            robust_all = False

    if robust_all:
        result["robustness_assessment"] = "robust_across_mappings"
    else:
        result["robustness_assessment"] = "mapping_sensitive_or_fragile"

    return result


def write_readout(path: Path, decision_summary: dict[str, Any]) -> None:
    lines = [
        "# H3_MIXED_LIKE_SENSITIVITY_01",
        "",
        "## Status",
        "completed",
        "",
        "## Zweck",
        "Sensitivitätstest für die Behandlung von mixed_like-Paaren.",
        "",
        "## Mapping-Modi",
    ]
    for mode, entry in decision_summary["overall_outcome_by_mode"].items():
        lines.extend(
            [
                f"- {mode} ({entry['label']}):",
                f"  - overall_outcome: {entry['overall_outcome']}",
                f"  - gain_A: {entry['gain_A']}",
                f"  - gain_B: {entry['gain_B']}",
                f"  - gain_C: {entry['gain_C']}",
                f"  - gain_D1: {entry['gain_D1']}",
                f"  - gain_D2: {entry['gain_D2']}",
            ]
        )

    lines.extend(
        [
            "",
            "## Robusteinschätzung",
            f"- robustness_assessment: {decision_summary['robustness_assessment']}",
            "",
            "## Projektinterne Lesart",
            "Prüft, wie stark der H3-Befund von der Behandlung der mixed_like-Paare abhängt.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


STATE_METRICS_COLUMNS = [
    "run_id",
    "mapping_mode",
    "mapping_label",
    "seed",
    "parameter_profile",
    "state",
    "null_variant",
    "profile_factor",
    "baseline_anchor_status",
    "combined_status_stability",
    "auxiliary_compatibility",
    "neighbor_shift_signal",
    "a1_shift_signal",
    "b1_shift_signal",
    "gain_value",
    "gain_vs_A",
    "gain_vs_D",
    "sign_stability",
    "replicate_consistency",
    "null_noise_margin",
    "auxiliary_primary_takeover",
    "role_flip",
    "support_sep_baseline",
    "support_sep_combined",
]


def run_block(
    ctx: RunContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    input_rows = load_input_rows(ctx.config)
    seeds = list(ctx.config["replication"]["seeds"])
    profiles = list(ctx.config["replication"]["parameter_perturbations"]["perturbation_profiles"].keys())
    states = ctx.config["states"]
    mapping_modes = ctx.config["mapping_modes"]

    state_metrics_rows: list[dict[str, Any]] = []

    for mapping_mode_name, mapping_mode_cfg in mapping_modes.items():
        mapped_rows = apply_mapping_mode(input_rows, mapping_mode_name, mapping_mode_cfg)

        for seed in seeds:
            for parameter_profile in profiles:
                for state_name in ["A", "B", "C", "D1", "D2"]:
                    row = compute_state_metrics(
                        config=ctx.config,
                        mapped_rows=mapped_rows,
                        mapping_mode_name=mapping_mode_name,
                        mapping_mode_cfg=mapping_mode_cfg,
                        state_name=state_name,
                        state_cfg=states[state_name],
                        seed=int(seed),
                        parameter_profile=str(parameter_profile),
                    )
                    row["run_id"] = ctx.run_id
                    state_metrics_rows.append(row)

    fill_reference_deltas(state_metrics_rows)
    update_replicate_consistency(state_metrics_rows)

    summary_rows = summarize_by_mode_and_state(state_metrics_rows)
    summary_profile_rows = summarize_by_mode_state_profile(state_metrics_rows)
    decision_summary = build_decision_summary(ctx, state_metrics_rows)

    return state_metrics_rows, summary_rows, summary_profile_rows, decision_summary


def write_outputs(
    ctx: RunContext,
    state_metrics_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    summary_profile_rows: list[dict[str, Any]],
    decision_summary: dict[str, Any],
) -> None:
    write_csv(ctx.output_dir / "state_metrics.csv", state_metrics_rows, STATE_METRICS_COLUMNS)

    summary_cols = [
        "mapping_mode",
        "mapping_label",
        "state",
        "n",
        "median_gain_value",
        "median_gain_vs_A",
        "median_gain_vs_D",
        "positive_direction_fraction",
        "median_sign_stability",
        "median_replicate_consistency",
        "median_null_noise_margin",
        "median_support_sep_baseline",
        "median_support_sep_combined",
    ]
    write_csv(ctx.output_dir / "mixed_like_sensitivity_summary.csv", summary_rows, summary_cols)

    summary_profile_cols = [
        "mapping_mode",
        "mapping_label",
        "state",
        "parameter_profile",
        "n",
        "median_profile_factor",
        "median_gain_value",
        "median_gain_vs_A",
        "median_gain_vs_D",
        "positive_direction_fraction",
        "median_sign_stability",
        "median_replicate_consistency",
        "median_null_noise_margin",
        "median_support_sep_baseline",
        "median_support_sep_combined",
    ]
    write_csv(
        ctx.output_dir / "mixed_like_sensitivity_by_profile.csv",
        summary_profile_rows,
        summary_profile_cols,
    )

    write_json(ctx.output_dir / "mixed_like_sensitivity_decision_summary.json", decision_summary)
    write_readout(ctx.output_dir / "mixed_like_sensitivity_readout.md", decision_summary)

    run_metadata = {
        "block_id": ctx.config["block_id"],
        "block_version": ctx.config.get("block_version"),
        "run_id": ctx.run_id,
        "source_block": ctx.config["source_block"],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config_path": str(ctx.config_path),
        "schema_path": str(ctx.schema_path),
    }
    write_json(ctx.output_dir / "run_metadata.json", run_metadata)

    copy_if_exists(ctx.config_path, ctx.output_dir / ctx.config_path.name)
    copy_if_exists(ctx.schema_path, ctx.output_dir / ctx.schema_path.name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runner for H3_MIXED_LIKE_SENSITIVITY_01")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--templates", type=Path, default=DEFAULT_TEMPLATE_DIR)
    parser.add_argument("--run-id", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ctx = build_run_context(
        config_path=args.config,
        schema_path=args.schema,
        template_dir=args.templates,
        run_id=args.run_id,
    )

    print(f"[INFO] Starting run: {ctx.run_id}")
    print(f"[INFO] Output dir:    {ctx.output_dir}")

    state_metrics_rows, summary_rows, summary_profile_rows, decision_summary = run_block(ctx)
    write_outputs(ctx, state_metrics_rows, summary_rows, summary_profile_rows, decision_summary)

    print("[INFO] Run completed.")
    print(f"[INFO] mixed_like_sensitivity_decision_summary.json -> {ctx.output_dir / 'mixed_like_sensitivity_decision_summary.json'}")
    print(f"[INFO] mixed_like_sensitivity_readout.md            -> {ctx.output_dir / 'mixed_like_sensitivity_readout.md'}")


if __name__ == "__main__":
    main()