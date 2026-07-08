#!/usr/bin/env python3
"""Validate the PBR lag mechanism design-only package."""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
FAMILIES = {
    "index_relabeling_test",
    "order_scrambling_test",
    "independent_lag_variable_test",
    "shift_operator_test",
    "toeplitz_dependency_test",
    "physical_proxy_test",
    "nullmodel_operationalization_review",
}
CASES = {"pure_index_construction", "formal_lag_mechanism_candidate", "physical_proxy_candidate"}
BLOCKED_CLAIMS = {
    "QSB is physically " + "validated",
    "PBR exists " + "physically",
    "six lag axes are spacetime " + "dimensions",
    "spacetime emergence is " + "proven",
    "empirical validation " + "exists",
    "lag classes are physical " + "dimensions",
    "lag mechanism is physically " + "proven",
    "no_specificity disproves QSB",
    "no_specificity proves QSB",
}
REQUIRED_FILES = [
    "README.md",
    f"{RUN_ID}.md",
    "RUN_COMMANDS_PBR_LAG_MECHANISM_DESIGN01.md",
    "data/lag_mechanism_design_summary.csv",
    "data/lag_mechanism_test_family_spec.csv",
    "data/lag_mechanism_decision_cases.csv",
    "data/lag_mechanism_required_inputs.csv",
    "data/lag_mechanism_required_metrics.csv",
    "data/lag_mechanism_claim_boundaries.csv",
    "data/lag_mechanism_next_gate_decision.csv",
    "data/lag_mechanism_failure_modes.csv",
    "data/lag_mechanism_design_manifest.json",
    "docs/PBR_LAG_MECHANISM_DESIGN_SUMMARY_DE.md",
    "docs/PBR_LAG_MECHANISM_DESIGN_TESTS_DE.md",
    "docs/PBR_LAG_MECHANISM_DESIGN_CLAIM_BOUNDARY_DE.md",
    "docs/PBR_LAG_MECHANISM_DESIGN_NEXT_GATE_DE.md",
    "scripts/run_pbr_lag_mechanism_design.py",
    "scripts/validate_pbr_lag_mechanism_design.py",
    "sql/001_create_qsb_pbr_lag_mechanism_design.sql",
    "sql/002_insert_qsb_pbr_lag_mechanism_design.sql",
    "sql/003_validation_queries.sql",
    "validation/validation_results.csv",
]
FORBIDDEN = [
    "QSB is physically " + "validated",
    "PBR exists " + "physically",
    "six lag axes are spacetime " + "dimensions",
    "spacetime emergence is " + "proven",
    "empirical validation " + "exists",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["run_id", "check_name", "status", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add(rows: List[Dict[str, str]], name: str, ok: bool, detail: str) -> None:
    rows.append({"run_id": RUN_ID, "check_name": name, "status": "pass" if ok else "fail", "detail": detail})


def has_lf_only(path: Path) -> bool:
    data = path.read_bytes()
    return b"\r\n" not in data and b"\r" not in data


def forbidden_context_ok(text: str, phrase: str) -> bool:
    start = 0
    while True:
        idx = text.find(phrase, start)
        if idx < 0:
            return True
        window = text[max(0, idx - 120): idx + len(phrase) + 120].lower()
        if not any(marker in window for marker in ["blocked", "prohibited", "not allowed", "claim boundary", "gesperrt", "nicht freigegeben"]):
            return False
        start = idx + len(phrase)


def validate_copy_blocks(sql_text: str) -> bool:
    lines = sql_text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("COPY "):
            match = re.search(r"\(([^)]+)\)", lines[i])
            if not match or i + 1 >= len(lines):
                return False
            count = len([col.strip() for col in match.group(1).split(",")])
            if len(lines[i + 1].split("\t")) != count:
                return False
            i += 2
            while i < len(lines) and lines[i] != r"\.":
                if len(lines[i].split("\t")) != count:
                    return False
                i += 1
            if i >= len(lines):
                return False
        i += 1
    return True


def sql_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def update_validation_import_block(run_dir: Path, rows: List[Dict[str, str]]) -> None:
    sql_path = run_dir / "sql/002_insert_qsb_pbr_lag_mechanism_design.sql"
    text = sql_path.read_text(encoding="utf-8")
    start = "-- BEGIN generated validation results import"
    end = "-- END generated validation results import"
    if start in text and end in text:
        text = text.split(start, 1)[0].rstrip() + "\n" + text.split(end, 1)[1].lstrip()
    fields = ["run_id", "check_name", "status", "detail"]
    block = [
        start,
        "COPY qsb_planck_bridge.pbr_lag_mechanism_validation_results (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');",
        "\t".join(fields),
    ]
    for row in rows:
        block.append("\t".join(sql_value(row[field]) for field in fields))
    block.extend([r"\.", end, ""])
    sql_path.write_text(text.replace("COMMIT;\n", "\n".join(block) + "COMMIT;\n"), encoding="utf-8")


def text_for_scan(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.name == "002_insert_qsb_pbr_lag_mechanism_design.sql":
        start = "-- BEGIN generated validation results import"
        end = "-- END generated validation results import"
        if start in text and end in text:
            return text.split(start, 1)[0] + text.split(end, 1)[1]
    return text


def main() -> int:
    run_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(f"runs/{RUN_ID}").resolve()
    repo_root = run_dir.parents[1]
    rows: List[Dict[str, str]] = []
    for rel in REQUIRED_FILES:
        add(rows, f"exists:{rel}", (run_dir / rel).exists(), rel)
    if not all((run_dir / rel).exists() for rel in REQUIRED_FILES):
        write_csv(run_dir / "validation/validation_results.csv", rows)
        return 1
    summary = read_csv(run_dir / "data/lag_mechanism_design_summary.csv")
    families = read_csv(run_dir / "data/lag_mechanism_test_family_spec.csv")
    cases = read_csv(run_dir / "data/lag_mechanism_decision_cases.csv")
    claims = read_csv(run_dir / "data/lag_mechanism_claim_boundaries.csv")
    next_gate = read_csv(run_dir / "data/lag_mechanism_next_gate_decision.csv")
    all_rows = summary + families + cases + claims + next_gate
    add(rows, "run_id_consistency", all(row.get("run_id") == RUN_ID for row in all_rows), RUN_ID)
    add(rows, "design_only_execution_status", summary[0].get("execution_status") == "design_only_not_executed", summary[0].get("execution_status", "missing"))
    manifest = (run_dir / "data/lag_mechanism_design_manifest.json").read_text(encoding="utf-8")
    add(rows, "no_tests_executed", '"lag_mechanism_tests_executed": false' in manifest and '"nullmodels_executed": false' in manifest, "manifest flags")
    add(rows, "all_seven_test_families_once", {row.get("test_key") for row in families} == FAMILIES and len(families) == 7, str(sorted(row.get("test_key", "") for row in families)))
    add(rows, "all_three_decision_cases_once", {row.get("lag_structure_status") for row in cases} == CASES and len(cases) == 3, str(sorted(row.get("lag_structure_status", "") for row in cases)))
    add(rows, "input_specificity_no_specificity", summary[0].get("input_specificity_classification") == "no_specificity", summary[0].get("input_specificity_classification", "missing"))
    add(rows, "input_critical_nullmodel", summary[0].get("input_critical_nullmodel") == "lag_preserving_shuffle_null", summary[0].get("input_critical_nullmodel", "missing"))
    add(rows, "input_critical_reproduction_rate", summary[0].get("input_critical_reproduction_rate") == "1.0", summary[0].get("input_critical_reproduction_rate", "missing"))
    add(rows, "physical_claim_release_blocked", all(row.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for row in summary + cases + claims + next_gate), PHYSICAL_CLAIM_RELEASE)
    add(rows, "next_gate", next_gate[0].get("next_gate") == "lag_mechanism_execution_required", next_gate[0].get("next_gate", "missing"))
    add(rows, "secondary_next_gate", next_gate[0].get("secondary_next_gate") == "nullmodel_operationalization_review_required", next_gate[0].get("secondary_next_gate", "missing"))
    claim_texts = {row.get("claim_text") for row in claims if row.get("status") in {"blocked", "prohibited", "not_allowed"}}
    add(rows, "blocked_claims_present", BLOCKED_CLAIMS.issubset(claim_texts), str(sorted(BLOCKED_CLAIMS - claim_texts)))
    scan_text = "\n".join(
        text_for_scan(path)
        for path in run_dir.rglob("*")
        if path.is_file()
        and path.relative_to(run_dir).as_posix() != "validation/validation_results.csv"
        and path.suffix in {".md", ".csv", ".json", ".sql", ".py"}
    )
    for phrase in FORBIDDEN:
        add(rows, f"forbidden_context:{phrase}", forbidden_context_ok(scan_text, phrase), phrase)
    sql_text = (run_dir / "sql/002_insert_qsb_pbr_lag_mechanism_design.sql").read_text(encoding="utf-8")
    add(rows, "sql_copy_column_lists_match_rows", validate_copy_blocks(sql_text), "COPY TSV blocks")
    csv_files = list((run_dir / "data").glob("*.csv")) + list((run_dir / "validation").glob("*.csv"))
    add(rows, "csv_lf_line_endings", all(has_lf_only(path) for path in csv_files), f"{len(csv_files)} CSV files")
    generator = (run_dir / "scripts/run_pbr_lag_mechanism_design.py").read_text(encoding="utf-8")
    add(rows, "csv_lineterminator_declared", 'lineterminator="\\n"' in generator, "csv.DictWriter lineterminator")
    files = [path for path in run_dir.rglob("*") if path.is_file()]
    add(rows, "utf8_text_files_readable", all(path.read_text(encoding="utf-8") is not None for path in files), f"{len(files)} files")
    diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, text=True, capture_output=True)
    add(rows, "git_diff_check", diff.returncode == 0, diff.stdout.strip() or diff.stderr.strip() or "ok")
    status = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=repo_root, text=True, capture_output=True)
    prefix = f"runs/{RUN_ID}/"
    outside = []
    for line in status.stdout.splitlines():
        path = line[3:] if len(line) > 3 else line
        if path and not path.startswith(prefix):
            outside.append(line)
    add(rows, "no_files_outside_run_package_modified", not outside, "\n".join(outside) if outside else "ok")
    write_csv(run_dir / "validation/validation_results.csv", rows)
    update_validation_import_block(run_dir, rows)
    ok = all(row["status"] == "pass" for row in rows)
    print(f"validation_status={'pass' if ok else 'fail'}")
    print(f"checks={len(rows)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
