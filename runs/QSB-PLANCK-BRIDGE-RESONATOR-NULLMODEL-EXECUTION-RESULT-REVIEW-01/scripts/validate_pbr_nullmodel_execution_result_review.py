#!/usr/bin/env python3
"""Validate the PBR nullmodel execution result-review package."""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01"
INPUT_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
FAMILIES = {
    "label_permutation_null",
    "lag_preserving_shuffle_null",
    "random_gram_psd_null",
    "directed_pair_rewire_null",
    "sign_flip_antiparallel_null",
}
REQUIRED_FILES = [
    "README.md",
    f"{RUN_ID}.md",
    "RUN_COMMANDS_PBR_NULLMODEL_EXECUTION_RESULT_REVIEW01.md",
    "data/input_run_lineage.csv",
    "data/nullmodel_execution_review_summary.csv",
    "data/nullmodel_family_review.csv",
    "data/critical_nullmodel_findings.csv",
    "data/specificity_interpretation.csv",
    "data/claim_boundaries.csv",
    "data/next_gate_decision.csv",
    "data/recommended_next_work.csv",
    "data/review_manifest.json",
    "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md",
    "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md",
    "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md",
    "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_LAG_MECHANISM_DE.md",
    "scripts/run_pbr_nullmodel_execution_result_review.py",
    "scripts/validate_pbr_nullmodel_execution_result_review.py",
    "sql/001_create_qsb_pbr_nullmodel_execution_result_review.sql",
    "sql/002_insert_qsb_pbr_nullmodel_execution_result_review.sql",
    "sql/003_validation_queries.sql",
    "validation/validation_results.csv",
]
FORBIDDEN = [
    "QSB is physically " + "validated",
    "PBR exists " + "physically",
    "The six lag axes are spacetime " + "dimensions",
    "Spacetime emergence is " + "proven",
    "Empirical validation " + "exists",
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
    idx = text.find(phrase)
    if idx < 0:
        return True
    window = text[max(0, idx - 120): idx + len(phrase) + 120].lower()
    return any(marker in window for marker in ["blocked", "gesperrt", "nicht freigegeben", "claim boundary", "prohibited", "not allowed"])


def validate_copy_blocks(sql_text: str) -> bool:
    lines = sql_text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("COPY "):
            match = re.search(r"\(([^)]+)\)", lines[i])
            if not match or i + 1 >= len(lines):
                return False
            cols = len([col.strip() for col in match.group(1).split(",")])
            if len(lines[i + 1].split("\t")) != cols:
                return False
            i += 2
            while i < len(lines) and lines[i] != r"\.":
                if len(lines[i].split("\t")) != cols:
                    return False
                i += 1
            if i >= len(lines):
                return False
        i += 1
    return True


def sql_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def update_validation_import_block(run_dir: Path, rows: List[Dict[str, str]]) -> None:
    sql_path = run_dir / "sql/002_insert_qsb_pbr_nullmodel_execution_result_review.sql"
    text = sql_path.read_text(encoding="utf-8")
    start = "-- BEGIN generated validation results import"
    end = "-- END generated validation results import"
    if start in text and end in text:
        text = text.split(start, 1)[0].rstrip() + "\n" + text.split(end, 1)[1].lstrip()
    fields = ["run_id", "check_name", "status", "detail"]
    block = [
        start,
        "COPY qsb_planck_bridge.pbr_nullmodel_execution_result_review_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');",
        "\t".join(fields),
    ]
    for row in rows:
        block.append("\t".join(sql_value(row[field]) for field in fields))
    block.extend([r"\.", end, ""])
    sql_path.write_text(text.replace("COMMIT;\n", "\n".join(block) + "COMMIT;\n"), encoding="utf-8")


def text_for_scan(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.name == "002_insert_qsb_pbr_nullmodel_execution_result_review.sql":
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

    summary = read_csv(run_dir / "data/nullmodel_execution_review_summary.csv")
    family = read_csv(run_dir / "data/nullmodel_family_review.csv")
    critical = read_csv(run_dir / "data/critical_nullmodel_findings.csv")
    specificity = read_csv(run_dir / "data/specificity_interpretation.csv")
    next_gate = read_csv(run_dir / "data/next_gate_decision.csv")
    lineage = read_csv(run_dir / "data/input_run_lineage.csv")
    claims = read_csv(run_dir / "data/claim_boundaries.csv")

    all_data = summary + family + critical + specificity + next_gate + lineage + claims
    add(rows, "run_id_consistency", all(row.get("run_id") == RUN_ID for row in all_data), RUN_ID)
    add(rows, "input_execution_run_referenced", any(row.get("source_run_id") == INPUT_RUN_ID for row in lineage), INPUT_RUN_ID)
    add(rows, "all_families_reviewed", {row.get("nullmodel_family") for row in family} == FAMILIES, ",".join(sorted({row.get("nullmodel_family") for row in family})))
    add(rows, "critical_nullmodel", critical[0].get("critical_nullmodel") == "lag_preserving_shuffle_null", critical[0].get("critical_nullmodel", "missing"))
    add(rows, "critical_reproduction_1000_of_1000", critical[0].get("complete_reproduction_count") == "1000" and critical[0].get("samples_total") == "1000", f"{critical[0].get('complete_reproduction_count')}/{critical[0].get('samples_total')}")
    add(rows, "specificity_no_specificity", specificity[0].get("specificity_classification") == "no_specificity", specificity[0].get("specificity_classification", "missing"))
    add(rows, "review_outcome", summary[0].get("review_outcome") == "no_specificity_confirmed_for_current_operationalization", summary[0].get("review_outcome", "missing"))
    add(rows, "physical_claim_release_blocked", all(row.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for row in summary + specificity + next_gate + claims), PHYSICAL_CLAIM_RELEASE)
    manifest = (run_dir / "data/review_manifest.json").read_text(encoding="utf-8")
    add(rows, "no_nullmodels_executed_in_review", '"nullmodels_executed_in_this_review_run": false' in manifest, "review manifest")
    add(rows, "next_gate", next_gate[0].get("next_gate") == "lag_mechanism_required", next_gate[0].get("next_gate", "missing"))
    add(rows, "secondary_next_gate", next_gate[0].get("secondary_next_gate") == "nullmodel_operationalization_review_required", next_gate[0].get("secondary_next_gate", "missing"))
    add(rows, "external_readiness_internal_only", summary[0].get("external_readiness") == "internal_only", summary[0].get("external_readiness", "missing"))

    scan_text = "\n".join(
        text_for_scan(path)
        for path in run_dir.rglob("*")
        if path.is_file()
        and path.relative_to(run_dir).as_posix() != "validation/validation_results.csv"
        and path.suffix in {".md", ".csv", ".json", ".sql", ".py"}
    )
    for phrase in FORBIDDEN:
        add(rows, f"forbidden_context:{phrase}", forbidden_context_ok(scan_text, phrase), phrase)

    sql_text = (run_dir / "sql/002_insert_qsb_pbr_nullmodel_execution_result_review.sql").read_text(encoding="utf-8")
    add(rows, "sql_copy_column_lists_match_rows", validate_copy_blocks(sql_text), "COPY TSV blocks")
    csv_files = list((run_dir / "data").glob("*.csv")) + list((run_dir / "validation").glob("*.csv"))
    add(rows, "csv_lf_line_endings", all(has_lf_only(path) for path in csv_files), f"{len(csv_files)} CSV files")
    generator = (run_dir / "scripts/run_pbr_nullmodel_execution_result_review.py").read_text(encoding="utf-8")
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
