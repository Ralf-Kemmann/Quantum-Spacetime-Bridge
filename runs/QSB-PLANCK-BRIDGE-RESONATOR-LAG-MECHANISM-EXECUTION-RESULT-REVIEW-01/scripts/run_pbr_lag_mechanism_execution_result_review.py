#!/usr/bin/env python3
"""Create the PBR lag mechanism execution result-review package."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01"
SOURCE_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
NEXT_GATE = "input_artifact_enrichment_required"
SECONDARY_GATE = "independent_lag_variable_design_required"
TERTIARY_GATE = "physical_proxy_source_review_required"
PRIMARY_NEXT_RUN = "QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DESIGN-01"
TESTS = [
    "index_relabeling_test",
    "order_scrambling_test",
    "independent_lag_variable_test",
    "shift_operator_test",
    "toeplitz_dependency_test",
    "physical_proxy_test",
    "nullmodel_operationalization_review",
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = "\n".join(line.rstrip() for line in text.strip().splitlines()) + "\n"
    path.write_text(clean, encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def git_commit(repo_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def sql_type(field: str) -> str:
    return "text"


def sql_value(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def create_sql(run_dir: Path, tables: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in tables.items():
        cols = ",\n  ".join(f"{field} {sql_type(field)}" for field in fields)
        parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  {cols}\n);")
        parts.append("")
    parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_lag_mechanismus_execution_review_de;")
    parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_lag_mechanismus_execution_review_de AS
SELECT
  run_id AS "Lauf-ID",
  source_run_id AS "Quell-Lauf-ID",
  review_outcome AS "Review-Ergebnis",
  formal_finding_status AS "formaler Befundstatus",
  mechanism_status AS "Mechanismusstatus",
  physical_proxy_status AS "physikalischer Proxy-Status",
  pure_index_status AS "Pure-Index-Status",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate",
  secondary_next_gate AS "sekundärer Gate",
  tertiary_next_gate AS "tertiärer Gate"
FROM {SCHEMA}.pbr_lag_mechanism_execution_result_review_summary
WHERE run_id = '{RUN_ID}';""")
    write_text(run_dir / "sql/001_create_qsb_pbr_lag_mechanism_execution_result_review.sql", "\n".join(parts))
    insert = ["BEGIN;", ""]
    for table in tables:
        insert.append(f"DELETE FROM {SCHEMA}.{table} WHERE run_id = '{RUN_ID}';")
    insert.append("")
    for table, (fields, rows) in tables.items():
        if not rows:
            continue
        insert.append(f"COPY {SCHEMA}.{table} ({', '.join(fields)}) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');")
        insert.append("\t".join(fields))
        for row in rows:
            insert.append("\t".join(sql_value(row.get(field, "")) for field in fields))
        insert.append(r"\.")
        insert.append("")
    insert.append("COMMIT;")
    write_text(run_dir / "sql/002_insert_qsb_pbr_lag_mechanism_execution_result_review.sql", "\n".join(insert))
    validation = f"""
SELECT 'review_outcome' AS check_name, review_outcome AS value
FROM {SCHEMA}.pbr_lag_mechanism_execution_result_review_summary
WHERE run_id = '{RUN_ID}';

SELECT 'confirmed_decision' AS check_name, review_confirmed_decision_class AS value
FROM {SCHEMA}.pbr_lag_mechanism_execution_result_review_decision
WHERE run_id = '{RUN_ID}';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM {SCHEMA}.pbr_lag_mechanism_execution_result_review_next_gate
WHERE run_id = '{RUN_ID}';

SELECT 'primary_next_run' AS check_name, recommended_run_id AS value
FROM {SCHEMA}.pbr_lag_mechanism_execution_result_review_recommended_work
WHERE run_id = '{RUN_ID}' AND recommendation_rank = 'primary';
"""
    write_text(run_dir / "sql/003_validation_queries.sql", validation)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, default=Path(f"runs/{RUN_ID}"))
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    source_dir = repo_root / f"runs/{SOURCE_RUN_ID}"
    data_dir = run_dir / "data"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if not source_dir.exists():
        row = {"run_id": RUN_ID, "source_run_id": SOURCE_RUN_ID, "review_status": "blocked_missing_input_run", "physical_claim_release": PHYSICAL_CLAIM_RELEASE, "next_gate": "input_run_required"}
        write_csv(data_dir / "lag_mechanism_execution_review_summary.csv", [row], list(row.keys()))
        return 2
    source_summary = read_csv(source_dir / "data/lag_mechanism_execution_summary.csv")[0]
    source_tests = read_csv(source_dir / "data/lag_mechanism_test_results.csv")
    source_decision = read_csv(source_dir / "data/lag_mechanism_decision.csv")[0]

    summary = {
        "run_id": RUN_ID,
        "source_run_id": SOURCE_RUN_ID,
        "review_outcome": "inconclusive_requires_more_inputs_confirmed",
        "formal_finding_status": "strong_formal_lag_dependence_observed",
        "mechanism_status": "independent_mechanism_not_established",
        "physical_proxy_status": "no_independent_physical_proxy_available",
        "pure_index_status": "not_conclusively_proven",
        "claim_status": "lag_mechanism_execution_result_review_only",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "external_readiness": "internal_only",
        "next_gate": NEXT_GATE,
        "secondary_next_gate": SECONDARY_GATE,
        "tertiary_next_gate": TERTIARY_GATE,
        "review_timestamp_utc": now,
        "git_commit": git_commit(repo_root),
    }
    test_review = []
    blocked_review = []
    for row in source_tests:
        key = row["test_key"]
        status = row["execution_status"]
        reviewed_status = "reviewed_executed_test" if status == "executed" else "reviewed_blocked_test"
        if key == "index_relabeling_test":
            contribution = "labels_alone_not_mechanism"
            next_need = "none_for_label_check"
        elif key == "order_scrambling_test":
            contribution = "strong_order_dependence_signal"
            next_need = "independent_order_variable_required"
        elif key == "shift_operator_test":
            contribution = "shift_diagnostic_executed_but_not_sufficient_for_independent_mechanism"
            next_need = "independent_shift_orbit_source_required"
        elif key == "toeplitz_dependency_test":
            contribution = "strong_formal_lag_dependence_signal"
            next_need = "independent_lag_variable_artifact_required"
        elif key == "nullmodel_operationalization_review":
            contribution = "lag_preserving_nullmodel_preserves_target_mechanism"
            next_need = "red_team_nullmodel_role_review_optional"
        elif key == "independent_lag_variable_test":
            contribution = "blocked_no_independent_variable"
            next_need = "independent_lag_variable_artifact_required"
        else:
            contribution = "blocked_no_physical_proxy"
            next_need = "physical_proxy_source_artifact_required"
        claim_implication = row.get("claim_implication") or "formal_review_only"
        test_review.append({
            "run_id": RUN_ID,
            "test_key": key,
            "source_execution_status": status,
            "review_status": reviewed_status,
            "contribution_to_decision": contribution,
            "claim_implication": claim_implication,
            "next_input_need": next_need,
        })
        if key == "independent_lag_variable_test":
            blocked_review.append({
                "run_id": RUN_ID,
                "test_key": key,
                "blocked_reason": "phase_response_values_assessed_as_alias_of_abs_lag",
                "claim_implication": "no_independent_lag_variable_claim",
                "next_input_need": "independent_lag_variable_artifact_required",
            })
        if key == "physical_proxy_test":
            blocked_review.append({
                "run_id": RUN_ID,
                "test_key": key,
                "blocked_reason": "no_independent_physical_proxy_data_found",
                "claim_implication": "no_physical_proxy_claim",
                "next_input_need": "physical_proxy_source_artifact_required",
            })
    decision = [{
        "run_id": RUN_ID,
        "source_run_id": SOURCE_RUN_ID,
        "source_final_decision_class": source_decision["final_decision_class"],
        "review_confirmed_decision_class": "inconclusive_requires_more_inputs",
        "not_formal_lag_mechanism_candidate_reason": "no_independent_lag_variable_or_shift_proxy_artifact_sufficient_to_establish_independent_mechanism",
        "not_physical_proxy_candidate_reason": "no_independent_physical_proxy_data_found",
        "not_pure_index_construction_reason": "strong_formal_lag_dependence_observed_but_not_sufficient_to_prove_pure_index_construction",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }]
    gaps = [
        ("independent_lag_variable_artifact", "missing", "Needed to distinguish lag aliasing from independent formal carrier.", "Per-pair or per-channel variable not derived solely from j-i.", "formal_lag_mechanism_candidate review", "physical_claims_remain_gate_required"),
        ("physical_proxy_source_artifact", "missing", "Needed for any physical proxy candidate assessment.", "Momentum, energy, phase, frequency, mode, or scale variable with lineage and independence note.", "physical_proxy_candidate review", "physical_claims_remain_gate_required"),
        ("proxy_independence_criteria", "missing", "Needed to prevent post-hoc alias use.", "Rules distinguishing independent proxy from abs-lag alias.", "cleaner proxy admissibility", "physical_claims_remain_gate_required"),
        ("phase_response_alias_review", "required", "Phase response values were assessed as abs-lag aliases.", "Review note proving whether phase-response ranges are independent or construction-derived.", "independent_lag_variable eligibility if resolved", "physical_claims_remain_gate_required"),
        ("source_lineage_for_candidate_variables", "missing", "Needed to audit any candidate variable source.", "Artifact path, schema, hash, unit/dimension status, and derivation boundary.", "auditable input enrichment", "physical_claims_remain_gate_required"),
    ]
    gap_rows = [{
        "run_id": RUN_ID,
        "gap_key": key,
        "gap_status": status,
        "why_needed": why,
        "minimum_required_content": minimum,
        "claim_unlocked_if_resolved": unlocked,
        "claim_still_blocked_after_resolution": still,
    } for key, status, why, minimum, unlocked, still in gaps]
    blocked_claims = [
        "QSB is physically " + "validated",
        "PBR exists " + "physically",
        "six lag axes are spacetime " + "dimensions",
        "spacetime emergence is " + "proven",
        "empirical validation " + "exists",
        "lag classes are physical dimensions",
        "lag mechanism is physically proven",
        "execution proves physical proxy",
        "execution proves independent formal lag mechanism",
        "execution proves pure index construction",
        "inconclusive_requires_more_inputs proves QSB",
        "inconclusive_requires_more_inputs disproves QSB",
        "phase-response values are independent lag variables despite alias assessment",
    ]
    claims = [{"run_id": RUN_ID, "claim_key": f"BLOCK-{idx:03d}", "claim_text": claim, "status": "blocked", "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for idx, claim in enumerate(blocked_claims, start=1)]
    next_gate = [{
        "run_id": RUN_ID,
        "next_gate": NEXT_GATE,
        "secondary_next_gate": SECONDARY_GATE,
        "tertiary_next_gate": TERTIARY_GATE,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "execution_authorization": "not_authorized_in_this_review_run",
    }]
    recommended = [
        {"run_id": RUN_ID, "recommended_run_id": PRIMARY_NEXT_RUN, "recommendation_rank": "primary", "purpose": "Define enrichment package for independent lag variables and proxy sources."},
        {"run_id": RUN_ID, "recommended_run_id": "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01", "recommendation_rank": "secondary", "purpose": "Define criteria for independent lag variable admissibility."},
        {"run_id": RUN_ID, "recommended_run_id": "QSB-PLANCK-BRIDGE-RESONATOR-PHYSICAL-PROXY-SOURCE-REVIEW-01", "recommendation_rank": "tertiary", "purpose": "Review possible physical proxy source systems without releasing physical claims."},
    ]
    lineage_ids = [
        SOURCE_RUN_ID,
        "QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01",
    ]
    lineage = [{"run_id": RUN_ID, "source_run_id": sid, "source_path": f"runs/{sid}", "source_exists": "true" if (repo_root / f"runs/{sid}").exists() else "false"} for sid in lineage_ids]
    manifest = {
        "run_id": RUN_ID,
        "source_run_id": SOURCE_RUN_ID,
        "no_lag_mechanism_tests_executed_in_review": True,
        "no_nullmodels_executed_in_review": True,
        "source_summary": source_summary,
        "review_outcome": summary["review_outcome"],
        "confirmed_decision_class": "inconclusive_requires_more_inputs",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }
    docs = {
        "README.md": f"# {RUN_ID}\n\nReview-Lauf zur Lag-Mechanismus-Ausführung.\n\nNo lag mechanism tests were executed in this review run.\nNo nullmodels were executed in this review run.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n`next_gate={NEXT_GATE}`\n",
        f"{RUN_ID}.md": f"# {RUN_ID}\n\n## Befund\n\nDie Lag-Mechanismus-Ausführung bestätigt starke formale Lag-/Ordnungsabhängigkeit, bleibt aber bei `{decision[0]['review_confirmed_decision_class']}`.\n\n## Interpretation\n\nOhne unabhängige Lag-Variable und ohne physische Proxy-Artefakte ist weder ein unabhängiger Mechanismus noch reine Indexkonstruktion abschließend belegt.\n\n## Hypothese\n\nDie nächste Arbeit muss Eingangsartefakte anreichern.\n\n## Offene Lücke\n\nUnabhängige Lag-Variablen, Proxy-Kriterien und Proxy-Quellen fehlen.\n\n## Claim Boundary\n\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "RUN_COMMANDS_PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW01.md": f"# Run Commands\n\n```bash\nRUN_DIR=\"runs/{RUN_ID}\"\n.venv/bin/python \"$RUN_DIR/scripts/run_pbr_lag_mechanism_execution_result_review.py\" --repo-root . --run-dir \"$RUN_DIR\"\n.venv/bin/python \"$RUN_DIR/scripts/validate_pbr_lag_mechanism_execution_result_review.py\" \"$RUN_DIR\"\ngit diff --check\ngit status --short --untracked-files=all\n```\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md": f"# Summary\n\n## Befund\n\nReview-Ergebnis: `{summary['review_outcome']}`.\n\n## Interpretation\n\nStarke formale Lag-Abhängigkeit wurde beobachtet, aber unabhängige Mechanismus- und Proxy-Belege fehlen.\n\n## Hypothese\n\nInput-Artefakt-Anreicherung ist der nächste Gate.\n\n## Offene Lücke\n\nKeine unabhängige Lag-Variable und keine physische Proxy-Quelle.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_TESTS_DE.md": "# Tests Review\n\n## Befund\n\nFünf ausgeführte Tests und zwei blockierte Tests wurden reviewt.\n\n## Interpretation\n\nDie ausgeführten Tests tragen zur formalen Lag-/Ordnungsdiagnostik bei; die blockierten Tests definieren die fehlende Evidenzklasse.\n\n## Hypothese\n\nEine spätere Ausführung nach Input-Anreicherung kann die Entscheidung schärfen.\n\n## Offene Lücke\n\nIndependent-Lag- und Physical-Proxy-Inputs fehlen.\n\n## Claim Boundary\n\nKeine neue Testausführung in diesem Review.\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md": f"# Claim Boundary\n\n## Befund\n\nAlle physischen Claims bleiben gesperrt.\n\n## Interpretation\n\nDer Review bestätigt keine physische Proxy- oder Mechanismusbehauptung.\n\n## Hypothese\n\nAuch nach Input-Anreicherung bleiben physische Claims gate-pflichtig.\n\n## Offene Lücke\n\nKein physisches Gate.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md": f"# Next Gate\n\n## Befund\n\n`next_gate={NEXT_GATE}`.\n\n## Interpretation\n\nDer nächste Gate ist keine blinde Nullmodellserie, sondern Eingangsartefakt-Anreicherung.\n\n## Hypothese\n\nPrimärer nächster Lauf: `{PRIMARY_NEXT_RUN}`.\n\n## Offene Lücke\n\nProxy- und Unabhängigkeitskriterien fehlen.\n\n## Claim Boundary\n\nKeine physikalische Claim-Freigabe.\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_RESULT_REVIEW_INPUT_GAPS_DE.md": "# Input Gaps\n\n## Befund\n\nFünf Input-Gaps wurden dokumentiert: unabhängige Lag-Variable, physische Proxy-Quelle, Proxy-Unabhängigkeitskriterien, Phase-Response-Alias-Review und Source-Lineage für Kandidatenvariablen.\n\n## Interpretation\n\nDiese Gaps verhindern stärkere Entscheidungsclaims.\n\n## Hypothese\n\nEin Enrichment-Design sollte diese Artefakte zuerst definieren.\n\n## Offene Lücke\n\nKeine Artefakte wurden in diesem Review erzeugt, die die Gaps schließen.\n\n## Claim Boundary\n\nPhysische Claims bleiben gesperrt.\n",
    }
    write_csv(data_dir / "lag_mechanism_execution_review_summary.csv", [summary], list(summary.keys()))
    write_csv(data_dir / "lag_mechanism_test_review.csv", test_review, list(test_review[0].keys()))
    write_csv(data_dir / "blocked_test_review.csv", blocked_review, list(blocked_review[0].keys()))
    write_csv(data_dir / "decision_class_review.csv", decision, list(decision[0].keys()))
    write_csv(data_dir / "input_artifact_gap_analysis.csv", gap_rows, list(gap_rows[0].keys()))
    write_csv(data_dir / "claim_boundaries.csv", claims, list(claims[0].keys()))
    write_csv(data_dir / "next_gate_decision.csv", next_gate, list(next_gate[0].keys()))
    write_csv(data_dir / "recommended_next_work.csv", recommended, list(recommended[0].keys()))
    write_csv(data_dir / "input_run_lineage.csv", lineage, list(lineage[0].keys()))
    (data_dir / "review_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validation_placeholder = [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Review generated; run validator."}]
    write_csv(run_dir / "validation/validation_results.csv", validation_placeholder, list(validation_placeholder[0].keys()))
    for rel, text in docs.items():
        write_text(run_dir / rel, text)
    tables = {
        "pbr_lag_mechanism_execution_result_review_summary": (list(summary.keys()), [summary]),
        "pbr_lag_mechanism_execution_result_review_test": (list(test_review[0].keys()), test_review),
        "pbr_lag_mechanism_execution_result_review_blocked_test": (list(blocked_review[0].keys()), blocked_review),
        "pbr_lag_mechanism_execution_result_review_decision": (list(decision[0].keys()), decision),
        "pbr_lag_mechanism_execution_result_review_input_gaps": (list(gap_rows[0].keys()), gap_rows),
        "pbr_lag_mechanism_execution_result_review_claim_boundaries": (list(claims[0].keys()), claims),
        "pbr_lag_mechanism_execution_result_review_next_gate": (list(next_gate[0].keys()), next_gate),
        "pbr_lag_mechanism_execution_result_review_recommended_work": (list(recommended[0].keys()), recommended),
        "pbr_lag_mechanism_execution_result_review_lineage": (list(lineage[0].keys()), lineage),
        "pbr_lag_mechanism_execution_result_review_validation": (list(validation_placeholder[0].keys()), []),
    }
    create_sql(run_dir, tables)
    print("PBR lag mechanism execution result review created")
    print(f"run_id={RUN_ID}")
    print("review_outcome=inconclusive_requires_more_inputs_confirmed")
    print("confirmed_decision_class=inconclusive_requires_more_inputs")
    print(f"next_gate={NEXT_GATE}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
