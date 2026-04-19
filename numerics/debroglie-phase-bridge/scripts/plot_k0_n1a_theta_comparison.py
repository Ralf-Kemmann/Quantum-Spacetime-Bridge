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
            # rhs looks like: [0.1, 0.2, ...]
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


def extract_crit_union(*cases: list[dict]) -> list[float]:
    vals = []
    for case in cases:
        for row in case:
            vals.extend(float(x) for x in row["theta_crit"])
    return sorted(set(vals))


def first_case_crit(case: list[dict]) -> list[float]:
    return [float(x) for x in case[0]["theta_crit"]]


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Plot K.0 / N.1a(alpha=0.5) / N.1a(alpha=2.0) on a shared theta axis."
    )
    ap.add_argument("--k0", default="results/n1a_scan/k0_t1", help="Directory with theta_* subfolders for K.0")
    ap.add_argument("--a05", default="results/n1a_scan/n1a_alpha_0p5_t1", help="Directory with theta_* subfolders for N.1a alpha=0.5")
    ap.add_argument("--a20", default="results/n1a_scan/n1a_alpha_2p0_t1", help="Directory with theta_* subfolders for N.1a alpha=2.0")
    ap.add_argument("--out", default="results/n1a_scan/k0_n1a_theta_comparison.png", help="Output PNG")
    ap.add_argument("--title", default="K.0 vs N.1a on shared theta axis (t=1.0)", help="Plot title")
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

    k0_diam = [0.0 if row["graph_diameter"] is None else row["graph_diameter"] for row in k0]
    a05_diam = [0.0 if row["graph_diameter"] is None else row["graph_diameter"] for row in a05]
    a20_diam = [0.0 if row["graph_diameter"] is None else row["graph_diameter"] for row in a20]

    k0_crit = first_case_crit(k0)
    a05_crit = first_case_crit(a05)
    a20_crit = first_case_crit(a20)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.5), sharex=True, constrained_layout=True)

    # Panel 1: edges
    ax = axes[0]
    ax.plot(theta, k0_edges, marker="o", linewidth=2.0, label="K.0")
    ax.plot(theta, a05_edges, marker="s", linewidth=2.0, label=r"N.1a ($\alpha=0.5$)")
    ax.plot(theta, a20_edges, marker="^", linewidth=2.0, label=r"N.1a ($\alpha=2.0$)")
    ax.set_ylabel("n_edges")
    ax.set_ylim(-0.2, 6.2)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="upper right")

    # Panel 2: defined pair fraction
    ax = axes[1]
    ax.plot(theta, k0_pairs, marker="o", linewidth=2.0, label="K.0")
    ax.plot(theta, a05_pairs, marker="s", linewidth=2.0, label=r"N.1a ($\alpha=0.5$)")
    ax.plot(theta, a20_pairs, marker="^", linewidth=2.0, label=r"N.1a ($\alpha=2.0$)")
    ax.set_ylabel("defined pairs / 3")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, which="both", alpha=0.25)

    # Panel 3: graph diameter
    ax = axes[2]
    ax.plot(theta, k0_diam, marker="o", linewidth=2.0, label="K.0")
    ax.plot(theta, a05_diam, marker="s", linewidth=2.0, label=r"N.1a ($\alpha=0.5$)")
    ax.plot(theta, a20_diam, marker="^", linewidth=2.0, label=r"N.1a ($\alpha=2.0$)")
    ax.set_ylabel("graph_diameter")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylim(-0.1, max(k0_diam + a05_diam + a20_diam) + 0.5)
    ax.grid(True, which="both", alpha=0.25)

    # Shared x settings + critical lines
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlim(min(theta) * 0.95, max(theta) * 1.05)

        for i, tc in enumerate(k0_crit):
            ax.axvline(tc, linestyle=":", linewidth=1.4, alpha=0.85,
                       label="K.0 crit" if (ax is axes[0] and i == 0) else None)
        for i, tc in enumerate(a05_crit):
            ax.axvline(tc, linestyle="--", linewidth=1.1, alpha=0.55,
                       label=r"N.1a $\alpha=0.5$ crit" if (ax is axes[0] and i == 0) else None)
        for i, tc in enumerate(a20_crit):
            ax.axvline(tc, linestyle="-.", linewidth=1.1, alpha=0.55,
                       label=r"N.1a $\alpha=2.0$ crit" if (ax is axes[0] and i == 0) else None)

    axes[0].legend(loc="upper right")
    fig.suptitle(args.title, fontsize=13)

    axes[0].text(
        0.5, 1.12,
        "Vertical lines mark critical theta values of K.0 and both wrong-dispersion controls.",
        transform=axes[0].transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
    )

    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved plot to: {out}")


if __name__ == "__main__":
    main()
