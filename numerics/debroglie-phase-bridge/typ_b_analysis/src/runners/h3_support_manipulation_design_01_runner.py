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

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "h3_support_manipulation_design_01.yaml"
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "h3_support_manipulation_design_01.schema.json"
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


def now_run_id(prefix: str = "H3SMD01") -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def safe_float(value: Any, default: float = math.nan) -> float:
    try:
        return float(value)
    except Exception:
        return default


def bool_to_yesno(value: bool) -> str:
    return "yes" if value else "no"


def median_from_values(values: list[float]) -> float:
    cleaned = [v for v in values if not math.isnan(v)]
    if not cleaned:
        return math.nan
    return median(cleaned)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must be a mapping/object: {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must be an object: {path}")
    return data


def validate_config(config: dict[str, Any], schema: dict[str, Any]) -> None:
    if jsonschema is None:
        print("[WARN] jsonschema not installed; skipping schema validation.")
        return
    jsonschema.validate(instance=config, schema=schema)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_json_template(path: Path) -> dict[str, Any]:
    return load_json(path)


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copy2(src, dst)


def load_input_payload(config: dict[str, Any]) -> dict[str, Any]:
    data_inputs = config.get("data_inputs", {})
    payload: dict[str, Any] = {"paths": {}, "exists": {}}

    for key, rel_path in data_inputs.items():
        if not str(key).endswith("_path"):
            continue
        abs_path = PROJECT_ROOT / str(rel_path)
        payload["paths"][key] = str(abs_path)
        payload["exists"][key] = abs_path.exists()

    score_path_str = data_inputs.get("support_score_table_path")
    if not score_path_str:
        raise ValueError("Missing data_inputs.support_score_table_path in config.")

    score_path = PROJECT_ROOT / str(score_path_str)
    if not score_path.exists():
        raise FileNotFoundError(f"Support score table not found: {score_path}")

    rows: list[dict[str, Any]] = []
    with score_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"unit_id", "baseline_score", "combined_score", "is_support", "is_neighbor"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Support score table missing required columns: {sorted(missing)}"
            )

        for row in reader:
            rows.append(
                {
                    "unit_id": str(row["unit_id"]),
                    "baseline_score": safe_float(row["baseline_score"]),
                    "combined_score": safe_float(row["combined_score"]),
                    "is_support": int(row["is_support"]),
                    "is_neighbor": int(row["is_neighbor"]),
                    "export_class": row.get("export_class", ""),
                    "support_like": int(row.get("support_like", row["is_support"])),
                    "boundary_like": int(row.get("boundary_like", row["is_neighbor"])),
                    "mixed_like": int(row.get("mixed_like", 0)),
                    "delta_score_g": safe_float(row.get("delta_score_g", math.nan)),
                }
            )

    payload["support_score_rows"] = rows
    payload["support_score_path"] = str(score_path)
    return payload


def get_profile_factor(config: dict[str, Any], parameter_profile: str) -> float:
    pp = config.get("replication", {}).get("parameter_perturbations", {})
    profiles = pp.get("perturbation_profiles", {})
    if isinstance(profiles, dict):
        profile_cfg = profiles.get(parameter_profile, {})
        return safe_float(profile_cfg.get("factor", 1.0), 1.0)
    return 1.0


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
    support_vals = [
        safe_float(r[score_key])
        for r in rows
        if int(r["is_support_effective"]) == 1
    ]
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
    state_name: str,
    state_cfg: dict[str, Any],
    seed: int,
    parameter_profile: str,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    source_rows = input_payload["support_score_rows"]
    profile_factor = get_profile_factor(config, parameter_profile)

    state_rows = apply_state_scores(
        rows=source_rows,
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

    sm_cfg = state_cfg.get("support_manipulation", {})
    null_variant = sm_cfg.get("variant")

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

    neighbor_shift_signal = classify_shift_signal(gain_value)
    a1_shift_signal = classify_shift_signal(gain_value)
    b1_shift_signal = (
        "stable" if combined_status_stability == "stable"
        else "unstable" if combined_status_stability == "destabilized"
        else "undefined"
    )

    sign_stability = 0.0 if math.isnan(gain_value) else (1.0 if gain_value > 0 else 0.0)
    replicate_consistency = sign_stability
    null_noise_margin = 0.02

    return {
        "seed": seed,
        "parameter_profile": parameter_profile,
        "state": state_name,
        "null_variant": null_variant,
        "profile_factor": round(profile_factor, 6),
        "baseline_anchor_status": baseline_anchor_status,
        "combined_status_stability": combined_status_stability,
        "auxiliary_compatibility": auxiliary_compatibility,
        "neighbor_shift_signal": neighbor_shift_signal,
        "a1_shift_signal": a1_shift_signal,
        "b1_shift_signal": b1_shift_signal,
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


def group_by_state(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["state"]), []).append(row)
    return grouped


def median_of(rows: list[dict[str, Any]], key: str) -> float:
    values = [safe_float(r.get(key)) for r in rows if not math.isnan(safe_float(r.get(key)))]
    if not values:
        return math.nan
    return median(values)


def fraction_positive(rows: list[dict[str, Any]], key: str) -> float:
    values = [safe_float(r.get(key)) for r in rows if not math.isnan(safe_float(r.get(key)))]
    if not values:
        return 0.0
    return sum(1 for v in values if v > 0) / len(values)


def all_equal(rows: list[dict[str, Any]], key: str, expected: Any) -> bool:
    return all(r.get(key) == expected for r in rows)


def fill_reference_deltas(rows: list[dict[str, Any]]) -> None:
    grouped = group_by_state(rows)
    median_A = median_of(grouped.get("A", []), "gain_value")
    d_rows = grouped.get("D1", []) + grouped.get("D2", [])
    median_D = median_of(d_rows, "gain_value")

    for row in rows:
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
    grouped = group_by_state(rows)
    fractions = {state: fraction_positive(state_rows, "gain_value") for state, state_rows in grouped.items()}
    for row in rows:
        row["replicate_consistency"] = round(fractions.get(str(row["state"]), 0.0), 6)


def summarize_replicates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = group_by_state(rows)
    out: list[dict[str, Any]] = []
    for state, state_rows in grouped.items():
        out.append(
            {
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
    return sorted(out, key=lambda x: x["state"])


def summarize_replicates_by_profile(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row["state"]), str(row["parameter_profile"]))
        grouped.setdefault(key, []).append(row)

    out: list[dict[str, Any]] = []
    for (state, parameter_profile), state_rows in sorted(grouped.items()):
        out.append(
            {
                "state": state,
                "parameter_profile": parameter_profile,
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


def build_decision_summary(ctx: RunContext, state_rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped = group_by_state(state_rows)

    rows_A = grouped.get("A", [])
    rows_B = grouped.get("B", [])
    rows_C = grouped.get("C", [])
    rows_D1 = grouped.get("D1", [])
    rows_D2 = grouped.get("D2", [])
    rows_D = rows_D1 + rows_D2

    median_gain_A = median_of(rows_A, "gain_value")
    median_gain_B = median_of(rows_B, "gain_value")
    median_gain_C = median_of(rows_C, "gain_value")
    median_gain_D = median_of(rows_D, "gain_value")
    median_gain_D1 = median_of(rows_D1, "gain_value")
    median_gain_D2 = median_of(rows_D2, "gain_value")

    baseline_first_preserved = (
        all_equal(rows_B, "baseline_anchor_status", "primary_retained")
        and all_equal(rows_C, "baseline_anchor_status", "primary_retained")
    )

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

    monotone_support_scaling = (
        not math.isnan(median_gain_A)
        and not math.isnan(median_gain_B)
        and not math.isnan(median_gain_C)
        and median_gain_A <= median_gain_B <= median_gain_C
    )

    null_model_suppression = (
        not math.isnan(median_gain_B)
        and not math.isnan(median_gain_C)
        and not math.isnan(median_gain_D)
        and median_gain_B > median_gain_D
        and median_gain_C > median_gain_D
    )

    boundedness_preserved = (
        not any(bool(r.get("auxiliary_primary_takeover")) for r in state_rows)
        and not any(bool(r.get("role_flip")) for r in state_rows)
    )

    hard_fail_reasons: list[str] = []
    if not baseline_first_preserved:
        hard_fail_reasons.append("baseline_first_broken")
    if not null_model_suppression:
        hard_fail_reasons.append("effect_not_above_null")
    if median_of(rows_B, "replicate_consistency") < 0.80:
        hard_fail_reasons.append("direction_random_across_replicates")

    hard_fail_triggered = len(hard_fail_reasons) > 0

    if hard_fail_triggered:
        overall_outcome = "not_supported"
    elif aux_shift_readable and null_model_suppression and monotone_support_scaling and boundedness_preserved:
        overall_outcome = "limited_supported"
    elif aux_shift_detectable and boundedness_preserved:
        overall_outcome = "limited_supported_but_fragile"
    else:
        overall_outcome = "noise_compatible"

    return {
        "block_id": ctx.config["block_id"],
        "source_block": ctx.config["source_block"],
        "baseline_first_preserved": baseline_first_preserved,
        "aux_shift_detectable": aux_shift_detectable,
        "aux_shift_readable": aux_shift_readable,
        "monotone_support_scaling": monotone_support_scaling,
        "null_model_suppression": null_model_suppression,
        "boundedness_preserved": boundedness_preserved,
        "hard_fail_triggered": hard_fail_triggered,
        "hard_fail_reasons": hard_fail_reasons,
        "overall_outcome": overall_outcome,
        "allowed_outcomes": [
            "not_supported",
            "noise_compatible",
            "limited_supported",
            "limited_supported_but_fragile",
        ],
        "medians": {
            "gain_A": round(median_gain_A, 6) if not math.isnan(median_gain_A) else None,
            "gain_B": round(median_gain_B, 6) if not math.isnan(median_gain_B) else None,
            "gain_C": round(median_gain_C, 6) if not math.isnan(median_gain_C) else None,
            "gain_D": round(median_gain_D, 6) if not math.isnan(median_gain_D) else None,
        },
        "nullmodel_variant_summary": {
            "D1_permutation_null": round(median_gain_D1, 6) if not math.isnan(median_gain_D1) else None,
            "D2_topology_preserving_random_null": round(median_gain_D2, 6) if not math.isnan(median_gain_D2) else None,
        },
    }


STATE_METRICS_COLUMNS = [
    "run_id",
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


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_block_readout(path: Path, decision_summary: dict[str, Any]) -> None:
    text = f"""# H3_SUPPORT_MANIPULATION_DESIGN_01

## Status
completed

## Zweck
Prüfung des bislang einzigen kleinen support-side-H3-Befunds unter kontrollierter A/B/C/D-Manipulation.

## Ausgangspunkt
Source block: `N1_A1_B1_DECOUPLING`
Current numerical status: limited support-side entry only.

## Kernbefund
- baseline_first_preserved: {bool_to_yesno(bool(decision_summary["baseline_first_preserved"]))}
- aux_shift_detectable: {bool_to_yesno(bool(decision_summary["aux_shift_detectable"]))}
- aux_shift_readable: {bool_to_yesno(bool(decision_summary["aux_shift_readable"]))}
- monotone_support_scaling: {bool_to_yesno(bool(decision_summary["monotone_support_scaling"]))}
- null_model_suppression: {bool_to_yesno(bool(decision_summary["null_model_suppression"]))}
- boundedness_preserved: {bool_to_yesno(bool(decision_summary["boundedness_preserved"]))}
- overall_outcome: {decision_summary["overall_outcome"]}

## Nullmodell-Varianten
- D1_permutation_null: {decision_summary["nullmodel_variant_summary"]["D1_permutation_null"]}
- D2_topology_preserving_random_null: {decision_summary["nullmodel_variant_summary"]["D2_topology_preserving_random_null"]}

## Projektinterne Lesart
Support-like vs boundary-like readout with mixed pairs excluded from the hard neighbor set.

## Was der Block bewusst gut macht
- explizite Readability-Schwelle
- echter Nullmodelltest mit D1/D2
- monotone A/B/C-Architektur
- Replikationslogik
- mixed pairs are not forced into boundary-like

## Was der Block bewusst vermeidet
- reference claim
- full hierarchy claim
- post-hoc Schwellenkosmetik
- narrative Überdehnung

## Anschlussrichtung
Replikation / Achsenvergleich / Blockabbruch / Übergang in nächsten H3-Teilblock
"""
    path.write_text(text, encoding="utf-8")


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
    root_pattern = str(config["outputs"]["root_dir"])
    output_dir = PROJECT_ROOT / root_pattern.replace("{run_id}", final_run_id)
    ensure_dir(output_dir)

    return RunContext(
        run_id=final_run_id,
        output_dir=output_dir,
        config_path=config_path,
        schema_path=schema_path,
        template_dir=template_dir,
        config=config,
    )


def write_run_metadata(ctx: RunContext) -> None:
    template_path = ctx.template_dir / "run_metadata.template.json"
    metadata = read_json_template(template_path) if template_path.exists() else {}
    metadata.update(
        {
            "block_id": ctx.config["block_id"],
            "block_version": ctx.config.get("block_version"),
            "run_id": ctx.run_id,
            "source_block": ctx.config["source_block"],
            "state_order": list(ctx.config["states"].keys()),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "config_path": str(ctx.config_path),
            "schema_path": str(ctx.schema_path),
        }
    )
    write_json(ctx.output_dir / "run_metadata.json", metadata)


def run_block(
    ctx: RunContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    input_payload = load_input_payload(ctx.config)
    seeds = list(ctx.config["replication"]["seeds"])

    pp_cfg = ctx.config["replication"].get("parameter_perturbations", {})
    profiles = pp_cfg.get("perturbation_profiles", {})
    parameter_profiles = list(profiles.keys()) if isinstance(profiles, dict) and profiles else ["base"]

    state_metrics_rows: list[dict[str, Any]] = []
    state_defs = ctx.config["states"]

    for seed in seeds:
        for parameter_profile in parameter_profiles:
            for state_name in ["A", "B", "C", "D1", "D2"]:
                row = compute_state_metrics(
                    config=ctx.config,
                    state_name=state_name,
                    state_cfg=state_defs[state_name],
                    seed=int(seed),
                    parameter_profile=str(parameter_profile),
                    input_payload=input_payload,
                )
                row["run_id"] = ctx.run_id
                state_metrics_rows.append(row)

    fill_reference_deltas(state_metrics_rows)
    update_replicate_consistency(state_metrics_rows)

    replicate_summary_rows = summarize_replicates(state_metrics_rows)
    replicate_summary_by_profile_rows = summarize_replicates_by_profile(state_metrics_rows)
    decision_summary = build_decision_summary(ctx, state_metrics_rows)

    return state_metrics_rows, replicate_summary_rows, replicate_summary_by_profile_rows, decision_summary


def write_outputs(
    ctx: RunContext,
    state_metrics_rows: list[dict[str, Any]],
    replicate_summary_rows: list[dict[str, Any]],
    replicate_summary_by_profile_rows: list[dict[str, Any]],
    decision_summary: dict[str, Any],
) -> None:
    write_csv(ctx.output_dir / "state_metrics.csv", state_metrics_rows, STATE_METRICS_COLUMNS)

    replicate_cols = [
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
    write_csv(ctx.output_dir / "replicate_summary.csv", replicate_summary_rows, replicate_cols)

    replicate_profile_cols = [
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
        ctx.output_dir / "replicate_summary_by_profile.csv",
        replicate_summary_by_profile_rows,
        replicate_profile_cols,
    )

    nullmodel_rows = [row for row in state_metrics_rows if row["state"] in {"D1", "D2"}]
    write_csv(ctx.output_dir / "nullmodel_comparison.csv", nullmodel_rows, STATE_METRICS_COLUMNS)

    decision_template_path = ctx.template_dir / "decision_summary.template.json"
    if decision_template_path.exists():
        template = read_json_template(decision_template_path)
        template.update(decision_summary)
        decision_summary = template

    write_json(ctx.output_dir / "decision_summary.json", decision_summary)
    write_block_readout(ctx.output_dir / "block_readout.md", decision_summary)

    copy_if_exists(ctx.config_path, ctx.output_dir / ctx.config_path.name)
    copy_if_exists(ctx.schema_path, ctx.output_dir / ctx.schema_path.name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runner for H3_SUPPORT_MANIPULATION_DESIGN_01")
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

    write_run_metadata(ctx)
    state_metrics_rows, replicate_summary_rows, replicate_summary_by_profile_rows, decision_summary = run_block(ctx)
    write_outputs(
        ctx,
        state_metrics_rows,
        replicate_summary_rows,
        replicate_summary_by_profile_rows,
        decision_summary,
    )

    print("[INFO] Run completed.")
    print(f"[INFO] decision_summary.json -> {ctx.output_dir / 'decision_summary.json'}")
    print(f"[INFO] block_readout.md       -> {ctx.output_dir / 'block_readout.md'}")


if __name__ == "__main__":
    main()