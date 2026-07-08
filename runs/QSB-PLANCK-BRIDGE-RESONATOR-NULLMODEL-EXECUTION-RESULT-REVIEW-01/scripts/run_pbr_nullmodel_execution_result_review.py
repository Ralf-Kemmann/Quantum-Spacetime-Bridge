#!/usr/bin/env python3
"""Create the PBR nullmodel execution result-review package."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01"
INPUT_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01"
INPUT_RUN_REL = f"runs/{INPUT_RUN_ID}"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
REVIEW_OUTCOME = "no_specificity_confirmed_for_current_operationalization"
NEXT_GATE = "lag_mechanism_required"
SECONDARY_NEXT_GATE = "nullmodel_operationalization_review_required"
FAMILIES = [
    "label_permutation_null",
    "lag_preserving_shuffle_null",
    "random_gram_psd_null",
    "directed_pair_rewire_null",
    "sign_flip_antiparallel_null",
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def fmt(value: Any) -> str:
    return str(value)


def sql_type(field: str) -> str:
    if field.endswith("_count") or field in {"samples_total", "sample_count_total", "samples_per_family"}:
        return "integer"
    if field.endswith("_rate"):
        return "double precision"
    return "text"


def sql_value(value: Any) -> str:
    return fmt(value).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def create_sql(run_dir: Path, tables: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in tables.items():
        cols = ",\n  ".join(f"{field} {sql_type(field)}" for field in fields)
        parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  {cols}\n);")
        parts.append("")
    parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_nullmodell_result_review_de;")
    parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_nullmodell_result_review_de AS
SELECT
  s.run_id AS "Lauf-ID",
  s.review_outcome AS "Review-Ergebnis",
  s.specificity_status AS "Spezifitätsstatus",
  c.critical_nullmodel AS "kritisches Nullmodell",
  c.complete_reproduction_rate AS "Reproduktionsrate",
  s.physical_claim_release AS "physikalische Claim-Freigabe",
  n.next_gate AS "nächster Gate",
  n.secondary_next_gate AS "sekundärer Gate"
FROM {SCHEMA}.pbr_nullmodel_execution_result_review_summary s
JOIN {SCHEMA}.pbr_nullmodel_execution_result_review_critical_findings c ON c.run_id = s.run_id
JOIN {SCHEMA}.pbr_nullmodel_execution_result_review_next_gate n ON n.run_id = s.run_id
WHERE s.run_id = '{RUN_ID}';""")
    write_text(run_dir / "sql/001_create_qsb_pbr_nullmodel_execution_result_review.sql", "\n".join(parts))

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
    write_text(run_dir / "sql/002_insert_qsb_pbr_nullmodel_execution_result_review.sql", "\n".join(insert))

    validation = f"""
SELECT 'review_outcome' AS check_name, review_outcome AS value
FROM {SCHEMA}.pbr_nullmodel_execution_result_review_summary
WHERE run_id = '{RUN_ID}';

SELECT 'critical_nullmodel' AS check_name, critical_nullmodel AS value
FROM {SCHEMA}.pbr_nullmodel_execution_result_review_critical_findings
WHERE run_id = '{RUN_ID}';

SELECT 'specificity_classification' AS check_name, specificity_classification AS value
FROM {SCHEMA}.pbr_nullmodel_execution_result_review_specificity
WHERE run_id = '{RUN_ID}';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM {SCHEMA}.pbr_nullmodel_execution_result_review_next_gate
WHERE run_id = '{RUN_ID}';
"""
    write_text(run_dir / "sql/003_validation_queries.sql", validation)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, default=Path(f"runs/{RUN_ID}"))
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    input_dir = repo_root / INPUT_RUN_REL
    data_dir = run_dir / "data"
    executed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    commit = git_commit(repo_root)

    if not input_dir.exists():
        summary = [{
            "run_id": RUN_ID,
            "input_run_id": INPUT_RUN_ID,
            "review_status": "blocked_missing_input_run",
            "review_outcome": "not_reviewed",
            "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
            "next_gate": "input_run_required",
        }]
        write_csv(data_dir / "nullmodel_execution_review_summary.csv", summary, list(summary[0].keys()))
        return 2

    exec_summary = read_csv(input_dir / "data/nullmodel_execution_summary.csv")[0]
    family_input = read_csv(input_dir / "data/nullmodel_family_summary.csv")
    specificity_input = read_csv(input_dir / "data/specificity_classification.csv")[0]
    family_by_name = {row["nullmodel_family"]: row for row in family_input}
    critical = family_by_name["lag_preserving_shuffle_null"]

    summary = {
        "run_id": RUN_ID,
        "input_run_id": INPUT_RUN_ID,
        "review_status": "review_completed",
        "review_outcome": REVIEW_OUTCOME,
        "formal_finding_status": "psd_rank6_lag_structure_remains_formal",
        "specificity_status": "no_specificity_beyond_lag_preserving_construction",
        "critical_nullmodel": "lag_preserving_shuffle_null",
        "critical_nullmodel_reproduction": f"{critical['complete_reproduction_count']}/{critical['sample_count']}",
        "claim_status": "nullmodel_result_review_only",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "external_readiness": "internal_only",
        "next_gate": NEXT_GATE,
        "secondary_next_gate": SECONDARY_NEXT_GATE,
        "review_timestamp_utc": executed_at,
        "git_commit": commit,
    }
    write_csv(data_dir / "nullmodel_execution_review_summary.csv", [summary], list(summary.keys()))

    family_rows = []
    for family in FAMILIES:
        row = family_by_name[family]
        complete_rate = row["null_reproduction_rate"]
        if family == "lag_preserving_shuffle_null":
            interpretation = "vollstaendige_reproduktion_bei_erhaltener_lag_klasse"
            implication = "keine_spezifitaet_ueber_lag_erhaltende_konstruktion_hinaus"
        else:
            interpretation = "keine_vollstaendige_reproduktion_in_dieser_nullmodellfamilie"
            implication = "stuetzt_nicht_allein_einen_staerkeren_spezifitaetsclaim"
        family_rows.append({
            "run_id": RUN_ID,
            "input_run_id": INPUT_RUN_ID,
            "nullmodel_family": family,
            "samples_total": row["sample_count"],
            "complete_reproduction_count": row["complete_reproduction_count"],
            "complete_reproduction_rate": complete_rate,
            "partial_reproduction_count": row.get("partial_reproduction_count", "not_available"),
            "rank6_preservation_count": str(round(float(row.get("rank6_rate", "0")) * int(row["sample_count"]))),
            "review_interpretation": interpretation,
            "claim_implication": implication,
            "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        })
    write_csv(data_dir / "nullmodel_family_review.csv", family_rows, list(family_rows[0].keys()))

    critical_rows = [{
        "run_id": RUN_ID,
        "critical_nullmodel": "lag_preserving_shuffle_null",
        "complete_reproduction_count": critical["complete_reproduction_count"],
        "samples_total": critical["sample_count"],
        "complete_reproduction_rate": critical["null_reproduction_rate"],
        "interpretation": "structure_fully_reproduced_when_lag_classes_preserved",
        "claim_implication": "no_specificity_beyond_lag_preserving_construction",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }]
    write_csv(data_dir / "critical_nullmodel_findings.csv", critical_rows, list(critical_rows[0].keys()))

    specificity = [{
        "run_id": RUN_ID,
        "input_run_id": INPUT_RUN_ID,
        "specificity_classification": "no_specificity",
        "specificity_de_label": "keine formale Spezifität",
        "specificity_reason": "lag_preserving_shuffle_null_reproduced_complete_structure_1000_of_1000",
        "formal_claim_status": "no_stronger_specificity_claim",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }]
    write_csv(data_dir / "specificity_interpretation.csv", specificity, list(specificity[0].keys()))

    lineage = []
    for source_run_id in [
        INPUT_RUN_ID,
        "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01",
        "QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01",
    ]:
        rel = f"runs/{source_run_id}"
        path = repo_root / rel
        lineage.append({
            "run_id": RUN_ID,
            "source_run_id": source_run_id,
            "source_path": rel,
            "source_exists": "true" if path.exists() else "false",
            "source_role": "review_input" if source_run_id == INPUT_RUN_ID else "upstream_context",
        })
    write_csv(data_dir / "input_run_lineage.csv", lineage, list(lineage[0].keys()))

    claim_rows = [
        {"run_id": RUN_ID, "claim_key": "formal_review_scope", "status": "allowed_formal_only", "claim_text": "Die Nullmodell-Ausführung wird nur formal reviewt.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "lag_mechanism", "status": "allowed_formal_only", "claim_text": "Die Lag-Klassenstruktur erscheint in der aktuellen Operationalisierung als tragender formaler Mechanismus des Befunds.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "qsb_physical_validation", "status": "blocked", "claim_text": "Eine physische QSB-Validierungsbehauptung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "pbr_physical_existence", "status": "blocked", "claim_text": "Eine physische PBR-Existenzbehauptung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "lag_axes_physical_dimensions", "status": "blocked", "claim_text": "Eine Deutung der Lag-Klassen als physische Dimensionen ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "proof_or_disproof", "status": "blocked", "claim_text": "Das Nullmodell-Resultat beweist oder widerlegt QSB nicht.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
    ]
    write_csv(data_dir / "claim_boundaries.csv", claim_rows, list(claim_rows[0].keys()))

    next_gate = [{
        "run_id": RUN_ID,
        "next_gate": NEXT_GATE,
        "secondary_next_gate": SECONDARY_NEXT_GATE,
        "execution_authorization": "not_authorized_in_this_review_run",
        "gate_meaning": "klaeren_ob_lag_klassen_index_konstruktion_oder_unabhaengig_motivierter_mechanismus_sind",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }]
    write_csv(data_dir / "next_gate_decision.csv", next_gate, list(next_gate[0].keys()))

    recommended = [
        {"run_id": RUN_ID, "work_item_id": "NW-001", "work_item": "lag_mechanism_review", "priority": "primary", "description": "Pruefen, ob die Lag-Klassenstruktur unabhaengig formal motiviert werden kann."},
        {"run_id": RUN_ID, "work_item_id": "NW-002", "work_item": "nullmodel_operationalization_review", "priority": "secondary", "description": "Pruefen, ob das lag-erhaltende Shuffle-Nullmodell passend, zu permissiv oder uebererhaltend ist."},
        {"run_id": RUN_ID, "work_item_id": "NW-003", "work_item": "no_external_claim_release", "priority": "boundary", "description": "Keine externe Claim-Freigabe ohne zusaetzliche Gates."},
    ]
    write_csv(data_dir / "recommended_next_work.csv", recommended, list(recommended[0].keys()))

    manifest = {
        "run_id": RUN_ID,
        "input_run_id": INPUT_RUN_ID,
        "created_at_utc": executed_at,
        "review_outcome": REVIEW_OUTCOME,
        "nullmodels_executed_in_this_review_run": False,
        "input_execution_summary": exec_summary,
        "input_specificity": specificity_input,
        "critical_nullmodel": critical_rows[0],
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "next_gate": NEXT_GATE,
        "secondary_next_gate": SECONDARY_NEXT_GATE,
    }
    (data_dir / "review_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    docs = {
        "README.md": f"# {RUN_ID}\n\nReview-Lauf zur abgeschlossenen PBR-Nullmodell-Ausführung.\n\nNo new nullmodels were executed in this review run.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n`next_gate={NEXT_GATE}`\n",
        f"{RUN_ID}.md": f"# {RUN_ID}\n\n## Befund\n\nDie vorherige PSD-/Rang-6-Lagstruktur bleibt ein formaler Matrixbefund. Die Nullmodell-Ausführung zeigt zugleich, dass `lag_preserving_shuffle_null` die vollständige Struktur in `{critical['complete_reproduction_count']}/{critical['sample_count']}` Proben reproduziert.\n\n## Interpretation\n\nDamit trägt der aktuelle Befund keine stärkere Spezifitätsaussage über die lag-erhaltende Konstruktion hinaus.\n\n## Hypothese\n\nDer nächste sinnvolle Gate betrifft den Lag-Mechanismus und nicht eine weitere blinde Nullmodellserie.\n\n## Offene Lücke\n\nUngeklärt bleibt, ob die Lag-Klassenstruktur nur Index-/Ordnungsstruktur ist oder unabhängig formal motiviert werden kann.\n\n## Claim Boundary\n\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "RUN_COMMANDS_PBR_NULLMODEL_EXECUTION_RESULT_REVIEW01.md": f"# Run Commands\n\n```bash\nRUN_DIR=\"runs/{RUN_ID}\"\n.venv/bin/python \"$RUN_DIR/scripts/run_pbr_nullmodel_execution_result_review.py\" --repo-root . --run-dir \"$RUN_DIR\"\n.venv/bin/python \"$RUN_DIR/scripts/validate_pbr_nullmodel_execution_result_review.py\" \"$RUN_DIR\"\ngit diff --check\ngit status --short --untracked-files=all\n```\n\nDieser Review-Lauf fuehrt keine neuen Nullmodelle aus.\n",
        "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_SUMMARY_DE.md": f"# Result-Review Summary\n\n## Befund\n\n`{INPUT_RUN_ID}` wurde formal reviewt. Ergebnis: `{REVIEW_OUTCOME}`.\n\n## Interpretation\n\n`no_specificity` bedeutet hier: keine staerkere formale Spezifitaet ueber die lag-erhaltende Konstruktion hinaus.\n\n## Hypothese\n\nDie Lag-Klassenstruktur ist der naechste zu pruefende Mechanismus.\n\n## Offene Lücke\n\nDie Eigenstaendigkeit des Lag-Mechanismus ist ungeklaert.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_CLAIM_BOUNDARY_DE.md": f"# Claim Boundary\n\n## Befund\n\nDer Review setzt `claim_status=nullmodel_result_review_only`.\n\n## Interpretation\n\nErlaubt sind nur formale Aussagen zur Nullmodell-Reproduktion.\n\n## Hypothese\n\nPhysikalische Interpretation bleibt an separate Gates gebunden.\n\n## Offene Lücke\n\nKein physikalisches Gate wurde in diesem Lauf ausgefuehrt.\n\n## Claim Boundary\n\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_NEXT_GATE_DE.md": f"# Next Gate\n\n## Befund\n\nDer naechste Gate ist `{NEXT_GATE}`. Sekundaer: `{SECONDARY_NEXT_GATE}`.\n\n## Interpretation\n\nZu klaeren ist, ob Lag-Klassen eine reine Index-/Ordnungskonstruktion oder ein unabhaengig motivierter Mechanismus sind.\n\n## Hypothese\n\nErst danach ist eine strengere Spezifitaetspruefung sinnvoll.\n\n## Offene Lücke\n\nKeine Ausfuehrungsautorisierung fuer neue Nullmodelle in diesem Review.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_NULLMODEL_EXECUTION_RESULT_REVIEW_LAG_MECHANISM_DE.md": f"# Lag-Mechanismus Review\n\n## Befund\n\nDas lag-erhaltende Shuffle-Nullmodell reproduziert die vollstaendige Struktur in `{critical['complete_reproduction_count']}/{critical['sample_count']}` Proben.\n\n## Interpretation\n\nDie Lag-Klassenstruktur erscheint in der aktuellen Operationalisierung als tragender formaler Mechanismus des Befunds.\n\n## Hypothese\n\nEin naechster Lauf sollte diesen Mechanismus isoliert pruefen.\n\n## Offene Lücke\n\nUnklar ist, ob das Nullmodell genau passend, zu permissiv oder uebererhaltend ist.\n\n## Claim Boundary\n\nKeine physikalische Freigabe.\n",
    }
    for rel, text in docs.items():
        write_text(run_dir / rel, text)

    validation_placeholder = [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Run generator completed; execute validator."}]
    write_csv(run_dir / "validation/validation_results.csv", validation_placeholder, list(validation_placeholder[0].keys()))

    tables = {
        "pbr_nullmodel_execution_result_review_summary": (list(summary.keys()), [summary]),
        "pbr_nullmodel_execution_result_review_family": (list(family_rows[0].keys()), family_rows),
        "pbr_nullmodel_execution_result_review_critical_findings": (list(critical_rows[0].keys()), critical_rows),
        "pbr_nullmodel_execution_result_review_specificity": (list(specificity[0].keys()), specificity),
        "pbr_nullmodel_execution_result_review_claim_boundaries": (list(claim_rows[0].keys()), claim_rows),
        "pbr_nullmodel_execution_result_review_next_gate": (list(next_gate[0].keys()), next_gate),
        "pbr_nullmodel_execution_result_review_lineage": (list(lineage[0].keys()), lineage),
        "pbr_nullmodel_execution_result_review_validation": (list(validation_placeholder[0].keys()), []),
    }
    create_sql(run_dir, tables)

    print("PBR nullmodel execution result review created")
    print(f"run_id={RUN_ID}")
    print(f"review_outcome={REVIEW_OUTCOME}")
    print(f"critical_nullmodel=lag_preserving_shuffle_null")
    print(f"critical_nullmodel_reproduction={critical['complete_reproduction_count']}/{critical['sample_count']}")
    print("No new nullmodels were executed in this review run.")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    print(f"next_gate={NEXT_GATE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
