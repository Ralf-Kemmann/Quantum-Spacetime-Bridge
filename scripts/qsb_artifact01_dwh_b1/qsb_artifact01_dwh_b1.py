#!/usr/bin/env python3
"""Build the QSB-ARTIFACT01-DWH-B1 visualization panel registry dry run."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_artifact01_dwh_b1/qsb_artifact01_dwh_b1.py")
SCHEMA_PATH = REPO_ROOT / "scripts/qsb_artifact01_dwh_b1/schema.sql"
INPUT_PNG = REPO_ROOT / "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/20_combined_topology_organized_matrix_panel.png"
PRIOR_REGISTRY = REPO_ROOT / "runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz.sqlite"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-ARTIFACT01-DWH-B1"
DB_PATH = OUTPUT_DIR / "qsb_artifact01_viz_panel.sqlite"
GENERATOR_NAME = "qsb_artifact01_dwh_b1.py"
GENERATOR_VERSION = "0.1"
RUN_ID = "QSB-ARTIFACT01-DWH-B1"
SOURCE_RUN_ID = "QSB-EXTRACT03-VIZ02"
ARTIFACT_ID = "QSB-ART-EXTRACT03-VIZ02-COMBINED-TOPOLOGY-PANEL-0001"
TITLE = "QSB-EXTRACT03 VIZ02 combined topology panel"
CAPTION = "QSB-EXTRACT03-VIZ02 combined topology-organized matrix panel, PNG overview visualization artifact."
ADMISSIBLE_USE = (
    "Presentation-ready combined visualization panel for inspecting QSB-EXTRACT03 "
    "VIZ02 topology-organized relational matrix heatmap structure across multiple "
    "matrix kinds."
)
FORBIDDEN_USE = (
    "Do not present this combined panel as evidence for physical causality, "
    "spacetime emergence, validated physics, or QSB confirmation."
)
CLAIM_BOUNDARY_SUMMARY = (
    "Sandbox visualization panel artifact metadata registry only; no production "
    "mutation, no input PNG modification, no physics claim, no spacetime claim, "
    "no causality claim, and no RELALG computation."
)
EXPECTED_TARGET_IDS = [
    "QSB-ART-EXTRACT03-VIZ02-K-COMPONENT-ORDERED-HEATMAP-0001",
    "QSB-ART-EXTRACT03-VIZ02-DLOWER-COMPONENT-ORDERED-HEATMAP-0001",
    "QSB-ART-EXTRACT03-VIZ02-D-COMPONENT-ORDERED-HEATMAP-0001",
    "QSB-ART-EXTRACT03-VIZ02-STRENGTH-COMPONENT-ORDERED-HEATMAP-0001",
    "QSB-ART-EXTRACT03-VIZ02-EDGE-COMPONENT-ORDERED-HEATMAP-0001",
]
ALIASES = [
    "QSB-EXTRACT03",
    "QSB-EXTRACT03-VIZ02",
    "combined panel",
    "combined topology panel",
    "topology organized matrix panel",
    "component ordered panel",
    "heatmap panel",
    "matrix panel",
    "presentation candidate",
    "overview visualization",
    "Relationsmatrix",
    "Matrixpanel",
    "Übersichtsgrafik",
    "präsentationsbereit",
    "Komponentenordnung",
]
FORBIDDEN_CONFIRMATION_WORDING = [
    "proves QSB",
    "proves spacetime",
    "establishes causality",
    "confirms emergent spacetime",
    "validates physical theory",
    "demonstrates new gravity",
]
REPORT_PATHS = {
    "validation": OUTPUT_DIR / "qsb_artifact01_viz_panel_validation_report.json",
    "registry": OUTPUT_DIR / "qsb_artifact01_viz_panel_registry_report.md",
    "claim_risk": OUTPUT_DIR / "qsb_artifact01_viz_panel_claim_risk_report.md",
    "downloads": OUTPUT_DIR / "qsb_artifact01_viz_panel_downloads_report.md",
    "summary": OUTPUT_DIR / "QSB-ARTIFACT01-DWH-B1_RUN_SUMMARY.md",
    "manifest": OUTPUT_DIR / "qsb_artifact01_viz_panel_seed_manifest.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def language(alias: str) -> str:
    if any(ch in alias for ch in "äöüÄÖÜß") or alias in {"Relationsmatrix", "Matrixpanel", "Komponentenordnung"}:
        return "de"
    return "en"


def connect_fresh_database(force: bool) -> sqlite3.Connection:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists() and not force:
        raise FileExistsError(f"{rel(DB_PATH)} already exists; rerun with --force to replace sandbox outputs.")
    if force and OUTPUT_DIR.exists():
        for path in OUTPUT_DIR.iterdir():
            if path.is_file():
                path.unlink()
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return con


def prior_targets() -> tuple[list[str], str]:
    if not PRIOR_REGISTRY.exists():
        return [], "prior_registry_missing"
    con = sqlite3.connect(PRIOR_REGISTRY)
    try:
        rows = con.execute(
            "SELECT artifact_id FROM qsb_artifact WHERE artifact_id IN ({})".format(
                ",".join("?" for _ in EXPECTED_TARGET_IDS)
            ),
            EXPECTED_TARGET_IDS,
        ).fetchall()
    finally:
        con.close()
    found = sorted(row[0] for row in rows)
    if len(found) == len(EXPECTED_TARGET_IDS):
        return found, "created_external_relation_references"
    return found, "partial_external_relation_references"


def insert_panel(con: sqlite3.Connection, timestamp: str, png_hash: str) -> dict[str, object]:
    canonical_path = rel(INPUT_PNG)
    mime_type = mimetypes.guess_type(INPUT_PNG.name)[0] or "image/png"
    size_bytes = INPUT_PNG.stat().st_size
    notes = (
        "run_id=QSB-EXTRACT03-VIZ02; visualization_family=topology_organized_relational_matrix; "
        "matrix_kind=combined_panel; ordering_mode=component_ordered_overview; "
        "existing PNG registered as metadata; input file not modified."
    )
    con.execute(
        """
        INSERT INTO qsb_artifact (
            artifact_id, title, artifact_type, semantic_role, mime_type,
            file_extension, canonical_path, uri, content_hash, hash_algorithm,
            size_bytes, created_at, created_by, source_system, status, visibility,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ARTIFACT_ID,
            TITLE,
            "image_png",
            "combined_visual_panel",
            mime_type,
            ".png",
            canonical_path,
            canonical_path,
            png_hash,
            "sha256",
            size_bytes,
            timestamp,
            GENERATOR_NAME,
            SOURCE_RUN_ID,
            "registered",
            "internal",
            notes,
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_version VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            f"{ARTIFACT_ID}-V001",
            ARTIFACT_ID,
            "v0.1",
            canonical_path,
            png_hash,
            timestamp,
            GENERATOR_NAME,
            GENERATOR_VERSION,
            None,
            "Initial sandbox visualization panel artifact registry dry-run version.",
            "active",
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_lineage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            f"{ARTIFACT_ID}-LIN-001",
            ARTIFACT_ID,
            "run_artifact",
            canonical_path,
            None,
            None,
            None,
            SOURCE_RUN_ID,
            "visualization_context",
            "Existing QSB-EXTRACT03 VIZ02 combined topology panel PNG registered as artifact metadata; file not modified.",
            "active",
        ),
    )
    for idx, alias in enumerate(ALIASES, start=1):
        con.execute(
            "INSERT INTO qsb_artifact_alias VALUES (?, ?, ?, ?, ?, ?)",
            (f"{ARTIFACT_ID}-ALIAS-{idx:03d}", ARTIFACT_ID, alias, language(alias), "search_alias", "active"),
        )
    con.execute(
        "INSERT INTO qsb_artifact_text_index VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            f"{ARTIFACT_ID}-TEXT-001",
            ARTIFACT_ID,
            "caption",
            "en",
            None,
            sha256_text(CAPTION),
            CAPTION,
            "filename_path_metadata",
            "not_text_extractable",
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_claim_boundary VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            f"{ARTIFACT_ID}-BOUNDARY-001",
            ARTIFACT_ID,
            ADMISSIBLE_USE,
            FORBIDDEN_USE,
            "high",
            "unreviewed",
            "Combined overview panels are presentation-ready and require explicit claim boundaries.",
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_export VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            f"{ARTIFACT_ID}-EXPORT-001",
            ARTIFACT_ID,
            "png",
            canonical_path,
            timestamp,
            GENERATOR_NAME,
            GENERATOR_VERSION,
            png_hash,
            TITLE,
            "registered_internal_export",
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_review VALUES (?, ?, ?, ?, ?, ?)",
        (
            f"{ARTIFACT_ID}-REVIEW-001",
            ARTIFACT_ID,
            "implementation_self_check",
            "unreviewed",
            "Registered by sandbox visualization panel artifact registry; human review pending.",
            timestamp,
        ),
    )
    return {"artifact_id": ARTIFACT_ID, "canonical_path": canonical_path, "content_hash": png_hash, "size_bytes": size_bytes}


def insert_relations(con: sqlite3.Connection, found_targets: list[str]) -> None:
    for idx, target_id in enumerate(found_targets, start=1):
        external_placeholder_id = f"EXTERNAL-B::{target_id}"
        con.execute(
            """
            INSERT INTO qsb_artifact (
                artifact_id, title, artifact_type, semantic_role, mime_type,
                file_extension, canonical_path, uri, content_hash, hash_algorithm,
                size_bytes, created_at, created_by, source_system, status,
                visibility, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                external_placeholder_id,
                f"External B registry reference: {target_id}",
                "external_reference",
                "prior_registry_heatmap_reference",
                None,
                None,
                rel(PRIOR_REGISTRY),
                target_id,
                "external-reference-no-local-content-hash",
                "external_reference",
                None,
                utc_now(),
                GENERATOR_NAME,
                "QSB-ARTIFACT01-DWH-B",
                "external_reference",
                "internal",
                "external_relation_reference to prior B registry; prior registry not mutated.",
            ),
        )
        con.execute(
            "INSERT INTO qsb_artifact_relation VALUES (?, ?, ?, ?, ?, ?)",
            (
                f"{ARTIFACT_ID}-REL-{idx:03d}",
                ARTIFACT_ID,
                external_placeholder_id,
                "panel_of",
                f"external_relation_reference:{target_id}",
                "external_relation_reference",
            ),
        )


def scalar(con: sqlite3.Connection, query: str, params: tuple[object, ...] = ()) -> int:
    return int(con.execute(query, params).fetchone()[0])


def table_counts(con: sqlite3.Connection) -> dict[str, int]:
    tables = [
        "qsb_artifact",
        "qsb_artifact_version",
        "qsb_artifact_lineage",
        "qsb_artifact_relation",
        "qsb_artifact_alias",
        "qsb_artifact_text_index",
        "qsb_artifact_claim_boundary",
        "qsb_artifact_export",
        "qsb_artifact_review",
        "qsb_artifact_validation_result",
    ]
    return {table: scalar(con, f"SELECT COUNT(*) FROM {table}") for table in tables}


def add_result(results: list[dict[str, str]], rule_id: str, severity: str, status: str, message: str, timestamp: str) -> None:
    results.append({"validation_id": f"QSB-ARTIFACT01-B1-VAL-{rule_id}", "rule_id": rule_id, "severity": severity, "status": status, "message": message, "checked_at": timestamp})


def validate(con: sqlite3.Connection, before_hash: str, after_hash: str, relation_status: str, found_targets: list[str], timestamp: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    add_result(results, "V01", "error", "pass" if INPUT_PNG.exists() else "fail", "Required panel PNG exists.", timestamp)
    add_result(results, "V02", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact WHERE artifact_id = ? AND content_hash != ''", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has content_hash.", timestamp)
    add_result(results, "V03", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact WHERE artifact_id = ? AND canonical_path != ''", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has canonical_path.", timestamp)
    add_result(results, "V04", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact WHERE artifact_id = ? AND artifact_type != '' AND semantic_role != ''", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has artifact_type and semantic_role.", timestamp)
    add_result(results, "V05", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact_version WHERE artifact_id = ? AND content_hash != ''", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has a version with content_hash.", timestamp)
    add_result(results, "V06", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact_claim_boundary WHERE artifact_id = ?", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has a claim boundary.", timestamp)
    add_result(results, "V07", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact_claim_boundary WHERE artifact_id = ? AND overclaim_risk = 'high' AND forbidden_use != ''", (ARTIFACT_ID,)) == 1 else "fail", "High-risk panel artifact has forbidden_use filled.", timestamp)
    add_result(results, "V08", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact_lineage WHERE artifact_id = ?", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has lineage.", timestamp)
    add_result(results, "V09", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact_review WHERE artifact_id = ?", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has review record.", timestamp)
    add_result(results, "V10", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact_text_index WHERE artifact_id = ? AND text_role = 'caption' AND extraction_status = 'not_text_extractable'", (ARTIFACT_ID,)) == 1 else "fail", "Panel artifact has text-index caption record.", timestamp)
    add_result(results, "V11", "error", "pass" if scalar(con, "SELECT COUNT(*) FROM qsb_artifact_export WHERE artifact_id = ? AND content_hash != '' AND output_path != ''", (ARTIFACT_ID,)) == 1 else "fail", "Export has content_hash and output_path.", timestamp)
    offending = []
    for phrase in FORBIDDEN_CONFIRMATION_WORDING:
        count = scalar(
            con,
            """
            SELECT COUNT(*) FROM (
                SELECT title AS text_value FROM qsb_artifact
                UNION ALL SELECT COALESCE(notes, '') FROM qsb_artifact
                UNION ALL SELECT admissible_use FROM qsb_artifact_claim_boundary
                UNION ALL SELECT COALESCE(excerpt, '') FROM qsb_artifact_text_index
                UNION ALL SELECT COALESCE(transformation_summary, '') FROM qsb_artifact_lineage
            )
            WHERE lower(text_value) LIKE ?
            """,
            (f"%{phrase.lower()}%",),
        )
        if count:
            offending.append(phrase)
    add_result(results, "V12", "error", "pass" if not offending else "fail", "No non-warning artifact text contains forbidden confirmation wording.", timestamp)
    add_result(results, "V13", "error", "pass" if before_hash == after_hash else "fail", "Input PNG hash before and after registration is identical.", timestamp)
    if relation_status == "created_external_relation_references":
        add_result(results, "V14", "warning", "pass", f"External relation references created for {len(found_targets)} prior B heatmap artifacts.", timestamp)
    elif found_targets:
        add_result(results, "V14", "warning", "warning", f"Partial external relation references created for {len(found_targets)} prior B heatmap artifacts.", timestamp)
    else:
        add_result(results, "V14", "warning", "warning", "Prior B registry relation links unavailable; no external relation references created.", timestamp)
    for result in results:
        con.execute("INSERT INTO qsb_artifact_validation_result VALUES (?, ?, ?, ?, ?, ?)", (result["validation_id"], result["rule_id"], result["severity"], result["status"], result["message"], result["checked_at"]))
    return results


def validation_status(results: list[dict[str, str]]) -> str:
    if any(row["status"] == "fail" for row in results):
        return "fail"
    if any(row["status"] == "warning" for row in results):
        return "warning"
    return "pass"


def markdown_table(headers: list[str], body: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in body)
    return "\n".join(lines)


def write_reports(con: sqlite3.Connection, record: dict[str, object], results: list[dict[str, str]], relation_status: str, found_targets: list[str], timestamp: str) -> None:
    relation_rows = [[row["relation_id"], row["target_artifact_id"], row["relation_type"], row["status"], row["relation_label"]] for row in con.execute("SELECT * FROM qsb_artifact_relation ORDER BY relation_id")]
    registry_text = dedent(f"""\
        # QSB-ARTIFACT01-DWH-B1 Panel Registry Report

        Generated at: {timestamp}

        Sandbox status: visualization panel artifact metadata registry dry run only.

        ## Registered Panel Artifact

        {markdown_table(["artifact_id", "hash", "size_bytes", "canonical_path"], [[record["artifact_id"], record["content_hash"], record["size_bytes"], record["canonical_path"]]])}

        ## Lineage Summary

        {markdown_table(["source_type", "source_ref", "run_id", "evidence_role"], [[row["source_type"], row["source_ref"], row["run_id"], row["evidence_role"]] for row in con.execute("SELECT source_type, source_ref, run_id, evidence_role FROM qsb_artifact_lineage")])}

        ## Relation Summary

        Prior registry relation status: {relation_status}

        {markdown_table(["relation_id", "target_artifact_id", "relation_type", "status", "relation_label"], relation_rows) if relation_rows else "- No relation references created."}

        No production DWH mutation was performed.

        Input PNG was not modified.
        """)
    REPORT_PATHS["registry"].write_text(registry_text, encoding="utf-8")
    claim = con.execute(
        "SELECT admissible_use, forbidden_use, overclaim_risk, review_status FROM qsb_artifact_claim_boundary WHERE artifact_id = ?",
        (ARTIFACT_ID,),
    ).fetchone()
    REPORT_PATHS["claim_risk"].write_text(dedent(f"""\
        # QSB-ARTIFACT01-DWH-B1 Claim Risk Report

        Generated at: {timestamp}

        {markdown_table(["artifact_id", "admissible_use", "forbidden_use", "overclaim_risk", "review_status"], [[ARTIFACT_ID, claim["admissible_use"], claim["forbidden_use"], claim["overclaim_risk"], claim["review_status"]]])}
        """), encoding="utf-8")
    download = con.execute(
        """
        SELECT e.download_label, e.output_path, e.content_hash, a.visibility, r.review_status
        FROM qsb_artifact_export AS e
        JOIN qsb_artifact AS a ON a.artifact_id = e.artifact_id
        JOIN qsb_artifact_review AS r ON r.artifact_id = e.artifact_id
        WHERE e.artifact_id = ?
        """,
        (ARTIFACT_ID,),
    ).fetchone()
    REPORT_PATHS["downloads"].write_text(dedent(f"""\
        # QSB-ARTIFACT01-DWH-B1 Downloads Report

        Generated at: {timestamp}

        No public publishing authorized. This is a registered internal PNG export only.

        {markdown_table(["download_label", "output_path", "hash", "visibility", "review_status"], [[download["download_label"], download["output_path"], download["content_hash"], download["visibility"], download["review_status"]]])}
        """), encoding="utf-8")
    validation = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": validation_status(results),
        "prior_registry_relation_status": relation_status,
        "prior_registry_targets_found": found_targets,
        "results": results,
        "row_counts": table_counts(con),
        "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
    }
    REPORT_PATHS["validation"].write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    created = [rel(DB_PATH), *(rel(path) for path in REPORT_PATHS.values())]
    REPORT_PATHS["summary"].write_text(dedent(f"""\
        # QSB-ARTIFACT01-DWH-B1 Run Summary

        Generated at: {timestamp}

        ## Purpose

        Register the QSB-EXTRACT03 VIZ02 combined topology panel PNG as a sandbox visualization panel artifact.

        ## Files Created

        {chr(10).join(f"- {path}" for path in created)}

        ## Input Registered

        - {record["canonical_path"]} -> {record["artifact_id"]}

        ## Validation Summary

        Status: {validation_status(results)}

        {chr(10).join(f"- {row['rule_id']}: {row['status']} ({row['severity']}) - {row['message']}" for row in results)}

        ## Prior Registry Relation Status

        {relation_status}; targets found: {len(found_targets)}.

        ## No Production Mutation Statement

        This run created a standalone sandbox registry under `runs/QSB-ARTIFACT01-DWH-B1/` and did not mutate production DWH, Source-Hub, EXTRACT, META, MAP01, ARTIFACT01-A/B, or existing project schemas.

        ## No Input PNG Modification Statement

        The input PNG hash before and after registration was identical.

        ## No Physics Claim Statement

        This dry run registers visualization panel artifact metadata only. It introduces no physical, spacetime, causality, RELALG computation, or QSB-confirmation claim.

        ## Next Allowed Step

        Human review may inspect the panel registry, claim-risk report, and external relation references before any further metadata integration is considered.
        """), encoding="utf-8")
    report_hashes = {name: sha256_file(path) for name, path in REPORT_PATHS.items() if name != "manifest" and path.exists()}
    manifest = {
        "run_id": RUN_ID,
        "script_path": str(SCRIPT_PATH),
        "input_png": rel(INPUT_PNG),
        "optional_prior_registry_path": rel(PRIOR_REGISTRY),
        "output_directory": rel(OUTPUT_DIR),
        "registered_artifact_id": ARTIFACT_ID,
        "row_counts_per_table": table_counts(con),
        "generated_report_paths": {name: rel(path) for name, path in REPORT_PATHS.items() if name != "manifest"},
        "hashes_of_generated_reports": report_hashes,
        "validation_status": validation_status(results),
        "timestamp": timestamp,
        "sandbox_only_claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
    }
    REPORT_PATHS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(force: bool) -> None:
    if not INPUT_PNG.exists():
        raise FileNotFoundError(f"Required input PNG is missing: {rel(INPUT_PNG)}")
    timestamp = utc_now()
    before_hash = sha256_file(INPUT_PNG)
    found_targets, relation_status = prior_targets()
    con = connect_fresh_database(force)
    try:
        record = insert_panel(con, timestamp, before_hash)
        insert_relations(con, found_targets)
        after_hash = sha256_file(INPUT_PNG)
        results = validate(con, before_hash, after_hash, relation_status, found_targets, timestamp)
        con.commit()
        write_reports(con, record, results, relation_status, found_targets, timestamp)
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace files inside runs/QSB-ARTIFACT01-DWH-B1 only.")
    args = parser.parse_args()
    try:
        build(force=args.force)
    except (FileNotFoundError, FileExistsError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
