#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


MEASURES = [
    ("natural_connectivity", "Natural connectivity"),
    ("weighted_clustering", "Weighted clustering"),
    ("global_efficiency", "Global efficiency"),
]

KERNEL_ORDER = ["abs", "positive", "negative"]
REF_CASES = ["k0", "n1a_alpha_0p5", "n1a_alpha_2p0"]
REF_LABELS = {
    "k0": "K.0",
    "n1a_alpha_0p5": r"N.1a ($\alpha=0.5$)",
    "n1a_alpha_2p0": r"N.1a ($\alpha=2.0$)",
}
MARKERS = {
    "k0": "o",
    "n1a_alpha_0p5": "s",
    "n1a_alpha_2p0": "^",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_ref_value(ref_rows: list[dict], case: str, kernel_mode: str, measure: str):
    for row in ref_rows:
        if row["case"] == case and row["kernel_mode"] == kernel_mode:
            return row[measure]
    return None


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Plot N.0 weighted-measure ensemble against K.0 and N.1a references."
    )
    ap.add_argument(
        "--seed-rows",
        default="results/m2_ensemble/comparisons/m2_n0_ensemble_seed_rows.json",
        help="Path to N.0 seed rows JSON",
    )
    ap.add_argument(
        "--refs",
        default="results/m2_ensemble/comparisons/m2_n0_ensemble_refs.json",
        help="Path to fixed reference rows JSON",
    )
    ap.add_argument(
        "--out-prefix",
        default="results/m2_ensemble/comparisons/m2_n0_ensemble_compare",
        help="Output prefix without suffix",
    )
    args = ap.parse_args()

    seed_rows = load_json(Path(args.seed_rows))
    ref_rows = load_json(Path(args.refs))
    out_prefix = Path(args.out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    for measure_key, measure_label in MEASURES:
        fig, axes = plt.subplots(
            1,
            len(KERNEL_ORDER),
            figsize=(10.8, 3.8),
            constrained_layout=True,
        )

        if len(KERNEL_ORDER) == 1:
            axes = [axes]

        for ax, kernel_mode in zip(axes, KERNEL_ORDER):
            vals = [row[measure_key] for row in seed_rows if row["kernel_mode"] == kernel_mode]
            # N.0 ensemble as jitter-free vertical strip at x=0
            ax.scatter([0.0] * len(vals), vals, alpha=0.8, label="N.0 seeds")

            for i, case in enumerate(REF_CASES, start=1):
                ref_val = get_ref_value(ref_rows, case, kernel_mode, measure_key)
                if ref_val is None:
                    continue
                ax.scatter(
                    [float(i)],
                    [ref_val],
                    marker=MARKERS[case],
                    s=70,
                    label=REF_LABELS[case] if kernel_mode == "abs" else None,
                )

            ax.set_title(kernel_mode, fontsize=10)
            ax.set_xticks([0.0, 1.0, 2.0, 3.0], ["N.0", "K.0", r"N.1a 0.5", r"N.1a 2.0"])
            ax.set_ylabel(measure_label if kernel_mode == "abs" else "")
            ax.grid(True, alpha=0.25)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        axes[0].legend(loc="best", frameon=False)
        fig.suptitle(f"M.2.4.2 — {measure_label}: N.0 ensemble vs K.0 / N.1a", fontsize=12)
        out_path = out_prefix.with_name(out_prefix.name + f"_{measure_key}.png")
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to: {out_path}")


if __name__ == "__main__":
    main()
