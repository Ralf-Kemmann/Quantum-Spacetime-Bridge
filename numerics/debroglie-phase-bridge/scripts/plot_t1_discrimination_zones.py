#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


D_ZONES = [
    ("D1", 1e-3, 0.011, "triviale Vollverbindung"),
    ("D2", 0.015, 0.023, "frühe Erosion"),
    ("D3", 0.023, 0.033, "erste Diskriminationszone"),
    ("D4", 0.033, 0.046, "Haupt-Kippband"),
    ("D5", 0.046, 0.055, "Fragmentierungsdomäne"),
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_k0_critical_values(k0_intervals: list[dict]) -> list[float]:
    return sorted({float(row["theta_min"]) for row in k0_intervals if float(row["theta_min"]) > 0.0})


def pair_defined_mean(row: dict) -> float:
    pair_stats = row["pair_stats"]
    vals = [
        float(pair_stats["d03_minus_d01"]["defined_fraction"]),
        float(pair_stats["d03_minus_d12"]["defined_fraction"]),
        float(pair_stats["d02_minus_d13"]["defined_fraction"]),
    ]
    return sum(vals) / len(vals)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Plot D1–D5 discrimination zones for K.0 vs N.0 on shared theta axis."
    )
    ap.add_argument(
        "--k0-intervals",
        default="results/t1/k0_reference_theta_map/k0_theta_intervals.json",
    )
    ap.add_argument(
        "--n0-aggregate",
        default="results/t1/n0_theta_ensemble/n0_theta_aggregate.json",
    )
    ap.add_argument(
        "--out",
        default="results/t1/k0_vs_n0_theta/discrimination_zones.png",
    )
    ap.add_argument(
        "--title",
        default="K.0 vs N.0 on shared theta axis",
    )
    args = ap.parse_args()

    k0_intervals = load_json(Path(args.k0_intervals))
    n0_aggregate = load_json(Path(args.n0_aggregate))

    theta = [float(row["theta"]) for row in n0_aggregate]
    fully_connected = [float(row["fully_connected_fraction"]) for row in n0_aggregate]
    defined_mean = [pair_defined_mean(row) for row in n0_aggregate]
    k0_crit = extract_k0_critical_values(k0_intervals)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)

    zone_colors = {
        "D1": "#d9d9d9",
        "D2": "#fee08b",
        "D3": "#fdae61",
        "D4": "#f46d43",
        "D5": "#d73027",
    }

    # Hintergrundbänder
    for name, x0, x1, _label in D_ZONES:
        ax.axvspan(x0, x1, alpha=0.16, color=zone_colors[name], lw=0)
        xmid = (x0 * x1) ** 0.5
        ax.text(
            xmid,
            1.01,
            name,
            ha="center",
            va="bottom",
            transform=ax.get_xaxis_transform(),
            fontsize=10,
            fontweight="bold",
            clip_on=False,
        )

    # N.0-Kurven
    ax.plot(theta, fully_connected, label="N.0 full connectivity", linewidth=2.2)
    ax.plot(theta, defined_mean, label="N.0 mean defined-pair fraction", linewidth=2.0, linestyle="--")

    # K.0-Kritwerte
    for i, tc in enumerate(k0_crit):
        ax.axvline(
            tc,
            linestyle=":",
            linewidth=1.8,
            label="K.0 critical values" if i == 0 else None,
        )

    # Annotationen: bewusst sparsamer und stabiler
    ax.text(
        0.028,
        0.83,
        "θ ≈ 0.03:\nK.0 noch vor\nerstem Kritwert",
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.75, edgecolor="none"),
    )
    ax.text(
        0.037,
        0.63,
        "D4:\nstärkste\nVergleichszone",
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.75, edgecolor="none"),
    )

    ax.set_xscale("log")
    ax.set_xlim(min(theta), max(theta))
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("Fraction")
    ax.set_title(args.title)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="lower left")

    # Caption direkt an die Achse statt fig.text
    ax.text(
        0.5,
        -0.18,
        (
            "D1–D5 markieren die gemeinsamen θ-Regime von K.0 und N.0. "
            "Die stärksten Vergleichszonen sind D3 und D4: "
            "Dort bleibt K.0 noch geordnet, während N.0 bereits kippt."
        ),
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=9,
    )

    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"Saved plot to: {out_path}")


if __name__ == "__main__":
    main()
