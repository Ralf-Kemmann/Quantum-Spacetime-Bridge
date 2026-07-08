#!/usr/bin/env python3
"""Validate the PBR nullmodel execution run package."""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
FAMILIES = {
    "label_permutation_null",
    "lag_preserving_shuffle_null",
    "random_gram_psd_null",
    "directed_pair_rewire_null",
    "sign_flip_antiparallel_null",
}
CLASSIFICATIONS = {"strong_formal_specificity", "moderate_formal_specificity", "weak_specificity", "no_specificity"}
REQUIRED_FILES = [
    "README.md",
    f"{RUN_ID}.md",
    "RUN_COMMANDS_PBR_NULLMODEL_EXECUTION01.md",
    "data/nullmodel_execution_summary.csv",
    "data/nullmodel_sample_results.csv",
    "data/nullmodel_family_summary.csv",
    "data/spectral_core_metrics.csv",
    "data/lag_class_metrics.csv",
    "data/nullmodel_comparison_metrics.csv",
    "data/specificity_classification.csv",
    "data/claim_boundaries.csv",
    "data/input_run_lineage.csv",
    "data/nullmodel_execution_manifest.json",
    "docs/PBR_NULLMODEL_EXECUTION_SUMMARY_DE.md",
    "docs/PBR_NULLMODEL_EXECUTION_METRICS_DE.md",
    "docs/PBR_NULLMODEL_EXECUTION_CLAIM_BOUNDARY_DE.md",
    "docs/PBR_NULLMODEL_EXECUTION_NEXT_GATE_DE.md",
    "scripts/run_pbr_nullmodel_execution.py",
    "scripts/validate_pbr_nullmodel_execution.py",
    "sql/001_create_qsb_pbr_nullmodel_execution.sql",
    "sql/002_insert_qsb_pbr_nullmodel_execution.sql",
    "sql/003_validation_queries.sql",
    "validation/validation_results.csv",
]
FORBIDDEN_AFFIRMATIVE = [
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
    markers = ["blocked", "gesperrt", "prohibited", "not allowed", "claim boundary", "affirmative aussage gesperrt"]
    return any(marker in window for marker in markers)


def validate_copy_blocks(sql_text: str) -> bool:
    lines = sql_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("COPY "):
            match = re.search(r"\(([^)]+)\)", line)
            if not match or i + 1 >= len(lines):
                return False
            column_count = len([col.strip() for col in match.group(1).split(",")])
            header_count = len(lines[i + 1].split("\t"))
            if column_count != header_count:
                return False
            i += 2
            while i < len(lines) and lines[i] != r"\.":
                if len(lines[i].split("\t")) != column_count:
                    return False
                i += 1
            if i >= len(lines):
                return False
        i += 1
    return True


def sql_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def update_validation_import_block(run_dir: Path, rows: List[Dict[str, str]]) -> None:
    sql_path = run_dir / "sql/002_insert_qsb_pbr_nullmodel_execution.sql"
    text = sql_path.read_text(encoding="utf-8")
    start_marker = "-- BEGIN generated validation results import"
    end_marker = "-- END generated validation results import"
    if start_marker in text and end_marker in text:
        before = text.split(start_marker, 1)[0].rstrip()
        after = text.split(end_marker, 1)[1].lstrip()
        text = before + "\n" + after
    fields = ["run_id", "check_name", "status", "detail"]
    block = [
        start_marker,
        "COPY qsb_planck_bridge.pbr_nullmodel_execution_validation_results (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');",
        "\t".join(fields),
    ]
    for row in rows:
        block.append("\t".join(sql_value(row[field]) for field in fields))
    block.extend([r"\.", end_marker, ""])
    text = text.replace("COMMIT;\n", "\n".join(block) + "COMMIT;\n")
    sql_path.write_text(text, encoding="utf-8")


def text_for_claim_scan(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.name == "002_insert_qsb_pbr_nullmodel_execution.sql":
        start_marker = "-- BEGIN generated validation results import"
        end_marker = "-- END generated validation results import"
        if start_marker in text and end_marker in text:
            before = text.split(start_marker, 1)[0]
            after = text.split(end_marker, 1)[1]
            return before + after
    return text


def main() -> int:
    run_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(f"runs/{RUN_ID}").resolve()
    repo_root = run_dir.parents[1]
    results: List[Dict[str, str]] = []

    for rel in REQUIRED_FILES:
        add(results, f"exists:{rel}", (run_dir / rel).exists(), rel)

    if not all((run_dir / rel).exists() for rel in REQUIRED_FILES):
        write_csv(run_dir / "validation/validation_results.csv", results)
        return 1

    summary = read_csv(run_dir / "data/nullmodel_execution_summary.csv")
    samples = read_csv(run_dir / "data/nullmodel_sample_results.csv")
    spectral = read_csv(run_dir / "data/spectral_core_metrics.csv")
    lag = read_csv(run_dir / "data/lag_class_metrics.csv")
    comparison = read_csv(run_dir / "data/nullmodel_comparison_metrics.csv")
    classification = read_csv(run_dir / "data/specificity_classification.csv")
    lineage = read_csv(run_dir / "data/input_run_lineage.csv")
    claims = read_csv(run_dir / "data/claim_boundaries.csv")

    add(results, "run_id_consistency", all(row.get("run_id") == RUN_ID for rows in [summary, samples, spectral, lag, comparison, classification, lineage, claims] for row in rows), RUN_ID)
    add(results, "previous_run_lineage_exists", any(row.get("source_run_id") == "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01" for row in lineage), "design lineage")
    found_families = {row.get("nullmodel_family") for row in samples}
    add(results, "all_families_present", found_families == FAMILIES, ",".join(sorted(found_families)))
    family_counts = {family: sum(1 for row in samples if row.get("nullmodel_family") == family) for family in FAMILIES}
    add(results, "samples_exist_all_families", all(count > 0 for count in family_counts.values()), str(family_counts))
    add(results, "sample_count_documented", bool(summary and summary[0].get("samples_per_family")), summary[0].get("samples_per_family", "missing") if summary else "missing")
    add(results, "no_missing_seed", all(row.get("seed") for row in samples), "seed column")
    add(results, "spectral_core_metrics_present", len(spectral) == len(samples), f"{len(spectral)} spectral rows")
    add(results, "lag_class_metrics_present", len(lag) == len(samples), f"{len(lag)} lag rows")
    add(results, "comparison_metrics_present", {row.get("nullmodel_family") for row in comparison} == FAMILIES, f"{len(comparison)} comparison rows")
    class_values = [row.get("specificity_classification") for row in classification]
    add(results, "exactly_one_final_classification", len(class_values) == 1 and class_values[0] in CLASSIFICATIONS, ",".join(class_values))
    add(results, "physical_claim_release_blocked", all(row.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for row in classification + claims), PHYSICAL_CLAIM_RELEASE)

    text = "\n".join(
        text_for_claim_scan(path)
        for path in run_dir.rglob("*")
        if path.is_file()
        and path.relative_to(run_dir).as_posix() != "validation/validation_results.csv"
        and path.suffix in {".md", ".csv", ".json", ".sql", ".py"}
    )
    for phrase in FORBIDDEN_AFFIRMATIVE:
        add(results, f"forbidden_context:{phrase}", forbidden_context_ok(text, phrase), phrase)
    add(results, "no_physical_claim_release", PHYSICAL_CLAIM_RELEASE in text and "physical_claim_release=blocked_no_physics_claim" in text, PHYSICAL_CLAIM_RELEASE)

    sql_insert = (run_dir / "sql/002_insert_qsb_pbr_nullmodel_execution.sql").read_text(encoding="utf-8")
    add(results, "sql_copy_column_lists_match_rows", validate_copy_blocks(sql_insert), "COPY TSV blocks")
    csv_files = list((run_dir / "data").glob("*.csv")) + list((run_dir / "validation").glob("*.csv"))
    add(results, "csv_lf_line_endings", all(has_lf_only(path) for path in csv_files), f"{len(csv_files)} CSV files")
    run_script = (run_dir / "scripts/run_pbr_nullmodel_execution.py").read_text(encoding="utf-8")
    add(results, "csv_lineterminator_declared", 'lineterminator="\\n"' in run_script, "csv.DictWriter lineterminator")
    text_files = [path for path in run_dir.rglob("*") if path.is_file()]
    add(results, "utf8_text_files_readable", all(path.read_text(encoding="utf-8") is not None for path in text_files), f"{len(text_files)} files")

    diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, text=True, capture_output=True)
    add(results, "git_diff_check", diff.returncode == 0, diff.stdout.strip() or diff.stderr.strip() or "ok")
    status = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=repo_root, text=True, capture_output=True)
    outside = []
    prefix = f"runs/{RUN_ID}/"
    for line in status.stdout.splitlines():
        path = line[3:] if len(line) > 3 else line
        if path and not path.startswith(prefix):
            outside.append(line)
    add(results, "no_files_outside_run_package_modified", not outside, "\n".join(outside) if outside else "ok")

    write_csv(run_dir / "validation/validation_results.csv", results)
    update_validation_import_block(run_dir, results)
    ok = all(row["status"] == "pass" for row in results)
    print(f"validation_status={'pass' if ok else 'fail'}")
    print(f"checks={len(results)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
