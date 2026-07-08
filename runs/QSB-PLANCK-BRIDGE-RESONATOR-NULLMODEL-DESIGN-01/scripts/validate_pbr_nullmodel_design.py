#!/usr/bin/env python3
"""Validate the PBR nullmodel design package."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01"
EXECUTION_STATUS = "design_only_not_executed"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
EXTERNAL_READINESS = "internal_only"
REQUIRED_FAMILIES = {
    "label_permutation_null",
    "lag_preserving_shuffle_null",
    "random_gram_psd_null",
    "directed_pair_rewire_null",
    "sign_flip_antiparallel_null",
}
REQUIRED_FILES = [
    "README.md",
    f"{RUN_ID}.md",
    "RUN_COMMANDS_PBR_NULLMODEL_DESIGN01.md",
    "data/nullmodel_design_summary.csv",
    "data/nullmodel_family_spec.csv",
    "data/claim_boundaries.csv",
    "data/input_artifact_requirements.csv",
    "data/gate_decision.csv",
    "data/nullmodel_diagnostics_required.csv",
    "data/nullmodel_failure_modes.csv",
    "data/nullmodel_execution_authorization.csv",
    "data/nullmodel_design_manifest.json",
    "docs/PBR_NULLMODEL_DESIGN_SUMMARY_DE.md",
    "docs/PBR_NULLMODEL_DESIGN_CLAIM_BOUNDARY_DE.md",
    "docs/PBR_NULLMODEL_DESIGN_NEXT_GATE_DE.md",
    "scripts/run_pbr_nullmodel_design.py",
    "scripts/validate_pbr_nullmodel_design.py",
    "sql/001_create_qsb_pbr_nullmodel_design.sql",
    "sql/002_insert_qsb_pbr_nullmodel_design.sql",
    "sql/003_validation_queries.sql",
    "validation/validation_results.csv",
]
CSV_FILES = [rel for rel in REQUIRED_FILES if rel.endswith(".csv")]
TEXT_SUFFIXES = {".md", ".py", ".sql", ".json", ".csv"}
FORBIDDEN_PHRASES = [
    "QSB " + "is physically validated",
    "PBR " + "exists physically",
    "The six lag axes " + "are spacetime dimensions",
    "Spacetime emergence " + "is proven",
    "Empirical validation " + "exists",
]
ALLOWED_CONTEXT_WORDS = [
    "blocked",
    "prohibited",
    "claim-boundary",
    "claim boundary",
    "gesperrt",
    "verboten",
]
NO_EXECUTION_PATTERNS = [
    "nullmodel_result",
    "samples_generated",
    "p_value",
    "empirical_quantile",
    "executed_successfully",
]
EXPECTED_CSV_COLUMNS = {
    "pbr_nullmodel_design_summary": ["run_id", "previous_run_id", "design_status", "execution_status", "claim_status", "physical_claim_release", "external_readiness", "next_gate", "schema_name", "nullmodel_family_count", "formal_reference_finding"],
    "pbr_nullmodel_family_spec": ["run_id", "nullmodel_id", "nullmodel_key", "purpose", "preserved_quantities", "randomized_quantities", "expected_diagnostic_outputs", "admissibility_criteria", "failure_modes", "required_input_artifacts", "execution_authorization_status", "claim_boundary", "next_gate_implication"],
    "pbr_nullmodel_claim_boundaries": ["run_id", "boundary_id", "claim_key", "status", "claim_boundary_text"],
    "pbr_nullmodel_input_artifact_requirements": ["run_id", "artifact_id", "artifact_key", "required_path", "required_for", "status"],
    "pbr_nullmodel_gate_decision": ["run_id", "gate_id", "gate_name", "gate_decision", "execution_status", "physical_claim_release", "external_readiness", "next_gate", "revision_trigger"],
    "pbr_nullmodel_diagnostics_required": ["run_id", "nullmodel_key", "diagnostic_key", "required", "execution_status", "output_claim_status"],
    "pbr_nullmodel_failure_modes": ["run_id", "nullmodel_key", "failure_mode_id", "failure_mode", "mitigation_status"],
    "pbr_nullmodel_execution_authorization": ["run_id", "nullmodel_key", "execution_authorization_status", "authorization_note", "required_before_execution"],
    "pbr_nullmodel_validation_results": ["run_id", "validation_id", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking"],
}
CSV_BY_TABLE = {
    "pbr_nullmodel_design_summary": "data/nullmodel_design_summary.csv",
    "pbr_nullmodel_family_spec": "data/nullmodel_family_spec.csv",
    "pbr_nullmodel_claim_boundaries": "data/claim_boundaries.csv",
    "pbr_nullmodel_input_artifact_requirements": "data/input_artifact_requirements.csv",
    "pbr_nullmodel_gate_decision": "data/gate_decision.csv",
    "pbr_nullmodel_diagnostics_required": "data/nullmodel_diagnostics_required.csv",
    "pbr_nullmodel_failure_modes": "data/nullmodel_failure_modes.csv",
    "pbr_nullmodel_execution_authorization": "data/nullmodel_execution_authorization.csv",
    "pbr_nullmodel_validation_results": "validation/validation_results.csv",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add(rows: List[Tuple[str, str, str, str, str, str, str, str]], name: str, ok: bool, observed: str, expected: str, message: str, severity: str = "error", blocking: str = "yes") -> None:
    rows.append((f"NM-VAL-{len(rows) + 1:03d}", name, "pass" if ok else "fail", severity, observed, expected, message, blocking))


def has_lf_only(path: Path) -> bool:
    data = path.read_bytes()
    return b"\r\n" not in data and b"\r" not in data


def has_exactly_one_lf(path: Path) -> bool:
    data = path.read_bytes()
    return data.endswith(b"\n") and not data.endswith(b"\n\n")


def has_trailing_whitespace(path: Path) -> bool:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.rstrip() != line:
            return True
    return False


def phrase_allowed(text: str, phrase: str) -> bool:
    lowered = text.lower()
    start = 0
    phrase_lower = phrase.lower()
    while True:
        idx = lowered.find(phrase_lower, start)
        if idx < 0:
            return True
        window = lowered[max(0, idx - 120): idx + len(phrase_lower) + 120]
        if not any(word in window for word in ALLOWED_CONTEXT_WORDS):
            return False
        start = idx + len(phrase_lower)


def csv_header(path: Path) -> List[str]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return next(reader, [])


def copy_columns(sql_text: str, table: str) -> List[str]:
    pattern = re.compile(rf"\\copy\s+\S+\.{table}\s+\(([^)]*)\)", re.IGNORECASE)
    match = pattern.search(sql_text)
    if not match:
        return []
    return [part.strip() for part in match.group(1).split(",")]


def status_path(line: str) -> str:
    path = line[3:] if len(line) > 3 else ""
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    base = base.resolve()
    repo_root = base.parents[1]
    rows: List[Tuple[str, str, str, str, str, str, str, str]] = []

    for rel in REQUIRED_FILES:
        exists = (base / rel).exists() or rel == "validation/validation_results.csv"
        add(rows, f"file_exists:{rel}", exists, rel, "exists", "Required file exists.")

    for rel in REQUIRED_FILES:
        path = base / rel
        if path.exists() and path.suffix in TEXT_SUFFIXES:
            try:
                path.read_text(encoding="utf-8")
                utf_ok = True
            except UnicodeDecodeError:
                utf_ok = False
            add(rows, f"utf8:{rel}", utf_ok, "utf-8" if utf_ok else "decode_error", "utf-8", "Generated text file is UTF-8.")
            add(rows, f"lf_only:{rel}", has_lf_only(path), "lf_only" if has_lf_only(path) else "crlf_or_cr", "lf_only", "Generated text file uses LF line endings.")
            add(rows, f"single_final_lf:{rel}", has_exactly_one_lf(path), "one_lf" if has_exactly_one_lf(path) else "not_one_lf", "one_lf", "Generated text file ends with exactly one LF.")
            add(rows, f"no_trailing_whitespace:{rel}", not has_trailing_whitespace(path), "none" if not has_trailing_whitespace(path) else "present", "none", "Generated text file has no trailing whitespace.")

    for rel in CSV_FILES:
        path = base / rel
        if path.exists():
            add(rows, f"csv_lf:{rel}", has_lf_only(path), "lf_only" if has_lf_only(path) else "crlf_or_cr", "lf_only", "CSV file uses LF line endings.")

    summary_path = base / "data/nullmodel_design_summary.csv"
    if summary_path.exists():
        summary_rows = read_csv(summary_path)
        add(rows, "summary_single_row", len(summary_rows) == 1, str(len(summary_rows)), "1", "Summary has exactly one row.")
        summary = summary_rows[0] if summary_rows else {}
        add(rows, "run_id_consistency_summary", summary.get("run_id") == RUN_ID, summary.get("run_id", "missing"), RUN_ID, "Run ID is consistent.")
        add(rows, "execution_status_design_only", summary.get("execution_status") == EXECUTION_STATUS, summary.get("execution_status", "missing"), EXECUTION_STATUS, "Execution status is design only.")
        add(rows, "physical_claim_release_blocked", summary.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE, summary.get("physical_claim_release", "missing"), PHYSICAL_CLAIM_RELEASE, "Physical claim release is blocked.")
        add(rows, "external_readiness_internal_only", summary.get("external_readiness") == EXTERNAL_READINESS, summary.get("external_readiness", "missing"), EXTERNAL_READINESS, "External readiness is internal only.")
        add(rows, "next_gate_allowed", summary.get("next_gate") in {"nullmodel_execution_required", "nullmodel_design_revision_required"}, summary.get("next_gate", "missing"), "nullmodel_execution_required or nullmodel_design_revision_required", "Next gate is allowed.")

    family_path = base / "data/nullmodel_family_spec.csv"
    if family_path.exists():
        families = read_csv(family_path)
        keys = [row.get("nullmodel_key", "") for row in families]
        add(rows, "all_families_present_exactly_once", set(keys) == REQUIRED_FAMILIES and len(keys) == len(set(keys)) == 5, ",".join(sorted(keys)), ",".join(sorted(REQUIRED_FAMILIES)), "All five nullmodel families are present exactly once.")
        add(rows, "family_execution_design_only", all(row.get("execution_authorization_status") == EXECUTION_STATUS for row in families), "checked", EXECUTION_STATUS, "Each family is design-only.")
        required_columns = set(EXPECTED_CSV_COLUMNS["pbr_nullmodel_family_spec"])
        add(rows, "family_required_columns", required_columns.issubset(set(families[0].keys()) if families else set()), ",".join(families[0].keys()) if families else "missing", ",".join(sorted(required_columns)), "Family spec includes required fields.")
        add(rows, "family_next_gate_implication_nonempty", all(row.get("next_gate_implication") for row in families), "checked", "nonempty", "Each family row has next_gate_implication.")
        add(rows, "family_next_gate_implication_value", all(row.get("next_gate_implication") == "nullmodel_execution_required" for row in families), ",".join(sorted({row.get("next_gate_implication", "") for row in families})), "nullmodel_execution_required", "Each family row points to the execution gate.")
        add(rows, "family_run_id_consistency", all(row.get("run_id") == RUN_ID for row in families), "checked", RUN_ID, "Each family row carries the run ID.")

    gate_path = base / "data/gate_decision.csv"
    if gate_path.exists():
        gate_rows = read_csv(gate_path)
        gate = gate_rows[0] if gate_rows else {}
        add(rows, "gate_execution_design_only", gate.get("execution_status") == EXECUTION_STATUS, gate.get("execution_status", "missing"), EXECUTION_STATUS, "Gate records design-only status.")
        add(rows, "gate_next_gate_allowed", gate.get("next_gate") in {"nullmodel_execution_required", "nullmodel_design_revision_required"}, gate.get("next_gate", "missing"), "nullmodel_execution_required or nullmodel_design_revision_required", "Gate next step is allowed.")

    manifest_path = base / "data/nullmodel_design_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        add(rows, "manifest_run_id", manifest.get("run_id") == RUN_ID, manifest.get("run_id", "missing"), RUN_ID, "Manifest run ID is consistent.")
        add(rows, "manifest_no_execution", manifest.get("execution_status") == EXECUTION_STATUS, manifest.get("execution_status", "missing"), EXECUTION_STATUS, "Manifest records no execution.")

    all_text = ""
    for path in base.rglob("*"):
        rel_path = path.relative_to(base)
        if rel_path.parts and rel_path.parts[0] in {"scripts", "validation"}:
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            all_text += "\n" + path.read_text(encoding="utf-8")
    add(rows, "no_nullmodel_execution_output_claimed", not any(pattern in all_text for pattern in NO_EXECUTION_PATTERNS), "pattern_absent" if not any(pattern in all_text for pattern in NO_EXECUTION_PATTERNS) else "pattern_present", "pattern_absent", "No nullmodel execution outputs are claimed.")
    for phrase in FORBIDDEN_PHRASES:
        add(rows, f"forbidden_phrase_context:{phrase}", phrase_allowed(all_text, phrase), "allowed_context_only" if phrase_allowed(all_text, phrase) else "affirmative_context_found", "allowed_context_only", "Forbidden phrases occur only in blocked/prohibited/claim-boundary contexts.")

    script_text = (base / "scripts/run_pbr_nullmodel_design.py").read_text(encoding="utf-8") if (base / "scripts/run_pbr_nullmodel_design.py").exists() else ""
    add(rows, "csv_writer_lineterminator", 'lineterminator="\\n"' in script_text, "present" if 'lineterminator="\\n"' in script_text else "missing", 'lineterminator="\\n"', "CSV writer uses LF lineterminator.")
    add(rows, "json_indent_ensure_ascii_false", "indent=2" in script_text and "ensure_ascii=False" in script_text, "present" if "indent=2" in script_text and "ensure_ascii=False" in script_text else "missing", "indent=2 and ensure_ascii=False", "JSON writer uses required options.")

    create_sql_path = base / "sql/001_create_qsb_pbr_nullmodel_design.sql"
    insert_sql_path = base / "sql/002_insert_qsb_pbr_nullmodel_design.sql"
    create_sql = create_sql_path.read_text(encoding="utf-8") if create_sql_path.exists() else ""
    insert_sql = insert_sql_path.read_text(encoding="utf-8") if insert_sql_path.exists() else ""
    add(rows, "sql_family_table_has_next_gate_implication", "next_gate_implication text NOT NULL" in create_sql, "present" if "next_gate_implication text NOT NULL" in create_sql else "missing", "present", "Family table includes next_gate_implication.")
    add(rows, "sql_validation_results_has_run_id", "pbr_nullmodel_validation_results" in create_sql and "run_id text NOT NULL" in create_sql, "present" if "pbr_nullmodel_validation_results" in create_sql and "run_id text NOT NULL" in create_sql else "missing", "present", "Validation results table has run_id.")
    add(rows, "sql_insert_transactional", "BEGIN;" in insert_sql and "COMMIT;" in insert_sql and "\\set ON_ERROR_STOP on" in insert_sql, "present" if "BEGIN;" in insert_sql and "COMMIT;" in insert_sql and "\\set ON_ERROR_STOP on" in insert_sql else "missing", "transaction with ON_ERROR_STOP", "Insert script is transactional.")
    add(rows, "sql_family_copy_uses_csv_artifact", "data/nullmodel_family_spec.csv" in insert_sql, "present" if "data/nullmodel_family_spec.csv" in insert_sql else "missing", "present", "Family import uses the CSV artifact.")
    add(rows, "sql_no_embedded_family_copy_rows", "COPY pbr_nullmodel_family_spec FROM stdin" not in insert_sql and "COPY qsb_planck_bridge.pbr_nullmodel_family_spec FROM stdin" not in insert_sql, "none", "none", "Family import does not use embedded COPY rows.")
    for table, expected in EXPECTED_CSV_COLUMNS.items():
        rel = CSV_BY_TABLE[table]
        path = base / rel
        if path.exists() and table != "pbr_nullmodel_validation_results":
            header = csv_header(path)
            add(rows, f"csv_header_contract:{rel}", header == expected, ",".join(header), ",".join(expected), "CSV header matches expected table contract.")
        elif table == "pbr_nullmodel_validation_results":
            add(rows, f"csv_header_contract:{rel}", True, ",".join(expected), ",".join(expected), "Validation CSV header is written by this validator.")
        columns = copy_columns(insert_sql, table)
        add(rows, f"copy_column_contract:{table}", columns == expected, ",".join(columns) if columns else "missing", ",".join(expected), "SQL COPY column list matches expected table contract.")

    diff_check = subprocess.run(["git", "diff", "--check"], cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    add(rows, "git_diff_check", diff_check.returncode == 0, diff_check.stdout.strip() or "ok", "ok", "git diff --check passes.")

    changed = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    outside = []
    for line in changed.stdout.splitlines():
        path = status_path(line)
        if line and not path.startswith(f"runs/{RUN_ID}/"):
            outside.append(line)
    add(rows, "no_files_outside_run_package_modified", not outside, "|".join(outside) if outside else "none", "none", "No files outside the run package are modified.")

    output = base / "validation/validation_results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["run_id", "validation_id", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking"])
        for row in rows:
            writer.writerow([RUN_ID, *row])

    failures = [row for row in rows if row[2] != "pass"]
    print(f"validation_results={output.relative_to(repo_root)}")
    print(f"checks={len(rows)}")
    print(f"failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure[1]}: observed={failure[4]} expected={failure[5]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
