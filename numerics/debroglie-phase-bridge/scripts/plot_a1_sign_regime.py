#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


CASE_ORDER = ["k0", "n1a_alpha_0p5", "n1a_alpha_2p0"]
CASE_LABELS = {
    "k0": "K.0",
    "n1a_alpha_0p5": r"N.1a ($\alpha=0.5$)",
    "n1a_alpha_2p0": r"N.1a ($\alpha=2.0$)",
}
KERNEL_ORDER = ["abs", "positive", "negative"]
KERNEL_LABELS = {
    "abs": "abs",
    "positive": "positive",
    "negative": "negative",
}
MARKERS = {
    "abs": "o",
    "positive": "s",
    "negative": "^",
}
LINESTYLES = {
    "abs": "-",
    "positive": "--",
    "negative": "-.",
}


def load_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append(
                {
                    "case": row["case"],
                    "theta": float(row["theta"]),
                    "kernel_mode": row["kernel_mode"],
                    "n_edges": int(row["n_edges"]),
                    "n_components": int(row["n_components"]),
                    "graph_diameter": None if row["graph_diameter"] in {"", "None"} else float(row["graph_diameter"]),
                    "defined_pair_fraction": float(row["defined_pair_fraction"]),
                    "topology_label": row["topology_label"],
                }
            )
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


def group_rows(rows: list[dict]) -> dict[str, dict[str, list[dict]]]:
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["case"]][row["kernel_mode"]].append(row)

    for case in grouped:
        for kernel in grouped[case]:
            grouped[case][kernel] = sorted(grouped[case][kernel], key=lambda r: r["theta"])
    return grouped


def plot_metric(
    grouped: dict[str, dict[str, list[dict]]],
    metric: str,
    ylabel: str,
    outpath: Path,
    title: str,
) -> None:
    fig, axes = plt.subplots(
        len(CASE_ORDER),
        1,
        figsize=(8.6, 7.0),
        sharex=True,
        constrained_layout=True,
    )

    if len(CASE_ORDER) == 1:
        axes = [axes]

    for ax, case in zip(axes, CASE_ORDER):
        for kernel in KERNEL_ORDER:
            rows = grouped.get(case, {}).get(kernel, [])
            if not rows:
                continue
            x = [r["theta"] for r in rows]
            y = []
            for r in rows:
                value = r[metric]
                if value is None:
                    value = 0.0
                y.append(value)

            ax.plot(
                x,
                y,
                marker=MARKERS[kernel],
                linestyle=LINESTYLES[kernel],
                linewidth=1.8 if kernel == "abs" else 1.5,
                markersize=4.5,
                label=KERNEL_LABELS[kernel],
            )

        ax.set_xscale("log")
        ax.set_ylabel(ylabel)
        ax.set_title(CASE_LABELS.get(case, case), fontsize=10)
        ax.grid(True, which="major", alpha=0.25)
        ax.grid(True, which="minor", alpha=0.10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[0].legend(loc="upper right", frameon=False)
    axes[-1].set_xlabel(r"$\theta$")
    fig.suptitle(title, fontsize=12)

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"Saved plot to: {outpath}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="A.1.4.3 plot generator from a1_sign_scan.csv"
    )
    ap.add_argument(
        "--csv",
        default="results/a1_sign_scan/a1_sign_scan.csv",
        help="Path to a1_sign_scan.csv",
    )
    ap.add_argument(
        "--out-prefix",
        default="results/a1_sign_scan/a1_sign_regime",
        help="Output prefix without extension suffix",
    )
    args = ap.parse_args()

    csv_path = Path(args.csv)
    rows = load_rows(csv_path)
    grouped = group_rows(rows)

    prefix = Path(args.out_prefix)

    plot_metric(
        grouped=grouped,
        metric="n_edges",
        ylabel="Edges",
        outpath=prefix.with_name(prefix.name + "_edges.png"),
        title="Negative kernel support as a regime pattern",
    )

    plot_metric(
        grouped=grouped,
        metric="defined_pair_fraction",
        ylabel="Defined pairs / 3",
        outpath=prefix.with_name(prefix.name + "_pairs.png"),
        title="Negative kernel support as a regime pattern",
    )


if __name__ == "__main__":
    main()
