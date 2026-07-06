#!/usr/bin/env python3
"""Validate the PBR nullmodel design package."""
from __future__ import annotations

import csv
import json
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
        required_columns = {"nullmodel_id", "nullmodel_key", "purpose", "preserved_quantities", "randomized_quantities", "expected_diagnostic_outputs", "admissibility_criteria", "failure_modes", "required_input_artifacts", "execution_authorization_status", "claim_boundary", "next_gate_implication"}
        add(rows, "family_required_columns", required_columns.issubset(set(families[0].keys()) if families else set()), ",".join(families[0].keys()) if families else "missing", ",".join(sorted(required_columns)), "Family spec includes required fields.")

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

    diff_check = subprocess.run(["git", "diff", "--check"], cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    add(rows, "git_diff_check", diff_check.returncode == 0, diff_check.stdout.strip() or "ok", "ok", "git diff --check passes.")

    changed = subprocess.run(["git", "status", "--short"], cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    outside = []
    prefix = f"?? runs/{RUN_ID}/"
    for line in changed.stdout.splitlines():
        if line and not line.startswith(prefix):
            outside.append(line)
    add(rows, "no_files_outside_run_package_modified", not outside, "|".join(outside) if outside else "none", "none", "No files outside the run package are modified.")

    output = base / "validation/validation_results.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["validation_id", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking"])
        writer.writerows(rows)

    failures = [row for row in rows if row[2] != "pass"]
    print(f"validation_results={output.relative_to(repo_root)}")
    print(f"checks={len(rows)}")
    print(f"failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure[1]}: observed={failure[4]} expected={failure[5]}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
