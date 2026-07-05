#!/usr/bin/env python3
"""Validate QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01 package files."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01"

REQUIRED_FILES = [
    "README.md",
    "QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01.md",
    "RUN_COMMANDS_PBR_STATE_SPEC01.md",
    "data/state_spec_manifest.json",
    "data/pbr_minimal_object_definition.csv",
    "data/pbr_field_registry.csv",
    "data/pbr_concept_definition.csv",
    "data/pbr_admissibility_gates.csv",
    "data/pbr_psd_gate_spec.csv",
    "data/pbr_claim_boundaries.csv",
    "data/pbr_external_suggestion_triage.csv",
    "data/pbr_redteam_action_items.csv",
    "sql/001_create_qsb_pbr_state_spec.sql",
    "sql/002_insert_qsb_pbr_state_spec.sql",
    "sql/003_validation_queries.sql",
    "scripts/psd_gate_template.py",
]

REQUIRED_LOCAL_FIELDS = {"H_i", "Phi_i", "M_i", "gamma_i", "sigma_i"}
REQUIRED_PSD_FIELDS = {
    "matrix_id",
    "matrix_source",
    "n",
    "is_square",
    "is_hermitian",
    "max_hermitian_deviation",
    "min_diagonal",
    "lambda_min",
    "lambda_max",
    "negative_eigenvalue_count",
    "negative_eigenvalue_mass",
    "tolerance",
    "psd_pass",
    "admissibility_result",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add(results: List[Tuple[str, str, str]], check: str, status: bool, detail: str) -> None:
    results.append((check, "pass" if status else "fail", detail))


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    results: List[Tuple[str, str, str]] = []

    for rel in REQUIRED_FILES:
        add(results, f"file_exists:{rel}", (base / rel).exists(), str(base / rel))

    manifest_path = base / "data/state_spec_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        add(results, "manifest_run_id", manifest.get("run_id") == RUN_ID, manifest.get("run_id", "missing"))
        add(
            results,
            "manifest_claim_blocked",
            manifest.get("physical_claim_release") == "blocked_no_physics_claim",
            manifest.get("physical_claim_release", "missing"),
        )
        add(
            results,
            "manifest_primary_gate_psd",
            "PSD" in manifest.get("primary_gate", ""),
            manifest.get("primary_gate", "missing"),
        )

    field_path = base / "data/pbr_field_registry.csv"
    if field_path.exists():
        rows = read_csv(field_path)
        fields = {r.get("field_symbol") for r in rows if r.get("required") == "yes"}
        add(results, "required_local_fields", REQUIRED_LOCAL_FIELDS.issubset(fields), ",".join(sorted(fields)))

    gate_path = base / "data/pbr_admissibility_gates.csv"
    if gate_path.exists():
        rows = read_csv(gate_path)
        gates = {r.get("gate_id") for r in rows}
        add(results, "psd_gate_present", "GATE-PSD-01" in gates, ",".join(sorted(gates)))

    psd_path = base / "data/pbr_psd_gate_spec.csv"
    if psd_path.exists():
        rows = read_csv(psd_path)
        psd_fields = {r.get("field_name") for r in rows}
        add(results, "psd_required_fields", REQUIRED_PSD_FIELDS.issubset(psd_fields), ",".join(sorted(psd_fields)))

    boundary_path = base / "data/pbr_claim_boundaries.csv"
    if boundary_path.exists():
        rows = read_csv(boundary_path)
        blocked = [r for r in rows if r.get("boundary_type") == "blocked_claim"]
        allowed = [r for r in rows if r.get("boundary_type") == "allowed_claim"]
        unsafe = [r for r in blocked if not r.get("release_status", "").startswith("blocked")]
        add(results, "blocked_claims_present", len(blocked) >= 5, str(len(blocked)))
        add(results, "allowed_claims_present", len(allowed) >= 2, str(len(allowed)))
        add(results, "blocked_claims_release_status", len(unsafe) == 0, f"unsafe={len(unsafe)}")

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
