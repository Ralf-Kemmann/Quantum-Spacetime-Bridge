#!/usr/bin/env python3
"""Generate draft explanatory figures for QSB-ST PUBLIC01.

The figures are publication-facing draft diagrams only. They do not compute
scientific results and do not quantify real degeneracy.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Rectangle


FIGURE_DIR = Path("figures")
SUMMARY_PATH = Path("runs/QSB-ST-IDSPACE-CPNS06/minimal_schema_validation_open/summary.json")

BG = "#f8f7f3"
INK = "#24323a"
MUTED = "#6f7d84"
BLUE = "#2f6f9f"
TEAL = "#3b9a8f"
GOLD = "#d49a2a"
GREEN = "#5f9d73"
RED_SOFT = "#b96b5d"
LAYER = "#ffffff"
LINE = "#c9d1d3"


def setup_canvas(width: float = 12.8, height: float = 7.2):
    fig, ax = plt.subplots(figsize=(width, height), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def add_box(ax, xy, width, height, text, *, face=LAYER, edge=LINE, color=INK, fontsize=12):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.2,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        color=color,
        fontsize=fontsize,
        linespacing=1.18,
    )
    return box


def add_arrow(ax, start, end, *, color=MUTED, lw=1.8, mutation_scale=16):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=mutation_scale,
        linewidth=lw,
        color=color,
        shrinkA=4,
        shrinkB=4,
    )
    ax.add_patch(arrow)
    return arrow


def add_header(ax, title, subtitle):
    ax.text(0.05, 0.94, title, ha="left", va="top", fontsize=21, color=INK, weight="bold")
    ax.text(0.05, 0.895, subtitle, ha="left", va="top", fontsize=12.5, color=MUTED)


def save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def figure_01():
    fig, ax = setup_canvas()
    add_header(
        ax,
        "QSB-ST method-gate route",
        "A cautious path from diagnostic closure to schema/example validation",
    )

    nodes = [
        ("WIFM01-D\nclosure", "minimal diagnostic\nroute closed"),
        ("BRIDGE-NATURE-01B\ngate", "no default\nescalation"),
        ("IDSPACE/CPNS\ndefinitions", "identity and\nambiguity safeguards"),
        ("CPNS04\nschema scaffold", "minimal records\nand examples"),
        ("CPNS06\nvalidator", "schema/example\nconsistency only"),
    ]
    xs = [0.08, 0.28, 0.49, 0.70, 0.88]
    y = 0.53
    w = 0.145
    h = 0.19
    for idx, ((title, sub), x) in enumerate(zip(nodes, xs)):
        edge = BLUE if idx in (0, 4) else TEAL
        add_box(ax, (x - w / 2, y - h / 2), w, h, f"{title}\n\n{sub}", edge=edge, fontsize=10.4)
        if idx < len(xs) - 1:
            add_arrow(ax, (x + w / 2 + 0.008, y), (xs[idx + 1] - w / 2 - 0.008, y), color=MUTED)

    ax.plot([0.07, 0.93], [0.30, 0.30], color=LINE, lw=1)
    ax.text(
        0.5,
        0.24,
        "Method path, not a discovery ladder: each station narrows what may be claimed.",
        ha="center",
        va="center",
        color=INK,
        fontsize=13,
    )
    ax.text(
        0.5,
        0.16,
        "No Bridge confirmation  |  No diagnostic specificity claim  |  No physical validation",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=11,
    )
    save(fig, FIGURE_DIR / "public01_figure01_red_thread_flow.png")


def figure_02():
    fig, ax = setup_canvas()
    add_header(
        ax,
        "Readable fingerprints are not identity resolution",
        "Fingerprint-Raum and Identitaets-Raum are related by declared rules, not by visual similarity alone",
    )

    lower = FancyBboxPatch(
        (0.08, 0.16),
        0.84,
        0.27,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor="#edf5f6",
        edgecolor="#a7c7ca",
        linewidth=1.4,
    )
    upper = FancyBboxPatch(
        (0.08, 0.63),
        0.84,
        0.22,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor="#fff7e4",
        edgecolor="#ddb868",
        linewidth=1.4,
    )
    ax.add_patch(lower)
    ax.add_patch(upper)
    ax.text(0.11, 0.39, "Fingerprint-Raum", color=BLUE, fontsize=16, weight="bold")
    ax.text(0.11, 0.82, "Identitaets-Raum", color=GOLD, fontsize=16, weight="bold")
    ax.text(0.11, 0.34, "diagnostic points, distances, neighborhoods", color=INK, fontsize=11)
    ax.text(0.11, 0.77, "same / different / ambiguous / outside scope", color=INK, fontsize=11)

    pts = [(0.23, 0.25), (0.31, 0.30), (0.39, 0.23), (0.53, 0.32), (0.61, 0.24), (0.72, 0.31)]
    for i, (x, y) in enumerate(pts):
        ax.add_patch(Circle((x, y), 0.022, facecolor=TEAL if i < 3 else BLUE, edgecolor="white", linewidth=1))
    for a, b in [(0, 1), (1, 2), (3, 4), (4, 5)]:
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color="#8eb7bd", lw=1)

    states = [
        (0.23, "same\ncandidate", GREEN),
        (0.42, "different\ncandidate", BLUE),
        (0.61, "ambiguous\nunresolved", GOLD),
        (0.80, "outside\nscope", RED_SOFT),
    ]
    for x, label, col in states:
        add_box(ax, (x - 0.065, 0.675), 0.13, 0.095, label, edge=col, fontsize=9.8)

    passage = FancyBboxPatch(
        (0.34, 0.465),
        0.32,
        0.10,
        boxstyle="round,pad=0.018,rounding_size=0.02",
        facecolor="#ffffff",
        edgecolor=GOLD,
        linewidth=1.4,
    )
    ax.add_patch(passage)
    ax.text(
        0.50,
        0.515,
        "guarded passage:\nmaps + equivalence rules + ambiguity handling",
        ha="center",
        va="center",
        fontsize=10.2,
        color=INK,
    )
    add_arrow(ax, (0.50, 0.43), (0.50, 0.465), color=GOLD)
    add_arrow(ax, (0.50, 0.565), (0.50, 0.63), color=GOLD)

    ax.text(
        0.50,
        0.08,
        "Geometric readability below does not automatically decide identity above.",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=12,
    )
    save(fig, FIGURE_DIR / "public01_figure02_fingerprint_vs_identity_space.png")


def figure_03():
    fig, ax = setup_canvas()
    add_header(
        ax,
        "Same-looking can remain unresolved",
        "Ambiguity is a valid result state until identity definitions and CPNS constraints are fixed",
    )

    # Two near-looking fingerprint clusters.
    left_center = (0.28, 0.53)
    right_center = (0.42, 0.52)
    for center, name in [(left_center, "fingerprint A"), (right_center, "fingerprint B")]:
        x0, y0 = center
        for dx, dy in [(-0.035, 0.025), (0.015, 0.04), (0.045, -0.015), (-0.01, -0.035)]:
            ax.add_patch(Circle((x0 + dx, y0 + dy), 0.018, facecolor="#b7d7d8", edgecolor="white", linewidth=1))
        ax.text(x0, y0 - 0.105, name, ha="center", va="center", fontsize=11, color=INK)

    ax.plot([0.32, 0.38], [0.52, 0.52], color=MUTED, lw=1.4, linestyle="--")
    ax.text(0.35, 0.60, "same-looking /\nnear-looking", ha="center", va="center", fontsize=11, color=MUTED)

    decision = FancyBboxPatch(
        (0.62, 0.43),
        0.24,
        0.18,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor="#fff7e4",
        edgecolor=GOLD,
        linewidth=1.6,
    )
    ax.add_patch(decision)
    ax.text(0.74, 0.54, "ambiguous_unresolved", ha="center", va="center", fontsize=15, color=INK, weight="bold")
    ax.text(0.74, 0.48, "valid diagnostic state", ha="center", va="center", fontsize=11, color=MUTED)
    add_arrow(ax, (0.48, 0.525), (0.62, 0.525), color=GOLD, mutation_scale=18)

    add_box(
        ax,
        (0.19, 0.17),
        0.62,
        0.12,
        "IDSPACE definitions + CPNS constraints are needed before alternatives can be counted or bounded.",
        edge=LINE,
        fontsize=11.3,
    )
    ax.text(
        0.50,
        0.09,
        "Unresolved is not an error icon. It prevents a same-looking pattern from becoming an identity claim too early.",
        ha="center",
        va="center",
        fontsize=11.5,
        color=MUTED,
    )
    save(fig, FIGURE_DIR / "public01_figure03_unresolved_ambiguity.png")


def figure_04():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    fig, ax = setup_canvas()
    add_header(
        ax,
        "CPNS06 validation card",
        "Schema/example consistency only; no physical result and no real degeneracy measurement",
    )

    card = FancyBboxPatch(
        (0.22, 0.15),
        0.56,
        0.68,
        boxstyle="round,pad=0.026,rounding_size=0.035",
        facecolor="#ffffff",
        edgecolor="#b8c4c8",
        linewidth=1.5,
    )
    ax.add_patch(card)
    ax.text(0.50, 0.77, "CPNS06 validator", ha="center", va="center", fontsize=18, color=INK, weight="bold")
    ax.text(0.50, 0.72, "schema/example consistency only", ha="center", va="center", fontsize=12, color=MUTED)

    rows = [
        ("passed", str(summary.get("passed")).lower(), GREEN),
        ("failed_checks", "[]", GREEN),
        ("warning", "placeholder degeneracy only", GOLD),
        ("boundary flags", "false", BLUE),
        ("ambiguous_unresolved", "accepted", TEAL),
        ("invalid_outside_scope", "non-success", RED_SOFT),
    ]
    y = 0.62
    for label, value, col in rows:
        ax.add_patch(Rectangle((0.28, y - 0.027), 0.035, 0.035, facecolor=col, edgecolor="none"))
        ax.text(0.34, y - 0.01, label, ha="left", va="center", fontsize=12, color=INK)
        ax.text(0.70, y - 0.01, value, ha="right", va="center", fontsize=12, color=INK, weight="bold")
        ax.plot([0.28, 0.72], [y - 0.052, y - 0.052], color="#edf0f0", lw=1)
        y -= 0.085

    flags = [
        "bridge_confirmation=false",
        "diagnostic_specificity_claim=false",
        "physical_validation=false",
        "wifm01e_opened=false",
        "wifm02_opened=false",
        "bridge_nature_02_opened=false",
    ]
    ax.text(0.50, 0.245, "Boundary flags remain false", ha="center", va="center", fontsize=12.5, color=INK)
    ax.text(0.50, 0.185, "  |  ".join(flags[:3]), ha="center", va="center", fontsize=8.8, color=MUTED)
    ax.text(0.50, 0.145, "  |  ".join(flags[3:]), ha="center", va="center", fontsize=8.8, color=MUTED)

    save(fig, FIGURE_DIR / "public01_figure04_cpns06_validation_card.png")


def main() -> None:
    figure_01()
    figure_02()
    figure_03()
    figure_04()
    print("draft figures generated")


if __name__ == "__main__":
    main()
