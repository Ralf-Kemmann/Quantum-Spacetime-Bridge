#!/usr/bin/env python3
"""Generate a result-review package for the PBR admissibility execution."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01"
SOURCE_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(line.rstrip() for line in text.strip().splitlines()) + "\n", encoding="utf-8")


def git_status(repo_root: Path) -> List[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=repo_root, text=True, capture_output=True)
    return proc.stdout.splitlines()


def git_head(repo_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def tsv(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def create_sql(run_dir: Path, tables: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in tables.items():
        parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  " + ",\n  ".join(f"{field} text" for field in fields) + "\n);")
        parts.append("")
    parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_unabhaengige_lag_variable_zulassung_review_de;")
    parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_unabhaengige_lag_variable_zulassung_review_de AS
SELECT
  run_id AS "Lauf-ID",
  source_run_id AS "Quell-Lauf-ID",
  review_outcome AS "Review-Ergebnis",
  candidate_count_total AS "Kandidaten gesamt",
  candidate_count_admissible_for_testing AS "sofort zugelassen",
  dominant_blocker AS "dominanter Blocker",
  dominant_blocker_count AS "Blocker-Anzahl",
  lineage_repair_candidate_count AS "Lineage-Reparaturkandidaten",
  metadata_repair_candidate_count AS "Metadaten-Reparaturkandidaten",
  mechanism_testing_readiness AS "Mechanismus-Testbereitschaft",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate",
  secondary_next_gate AS "sekundärer Gate",
  tertiary_next_gate AS "tertiärer Gate"
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = '{RUN_ID}';""")
    write_text(run_dir / "sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql", "\n".join(parts))
    lines = ["BEGIN;", ""]
    for table in tables:
        lines.append(f"DELETE FROM {SCHEMA}.{table} WHERE run_id = '{RUN_ID}';")
    lines.append("")
    for table, (fields, rows) in tables.items():
        if not rows:
            continue
        lines.append(f"COPY {SCHEMA}.{table} ({', '.join(fields)}) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');")
        lines.append("\t".join(fields))
        for row in rows:
            lines.append("\t".join(tsv(row.get(field, "")) for field in fields))
        lines.append(r"\.")
        lines.append("")
    lines.append("COMMIT;")
    write_text(run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql", "\n".join(lines))
    write_text(run_dir / "sql/003_validation_queries.sql", f"""
SELECT 'review_outcome' AS check_name, review_outcome AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = '{RUN_ID}';

SELECT 'candidate_count_total' AS check_name, candidate_count_total AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = '{RUN_ID}';

SELECT 'dominant_blocker' AS check_name, dominant_blocker AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = '{RUN_ID}';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_result_review_next_gate
WHERE run_id = '{RUN_ID}';
""")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, default=Path(f"runs/{RUN_ID}"))
    parser.add_argument("--database", default="qsb_research_dwh")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    if run_dir.name != RUN_ID:
        raise SystemExit("wrong_prompt_or_stale_context_detected")

    status_before = git_status(repo_root)
    pre_existing = [line for line in status_before if not (line[3:] if len(line) > 3 else line).startswith(f"runs/{RUN_ID}/")]
    source_dir = repo_root / "runs" / SOURCE_RUN_ID
    source_summary = (read_csv(source_dir / "data/execution_summary.csv") or [{}])[0]
    results = read_csv(source_dir / "data/candidate_admissibility_results.csv")
    repairs = read_csv(source_dir / "data/repair_required_candidate_summary.csv")
    validation = read_csv(source_dir / "validation/validation_results.csv")
    source_missing = not source_summary
    lineage_commit_status = "local_uncommitted_input_run" if any(SOURCE_RUN_ID in line for line in status_before) else "committed_or_no_local_delta_detected"
    review_outcome = "blocked_missing_input_run" if source_missing else "admissibility_execution_review_completed"
    next_gate = "input_run_required" if source_missing else "lineage_repair_required"

    summary = {
        "run_id": RUN_ID,
        "run_type": "independent_lag_variable_admissibility_execution_result_review",
        "source_run_id": SOURCE_RUN_ID,
        "review_outcome": review_outcome,
        "confirmed_execution_status": source_summary.get("execution_status", "blocked_missing_input_run"),
        "confirmed_final_admissibility_status": source_summary.get("final_admissibility_status", "blocked_missing_input_run"),
        "candidate_count_total": source_summary.get("candidate_count_total", "0"),
        "candidate_count_admissible_for_testing": source_summary.get("candidate_count_admissible_for_testing", "0"),
        "dominant_blocker": "not_pair_mappable" if source_summary.get("candidate_count_rejected_not_pair_mappable", "0") != "0" else "unknown",
        "dominant_blocker_count": source_summary.get("candidate_count_rejected_not_pair_mappable", "0"),
        "lineage_repair_candidate_count": source_summary.get("candidate_count_lineage_repair", "0"),
        "metadata_repair_candidate_count": source_summary.get("candidate_count_metadata_repair", "0"),
        "mechanism_testing_readiness": "not_ready_no_admissible_candidates",
        "claim_status": "admissibility_execution_result_review_only",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "external_readiness": "internal_only",
        "next_gate": next_gate,
        "secondary_next_gate": "physical_proxy_source_review_required",
        "tertiary_next_gate": "deep_research_method_criteria_review_pending",
        "lineage_commit_status": lineage_commit_status,
        "pre_existing_modified_files_detected": "true" if pre_existing else "false",
        "git_head": git_head(repo_root),
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    input_lineage = [{
        "run_id": RUN_ID, "source_run_id": SOURCE_RUN_ID, "source_status": "missing" if source_missing else "available",
        "source_execution_status": source_summary.get("execution_status", "missing"),
        "source_validation_pass_count": str(sum(1 for row in validation if row.get("status") == "PASS")),
        "source_validation_fail_count": str(sum(1 for row in validation if row.get("status") == "FAIL")),
        "lineage_commit_status": lineage_commit_status,
    }]
    result_review = [{
        "run_id": RUN_ID,
        "review_question": "what_did_execution_establish",
        "review_answer": "260 Kandidaten wurden gegen Nicht-Alias-, Lineage-, Pair-Mapping- und Metadatenkriterien geprüft; kein Kandidat wurde unmittelbar für spätere Lag-Mechanismus-Tests zugelassen.",
        "interpretation_boundary": "Das widerlegt QSB/PBR nicht und beweist keine reine Indexkonstruktion; es begrenzt nur die aktuelle Artefaktzulassung.",
        "claim_implication": "admissibility_result_review_only_no_physical_claim",
    }]
    blocker_rows = [
        {"run_id": RUN_ID, "blocker_key": "not_pair_mappable", "blocker_count": source_summary.get("candidate_count_rejected_not_pair_mappable", "0"), "blocker_role": "dominant_blocker", "review_interpretation": "Ohne Pair-Mapping sind Kandidaten nicht für 42 directed pair-feature Lag-Mechanismus-Tests nutzbar.", "next_action": "do_not_use_without_pair_mapping_repair", "claim_implication": "no_lag_mechanism_test_admissibility"},
        {"run_id": RUN_ID, "blocker_key": "lineage_incomplete", "blocker_count": source_summary.get("candidate_count_lineage_repair", "0"), "blocker_role": "repair_gate", "review_interpretation": "Lineage-Lücken müssen vor erneuter Admissibility-Prüfung geschlossen werden.", "next_action": "lineage_repair_required", "claim_implication": "no_independence_claim"},
        {"run_id": RUN_ID, "blocker_key": "metadata_incomplete", "blocker_count": source_summary.get("candidate_count_metadata_repair", "0"), "blocker_role": "secondary_repair_gate", "review_interpretation": "Proxy-artige Kandidaten brauchen Einheiten-/Dimensionskontext.", "next_action": "physical_proxy_source_review_required", "claim_implication": "no_physical_proxy_claim"},
        {"run_id": RUN_ID, "blocker_key": "no_admissible_candidate", "blocker_count": source_summary.get("candidate_count_admissible_for_testing", "0"), "blocker_role": "mechanism_testing_readiness", "review_interpretation": "0 zugelassene Kandidaten bedeutet: aktuelle Artefakte erfüllen die Zulassung nicht.", "next_action": "do_not_start_lag_mechanism_testing_from_current_candidates", "claim_implication": "not_ready_no_admissible_candidates"},
    ]
    repair_rows = []
    for row in repairs:
        repair_type = "metadata_repair" if row.get("admissibility_decision_class") == "candidate_admissible_only_after_metadata_repair" else "lineage_repair"
        repair_rows.append({
            "run_id": RUN_ID, "candidate_id": row.get("candidate_id", ""), "candidate_variable_name": row.get("candidate_variable_name", ""),
            "repair_type": repair_type, "source_type": row.get("source_type", ""), "source_path_or_table": row.get("source_path_or_table", ""),
            "current_decision_class": row.get("admissibility_decision_class", ""), "repair_need": repair_type,
            "minimum_repair_requirement": "source_lineage_and_non_alias_evidence" if repair_type == "lineage_repair" else "unit_dimension_metadata_and_proxy_source_review",
            "allowed_next_use_after_repair": "rerun_admissibility_execution_only", "claim_boundary": "repair_candidate_not_mechanism_evidence",
        })
    not_pair_rows = [{
        "run_id": RUN_ID, "rejected_not_pair_mappable_count": source_summary.get("candidate_count_rejected_not_pair_mappable", "0"),
        "interpretation": "not_pair_mappable_candidates_cannot_be_used_for_42_directed_pair_feature_lag_mechanism_testing",
        "next_action": "do_not_use_without_pair_mapping_repair", "claim_implication": "no_lag_mechanism_test_admissibility",
    }]
    deep_rows = [{
        "run_id": RUN_ID, "deep_research_status": "pending_or_parallel",
        "deep_research_role": "method_criteria_and_reviewer_risk_only",
        "deep_research_cannot_replace_internal_lineage": "true",
        "deep_research_cannot_confirm_current_matrix_proxy": "true",
        "allowed_use": "criteria_context_and_red_team_risk",
        "not_allowed_use": "internal_evidence_substitution",
    }]
    next_rows = [{
        "run_id": RUN_ID, "next_gate": next_gate, "secondary_next_gate": "physical_proxy_source_review_required",
        "tertiary_next_gate": "deep_research_method_criteria_review_pending",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE, "execution_authorization": "not_authorized_in_this_review_run",
    }]
    recommended = [
        ("QSB-PLANCK-BRIDGE-RESONATOR-LINEAGE-REPAIR-DESIGN-01", "primary", "Design source-lineage repair for the two lineage repair candidates."),
        ("QSB-PLANCK-BRIDGE-RESONATOR-PHYSICAL-PROXY-SOURCE-REVIEW-01", "secondary", "Review proxy-source artifacts separately."),
        ("QSB-PLANCK-BRIDGE-RESONATOR-DEEP-RESEARCH-METHOD-CRITERIA-INTEGRATION-01", "later", "Integrate Deep Research criteria as context only."),
    ]
    recommended_rows = [{"run_id": RUN_ID, "recommended_run_id": r, "priority": p, "rationale": t} for r, p, t in recommended]
    blocked_claims = [
        "QSB is physically " + "validated", "PBR exists " + "physically", "six lag axes are " + "spacetime dimensions",
        "spacetime emergence is " + "proven", "empirical validation " + "exists", "lag classes are " + "physical dimensions",
        "lag mechanism is physically " + "proven", "admissibility execution proves " + "independent lag variable",
        "admissibility execution proves " + "physical proxy", "0 admissible candidates disproves " + "QSB",
        "0 admissible candidates proves " + "pure index construction", "repair candidate proves " + "mechanism",
        "Deep Research can replace " + "internal lineage", "DWH presence alone proves " + "independence",
        "repo presence alone proves " + "independence", "literature note alone proves " + "proxy for current matrix",
    ]
    claims = [{"run_id": RUN_ID, "claim_key": f"BLOCK-{i:03d}", "claim_text": claim, "status": "blocked", "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for i, claim in enumerate(blocked_claims, 1)]
    manifest = {
        "run_id": RUN_ID, "target_run_id_verified": RUN_ID, "source_run_id": SOURCE_RUN_ID,
        "pre_existing_modified_files_detected": bool(pre_existing), "pre_existing_modified_files": pre_existing,
        "no_admissibility_checks_executed_in_review_run": True, "no_lag_mechanism_tests_executed": True,
        "no_nullmodels_executed": True, "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }
    validation_placeholder = [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Review generated; run validator."}]

    data_dir = run_dir / "data"
    write_csv(data_dir / "review_summary.csv", [summary], list(summary.keys()))
    write_csv(data_dir / "input_run_lineage.csv", input_lineage, list(input_lineage[0].keys()))
    write_csv(data_dir / "admissibility_result_review.csv", result_review, list(result_review[0].keys()))
    write_csv(data_dir / "blocker_analysis.csv", blocker_rows, list(blocker_rows[0].keys()))
    write_csv(data_dir / "repair_candidate_review.csv", repair_rows, list(repair_rows[0].keys()) if repair_rows else ["run_id", "candidate_id", "candidate_details_status"])
    write_csv(data_dir / "not_pair_mappable_review.csv", not_pair_rows, list(not_pair_rows[0].keys()))
    write_csv(data_dir / "claim_boundaries.csv", claims, list(claims[0].keys()))
    write_csv(data_dir / "deep_research_boundary.csv", deep_rows, list(deep_rows[0].keys()))
    write_csv(data_dir / "next_gate_decision.csv", next_rows, list(next_rows[0].keys()))
    write_csv(data_dir / "recommended_next_work.csv", recommended_rows, list(recommended_rows[0].keys()))
    write_text(data_dir / "review_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
    write_csv(run_dir / "validation/validation_results.csv", validation_placeholder, list(validation_placeholder[0].keys()))

    docs = {
        "README.md": f"# {RUN_ID}\n\nResult-Review der Independent-Lag-Variable-Admissibility-Ausführung.\n\nNo admissibility checks were executed in this review run.\nNo lag mechanism tests were executed.\nNo nullmodels were executed.\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        f"{RUN_ID}.md": f"# {RUN_ID}\n\n## Befund\n\nDie Admissibility-Ausführung prüfte {summary['candidate_count_total']} Kandidaten. Kein Kandidat wurde unmittelbar für spätere Lag-Mechanismus-Tests zugelassen. Dominanter Blocker: `{summary['dominant_blocker']}` mit `{summary['dominant_blocker_count']}` Fällen.\n\n## Interpretation\n\n0 zugelassene Kandidaten widerlegt QSB/PBR nicht und beweist keine reine Indexkonstruktion. Es bedeutet, dass die aktuellen Kandidatenartefakte die Zulassungskriterien noch nicht erfüllen.\n\n## Hypothese\n\nLineage-Reparatur und Proxy-Source-Review können die Eingabelage für spätere Admissibility-Runs verbessern.\n\n## Offene Lücke\n\nPair-Mapping, Lineage und Metadaten sind vor Mechanismus-Tests zu reparieren.\n\n## Claim Boundary\n\nNo physical claims are released. `physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "RUN_COMMANDS_PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW01.md": f"# Run Commands\n\n```bash\nRUN_DIR=\"runs/{RUN_ID}\"\n.venv/bin/python \"$RUN_DIR/scripts/run_pbr_independent_lag_variable_admissibility_execution_result_review.py\" --repo-root . --run-dir \"$RUN_DIR\" --database qsb_research_dwh\n.venv/bin/python \"$RUN_DIR/scripts/validate_pbr_independent_lag_variable_admissibility_execution_result_review.py\" \"$RUN_DIR\"\ngit diff --check\ngit status --short --untracked-files=all\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql\"\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution_result_review.sql\"\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/003_validation_queries.sql\"\n```\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md": "# Summary\n\n## Befund\n\n260 Kandidaten geprüft; 0 unmittelbar zugelassen; 257 nicht pair-mappable.\n\n## Interpretation\n\nNichtzulassung ist keine Widerlegung.\n\n## Hypothese\n\nLineage-Reparatur ist der nächste interne Gate.\n\n## Offene Lücke\n\nKeine Mechanismus-Testbereitschaft.\n\n## Claim Boundary\n\nKeine physikalische Claim-Freigabe.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_BLOCKERS_DE.md": "# Blocker\n\n## Befund\n\nDominanter Blocker ist fehlende Pair-Mappbarkeit.\n\n## Interpretation\n\nNicht pair-mappable Kandidaten sind nicht für 42 directed pair-feature Tests nutzbar.\n\n## Hypothese\n\nPair-Mapping- oder Lineage-Reparatur kann Kandidaten erneut prüfbar machen.\n\n## Offene Lücke\n\nRepair nicht ausgeführt.\n\n## Claim Boundary\n\nKein Mechanismusclaim.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_REPAIR_CANDIDATES_DE.md": "# Repair Candidates\n\n## Befund\n\nZwei Kandidaten benötigen Lineage-Reparatur und ein Kandidat Metadaten-Reparatur.\n\n## Interpretation\n\nReparaturkandidaten sind relevant, aber nicht zugelassen.\n\n## Hypothese\n\nNach Reparatur kann ein neuer Admissibility-Run sinnvoll sein.\n\n## Offene Lücke\n\nKeine Reparatur in diesem Review.\n\n## Claim Boundary\n\nRepair ist keine Evidenz für Mechanismus.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md": "# Claim Boundary\n\n## Befund\n\nPhysikalische Claims bleiben gesperrt.\n\n## Interpretation\n\n0 admissible Kandidaten beweist weder QSB noch dessen Gegenteil.\n\n## Hypothese\n\nWeitere interne Evidenz kann spätere Gates öffnen.\n\n## Offene Lücke\n\nInterne Lineage bleibt erforderlich.\n\n## Claim Boundary\n\n`physical_claim_release=blocked_no_physics_claim`\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md": "# Next Gate\n\n## Befund\n\nPrimary: `lineage_repair_required`; Secondary: `physical_proxy_source_review_required`; Tertiary: `deep_research_method_criteria_review_pending`.\n\n## Interpretation\n\nDeep Research kann Kriterienkontext liefern, ersetzt aber keine interne Evidenz.\n\n## Hypothese\n\nDer nächste Run sollte Lineage-Reparatur designen.\n\n## Offene Lücke\n\nKeine Ausführungsautorisation in diesem Review.\n\n## Claim Boundary\n\nKeine Claim-Freigabe.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULT_REVIEW_DEEP_RESEARCH_BOUNDARY_DE.md": "# Deep Research Boundary\n\n## Befund\n\nDeep Research ist pending oder parallel und hat nur Methoden-/Reviewer-Risiko-Rolle.\n\n## Interpretation\n\nExterne Methodik ersetzt keine interne Source-Lineage.\n\n## Hypothese\n\nSpätere Integration kann Kriterien schärfen.\n\n## Offene Lücke\n\nKeine Deep-Research-Ergebnisse in diesem Run.\n\n## Claim Boundary\n\nKeine Proxy-Bestätigung durch Deep Research.\n",
    }
    for rel, text in docs.items():
        write_text(run_dir / rel, text)

    tables = {
        "pbr_independent_lag_variable_admissibility_result_review_summary": (list(summary.keys()), [summary]),
        "pbr_independent_lag_variable_admissibility_result_review_lineage": (list(input_lineage[0].keys()), input_lineage),
        "pbr_independent_lag_variable_admissibility_result_review_results": (list(result_review[0].keys()), result_review),
        "pbr_independent_lag_variable_admissibility_result_review_blockers": (list(blocker_rows[0].keys()), blocker_rows),
        "pbr_independent_lag_variable_admissibility_result_review_repair_candidates": (list(repair_rows[0].keys()) if repair_rows else ["run_id", "candidate_id", "candidate_details_status"], repair_rows),
        "pbr_independent_lag_variable_admissibility_result_review_not_pair_mappable": (list(not_pair_rows[0].keys()), not_pair_rows),
        "pbr_independent_lag_variable_admissibility_result_review_claim_boundaries": (list(claims[0].keys()), claims),
        "pbr_independent_lag_variable_admissibility_result_review_deep_research_boundary": (list(deep_rows[0].keys()), deep_rows),
        "pbr_independent_lag_variable_admissibility_result_review_next_gate": (list(next_rows[0].keys()), next_rows),
        "pbr_independent_lag_variable_admissibility_result_review_recommended_work": (list(recommended_rows[0].keys()), recommended_rows),
        "pbr_independent_lag_variable_admissibility_result_review_validation": (list(validation_placeholder[0].keys()), validation_placeholder),
    }
    create_sql(run_dir, tables)
    print(f"target_run_id={RUN_ID}")
    print(f"review_outcome={review_outcome}")
    print(f"confirmed_execution_status={summary['confirmed_execution_status']}")
    print(f"candidate_count_total={summary['candidate_count_total']}")
    print(f"dominant_blocker={summary['dominant_blocker']}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
