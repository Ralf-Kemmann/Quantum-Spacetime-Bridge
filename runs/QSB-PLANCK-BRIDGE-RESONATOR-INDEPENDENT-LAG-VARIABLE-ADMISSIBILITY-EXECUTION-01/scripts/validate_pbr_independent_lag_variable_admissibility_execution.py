#!/usr/bin/env python3
"""Validate the PBR independent-lag-variable admissibility execution run."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01"
SCOUT_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01"
DESIGN_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
ALLOWED_OUTCOMES = {
    "admissibility_execution_completed",
    "admissibility_execution_completed_no_admissible_candidates",
    "admissibility_execution_completed_with_repair_required_candidates",
    "blocked_missing_input_run",
    "blocked_invalid_design_input",
    "blocked_invalid_scout_input",
}
ALLOWED_DECISIONS = {
    "candidate_admissible_for_lag_mechanism_testing",
    "candidate_admissible_only_after_lineage_repair",
    "candidate_admissible_only_after_metadata_repair",
    "candidate_rejected_alias_of_lag",
    "candidate_rejected_alias_of_pair_or_index",
    "candidate_rejected_not_pair_mappable",
    "candidate_rejected_not_independent",
    "candidate_requires_red_team_review",
}
ALLOWED_NEXT_GATES = {
    "lag_mechanism_testing_with_admissible_candidates_required",
    "lineage_repair_required",
    "metadata_repair_required",
    "red_team_candidate_review_required",
    "input_artifact_enrichment_required",
    "physical_proxy_source_review_required",
    "no_admissible_candidates_review_required",
}
FORBIDDEN_PHRASES = [
    "QSB is physically " + "validated",
    "PBR exists " + "physically",
    "six lag axes are " + "spacetime dimensions",
    "spacetime emergence is " + "proven",
    "empirical validation " + "exists",
    "lag classes are " + "physical dimensions",
    "lag mechanism is physically " + "proven",
    "candidate artifact proves " + "independent lag mechanism",
    "candidate artifact proves " + "physical proxy",
    "admissible candidate confirms " + "independent lag variable",
    "admissible candidate releases " + "physical claim",
    "DWH presence alone proves " + "independence",
    "repo presence alone proves " + "independence",
    "literature note alone proves " + "proxy for current matrix",
    "phase-response values are independent " + "lag variables despite alias assessment",
]
ALLOWED_CONTEXT = ["blocked", "prohibited", "claim_boundaries", "claim boundary", "no physical claims are released", PHYSICAL_CLAIM_RELEASE]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Iterable[Dict[str, str]]) -> None:
    fields = ["run_id", "check_name", "status", "detail"]
    rows = list(rows)
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
    result: Dict[str, List[str]] = {}
    pattern = re.compile(r"COPY\s+qsb_planck_bridge\.([a-z0-9_]+)\s+\(([^)]*)\)\s+FROM stdin", re.IGNORECASE)
    for match in pattern.finditer(sql_text):
        result[match.group(1)] = [col.strip() for col in match.group(2).split(",")]
    return result


def main() -> int:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"runs/{RUN_ID}")
    run_dir = run_dir.resolve()
    repo_root = Path.cwd().resolve()
    rows: List[Dict[str, str]] = []
    add(rows, "run_directory_exact", run_dir == repo_root / "runs" / RUN_ID, str(run_dir))
    required_files = [
        "README.md", f"{RUN_ID}.md", "RUN_COMMANDS_PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION01.md",
        "data/execution_summary.csv", "data/input_lineage.csv", "data/candidate_admissibility_results.csv",
        "data/candidate_criteria_results.csv", "data/candidate_alias_flags.csv", "data/deterministic_alias_check.csv",
        "data/scramble_invariance_feasibility.csv", "data/source_lineage_audit.csv", "data/pair_mapping_audit.csv",
        "data/information_gain_feasibility.csv", "data/directionality_consistency_audit.csv", "data/unit_dimension_metadata_audit.csv",
        "data/admissibility_decision_summary.csv", "data/category_summary.csv", "data/rejected_candidate_summary.csv",
        "data/repair_required_candidate_summary.csv", "data/red_team_candidate_summary.csv", "data/claim_boundaries.csv",
        "data/next_gate_decision.csv", "data/execution_manifest.json",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_SUMMARY_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULTS_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_ALIAS_FINDINGS_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_REPAIR_NEEDS_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RED_TEAM_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_NEXT_GATE_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_CLAIM_BOUNDARY_DE.md",
        "scripts/run_pbr_independent_lag_variable_admissibility_execution.py",
        "scripts/validate_pbr_independent_lag_variable_admissibility_execution.py",
        "sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution.sql",
        "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution.sql",
        "sql/003_validation_queries.sql", "validation/validation_results.csv",
    ]
    missing = [rel for rel in required_files if not (run_dir / rel).exists()]
    add(rows, "required_files_exist", not missing, "|".join(missing) or "all_required_files_present")
    lf_bad = [rel for rel in required_files if (run_dir / rel).exists() and not ensure_lf_utf8(run_dir / rel)]
    add(rows, "utf8_lf_files", not lf_bad, "|".join(lf_bad) or "all_required_text_files_utf8_lf")

    summary = read_csv(run_dir / "data/execution_summary.csv")
    s = summary[0] if summary else {}
    add(rows, "run_id_exact", s.get("run_id") == RUN_ID, s.get("run_id", "missing"))
    add(rows, "run_type", s.get("run_type") == "independent_lag_variable_admissibility_execution", s.get("run_type", "missing"))
    add(rows, "execution_status_allowed", s.get("execution_status") in ALLOWED_OUTCOMES, s.get("execution_status", "missing"))
    add(rows, "physical_claim_release_blocked", s.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE, s.get("physical_claim_release", "missing"))
    add(rows, "input_runs_referenced", s.get("input_scout_run_id") == SCOUT_RUN_ID and s.get("input_design_run_id") == DESIGN_RUN_ID, f"{s.get('input_scout_run_id')}|{s.get('input_design_run_id')}")
    add(rows, "next_gate_allowed", s.get("next_gate") in ALLOWED_NEXT_GATES, s.get("next_gate", "missing"))
    add(rows, "no_lag_mechanism_tests_or_nullmodels", s.get("no_lag_mechanism_tests_executed") == "true" and s.get("no_nullmodels_executed") == "true", f"lag={s.get('no_lag_mechanism_tests_executed')} null={s.get('no_nullmodels_executed')}")

    results = read_csv(run_dir / "data/candidate_admissibility_results.csv")
    add(rows, "candidate_results_exist", len(results) > 0, f"candidate_rows={len(results)}")
    decisions = Counter(r.get("admissibility_decision_class", "") for r in results)
    add(rows, "all_decision_classes_allowed", set(decisions).issubset(ALLOWED_DECISIONS), "|".join(sorted(set(decisions) - ALLOWED_DECISIONS)) or "all_allowed")
    bad_confirm = [r.get("candidate_id", "") for r in results if "confirmed" in r.get("claim_implication", "").lower() or r.get("physical_claim_release") != PHYSICAL_CLAIM_RELEASE]
    add(rows, "no_candidate_confirmed_independent_or_physical_proxy", not bad_confirm, "|".join(bad_confirm) or "no_confirming_rows")
    admissible_bad = [r.get("candidate_id", "") for r in results if r.get("admissibility_decision_class") == "candidate_admissible_for_lag_mechanism_testing" and "testing_only" not in r.get("claim_implication", "")]
    add(rows, "admissible_candidates_testing_only", not admissible_bad, "|".join(admissible_bad) or "all_admissible_testing_only")
    presence_bad = [r.get("candidate_id", "") for r in results if "presence" in r.get("claim_implication", "").lower() and "proof" in r.get("claim_implication", "").lower()]
    add(rows, "presence_alone_not_independence_proof", not presence_bad, "|".join(presence_bad) or "no_presence_as_proof")

    alias = read_csv(run_dir / "data/candidate_alias_flags.csv")
    phase_source_present = any("phase" in r.get("candidate_variable_name", "").lower() or "phase" in r.get("source_path_or_table", "").lower() for r in results)
    phase_rule_rows = [r for r in alias if r.get("alias_flag") == "phase_response_abs_lag_alias" and r.get("alias_flag_status") == "triggered"]
    add(rows, "phase_response_special_rule_applied_if_present", (not phase_source_present) or bool(phase_rule_rows) or any("delta_phi" in r.get("candidate_variable_name", "") for r in results), f"phase_flag_triggered={len(phase_rule_rows)}")

    summary_count_ok = (
        int(s.get("candidate_count_total", "-1")) == len(results)
        and int(s.get("candidate_count_admissible_for_testing", "-1")) == decisions["candidate_admissible_for_lag_mechanism_testing"]
        and int(s.get("candidate_count_lineage_repair", "-1")) == decisions["candidate_admissible_only_after_lineage_repair"]
        and int(s.get("candidate_count_metadata_repair", "-1")) == decisions["candidate_admissible_only_after_metadata_repair"]
        and int(s.get("candidate_count_rejected_alias_lag", "-1")) == decisions["candidate_rejected_alias_of_lag"]
        and int(s.get("candidate_count_rejected_alias_pair_or_index", "-1")) == decisions["candidate_rejected_alias_of_pair_or_index"]
        and int(s.get("candidate_count_rejected_not_pair_mappable", "-1")) == decisions["candidate_rejected_not_pair_mappable"]
        and int(s.get("candidate_count_rejected_not_independent", "-1")) == decisions["candidate_rejected_not_independent"]
        and int(s.get("candidate_count_red_team_review", "-1")) == decisions["candidate_requires_red_team_review"]
    )
    add(rows, "summary_counts_match_results", summary_count_ok, "summary_vs_candidate_rows")
    categories = read_csv(run_dir / "data/category_summary.csv")
    cat_total_ok = sum(int(r.get("count_total", "0")) for r in categories) == len(results)
    add(rows, "category_summary_matches_results", cat_total_ok, f"category_total={sum(int(r.get('count_total', '0')) for r in categories)}")
    rejected = read_csv(run_dir / "data/rejected_candidate_summary.csv")
    repair = read_csv(run_dir / "data/repair_required_candidate_summary.csv")
    red = read_csv(run_dir / "data/red_team_candidate_summary.csv")
    add(rows, "subset_summaries_consistent", len(rejected) == sum(decisions[d] for d in decisions if d.startswith("candidate_rejected")) and len(repair) == decisions["candidate_admissible_only_after_lineage_repair"] + decisions["candidate_admissible_only_after_metadata_repair"] and len(red) == decisions["candidate_requires_red_team_review"], f"rejected={len(rejected)} repair={len(repair)} red={len(red)}")

    manifest = json.loads((run_dir / "data/execution_manifest.json").read_text(encoding="utf-8"))
    add(rows, "manifest_flags", manifest.get("no_lag_mechanism_tests_executed") is True and manifest.get("no_nullmodels_executed") is True and manifest.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE, "manifest_checked")
    claims = read_csv(run_dir / "data/claim_boundaries.csv")
    add(rows, "claim_boundaries_blocked", claims and all(r.get("status") == "blocked" and r.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for r in claims), f"claim_rows={len(claims)}")

    create_sql = (run_dir / "sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution.sql").read_text(encoding="utf-8")
    insert_sql = (run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution.sql").read_text(encoding="utf-8")
    add(rows, "german_view_created", "v_pbr_unabhaengige_lag_variable_zulassung_de" in create_sql, "view_name_present")
    expected_tables = {"pbr_independent_lag_variable_admissibility_summary", "pbr_independent_lag_variable_admissibility_results", "pbr_independent_lag_variable_admissibility_alias_flags", "pbr_independent_lag_variable_admissibility_next_gate"}
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
    pre_existing = manifest.get("pre_existing_modified_files", [])
    add(rows, "no_files_outside_run_package_modified", not outside or bool(pre_existing), "|".join(outside) or "no_outside_changes")
    add(rows, "pre_existing_modifications_recorded", (not outside) or bool(pre_existing), "|".join(pre_existing) if isinstance(pre_existing, list) else str(pre_existing))
    add(rows, "git_diff_check_passes", git_diff_check(repo_root), "git diff --check")

    validation_path = run_dir / "validation/validation_results.csv"
    write_csv(validation_path, rows)
    block_lines = [
        "-- BEGIN generated validation results import",
        f"DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_validation WHERE run_id = '{RUN_ID}';",
        "COPY qsb_planck_bridge.pbr_independent_lag_variable_admissibility_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');",
        "run_id\tcheck_name\tstatus\tdetail",
    ]
    for row in rows:
        block_lines.append("\t".join(row[field].replace("\t", " ").replace("\n", " ") for field in ["run_id", "check_name", "status", "detail"]))
    block_lines.extend([r"\.", "-- END generated validation results import"])
    block = "\n".join(block_lines)
    marker = "-- BEGIN generated validation results import"
    if marker in insert_sql:
        insert_sql = insert_sql.split(marker, 1)[0].rstrip() + "\n" + block + "\nCOMMIT;\n"
    else:
        insert_sql = insert_sql.replace("\nCOMMIT;\n", "\n" + block + "\nCOMMIT;\n")
    (run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution.sql").write_text(insert_sql, encoding="utf-8")

    failed = [row for row in rows if row["status"] != "PASS"]
    print(f"target_run_id={RUN_ID}")
    print(f"validation_checks={len(rows)}")
    print(f"validation_failed={len(failed)}")
    for row in failed:
        print(f"FAIL {row['check_name']}: {row['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
