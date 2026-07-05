#!/usr/bin/env python3
"""PSD gate template for a candidate K matrix.

Reads a CSV matrix and writes one CSV row with Hermitian/symmetric and PSD diagnostics.

Supported simple CSV shapes:
1. Pure numeric matrix with no row/column labels.
2. First row column labels and first column row labels; nonnumeric first cell is ignored.

Complex numbers may use Python notation such as 1+2j. For real matrices, normal floats work.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

import numpy as np


def parse_cell(x: str) -> complex:
    text = x.strip()
    if text == "":
        return complex(np.nan)
    # tolerate i notation by replacing terminal i with j
    text = text.replace("i", "j")
    return complex(text)


def try_parse_matrix(path: Path) -> np.ndarray:
    raw: List[List[str]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if row:
                raw.append(row)
    if not raw:
        raise ValueError("empty CSV")

    # Try pure numeric first.
    try:
        return np.array([[parse_cell(c) for c in row] for row in raw], dtype=complex)
    except Exception:
        pass

    # Try labelled matrix: drop header row and first column.
    body = [row[1:] for row in raw[1:]]
    try:
        return np.array([[parse_cell(c) for c in row] for row in body], dtype=complex)
    except Exception as exc:
        raise ValueError(f"could not parse matrix as numeric or labelled CSV: {exc}") from exc


def psd_gate(matrix: np.ndarray, tolerance: float) -> dict:
    is_square = matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1]
    result = {
        "n": matrix.shape[0] if matrix.ndim == 2 else 0,
        "is_square": is_square,
        "is_hermitian": False,
        "max_hermitian_deviation": np.nan,
        "min_diagonal": np.nan,
        "lambda_min": np.nan,
        "lambda_max": np.nan,
        "negative_eigenvalue_count": np.nan,
        "negative_eigenvalue_mass": np.nan,
        "tolerance": tolerance,
        "psd_pass": False,
        "admissibility_result": "fail_not_square",
    }
    if not is_square:
        return result

    hermitian_deviation = np.max(np.abs(matrix - matrix.conj().T))
    is_hermitian = bool(hermitian_deviation <= tolerance)
    hermitian_part = (matrix + matrix.conj().T) / 2.0
    eigvals = np.linalg.eigvalsh(hermitian_part).real
    diag = np.diag(hermitian_part).real
    neg = eigvals[eigvals < -tolerance]
    psd_pass = is_hermitian and bool(np.min(diag) >= -tolerance) and bool(np.min(eigvals) >= -tolerance)

    result.update(
        {
            "is_hermitian": is_hermitian,
            "max_hermitian_deviation": float(hermitian_deviation),
            "min_diagonal": float(np.min(diag)),
            "lambda_min": float(np.min(eigvals)),
            "lambda_max": float(np.max(eigvals)),
            "negative_eigenvalue_count": int(len(neg)),
            "negative_eigenvalue_mass": float(np.sum(np.abs(neg))) if len(neg) else 0.0,
            "psd_pass": bool(psd_pass),
            "admissibility_result": "pass" if psd_pass else "fail_psd_or_hermitian",
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix_csv", type=Path)
    parser.add_argument("--matrix-id", default="candidate_matrix")
    parser.add_argument("--tolerance", type=float, default=1e-10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    matrix = try_parse_matrix(args.matrix_csv)
    result = psd_gate(matrix, args.tolerance)
    result = {
        "matrix_id": args.matrix_id,
        "matrix_source": str(args.matrix_csv),
        **result,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)

    print(f"wrote={args.output}")
    print(f"psd_pass={result['psd_pass']} lambda_min={result['lambda_min']} neg_count={result['negative_eigenvalue_count']}")
    return 0 if result["psd_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
