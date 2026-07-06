#!/usr/bin/env python3
"""Validate QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01."""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01"
KNOWN_MATRIX_SHA256 = "e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d"

REQUIRED_FILES = [
    "README.md",
    "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01.md",
    "RUN_COMMANDS_PBR_SPECTRAL_READOUT01.md",
    "data/input_lineage.csv",
    "data/spectral_readout_result.csv",
    "data/eigenvalue_mass_report.csv",
    "data/lag_class_summary.csv",
    "data/parallel_antiparallel_counts.csv",
    "data/claim_boundaries.csv",
    "data/spectral_readout_manifest.json",
    "results/eigenvalue_spectrum.csv",
    "results/lag_class_membership.csv",
    "results/parallel_pairs.csv",
    "results/antiparallel_pairs.csv",
    "results/effective_lag_axis_gram.csv",
    "docs/PBR_SPECTRAL_READOUT_SUMMARY_DE.md",
    "scripts/run_pbr_spectral_readout.py",
    "scripts/validate_pbr_spectral_readout.py",
    "sql/001_create_qsb_pbr_spectral_readout.sql",
    "sql/002_insert_qsb_pbr_spectral_readout.sql",
    "sql/003_validation_queries.sql",
]

CSV_FILES = [path for path in REQUIRED_FILES if path.endswith(".csv")]
MARKDOWN_FILES = [
    "README.md",
    "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01.md",
    "RUN_COMMANDS_PBR_SPECTRAL_READOUT01.md",
    "docs/PBR_SPECTRAL_READOUT_SUMMARY_DE.md",
]
FORBIDDEN_MARKDOWN_PHRASES = [
    "QSB is physically validated",
    "PBRs physically exist",
    "six effective lag axes are physical spacetime dimensions",
    "K matrix proves spacetime emergence",
    "discovery of physical modes",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add(results: List[Tuple[str, str, str, str, str, str, str, str]], check_name: str, ok: bool, observed: str, expected: str, message: str, severity: str = "error", blocking: str = "yes") -> None:
    validation_id = f"SR-VAL-{len(results) + 1:03d}"
    results.append((validation_id, check_name, "pass" if ok else "fail", severity, observed, expected, message, blocking))


def has_blank_row(path: Path) -> bool:
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if row and all(cell.strip() == "" for cell in row):
                return True
    return False


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    repo_root = base.resolve().parents[1]
    results: List[Tuple[str, str, str, str, str, str, str, str]] = []

    for rel in REQUIRED_FILES:
        add(results, f"file_exists:{rel}", (base / rel).exists(), str(base / rel), "exists", "Required package file check.")

    for rel in CSV_FILES:
        path = base / rel
        if path.exists():
            add(results, f"no_blank_rows:{rel}", not has_blank_row(path), "blank_row_found" if has_blank_row(path) else "none", "none", "CSV must not contain blank rows.")

    matrix_path = repo_root / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv"
    if matrix_path.exists():
        observed_hash = sha256_file(matrix_path)
        add(results, "input_matrix_sha256", observed_hash == KNOWN_MATRIX_SHA256, observed_hash, KNOWN_MATRIX_SHA256, "Input matrix hash must match registered value.")

    readout_path = base / "data/spectral_readout_result.csv"
    if readout_path.exists():
        rows = read_csv(readout_path)
        row = rows[0] if rows else {}
        add(results, "rank_tol_1e_10", row.get("rank_tol_1e_10") == "6", row.get("rank_tol_1e_10", "missing"), "6", "Rank must match directed lag-class expectation.")
        add(results, "nullity", row.get("nullity") == "36", row.get("nullity", "missing"), "36", "Nullity must match 42 minus rank 6.")
        add(results, "trace", abs(float(row.get("trace", "nan")) - 42.0) <= 1e-10, row.get("trace", "missing"), "42", "Trace must match matrix dimension.")
        add(results, "parallel_count", row.get("parallel_count") == "70", row.get("parallel_count", "missing"), "70", "Parallel count must match expected combinatorics.")
        add(results, "antiparallel_count", row.get("antiparallel_count") == "91", row.get("antiparallel_count", "missing"), "91", "Antiparallel count must match expected combinatorics.")
        add(results, "physical_claim_release", row.get("physical_claim_release") == "blocked_no_physics_claim", row.get("physical_claim_release", "missing"), "blocked_no_physics_claim", "Physics claims must remain blocked.")

    for rel in MARKDOWN_FILES:
        path = base / rel
        if path.exists():
            text = path.read_text(encoding="utf-8")
            hits = [phrase for phrase in FORBIDDEN_MARKDOWN_PHRASES if phrase in text]
            add(results, f"no_forbidden_markdown_text:{rel}", len(hits) == 0, "|".join(hits) if hits else "none", "none", "Markdown must not contain forbidden claim text.")

    output_dir = base / "validation"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "validation_results.csv"
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["validation_id", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking"])
        writer.writerows(results)

    failures = [row for row in results if row[2] != "pass"]
    print(f"validation_results={output_path}")
    print(f"checks={len(results)} failures={len(failures)}")
    for row in failures:
        print(f"FAIL {row[1]}: observed={row[4]} expected={row[5]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

