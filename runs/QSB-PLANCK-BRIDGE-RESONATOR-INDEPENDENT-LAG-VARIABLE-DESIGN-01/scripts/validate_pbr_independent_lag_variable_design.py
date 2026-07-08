#!/usr/bin/env python3
"""Validate the PBR independent-lag-variable design-only run package."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01"
SCOUT_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
REQUIRED_CLASSES = {
    "admissible_independent_lag_variable_candidate",
    "formal_independent_variable_candidate_requires_execution",
    "physical_proxy_candidate_requires_source_review",
    "alias_of_abs_lag_or_lag",
    "alias_of_pair_id_or_index_order",
    "lineage_incomplete_requires_repair",
    "not_pair_mappable",
    "unit_or_dimension_missing_requires_metadata",
    "excluded_not_relevant",
    "unknown_requires_review",
}
REQUIRED_ALIAS_FLAGS = {
    "exact_lag_alias",
    "absolute_lag_alias",
    "pair_id_lookup_alias",
    "index_order_alias",
    "monotonic_lag_surrogate",
    "piecewise_lag_surrogate",
    "symmetry_only_alias",
    "phase_response_abs_lag_alias",
    "unknown_alias_risk",
}
REQUIRED_TESTS = {
    "deterministic_alias_test",
    "scramble_invariance_test",
    "source_lineage_audit",
    "pair_mapping_audit",
    "information_gain_over_lag_test",
    "directionality_consistency_test",
    "unit_dimension_metadata_audit",
    "candidate_admissibility_gate",
}
REQUIRED_DECISIONS = {
    "candidate_admissible_for_lag_mechanism_testing",
    "candidate_admissible_only_after_lineage_repair",
    "candidate_admissible_only_after_metadata_repair",
    "candidate_rejected_alias_of_lag",
    "candidate_rejected_alias_of_pair_or_index",
    "candidate_rejected_not_pair_mappable",
    "candidate_rejected_not_independent",
    "candidate_requires_red_team_review",
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
    "DWH presence alone proves " + "independence",
    "repo presence alone proves " + "independence",
    "literature note alone proves " + "proxy for current matrix",
    "criteria definition confirms " + "independence",
    "admissible candidate class releases " + "physical claim",
]
ALLOWED_CONTEXT = ["blocked", "prohibited", "claim_boundaries", "claim boundary", "no physical claims are released", PHYSICAL_CLAIM_RELEASE]


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
        "README.md",
        f"{RUN_ID}.md",
        "RUN_COMMANDS_PBR_INDEPENDENT_LAG_VARIABLE_DESIGN01.md",
        "data/design_summary.csv",
        "data/input_scout_lineage.csv",
        "data/independence_criteria.csv",
        "data/alias_detection_rules.csv",
        "data/candidate_classification_schema.csv",
        "data/test_design_spec.csv",
        "data/later_execution_decision_logic.csv",
        "data/source_lineage_requirements.csv",
        "data/pair_mapping_requirements.csv",
        "data/unit_dimension_requirements.csv",
        "data/phase_response_special_rule.csv",
        "data/deep_research_handoff_questions.csv",
        "data/claim_boundaries.csv",
        "data/next_gate_decision.csv",
        "data/design_manifest.json",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_SUMMARY_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_CRITERIA_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_ALIAS_RULES_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_TESTS_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_NEXT_GATE_DE.md",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_CLAIM_BOUNDARY_DE.md",
        "scripts/run_pbr_independent_lag_variable_design.py",
        "scripts/validate_pbr_independent_lag_variable_design.py",
        "sql/001_create_qsb_pbr_independent_lag_variable_design.sql",
        "sql/002_insert_qsb_pbr_independent_lag_variable_design.sql",
        "sql/003_validation_queries.sql",
        "validation/validation_results.csv",
    ]
    missing = [rel for rel in required_files if not (run_dir / rel).exists()]
    add(rows, "required_files_exist", not missing, "|".join(missing) or "all_required_files_present")
    lf_bad = [rel for rel in required_files if (run_dir / rel).exists() and not ensure_lf_utf8(run_dir / rel)]
    add(rows, "utf8_lf_text_files", not lf_bad, "|".join(lf_bad) or "all_required_text_files_utf8_lf")

    summary = read_csv(run_dir / "data/design_summary.csv")
    s = summary[0] if summary else {}
    add(rows, "run_id_exact", s.get("run_id") == RUN_ID, s.get("run_id", "missing"))
    add(rows, "run_type", s.get("run_type") == "independent_lag_variable_design", s.get("run_type", "missing"))
    add(rows, "execution_status_design_only", s.get("execution_status") == "design_only_not_executed", s.get("execution_status", "missing"))
    add(rows, "physical_claim_release_blocked", s.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE, s.get("physical_claim_release", "missing"))
    add(rows, "input_scout_referenced_or_blocked", s.get("input_scout_run_id") == SCOUT_RUN_ID and s.get("input_scout_status") in {"available", "missing"}, s.get("input_scout_status", "missing"))
    add(rows, "next_gate_design_completed", s.get("design_status") != "independent_lag_variable_design_completed_execution_required" or s.get("next_gate") == "independent_lag_variable_admissibility_execution_required", s.get("next_gate", "missing"))

    criteria = read_csv(run_dir / "data/independence_criteria.csv")
    add(rows, "all_required_independence_criteria_present", len(criteria) >= 8 and {r.get("criterion_key") for r in criteria} >= {f"C0{i}_{suffix}" for i, suffix in []}, f"criterion_rows={len(criteria)}")
    add(rows, "criteria_definition_no_confirmation", all("confirm" not in r.get("claim_implication", "").lower() for r in criteria), "criteria_claim_implications_checked")

    alias = read_csv(run_dir / "data/alias_detection_rules.csv")
    aliases = {r.get("flag_key", "") for r in alias}
    add(rows, "all_required_alias_flags_present", aliases == REQUIRED_ALIAS_FLAGS, "|".join(sorted(REQUIRED_ALIAS_FLAGS - aliases)) or "all_alias_flags_present")
    add(rows, "phase_response_special_alias_rule_present", any(r.get("flag_key") == "phase_response_abs_lag_alias" for r in alias), "phase_response_abs_lag_alias")

    classes = read_csv(run_dir / "data/candidate_classification_schema.csv")
    class_set = {r.get("candidate_class", "") for r in classes}
    add(rows, "all_required_candidate_classes_present", class_set == REQUIRED_CLASSES, "|".join(sorted(REQUIRED_CLASSES - class_set)) or "all_classes_present")
    bad_class_claims = [r.get("candidate_class", "") for r in classes if "confirmed" in r.get("allowed_status", "").lower() or r.get("physical_claim_release") != PHYSICAL_CLAIM_RELEASE]
    add(rows, "no_class_confirms_independence_or_physical_proxy", not bad_class_claims, "|".join(bad_class_claims) or "no_confirming_classes")

    tests = read_csv(run_dir / "data/test_design_spec.csv")
    test_set = {r.get("test_key", "") for r in tests}
    add(rows, "all_required_test_designs_present", test_set == REQUIRED_TESTS, "|".join(sorted(REQUIRED_TESTS - test_set)) or "all_test_designs_present")
    add(rows, "no_tests_executed", all(r.get("execution_status") == "not_executed_design_only" for r in tests) and s.get("no_tests_executed") == "true", "test_design_only")

    decisions = read_csv(run_dir / "data/later_execution_decision_logic.csv")
    decision_set = {r.get("decision_class", "") for r in decisions}
    add(rows, "all_required_decision_classes_present", decision_set == REQUIRED_DECISIONS, "|".join(sorted(REQUIRED_DECISIONS - decision_set)) or "all_decisions_present")
    add(rows, "decision_logic_claim_release_blocked", all(r.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for r in decisions), "all_decisions_block_physical_claims")

    phase_rule = read_csv(run_dir / "data/phase_response_special_rule.csv")
    add(rows, "phase_response_special_rule_file_present", phase_rule and phase_rule[0].get("rule_key") == "phase_response_abs_lag_alias", phase_rule[0].get("rule_key", "missing") if phase_rule else "missing")

    dr = read_csv(run_dir / "data/deep_research_handoff_questions.csv")
    add(rows, "deep_research_questions_only", dr and all(r.get("handoff_question", "").strip().endswith("?") and r.get("evidence_status") == "question_only_no_deep_research_answer" for r in dr), f"question_rows={len(dr)}")

    manifest = json.loads((run_dir / "data/design_manifest.json").read_text(encoding="utf-8"))
    add(rows, "manifest_target_run_id", manifest.get("target_run_id_verified") == RUN_ID, manifest.get("target_run_id_verified", "missing"))
    add(rows, "manifest_no_tests_no_nullmodels", manifest.get("no_tests_executed") is True and manifest.get("no_nullmodels_executed") is True, f"tests={manifest.get('no_tests_executed')} nullmodels={manifest.get('no_nullmodels_executed')}")
    add(rows, "no_nullmodels_executed", s.get("no_nullmodels_executed") == "true", s.get("no_nullmodels_executed", "missing"))

    claims = read_csv(run_dir / "data/claim_boundaries.csv")
    add(rows, "claim_boundaries_blocked", claims and all(r.get("status") == "blocked" and r.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE for r in claims), f"claim_rows={len(claims)}")

    insert_sql = (run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_design.sql").read_text(encoding="utf-8")
    create_sql = (run_dir / "sql/001_create_qsb_pbr_independent_lag_variable_design.sql").read_text(encoding="utf-8")
    add(rows, "german_view_created", "v_pbr_unabhaengige_lag_variable_design_de" in create_sql, "view_name_present")
    expected_tables = {"pbr_independent_lag_variable_design_summary", "pbr_independent_lag_variable_independence_criteria", "pbr_independent_lag_variable_alias_rules", "pbr_independent_lag_variable_test_design", "pbr_independent_lag_variable_next_gate"}
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
    add(rows, "no_files_outside_run_package_modified", not outside or s.get("pre_existing_modified_files_detected") == "true", "|".join(outside) or "no_outside_changes")
    add(rows, "pre_existing_modifications_recorded", (not outside) or bool(s.get("pre_existing_modified_files")), s.get("pre_existing_modified_files", "none"))
    add(rows, "git_diff_check_passes", git_diff_check(repo_root), "git diff --check")

    validation_path = run_dir / "validation/validation_results.csv"
    write_csv(validation_path, rows)

    block_lines = [
        "-- BEGIN generated validation results import",
        f"DELETE FROM qsb_planck_bridge.pbr_independent_lag_variable_validation WHERE run_id = '{RUN_ID}';",
        "COPY qsb_planck_bridge.pbr_independent_lag_variable_validation (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');",
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
    (run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_design.sql").write_text(insert_sql, encoding="utf-8")

    failed = [row for row in rows if row["status"] != "PASS"]
    print(f"target_run_id={RUN_ID}")
    print(f"validation_checks={len(rows)}")
    print(f"validation_failed={len(failed)}")
    for row in failed:
        print(f"FAIL {row['check_name']}: {row['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
