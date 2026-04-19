#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def load_summary(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data: dict = {
        "run_kind": None,
        "theta": None,
        "theta_crit": [],
        "n_edges": None,
        "n_components": None,
        "graph_diameter": None,
        "defined_pair_count": 0,
        "wrong_dispersion": None,
    }

    in_standard_pairs = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.startswith("run_kind:"):
            data["run_kind"] = line.split(":", 1)[1].strip()
        elif line.startswith("theta:"):
            data["theta"] = float(line.split(":", 1)[1].strip())
        elif line.startswith("theta_crit:"):
            rhs = line.split(":", 1)[1].strip()
            data["theta_crit"] = json.loads(rhs.replace("'", '"'))
        elif line.startswith("n_edges:"):
            data["n_edges"] = int(line.split(":", 1)[1].strip())
        elif line.startswith("connected_components:"):
            rhs = line.split(":", 1)[1].strip()
            comps = json.loads(rhs.replace("(", "[").replace(")", "]"))
            data["n_components"] = len(comps)
        elif line.startswith("graph_diameter:"):
            rhs = line.split(":", 1)[1].strip()
            data["graph_diameter"] = None if rhs == "None" else float(rhs)
        elif line.startswith("wrong_dispersion:"):
            data["wrong_dispersion"] = line.split(":", 1)[1].strip()
        elif line.startswith("standard_pairs:"):
            in_standard_pairs = True
        elif in_standard_pairs and line.startswith("bridge_predictions:"):
            in_standard_pairs = False
        elif in_standard_pairs and line.startswith("d0"):
            _, rhs = line.split(":", 1)
            if rhs.strip() != "None":
                data["defined_pair_count"] += 1

    return data


def theta_key(folder: Path) -> float:
    name = folder.name
    if not name.startswith("theta_"):
        raise ValueError(f"Unexpected folder name: {name}")
    return float(name.split("_", 1)[1])


def collect_case(root: Path) -> list[dict]:
    rows = []
    for child in sorted(root.iterdir(), key=theta_key):
        summary = child / "summary.txt"
        if summary.exists():
            rows.append(load_summary(summary))
    if not rows:
        raise FileNotFoundError(f"No summary.txt files found in {root}")
    return rows


def first_case_crit(case: list[dict]) -> list[float]:
    return [float(x) for x in case[0]["theta_crit"]]


def add_critical_lines(ax, crit_values: list[float], linestyle: str, linewidth: float, alpha: float, label: str | None):
    for i, tc in enumerate(crit_values):
        ax.axvline(
            tc,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=label if i == 0 else None,
        )


def style_axis(ax):
    ax.set_xscale("log")
    ax.grid(True, which="major", alpha=0.25)
    ax.grid(True, which="minor", alpha=0.10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Publication-style plot for K.0 / N.1a(alpha=0.5) / N.1a(alpha=2.0) on a shared theta axis."
    )
    ap.add_argument("--k0", default="results/n1a_scan/k0_t1", help="Directory with theta_* subfolders for K.0")
    ap.add_argument("--a05", default="results/n1a_scan/n1a_alpha_0p5_t1", help="Directory with theta_* subfolders for N.1a alpha=0.5")
    ap.add_argument("--a20", default="results/n1a_scan/n1a_alpha_2p0_t1", help="Directory with theta_* subfolders for N.1a alpha=2.0")
    ap.add_argument("--out", default="results/n1a_scan/k0_n1a_theta_comparison_publication.png", help="Output PNG")
    ap.add_argument("--title", default="Shared $\\theta$-axis comparison: K.0 vs wrong-dispersion controls", help="Plot title")
    args = ap.parse_args()

    k0 = collect_case(Path(args.k0))
    a05 = collect_case(Path(args.a05))
    a20 = collect_case(Path(args.a20))

    theta = [row["theta"] for row in k0]
    if theta != [row["theta"] for row in a05] or theta != [row["theta"] for row in a20]:
        raise ValueError("Theta grids do not match across the three cases.")

    k0_edges = [row["n_edges"] for row in k0]
    a05_edges = [row["n_edges"] for row in a05]
    a20_edges = [row["n_edges"] for row in a20]

    k0_pairs = [row["defined_pair_count"] / 3.0 for row in k0]
    a05_pairs = [row["defined_pair_count"] / 3.0 for row in a05]
    a20_pairs = [row["defined_pair_count"] / 3.0 for row in a20]

    k0_crit = first_case_crit(k0)
    a05_crit = first_case_crit(a05)
    a20_crit = first_case_crit(a20)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(8.4, 5.8),
        sharex=True,
        constrained_layout=True,
    )

    ax = axes[0]
    ax.plot(theta, k0_edges, linewidth=2.0, marker="o", markersize=4.5, label="K.0")
    ax.plot(theta, a05_edges, linewidth=1.8, marker="s", markersize=4.0, label=r"N.1a ($\alpha=0.5$)")
    ax.plot(theta, a20_edges, linewidth=1.8, marker="^", markersize=4.0, label=r"N.1a ($\alpha=2.0$)")
    ax.set_ylabel("Edges")
    ax.set_ylim(-0.2, 6.2)
    style_axis(ax)

    ax = axes[1]
    ax.plot(theta, k0_pairs, linewidth=2.0, marker="o", markersize=4.5, label="K.0")
    ax.plot(theta, a05_pairs, linewidth=1.8, marker="s", markersize=4.0, label=r"N.1a ($\alpha=0.5$)")
    ax.plot(theta, a20_pairs, linewidth=1.8, marker="^", markersize=4.0, label=r"N.1a ($\alpha=2.0$)")
    ax.set_ylabel("Defined pairs / 3")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylim(-0.05, 1.05)
    style_axis(ax)

    xmin = min(theta) * 0.92
    xmax = max(theta) * 1.08
    for ax in axes:
        ax.set_xlim(xmin, xmax)
        add_critical_lines(ax, k0_crit, ":", 1.3, 0.9, "K.0 critical values")
        add_critical_lines(ax, a05_crit, "--", 1.0, 0.55, r"N.1a $\alpha=0.5$ critical values")
        add_critical_lines(ax, a20_crit, "-.", 1.0, 0.55, r"N.1a $\alpha=2.0$ critical values")

    fig.suptitle(args.title, fontsize=12)
    axes[0].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.22),
        ncol=2,
        frameon=False,
    )

    axes[1].text(
        0.02,
        0.08,
        "Wrong dispersion shifts the transition windows:\n"
        r"$\alpha=2.0$ left, $\alpha=0.5$ right.",
        transform=axes[1].transAxes,
        fontsize=8.8,
        ha="left",
        va="bottom",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"),
    )

    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Saved plot to: {out}")


if __name__ == "__main__":
    main()
