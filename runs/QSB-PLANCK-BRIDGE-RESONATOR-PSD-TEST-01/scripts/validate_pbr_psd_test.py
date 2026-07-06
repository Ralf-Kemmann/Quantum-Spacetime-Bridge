#!/usr/bin/env python3
"""Validate QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01 package files."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01"
KNOWN_K_SHA256 = "e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d"
KNOWN_VALIDATION_SHA256 = "a0137b42013e3191657d8b3e0b53c28015cb1eb63e5b6371fc96c4e144bbec27"
KNOWN_LINEAGE_SHA256 = "9b242d40f34d864e4c521d873e94b3bea8f07b573386e99d617cd320d483646a"

REQUIRED_FILES = [
    "README.md",
    "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01.md",
    "RUN_COMMANDS_PBR_PSD_TEST01.md",
    "data/input_lineage.csv",
    "data/psd_gate_result.csv",
    "data/eigenvalue_report.csv",
    "data/claim_boundaries.csv",
    "data/psd_test_manifest.json",
    "docs/PBR_PSD_TEST_SUMMARY_DE.md",
    "scripts/run_pbr_psd_test.py",
    "scripts/validate_pbr_psd_test.py",
    "sql/001_create_qsb_pbr_psd_test.sql",
    "sql/002_insert_qsb_pbr_psd_test.sql",
    "sql/003_validation_queries.sql",
]

FORBIDDEN_MARKDOWN_PHRASES = [
    "QSB is physically validated",
    "Planck-Bridge-Resonators physically exist",
    "K matrix proves spacetime emergence",
    "empirical validation",
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


def add(results: List[Tuple[str, str, str]], check: str, status: bool, detail: str) -> None:
    results.append((check, "pass" if status else "fail", detail))


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    repo_root = base.resolve().parents[1]
    results: List[Tuple[str, str, str]] = []

    for rel in REQUIRED_FILES:
        add(results, f"file_exists:{rel}", (base / rel).exists(), str(base / rel))

    gate_path = base / "data/psd_gate_result.csv"
    if gate_path.exists():
        rows = read_csv(gate_path)
        add(results, "psd_gate_single_row", len(rows) == 1, str(len(rows)))
        if rows:
            row = rows[0]
            add(results, "psd_pass_boolean", row.get("psd_pass") in {"true", "false"}, row.get("psd_pass", "missing"))
            add(
                results,
                "physical_claim_release_blocked",
                row.get("physical_claim_release") == "blocked_no_physics_claim",
                row.get("physical_claim_release", "missing"),
            )
            add(
                results,
                "claim_status_formal_only",
                row.get("claim_status") == "formal_admissibility_result_only",
                row.get("claim_status", "missing"),
            )

    manifest_path = base / "data/psd_test_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        add(results, "manifest_run_id", manifest.get("run_id") == RUN_ID, manifest.get("run_id", "missing"))
        add(
            results,
            "manifest_physical_claim_blocked",
            manifest.get("physical_claim_release") == "blocked_no_physics_claim",
            manifest.get("physical_claim_release", "missing"),
        )

    lineage_path = base / "data/input_lineage.csv"
    if lineage_path.exists():
        rows = read_csv(lineage_path)
        by_id = {r.get("input_id"): r for r in rows}
        add(results, "lineage_k_hash_match", by_id.get("K_candidate_matrix", {}).get("sha256") == KNOWN_K_SHA256, by_id.get("K_candidate_matrix", {}).get("sha256", "missing"))
        add(results, "lineage_validation_hash_match", by_id.get("K_validation_results", {}).get("sha256") == KNOWN_VALIDATION_SHA256, by_id.get("K_validation_results", {}).get("sha256", "missing"))
        add(results, "lineage_bundle_hash_match", by_id.get("matrix_embedded_lineage", {}).get("sha256") == KNOWN_LINEAGE_SHA256, by_id.get("matrix_embedded_lineage", {}).get("sha256", "missing"))

    matrix_path = repo_root / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv"
    validation_path = repo_root / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv"
    if matrix_path.exists():
        add(results, "source_k_hash_match", sha256_file(matrix_path) == KNOWN_K_SHA256, sha256_file(matrix_path))
    if validation_path.exists():
        add(results, "source_validation_hash_match", sha256_file(validation_path) == KNOWN_VALIDATION_SHA256, sha256_file(validation_path))

    md_files = [base / "README.md", base / "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01.md", base / "RUN_COMMANDS_PBR_PSD_TEST01.md", base / "docs/PBR_PSD_TEST_SUMMARY_DE.md"]
    for md_file in md_files:
        if md_file.exists():
            text = md_file.read_text(encoding="utf-8")
            hits = [phrase for phrase in FORBIDDEN_MARKDOWN_PHRASES if phrase in text]
            add(results, f"no_forbidden_markdown_text:{md_file.relative_to(base)}", len(hits) == 0, "|".join(hits) if hits else "none")

    output_dir = base / "validation"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "validation_results.csv"
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["check_name", "result", "detail"])
        writer.writerows(results)

    failures = [r for r in results if r[1] != "pass"]
    print(f"validation_results={output_path}")
    print(f"checks={len(results)} failures={len(failures)}")
    for check, status, detail in failures:
        print(f"FAIL {check}: {detail}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

