#!/usr/bin/env python3
"""Validate the PBR lag mechanism execution package."""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
ALLOWED_DECISIONS = {
    "pure_index_construction",
    "formal_lag_mechanism_candidate",
    "physical_proxy_candidate",
    "inconclusive_requires_more_inputs",
    "blocked_missing_input_artifact",
}
FAMILIES = {
    "index_relabeling_test",
    "order_scrambling_test",
    "independent_lag_variable_test",
    "shift_operator_test",
    "toeplitz_dependency_test",
    "physical_proxy_test",
    "nullmodel_operationalization_review",
}
REQUIRED_FILES = [
    "README.md",
    f"{RUN_ID}.md",
    "RUN_COMMANDS_PBR_LAG_MECHANISM_EXECUTION01.md",
    "data/lag_mechanism_execution_summary.csv",
    "data/lag_mechanism_test_results.csv",
    "data/index_relabeling_results.csv",
    "data/order_scrambling_results.csv",
    "data/independent_lag_variable_results.csv",
    "data/shift_operator_results.csv",
    "data/toeplitz_dependency_results.csv",
    "data/physical_proxy_results.csv",
    "data/nullmodel_operationalization_review.csv",
    "data/lag_mechanism_decision.csv",
    "data/claim_boundaries.csv",
    "data/input_run_lineage.csv",
    "data/lag_mechanism_execution_manifest.json",
    "docs/PBR_LAG_MECHANISM_EXECUTION_SUMMARY_DE.md",
    "docs/PBR_LAG_MECHANISM_EXECUTION_TEST_RESULTS_DE.md",
    "docs/PBR_LAG_MECHANISM_EXECUTION_CLAIM_BOUNDARY_DE.md",
    "docs/PBR_LAG_MECHANISM_EXECUTION_NEXT_GATE_DE.md",
    "docs/PBR_LAG_MECHANISM_EXECUTION_INTERPRETATION_DE.md",
    "scripts/run_pbr_lag_mechanism_execution.py",
    "scripts/validate_pbr_lag_mechanism_execution.py",
    "sql/001_create_qsb_pbr_lag_mechanism_execution.sql",
    "sql/002_insert_qsb_pbr_lag_mechanism_execution.sql",
    "sql/003_validation_queries.sql",
    "validation/validation_results.csv",
]
FORBIDDEN = [
    "QSB is physically " + "validated",
    "PBR exists " + "physically",
    "six lag axes are spacetime " + "dimensions",
    "spacetime emergence is " + "proven",
    "empirical validation " + "exists",
    "lag mechanism is physically " + "proven",
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
    sql_path = run_dir / "sql/002_insert_qsb_pbr_lag_mechanism_execution.sql"
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
    if path.name == "002_insert_qsb_pbr_lag_mechanism_execution.sql":
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
    summary = read_csv(run_dir / "data/lag_mechanism_execution_summary.csv")
    tests = read_csv(run_dir / "data/lag_mechanism_test_results.csv")
    decision = read_csv(run_dir / "data/lag_mechanism_decision.csv")
    claims = read_csv(run_dir / "data/claim_boundaries.csv")
    lineage = read_csv(run_dir / "data/input_run_lineage.csv")
    physical = read_csv(run_dir / "data/physical_proxy_results.csv")
    all_rows = summary + tests + decision + claims + lineage + physical
    add(rows, "run_id_consistency", all(row.get("run_id") == RUN_ID for row in all_rows), RUN_ID)
    lineage_ids = {row.get("source_run_id") for row in lineage}
    add(rows, "lineage_includes_design_and_review", {"QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01", "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01"}.issubset(lineage_ids), ",".join(sorted(lineage_ids)))
    add(rows, "all_seven_test_families", {row.get("test_key") for row in tests} == FAMILIES and len(tests) == 7, ",".join(sorted(row.get("test_key", "") for row in tests)))
    valid_statuses = {"executed", "blocked_missing_required_input", "blocked_missing_physical_proxy_input", "blocked_missing_input_artifact"}
    add(rows, "valid_execution_status_each_test", all(row.get("execution_status") in valid_statuses for row in tests), "status set")
    final_decision = decision[0].get("final_decision_class", "")
    add(rows, "final_decision_allowed", final_decision in ALLOWED_DECISIONS, final_decision)
    add(rows, "physical_claim_release_blocked", all(row.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for row in summary + tests + decision + claims), PHYSICAL_CLAIM_RELEASE)
    proxy_available = physical[0].get("physical_proxy_available") == "True" or physical[0].get("physical_proxy_available") == "true"
    proxy_source = physical[0].get("physical_proxy_source_artifact", "")
    add(rows, "physical_proxy_candidate_requires_source", final_decision != "physical_proxy_candidate" or (proxy_available and proxy_source not in {"", "not_available"}), proxy_source or "not_available")
    add(rows, "missing_proxy_no_proxy_candidate", proxy_available or final_decision != "physical_proxy_candidate", final_decision)
    scan_text = "\n".join(
        text_for_scan(path)
        for path in run_dir.rglob("*")
        if path.is_file()
        and path.relative_to(run_dir).as_posix() != "validation/validation_results.csv"
        and path.suffix in {".md", ".csv", ".json", ".sql", ".py"}
    )
    for phrase in FORBIDDEN:
        add(rows, f"forbidden_context:{phrase}", forbidden_context_ok(scan_text, phrase), phrase)
    sql_text = (run_dir / "sql/002_insert_qsb_pbr_lag_mechanism_execution.sql").read_text(encoding="utf-8")
    add(rows, "sql_copy_column_lists_match_rows", validate_copy_blocks(sql_text), "COPY TSV blocks")
    csv_files = list((run_dir / "data").glob("*.csv")) + list((run_dir / "validation").glob("*.csv"))
    add(rows, "csv_lf_line_endings", all(has_lf_only(path) for path in csv_files), f"{len(csv_files)} CSV files")
    generator = (run_dir / "scripts/run_pbr_lag_mechanism_execution.py").read_text(encoding="utf-8")
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
