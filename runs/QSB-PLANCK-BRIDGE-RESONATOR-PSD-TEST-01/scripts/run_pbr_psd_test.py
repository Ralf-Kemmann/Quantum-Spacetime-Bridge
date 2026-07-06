#!/usr/bin/env python3
"""Run PBR-State-Spec Gram/PSD admissibility test for the EXTRACT03A-R1 K matrix."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01"
STATE_SPEC_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01"
MATRIX_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv"
VALIDATION_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv"
KNOWN_K_SHA256 = "e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d"
KNOWN_VALIDATION_SHA256 = "a0137b42013e3191657d8b3e0b53c28015cb1eb63e5b6371fc96c4e144bbec27"
KNOWN_LINEAGE_SHA256 = "9b242d40f34d864e4c521d873e94b3bea8f07b573386e99d617cd320d483646a"
TOLERANCE = 1e-10


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_matrix(path: Path) -> tuple[np.ndarray, List[str], List[str], List[str]]:
    required = {"row_pair_id", "column_pair_id", "K_candidate", "lineage_bundle_sha256"}
    rows: List[Dict[str, str]] = []
    row_order: List[str] = []
    col_order: List[str] = []
    row_seen = set()
    col_seen = set()
    lineages = set()

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if set(reader.fieldnames or []) != required:
            raise ValueError(f"unexpected matrix columns: {reader.fieldnames}")
        for row in reader:
            rows.append(row)
            r = row["row_pair_id"]
            c = row["column_pair_id"]
            if r not in row_seen:
                row_order.append(r)
                row_seen.add(r)
            if c not in col_seen:
                col_order.append(c)
                col_seen.add(c)
            lineages.add(row["lineage_bundle_sha256"])

    matrix = np.full((len(row_order), len(col_order)), np.nan, dtype=float)
    row_idx = {v: i for i, v in enumerate(row_order)}
    col_idx = {v: i for i, v in enumerate(col_order)}
    duplicate_count = 0
    filled = np.zeros_like(matrix, dtype=bool)

    for row in rows:
        i = row_idx[row["row_pair_id"]]
        j = col_idx[row["column_pair_id"]]
        if filled[i, j]:
            duplicate_count += 1
        matrix[i, j] = float(row["K_candidate"])
        filled[i, j] = True

    if duplicate_count:
        raise ValueError(f"duplicate matrix cells detected: {duplicate_count}")
    if not np.all(filled):
        raise ValueError(f"missing matrix cells detected: {int(np.size(filled) - np.count_nonzero(filled))}")

    return matrix, row_order, col_order, sorted(lineages)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    data_dir = run_dir / "data"

    matrix_path = repo_root / MATRIX_REL
    validation_path = repo_root / VALIDATION_REL
    k_sha = sha256_file(matrix_path)
    validation_sha = sha256_file(validation_path)

    matrix, row_order, col_order, lineages = parse_matrix(matrix_path)
    is_square = matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1]
    all_finite = bool(np.all(np.isfinite(matrix)))
    symmetry_max_deviation = float(np.max(np.abs(matrix - matrix.T))) if is_square else math.nan
    diagonal_max_deviation_from_one = float(np.max(np.abs(np.diag(matrix) - 1.0))) if is_square else math.nan

    eigenvalues = np.linalg.eigvalsh(matrix) if is_square and all_finite else np.array([], dtype=float)
    lambda_min = float(np.min(eigenvalues)) if eigenvalues.size else math.nan
    lambda_max = float(np.max(eigenvalues)) if eigenvalues.size else math.nan
    negative = eigenvalues[eigenvalues < -args.tolerance]
    negative_eigenvalue_count = int(len(negative))
    negative_eigenvalue_mass = float(np.sum(np.abs(negative))) if len(negative) else 0.0

    psd_pass = bool(
        is_square
        and all_finite
        and symmetry_max_deviation <= args.tolerance
        and diagonal_max_deviation_from_one <= args.tolerance
        and lambda_min >= -args.tolerance
        and negative_eigenvalue_count == 0
    )
    admissibility_result = "pass" if psd_pass else "fail"

    lineage_rows = [
        {
            "run_id": RUN_ID,
            "input_id": "K_candidate_matrix",
            "source_path": MATRIX_REL,
            "sha256": k_sha,
            "expected_sha256": KNOWN_K_SHA256,
            "hash_match": bool_text(k_sha == KNOWN_K_SHA256),
            "lineage_bundle_sha256": KNOWN_LINEAGE_SHA256,
        },
        {
            "run_id": RUN_ID,
            "input_id": "K_validation_results",
            "source_path": VALIDATION_REL,
            "sha256": validation_sha,
            "expected_sha256": KNOWN_VALIDATION_SHA256,
            "hash_match": bool_text(validation_sha == KNOWN_VALIDATION_SHA256),
            "lineage_bundle_sha256": KNOWN_LINEAGE_SHA256,
        },
        {
            "run_id": RUN_ID,
            "input_id": "matrix_embedded_lineage",
            "source_path": MATRIX_REL,
            "sha256": lineages[0] if len(lineages) == 1 else "|".join(lineages),
            "expected_sha256": KNOWN_LINEAGE_SHA256,
            "hash_match": bool_text(lineages == [KNOWN_LINEAGE_SHA256]),
            "lineage_bundle_sha256": KNOWN_LINEAGE_SHA256,
        },
    ]
    write_csv(
        data_dir / "input_lineage.csv",
        lineage_rows,
        ["run_id", "input_id", "source_path", "sha256", "expected_sha256", "hash_match", "lineage_bundle_sha256"],
    )

    gate_row = {
        "run_id": RUN_ID,
        "matrix_id": "QSB-EXTRACT03A-R1_K_candidate",
        "matrix_source": MATRIX_REL,
        "state_spec_run_id": STATE_SPEC_RUN_ID,
        "n_rows": matrix.shape[0],
        "n_columns": matrix.shape[1],
        "is_square": bool_text(is_square),
        "all_values_finite": bool_text(all_finite),
        "symmetry_max_deviation": f"{symmetry_max_deviation:.17g}",
        "diagonal_max_deviation_from_one": f"{diagonal_max_deviation_from_one:.17g}",
        "lambda_min": f"{lambda_min:.17g}",
        "lambda_max": f"{lambda_max:.17g}",
        "negative_eigenvalue_count": negative_eigenvalue_count,
        "negative_eigenvalue_mass": f"{negative_eigenvalue_mass:.17g}",
        "tolerance": f"{args.tolerance:.17g}",
        "psd_pass": bool_text(psd_pass),
        "admissibility_result": admissibility_result,
        "claim_status": "formal_admissibility_result_only",
        "physical_claim_release": "blocked_no_physics_claim",
        "review_status": "requires_human_review",
    }
    write_csv(data_dir / "psd_gate_result.csv", [gate_row], list(gate_row.keys()))

    eigen_rows = [
        {
            "run_id": RUN_ID,
            "matrix_id": "QSB-EXTRACT03A-R1_K_candidate",
            "eigenvalue_index": idx,
            "eigenvalue": f"{float(value):.17g}",
            "below_negative_tolerance": bool_text(float(value) < -args.tolerance),
            "tolerance": f"{args.tolerance:.17g}",
        }
        for idx, value in enumerate(eigenvalues)
    ]
    write_csv(
        data_dir / "eigenvalue_report.csv",
        eigen_rows,
        ["run_id", "matrix_id", "eigenvalue_index", "eigenvalue", "below_negative_tolerance", "tolerance"],
    )

    manifest = {
        "run_id": RUN_ID,
        "created_date": "2026-07-06",
        "purpose": "Re-evaluate the existing K_candidate matrix under the PBR-State-Spec Gram/PSD admissibility gate.",
        "state_spec_commit": "3a486ca",
        "state_spec_run_id": STATE_SPEC_RUN_ID,
        "matrix_source": MATRIX_REL,
        "validation_source": VALIDATION_REL,
        "tolerance": args.tolerance,
        "claim_status": "formal_admissibility_result_only",
        "physical_claim_release": "blocked_no_physics_claim",
        "review_status": "requires_human_review",
        "input_hashes": {
            "K_candidate_matrix_sha256": k_sha,
            "K_candidate_matrix_expected_sha256": KNOWN_K_SHA256,
            "K_validation_sha256": validation_sha,
            "K_validation_expected_sha256": KNOWN_VALIDATION_SHA256,
            "lineage_bundle_sha256": lineages[0] if len(lineages) == 1 else lineages,
            "lineage_bundle_expected_sha256": KNOWN_LINEAGE_SHA256,
        },
        "result": gate_row,
        "ordering": {
            "method": "first_seen_order_from_row_pair_id_and_column_pair_id",
            "row_pair_ids": row_order,
            "column_pair_ids": col_order,
        },
    }
    with (data_dir / "psd_test_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print("PBR PSD test result summary")
    print(f"run_id={RUN_ID}")
    print(f"shape=({matrix.shape[0]}, {matrix.shape[1]})")
    print(f"all_values_finite={bool_text(all_finite)}")
    print(f"symmetry_max_deviation={symmetry_max_deviation:.17g}")
    print(f"diagonal_max_deviation_from_one={diagonal_max_deviation_from_one:.17g}")
    print(f"lambda_min={lambda_min:.17g}")
    print(f"lambda_max={lambda_max:.17g}")
    print(f"negative_eigenvalue_count={negative_eigenvalue_count}")
    print(f"negative_eigenvalue_mass={negative_eigenvalue_mass:.17g}")
    print(f"tolerance={args.tolerance:.17g}")
    print(f"psd_pass={bool_text(psd_pass)}")
    print(f"admissibility_result={admissibility_result}")
    print(f"physical_claim_release=blocked_no_physics_claim")
    print(f"review_status=requires_human_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

