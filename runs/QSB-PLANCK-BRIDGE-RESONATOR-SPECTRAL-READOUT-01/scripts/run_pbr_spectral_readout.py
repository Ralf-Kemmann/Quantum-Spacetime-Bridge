#!/usr/bin/env python3
"""Formal spectral readout for the PBR K_candidate matrix."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01"
MATRIX_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv"
PSD_VALIDATION_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv"
KNOWN_MATRIX_SHA256 = "e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d"
KNOWN_PSD_VALIDATION_SHA256 = "a0137b42013e3191657d8b3e0b53c28015cb1eb63e5b6371fc96c4e144bbec27"
KNOWN_LINEAGE_SHA256 = "9b242d40f34d864e4c521d873e94b3bea8f07b573386e99d617cd320d483646a"
TOLERANCE = 1e-10
PAIR_TOLERANCE = 1e-12


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


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def parse_pair_id(pair_id: str) -> Tuple[int, int, int, int, str, str]:
    left, right = pair_id.split("|", 1)
    i = int(left)
    j = int(right)
    lag = j - i
    if lag == 0:
        raise ValueError(f"diagonal pair id is not allowed: {pair_id}")
    abs_lag = abs(lag)
    direction = "+" if lag > 0 else "-"
    lag_axis = f"L{abs_lag}"
    return i, j, lag, abs_lag, direction, lag_axis


def parse_matrix(path: Path) -> Tuple[np.ndarray, List[str], List[str], List[str]]:
    required = ["row_pair_id", "column_pair_id", "K_candidate", "lineage_bundle_sha256"]
    row_order: List[str] = []
    col_order: List[str] = []
    row_seen = set()
    col_seen = set()
    rows: List[Dict[str, str]] = []
    lineages = set()

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != required:
            raise ValueError(f"unexpected matrix header: {reader.fieldnames}")
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
    filled = np.zeros_like(matrix, dtype=bool)
    row_idx = {pair_id: idx for idx, pair_id in enumerate(row_order)}
    col_idx = {pair_id: idx for idx, pair_id in enumerate(col_order)}
    for row in rows:
        i = row_idx[row["row_pair_id"]]
        j = col_idx[row["column_pair_id"]]
        if filled[i, j]:
            raise ValueError(f"duplicate matrix cell: {row['row_pair_id']} x {row['column_pair_id']}")
        matrix[i, j] = float(row["K_candidate"])
        filled[i, j] = True

    if not np.all(filled):
        raise ValueError("matrix CSV does not contain a complete rectangular matrix")
    if row_order != col_order:
        raise ValueError("row and column pair ordering differ")
    return matrix, row_order, col_order, sorted(lineages)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    data_dir = run_dir / "data"
    results_dir = run_dir / "results"
    matrix_path = repo_root / MATRIX_REL
    psd_validation_path = repo_root / PSD_VALIDATION_REL

    matrix_sha = sha256_file(matrix_path)
    prior_validation_sha = sha256_file(psd_validation_path)
    matrix, pair_ids, _col_ids, lineages = parse_matrix(matrix_path)

    is_square = matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1]
    all_finite = bool(np.all(np.isfinite(matrix)))
    symmetry_max_deviation = float(np.max(np.abs(matrix - matrix.T))) if is_square else math.nan
    diagonal_max_deviation = float(np.max(np.abs(np.diag(matrix) - 1.0))) if is_square else math.nan
    trace = float(np.trace(matrix)) if is_square else math.nan
    eigenvalues = np.linalg.eigvalsh(matrix) if is_square and all_finite else np.array([], dtype=float)
    rank = int(np.count_nonzero(eigenvalues > args.tolerance))
    nullity = int(matrix.shape[0] - rank) if is_square else 0
    positive_eigenvalue_sum = float(np.sum(eigenvalues[eigenvalues > args.tolerance]))
    negative = eigenvalues[eigenvalues < -args.tolerance]
    negative_count = int(len(negative))
    negative_mass = float(np.sum(np.abs(negative))) if len(negative) else 0.0
    lambda_min = float(np.min(eigenvalues)) if eigenvalues.size else math.nan
    lambda_max = float(np.max(eigenvalues)) if eigenvalues.size else math.nan
    psd_pass = bool(is_square and all_finite and symmetry_max_deviation <= args.tolerance and lambda_min >= -args.tolerance)
    admissibility_result = "pass_with_numerical_tolerance" if psd_pass else "fail"

    membership_rows: List[Dict[str, object]] = []
    for pair_id in pair_ids:
        i, j, lag, abs_lag, direction, lag_axis = parse_pair_id(pair_id)
        membership_rows.append(
            {
                "run_id": RUN_ID,
                "pair_id": pair_id,
                "i": i,
                "j": j,
                "lag": lag,
                "abs_lag": abs_lag,
                "direction": direction,
                "lag_axis": lag_axis,
            }
        )
    write_csv(
        results_dir / "lag_class_membership.csv",
        membership_rows,
        ["run_id", "pair_id", "i", "j", "lag", "abs_lag", "direction", "lag_axis"],
    )

    class_counts = Counter((row["direction"], int(row["abs_lag"])) for row in membership_rows)
    lag_summary_rows = []
    for abs_lag in range(1, 7):
        plus_count = class_counts[("+", abs_lag)]
        minus_count = class_counts[("-", abs_lag)]
        lag_summary_rows.append(
            {
                "run_id": RUN_ID,
                "lag_axis": f"L{abs_lag}",
                "abs_lag": abs_lag,
                "positive_direction_count": plus_count,
                "negative_direction_count": minus_count,
                "total_count": plus_count + minus_count,
                "expected_positive_count": 7 - abs_lag,
                "expected_negative_count": 7 - abs_lag,
                "expected_total_count": 2 * (7 - abs_lag),
                "class_size_check": bool_text(plus_count == 7 - abs_lag and minus_count == 7 - abs_lag),
            }
        )
    write_csv(
        data_dir / "lag_class_summary.csv",
        lag_summary_rows,
        [
            "run_id",
            "lag_axis",
            "abs_lag",
            "positive_direction_count",
            "negative_direction_count",
            "total_count",
            "expected_positive_count",
            "expected_negative_count",
            "expected_total_count",
            "class_size_check",
        ],
    )

    parallel_rows = []
    antiparallel_rows = []
    for a, b in combinations(range(len(pair_ids)), 2):
        value = float(matrix[a, b])
        base_row = {
            "run_id": RUN_ID,
            "pair_id_a": pair_ids[a],
            "pair_id_b": pair_ids[b],
            "row_index": a,
            "column_index": b,
            "K_candidate": f"{value:.17g}",
        }
        if abs(value - 1.0) <= PAIR_TOLERANCE:
            parallel_rows.append({**base_row, "relation_type": "parallel"})
        if abs(value + 1.0) <= PAIR_TOLERANCE:
            antiparallel_rows.append({**base_row, "relation_type": "antiparallel"})
    relation_fields = ["run_id", "pair_id_a", "pair_id_b", "row_index", "column_index", "K_candidate", "relation_type"]
    write_csv(results_dir / "parallel_pairs.csv", parallel_rows, relation_fields)
    write_csv(results_dir / "antiparallel_pairs.csv", antiparallel_rows, relation_fields)

    reps = [f"0|{abs_lag}" for abs_lag in range(1, 7)]
    rep_indices = [pair_ids.index(rep) for rep in reps]
    gram_rows = []
    for row_axis, row_pair, row_idx in zip([f"L{i}" for i in range(1, 7)], reps, rep_indices):
        out = {"run_id": RUN_ID, "lag_axis": row_axis, "representative_pair_id": row_pair}
        for col_axis, col_idx in zip([f"L{i}" for i in range(1, 7)], rep_indices):
            out[col_axis] = f"{float(matrix[row_idx, col_idx]):.17g}"
        gram_rows.append(out)
    write_csv(
        results_dir / "effective_lag_axis_gram.csv",
        gram_rows,
        ["run_id", "lag_axis", "representative_pair_id", "L1", "L2", "L3", "L4", "L5", "L6"],
    )

    eigen_rows = [
        {
            "run_id": RUN_ID,
            "eigenvalue_index_ascending": idx,
            "eigenvalue": f"{float(value):.17g}",
            "positive_above_tolerance": bool_text(float(value) > args.tolerance),
            "below_negative_tolerance": bool_text(float(value) < -args.tolerance),
            "tolerance": f"{args.tolerance:.17g}",
        }
        for idx, value in enumerate(eigenvalues)
    ]
    write_csv(
        results_dir / "eigenvalue_spectrum.csv",
        eigen_rows,
        ["run_id", "eigenvalue_index_ascending", "eigenvalue", "positive_above_tolerance", "below_negative_tolerance", "tolerance"],
    )

    positive_desc = sorted([float(v) for v in eigenvalues if v > args.tolerance], reverse=True)
    mass_rows = []
    for idx, value in enumerate(positive_desc, start=1):
        mass_rows.append(
            {
                "run_id": RUN_ID,
                "component_rank_desc": idx,
                "eigenvalue": f"{value:.17g}",
                "fraction_of_trace": f"{value / trace:.6f}",
                "tolerance": f"{args.tolerance:.17g}",
            }
        )
    write_csv(
        data_dir / "eigenvalue_mass_report.csv",
        mass_rows,
        ["run_id", "component_rank_desc", "eigenvalue", "fraction_of_trace", "tolerance"],
    )

    expected_parallel = sum(2 * math.comb(7 - lag, 2) for lag in range(1, 7))
    expected_antiparallel = sum((7 - lag) ** 2 for lag in range(1, 7))
    count_rows = [
        {
            "run_id": RUN_ID,
            "metric": "parallel_count",
            "observed_count": len(parallel_rows),
            "expected_count": expected_parallel,
            "status": "pass" if len(parallel_rows) == expected_parallel else "fail",
            "definition": "unordered off-diagonal entries with abs(K_candidate - 1.0) <= 1e-12",
        },
        {
            "run_id": RUN_ID,
            "metric": "antiparallel_count",
            "observed_count": len(antiparallel_rows),
            "expected_count": expected_antiparallel,
            "status": "pass" if len(antiparallel_rows) == expected_antiparallel else "fail",
            "definition": "unordered off-diagonal entries with abs(K_candidate + 1.0) <= 1e-12",
        },
    ]
    write_csv(
        data_dir / "parallel_antiparallel_counts.csv",
        count_rows,
        ["run_id", "metric", "observed_count", "expected_count", "status", "definition"],
    )

    readout_row = {
        "run_id": RUN_ID,
        "input_id": "K-CANDIDATE-EXTRACT03A-R1",
        "matrix_sha256": matrix_sha,
        "prior_psd_validation_sha256": prior_validation_sha,
        "lineage_bundle_sha256": lineages[0] if len(lineages) == 1 else "|".join(lineages),
        "n_rows": matrix.shape[0],
        "n_columns": matrix.shape[1],
        "all_values_finite": bool_text(all_finite),
        "symmetry_max_deviation": f"{symmetry_max_deviation:.17g}",
        "diagonal_max_deviation_from_one": f"{diagonal_max_deviation:.17g}",
        "trace": f"{trace:.17g}",
        "rank_tol_1e_10": rank,
        "nullity": nullity,
        "positive_eigenvalue_sum": f"{positive_eigenvalue_sum:.17g}",
        "lambda_min": f"{lambda_min:.17g}",
        "lambda_max": f"{lambda_max:.17g}",
        "negative_eigenvalue_count": negative_count,
        "negative_eigenvalue_mass": f"{negative_mass:.17g}",
        "tolerance": f"{args.tolerance:.17g}",
        "psd_pass": bool_text(psd_pass),
        "admissibility_result": admissibility_result,
        "parallel_count": len(parallel_rows),
        "antiparallel_count": len(antiparallel_rows),
        "claim_status": "formal_matrix_structure_readout_only",
        "physical_claim_release": "blocked_no_physics_claim",
        "review_status": "requires_human_review",
    }
    write_csv(data_dir / "spectral_readout_result.csv", [readout_row], list(readout_row.keys()))

    lineage_rows = [
        {
            "run_id": RUN_ID,
            "input_id": "K_candidate_matrix",
            "source_path": MATRIX_REL,
            "sha256": matrix_sha,
            "expected_sha256": KNOWN_MATRIX_SHA256,
            "hash_match": bool_text(matrix_sha == KNOWN_MATRIX_SHA256),
            "lineage_bundle_sha256": KNOWN_LINEAGE_SHA256,
        },
        {
            "run_id": RUN_ID,
            "input_id": "prior_psd_validation",
            "source_path": PSD_VALIDATION_REL,
            "sha256": prior_validation_sha,
            "expected_sha256": KNOWN_PSD_VALIDATION_SHA256,
            "hash_match": bool_text(prior_validation_sha == KNOWN_PSD_VALIDATION_SHA256),
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

    boundary_rows = [
        {
            "run_id": RUN_ID,
            "boundary_id": "ALLOW-001",
            "boundary_type": "allowed_claim",
            "claim_status": "formal_matrix_structure_readout_only",
            "physical_claim_release": "blocked_no_physics_claim",
            "review_status": "requires_human_review",
            "claim_text": "The K_candidate matrix has a formal directed lag/difference structure.",
            "release_status": "released_formal_structure_readout",
            "rationale": "This is a matrix-structure statement only.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "ALLOW-002",
            "boundary_type": "allowed_claim",
            "claim_status": "formal_matrix_structure_readout_only",
            "physical_claim_release": "blocked_no_physics_claim",
            "review_status": "requires_human_review",
            "claim_text": "The 42 directed pair-features collapse into 6 effective lag axes under the observed Gram structure.",
            "release_status": "released_formal_structure_readout",
            "rationale": "The statement follows from rank and lag-class diagnostics.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "BLOCK-001",
            "boundary_type": "blocked_claim",
            "claim_status": "formal_matrix_structure_readout_only",
            "physical_claim_release": "blocked_no_physics_claim",
            "review_status": "requires_human_review",
            "claim_text": "Physical validation of QSB is not released.",
            "release_status": "blocked_no_physics_claim",
            "rationale": "No physical or empirical test is performed.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "BLOCK-002",
            "boundary_type": "blocked_claim",
            "claim_status": "formal_matrix_structure_readout_only",
            "physical_claim_release": "blocked_no_physics_claim",
            "review_status": "requires_human_review",
            "claim_text": "PBR existence is not released.",
            "release_status": "blocked_no_physics_claim",
            "rationale": "The readout concerns only a formal matrix.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "BLOCK-003",
            "boundary_type": "blocked_claim",
            "claim_status": "formal_matrix_structure_readout_only",
            "physical_claim_release": "blocked_no_physics_claim",
            "review_status": "requires_human_review",
            "claim_text": "The six lag axes are not released as physical spacetime dimensions.",
            "release_status": "blocked_no_physics_claim",
            "rationale": "Effective lag axes are formal readout axes only.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "BLOCK-004",
            "boundary_type": "blocked_claim",
            "claim_status": "formal_matrix_structure_readout_only",
            "physical_claim_release": "blocked_no_physics_claim",
            "review_status": "requires_human_review",
            "claim_text": "Spacetime-emergence proof is not released.",
            "release_status": "blocked_no_physics_claim",
            "rationale": "No emergence proof is tested.",
        },
    ]
    write_csv(
        data_dir / "claim_boundaries.csv",
        boundary_rows,
        ["run_id", "boundary_id", "boundary_type", "claim_status", "physical_claim_release", "review_status", "claim_text", "release_status", "rationale"],
    )

    manifest = {
        "run_id": RUN_ID,
        "created_date": "2026-07-06",
        "purpose": "Perform a formal spectral readout of the existing K_candidate matrix after the PSD gate has passed.",
        "matrix_source": MATRIX_REL,
        "prior_state_spec_commit": "3a486ca",
        "prior_psd_test_commit": "0d74576",
        "tolerance": args.tolerance,
        "parallel_antiparallel_tolerance": PAIR_TOLERANCE,
        "representative_choice": {
            "method": "positive-direction pair 0|k for each abs_lag k",
            "representative_pair_ids": reps,
            "claim_boundary": "formal aggregation/readout only; no physical interpretation",
        },
        "result": readout_row,
        "claim_status": "formal_matrix_structure_readout_only",
        "physical_claim_release": "blocked_no_physics_claim",
        "review_status": "requires_human_review",
        "final_claim_statement": "The spectral readout supports only a formal matrix-structure statement: the K_candidate matrix is consistent with a rank-6 directed lag-class Gram structure. All physical claims remain blocked.",
    }
    with (data_dir / "spectral_readout_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print("PBR spectral readout result summary")
    print(f"run_id={RUN_ID}")
    print(f"shape=({matrix.shape[0]}, {matrix.shape[1]})")
    print(f"rank_tol_1e-10={rank}")
    print(f"nullity={nullity}")
    print(f"trace={trace:.17g}")
    print(f"positive_eigenvalue_sum={positive_eigenvalue_sum:.17g}")
    print(f"lambda_min={lambda_min:.17g}")
    print(f"lambda_max={lambda_max:.17g}")
    print(f"psd_pass={bool_text(psd_pass)}")
    print(f"parallel_count={len(parallel_rows)}")
    print(f"antiparallel_count={len(antiparallel_rows)}")
    print("claim_status=formal_matrix_structure_readout_only")
    print("physical_claim_release=blocked_no_physics_claim")
    print("review_status=requires_human_review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

