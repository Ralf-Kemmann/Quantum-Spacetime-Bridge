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

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "h3_d1_d2_divergence.yaml"
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "h3_d1_d2_divergence.schema.json"
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


def now_run_id(prefix: str = "H3D12DIV01") -> str:
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
        "is_support",
        "is_neighbor",
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
                    "is_support": int(row["is_support"]),
                    "is_neighbor": int(row["is_neighbor"]),
                    "export_class": row.get("export_class", ""),
                    "pair_i": row.get("pair_i", ""),
                    "pair_j": row.get("pair_j", ""),
                    "delta_score_g": safe_float(row.get("delta_score_g", math.nan)),
                }
            )
    return rows


def get_profile_factor(config: dict[str, Any], parameter_profile: str) -> float:
    profiles = config["replication"]["parameter_perturbations"]["perturbation_profiles"]
    return safe_float(profiles[parameter_profile]["factor"], 1.0)


def apply_nullmodel(
    rows: list[dict[str, Any]],
    state_name: str,
    seed: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

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

    raise ValueError(f"Unknown nullmodel state: {state_name}")


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


def effective_support_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {str(r["unit_id"]) for r in rows if int(r["is_support_effective"]) == 1}


def jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def symmetric_diff_fraction(a: set[str], b: set[str], universe_size: int) -> float:
    if universe_size <= 0:
        return 0.0
    return len(a ^ b) / universe_size


def compute_state_metrics(
    config: dict[str, Any],
    rows: list[dict[str, Any]],
    state_name: str,
    state_cfg: dict[str, Any],
    seed: int,
    parameter_profile: str,
) -> dict[str, Any]:
    profile_factor = get_profile_factor(config, parameter_profile)
    state_rows = apply_nullmodel(rows=rows, state_name=state_name, seed=seed)

    support_sep_baseline = compute_support_separation(state_rows, "baseline_score")
    support_sep_combined = compute_support_separation(state_rows, "combined_score_effective")

    gain_value = (
        support_sep_combined - support_sep_baseline
        if not (math.isnan(support_sep_baseline) or math.isnan(support_sep_combined))
        else math.nan
    )

    null_variant = state_cfg.get("support_manipulation", {}).get("variant")
    eff_support_ids = effective_support_ids(state_rows)
    eff_neighbor_count = sum(
        1 for r in state_rows
        if int(r["is_support_effective"]) == 0 and int(r["is_neighbor_effective"]) == 1
    )

    if math.isnan(gain_value):
        combined_status_stability = "unstable"
        auxiliary_compatibility = "undefined"
    elif gain_value >= 0:
        combined_status_stability = "stable"
        auxiliary_compatibility = "noise_compatible"
    else:
        combined_status_stability = "destabilized"
        auxiliary_compatibility = "not_compatible"

    sign_stability = 0.0 if math.isnan(gain_value) else (1.0 if gain_value > 0 else 0.0)
    replicate_consistency = sign_stability
    null_noise_margin = 0.02

    return {
        "seed": seed,
        "parameter_profile": parameter_profile,
        "state": state_name,
        "null_variant": null_variant,
        "profile_factor": round(profile_factor, 6),
        "gain_value": round(gain_value, 6) if not math.isnan(gain_value) else math.nan,
        "support_sep_baseline": round(support_sep_baseline, 6) if not math.isnan(support_sep_baseline) else math.nan,
        "support_sep_combined": round(support_sep_combined, 6) if not math.isnan(support_sep_combined) else math.nan,
        "neighbor_shift_signal": classify_shift_signal(gain_value),
        "combined_status_stability": combined_status_stability,
        "auxiliary_compatibility": auxiliary_compatibility,
        "sign_stability": round(sign_stability, 6),
        "replicate_consistency": round(replicate_consistency, 6),
        "positive_direction_fraction": round(1.0 if gain_value > 0 else 0.0, 6) if not math.isnan(gain_value) else 0.0,
        "null_noise_margin": round(null_noise_margin, 6),
        "effective_support_count": len(eff_support_ids),
        "effective_neighbor_count": eff_neighbor_count,
        "effective_support_unit_ids": "|".join(sorted(eff_support_ids)),
    }


def build_assignment_comparison(
    rows_D1: list[dict[str, Any]],
    rows_D2: list[dict[str, Any]],
    seed: int,
    parameter_profile: str,
) -> dict[str, Any]:
    support_D1 = effective_support_ids(rows_D1)
    support_D2 = effective_support_ids(rows_D2)
    universe_size = len(rows_D1)

    overlap = len(support_D1 & support_D2)
    jac = jaccard(support_D1, support_D2)
    changed_fraction = symmetric_diff_fraction(support_D1, support_D2, universe_size)

    return {
        "seed": seed,
        "parameter_profile": parameter_profile,
        "effective_support_count_D1": len(support_D1),
        "effective_support_count_D2": len(support_D2),
        "overlap_support": overlap,
        "jaccard_support_D1_vs_D2": round(jac, 6),
        "changed_assignment_fraction_D1_vs_D2": round(changed_fraction, 6),
        "effective_support_unit_ids_D1": "|".join(sorted(support_D1)),
        "effective_support_unit_ids_D2": "|".join(sorted(support_D2)),
    }


def build_divergence_summary(
    metrics_D1: dict[str, Any],
    metrics_D2: dict[str, Any],
    assignment_cmp: dict[str, Any],
) -> dict[str, Any]:
    gain_D1 = safe_float(metrics_D1["gain_value"])
    gain_D2 = safe_float(metrics_D2["gain_value"])
    sep_D1 = safe_float(metrics_D1["support_sep_combined"])
    sep_D2 = safe_float(metrics_D2["support_sep_combined"])

    delta_gain = gain_D2 - gain_D1 if not (math.isnan(gain_D1) or math.isnan(gain_D2)) else math.nan
    delta_sep = sep_D2 - sep_D1 if not (math.isnan(sep_D1) or math.isnan(sep_D2)) else math.nan

    return {
        "seed": metrics_D1["seed"],
        "parameter_profile": metrics_D1["parameter_profile"],
        "gain_D1": round(gain_D1, 6) if not math.isnan(gain_D1) else math.nan,
        "gain_D2": round(gain_D2, 6) if not math.isnan(gain_D2) else math.nan,
        "delta_gain_D2_minus_D1": round(delta_gain, 6) if not math.isnan(delta_gain) else math.nan,
        "support_sep_combined_D1": round(sep_D1, 6) if not math.isnan(sep_D1) else math.nan,
        "support_sep_combined_D2": round(sep_D2, 6) if not math.isnan(sep_D2) else math.nan,
        "delta_support_sep_combined_D2_minus_D1": round(delta_sep, 6) if not math.isnan(delta_sep) else math.nan,
        "jaccard_support_D1_vs_D2": assignment_cmp["jaccard_support_D1_vs_D2"],
        "changed_assignment_fraction_D1_vs_D2": assignment_cmp["changed_assignment_fraction_D1_vs_D2"],
    }


def detect_algorithmic_divergence(assignment_rows: list[dict[str, Any]]) -> bool:
    return any(safe_float(r["changed_assignment_fraction_D1_vs_D2"]) > 0.0 for r in assignment_rows)


def detect_outcome_divergence(summary_rows: list[dict[str, Any]], eps: float = 1e-9) -> bool:
    return any(abs(safe_float(r["delta_gain_D2_minus_D1"])) > eps for r in summary_rows)


def detect_practical_collapse(
    assignment_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    jaccard_tol: float = 0.999999,
    delta_tol: float = 1e-9,
) -> bool:
    all_assign_same = all(safe_float(r["jaccard_support_D1_vs_D2"]) >= jaccard_tol for r in assignment_rows)
    all_gain_same = all(abs(safe_float(r["delta_gain_D2_minus_D1"])) <= delta_tol for r in summary_rows)
    return all_assign_same and all_gain_same


def build_decision_summary(
    ctx: RunContext,
    assignment_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    alg_div = detect_algorithmic_divergence(assignment_rows)
    out_div = detect_outcome_divergence(summary_rows)
    collapse = detect_practical_collapse(assignment_rows, summary_rows)

    median_jaccard = median_of(assignment_rows, "jaccard_support_D1_vs_D2")
    median_delta_gain = median_of(summary_rows, "delta_gain_D2_minus_D1")
    median_delta_sep = median_of(summary_rows, "delta_support_sep_combined_D2_minus_D1")

    if collapse:
        final_assessment = "practical_collapse"
    elif alg_div and out_div:
        final_assessment = "distinct_nullmodels"
    elif alg_div and not out_div:
        final_assessment = "distinct_mechanism_same_outcome"
    else:
        final_assessment = "unclear_or_weak_divergence"

    return {
        "block_id": ctx.config["block_id"],
        "source_block": ctx.config["source_block"],
        "algorithmic_divergence_detected": alg_div,
        "outcome_divergence_detected": out_div,
        "practical_collapse_detected": collapse,
        "median_jaccard_support": round(median_jaccard, 6) if not math.isnan(median_jaccard) else None,
        "median_delta_gain_D2_minus_D1": round(median_delta_gain, 6) if not math.isnan(median_delta_gain) else None,
        "median_delta_support_sep_combined_D2_minus_D1": round(median_delta_sep, 6) if not math.isnan(median_delta_sep) else None,
        "final_assessment": final_assessment,
    }


def write_readout(path: Path, decision_summary: dict[str, Any]) -> None:
    text = f"""# H3_D1_D2_DIVERGENCE_01

## Status
completed

## Zweck
Prüfung, ob D1 und D2 im aktuellen H3-Setup algorithmisch und outcome-seitig wirklich verschieden wirken.

## Kernbefund
- algorithmic_divergence_detected: {decision_summary["algorithmic_divergence_detected"]}
- outcome_divergence_detected: {decision_summary["outcome_divergence_detected"]}
- practical_collapse_detected: {decision_summary["practical_collapse_detected"]}
- median_jaccard_support: {decision_summary["median_jaccard_support"]}
- median_delta_gain_D2_minus_D1: {decision_summary["median_delta_gain_D2_minus_D1"]}
- median_delta_support_sep_combined_D2_minus_D1: {decision_summary["median_delta_support_sep_combined_D2_minus_D1"]}
- final_assessment: {decision_summary["final_assessment"]}

## Projektinterne Lesart
Meta-Test auf die Trennschärfe der beiden Nullmodelle D1 und D2.

"""
    path.write_text(text, encoding="utf-8")


STATE_METRICS_COLUMNS = [
    "run_id",
    "seed",
    "parameter_profile",
    "state",
    "null_variant",
    "profile_factor",
    "gain_value",
    "support_sep_baseline",
    "support_sep_combined",
    "neighbor_shift_signal",
    "combined_status_stability",
    "auxiliary_compatibility",
    "sign_stability",
    "replicate_consistency",
    "positive_direction_fraction",
    "null_noise_margin",
    "effective_support_count",
    "effective_neighbor_count",
    "effective_support_unit_ids",
]


ASSIGNMENT_COMPARISON_COLUMNS = [
    "seed",
    "parameter_profile",
    "effective_support_count_D1",
    "effective_support_count_D2",
    "overlap_support",
    "jaccard_support_D1_vs_D2",
    "changed_assignment_fraction_D1_vs_D2",
    "effective_support_unit_ids_D1",
    "effective_support_unit_ids_D2",
]


DIVERGENCE_SUMMARY_COLUMNS = [
    "seed",
    "parameter_profile",
    "gain_D1",
    "gain_D2",
    "delta_gain_D2_minus_D1",
    "support_sep_combined_D1",
    "support_sep_combined_D2",
    "delta_support_sep_combined_D2_minus_D1",
    "jaccard_support_D1_vs_D2",
    "changed_assignment_fraction_D1_vs_D2",
]


def run_block(
    ctx: RunContext,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    input_rows = load_input_rows(ctx.config)
    seeds = list(ctx.config["replication"]["seeds"])
    profiles = list(ctx.config["replication"]["parameter_perturbations"]["perturbation_profiles"].keys())
    state_defs = ctx.config["states"]

    state_metrics_rows: list[dict[str, Any]] = []
    assignment_rows: list[dict[str, Any]] = []
    divergence_summary_rows: list[dict[str, Any]] = []

    for seed in seeds:
        for parameter_profile in profiles:
            metrics_by_state: dict[str, dict[str, Any]] = {}
            rows_by_state: dict[str, list[dict[str, Any]]] = {}

            for state_name in ["D1", "D2"]:
                metrics = compute_state_metrics(
                    config=ctx.config,
                    rows=input_rows,
                    state_name=state_name,
                    state_cfg=state_defs[state_name],
                    seed=int(seed),
                    parameter_profile=str(parameter_profile),
                )
                metrics["run_id"] = ctx.run_id
                state_metrics_rows.append(metrics)
                metrics_by_state[state_name] = metrics

                rows_by_state[state_name] = apply_nullmodel(
                    rows=input_rows,
                    state_name=state_name,
                    seed=int(seed),
                )

            assignment_cmp = build_assignment_comparison(
                rows_D1=rows_by_state["D1"],
                rows_D2=rows_by_state["D2"],
                seed=int(seed),
                parameter_profile=str(parameter_profile),
            )
            assignment_rows.append(assignment_cmp)

            divergence_summary_rows.append(
                build_divergence_summary(
                    metrics_D1=metrics_by_state["D1"],
                    metrics_D2=metrics_by_state["D2"],
                    assignment_cmp=assignment_cmp,
                )
            )

    decision_summary = build_decision_summary(
        ctx=ctx,
        assignment_rows=assignment_rows,
        summary_rows=divergence_summary_rows,
    )

    return state_metrics_rows, assignment_rows, divergence_summary_rows, decision_summary


def write_outputs(
    ctx: RunContext,
    state_metrics_rows: list[dict[str, Any]],
    assignment_rows: list[dict[str, Any]],
    divergence_summary_rows: list[dict[str, Any]],
    decision_summary: dict[str, Any],
) -> None:
    write_csv(
        ctx.output_dir / "d1_d2_divergence_state_metrics.csv",
        state_metrics_rows,
        STATE_METRICS_COLUMNS,
    )
    write_csv(
        ctx.output_dir / "d1_d2_assignment_comparison.csv",
        assignment_rows,
        ASSIGNMENT_COMPARISON_COLUMNS,
    )
    write_csv(
        ctx.output_dir / "d1_d2_divergence_summary.csv",
        divergence_summary_rows,
        DIVERGENCE_SUMMARY_COLUMNS,
    )
    write_json(ctx.output_dir / "d1_d2_divergence_decision_summary.json", decision_summary)
    write_readout(ctx.output_dir / "d1_d2_divergence_readout.md", decision_summary)

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
    parser = argparse.ArgumentParser(description="Runner for H3_D1_D2_DIVERGENCE_01")
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

    state_metrics_rows, assignment_rows, divergence_summary_rows, decision_summary = run_block(ctx)
    write_outputs(ctx, state_metrics_rows, assignment_rows, divergence_summary_rows, decision_summary)

    print("[INFO] Run completed.")
    print(f"[INFO] d1_d2_divergence_decision_summary.json -> {ctx.output_dir / 'd1_d2_divergence_decision_summary.json'}")
    print(f"[INFO] d1_d2_divergence_readout.md           -> {ctx.output_dir / 'd1_d2_divergence_readout.md'}")


if __name__ == "__main__":
    main()
