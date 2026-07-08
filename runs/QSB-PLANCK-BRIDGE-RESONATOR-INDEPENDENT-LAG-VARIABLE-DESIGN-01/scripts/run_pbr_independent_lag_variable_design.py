#!/usr/bin/env python3
"""Generate the PBR independent-lag-variable design-only run package."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01"
SCOUT_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(line.rstrip() for line in text.strip().splitlines()) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def git_head(repo_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def git_status(repo_root: Path) -> List[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=repo_root, text=True, capture_output=True)
    return proc.stdout.splitlines()


def tsv(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def sql_type(_field: str) -> str:
    return "text"


def create_sql(run_dir: Path, tables: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in tables.items():
        cols = ",\n  ".join(f"{field} {sql_type(field)}" for field in fields)
        parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  {cols}\n);")
        parts.append("")
    parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_unabhaengige_lag_variable_design_de;")
    parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_unabhaengige_lag_variable_design_de AS
SELECT
  s.run_id AS "Lauf-ID",
  s.design_status AS "Designstatus",
  s.execution_status AS "Ausführungsstatus",
  s.input_scout_run_id AS "Quell-Scout",
  s.input_scout_decision AS "Scout-Entscheidung",
  c.criterion_key AS "Kriterium",
  c.deutscher_name AS "deutscher Kriterienname",
  a.flag_key AS "Alias-Regel",
  cl.candidate_class AS "Kandidatenklasse",
  t.test_key AS "Testdesign",
  d.decision_class AS "Entscheidungsklasse",
  d.claim_implication AS "Claim-Folge",
  s.physical_claim_release AS "physikalische Claim-Freigabe",
  s.next_gate AS "nächster Gate",
  s.secondary_next_gate AS "sekundärer Gate"
FROM {SCHEMA}.pbr_independent_lag_variable_design_summary s
LEFT JOIN {SCHEMA}.pbr_independent_lag_variable_independence_criteria c ON c.run_id = s.run_id
LEFT JOIN {SCHEMA}.pbr_independent_lag_variable_alias_rules a ON a.run_id = s.run_id
LEFT JOIN {SCHEMA}.pbr_independent_lag_variable_classification_schema cl ON cl.run_id = s.run_id
LEFT JOIN {SCHEMA}.pbr_independent_lag_variable_test_design t ON t.run_id = s.run_id
LEFT JOIN {SCHEMA}.pbr_independent_lag_variable_decision_logic d ON d.run_id = s.run_id
WHERE s.run_id = '{RUN_ID}';""")
    write_text(run_dir / "sql/001_create_qsb_pbr_independent_lag_variable_design.sql", "\n".join(parts))

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
    write_text(run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_design.sql", "\n".join(lines))
    write_text(run_dir / "sql/003_validation_queries.sql", f"""
SELECT 'design_status' AS check_name, design_status AS value
FROM {SCHEMA}.pbr_independent_lag_variable_design_summary
WHERE run_id = '{RUN_ID}';

SELECT 'criterion_count' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_independent_lag_variable_independence_criteria
WHERE run_id = '{RUN_ID}';

SELECT 'alias_rule_count' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_independent_lag_variable_alias_rules
WHERE run_id = '{RUN_ID}';

SELECT 'test_design_count' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_independent_lag_variable_test_design
WHERE run_id = '{RUN_ID}';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM {SCHEMA}.pbr_independent_lag_variable_next_gate
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
    scout_dir = repo_root / "runs" / SCOUT_RUN_ID
    scout_summary_rows = read_csv(scout_dir / "data/scout_summary.csv")
    scout_summary = scout_summary_rows[0] if scout_summary_rows else {}
    candidate_rows = read_csv(scout_dir / "data/candidate_variable_inventory.csv")
    alias_rows = read_csv(scout_dir / "data/candidate_alias_risk_assessment.csv")
    proxy_rows = read_csv(scout_dir / "data/physical_proxy_source_candidates.csv")
    gap_rows = read_csv(scout_dir / "data/input_artifact_gap_update.csv")
    scout_exists = bool(scout_summary_rows)
    scout_status = "available" if scout_exists else "missing"
    lineage_commit_status = "local_uncommitted_input_scout" if any(SCOUT_RUN_ID in line for line in status_before) else "committed_or_no_local_delta_detected"

    design_status = "independent_lag_variable_design_completed_execution_required" if scout_exists else "blocked_missing_scout_input"
    next_gate = "independent_lag_variable_admissibility_execution_required" if scout_exists else "scout_input_required"
    secondary_next_gate = "physical_proxy_source_review_required" if scout_exists else "input_scout_required"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    summary = {
        "run_id": RUN_ID,
        "run_type": "independent_lag_variable_design",
        "design_status": design_status,
        "execution_status": "design_only_not_executed",
        "claim_status": "independent_lag_variable_design_only",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "input_scout_run_id": SCOUT_RUN_ID,
        "input_scout_status": scout_status,
        "input_scout_decision": scout_summary.get("scout_decision", "blocked_missing_scout_input"),
        "input_scout_candidate_count": scout_summary.get("candidate_count", "0"),
        "input_scout_repo_artifact_match_count": scout_summary.get("repo_artifact_match_count", "0"),
        "input_scout_dwh_artifact_match_count": scout_summary.get("dwh_artifact_match_count", "0"),
        "lineage_commit_status": lineage_commit_status,
        "pre_existing_modified_files_detected": "true" if pre_existing else "false",
        "pre_existing_modified_files": "|".join(pre_existing),
        "next_gate": next_gate,
        "secondary_next_gate": secondary_next_gate,
        "no_tests_executed": "true",
        "no_nullmodels_executed": "true",
        "git_head": git_head(repo_root),
        "created_at_utc": now,
    }

    input_lineage = [{
        "run_id": RUN_ID,
        "input_scout_run_id": SCOUT_RUN_ID,
        "input_file": "data/scout_summary.csv",
        "input_status": scout_status,
        "input_scout_decision": scout_summary.get("scout_decision", "missing"),
        "candidate_count": scout_summary.get("candidate_count", "0"),
        "alias_high_count": str(sum(1 for row in alias_rows if row.get("alias_risk_level") == "high")),
        "proxy_family_count": str(len(proxy_rows)),
        "gap_count": str(len(gap_rows)),
        "lineage_commit_status": lineage_commit_status,
        "claim_implication": "input_scout_used_for_design_only_no_independence_claim",
    }]

    criteria_specs = [
        ("C01_pre_pair_existence", "Vor-Paar-Existenz", "Variable muss vor oder unabhängig von Pair-Konstruktion existieren oder Source-Lineage haben, die nicht aus pair_id, lag, |j-i| oder Kanalindexordnung abgeleitet ist.", "candidate_only_requires_execution"),
        ("C02_non_alias_derivation", "Nicht-Alias-Ableitung", "Variable darf nicht aus lag, |j-i|, pair_id, i, j, Kanalindex oder Kanalordnung berechnet sein.", "alias_if_derivation_from_forbidden_basis"),
        ("C03_independent_source_lineage", "unabhängige Source-Lineage", "Generating Run, Datei/Tabelle und Transformationsregel müssen nachvollziehbar sein.", "lineage_incomplete_blocks_admissibility"),
        ("C04_pair_mappability", "Paar-Mappbarkeit", "Variable muss auf 42 gerichtete Pair-Features mappbar sein, ohne lag selbst als Wertquelle zu benutzen; i/j-Mapping darf nur dokumentierter Schlüssel sein.", "not_pair_mappable_blocks_lag_mechanism_testing"),
        ("C05_value_variation_not_lag_determined", "nicht vollständig lag-determiniert", "Werte dürfen nicht vollständig deterministische Funktion von lag oder |lag| sein.", "deterministic_lag_function_is_alias"),
        ("C06_symmetry_directionality_check", "Richtungs-/Symmetrieprüfung", "Verhalten unter i-j-Umkehr muss dokumentiert sein; Richtung, Antirichtung, Symmetrie oder Absolutheit sind keine Unabhängigkeitsbelege.", "directionality_is_documentation_not_independence"),
        ("C07_unit_dimension_metadata", "Einheiten-/Dimensionsmetadaten", "Physikalische oder proxy-artige Variablen brauchen Einheiten-/Dimensionsmetadaten oder dokumentierte Dimensionslosigkeit.", "metadata_missing_blocks_physical_proxy_review"),
        ("C08_null_alias_stress_test_design", "Null-Alias-Stresstest", "Spätere Ausführung muss gegen lag, |lag|, pair_id, i, j und permutierte Ordnungsbaselines vergleichen.", "requires_execution_no_result_claim"),
    ]
    criteria = [{"run_id": RUN_ID, "criterion_key": k, "deutscher_name": n, "criterion_definition": d, "required_evidence": "later_execution_artifact_required", "design_status": "criteria_defined", "claim_implication": ci, "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for k, n, d, ci in criteria_specs]

    alias_specs = [
        ("exact_lag_alias", "exakter lag-Alias", "Kandidat ist identisch oder deterministisch äquivalent zu lag.", "Wertvergleich gegen lag; R2/Lookup exakt.", "no_independent_lag_variable_claim", "reject_as_alias"),
        ("absolute_lag_alias", "absoluter lag-Alias", "Kandidat ist identisch oder deterministisch äquivalent zu |lag|.", "Wertvergleich gegen |lag|; Richtung geht verloren.", "no_independent_lag_variable_claim", "reject_as_abs_lag_alias"),
        ("pair_id_lookup_alias", "pair_id-Lookup-Alias", "Kandidat wird über pair_id nachgeschlagen oder aus pair_id rekonstruiert.", "Lookup-Accuracy gegen pair_id.", "pair_presence_not_independence", "reject_or_require_source_repair"),
        ("index_order_alias", "Indexordnungs-Alias", "Kandidat folgt i, j, Kanalindex oder Kanalordnung.", "Regression/Lookup gegen i, j und Order-Baselines.", "index_surrogate_not_independence", "reject_or_scramble_test"),
        ("monotonic_lag_surrogate", "monotones lag-Surrogat", "Kandidat ist monotone Transformation von lag oder |lag|.", "Monotonie- und Rangsvergleich.", "high_alias_risk_no_confirmation", "require_information_gain_test"),
        ("piecewise_lag_surrogate", "stückweises lag-Surrogat", "Kandidat ist stückweise aus lag-Klassen ableitbar.", "Piecewise-Modelle und Residualprüfung.", "high_alias_risk_no_confirmation", "require_residual_entropy_test"),
        ("symmetry_only_alias", "reiner Symmetrie-Alias", "Kandidat trägt nur Symmetrie-/Absolutwertinformation der Pair-Ordnung.", "i-j-Reversal und Absolutwertprüfung.", "symmetry_is_not_independence", "require_directionality_review"),
        ("phase_response_abs_lag_alias", "Phase-Response-|lag|-Alias", "Wenn Phase-Response upstream als Alias von |j-i| bewertet wurde, darf sie nicht als unabhängige Lag-Variable genutzt werden, außer ein neues Quellartefakt belegt unabhängige Erzeugung und Nicht-Alias-Verhalten.", "Upstream-Aliasbefund plus neues Source-Artefakt und Nicht-Alias-Test.", "phase_response_no_independent_lag_variable_claim_without_new_source", "block_until_new_source_and_tests"),
        ("unknown_alias_risk", "unbekanntes Alias-Risiko", "Lineage oder Testlage reicht nicht zur Aliasentscheidung.", "Vollständige Lineage- und Alias-Testausführung.", "requires_review_no_confirmation", "route_to_red_team_review"),
    ]
    alias_rules = [{"run_id": RUN_ID, "flag_key": k, "deutscher_name": n, "detection_rule": d, "required_evidence": e, "claim_implication": ci, "recommended_action": a, "design_status": "criteria_defined", "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for k, n, d, e, ci, a in alias_specs]

    classes = [
        ("admissible_independent_lag_variable_candidate", "Alle Designkriterien scheinen erfüllbar; spätere Ausführung erforderlich.", "candidate_class_only_no_confirmation"),
        ("formal_independent_variable_candidate_requires_execution", "Formal plausibler Kandidat mit offener Testausführung.", "requires_execution"),
        ("physical_proxy_candidate_requires_source_review", "Proxy-artiger Kandidat mit Source-, Einheiten- und Dimensionsreview-Bedarf.", "no_physical_proxy_claim"),
        ("alias_of_abs_lag_or_lag", "Kandidat ist oder wirkt wie lag/|lag|-Alias.", "reject_for_independent_lag_gate"),
        ("alias_of_pair_id_or_index_order", "Kandidat folgt pair_id, i/j oder Kanalordnung.", "reject_or_repair_lineage"),
        ("lineage_incomplete_requires_repair", "Source-Lineage reicht nicht aus.", "repair_before_use"),
        ("not_pair_mappable", "Mapping auf 42 gerichtete Pair-Features fehlt.", "cannot_enter_lag_mechanism_test"),
        ("unit_or_dimension_missing_requires_metadata", "Einheiten-/Dimensionsmetadaten fehlen bei proxy-artigem Kandidat.", "metadata_repair_required"),
        ("excluded_not_relevant", "Nicht relevant für unabhängige Lag-Variable.", "exclude_from_gate"),
        ("unknown_requires_review", "Befund unklar.", "manual_review_required"),
    ]
    classification = [{"run_id": RUN_ID, "candidate_class": c, "class_definition": d, "allowed_status": "candidate_class_defined", "claim_implication": ci, "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for c, d, ci in classes]

    test_specs = [
        ("deterministic_alias_test", "Prüfen, ob Kandidatenwerte exakt oder nahezu exakt aus lag, |lag|, pair_id, i, j oder Indexordnung berechenbar sind.", "r2_lag|r2_abs_lag|lookup_accuracy_pair_id|lookup_accuracy_index_order|residual_entropy|alias_classification"),
        ("scramble_invariance_test", "Prüfen, ob Kandidatenwerte bei Neuordnung/Permutation der Kanalordnung unabhängig bleiben.", "scramble_count|candidate_value_preservation_rate|lag_relation_change_rate|independence_stability_score"),
        ("source_lineage_audit", "Prüfen, ob Kandidatenwerte upstream unabhängig erzeugt wurden.", "source_artifact_present|generation_rule_present|transformation_chain_complete|derived_from_lag_flag|derived_from_pair_id_flag|lineage_score"),
        ("pair_mapping_audit", "Prüfen, ob Kandidaten sauber auf die 42 gerichteten Pair-Features mappbar sind.", "pair_mapping_coverage|directed_pair_coverage|missing_pair_count|mapping_uses_lag_as_value_source|mapping_uses_pair_id_as_value_source"),
        ("information_gain_over_lag_test", "Prüfen, ob die Kandidatenvariable zusätzliche Information über lag oder |lag| hinaus trägt.", "mutual_information_candidate_lag|conditional_entropy_candidate_given_lag|residual_variance_after_lag_model|information_gain_over_lag"),
        ("directionality_consistency_test", "Prüfen, ob Richtung, Vorzeichen und i/j-Umkehr unabhängig dokumentiert sind.", "directionality_class|ij_reversal_behavior|antisymmetry_score|symmetry_score|absolute_value_risk"),
        ("unit_dimension_metadata_audit", "Prüfen, ob physikalisch/proxy-artige Kandidaten Einheit und Dimension korrekt dokumentieren.", "unit_present|dimension_vector_present|dimensionless_reason_present|conversion_rule_present|metadata_score"),
        ("candidate_admissibility_gate", "Zusammenführen aller Prüfungen zu einer Gate-Entscheidung.", "criteria_pass_count|criteria_fail_count|critical_failures|admissibility_class|allowed_next_use|claim_boundary"),
    ]
    test_design = [{"run_id": RUN_ID, "test_key": k, "purpose": p, "required_later_metrics": m, "execution_status": "not_executed_design_only", "design_status": "test_design_defined", "claim_implication": "requires_execution_no_result_claim", "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for k, p, m in test_specs]

    decision_specs = [
        ("candidate_admissible_for_lag_mechanism_testing", "All criteria pass in later execution; no critical alias flags.", "Any confirmed alias, missing lineage, missing pair mapping.", "later_lag_mechanism_testing_input_only", "admissible_for_testing_not_confirmation"),
        ("candidate_admissible_only_after_lineage_repair", "Non-alias plausible but lineage incomplete.", "No repair artifact.", "lineage_repair_then_retest", "no_independence_claim"),
        ("candidate_admissible_only_after_metadata_repair", "Proxy-like candidate missing units/dimensions.", "Metadata absent after repair window.", "metadata_repair_then_review", "no_physical_proxy_claim"),
        ("candidate_rejected_alias_of_lag", "Exact/absolute/monotonic/piecewise lag alias detected.", "None.", "exclude_from_independent_lag_gate", "alias_rejection"),
        ("candidate_rejected_alias_of_pair_or_index", "pair_id/index/order alias detected.", "None.", "exclude_from_independent_lag_gate", "alias_rejection"),
        ("candidate_rejected_not_pair_mappable", "Cannot map to 42 directed pair features.", "None.", "exclude_from_lag_mechanism_testing", "mapping_rejection"),
        ("candidate_rejected_not_independent", "Information gain and lineage do not support independence.", "None.", "exclude_from_independent_lag_gate", "no_independence_claim"),
        ("candidate_requires_red_team_review", "Conflicting tests, high correlation, or unclear alias risk.", "Review not completed.", "manual_review_before_any_use", "requires_review_no_confirmation"),
    ]
    decisions = [{"run_id": RUN_ID, "decision_class": c, "required_conditions": r, "blocking_conditions": b, "allowed_next_use": u, "claim_implication": ci, "physical_claim_release": PHYSICAL_CLAIM_RELEASE, "design_status": "test_design_defined"} for c, r, b, u, ci in decision_specs]

    source_requirements = [{"run_id": RUN_ID, "requirement_key": key, "requirement_text": text, "blocking_if_missing": "true", "claim_implication": "lineage_required_before_admissibility"} for key, text in [
        ("generating_run", "Generating Run oder Datenquelle muss eindeutig angegeben sein."),
        ("source_file_or_table", "Quell-Datei oder DWH-Tabelle muss angegeben sein."),
        ("transformation_rule", "Transformationsregel muss vollständig dokumentiert sein."),
        ("not_derived_from_forbidden_basis", "Nicht-Ableitung aus lag, |j-i|, pair_id oder Indexordnung muss belegbar sein."),
    ]]
    pair_requirements = [{"run_id": RUN_ID, "requirement_key": key, "requirement_text": text, "blocking_if_missing": "true", "claim_implication": "pair_mapping_required_before_testing"} for key, text in [
        ("directed_pair_coverage", "Coverage für 42 gerichtete Pair-Features muss messbar sein."),
        ("mapping_key_separation", "Mapping-Schlüssel darf nicht zugleich Wertquelle sein."),
        ("missing_pair_report", "Fehlende Paare müssen explizit gelistet werden."),
    ]]
    unit_requirements = [{"run_id": RUN_ID, "requirement_key": key, "requirement_text": text, "blocking_if_missing": block, "claim_implication": "metadata_required_for_proxy_review"} for key, text, block in [
        ("unit_present", "Einheit muss vorhanden sein, wenn Kandidat physikalisch/proxy-artig ist.", "true"),
        ("dimension_vector_present", "Dimensionsvektor oder dimensionslose Begründung muss vorhanden sein.", "true"),
        ("conversion_rule_present", "Konversionsregel muss dokumentiert sein, falls Werte transformiert wurden.", "true"),
        ("dimensionless_reason_present", "Dimensionslosigkeit muss begründet sein, falls keine Einheit vorliegt.", "conditional"),
    ]]
    phase_rule = [{
        "run_id": RUN_ID,
        "rule_key": "phase_response_abs_lag_alias",
        "rule_text": "Wenn Phase-Response-Werte upstream als Alias von |j-i| bewertet wurden, dürfen sie nicht als unabhängige Lag-Variablen genutzt werden, außer ein neues Quellartefakt belegt unabhängige Erzeugung und Nicht-Alias-Verhalten.",
        "upstream_basis": "input_scout_alias_risk_high_and_prior_phase_response_alias_assessment",
        "required_new_evidence": "new_source_artifact|source_lineage_audit|deterministic_alias_test|information_gain_over_lag_test",
        "claim_implication": "phase_response_no_independent_lag_variable_claim_without_new_source",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }]
    questions = [
        "Welche mathematischen Nicht-Alias-Kriterien sind für lag-dominierte Matrizen geeignet?",
        "Welche Informationsmaße eignen sich zur Trennung von Kandidatenvariable und lag/|lag|?",
        "Welche formalen Kriterien unterscheiden unabhängige Ordnungsvariablen von Indexsurrogaten?",
        "Welche Reviewer-Einwände entstehen bei Kandidatenvariablen, die hoch mit |lag| korrelieren?",
        "Welche Proxy-Kriterien sind in Moden-, Phasen-, Energie- und Impulsstrukturen methodisch zulässig?",
    ]
    dr_questions = [{"run_id": RUN_ID, "question_id": f"DRQ-{i:03d}", "handoff_question": q, "evidence_status": "question_only_no_deep_research_answer"} for i, q in enumerate(questions, 1)]
    blocked_claims = [
        "QSB is physically " + "validated", "PBR exists " + "physically", "six lag axes are " + "spacetime dimensions",
        "spacetime emergence is " + "proven", "empirical validation " + "exists", "lag classes are " + "physical dimensions",
        "lag mechanism is physically " + "proven", "candidate artifact proves " + "independent lag mechanism",
        "candidate artifact proves " + "physical proxy", "DWH presence alone proves " + "independence",
        "repo presence alone proves " + "independence", "literature note alone proves " + "proxy for current matrix",
        "phase-response values are independent " + "lag variables despite alias assessment",
        "criteria definition confirms " + "independence", "admissible candidate class releases " + "physical claim",
    ]
    claims = [{"run_id": RUN_ID, "claim_key": f"BLOCK-{i:03d}", "claim_text": claim, "status": "blocked", "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for i, claim in enumerate(blocked_claims, 1)]
    next_gate_rows = [{"run_id": RUN_ID, "next_gate": next_gate, "secondary_next_gate": secondary_next_gate, "execution_authorization": "not_authorized_in_this_design_run", "physical_claim_release": PHYSICAL_CLAIM_RELEASE}]
    validation_placeholder = [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Design package generated; run validator."}]
    manifest = {
        "run_id": RUN_ID,
        "target_run_id_verified": RUN_ID,
        "run_type": "independent_lag_variable_design",
        "design_only": True,
        "no_tests_executed": True,
        "no_nullmodels_executed": True,
        "input_scout_run_id": SCOUT_RUN_ID,
        "input_scout_status": scout_status,
        "lineage_commit_status": lineage_commit_status,
        "required_candidate_classes": [row["candidate_class"] for row in classification],
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }

    data_dir = run_dir / "data"
    write_csv(data_dir / "design_summary.csv", [summary], list(summary.keys()))
    write_csv(data_dir / "input_scout_lineage.csv", input_lineage, list(input_lineage[0].keys()))
    write_csv(data_dir / "independence_criteria.csv", criteria, list(criteria[0].keys()))
    write_csv(data_dir / "alias_detection_rules.csv", alias_rules, list(alias_rules[0].keys()))
    write_csv(data_dir / "candidate_classification_schema.csv", classification, list(classification[0].keys()))
    write_csv(data_dir / "test_design_spec.csv", test_design, list(test_design[0].keys()))
    write_csv(data_dir / "later_execution_decision_logic.csv", decisions, list(decisions[0].keys()))
    write_csv(data_dir / "source_lineage_requirements.csv", source_requirements, list(source_requirements[0].keys()))
    write_csv(data_dir / "pair_mapping_requirements.csv", pair_requirements, list(pair_requirements[0].keys()))
    write_csv(data_dir / "unit_dimension_requirements.csv", unit_requirements, list(unit_requirements[0].keys()))
    write_csv(data_dir / "phase_response_special_rule.csv", phase_rule, list(phase_rule[0].keys()))
    write_csv(data_dir / "deep_research_handoff_questions.csv", dr_questions, list(dr_questions[0].keys()))
    write_csv(data_dir / "claim_boundaries.csv", claims, list(claims[0].keys()))
    write_csv(data_dir / "next_gate_decision.csv", next_gate_rows, list(next_gate_rows[0].keys()))
    write_text(data_dir / "design_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
    write_csv(run_dir / "validation/validation_results.csv", validation_placeholder, list(validation_placeholder[0].keys()))

    docs = {
        "README.md": f"# {RUN_ID}\n\nDesign-only Run zur Definition von Kriterien für unabhängige Lag-Variablen.\n\nNo tests were executed.\nNo nullmodels were executed.\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        f"{RUN_ID}.md": f"# {RUN_ID}\n\n## Befund\n\nDer Run definiert Kriterien, Alias-Regeln, Klassifikationsschema, spätere Testdesigns und Entscheidungslogik. Designstatus: `{design_status}`.\n\n## Interpretation\n\nDie Definitionen strukturieren den nächsten Gate; sie bestätigen keine Kandidatenvariable.\n\n## Hypothese\n\nSpätere Ausführungen können Kandidaten anhand dieser Kriterien prüfen.\n\n## Offene Lücke\n\nAusführung, Source-Lineage-Prüfung und Alias-Stresstests stehen aus.\n\n## Claim Boundary\n\nNo physical claims are released. `physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "RUN_COMMANDS_PBR_INDEPENDENT_LAG_VARIABLE_DESIGN01.md": f"# Run Commands\n\n```bash\nRUN_DIR=\"runs/{RUN_ID}\"\n.venv/bin/python \"$RUN_DIR/scripts/run_pbr_independent_lag_variable_design.py\" --repo-root . --run-dir \"$RUN_DIR\" --database qsb_research_dwh\n.venv/bin/python \"$RUN_DIR/scripts/validate_pbr_independent_lag_variable_design.py\" \"$RUN_DIR\"\ngit diff --check\ngit status --short --untracked-files=all\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/001_create_qsb_pbr_independent_lag_variable_design.sql\"\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/002_insert_qsb_pbr_independent_lag_variable_design.sql\"\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/003_validation_queries.sql\"\n```\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_SUMMARY_DE.md": f"# Design Summary\n\n## Befund\n\nDer Design-Run ist abgeschlossen, Ausführung bleibt erforderlich.\n\n## Interpretation\n\nDer Scout-Befund `{summary['input_scout_decision']}` begründet Kriterienarbeit, keine Bestätigung.\n\n## Hypothese\n\nNicht-Alias-, Lineage- und Pair-Mapping-Prüfungen können den nächsten Gate strukturieren.\n\n## Offene Lücke\n\nKeine Kandidatenprüfung wurde ausgeführt.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_CRITERIA_DE.md": "# Kriterien\n\n## Befund\n\nAcht Kriterien wurden definiert: Vor-Paar-Existenz, Nicht-Alias-Ableitung, Source-Lineage, Paar-Mappbarkeit, nicht lag-determinierte Variation, Richtungsprüfung, Metadaten und Null-Alias-Stresstest.\n\n## Interpretation\n\nDie Kriterien sind Designvorgaben.\n\n## Hypothese\n\nSie können spätere Admissibility-Ausführungen steuern.\n\n## Offene Lücke\n\nKandidatenwerte wurden nicht geprüft.\n\n## Claim Boundary\n\nKriterien bestätigen keine Unabhängigkeit.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_ALIAS_RULES_DE.md": "# Alias-Regeln\n\n## Befund\n\nNeun Alias-Flags wurden definiert, einschließlich `phase_response_abs_lag_alias`.\n\n## Interpretation\n\nAlias-Regeln blockieren voreilige Unabhängigkeitsclaims.\n\n## Hypothese\n\nDeterministische und informationstheoretische Tests können Aliasrisiken trennen.\n\n## Offene Lücke\n\nTests sind nur entworfen, nicht ausgeführt.\n\n## Claim Boundary\n\nKein Mechanismusclaim.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_TESTS_DE.md": "# Testdesigns\n\n## Befund\n\nAcht spätere Testdesigns wurden definiert.\n\n## Interpretation\n\nDiese Designs sind Ausführungspläne, keine Ergebnisse.\n\n## Hypothese\n\nGemeinsam prüfen sie Alias, Scramble-Stabilität, Lineage, Mapping, Informationsgewinn, Richtung und Metadaten.\n\n## Offene Lücke\n\nAusführung steht aus.\n\n## Claim Boundary\n\nKeine Bestätigung in diesem Run.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_NEXT_GATE_DE.md": f"# Next Gate\n\n## Befund\n\n`next_gate={next_gate}`.\n\n## Interpretation\n\nDer nächste Gate verlangt Admissibility-Ausführung.\n\n## Hypothese\n\nEin separater Execution-Run kann die Designlogik anwenden.\n\n## Offene Lücke\n\nKeine Execution-Autorisierung in diesem Run.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_DESIGN_CLAIM_BOUNDARY_DE.md": "# Claim Boundary\n\n## Befund\n\nAlle physikalischen und Bestätigungsclaims sind geblockt.\n\n## Interpretation\n\nDesignklassen sind keine Bestätigung.\n\n## Hypothese\n\nEine spätere Prüfung kann Kandidaten für Tests zulassen, ohne physikalische Claims freizugeben.\n\n## Offene Lücke\n\nPhysikalische Proxy-Reviews sind separat erforderlich.\n\n## Claim Boundary\n\nNo physical claims are released.\n",
    }
    for rel, text in docs.items():
        write_text(run_dir / rel, text)

    tables = {
        "pbr_independent_lag_variable_design_summary": (list(summary.keys()), [summary]),
        "pbr_independent_lag_variable_input_scout_lineage": (list(input_lineage[0].keys()), input_lineage),
        "pbr_independent_lag_variable_independence_criteria": (list(criteria[0].keys()), criteria),
        "pbr_independent_lag_variable_alias_rules": (list(alias_rules[0].keys()), alias_rules),
        "pbr_independent_lag_variable_classification_schema": (list(classification[0].keys()), classification),
        "pbr_independent_lag_variable_test_design": (list(test_design[0].keys()), test_design),
        "pbr_independent_lag_variable_decision_logic": (list(decisions[0].keys()), decisions),
        "pbr_independent_lag_variable_source_lineage_requirements": (list(source_requirements[0].keys()), source_requirements),
        "pbr_independent_lag_variable_pair_mapping_requirements": (list(pair_requirements[0].keys()), pair_requirements),
        "pbr_independent_lag_variable_unit_dimension_requirements": (list(unit_requirements[0].keys()), unit_requirements),
        "pbr_independent_lag_variable_phase_response_rule": (list(phase_rule[0].keys()), phase_rule),
        "pbr_independent_lag_variable_deep_research_handoff": (list(dr_questions[0].keys()), dr_questions),
        "pbr_independent_lag_variable_claim_boundaries": (list(claims[0].keys()), claims),
        "pbr_independent_lag_variable_next_gate": (list(next_gate_rows[0].keys()), next_gate_rows),
        "pbr_independent_lag_variable_validation": (list(validation_placeholder[0].keys()), []),
    }
    create_sql(run_dir, tables)
    print(f"target_run_id={RUN_ID}")
    print(f"design_status={design_status}")
    print(f"input_scout_status={scout_status}")
    print(f"criteria_count={len(criteria)}")
    print(f"alias_rule_count={len(alias_rules)}")
    print(f"test_design_count={len(test_design)}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
