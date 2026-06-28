#!/usr/bin/env python3
"""Build the QSB-ARTIFACT01-DWH-B visualization artifact registry dry run."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_artifact01_dwh_b/qsb_artifact01_dwh_b.py")
SCHEMA_PATH = REPO_ROOT / "scripts/qsb_artifact01_dwh_b/schema.sql"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-ARTIFACT01-DWH-B"
DB_PATH = OUTPUT_DIR / "qsb_artifact01_viz.sqlite"
GENERATOR_NAME = "qsb_artifact01_dwh_b.py"
GENERATOR_VERSION = "0.1"
RUN_ID = "QSB-ARTIFACT01-DWH-B"
CLAIM_BOUNDARY_SUMMARY = (
    "Sandbox visualization artifact metadata registry only; no production "
    "mutation, no physics claim, no spacetime claim, no causality claim, "
    "and no RELALG computation."
)
ADMISSIBLE_USE = (
    "Presentation-ready visualization artifact for inspecting QSB-EXTRACT03 "
    "relational matrix structure, matrix ordering, component organization, "
    "or heatmap patterns."
)
FORBIDDEN_USE = (
    "Do not present this heatmap as evidence for physical causality, spacetime "
    "emergence, validated physics, or QSB confirmation."
)
FORBIDDEN_CONFIRMATION_WORDING = [
    "proves QSB",
    "proves spacetime",
    "establishes causality",
    "confirms emergent spacetime",
    "validates physical theory",
    "demonstrates new gravity",
]
VIZ01_ROOT = REPO_ROOT / "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization"
VIZ02_ROOT = REPO_ROOT / "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix"
ALLOWED_ROOTS = [VIZ01_ROOT, VIZ02_ROOT]
EXPECTED_FILES = [
    "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/16_d_component_ordered_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/17_D_component_ordered_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/18_strength_component_ordered_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/19_edge_component_ordered_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/15_K_component_ordered_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/11_K_unsorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/12_K_split_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/13_K_cluster_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/14_d_unsorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/15_d_split_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/16_d_cluster_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/17_D_unsorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/18_D_split_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/19_D_cluster_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/20_strength_unsorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/21_strength_split_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/22_strength_cluster_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/23_edge_unsorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/24_edge_split_sorted_heatmap.png",
    "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/25_edge_cluster_sorted_heatmap.png",
]
BASE_ALIASES = [
    "QSB-EXTRACT03",
    "heatmap",
    "matrix heatmap",
    "relational matrix",
    "visualization",
    "presentation candidate",
    "Heatmap",
    "Wärmekarte",
    "Matrixgrafik",
    "Relationsmatrix",
    "Komponentenordnung",
    "Clusterordnung",
    "präsentationsbereit",
]
REPORT_PATHS = {
    "validation": OUTPUT_DIR / "qsb_artifact01_viz_validation_report.json",
    "registry": OUTPUT_DIR / "qsb_artifact01_viz_registry_report.md",
    "claim_risk": OUTPUT_DIR / "qsb_artifact01_viz_claim_risk_report.md",
    "downloads": OUTPUT_DIR / "qsb_artifact01_viz_downloads_report.md",
    "gallery": OUTPUT_DIR / "qsb_artifact01_viz_gallery_index.md",
    "summary": OUTPUT_DIR / "QSB-ARTIFACT01-DWH-B_RUN_SUMMARY.md",
    "manifest": OUTPUT_DIR / "qsb_artifact01_viz_seed_manifest.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lang(alias: str) -> str:
    if any(ch in alias for ch in "äöüÄÖÜß") or alias in {"Matrixgrafik", "Relationsmatrix", "Komponentenordnung", "Clusterordnung"}:
        return "de"
    return "en"


def connect_fresh_database(force: bool) -> sqlite3.Connection:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists() and not force:
        raise FileExistsError(f"{rel(DB_PATH)} already exists; rerun with --force to replace sandbox outputs.")
    if force:
        for path in OUTPUT_DIR.iterdir():
            if path.is_file():
                path.unlink()
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return con


def parse_metadata(path: Path) -> dict[str, str]:
    filename = path.name
    if "QSB-EXTRACT03-VIZ01" in rel(path):
        run_id = "QSB-EXTRACT03-VIZ01"
        family = "matrix_heatmap_visualization"
        match = re.match(r"^\d+_(K|d|D|strength|edge)_(unsorted|split_sorted|cluster_sorted)_heatmap\.png$", filename)
    else:
        run_id = "QSB-EXTRACT03-VIZ02"
        family = "topology_organized_relational_matrix"
        match = re.match(r"^\d+_(K|d|D|strength|edge)_component_ordered_heatmap\.png$", filename)
    if not match:
        raise ValueError(f"Cannot parse expected heatmap filename: {filename}")
    matrix_kind = match.group(1)
    ordering_mode = match.group(2) if run_id.endswith("VIZ01") else "component_ordered"
    return {
        "run_id": run_id,
        "visualization_family": family,
        "matrix_kind": matrix_kind,
        "ordering_mode": ordering_mode,
    }


def artifact_id(meta: dict[str, str]) -> str:
    matrix = {"d": "DLOWER", "D": "D"}.get(meta["matrix_kind"], meta["matrix_kind"].upper())
    ordering = meta["ordering_mode"].upper().replace("_", "-")
    if meta["run_id"].endswith("VIZ02"):
        return f"QSB-ART-EXTRACT03-VIZ02-{matrix}-COMPONENT-ORDERED-HEATMAP-0001"
    return f"QSB-ART-EXTRACT03-VIZ01-{matrix}-{ordering}-HEATMAP-0001"


def title(meta: dict[str, str]) -> str:
    ordering = meta["ordering_mode"].replace("_", "-")
    return f"{meta['run_id']} {meta['matrix_kind']} matrix heatmap ({ordering})"


def caption(meta: dict[str, str]) -> str:
    ordering = meta["ordering_mode"].replace("_", "-")
    return f"{meta['run_id']} {meta['matrix_kind']} matrix heatmap, {ordering} ordering, PNG visualization artifact."


def aliases_for(meta: dict[str, str]) -> list[str]:
    ordering = meta["ordering_mode"].replace("_", " ")
    matrix = meta["matrix_kind"]
    aliases = [
        *BASE_ALIASES,
        meta["run_id"],
        meta["visualization_family"],
        matrix,
        f"{matrix} matrix",
        ordering,
    ]
    if meta["ordering_mode"] == "component_ordered":
        aliases.append("topology organized")
    return list(dict.fromkeys(aliases))


def insert_artifact(con: sqlite3.Connection, path: Path, timestamp: str) -> dict[str, str | int]:
    meta = parse_metadata(path)
    aid = artifact_id(meta)
    canonical_path = rel(path)
    content_hash = sha256_file(path)
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    notes = (
        f"run_id={meta['run_id']}; visualization_family={meta['visualization_family']}; "
        f"matrix_kind={meta['matrix_kind']}; ordering_mode={meta['ordering_mode']}; "
        "existing PNG registered as metadata; source file not modified."
    )
    record = {
        **meta,
        "artifact_id": aid,
        "title": title(meta),
        "path": path,
        "canonical_path": canonical_path,
        "content_hash": content_hash,
        "size_bytes": path.stat().st_size,
        "mime_type": mime_type,
        "file_extension": ".png",
        "caption": caption(meta),
    }
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
            aid,
            record["title"],
            "image_png",
            "matrix_heatmap_visualization",
            mime_type,
            ".png",
            canonical_path,
            canonical_path,
            content_hash,
            "sha256",
            record["size_bytes"],
            timestamp,
            GENERATOR_NAME,
            meta["run_id"],
            "registered",
            "internal",
            notes,
        ),
    )
    con.execute(
        """
        INSERT INTO qsb_artifact_version (
            artifact_version_id, artifact_id, version, canonical_path,
            content_hash, generated_at, generator_name, generator_version,
            supersedes_version_id, change_summary, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"{aid}-V001",
            aid,
            "v0.1",
            canonical_path,
            content_hash,
            timestamp,
            GENERATOR_NAME,
            GENERATOR_VERSION,
            None,
            "Initial sandbox visualization artifact registry dry-run version.",
            "active",
        ),
    )
    con.execute(
        """
        INSERT INTO qsb_artifact_lineage (
            lineage_id, artifact_id, source_type, source_ref, source_artifact_id,
            source_table, source_query, run_id, evidence_role,
            transformation_summary, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"{aid}-LIN-001",
            aid,
            "run_artifact",
            canonical_path,
            None,
            None,
            None,
            meta["run_id"],
            "visualization_context",
            "Existing QSB-EXTRACT03 visualization PNG registered as artifact metadata; file not modified.",
            "active",
        ),
    )
    return record


def insert_supporting_rows(con: sqlite3.Connection, record: dict[str, str | int], timestamp: str) -> None:
    aid = str(record["artifact_id"])
    for idx, alias in enumerate(aliases_for({k: str(record[k]) for k in ("run_id", "visualization_family", "matrix_kind", "ordering_mode")}), start=1):
        con.execute(
            "INSERT INTO qsb_artifact_alias VALUES (?, ?, ?, ?, ?, ?)",
            (f"{aid}-ALIAS-{idx:03d}", aid, alias, lang(alias), "search_alias", "active"),
        )
    con.execute(
        "INSERT INTO qsb_artifact_text_index VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            f"{aid}-TEXT-001",
            aid,
            "caption",
            "en",
            None,
            sha256_text(str(record["caption"])),
            str(record["caption"]),
            "filename_path_metadata",
            "not_text_extractable",
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_claim_boundary VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            f"{aid}-BOUNDARY-001",
            aid,
            ADMISSIBLE_USE,
            FORBIDDEN_USE,
            "high",
            "unreviewed",
            "Visual artifact claim boundary; human review pending before any broader use.",
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_export VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            f"{aid}-EXPORT-001",
            aid,
            "png",
            str(record["canonical_path"]),
            timestamp,
            GENERATOR_NAME,
            GENERATOR_VERSION,
            str(record["content_hash"]),
            str(record["title"]),
            "registered_internal_export",
        ),
    )
    con.execute(
        "INSERT INTO qsb_artifact_review VALUES (?, ?, ?, ?, ?, ?)",
        (
            f"{aid}-REVIEW-001",
            aid,
            "implementation_self_check",
            "unreviewed",
            "Registered by sandbox visualization artifact registry; human review pending.",
            timestamp,
        ),
    )


def insert_relations(con: sqlite3.Connection, by_key: dict[tuple[str, str, str], dict[str, str | int]]) -> None:
    relation_idx = 1
    for matrix in ["K", "d", "D", "strength", "edge"]:
        chain = ["unsorted", "split_sorted", "cluster_sorted"]
        for source_mode, target_mode in zip(chain, chain[1:]):
            source = by_key.get(("QSB-EXTRACT03-VIZ01", matrix, source_mode))
            target = by_key.get(("QSB-EXTRACT03-VIZ01", matrix, target_mode))
            if source and target:
                con.execute(
                    "INSERT INTO qsb_artifact_relation VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        f"QSB-ARTIFACT01-VIZ-REL-{relation_idx:03d}",
                        str(source["artifact_id"]),
                        str(target["artifact_id"]),
                        "ordering_variant_of",
                        f"{matrix} heatmap ordering variant sequence.",
                        "active",
                    ),
                )
                relation_idx += 1
        source = by_key.get(("QSB-EXTRACT03-VIZ02", matrix, "component_ordered"))
        target = by_key.get(("QSB-EXTRACT03-VIZ01", matrix, "cluster_sorted"))
        if source and target:
            con.execute(
                "INSERT INTO qsb_artifact_relation VALUES (?, ?, ?, ?, ?, ?)",
                (
                    f"QSB-ARTIFACT01-VIZ-REL-{relation_idx:03d}",
                    str(source["artifact_id"]),
                    str(target["artifact_id"]),
                    "topology_variant_of",
                    f"{matrix} component-ordered heatmap relates to the cluster-sorted heatmap.",
                    "active",
                ),
            )
            relation_idx += 1


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
    return {name: int(con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]) for name in tables}


def scalar(con: sqlite3.Connection, query: str, params: tuple[object, ...] = ()) -> int:
    return int(con.execute(query, params).fetchone()[0])


def add_result(results: list[dict[str, str]], rule_id: str, severity: str, status: str, message: str, timestamp: str) -> None:
    results.append({"validation_id": f"QSB-ARTIFACT01-VIZ-VAL-{rule_id}", "rule_id": rule_id, "severity": severity, "status": status, "message": message, "checked_at": timestamp})


def validate(con: sqlite3.Connection, missing_inputs: list[str], timestamp: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    checks = [
        ("V01", "error", "SELECT COUNT(*) FROM qsb_artifact WHERE content_hash = '' OR content_hash IS NULL", "Every artifact has content_hash."),
        ("V02", "error", "SELECT COUNT(*) FROM qsb_artifact WHERE canonical_path = '' OR canonical_path IS NULL", "Every artifact has canonical_path."),
        ("V03", "error", "SELECT COUNT(*) FROM qsb_artifact WHERE artifact_type = '' OR semantic_role = ''", "Every artifact has artifact_type and semantic_role."),
        ("V04", "error", "SELECT COUNT(*) FROM qsb_artifact_version WHERE content_hash = '' OR content_hash IS NULL", "Every artifact version has content_hash."),
        ("V07", "error", "SELECT COUNT(*) FROM qsb_artifact_claim_boundary WHERE overclaim_risk IN ('high', 'critical') AND (forbidden_use = '' OR forbidden_use IS NULL)", "Every high-risk artifact has forbidden_use filled."),
        ("V10", "error", "SELECT COUNT(*) FROM qsb_artifact_text_index WHERE extraction_status = '' OR extraction_status IS NULL", "Every text-indexed artifact has extraction_status."),
        ("V13", "error", "SELECT COUNT(*) FROM qsb_artifact_export WHERE content_hash = '' OR content_hash IS NULL OR output_path = '' OR output_path IS NULL", "Every export has content_hash and output_path."),
        ("V14", "error", "SELECT COUNT(*) FROM qsb_artifact_lineage WHERE source_type = 'run_artifact' AND (run_id = '' OR run_id IS NULL)", "Every artifact linked to run_artifact has run_id."),
    ]
    for rule_id, severity, query, message in checks:
        add_result(results, rule_id, severity, "pass" if scalar(con, query) == 0 else "fail", message, timestamp)
    missing_versions = scalar(con, "SELECT COUNT(*) FROM qsb_artifact AS a WHERE NOT EXISTS (SELECT 1 FROM qsb_artifact_version AS v WHERE v.artifact_id = a.artifact_id)")
    add_result(results, "V05", "error", "pass" if missing_versions == 0 else "fail", "Every registered artifact has at least one version.", timestamp)
    missing_boundaries = scalar(con, "SELECT COUNT(*) FROM qsb_artifact AS a WHERE NOT EXISTS (SELECT 1 FROM qsb_artifact_claim_boundary AS b WHERE b.artifact_id = a.artifact_id)")
    add_result(results, "V06", "error", "pass" if missing_boundaries == 0 else "fail", "Every artifact has a claim boundary.", timestamp)
    no_context = scalar(con, "SELECT COUNT(*) FROM qsb_artifact_export AS e WHERE (e.generator_name IS NULL OR e.generator_name = '') AND NOT EXISTS (SELECT 1 FROM qsb_artifact_lineage AS l WHERE l.artifact_id = e.artifact_id)")
    add_result(results, "V08", "error", "pass" if no_context == 0 else "fail", "Every generated export has lineage or generator metadata.", timestamp)
    broken_relations = scalar(con, "SELECT COUNT(*) FROM qsb_artifact_relation AS r LEFT JOIN qsb_artifact AS s ON s.artifact_id = r.source_artifact_id LEFT JOIN qsb_artifact AS t ON t.artifact_id = r.target_artifact_id WHERE s.artifact_id IS NULL OR t.artifact_id IS NULL")
    add_result(results, "V09", "error", "pass" if broken_relations == 0 else "fail", "Every artifact relation references existing artifacts.", timestamp)
    missing_reviews = scalar(con, "SELECT COUNT(*) FROM qsb_artifact AS a WHERE NOT EXISTS (SELECT 1 FROM qsb_artifact_review AS r WHERE r.artifact_id = a.artifact_id)")
    add_result(results, "V11", "error", "pass" if missing_reviews == 0 else "fail", "Every registered artifact has a review record.", timestamp)
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
    if missing_inputs:
        add_result(results, "V15", "warning", "warning", f"Missing expected PNG files: {', '.join(missing_inputs)}.", timestamp)
    else:
        add_result(results, "V15", "warning", "pass", "No expected PNG files are missing.", timestamp)
    allowed_prefixes = tuple(f"{rel(root)}/" for root in ALLOWED_ROOTS)
    bad_roots = scalar(
        con,
        "SELECT COUNT(*) FROM qsb_artifact WHERE file_extension != '.png' OR mime_type != 'image/png' OR (canonical_path NOT LIKE ? AND canonical_path NOT LIKE ?)",
        (f"{allowed_prefixes[0]}%", f"{allowed_prefixes[1]}%"),
    )
    add_result(results, "V16", "error", "pass" if bad_roots == 0 else "fail", "All registered artifacts are PNG files from the allowed input roots.", timestamp)
    for result in sorted(results, key=lambda row: int(row["rule_id"][1:])):
        con.execute("INSERT INTO qsb_artifact_validation_result VALUES (?, ?, ?, ?, ?, ?)", (result["validation_id"], result["rule_id"], result["severity"], result["status"], result["message"], result["checked_at"]))
    return sorted(results, key=lambda row: int(row["rule_id"][1:]))


def validation_status(results: list[dict[str, str]]) -> str:
    if any(row["status"] == "fail" for row in results):
        return "fail"
    if any(row["status"] == "warning" for row in results):
        return "warning"
    return "pass"


def rows(con: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    return list(con.execute(query))


def markdown_table(headers: list[str], body: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in body)
    return "\n".join(lines)


def write_reports(con: sqlite3.Connection, records: list[dict[str, str | int]], results: list[dict[str, str]], missing_inputs: list[str], timestamp: str) -> None:
    artifact_rows = [[r["artifact_id"], r["run_id"], r["matrix_kind"], r["ordering_mode"], r["canonical_path"], r["size_bytes"]] for r in records]
    by_run = rows(con, "SELECT source_system AS run_id, COUNT(*) AS count FROM qsb_artifact GROUP BY source_system ORDER BY source_system")
    by_matrix = {}
    by_ordering = {}
    for record in records:
        by_matrix[str(record["matrix_kind"])] = by_matrix.get(str(record["matrix_kind"]), 0) + 1
        by_ordering[str(record["ordering_mode"])] = by_ordering.get(str(record["ordering_mode"]), 0) + 1
    lineage = rows(con, "SELECT run_id, source_type, COUNT(*) AS count FROM qsb_artifact_lineage GROUP BY run_id, source_type ORDER BY run_id")
    REPORT_PATHS["registry"].write_text(dedent(f"""\
        # QSB-ARTIFACT01-DWH-B Visualization Registry Report

        Generated at: {timestamp}

        Sandbox status: visualization artifact metadata registry dry run only.

        Registered PNG count: {len(records)}

        Missing expected input count: {len(missing_inputs)}

        ## Artifacts

        {markdown_table(["artifact_id", "run_id", "matrix_kind", "ordering_mode", "path", "size_bytes"], artifact_rows)}

        ## Counts By Run

        {markdown_table(["run_id", "count"], [[r["run_id"], r["count"]] for r in by_run])}

        ## Counts By Matrix Kind

        {markdown_table(["matrix_kind", "count"], sorted(by_matrix.items()))}

        ## Counts By Ordering Mode

        {markdown_table(["ordering_mode", "count"], sorted(by_ordering.items()))}

        ## Lineage Summary

        {markdown_table(["run_id", "source_type", "count"], [[r["run_id"], r["source_type"], r["count"]] for r in lineage])}

        No production DWH mutation was performed.
        """), encoding="utf-8")
    risk = rows(con, "SELECT a.artifact_id, a.title, b.admissible_use, b.forbidden_use, b.review_status FROM qsb_artifact AS a JOIN qsb_artifact_claim_boundary AS b ON b.artifact_id = a.artifact_id ORDER BY a.artifact_id")
    REPORT_PATHS["claim_risk"].write_text(dedent(f"""\
        # QSB-ARTIFACT01-DWH-B Claim Risk Report

        Generated at: {timestamp}

        All registered PNG artifacts are high risk because visual artifacts are presentation-ready.

        {markdown_table(["artifact_id", "title", "admissible_use", "forbidden_use", "review_status"], [[r["artifact_id"], r["title"], r["admissible_use"], r["forbidden_use"], r["review_status"]] for r in risk])}
        """), encoding="utf-8")
    downloads = rows(con, "SELECT e.download_label, e.output_path, e.content_hash, a.visibility, r.review_status FROM qsb_artifact_export AS e JOIN qsb_artifact AS a ON a.artifact_id = e.artifact_id JOIN qsb_artifact_review AS r ON r.artifact_id = e.artifact_id ORDER BY e.output_path")
    REPORT_PATHS["downloads"].write_text(dedent(f"""\
        # QSB-ARTIFACT01-DWH-B Downloads Report

        Generated at: {timestamp}

        No public publishing authorized. These are registered internal PNG exports only.

        {markdown_table(["download_label", "output_path", "hash", "visibility", "review_status"], [[r["download_label"], r["output_path"], r["content_hash"], r["visibility"], r["review_status"]] for r in downloads])}
        """), encoding="utf-8")
    gallery_lines = [
        "# QSB-ARTIFACT01-DWH-B Gallery Index",
        "",
        f"Generated at: {timestamp}",
        "",
        "Internal review-only gallery. This index is not a physics claim and does not authorize public publishing.",
    ]
    for run_id in ["QSB-EXTRACT03-VIZ01", "QSB-EXTRACT03-VIZ02"]:
        gallery_lines.extend(["", f"## {run_id}"])
        for matrix in ["K", "d", "D", "strength", "edge"]:
            subset = [r for r in records if r["run_id"] == run_id and r["matrix_kind"] == matrix]
            if not subset:
                continue
            gallery_lines.extend(["", f"### {matrix}"])
            for record in sorted(subset, key=lambda r: str(r["ordering_mode"])):
                image_link = "../" + str(record["canonical_path"]).removeprefix("runs/")
                gallery_lines.extend(["", f"![{record['caption']}]({image_link})", "", str(record["caption"])])
    REPORT_PATHS["gallery"].write_text("\n".join(gallery_lines) + "\n", encoding="utf-8")
    validation = {"run_id": RUN_ID, "timestamp": timestamp, "validation_status": validation_status(results), "missing_expected_inputs": missing_inputs, "results": results, "row_counts": table_counts(con), "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY}
    REPORT_PATHS["validation"].write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    created = [rel(DB_PATH), *(rel(path) for path in REPORT_PATHS.values())]
    REPORT_PATHS["summary"].write_text(dedent(f"""\
        # QSB-ARTIFACT01-DWH-B Run Summary

        Generated at: {timestamp}

        ## Purpose

        Create a sandbox-only SQLite artifact registry dry run for existing QSB-EXTRACT03 visualization PNG heatmaps.

        ## Files Created

        {chr(10).join(f"- {path}" for path in created)}

        ## Inputs Registered

        {chr(10).join(f"- {record['canonical_path']} -> {record['artifact_id']}" for record in records)}

        Registered count: {len(records)}

        ## Missing Inputs

        {chr(10).join(f"- {name}" for name in missing_inputs) if missing_inputs else "- None"}

        ## Validation Summary

        Status: {validation_status(results)}

        {chr(10).join(f"- {row['rule_id']}: {row['status']} ({row['severity']}) - {row['message']}" for row in results)}

        ## No Production Mutation Statement

        This run created a standalone sandbox registry under `runs/QSB-ARTIFACT01-DWH-B/` and did not mutate a production DWH, Source-Hub, EXTRACT, META, MAP01, ARTIFACT01-A, or existing project schema.

        ## No Physics Claim Statement

        This dry run registers visualization artifact metadata only. It introduces no physical, spacetime, causality, RELALG computation, or QSB-confirmation claim.

        ## Next Allowed Step

        Human review may inspect the registry tables, validation report, claim-risk report, and internal gallery index before any further metadata integration is considered.
        """), encoding="utf-8")
    report_hashes = {name: sha256_file(path) for name, path in REPORT_PATHS.items() if name != "manifest" and path.exists()}
    manifest = {
        "run_id": RUN_ID,
        "script_path": str(SCRIPT_PATH),
        "input_roots": [rel(root) for root in ALLOWED_ROOTS],
        "output_directory": rel(OUTPUT_DIR),
        "registered_artifact_ids": [str(record["artifact_id"]) for record in records],
        "row_counts_per_table": table_counts(con),
        "generated_report_paths": {name: rel(path) for name, path in REPORT_PATHS.items() if name != "manifest"},
        "hashes_of_generated_reports": report_hashes,
        "validation_status": validation_status(results),
        "timestamp": timestamp,
        "sandbox_only_claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
    }
    REPORT_PATHS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(force: bool) -> None:
    timestamp = utc_now()
    con = connect_fresh_database(force)
    records: list[dict[str, str | int]] = []
    by_key: dict[tuple[str, str, str], dict[str, str | int]] = {}
    missing_inputs: list[str] = []
    try:
        for expected in EXPECTED_FILES:
            path = REPO_ROOT / expected
            if not path.exists():
                missing_inputs.append(expected)
                continue
            record = insert_artifact(con, path, timestamp)
            insert_supporting_rows(con, record, timestamp)
            records.append(record)
            by_key[(str(record["run_id"]), str(record["matrix_kind"]), str(record["ordering_mode"]))] = record
        insert_relations(con, by_key)
        results = validate(con, missing_inputs, timestamp)
        con.commit()
        write_reports(con, records, results, missing_inputs, timestamp)
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace files inside runs/QSB-ARTIFACT01-DWH-B only.")
    args = parser.parse_args()
    build(force=args.force)


if __name__ == "__main__":
    main()
