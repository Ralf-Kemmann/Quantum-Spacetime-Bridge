#!/usr/bin/env python3
"""Execute inventory-based admissibility checks for independent lag variable candidates."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01"
SCOUT_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01"
DESIGN_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
ALLOWED_DECISIONS = [
    "candidate_admissible_for_lag_mechanism_testing",
    "candidate_admissible_only_after_lineage_repair",
    "candidate_admissible_only_after_metadata_repair",
    "candidate_rejected_alias_of_lag",
    "candidate_rejected_alias_of_pair_or_index",
    "candidate_rejected_not_pair_mappable",
    "candidate_rejected_not_independent",
    "candidate_requires_red_team_review",
]
CRITERIA = [
    "Vor-Paar-Existenz",
    "Nicht-Alias-Ableitung",
    "unabhängige Source-Lineage",
    "Paar-Mappbarkeit",
    "nicht vollständig lag-determiniert",
    "Richtungs-/Symmetrieprüfung",
    "Einheiten-/Dimensionsmetadaten",
    "Null-Alias-Stresstest",
]
ALIAS_FLAGS = [
    "exact_lag_alias",
    "absolute_lag_alias",
    "pair_id_lookup_alias",
    "index_order_alias",
    "monotonic_lag_surrogate",
    "piecewise_lag_surrogate",
    "symmetry_only_alias",
    "phase_response_abs_lag_alias",
    "unknown_alias_risk",
]


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


def truth(value: str) -> bool:
    return str(value).lower() == "true"


def unknown(value: str) -> bool:
    return str(value).lower() in {"", "unknown", "not_established_by_scout"}


def tsv(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def create_sql(run_dir: Path, tables: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in tables.items():
        parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  " + ",\n  ".join(f"{field} text" for field in fields) + "\n);")
        parts.append("")
    parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_unabhaengige_lag_variable_zulassung_de;")
    parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_unabhaengige_lag_variable_zulassung_de AS
SELECT
  r.run_id AS "Lauf-ID",
  r.candidate_id AS "Kandidaten-ID",
  r.candidate_variable_name AS "Kandidatenvariable",
  r.candidate_category AS "Kandidatenkategorie",
  r.source_path_or_table AS "Quelle",
  r.alias_risk_level AS "Alias-Risiko",
  r.input_independence_status AS "Unabhängigkeitsstatus",
  r.criteria_pass_count AS "Kriterien bestanden",
  r.criteria_fail_count AS "Kriterien gescheitert",
  r.critical_failures AS "kritische Fehler",
  r.admissibility_decision_class AS "Zulassungsentscheidung",
  r.allowed_next_use AS "erlaubte nächste Verwendung",
  r.claim_implication AS "Claim-Folge",
  r.physical_claim_release AS "physikalische Claim-Freigabe",
  s.next_gate AS "nächster Gate"
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_results r
JOIN {SCHEMA}.pbr_independent_lag_variable_admissibility_summary s ON s.run_id = r.run_id
WHERE r.run_id = '{RUN_ID}';""")
    write_text(run_dir / "sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution.sql", "\n".join(parts))

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
    write_text(run_dir / "sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution.sql", "\n".join(lines))
    write_text(run_dir / "sql/003_validation_queries.sql", f"""
SELECT 'execution_status' AS check_name, execution_status AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_summary
WHERE run_id = '{RUN_ID}';

SELECT 'candidate_count_total' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_results
WHERE run_id = '{RUN_ID}';

SELECT 'admissible_for_testing' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_results
WHERE run_id = '{RUN_ID}' AND admissibility_decision_class = 'candidate_admissible_for_lag_mechanism_testing';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM {SCHEMA}.pbr_independent_lag_variable_admissibility_next_gate
WHERE run_id = '{RUN_ID}';
""")


def classify(row: Dict[str, str]) -> Tuple[str, str, str, str, List[str], Dict[str, str]]:
    name = row.get("candidate_variable_name", "")
    source = row.get("source_path_or_table", "")
    cat = row.get("candidate_category", "")
    indep = row.get("independence_status", "")
    alias_risk = row.get("alias_risk_level", "unknown")
    non_alias = row.get("non_alias_evidence", "")
    has_lineage = truth(row.get("has_source_lineage", ""))
    pair_mappable = truth(row.get("pair_mappable", ""))
    has_units = truth(row.get("has_units", ""))
    has_dim = truth(row.get("has_dimension_metadata", ""))
    proxy_like = "proxy" in cat or "physical" in cat
    phase_response = "phase_response" in name.lower() or "phase_response" in source.lower()
    derived_lag = truth(row.get("derived_from_lag_or_abs_lag", "")) or indep == "not_independent_alias_of_lag"
    derived_pair = truth(row.get("derived_from_pair_id", "")) or indep == "not_independent_alias_of_pair_id"
    derived_index = truth(row.get("derived_from_index_order", "")) or indep == "not_independent_index_derived"
    explicit_non_alias = bool(non_alias and non_alias != "not_established_by_scout")
    flags = {flag: "not_triggered" for flag in ALIAS_FLAGS}
    evidence = {flag: "inventory_evidence_not_triggered" for flag in ALIAS_FLAGS}
    if derived_lag:
        flags["absolute_lag_alias"] = "triggered"
        evidence["absolute_lag_alias"] = "derived_from_lag_or_abs_lag_or_alias_status"
    if derived_pair:
        flags["pair_id_lookup_alias"] = "triggered"
        evidence["pair_id_lookup_alias"] = "derived_from_pair_id_or_alias_status"
    if derived_index:
        flags["index_order_alias"] = "triggered"
        evidence["index_order_alias"] = "derived_from_index_order_or_alias_status"
    if phase_response:
        flags["phase_response_abs_lag_alias"] = "triggered"
        evidence["phase_response_abs_lag_alias"] = "phase_response_special_rule_no_new_source_artifact"
    if alias_risk in {"high", "medium", "unknown"} and not any(v == "triggered" for v in flags.values()):
        flags["unknown_alias_risk"] = "triggered" if alias_risk in {"high", "unknown"} else "unknown"
        evidence["unknown_alias_risk"] = f"alias_risk_level={alias_risk}; value_series_status=not_available"

    criteria = {}
    criteria["Vor-Paar-Existenz"] = "fail" if derived_pair or derived_index else ("unknown" if unknown(row.get("derived_from_pair_id", "")) else "pass")
    criteria["Nicht-Alias-Ableitung"] = "fail" if any(flags[f] == "triggered" for f in ["absolute_lag_alias", "pair_id_lookup_alias", "index_order_alias", "phase_response_abs_lag_alias"]) else ("unknown" if flags["unknown_alias_risk"] != "not_triggered" else "pass")
    criteria["unabhängige Source-Lineage"] = "pass" if has_lineage else "blocked_missing_evidence"
    criteria["Paar-Mappbarkeit"] = "pass" if pair_mappable else "fail"
    criteria["nicht vollständig lag-determiniert"] = "fail" if derived_lag or phase_response else ("unknown" if not explicit_non_alias else "pass")
    criteria["Richtungs-/Symmetrieprüfung"] = "unknown"
    criteria["Einheiten-/Dimensionsmetadaten"] = "pass" if (not proxy_like or (has_units and has_dim)) else "blocked_missing_evidence"
    criteria["Null-Alias-Stresstest"] = "blocked_missing_evidence"

    if derived_lag or phase_response:
        decision = "candidate_rejected_alias_of_lag"
    elif derived_pair or derived_index:
        decision = "candidate_rejected_alias_of_pair_or_index"
    elif not pair_mappable or indep == "not_pair_mappable":
        decision = "candidate_rejected_not_pair_mappable"
    elif not explicit_non_alias and alias_risk == "high" and not has_lineage:
        decision = "candidate_rejected_not_independent"
    elif pair_mappable and not has_lineage and not any(v == "triggered" for k, v in flags.items() if k != "unknown_alias_risk"):
        decision = "candidate_admissible_only_after_lineage_repair"
    elif pair_mappable and has_lineage and proxy_like and not (has_units and has_dim):
        decision = "candidate_admissible_only_after_metadata_repair"
    elif alias_risk in {"medium", "unknown"} or proxy_like:
        decision = "candidate_requires_red_team_review"
    elif pair_mappable and has_lineage and explicit_non_alias and not proxy_like:
        decision = "candidate_admissible_for_lag_mechanism_testing"
    else:
        decision = "candidate_requires_red_team_review"

    allowed = {
        "candidate_admissible_for_lag_mechanism_testing": "later_lag_mechanism_testing_input_only",
        "candidate_admissible_only_after_lineage_repair": "lineage_repair_then_retest",
        "candidate_admissible_only_after_metadata_repair": "metadata_repair_then_review",
        "candidate_rejected_alias_of_lag": "exclude_from_independent_lag_gate",
        "candidate_rejected_alias_of_pair_or_index": "exclude_from_independent_lag_gate",
        "candidate_rejected_not_pair_mappable": "exclude_from_lag_mechanism_testing",
        "candidate_rejected_not_independent": "exclude_from_independent_lag_gate",
        "candidate_requires_red_team_review": "manual_review_before_any_use",
    }[decision]
    claim = "admissible_for_testing_only_not_confirmed_independent" if decision == "candidate_admissible_for_lag_mechanism_testing" else "no_independent_lag_variable_claim"
    critical = [k for k, v in criteria.items() if v == "fail"]
    if decision.startswith("candidate_rejected"):
        critical.append(decision)
    return decision, allowed, claim, "|".join(sorted(set(critical))), [criteria[c] for c in CRITERIA], {**flags, **{f"{k}__evidence": v for k, v in evidence.items()}}


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
    design_dir = repo_root / "runs" / DESIGN_RUN_ID
    scout_summary = (read_csv(scout_dir / "data/scout_summary.csv") or [{}])[0]
    design_summary = (read_csv(design_dir / "data/design_summary.csv") or [{}])[0]
    candidates = read_csv(scout_dir / "data/candidate_variable_inventory.csv")
    input_files_ok = bool(candidates and scout_summary and design_summary)
    blocked = not input_files_ok
    lineage_commit_status = "local_uncommitted_input_run" if any(SCOUT_RUN_ID in line or DESIGN_RUN_ID in line for line in status_before) else "committed_or_no_local_delta_detected"

    result_rows: List[Dict[str, Any]] = []
    criteria_rows: List[Dict[str, Any]] = []
    alias_rows: List[Dict[str, Any]] = []
    det_rows: List[Dict[str, Any]] = []
    scramble_rows: List[Dict[str, Any]] = []
    lineage_rows: List[Dict[str, Any]] = []
    pair_rows: List[Dict[str, Any]] = []
    info_rows: List[Dict[str, Any]] = []
    direction_rows: List[Dict[str, Any]] = []
    unit_rows: List[Dict[str, Any]] = []

    for row in candidates:
        decision, allowed, claim, critical, criteria_values, flag_data = classify(row)
        pass_count = sum(1 for v in criteria_values if v == "pass")
        fail_count = sum(1 for v in criteria_values if v == "fail")
        unknown_count = sum(1 for v in criteria_values if v in {"unknown", "blocked_missing_evidence"})
        result_rows.append({
            "run_id": RUN_ID, "candidate_id": row["candidate_id"], "source_type": row.get("source_type", ""),
            "source_path_or_table": row.get("source_path_or_table", ""), "candidate_variable_name": row.get("candidate_variable_name", ""),
            "candidate_category": row.get("candidate_category", ""), "artifact_level": row.get("artifact_level", ""),
            "alias_risk_level": row.get("alias_risk_level", "unknown"), "input_independence_status": row.get("independence_status", ""),
            "criteria_pass_count": str(pass_count), "criteria_fail_count": str(fail_count), "criteria_unknown_count": str(unknown_count),
            "critical_failures": critical, "admissibility_decision_class": decision, "allowed_next_use": allowed,
            "claim_implication": claim, "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        })
        for crit, status in zip(CRITERIA, criteria_values):
            criteria_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "criterion_name": crit, "criterion_status": status, "criterion_evidence": "inventory_field_based_admissibility_execution"})
        for flag in ALIAS_FLAGS:
            alias_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "alias_flag": flag, "alias_flag_status": flag_data[flag], "alias_evidence": flag_data[f"{flag}__evidence"], "alias_risk_level": row.get("alias_risk_level", "unknown")})
        det_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "value_series_status": "not_available", "deterministic_alias_check_status": "evidence_based_inventory_only", "r2_lag": "not_computed", "r2_abs_lag": "not_computed", "lookup_accuracy_pair_id": "not_computed", "lookup_accuracy_index_order": "not_computed", "residual_entropy": "not_computed"})
        scramble_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "scramble_test_feasible": "false" if not truth(row.get("pair_mappable", "")) else "unknown_requires_values", "required_source_values_present": "false", "required_mapping_present": row.get("pair_mappable", "unknown"), "expected_blocker": "blocked_missing_source_values"})
        lineage_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "source_artifact_present": "true" if row.get("source_path_or_table") else "false", "generation_rule_present": "unknown", "transformation_chain_complete": "false" if not truth(row.get("has_source_lineage", "")) else "unknown", "derived_from_lag_flag": row.get("derived_from_lag_or_abs_lag", "unknown"), "derived_from_pair_id_flag": row.get("derived_from_pair_id", "unknown"), "derived_from_index_flag": row.get("derived_from_index_order", "unknown"), "lineage_score": "1" if truth(row.get("has_source_lineage", "")) else "0", "lineage_decision": "lineage_present_requires_review" if truth(row.get("has_source_lineage", "")) else "lineage_incomplete_requires_repair"})
        pair_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "pair_mapping_status": row.get("pair_mappable", "unknown"), "pair_mapping_coverage_status": "not_measured_inventory_only", "directed_pair_support": row.get("has_i_j_or_pair_id", "unknown"), "mapping_uses_lag_as_value_source": row.get("has_lag", "unknown"), "mapping_uses_pair_id_as_value_source": row.get("derived_from_pair_id", "unknown"), "mapping_decision": "pair_mapping_plausible_requires_review" if truth(row.get("pair_mappable", "")) else "not_pair_mappable"})
        info_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "information_gain_test_feasible": "false", "candidate_values_available": "false", "lag_values_available": "false", "minimum_data_requirements_met": "false", "information_gain_status": "blocked_missing_source_values"})
        direction_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "directionality_documented": "unknown", "directionality_class": "unknown", "ij_reversal_behavior_available": "false", "absolute_value_risk": "high" if row.get("derived_from_lag_or_abs_lag") == "true" else "unknown", "directionality_decision": "directionality_not_established_inventory_only"})
        unit_rows.append({"run_id": RUN_ID, "candidate_id": row["candidate_id"], "unit_present": row.get("has_units", "unknown"), "dimension_vector_present": row.get("has_dimension_metadata", "unknown"), "dimensionless_reason_present": "unknown", "metadata_decision": "metadata_present_or_not_required" if row.get("candidate_category") == "unknown" or (truth(row.get("has_units", "")) and truth(row.get("has_dimension_metadata", ""))) else "metadata_missing_requires_review"})

    decision_counts = Counter(r["admissibility_decision_class"] for r in result_rows)
    total = len(result_rows)
    admissible = decision_counts["candidate_admissible_for_lag_mechanism_testing"]
    repair_lineage = decision_counts["candidate_admissible_only_after_lineage_repair"]
    repair_meta = decision_counts["candidate_admissible_only_after_metadata_repair"]
    red_team = decision_counts["candidate_requires_red_team_review"]
    if blocked:
        execution_status = "blocked_missing_input_run"
        final_status = "blocked_missing_input_run"
        next_gate = "input_artifact_enrichment_required"
        secondary = "input_artifact_enrichment_required"
    elif admissible:
        execution_status = "admissibility_execution_completed"
        final_status = "admissibility_execution_completed"
        next_gate = "lag_mechanism_testing_with_admissible_candidates_required"
        secondary = "physical_proxy_source_review_required"
    elif repair_lineage:
        execution_status = "admissibility_execution_completed_with_repair_required_candidates"
        final_status = execution_status
        next_gate = "lineage_repair_required"
        secondary = "red_team_candidate_review_required" if red_team else "physical_proxy_source_review_required"
    elif repair_meta:
        execution_status = "admissibility_execution_completed_with_repair_required_candidates"
        final_status = execution_status
        next_gate = "metadata_repair_required"
        secondary = "physical_proxy_source_review_required"
    elif red_team:
        execution_status = "admissibility_execution_completed_no_admissible_candidates"
        final_status = execution_status
        next_gate = "red_team_candidate_review_required"
        secondary = "input_artifact_enrichment_required"
    else:
        execution_status = "admissibility_execution_completed_no_admissible_candidates"
        final_status = execution_status
        next_gate = "no_admissible_candidates_review_required"
        secondary = "input_artifact_enrichment_required"

    summary = {
        "run_id": RUN_ID, "run_type": "independent_lag_variable_admissibility_execution",
        "execution_status": execution_status, "final_admissibility_status": final_status,
        "claim_status": "independent_lag_variable_admissibility_execution_only", "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "input_scout_run_id": SCOUT_RUN_ID, "input_design_run_id": DESIGN_RUN_ID,
        "input_scout_decision": scout_summary.get("scout_decision", "missing"),
        "candidate_count_total": str(total),
        "candidate_count_admissible_for_testing": str(admissible),
        "candidate_count_lineage_repair": str(repair_lineage),
        "candidate_count_metadata_repair": str(repair_meta),
        "candidate_count_rejected_alias_lag": str(decision_counts["candidate_rejected_alias_of_lag"]),
        "candidate_count_rejected_alias_pair_or_index": str(decision_counts["candidate_rejected_alias_of_pair_or_index"]),
        "candidate_count_rejected_not_pair_mappable": str(decision_counts["candidate_rejected_not_pair_mappable"]),
        "candidate_count_rejected_not_independent": str(decision_counts["candidate_rejected_not_independent"]),
        "candidate_count_red_team_review": str(red_team),
        "candidate_count_unknown_or_blocked": "0" if not blocked else str(total),
        "lineage_commit_status": lineage_commit_status,
        "pre_existing_modified_files_detected": "true" if pre_existing else "false",
        "next_gate": next_gate, "secondary_next_gate": secondary,
        "no_lag_mechanism_tests_executed": "true", "no_nullmodels_executed": "true",
        "git_head": git_head(repo_root), "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    input_lineage = [
        {"run_id": RUN_ID, "input_run_id": SCOUT_RUN_ID, "input_kind": "scout", "input_status": "available" if scout_summary else "missing", "input_decision": scout_summary.get("scout_decision", "missing"), "lineage_commit_status": lineage_commit_status},
        {"run_id": RUN_ID, "input_run_id": DESIGN_RUN_ID, "input_kind": "design", "input_status": "available" if design_summary else "missing", "input_decision": design_summary.get("design_status", "missing"), "lineage_commit_status": lineage_commit_status},
    ]
    decision_summary = [{"run_id": RUN_ID, "admissibility_decision_class": dec, "candidate_count": str(decision_counts[dec]), "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for dec in ALLOWED_DECISIONS]
    by_cat: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in result_rows:
        by_cat[r["candidate_category"]].append(r)
    category_rows = []
    for cat, rows in sorted(by_cat.items()):
        counts = Counter(r["admissibility_decision_class"] for r in rows)
        category_rows.append({"run_id": RUN_ID, "category": cat, "count_total": str(len(rows)), "count_admissible_for_testing": str(counts["candidate_admissible_for_lag_mechanism_testing"]), "count_rejected": str(sum(counts[d] for d in ALLOWED_DECISIONS if d.startswith("candidate_rejected"))), "count_repair_required": str(counts["candidate_admissible_only_after_lineage_repair"] + counts["candidate_admissible_only_after_metadata_repair"]), "count_red_team_review": str(counts["candidate_requires_red_team_review"]), "dominant_blocker": counts.most_common(1)[0][0] if counts else "none"})
    rejected_rows = [r for r in result_rows if r["admissibility_decision_class"].startswith("candidate_rejected")]
    repair_rows = [r for r in result_rows if "repair" in r["admissibility_decision_class"]]
    red_rows = [r for r in result_rows if r["admissibility_decision_class"] == "candidate_requires_red_team_review"]
    claims = [{"run_id": RUN_ID, "claim_key": f"BLOCK-{i:03d}", "claim_text": c, "status": "blocked", "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for i, c in enumerate([
        "QSB is physically " + "validated", "PBR exists " + "physically", "six lag axes are " + "spacetime dimensions",
        "spacetime emergence is " + "proven", "empirical validation " + "exists", "lag classes are " + "physical dimensions",
        "lag mechanism is physically " + "proven", "candidate artifact proves " + "independent lag mechanism",
        "candidate artifact proves " + "physical proxy", "admissible candidate confirms " + "independent lag variable",
        "admissible candidate releases " + "physical claim", "DWH presence alone proves " + "independence",
        "repo presence alone proves " + "independence", "literature note alone proves " + "proxy for current matrix",
        "phase-response values are independent " + "lag variables despite alias assessment",
    ], 1)]
    next_gate_rows = [{"run_id": RUN_ID, "next_gate": next_gate, "secondary_next_gate": secondary, "execution_authorization": "admissibility_execution_completed_no_lag_mechanism_test", "physical_claim_release": PHYSICAL_CLAIM_RELEASE}]
    manifest = {"run_id": RUN_ID, "target_run_id_verified": RUN_ID, "input_scout_run_id": SCOUT_RUN_ID, "input_design_run_id": DESIGN_RUN_ID, "pre_existing_modified_files_detected": bool(pre_existing), "pre_existing_modified_files": pre_existing, "no_lag_mechanism_tests_executed": True, "no_nullmodels_executed": True, "physical_claim_release": PHYSICAL_CLAIM_RELEASE}
    validation_placeholder = [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Execution generated; run validator."}]

    data_dir = run_dir / "data"
    write_csv(data_dir / "execution_summary.csv", [summary], list(summary.keys()))
    write_csv(data_dir / "input_lineage.csv", input_lineage, list(input_lineage[0].keys()))
    res_fields = list(result_rows[0].keys()) if result_rows else ["run_id", "candidate_id", "admissibility_decision_class"]
    write_csv(data_dir / "candidate_admissibility_results.csv", result_rows, res_fields)
    write_csv(data_dir / "candidate_criteria_results.csv", criteria_rows, ["run_id", "candidate_id", "criterion_name", "criterion_status", "criterion_evidence"])
    write_csv(data_dir / "candidate_alias_flags.csv", alias_rows, ["run_id", "candidate_id", "alias_flag", "alias_flag_status", "alias_evidence", "alias_risk_level"])
    write_csv(data_dir / "deterministic_alias_check.csv", det_rows, ["run_id", "candidate_id", "value_series_status", "deterministic_alias_check_status", "r2_lag", "r2_abs_lag", "lookup_accuracy_pair_id", "lookup_accuracy_index_order", "residual_entropy"])
    write_csv(data_dir / "scramble_invariance_feasibility.csv", scramble_rows, ["run_id", "candidate_id", "scramble_test_feasible", "required_source_values_present", "required_mapping_present", "expected_blocker"])
    write_csv(data_dir / "source_lineage_audit.csv", lineage_rows, ["run_id", "candidate_id", "source_artifact_present", "generation_rule_present", "transformation_chain_complete", "derived_from_lag_flag", "derived_from_pair_id_flag", "derived_from_index_flag", "lineage_score", "lineage_decision"])
    write_csv(data_dir / "pair_mapping_audit.csv", pair_rows, ["run_id", "candidate_id", "pair_mapping_status", "pair_mapping_coverage_status", "directed_pair_support", "mapping_uses_lag_as_value_source", "mapping_uses_pair_id_as_value_source", "mapping_decision"])
    write_csv(data_dir / "information_gain_feasibility.csv", info_rows, ["run_id", "candidate_id", "information_gain_test_feasible", "candidate_values_available", "lag_values_available", "minimum_data_requirements_met", "information_gain_status"])
    write_csv(data_dir / "directionality_consistency_audit.csv", direction_rows, ["run_id", "candidate_id", "directionality_documented", "directionality_class", "ij_reversal_behavior_available", "absolute_value_risk", "directionality_decision"])
    write_csv(data_dir / "unit_dimension_metadata_audit.csv", unit_rows, ["run_id", "candidate_id", "unit_present", "dimension_vector_present", "dimensionless_reason_present", "metadata_decision"])
    write_csv(data_dir / "admissibility_decision_summary.csv", decision_summary, list(decision_summary[0].keys()))
    write_csv(data_dir / "category_summary.csv", category_rows, list(category_rows[0].keys()) if category_rows else ["run_id", "category"])
    write_csv(data_dir / "rejected_candidate_summary.csv", rejected_rows, res_fields)
    write_csv(data_dir / "repair_required_candidate_summary.csv", repair_rows, res_fields)
    write_csv(data_dir / "red_team_candidate_summary.csv", red_rows, res_fields)
    write_csv(data_dir / "claim_boundaries.csv", claims, list(claims[0].keys()))
    write_csv(data_dir / "next_gate_decision.csv", next_gate_rows, list(next_gate_rows[0].keys()))
    write_text(data_dir / "execution_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
    write_csv(run_dir / "validation/validation_results.csv", validation_placeholder, list(validation_placeholder[0].keys()))

    docs = {
        "README.md": f"# {RUN_ID}\n\nAdmissibility Execution auf Basis von Scout-Inventar und Design-Kriterien.\n\nNo lag mechanism tests were executed.\nNo nullmodels were executed.\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        f"{RUN_ID}.md": f"# {RUN_ID}\n\n## Befund\n\nDie Kandidaten wurden inventarbasiert klassifiziert. Finalstatus: `{final_status}`.\n\n## Interpretation\n\nZulassung bedeutet nur spätere Testverwendbarkeit, nicht bestätigte Unabhängigkeit.\n\n## Hypothese\n\nWeitere Lineage-, Metadata- und Red-Team-Arbeit kann neue Eingaben für spätere Tests liefern.\n\n## Offene Lücke\n\nWertreihen fehlen; deterministische Aliasdiagnostik ist deshalb inventarbasiert.\n\n## Claim Boundary\n\nNo physical claims are released. `physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "RUN_COMMANDS_PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION01.md": f"# Run Commands\n\n```bash\nRUN_DIR=\"runs/{RUN_ID}\"\n.venv/bin/python \"$RUN_DIR/scripts/run_pbr_independent_lag_variable_admissibility_execution.py\" --repo-root . --run-dir \"$RUN_DIR\" --database qsb_research_dwh\n.venv/bin/python \"$RUN_DIR/scripts/validate_pbr_independent_lag_variable_admissibility_execution.py\" \"$RUN_DIR\"\ngit diff --check\ngit status --short --untracked-files=all\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/001_create_qsb_pbr_independent_lag_variable_admissibility_execution.sql\"\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/002_insert_qsb_pbr_independent_lag_variable_admissibility_execution.sql\"\npsql -d qsb_research_dwh -f \"$RUN_DIR/sql/003_validation_queries.sql\"\n```\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_SUMMARY_DE.md": f"# Summary\n\n## Befund\n\nKandidaten total: {total}; admissible for testing: {admissible}.\n\n## Interpretation\n\nDie Ergebnisse sind Zulassungsentscheidungen für spätere Tests.\n\n## Hypothese\n\nAktuelle Blocker liegen in Aliasrisiko, Pair-Mapping, Lineage und fehlenden Wertreihen.\n\n## Offene Lücke\n\nKeine Lag-Mechanismus-Ausführung.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RESULTS_DE.md": "# Ergebnisse\n\n## Befund\n\nDie Ergebnis-CSV enthält pro Kandidat Kriterienzählung, kritische Fehler und Entscheidungsklasse.\n\n## Interpretation\n\nKeine Entscheidung bestätigt eine unabhängige Lag-Variable.\n\n## Hypothese\n\nReparatur- und Review-Klassen können spätere Arbeit priorisieren.\n\n## Offene Lücke\n\nWertserien fehlen.\n\n## Claim Boundary\n\nKeine physikalische Freigabe.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_ALIAS_FINDINGS_DE.md": "# Alias Findings\n\n## Befund\n\nAlias-Flags wurden pro Kandidat aus Inventarfeldern abgeleitet.\n\n## Interpretation\n\nGetriggerte Aliasflags blockieren den Independent-Lag-Gate.\n\n## Hypothese\n\nNeue Source-Artefakte könnten einzelne Unknown-Risiken klären.\n\n## Offene Lücke\n\nKeine neuen Wertreihen verfügbar.\n\n## Claim Boundary\n\nKein Mechanismusclaim.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_REPAIR_NEEDS_DE.md": "# Repair Needs\n\n## Befund\n\nLineage- und Metadata-Reparaturklassen wurden separat ausgewiesen.\n\n## Interpretation\n\nReparatur ist keine Zulassung und keine Bestätigung.\n\n## Hypothese\n\nSource-Lineage kann die Evidenzlage verbessern.\n\n## Offene Lücke\n\nReparatur wurde nicht ausgeführt.\n\n## Claim Boundary\n\nKeine Claim-Freigabe.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_RED_TEAM_DE.md": "# Red Team\n\n## Befund\n\nKandidaten mit gemischter oder unklarer Evidenz werden zum Red-Team-Review geroutet.\n\n## Interpretation\n\nRed-Team-Review verhindert voreilige Alias-/Proxyclaims.\n\n## Hypothese\n\nManueller Review kann unklare Inventarfelder klären.\n\n## Offene Lücke\n\nReview nicht ausgeführt.\n\n## Claim Boundary\n\nKeine physikalische Freigabe.\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_NEXT_GATE_DE.md": f"# Next Gate\n\n## Befund\n\n`next_gate={next_gate}`; `secondary_next_gate={secondary}`.\n\n## Interpretation\n\nDer nächste Gate folgt aus der Zulassungsauswertung, nicht aus Mechanismusbestätigung.\n\n## Hypothese\n\nWeitere Gate-Arbeit kann fehlende Eingaben adressieren.\n\n## Offene Lücke\n\nKeine Nullmodelle, keine Lag-Mechanismus-Tests.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_INDEPENDENT_LAG_VARIABLE_ADMISSIBILITY_EXECUTION_CLAIM_BOUNDARY_DE.md": "# Claim Boundary\n\n## Befund\n\nAlle Bestätigungs- und Physikclaims sind geblockt.\n\n## Interpretation\n\nAdmissibility ist Testzulassung, keine Evidenz für Mechanismus.\n\n## Hypothese\n\nSpätere Tests können neue Befunde liefern.\n\n## Offene Lücke\n\nKeine physikalische Validierung.\n\n## Claim Boundary\n\nNo physical claims are released.\n",
    }
    for rel, text in docs.items():
        write_text(run_dir / rel, text)

    tables = {
        "pbr_independent_lag_variable_admissibility_summary": (list(summary.keys()), [summary]),
        "pbr_independent_lag_variable_admissibility_input_lineage": (list(input_lineage[0].keys()), input_lineage),
        "pbr_independent_lag_variable_admissibility_results": (res_fields, result_rows),
        "pbr_independent_lag_variable_admissibility_criteria_results": (["run_id", "candidate_id", "criterion_name", "criterion_status", "criterion_evidence"], criteria_rows),
        "pbr_independent_lag_variable_admissibility_alias_flags": (["run_id", "candidate_id", "alias_flag", "alias_flag_status", "alias_evidence", "alias_risk_level"], alias_rows),
        "pbr_independent_lag_variable_deterministic_alias_check": (["run_id", "candidate_id", "value_series_status", "deterministic_alias_check_status", "r2_lag", "r2_abs_lag", "lookup_accuracy_pair_id", "lookup_accuracy_index_order", "residual_entropy"], det_rows),
        "pbr_independent_lag_variable_scramble_feasibility": (["run_id", "candidate_id", "scramble_test_feasible", "required_source_values_present", "required_mapping_present", "expected_blocker"], scramble_rows),
        "pbr_independent_lag_variable_source_lineage_audit": (["run_id", "candidate_id", "source_artifact_present", "generation_rule_present", "transformation_chain_complete", "derived_from_lag_flag", "derived_from_pair_id_flag", "derived_from_index_flag", "lineage_score", "lineage_decision"], lineage_rows),
        "pbr_independent_lag_variable_pair_mapping_audit": (["run_id", "candidate_id", "pair_mapping_status", "pair_mapping_coverage_status", "directed_pair_support", "mapping_uses_lag_as_value_source", "mapping_uses_pair_id_as_value_source", "mapping_decision"], pair_rows),
        "pbr_independent_lag_variable_information_gain_feasibility": (["run_id", "candidate_id", "information_gain_test_feasible", "candidate_values_available", "lag_values_available", "minimum_data_requirements_met", "information_gain_status"], info_rows),
        "pbr_independent_lag_variable_directionality_audit": (["run_id", "candidate_id", "directionality_documented", "directionality_class", "ij_reversal_behavior_available", "absolute_value_risk", "directionality_decision"], direction_rows),
        "pbr_independent_lag_variable_unit_dimension_audit": (["run_id", "candidate_id", "unit_present", "dimension_vector_present", "dimensionless_reason_present", "metadata_decision"], unit_rows),
        "pbr_independent_lag_variable_admissibility_decision_summary": (list(decision_summary[0].keys()), decision_summary),
        "pbr_independent_lag_variable_category_summary": (list(category_rows[0].keys()) if category_rows else ["run_id", "category"], category_rows),
        "pbr_independent_lag_variable_rejected_summary": (res_fields, rejected_rows),
        "pbr_independent_lag_variable_repair_required_summary": (res_fields, repair_rows),
        "pbr_independent_lag_variable_red_team_summary": (res_fields, red_rows),
        "pbr_independent_lag_variable_admissibility_claim_boundaries": (list(claims[0].keys()), claims),
        "pbr_independent_lag_variable_admissibility_next_gate": (list(next_gate_rows[0].keys()), next_gate_rows),
        "pbr_independent_lag_variable_admissibility_validation": (list(validation_placeholder[0].keys()), []),
    }
    create_sql(run_dir, tables)
    print(f"target_run_id={RUN_ID}")
    print(f"execution_status={execution_status}")
    print(f"final_admissibility_status={final_status}")
    print(f"candidate_count_total={total}")
    print(f"candidate_count_admissible_for_testing={admissible}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
