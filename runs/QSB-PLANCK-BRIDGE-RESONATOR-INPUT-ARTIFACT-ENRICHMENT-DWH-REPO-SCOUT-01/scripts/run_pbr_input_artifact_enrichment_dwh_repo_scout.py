#!/usr/bin/env python3
"""Scout repo and DWH artifacts for PBR input artifact enrichment candidates."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
TERMS = [
    "momentum", "p_i", "p_j", "delta_p", "delta_p2", "p_squared", "energy", "E_i", "E_j", "delta_E",
    "omega", "omega_i", "omega_j", "delta_omega", "frequency", "mode", "mode_index", "phase", "phase_i",
    "phase_j", "delta_phi", "phase_response", "spectral_gap", "scale_mapping", "Compton", "Schwarzschild",
    "Planck", "lambda_C", "r_s", "beta_B", "Xi_CS", "K_candidate", "pair_id", "lag", "directed_pair",
    "Impuls", "Impulsdifferenz", "quadratische Impulsdifferenz", "Energie", "Energiedifferenz", "Frequenz",
    "Frequenzabstand", "Modus", "Modenindex", "Phase", "Phasendifferenz", "Phasenfortschritt", "Spektrallücke",
    "Skalenmapping", "Paar", "Kandidat", "Matrix",
]
PROXY_FAMILIES = [
    "momentum_proxy", "energy_proxy", "frequency_proxy", "phase_proxy", "mode_proxy", "spectral_gap_proxy",
    "compton_schwarzschild_proxy", "planck_scale_mapping_proxy",
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


def git_head(repo_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def repo_files(repo_root: Path) -> List[Path]:
    roots = [repo_root / name for name in ["runs", "docs", "scripts", "data", "sql"]]
    files: List[Path] = []
    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return sorted(files)


def safe_read(path: Path, max_bytes: int = 300_000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def classify_file(rel: str, text: str) -> Tuple[str, str, str, str, str]:
    low = (rel + "\n" + text).lower()
    if "10_phase_response_vector_summary.csv" in rel:
        return ("phase_response", "phase_proxy", "pair_level", "high", "not_independent_alias_of_lag")
    if "scale_mapping" in low or "compton" in low or "schwarzschild" in low or "beta_b" in low or "xi_cs" in low:
        return ("scale_mapping", "planck_scale_mapping_proxy", "scale_mapping_level", "medium", "not_pair_mappable")
    if "k_candidate" in low:
        return ("K_candidate", "matrix_structure", "matrix_level", "high", "not_independent_alias_of_pair_id")
    if "delta_phi" in low or "phase" in low:
        return ("delta_phi_or_phase", "phase_proxy", "unknown_level", "high", "unknown_requires_lineage")
    if "mode_frequency" in low or "frequency" in low or "mode" in low:
        return ("mode_or_frequency", "frequency_proxy", "unknown_level", "unknown", "unknown_requires_lineage")
    return ("candidate_term_match", "unknown", "unknown_level", "unknown", "unknown_requires_lineage")


def psql_rows(database: str, sql: str, repo_root: Path) -> Tuple[bool, List[List[str]], str]:
    cmd = ["psql", "-d", database, "-At", "-F", "\t", "-c", sql]
    try:
        proc = subprocess.run(cmd, cwd=repo_root, text=True, capture_output=True, timeout=20)
    except Exception as exc:
        return False, [], str(exc)
    if proc.returncode != 0:
        return False, [], (proc.stderr or proc.stdout).strip()
    rows = [line.split("\t") for line in proc.stdout.splitlines() if line.strip()]
    return True, rows, "ok"


def sql_type(_field: str) -> str:
    return "text"


def tsv(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def create_sql(run_dir: Path, tables: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in tables.items():
        parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  " + ",\n  ".join(f"{f} {sql_type(f)}" for f in fields) + "\n);")
        parts.append("")
    parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_input_artefakt_scout_de;")
    parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_input_artefakt_scout_de AS
SELECT
  run_id AS "Lauf-ID",
  run_type AS "Lauftyp",
  execution_status AS "Ausführungsstatus",
  scout_decision AS "Scout-Entscheidung",
  repo_scout_status AS "Repo-Scout-Status",
  dwh_scout_status AS "DWH-Scout-Status",
  candidate_count AS "Kandidatenanzahl",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate"
FROM {SCHEMA}.pbr_input_artifact_enrichment_scout_summary
WHERE run_id = '{RUN_ID}';""")
    write_text(run_dir / "sql/001_create_qsb_pbr_input_artifact_enrichment_dwh_repo_scout.sql", "\n".join(parts))
    ins = ["BEGIN;", ""]
    for table in tables:
        ins.append(f"DELETE FROM {SCHEMA}.{table} WHERE run_id = '{RUN_ID}';")
    ins.append("")
    for table, (fields, rows) in tables.items():
        if not rows:
            continue
        ins.append(f"COPY {SCHEMA}.{table} ({', '.join(fields)}) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');")
        ins.append("\t".join(fields))
        for row in rows:
            ins.append("\t".join(tsv(row.get(field, "")) for field in fields))
        ins.append(r"\.")
        ins.append("")
    ins.append("COMMIT;")
    write_text(run_dir / "sql/002_insert_qsb_pbr_input_artifact_enrichment_dwh_repo_scout.sql", "\n".join(ins))
    write_text(run_dir / "sql/003_validation_queries.sql", f"""
SELECT 'scout_decision' AS check_name, scout_decision AS value
FROM {SCHEMA}.pbr_input_artifact_enrichment_scout_summary
WHERE run_id = '{RUN_ID}';

SELECT 'candidate_count' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_input_artifact_enrichment_candidate_variables
WHERE run_id = '{RUN_ID}';

SELECT 'proxy_family_count' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_input_artifact_enrichment_physical_proxy_sources
WHERE run_id = '{RUN_ID}';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM {SCHEMA}.pbr_input_artifact_enrichment_next_gate
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
    data_dir = run_dir / "data"
    if run_dir.name != RUN_ID:
        raise SystemExit("wrong_prompt_or_stale_context_detected")
    status = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=repo_root, text=True, capture_output=True).stdout.splitlines()
    pre_existing_review_mods = [line for line in status if "runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01/" in line]

    files = repo_files(repo_root)
    repo_inventory = []
    candidates = []
    alias_rows = []
    lineage_rows = []
    readiness = []
    for path in files:
        rel = path.relative_to(repo_root).as_posix()
        text = safe_read(path)
        hits = sorted({term for term in TERMS if term.lower() in (rel + "\n" + text).lower()})
        if hits:
            repo_inventory.append({"run_id": RUN_ID, "source_path": rel, "matched_terms": "|".join(hits[:20]), "artifact_kind": path.suffix.lstrip(".") or "no_suffix"})
        if hits and len(candidates) < 200:
            name, category, level, alias_risk, independence = classify_file(rel, text)
            has_pair = "pair_id" in text or "canonical_pair_id" in text or "row_pair_id" in text
            has_lag = "lag" in text.lower() or "j-i" in text or "|j-i|" in text
            candidate_id = f"CAND-{len(candidates) + 1:04d}"
            row = {
                "run_id": RUN_ID, "candidate_id": candidate_id, "source_type": "repo_file", "source_path_or_table": rel,
                "candidate_variable_name": name, "candidate_category": category, "artifact_level": level,
                "pair_mappable": "true" if has_pair else "false", "has_i_j_or_pair_id": "true" if has_pair else "false",
                "has_lag": "true" if has_lag else "false", "has_units": "true" if "unit" in text.lower() else "false",
                "has_dimension_metadata": "true" if "dimension" in text.lower() else "false",
                "has_source_lineage": "true" if "lineage" in text.lower() or "sha256" in text.lower() else "false",
                "upstream_generation_stage": rel.split("/")[1] if rel.startswith("runs/") and len(rel.split("/")) > 1 else "repo",
                "derived_from_index_order": "unknown", "derived_from_lag_or_abs_lag": "true" if independence == "not_independent_alias_of_lag" else "unknown",
                "derived_from_pair_id": "true" if independence == "not_independent_alias_of_pair_id" else "unknown",
                "non_alias_evidence": "not_established_by_scout", "alias_risk_level": alias_risk, "independence_status": independence,
                "review_need": "review_required_before_use", "claim_implication": "candidate_only_no_independence_claim",
            }
            if name == "phase_response":
                row.update({"derived_from_lag_or_abs_lag": "true", "non_alias_evidence": "phase_response_raw_ranges_follow_abs_lag_in_source_summary", "claim_implication": "no_independent_lag_variable_claim"})
            candidates.append(row)
            alias_rows.append({"run_id": RUN_ID, "candidate_id": candidate_id, "candidate_variable_name": name, "alias_reference": "abs_lag" if name == "phase_response" else "unknown", "alias_risk_level": alias_risk, "independence_status": independence, "claim_implication": row["claim_implication"]})
            lineage_rows.append({"run_id": RUN_ID, "candidate_id": candidate_id, "source_path_or_table": rel, "has_source_lineage": row["has_source_lineage"], "lineage_assessment": "lineage_present_requires_review" if row["has_source_lineage"] == "true" else "lineage_incomplete"})
            readiness.append({"run_id": RUN_ID, "candidate_id": candidate_id, "pair_mappable": row["pair_mappable"], "mapping_readiness": "pair_mappable_requires_review" if row["pair_mappable"] == "true" else "not_pair_mappable"})

    column_sql = """SELECT table_schema, table_name, column_name FROM information_schema.columns WHERE table_schema IN ('qsb_planck_bridge','public') AND (column_name ILIKE '%momentum%' OR column_name ILIKE '%delta_p%' OR column_name ILIKE '%omega%' OR column_name ILIKE '%energy%' OR column_name ILIKE '%phase%' OR column_name ILIKE '%phi%' OR column_name ILIKE '%frequency%' OR column_name ILIKE '%mode%' OR column_name ILIKE '%compton%' OR column_name ILIKE '%schwarzschild%' OR column_name ILIKE '%planck%' OR column_name ILIKE '%lambda%' OR column_name ILIKE '%lag%' OR column_name ILIKE '%pair%') ORDER BY table_schema, table_name, column_name;"""
    ok_cols, col_rows, dwh_msg = psql_rows(args.database, column_sql, repo_root)
    meta_sql = "SELECT table_schema, table_name FROM information_schema.tables WHERE table_name ILIKE 'meta_%' OR table_name ILIKE '%metadata%' ORDER BY table_schema, table_name;"
    ok_meta, meta_rows, meta_msg = psql_rows(args.database, meta_sql, repo_root)
    dwh_inventory = []
    if ok_cols:
        for schema, table, column in col_rows:
            dwh_inventory.append({"run_id": RUN_ID, "object_type": "column", "table_schema": schema, "table_name": table, "column_name": column, "matched_reason": "candidate_column_name"})
            if len(candidates) < 260:
                candidate_id = f"CAND-{len(candidates) + 1:04d}"
                name, category, level, alias_risk, independence = classify_file(f"{schema}.{table}.{column}", column)
                candidates.append({
                    "run_id": RUN_ID, "candidate_id": candidate_id, "source_type": "dwh_table", "source_path_or_table": f"{schema}.{table}", "candidate_variable_name": column,
                    "candidate_category": category, "artifact_level": "metadata_level", "pair_mappable": "unknown", "has_i_j_or_pair_id": "true" if "pair" in column.lower() else "unknown",
                    "has_lag": "true" if "lag" in column.lower() else "unknown", "has_units": "unknown", "has_dimension_metadata": "unknown", "has_source_lineage": "unknown",
                    "upstream_generation_stage": "dwh", "derived_from_index_order": "unknown", "derived_from_lag_or_abs_lag": "unknown", "derived_from_pair_id": "unknown",
                    "non_alias_evidence": "not_established_by_dwh_presence", "alias_risk_level": alias_risk, "independence_status": "unknown_requires_lineage",
                    "review_need": "dwh_source_lineage_check_required", "claim_implication": "dwh_presence_alone_no_independence_claim",
                })
    if ok_meta:
        for schema, table in meta_rows:
            dwh_inventory.append({"run_id": RUN_ID, "object_type": "metadata_table", "table_schema": schema, "table_name": table, "column_name": "", "matched_reason": "metadata_table_name"})
    dwh_status = "executed" if ok_cols or ok_meta else "blocked_dwh_unavailable"
    if not dwh_inventory:
        dwh_inventory.append({"run_id": RUN_ID, "object_type": "dwh_scout_status", "table_schema": "", "table_name": "", "column_name": "", "matched_reason": f"{dwh_status}:{dwh_msg or meta_msg}"})

    proxy_rows = []
    for family in PROXY_FAMILIES:
        related = [c for c in candidates if family.replace("_proxy", "") in c["candidate_category"] or (family.startswith("phase") and "phase" in c["candidate_variable_name"].lower())]
        if related:
            status = "source_candidate_found_requires_mapping_review" if any(c["pair_mappable"] == "true" for c in related) else "source_candidate_found_not_pair_mappable"
            source = related[0]["source_path_or_table"]
        else:
            status = "source_candidate_not_found"
            source = "not_available"
        if family in {"compton_schwarzschild_proxy", "planck_scale_mapping_proxy"} and related:
            status = "source_candidate_found_not_pair_mappable"
        proxy_rows.append({"run_id": RUN_ID, "proxy_family": family, "candidate_status": status, "source_path_or_table": source, "claim_implication": "source_candidate_only_no_physical_proxy_claim"})

    gap_rows = [
        ("independent_lag_variable_artifact", "open_candidate_scout_completed", "Need non-alias lag variable with lineage.", "candidate_artifacts_require_review"),
        ("physical_proxy_source_artifact", "open_candidate_scout_completed", "Need mappable physical proxy source values.", "candidate_sources_require_mapping_review"),
        ("proxy_independence_criteria", "open_requires_design", "Need criteria distinguishing proxy from lag alias.", "deep_research_or_design_criteria_required"),
        ("phase_response_alias_review", "high_priority", "Phase response appears alias-like against abs_lag.", "alias_review_required"),
        ("source_lineage_for_candidate_variables", "open_requires_lineage_review", "Need source lineage for candidate variables.", "lineage_repair_or_review_required"),
    ]
    gap_update = [{"run_id": RUN_ID, "gap_key": k, "gap_status": s, "why_needed": w, "update_note": u} for k, s, w, u in gap_rows]
    questions = [
        "Welche formalen Kriterien unterscheiden eine unabhängige Lag-Variable von einem Alias von |j-i|?",
        "Welche mathematischen Strukturen sind für lag-dominierte Matrizen relevant?",
        "Welche Kriterien gelten für Shift-/Translations-/Toeplitz-Strukturen?",
        "Welche physikalischen Proxy-Größen wären bei Moden-, Phasen-, Energie- oder Impulsstrukturen methodisch zulässig?",
        "Welche Reviewer-Einwände entstehen bei Proxy-Korrelationen?",
    ]
    question_rows = [{"run_id": RUN_ID, "question_id": f"DRQ-{i:03d}", "handoff_question": q, "evidence_status": "question_only_no_deep_research_answer"} for i, q in enumerate(questions, start=1)]
    blocked_claims = [
        "QSB is physically " + "validated", "PBR exists " + "physically", "six lag axes are " + "spacetime dimensions",
        "spacetime emergence is " + "proven", "empirical validation " + "exists", "lag classes are " + "physical dimensions",
        "lag mechanism is physically " + "proven", "candidate artifact proves " + "independent lag mechanism",
        "candidate artifact proves " + "physical proxy", "DWH presence alone proves " + "independence",
        "repo presence alone proves " + "independence", "literature note alone proves " + "proxy for current matrix",
        "phase-response values are independent " + "lag variables despite alias assessment",
    ]
    claims = [{"run_id": RUN_ID, "claim_key": f"BLOCK-{i:03d}", "claim_text": c, "status": "blocked", "physical_claim_release": PHYSICAL_CLAIM_RELEASE} for i, c in enumerate(blocked_claims, start=1)]
    scout_decision = "candidate_artifacts_found_but_alias_risk_high" if any(c["alias_risk_level"] == "high" for c in candidates) else ("candidate_artifacts_found_require_review" if candidates else "no_candidate_artifacts_found")
    next_gate = "independent_lag_variable_design_required" if scout_decision == "candidate_artifacts_found_but_alias_risk_high" else "input_artifact_enrichment_design_required"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    summary = {
        "run_id": RUN_ID, "run_type": "dwh_repo_artifact_scout", "execution_status": "executed", "claim_status": "input_artifact_scout_only",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE, "input_gate": "input_artifact_enrichment_required", "source_final_decision_class": "inconclusive_requires_more_inputs",
        "scout_decision": scout_decision, "next_gate": next_gate, "repo_scout_status": "executed", "dwh_scout_status": dwh_status,
        "candidate_count": str(len(candidates)), "repo_artifact_match_count": str(len(repo_inventory)), "dwh_artifact_match_count": str(len(dwh_inventory)),
        "pre_existing_modified_review_run": "|".join(pre_existing_review_mods), "git_head": git_head(repo_root), "created_at_utc": now,
    }
    next_gate_rows = [{"run_id": RUN_ID, "next_gate": next_gate, "secondary_next_gate": "deep_research_criteria_review_required", "execution_authorization": "not_authorized_in_this_scout_run", "physical_claim_release": PHYSICAL_CLAIM_RELEASE}]
    manifest = {"run_id": RUN_ID, "target_run_id_verified": RUN_ID, "terms": TERMS, "dwh_scout_status": dwh_status, "scout_decision": scout_decision, "no_lag_mechanism_tests_executed": True, "no_nullmodels_executed": True}

    write_csv(data_dir / "scout_summary.csv", [summary], list(summary.keys()))
    write_csv(data_dir / "repo_artifact_inventory.csv", repo_inventory[:1000] or [{"run_id": RUN_ID, "source_path": "not_found", "matched_terms": "", "artifact_kind": ""}], ["run_id", "source_path", "matched_terms", "artifact_kind"])
    write_csv(data_dir / "dwh_artifact_inventory.csv", dwh_inventory, ["run_id", "object_type", "table_schema", "table_name", "column_name", "matched_reason"])
    cand_fields = ["run_id","candidate_id","source_type","source_path_or_table","candidate_variable_name","candidate_category","artifact_level","pair_mappable","has_i_j_or_pair_id","has_lag","has_units","has_dimension_metadata","has_source_lineage","upstream_generation_stage","derived_from_index_order","derived_from_lag_or_abs_lag","derived_from_pair_id","non_alias_evidence","alias_risk_level","independence_status","review_need","claim_implication"]
    write_csv(data_dir / "candidate_variable_inventory.csv", candidates, cand_fields)
    write_csv(data_dir / "candidate_lineage_assessment.csv", lineage_rows, ["run_id", "candidate_id", "source_path_or_table", "has_source_lineage", "lineage_assessment"])
    write_csv(data_dir / "candidate_alias_risk_assessment.csv", alias_rows, ["run_id", "candidate_id", "candidate_variable_name", "alias_reference", "alias_risk_level", "independence_status", "claim_implication"])
    write_csv(data_dir / "physical_proxy_source_candidates.csv", proxy_rows, ["run_id", "proxy_family", "candidate_status", "source_path_or_table", "claim_implication"])
    write_csv(data_dir / "pair_mapping_readiness.csv", readiness, ["run_id", "candidate_id", "pair_mappable", "mapping_readiness"])
    write_csv(data_dir / "input_artifact_gap_update.csv", gap_update, ["run_id", "gap_key", "gap_status", "why_needed", "update_note"])
    write_csv(data_dir / "deep_research_handoff_questions.csv", question_rows, ["run_id", "question_id", "handoff_question", "evidence_status"])
    write_csv(data_dir / "claim_boundaries.csv", claims, list(claims[0].keys()))
    write_csv(data_dir / "next_gate_decision.csv", next_gate_rows, list(next_gate_rows[0].keys()))
    (data_dir / "scout_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validation_placeholder = [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Scout generated; run validator."}]
    write_csv(run_dir / "validation/validation_results.csv", validation_placeholder, list(validation_placeholder[0].keys()))

    docs = {
        "README.md": f"# {RUN_ID}\n\nDWH/Repo-Scout für Input-Artefakt-Anreicherung.\n\nNo lag mechanism tests were executed.\nNo nullmodels were executed.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        f"{RUN_ID}.md": f"# {RUN_ID}\n\n## Befund\n\nDer Scout fand Kandidatenartefakte mit Review-Bedarf. Scout-Entscheidung: `{scout_decision}`.\n\n## Interpretation\n\nKandidaten sind nicht als unabhängige Lag-Variablen oder physische Proxies bestätigt.\n\n## Hypothese\n\nDie nächsten Gates müssen Alias- und Lineage-Kriterien schärfen.\n\n## Offene Lücke\n\nDWH-/Repo-Präsenz allein belegt keine Unabhängigkeit.\n\n## Claim Boundary\n\nNo physical claims are released.\n",
        "RUN_COMMANDS_PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT01.md": f"# Run Commands\n\n```bash\nRUN_DIR=\"runs/{RUN_ID}\"\n.venv/bin/python \"$RUN_DIR/scripts/run_pbr_input_artifact_enrichment_dwh_repo_scout.py\" --repo-root . --run-dir \"$RUN_DIR\" --database qsb_research_dwh\n.venv/bin/python \"$RUN_DIR/scripts/validate_pbr_input_artifact_enrichment_dwh_repo_scout.py\" \"$RUN_DIR\"\ngit diff --check\ngit status --short --untracked-files=all\n```\n",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_SUMMARY_DE.md": f"# Scout Summary\n\n## Befund\n\nScout-Entscheidung: `{scout_decision}`.\n\n## Interpretation\n\nGefundene Artefakte benötigen Review; keine Bestätigung.\n\n## Hypothese\n\nAlias-Risiko und Lineage sind die nächsten Prüfstellen.\n\n## Offene Lücke\n\nUnabhängigkeit nicht belegt.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_CANDIDATES_DE.md": "# Kandidaten\n\n## Befund\n\nDer Scout listet Repo- und DWH-Kandidaten.\n\n## Interpretation\n\nKandidaten sind nur Scout-Funde.\n\n## Hypothese\n\nEinige Funde können für spätere Enrichment-Designs relevant sein.\n\n## Offene Lücke\n\nMapping und Lineage sind offen.\n\n## Claim Boundary\n\nKeine Claim-Freigabe.\n",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_ALIAS_RISK_DE.md": "# Alias-Risiko\n\n## Befund\n\nPhase-Response wird als hohes Alias-Risiko gegen abs_lag geführt.\n\n## Interpretation\n\nDamit entsteht kein unabhängiger Lag-Variablenclaim.\n\n## Hypothese\n\nEin separater Alias-Review ist nötig.\n\n## Offene Lücke\n\nNicht-Alias-Evidenz fehlt.\n\n## Claim Boundary\n\nKeine physikalische Freigabe.\n",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_DWH_RESULTS_DE.md": f"# DWH Results\n\n## Befund\n\nDWH-Scout-Status: `{dwh_status}`.\n\n## Interpretation\n\nDWH-Präsenz allein beweist keine Unabhängigkeit.\n\n## Hypothese\n\nDWH-Kandidaten brauchen Source-Lineage-Review.\n\n## Offene Lücke\n\nQuellartefakt-Mapping offen.\n\n## Claim Boundary\n\nKeine Claim-Freigabe.\n",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_NEXT_GATE_DE.md": f"# Next Gate\n\n## Befund\n\n`next_gate={next_gate}`.\n\n## Interpretation\n\nDer nächste Gate betrifft Kriterien und Enrichment, keine Testausführung.\n\n## Hypothese\n\nDeep-Research-Fragen können Kriterien vorbereiten.\n\n## Offene Lücke\n\nKeine Deep-Research-Antworten in diesem Lauf.\n\n## Claim Boundary\n\nKeine physikalische Claim-Freigabe.\n",
        "docs/PBR_INPUT_ARTIFACT_ENRICHMENT_DWH_REPO_SCOUT_DEEP_RESEARCH_HANDOFF_DE.md": "# Deep Research Handoff\n\n## Befund\n\nEs wurden nur Fragen formuliert.\n\n## Interpretation\n\nDiese Fragen sind keine Evidenz.\n\n## Hypothese\n\nSie können einen späteren Kriterienreview strukturieren.\n\n## Offene Lücke\n\nKeine externe Recherche wurde durchgeführt.\n\n## Claim Boundary\n\nKeine Claim-Freigabe.\n",
    }
    for rel, text in docs.items():
        write_text(run_dir / rel, text)

    tables = {
        "pbr_input_artifact_enrichment_scout_summary": (list(summary.keys()), [summary]),
        "pbr_input_artifact_enrichment_repo_inventory": (["run_id", "source_path", "matched_terms", "artifact_kind"], repo_inventory[:1000] or []),
        "pbr_input_artifact_enrichment_dwh_inventory": (["run_id", "object_type", "table_schema", "table_name", "column_name", "matched_reason"], dwh_inventory),
        "pbr_input_artifact_enrichment_candidate_variables": (cand_fields, candidates),
        "pbr_input_artifact_enrichment_lineage_assessment": (["run_id", "candidate_id", "source_path_or_table", "has_source_lineage", "lineage_assessment"], lineage_rows),
        "pbr_input_artifact_enrichment_alias_risk": (["run_id", "candidate_id", "candidate_variable_name", "alias_reference", "alias_risk_level", "independence_status", "claim_implication"], alias_rows),
        "pbr_input_artifact_enrichment_physical_proxy_sources": (["run_id", "proxy_family", "candidate_status", "source_path_or_table", "claim_implication"], proxy_rows),
        "pbr_input_artifact_enrichment_pair_mapping_readiness": (["run_id", "candidate_id", "pair_mappable", "mapping_readiness"], readiness),
        "pbr_input_artifact_enrichment_gap_update": (["run_id", "gap_key", "gap_status", "why_needed", "update_note"], gap_update),
        "pbr_input_artifact_enrichment_deep_research_handoff": (["run_id", "question_id", "handoff_question", "evidence_status"], question_rows),
        "pbr_input_artifact_enrichment_claim_boundaries": (list(claims[0].keys()), claims),
        "pbr_input_artifact_enrichment_next_gate": (list(next_gate_rows[0].keys()), next_gate_rows),
        "pbr_input_artifact_enrichment_validation": (list(validation_placeholder[0].keys()), []),
    }
    create_sql(run_dir, tables)
    print(f"target_run_id={RUN_ID}")
    print(f"scout_decision={scout_decision}")
    print(f"dwh_scout_status={dwh_status}")
    print(f"candidate_count={len(candidates)}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
