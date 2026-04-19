from __future__ import annotations

import csv
import random
from pathlib import Path
from statistics import median
from typing import Any


PROJECT_ROOT = Path(
    "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/"
    "debroglie-phase-bridge/debroglie-phase-bridge/typ_b_analysis"
)

INPUT_CSV = PROJECT_ROOT / "data" / "original" / "h3_support_scores.csv"
SEEDS = [101, 202, 303, 404, 505]


def safe_float(x: Any) -> float:
    return float(x)


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "unit_id": row["unit_id"],
                    "baseline_score": safe_float(row["baseline_score"]),
                    "combined_score": safe_float(row["combined_score"]),
                    "delta_score_g": safe_float(row.get("delta_score_g", row["combined_score"]) ) - safe_float(row["baseline_score"])
                    if "delta_score_g" not in row or row["delta_score_g"] == ""
                    else safe_float(row["delta_score_g"]),
                    "is_support": int(row["is_support"]),
                    "is_neighbor": int(row["is_neighbor"]),
                    "export_class": row.get("export_class", ""),
                    "pair_i": row.get("pair_i", ""),
                    "pair_j": row.get("pair_j", ""),
                }
            )
    return rows


def median_or_nan(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(median(values))


def run_d2(rows: list[dict[str, Any]], seed: int) -> tuple[float, list[dict[str, Any]]]:
    rng = random.Random(seed + 10_000)

    n_support = sum(r["is_support"] for r in rows)
    indices = list(range(len(rows)))
    chosen_support = set(rng.sample(indices, k=n_support))

    annotated: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        new_row = dict(row)
        new_row["d2_is_support_effective"] = 1 if idx in chosen_support else 0
        new_row["d2_is_neighbor_effective"] = row["is_neighbor"]
        annotated.append(new_row)

    support_vals = [
        r["combined_score"]
        for r in annotated
        if r["d2_is_support_effective"] == 1
    ]
    neighbor_vals = [
        r["combined_score"]
        for r in annotated
        if r["d2_is_support_effective"] == 0 and r["d2_is_neighbor_effective"] == 1
    ]
    baseline_support_vals = [
        r["baseline_score"]
        for r in annotated
        if r["d2_is_support_effective"] == 1
    ]
    baseline_neighbor_vals = [
        r["baseline_score"]
        for r in annotated
        if r["d2_is_support_effective"] == 0 and r["d2_is_neighbor_effective"] == 1
    ]

    support_sep_combined = median_or_nan(support_vals) - median_or_nan(neighbor_vals)
    support_sep_baseline = median_or_nan(baseline_support_vals) - median_or_nan(baseline_neighbor_vals)
    gain_value = support_sep_combined - support_sep_baseline

    for r in annotated:
        score = r["combined_score"]
        if r["d2_is_support_effective"] == 1:
            r["d2_group"] = "effective_support"
            r["signed_contribution"] = score
        elif r["d2_is_neighbor_effective"] == 1:
            r["d2_group"] = "effective_neighbor"
            r["signed_contribution"] = -score
        else:
            r["d2_group"] = "inactive_other"
            r["signed_contribution"] = 0.0

    return gain_value, annotated


def summarize_seed(seed: int, gain_value: float, rows: list[dict[str, Any]]) -> None:
    print("=" * 90)
    print(f"SEED {seed}  |  D2 gain_value = {gain_value:.6f}")
    print()

    grouped: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        grouped.setdefault(r["export_class"], []).append(r)

    print("Per class summary:")
    for cls, cls_rows in grouped.items():
        eff_support = sum(r["d2_is_support_effective"] for r in cls_rows)
        eff_neighbor = sum(
            1 for r in cls_rows
            if r["d2_is_support_effective"] == 0 and r["d2_is_neighbor_effective"] == 1
        )
        mean_signed = sum(r["signed_contribution"] for r in cls_rows) / len(cls_rows)
        print(
            f"  {cls:8s}  effective_support={eff_support:2d}  "
            f"effective_neighbor={eff_neighbor:2d}  mean_signed_contribution={mean_signed:.6f}"
        )
    print()

    ranked = sorted(rows, key=lambda r: abs(r["signed_contribution"]), reverse=True)

    print("Top pair contributions:")
    for r in ranked[:12]:
        print(
            f"  {r['unit_id']:15s} "
            f"class={r['export_class']:8s} "
            f"group={r['d2_group']:16s} "
            f"orig_support={r['is_support']} "
            f"eff_support={r['d2_is_support_effective']} "
            f"neighbor={r['d2_is_neighbor_effective']} "
            f"baseline={r['baseline_score']:.6f} "
            f"combined={r['combined_score']:.6f} "
            f"delta_g={r['delta_score_g']:.6f} "
            f"signed={r['signed_contribution']:.6f}"
        )
    print()


def main() -> None:
    rows = load_rows(INPUT_CSV)
    for seed in SEEDS:
        gain_value, annotated = run_d2(rows, seed)
        summarize_seed(seed, gain_value, annotated)


if __name__ == "__main__":
    main()