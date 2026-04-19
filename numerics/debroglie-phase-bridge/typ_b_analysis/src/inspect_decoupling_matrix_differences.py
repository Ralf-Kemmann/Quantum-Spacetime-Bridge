from __future__ import annotations

from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(
    "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/"
    "debroglie-phase-bridge/debroglie-phase-bridge/typ_b_analysis"
)

RESULTS_ROOT = PROJECT_ROOT.parent / "results"

BASELINE_ROOT = RESULTS_ROOT / "a1_probe" / "k0"
COMBINED_ROOT = RESULTS_ROOT / "a1_probe" / "n1a_alpha"

EXPORT_CLASSES = ["negative", "abs", "positive"]
MATRIX_KEYS = ["G", "kbar", "adjacency", "graph_distance", "edge_length", "d_rel"]


def load_matrix(npz_path: Path, key: str) -> np.ndarray:
    if not npz_path.exists():
        raise FileNotFoundError(f"Missing NPZ file: {npz_path}")
    with np.load(npz_path, allow_pickle=True) as data:
        if key not in data.files:
            raise KeyError(f"Key '{key}' not found in {npz_path}. Available: {data.files}")
        return np.asarray(data[key])


def safe_diff(a: np.ndarray, b: np.ndarray) -> np.ndarray | None:
    try:
        return b.astype(float) - a.astype(float)
    except Exception:
        return None


def finite_stats(diff: np.ndarray) -> dict[str, float]:
    finite = diff[np.isfinite(diff)]
    if finite.size == 0:
        return {
            "max_abs_diff": float("nan"),
            "sum_abs_diff": float("nan"),
            "mean_abs_diff": float("nan"),
        }
    absvals = np.abs(finite)
    return {
        "max_abs_diff": float(np.max(absvals)),
        "sum_abs_diff": float(np.sum(absvals)),
        "mean_abs_diff": float(np.mean(absvals)),
    }


def offdiag_mask(n: int) -> np.ndarray:
    mask = np.ones((n, n), dtype=bool)
    np.fill_diagonal(mask, False)
    return mask


def print_matrix(name: str, mat: np.ndarray) -> None:
    print(f"{name}:")
    with np.printoptions(precision=6, suppress=True):
        print(mat)


def inspect_class(export_class: str) -> None:
    baseline_npz = BASELINE_ROOT / export_class / "matrices.npz"
    combined_npz = COMBINED_ROOT / export_class / "matrices.npz"

    print("=" * 80)
    print(f"CLASS: {export_class}")
    print(f"baseline: {baseline_npz}")
    print(f"combined: {combined_npz}")
    print()

    for key in MATRIX_KEYS:
        a = load_matrix(baseline_npz, key)
        b = load_matrix(combined_npz, key)

        print(f"--- {key} ---")
        print(f"shape baseline={a.shape} combined={b.shape}")
        print(f"array_equal={np.array_equal(a, b)}")

        diff = safe_diff(a, b)
        if diff is None:
            print("diff: not computable")
            print()
            continue

        stats = finite_stats(diff)
        print(
            "stats: "
            f"max_abs_diff={stats['max_abs_diff']:.12f}, "
            f"sum_abs_diff={stats['sum_abs_diff']:.12f}, "
            f"mean_abs_diff={stats['mean_abs_diff']:.12f}"
        )

        if a.ndim == 2 and a.shape[0] == a.shape[1]:
            n = a.shape[0]
            mask = offdiag_mask(n)

            offdiag_a = a.astype(float)[mask]
            offdiag_b = b.astype(float)[mask]
            offdiag_diff = diff[mask]
            finite_offdiag = offdiag_diff[np.isfinite(offdiag_diff)]

            print(
                "offdiag: "
                f"median_baseline={np.median(offdiag_a[np.isfinite(offdiag_a)]):.12f}, "
                f"median_combined={np.median(offdiag_b[np.isfinite(offdiag_b)]):.12f}"
            )
            if finite_offdiag.size:
                print(
                    "offdiag_diff: "
                    f"max_abs={np.max(np.abs(finite_offdiag)):.12f}, "
                    f"sum_abs={np.sum(np.abs(finite_offdiag)):.12f}, "
                    f"median={np.median(finite_offdiag):.12f}"
                )

            print_matrix("baseline", a)
            print_matrix("combined", b)
            print_matrix("combined_minus_baseline", diff)

            if key in {"G", "kbar"}:
                print("row-wise offdiag medians:")
                for i in range(n):
                    row_mask = np.ones(n, dtype=bool)
                    row_mask[i] = False
                    row_a = a.astype(float)[i][row_mask]
                    row_b = b.astype(float)[i][row_mask]
                    med_a = np.median(row_a[np.isfinite(row_a)]) if np.isfinite(row_a).any() else float("nan")
                    med_b = np.median(row_b[np.isfinite(row_b)]) if np.isfinite(row_b).any() else float("nan")
                    print(
                        f"  row {i}: baseline={med_a:.12f}, "
                        f"combined={med_b:.12f}, diff={med_b - med_a:.12f}"
                    )
        print()


def main() -> None:
    for export_class in EXPORT_CLASSES:
        inspect_class(export_class)


if __name__ == "__main__":
    main()