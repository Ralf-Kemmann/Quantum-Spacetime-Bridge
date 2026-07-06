#!/usr/bin/env python3
"""Validate the PBR result review package."""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01"

REQUIRED_FILES = [
    "README.md",
    "QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01.md",
    "RUN_COMMANDS_PBR_RESULT_REVIEW01.md",
    "data/input_run_lineage.csv",
    "data/result_review_summary.csv",
    "data/formal_findings.csv",
    "data/construction_bound_findings.csv",
    "data/blocked_claims.csv",
    "data/recommended_next_tests.csv",
    "data/external_communication_readiness.csv",
    "data/result_review_manifest.json",
    "docs/PBR_RESULT_REVIEW_SUMMARY_DE.md",
    "docs/PBR_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md",
    "docs/PBR_RESULT_REVIEW_NEXT_STEPS_DE.md",
    "scripts/run_pbr_result_review.py",
    "scripts/validate_pbr_result_review.py",
    "sql/001_create_qsb_pbr_result_review.sql",
    "sql/002_insert_qsb_pbr_result_review.sql",
    "sql/003_validation_queries.sql",
]
CSV_FILES = [p for p in REQUIRED_FILES if p.endswith(".csv")]
MARKDOWN_FILES = [p for p in REQUIRED_FILES if p.endswith(".md")]
FORBIDDEN = [
    "QSB is physically validated",
    "Planck-Bridge-Resonators exist physically",
    "six lag axes are spacetime dimensions",
    "K matrix proves spacetime emergence",
    "experimental evidence",
    "discovery of physical modes",
]
REQUIRED_BLOCKED_KEYS = {
    "physical_validation_qsb_blocked",
    "pbr_physical_existence_blocked",
    "spacetime_emergence_proof_blocked",
    "empirical_validation_blocked",
    "lag_axes_physical_dimensions_blocked",
}
REQUIRED_TEST_KEYS = {
    "nullmodel_design_review",
    "robustness_under_perturbation_noise",
    "label_permutation_controls",
    "lineage_audit_k_candidate_construction",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add(rows: List[Tuple[str, str, str, str, str, str, str, str]], name: str, ok: bool, observed: str, expected: str, message: str, severity: str = "error", blocking: str = "yes") -> None:
    rows.append((f"RR-VAL-{len(rows) + 1:03d}", name, "pass" if ok else "fail", severity, observed, expected, message, blocking))


def has_blank_row(path: Path) -> bool:
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if row and all(cell.strip() == "" for cell in row):
                return True
    return False


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    repo_root = base.resolve().parents[1]
    rows: List[Tuple[str, str, str, str, str, str, str, str]] = []

    for rel in REQUIRED_FILES:
        add(rows, f"file_exists:{rel}", (base / rel).exists(), str(base / rel), "exists", "Required file exists.")
    for rel in CSV_FILES:
        path = base / rel
        if path.exists():
            add(rows, f"no_blank_rows:{rel}", not has_blank_row(path), "blank_row_found" if has_blank_row(path) else "none", "none", "CSV must not contain blank rows.")

    for run_id in ["QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01", "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01", "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01"]:
        add(rows, f"prior_run_exists:{run_id}", (repo_root / "runs" / run_id).is_dir(), str(repo_root / "runs" / run_id), "exists", "Prior run directory exists.")

    summary_path = base / "data/result_review_summary.csv"
    if summary_path.exists():
        summary_rows = read_csv(summary_path)
        add(rows, "summary_single_row", len(summary_rows) == 1, str(len(summary_rows)), "1", "Review summary must have exactly one row.")
        summary = summary_rows[0] if summary_rows else {}
        add(rows, "physical_claim_release_blocked", summary.get("physical_claim_release") == "blocked_no_physics_claim", summary.get("physical_claim_release", "missing"), "blocked_no_physics_claim", "Physics claims remain blocked.")
        add(rows, "claim_status_result_review_only", summary.get("claim_status") == "result_review_only", summary.get("claim_status", "missing"), "result_review_only", "Claim status is review only.")
        add(rows, "next_gate_nullmodel", summary.get("next_gate") == "nullmodel_design_required", summary.get("next_gate", "missing"), "nullmodel_design_required", "Next gate is nullmodel design.")

    blocked_path = base / "data/blocked_claims.csv"
    if blocked_path.exists():
        blocked_keys = {r.get("blocked_claim_key", "") for r in read_csv(blocked_path)}
        add(rows, "required_blocked_claims", REQUIRED_BLOCKED_KEYS.issubset(blocked_keys), ",".join(sorted(blocked_keys)), ",".join(sorted(REQUIRED_BLOCKED_KEYS)), "Required blocked claims are present.")

    tests_path = base / "data/recommended_next_tests.csv"
    if tests_path.exists():
        test_keys = {r.get("test_key", "") for r in read_csv(tests_path)}
        add(rows, "required_next_tests", REQUIRED_TEST_KEYS.issubset(test_keys), ",".join(sorted(test_keys)), ",".join(sorted(REQUIRED_TEST_KEYS)), "Required next tests are present.")

    for rel in MARKDOWN_FILES:
        path = base / rel
        if path.exists():
            text = path.read_text(encoding="utf-8")
            hits = [phrase for phrase in FORBIDDEN if phrase in text]
            add(rows, f"no_forbidden_markdown_text:{rel}", len(hits) == 0, "|".join(hits) if hits else "none", "none", "Markdown claim hygiene.")

    output = base / "validation/validation_results.csv"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["validation_id", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking"])
        writer.writerows(rows)

    failures = [r for r in rows if r[2] != "pass"]
    print(f"validation_results={output}")
    print(f"checks={len(rows)} failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure[1]}: observed={failure[4]} expected={failure[5]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
