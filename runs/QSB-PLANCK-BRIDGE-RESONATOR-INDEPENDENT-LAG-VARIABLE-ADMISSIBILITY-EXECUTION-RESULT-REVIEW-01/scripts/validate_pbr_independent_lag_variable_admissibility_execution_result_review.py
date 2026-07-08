#!/usr/bin/env python3
"""Validate the PBR admissibility execution result-review package."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01"
SOURCE_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
FORBIDDEN_PHRASES = [
    "QSB is physically " + "validated",
    "PBR exists " + "physically",
    "six lag axes are " + "spacetime dimensions",
    "spacetime emergence is " + "proven",
    "empirical validation " + "exists",
    "lag classes are " + "physical dimensions",
    "lag mechanism is physically " + "proven",
    "admissibility execution proves " + "independent lag variable",
    "admissibility execution proves " + "physical proxy",
    "0 admissible candidates disproves " + "QSB",
    "0 admissible candidates proves " + "pure index construction",
    "repair candidate proves " + "mechanism",
    "Deep Research can replace " + "internal lineage",
    "DWH presence alone proves " + "independence",
    "repo presence alone proves " + "independence",
    "literature note alone proves " + "proxy for current matrix",
]
ALLOWED_CONTEXT = ["blocked", "prohibited", "claim_boundaries", "claim boundary", PHYSICAL_CLAIM_RELEASE]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Iterable[Dict[str, str]]) -> None:
    rows = list(rows)
    fields = ["run_id", "check_name", "status", "detail"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add(rows: List[Dict[str, str]], name: str, ok: bool, detail: str) -> None:
    rows.append({"run_id": RUN_ID, "check_name": name, "status": "PASS" if ok else "FAIL", "detail": detail})


def ensure_lf_utf8(path: Path) -> bool:
    try:
        raw = path.read_bytes()
        raw.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return b"\r" not in raw


def git_status(repo_root: Path) -> List[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=repo_root, text=True, capture_output=True)
    return proc.stdout.splitlines()


def git_diff_check(repo_root: Path) -> bool:
    proc = subprocess.run(["git", "diff", "--check"], cwd=repo_root, text=True, capture_output=True)
    return proc.returncode == 0


def status_path(line: str) -> str:
    return line[3:] if len(line) > 3 else line


def copy_table_columns(sql_text: str) -> Dict[str, List[str]]:
    pattern = re.compile(r"COPY\s+qsb_planck_bridge\.([a-z0-9_]+)\s+\(([^)]*)\)\s+FROM stdin", re.IGNORECASE)
    return {m.group(1): [c.strip() for c in m.group(2).split(",")] for m in pattern.finditer(sql_text)}


def main() -> int:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"runs/{RUN_ID}")
    run_dir = run_dir.resolve()
    repo_root = Path.cwd().resolve()
    rows: List[Dict[str, str]] = []
    required = [
        "README.md", f"{RUN_ID}.md", "RUN_COMMANDS_PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW01.md",
        "data/review_summary.csv", "data/input_run_lineage.csv", "data/admissibility_result_review.csv",
        "data/blocker_analysis.csv", "data/repair_candidate_review.csv", "data/not_pair_mappable_review.csv",
        "data/claim_boundaries.csv", "data/deep_research_boundary.csv", "data/next_gate_decision.csv",
        "data/recommended_next_work.csv", "data/review_manifest.json",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_BLOCKERS_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_REPAIR_CANDIDATES_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_DEEP_RESEARCH_BOUNDARY_DE.md",
        "scripts/run_pbr_independent_lag_variable_admissibility_execution_result_review.py",
        "scripts/validate_pbr_independent_lag_variable_admissibility_execution_result_review.py",
        "sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql",
        "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql",
        "sql/003_validation_queries.sql",
        "validation/validation_results.csv",
    ]
    add(rows, "run_directory_exact", run_dir == repo_root / "runs" / RUN_ID, str(run_dir))
    missing = [rel for rel in required if not (run_dir / rel).exists()]
    add(rows, "required_files_exist", not missing, "|".join(missing) or "all_required_files_present")
    lf_bad = [rel for rel in required if (run_dir / rel).exists() and not ensure_lf_utf8(run_dir / rel)]
    add(rows, "utf8_lf_files", not lf_bad, "|".join(lf_bad) or "all_required_text_files_utf8_lf")

    summary = read_csv(run_dir / "data/review_summary.csv")[0]
    source_summary = read_csv(repo_root / "runs" / SOURCE_RUN_ID / "data/execution_summary.csv")[0]
    add(rows, "run_id_exact", summary.get("run_id") == RUN_ID, summary.get("run_id", "missing"))
    add(rows, "run_type", summary.get("run_type") == "independent_lag_variable_admissibility_execution_result_review", summary.get("run_type", "missing"))
    add(rows, "source_run_referenced", summary.get("source_run_id") == SOURCE_RUN_ID, summary.get("source_run_id", "missing"))
    add(rows, "review_outcome_allowed", summary.get("review_outcome") in {"admissibility_execution_review_completed", "blocked_missing_input_run"}, summary.get("review_outcome", "missing"))
    add(rows, "confirmed_execution_status_recorded", summary.get("confirmed_execution_status") == source_summary.get("execution_status"), summary.get("confirmed_execution_status", "missing"))
    add(rows, "candidate_count_admissible_zero_if_source_zero", summary.get("candidate_count_admissible_for_testing") == source_summary.get("candidate_count_admissible_for_testing"), f"review={summary.get('candidate_count_admissible_for_testing')} source={source_summary.get('candidate_count_admissible_for_testing')}")
    add(rows, "dominant_blocker_not_pair_mappable", summary.get("dominant_blocker") == "not_pair_mappable" and summary.get("dominant_blocker_count") == source_summary.get("candidate_count_rejected_not_pair_mappable"), f"{summary.get('dominant_blocker')}:{summary.get('dominant_blocker_count')}")
    add(rows, "next_gates_exact", summary.get("next_gate") == "lineage_repair_required" and summary.get("secondary_next_gate") == "physical_proxy_source_review_required" and summary.get("tertiary_next_gate") == "deep_research_method_criteria_review_pending", f"{summary.get('next_gate')}|{summary.get('secondary_next_gate')}|{summary.get('tertiary_next_gate')}")
    add(rows, "physical_claim_release_blocked", summary.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE, summary.get("physical_claim_release", "missing"))

    deep = read_csv(run_dir / "data/deep_research_boundary.csv")[0]
    add(rows, "deep_research_boundary_recorded", deep.get("deep_research_status") == "pending_or_parallel" and deep.get("deep_research_cannot_replace_internal_lineage") == "true", json.dumps(deep, ensure_ascii=False))
    manifest = json.loads((run_dir / "data/review_manifest.json").read_text(encoding="utf-8"))
    add(rows, "no_execution_tests_in_review", manifest.get("no_admissibility_checks_executed_in_review_run") is True and manifest.get("no_lag_mechanism_tests_executed") is True and manifest.get("no_nullmodels_executed") is True, "manifest_execution_flags")
    repairs = read_csv(run_dir / "data/repair_candidate_review.csv")
    add(rows, "repair_candidate_count_matches_source", len(repairs) == int(source_summary.get("candidate_count_lineage_repair", "0")) + int(source_summary.get("candidate_count_metadata_repair", "0")), f"repair_rows={len(repairs)}")
    blocker_keys = {r.get("blocker_key") for r in read_csv(run_dir / "data/blocker_analysis.csv")}
    add(rows, "required_blockers_present", {"not_pair_mappable", "lineage_incomplete", "metadata_incomplete", "no_admissible_candidate"}.issubset(blocker_keys), "|".join(sorted(blocker_keys)))
    claims = read_csv(run_dir / "data/claim_boundaries.csv")
    add(rows, "claim_boundaries_blocked", claims and all(r.get("status") == "blocked" and r.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for r in claims), f"claim_rows={len(claims)}")
    rec = read_csv(run_dir / "data/recommended_next_work.csv")
    add(rows, "primary_next_work_recorded", any(r.get("recommended_run_id") == "QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-DESIGN-01" and r.get("priority") == "primary" for r in rec), f"rows={len(rec)}")

    create_sql = (run_dir / "sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql").read_text(encoding="utf-8")
    insert_sql = (run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql").read_text(encoding="utf-8")
    add(rows, "german_view_created", "v_pbr_unabhaengige_lag_variable_zulassung_review_de" in create_sql, "view_name_present")
    expected_tables = {"pbr_independent_lag_variable_admissibility_result_review_summary", "pbr_independent_lag_variable_admissibility_result_review_next_gate", "pbr_independent_lag_variable_admissibility_result_review_validation"}
    copy_tables = set(copy_table_columns(insert_sql))
    add(rows, "sql_copy_tables_present", expected_tables.issubset(copy_tables), "|".join(sorted(expected_tables - copy_tables)) or "required_copy_tables_present")

    forbidden_hits = []
    for path in run_dir.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".csv", ".sql", ".json", ".py"}:
            rel_path = path.relative_to(repo_root)
            if rel_path.as_posix().endswith("validation/validation_results.csv"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix == ".sql" and "-- BEGIN generated validation results import" in text:
                prefix, rest = text.split("-- BEGIN generated validation results import", 1)
                suffix = rest.split("-- END generated validation results import", 1)[1] if "-- END generated validation results import" in rest else ""
                text = prefix + suffix
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    idx = text.index(phrase)
                    context = text[max(0, idx - 120):idx + len(phrase) + 120].lower()
                    if not any(marker in context for marker in ALLOWED_CONTEXT):
                        forbidden_hits.append(f"{rel_path}:{phrase}")
    add(rows, "forbidden_phrases_only_blocked_context", not forbidden_hits, "|".join(forbidden_hits) or "no_unblocked_forbidden_phrase_hits")

    status = git_status(repo_root)
    outside = [line for line in status if not status_path(line).startswith(f"runs/{RUN_ID}/")]
    add(rows, "no_files_outside_run_package_modified", not outside or bool(manifest.get("pre_existing_modified_files")), "|".join(outside) or "no_outside_changes")
    add(rows, "git_diff_check_passes", git_diff_check(repo_root), "git diff --check")

    validation_path = run_dir / "validation/validation_results.csv"
    write_csv(validation_path, rows)
    block_lines = [
        "-- BEGIN generated validation results import",
        f"DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_validation WHERE run_id = '{RUN_ID}';",
        "COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');",
        "run_id\tcheck_name\tstatus\tdetail",
    ]
    for row in rows:
        block_lines.append("\t".join(row[field].replace("\t", " ").replace("\n", " ") for field in ["run_id", "check_name", "status", "detail"]))
    block_lines.extend([r"\.", "-- END generated validation results import"])
    block = "\n".join(block_lines)
    if "-- BEGIN generated validation results import" in insert_sql:
        insert_sql = insert_sql.split("-- BEGIN generated validation results import", 1)[0].rstrip() + "\n" + block + "\nCOMMIT;\n"
    else:
        insert_sql = insert_sql.replace("\nCOMMIT;\n", "\n" + block + "\nCOMMIT;\n")
    (run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql").write_text(insert_sql, encoding="utf-8")

    failed = [row for row in rows if row["status"] != "PASS"]
    print(f"target_run_id={RUN_ID}")
    print(f"validation_checks={len(rows)}")
    print(f"validation_failed={len(failed)}")
    for row in failed:
        print(f"FAIL {row['check_name']}: {row['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
