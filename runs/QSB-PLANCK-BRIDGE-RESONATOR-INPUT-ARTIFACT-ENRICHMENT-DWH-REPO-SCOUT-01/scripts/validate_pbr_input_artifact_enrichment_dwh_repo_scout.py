#!/usr/bin/env python3
"""Validate the PBR input-artifact DWH/repo scout package."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
REVIEW_RUN_PREFIX = "runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01/"
REQUIRED_PROXY_FAMILIES = {
    "momentum_proxy",
    "energy_proxy",
    "frequency_proxy",
    "phase_proxy",
    "mode_proxy",
    "spectral_gap_proxy",
    "compton_schwarzschild_proxy",
    "planck_scale_mapping_proxy",
}
FORBIDDEN_INDEPENDENCE_STATUSES = {
    "confirmed_independent",
    "confirmed_physical_proxy",
    "validated_physical_proxy",
    "physical_proxy_confirmed",
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
]
ALLOWED_CONTEXT_MARKERS = [
    "blocked",
    "prohibited",
    "claim_boundaries",
    "claim boundary",
    "no physical claims are released",
    "blocked_no_physics_claim",
]


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
    return b"\r\n" not in raw and b"\r" not in raw


def git_status(repo_root: Path) -> List[str]:
    proc = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.splitlines()


def status_path(line: str) -> str:
    return line[3:] if len(line) > 3 else line


def copy_table_columns(sql_text: str) -> Dict[str, List[str]]:
    tables: Dict[str, List[str]] = {}
    pattern = re.compile(r"COPY\s+qsb_planck_bridge\.([a-z0-9_]+)\s+\(([^)]*)\)\s+FROM stdin", re.IGNORECASE)
    for match in pattern.finditer(sql_text):
        tables[match.group(1)] = [col.strip() for col in match.group(2).split(",")]
    return tables


def main() -> int:
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"runs/{RUN_ID}")
    run_dir = run_dir.resolve()
    repo_root = Path.cwd().resolve()
    rows: List[Dict[str, str]] = []

    add(rows, "run_directory_name", run_dir.name == RUN_ID, str(run_dir))

    required_files = [
        "README.md",
        f"{RUN_ID}.md",
        "RUN_COMMANDS_PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT01.md",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_SUMMARY_DE.md",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_CANDIDATES_DE.md",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_ALIAS_RISK_DE.md",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_DWH_RESULTS_DE.md",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_NEXT_GATE_DE.md",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_DEEP_RESEARCH_HANDOFF_DE.md",
        "data/scout_summary.csv",
        "data/repo_artifact_inventory.csv",
        "data/dwh_artifact_inventory.csv",
        "data/candidate_variable_inventory.csv",
        "data/candidate_lineage_assessment.csv",
        "data/candidate_alias_risk_assessment.csv",
        "data/physical_proxy_source_candidates.csv",
        "data/pair_mapping_readiness.csv",
        "data/input_artifact_gap_update.csv",
        "data/deep_research_handoff_questions.csv",
        "data/claim_boundaries.csv",
        "data/next_gate_decision.csv",
        "data/scout_manifest.json",
        "scripts/run_pbr_input_artifact_enrichment_dwh_repo_scout.py",
        "scripts/validate_pbr_input_artifact_enrichment_dwh_repo_scout.py",
        "sql/001_create_qsb_pbr_input_artifact_enrichment_dwh_repo_scout.sql",
        "sql/002_insert_qsb_pbr_input_artifact_enrichment_dwh_repo_scout.sql",
        "sql/003_validation_queries.sql",
        "validation/validation_results.csv",
    ]
    missing = [rel for rel in required_files if not (run_dir / rel).exists()]
    add(rows, "required_files_exist", not missing, "|".join(missing) or "all_required_files_present")

    lf_bad = [rel for rel in required_files if (run_dir / rel).exists() and not ensure_lf_utf8(run_dir / rel)]
    add(rows, "utf8_lf_files", not lf_bad, "|".join(lf_bad) or "all_required_text_files_utf8_lf")

    summary = read_csv(run_dir / "data/scout_summary.csv")
    summary_row = summary[0] if summary else {}
    add(rows, "summary_run_id_exact", summary_row.get("run_id") == RUN_ID, summary_row.get("run_id", "missing"))
    add(rows, "summary_run_type", summary_row.get("run_type") == "dwh_repo_artifact_scout", summary_row.get("run_type", "missing"))
    add(rows, "execution_status", summary_row.get("execution_status") in {"executed", "blocked_dwh_unavailable"}, summary_row.get("execution_status", "missing"))
    add(rows, "physical_claim_release_blocked", summary_row.get("physical_claim_release") == PHYSICAL_CLAIM_RELEASE, summary_row.get("physical_claim_release", "missing"))
    add(rows, "dwh_status_recorded", summary_row.get("dwh_scout_status") in {"executed", "blocked_dwh_unavailable"}, summary_row.get("dwh_scout_status", "missing"))

    candidates = read_csv(run_dir / "data/candidate_variable_inventory.csv")
    add(rows, "candidate_inventory_present", len(candidates) > 0, f"candidate_rows={len(candidates)}")
    bad_independence = [
        c.get("candidate_id", "")
        for c in candidates
        if c.get("independence_status", "") in FORBIDDEN_INDEPENDENCE_STATUSES
        or c.get("claim_implication", "") in FORBIDDEN_INDEPENDENCE_STATUSES
    ]
    add(rows, "no_confirmed_independence_or_physical_proxy", not bad_independence, "|".join(bad_independence) or "no_forbidden_confirmations")
    presence_claim_bad = [
        c.get("candidate_id", "")
        for c in candidates
        if c.get("source_type") in {"dwh_table", "repo_file"}
        and "proves" in c.get("claim_implication", "").lower()
    ]
    add(rows, "presence_alone_not_treated_as_proof", not presence_claim_bad, "|".join(presence_claim_bad) or "no_presence_as_proof")

    proxy_rows = read_csv(run_dir / "data/physical_proxy_source_candidates.csv")
    proxy_families = {r.get("proxy_family", "") for r in proxy_rows}
    add(rows, "all_proxy_families_represented", proxy_families == REQUIRED_PROXY_FAMILIES, "|".join(sorted(REQUIRED_PROXY_FAMILIES - proxy_families)) or "all_proxy_families_present")
    proxy_claim_bad = [r.get("proxy_family", "") for r in proxy_rows if "physical_proxy_claim" not in r.get("claim_implication", "")]
    add(rows, "proxy_rows_candidate_only", not proxy_claim_bad, "|".join(proxy_claim_bad) or "all_proxy_rows_candidate_only")

    alias_rows = read_csv(run_dir / "data/candidate_alias_risk_assessment.csv")
    phase_rows = [r for r in alias_rows if "phase" in r.get("candidate_variable_name", "").lower()]
    bad_phase_alias = [r.get("candidate_id", "") for r in phase_rows if r.get("alias_risk_level") != "high"]
    add(rows, "phase_response_alias_risk_high", phase_rows and not bad_phase_alias, "|".join(bad_phase_alias) or f"phase_rows={len(phase_rows)}")

    gaps = read_csv(run_dir / "data/input_artifact_gap_update.csv")
    add(rows, "gap_update_present", len(gaps) >= 5, f"gap_rows={len(gaps)}")
    questions = read_csv(run_dir / "data/deep_research_handoff_questions.csv")
    non_questions = [q.get("question_id", "") for q in questions if not q.get("handoff_question", "").strip().endswith("?")]
    answered = [q.get("question_id", "") for q in questions if q.get("evidence_status") != "question_only_no_deep_research_answer"]
    add(rows, "deep_research_handoff_questions_only", questions and not non_questions and not answered, "|".join(non_questions + answered) or f"question_rows={len(questions)}")

    manifest = json.loads((run_dir / "data/scout_manifest.json").read_text(encoding="utf-8"))
    add(rows, "target_run_id_verified", manifest.get("target_run_id_verified") == RUN_ID, manifest.get("target_run_id_verified", "missing"))
    add(rows, "no_lag_mechanism_tests_executed", manifest.get("no_lag_mechanism_tests_executed") is True, str(manifest.get("no_lag_mechanism_tests_executed")))
    add(rows, "no_nullmodels_executed", manifest.get("no_nullmodels_executed") is True, str(manifest.get("no_nullmodels_executed")))

    claims = read_csv(run_dir / "data/claim_boundaries.csv")
    claim_status_bad = [c.get("claim_key", "") for c in claims if c.get("status") != "blocked" or c.get("physical_claim_release") != PHYSICAL_CLAIM_RELEASE]
    add(rows, "claim_boundaries_block_forbidden_claims", claims and not claim_status_bad, "|".join(claim_status_bad) or f"claim_rows={len(claims)}")

    create_sql = (run_dir / "sql/001_create_qsb_pbr_input_artifact_enrichment_dwh_repo_scout.sql").read_text(encoding="utf-8")
    insert_sql = (run_dir / "sql/002_insert_qsb_pbr_input_artifact_enrichment_dwh_repo_scout.sql").read_text(encoding="utf-8")
    add(rows, "german_view_created", "v_pbr_input_artefakt_scout_de" in create_sql, "view_name_present")
    copy_tables = copy_table_columns(insert_sql)
    expected_tables = {
        "pbr_input_artifact_enrichment_scout_summary",
        "pbr_input_artifact_enrichment_candidate_variables",
        "pbr_input_artifact_enrichment_claim_boundaries",
        "pbr_input_artifact_enrichment_next_gate",
    }
    add(rows, "sql_copy_tables_present", expected_tables.issubset(copy_tables), "|".join(sorted(expected_tables - set(copy_tables))) or "required_copy_tables_present")

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
                    if not any(marker in context for marker in ALLOWED_CONTEXT_MARKERS):
                        forbidden_hits.append(f"{rel_path}:{phrase}")
    add(rows, "forbidden_phrases_only_in_blocked_context", not forbidden_hits, "|".join(forbidden_hits) or "no_unblocked_forbidden_phrase_hits")

    status = git_status(repo_root)
    outside = []
    pre_existing_review = []
    for line in status:
        path = status_path(line)
        if path.startswith(f"runs/{RUN_ID}/"):
            continue
        if path.startswith(REVIEW_RUN_PREFIX):
            pre_existing_review.append(line)
            continue
        outside.append(line)
    add(rows, "working_tree_scope", not outside, "|".join(outside) or "only_scout_run_plus_pre_existing_review_modifications")
    add(rows, "pre_existing_review_modifications_reported", bool(pre_existing_review), "|".join(pre_existing_review) or "none_detected")

    validation_path = run_dir / "validation/validation_results.csv"
    write_csv(validation_path, rows)

    validation_table = "pbr_input_artifact_enrichment_validation"
    block_lines = [
        "-- BEGIN generated validation results import",
        f"DELETE FROM qsb_planck_bridge.{validation_table} WHERE run_id = '{RUN_ID}';",
        f"COPY qsb_planck_bridge.{validation_table} (run_id, check_name, status, detail) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');",
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
    (run_dir / "sql/002_insert_qsb_pbr_input_artifact_enrichment_dwh_repo_scout.sql").write_text(insert_sql, encoding="utf-8")

    failed = [row for row in rows if row["status"] != "PASS"]
    print(f"target_run_id={RUN_ID}")
    print(f"validation_checks={len(rows)}")
    print(f"validation_failed={len(failed)}")
    for row in failed:
        print(f"FAIL {row['check_name']}: {row['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
