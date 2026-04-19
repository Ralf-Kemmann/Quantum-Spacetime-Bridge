from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import numpy as np


PROJECT_ROOT = Path(
    "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/"
    "debroglie-phase-bridge/debroglie-phase-bridge/typ_b_analysis"
)

RESULTS_ROOT = PROJECT_ROOT.parent / "results"
OUTPUT_CSV = PROJECT_ROOT / "data" / "original" / "h3_support_scores.csv"

BASELINE_ROOT = RESULTS_ROOT / "a1_probe" / "k0"
COMBINED_ROOT = RESULTS_ROOT / "a1_probe" / "n1a_alpha"

EXPORT_CLASSES = ["negative", "abs", "positive"]
MATRIX_KEY = "G"
ADJ_KEY = "adjacency"


def offdiag_row_values(mat: np.ndarray, row_idx: int) -> np.ndarray:
    row = np.asarray(mat[row_idx], dtype=float)
    mask = np.ones(len(row), dtype=bool)
    mask[row_idx] = False
    return row[mask]


def adjacency_row_values(mat: np.ndarray, adjacency: np.ndarray, row_idx: int) -> np.ndarray:
    row = np.asarray(mat[row_idx], dtype=float)
    adj_row = np.asarray(adjacency[row_idx], dtype=int)

    mask = (adj_row == 1)
    mask[row_idx] = False
    return row[mask]


def score_from_values(values: np.ndarray, method: str = "median") -> float:
    if values.size == 0:
        return float("nan")
    if method == "mean":
        return float(np.mean(values))
    return float(np.median(values))


def row_score(
    mat: np.ndarray,
    adjacency: np.ndarray,
    row_idx: int,
    method: str = "median",
) -> float:
    vals = adjacency_row_values(mat, adjacency, row_idx)
    if vals.size == 0:
        vals = offdiag_row_values(mat, row_idx)
    return score_from_values(vals, method=method)


def load_matrix(npz_path: Path, key: str) -> np.ndarray:
    if not npz_path.exists():
        raise FileNotFoundError(f"Missing NPZ file: {npz_path}")
    with np.load(npz_path, allow_pickle=True) as data:
        if key not in data.files:
            raise KeyError(f"Key '{key}' not found in {npz_path}. Available: {data.files}")
        mat = np.asarray(data[key])
    return mat


def load_square_float_matrix(npz_path: Path, key: str) -> np.ndarray:
    mat = np.asarray(load_matrix(npz_path, key), dtype=float)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError(f"Expected square 2D matrix for '{key}' in {npz_path}, got {mat.shape}")
    return mat


def load_square_int_matrix(npz_path: Path, key: str) -> np.ndarray:
    mat = np.asarray(load_matrix(npz_path, key), dtype=int)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError(f"Expected square 2D matrix for '{key}' in {npz_path}, got {mat.shape}")
    return mat


def class_flags(export_class: str) -> tuple[int, int]:
    if export_class in {"negative", "abs"}:
        return 1, 0
    if export_class == "positive":
        return 0, 1
    return 0, 0


def iter_rows() -> Iterable[dict[str, object]]:
    for export_class in EXPORT_CLASSES:
        baseline_npz = BASELINE_ROOT / export_class / "matrices.npz"
        combined_npz = COMBINED_ROOT / export_class / "matrices.npz"

        baseline_mat = load_square_float_matrix(baseline_npz, MATRIX_KEY)
        combined_mat = load_square_float_matrix(combined_npz, MATRIX_KEY)

        baseline_adj = load_square_int_matrix(baseline_npz, ADJ_KEY)
        combined_adj = load_square_int_matrix(combined_npz, ADJ_KEY)

        if baseline_mat.shape != combined_mat.shape:
            raise ValueError(
                f"Shape mismatch for class '{export_class}': "
                f"baseline {baseline_mat.shape} vs combined {combined_mat.shape}"
            )
        if baseline_adj.shape != baseline_mat.shape:
            raise ValueError(
                f"Adjacency shape mismatch for baseline '{export_class}': "
                f"adjacency {baseline_adj.shape} vs matrix {baseline_mat.shape}"
            )
        if combined_adj.shape != combined_mat.shape:
            raise ValueError(
                f"Adjacency shape mismatch for combined '{export_class}': "
                f"adjacency {combined_adj.shape} vs matrix {combined_mat.shape}"
            )

        n = baseline_mat.shape[0]
        is_support, is_neighbor = class_flags(export_class)

        for row_idx in range(n):
            baseline_score = row_score(
                baseline_mat,
                baseline_adj,
                row_idx,
                method="median",
            )
            combined_score = row_score(
                combined_mat,
                combined_adj,
                row_idx,
                method="median",
            )

            baseline_degree = int(np.sum(baseline_adj[row_idx]) - baseline_adj[row_idx, row_idx])
            combined_degree = int(np.sum(combined_adj[row_idx]) - combined_adj[row_idx, row_idx])

            yield {
                "unit_id": f"{export_class}_r{row_idx}",
                "baseline_score": round(baseline_score, 6),
                "combined_score": round(combined_score, 6),
                "is_support": is_support,
                "is_neighbor": is_neighbor,
                "export_class": export_class,
                "row_index": row_idx,
                "baseline_degree": baseline_degree,
                "combined_degree": combined_degree,
                "baseline_npz": str(baseline_npz),
                "combined_npz": str(combined_npz),
            }


def write_csv(rows: list[dict[str, object]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "unit_id",
        "baseline_score",
        "combined_score",
        "is_support",
        "is_neighbor",
        "export_class",
        "row_index",
        "baseline_degree",
        "combined_degree",
        "baseline_npz",
        "combined_npz",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = list(iter_rows())
    write_csv(rows, OUTPUT_CSV)
    print(f"[INFO] Wrote {len(rows)} rows to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()