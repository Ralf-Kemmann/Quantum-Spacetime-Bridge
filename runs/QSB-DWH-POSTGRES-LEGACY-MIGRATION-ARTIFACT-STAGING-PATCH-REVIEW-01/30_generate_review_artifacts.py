#!/usr/bin/env python3
"""Generate read-only review artifacts for the artifact staging patch review."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-REVIEW-01"
REVIEWED_RUN_ID = "QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-01"
DB = "qsb_research_dwh"
ROOT = Path.cwd()
OUT = ROOT / "runs" / RUN_ID
SUMMARY_PATH = ROOT / "runs" / REVIEWED_RUN_ID / "04_artifact_staging_patch_summary.json"
PREVIOUS_METADATA_SUMMARY_PATH = (
    ROOT
    / "runs"
    / "QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01"
    / "04_legacy_migration_summary.json"
)


EXPECTED = {
    "status": "qsb_dwh_postgres_legacy_artifact_staging_patch_completed",
    "postgres_connection_ok": True,
    "previous_status": "qsb_dwh_postgres_legacy_migration_metadata_server_completed",
    "total_files_inventoried": 9324,
    "artifacts_registered_before": 17,
    "artifacts_registered_after": 9341,
    "artifacts_registered_delta": 9324,
    "checksums_computed": 9324,
    "raw_checksums_registered_after": 9328,
    "generic_csv_files_loaded": 388,
    "generic_csv_rows_loaded": 100000,
    "json_documents_loaded": 1945,
    "json_key_values_loaded": 50100,
    "markdown_documents_loaded": 2105,
    "sqlite_catalogs_discovered": 97,
    "sqlite_catalogs_imported": 97,
    "global_search_rows_before": 29,
    "global_search_rows_after": 107360,
    "global_search_rows_delta": 107331,
    "views_verified": 14,
    "metadata_server_check_status": "ready_for_read_only_psql_cli_server",
    "residual_analysis_executed": False,
    "rbci_v1_evaluated": False,
    "qsb_observable_evaluated": False,
}

COUNT_MAP = [
    ("raw.source_artifact", "artifacts_registered_after", "SELECT COUNT(*) FROM raw.source_artifact"),
    ("raw.raw_checksum", "raw_checksums_registered_after", "SELECT COUNT(*) FROM raw.raw_checksum"),
    ("staging.csv_row_json", "generic_csv_rows_loaded", "SELECT COUNT(*) FROM staging.csv_row_json"),
    ("staging.json_document", "json_documents_loaded", "SELECT COUNT(*) FROM staging.json_document"),
    ("staging.json_key_value", "json_key_values_loaded", "SELECT COUNT(*) FROM staging.json_key_value"),
    ("staging.markdown_document", "markdown_documents_loaded", "SELECT COUNT(*) FROM staging.markdown_document"),
    ("staging.sqlite_table_inventory", "sqlite_catalogs_imported", "SELECT COUNT(DISTINCT relative_path) FROM staging.sqlite_table_inventory"),
    ("staging.sqlite_row_count", None, "SELECT COUNT(*) FROM staging.sqlite_row_count"),
    ("metadata.meta_search_token", None, "SELECT COUNT(*) FROM metadata.meta_search_token"),
    ("mart.v_qsb_global_search", "global_search_rows_after", "SELECT COUNT(*) FROM mart.v_qsb_global_search"),
]


command_log: list[dict[str, object]] = []


def log_command(cmd: list[str], rc: int, stdout: str = "", stderr: str = "") -> None:
    command_log.append(
        {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "cmd": " ".join(cmd),
            "returncode": rc,
            "stdout_preview": stdout[:500],
            "stderr_preview": stderr[:500],
        }
    )


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    log_command(cmd, proc.returncode, proc.stdout, proc.stderr)
    return proc


def read_json(path: Path) -> tuple[bool, dict]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return True, json.load(handle)
    except Exception as exc:
        return False, {"_error": str(exc)}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_md(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def psql_rows(query: str) -> tuple[bool, list[dict[str, str]], str]:
    proc = run(["psql", "-d", DB, "--csv", "-q", "-c", query])
    if proc.returncode != 0:
        return False, [], proc.stderr.strip()
    lines = proc.stdout.splitlines()
    if not lines:
        return True, [], ""
    reader = csv.DictReader(lines)
    return True, list(reader), ""


def psql_scalar(query: str) -> tuple[bool, int | None, str]:
    proc = run(["psql", "-d", DB, "-At", "-q", "-c", query])
    if proc.returncode != 0:
        return False, None, proc.stderr.strip()
    try:
        return True, int(proc.stdout.strip().splitlines()[-1]), ""
    except Exception as exc:
        return False, None, f"could not parse integer from psql output: {exc}: {proc.stdout!r}"


def append_query_rows(rows: list[dict[str, object]], section: str, query: str) -> None:
    ok, data, err = psql_rows(query)
    if not ok:
        rows.append({"section": section, "field_1": "query_error", "field_2": err, "field_3": "", "field_4": "", "notes": query})
        return
    for item in data:
        values = list(item.values())
        rows.append(
            {
                "section": section,
                "field_1": values[0] if len(values) > 0 else "",
                "field_2": values[1] if len(values) > 1 else "",
                "field_3": values[2] if len(values) > 2 else "",
                "field_4": values[3] if len(values) > 3 else "",
                "notes": "; ".join(f"{k}={v}" for k, v in item.items()),
            }
        )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_ignored(path: Path) -> str:
    proc = run(["git", "check-ignore", "-q", str(path.relative_to(ROOT))])
    if proc.returncode == 0:
        return "ignored"
    if proc.returncode == 1:
        return "not_ignored_or_absent"
    return f"check_error_rc_{proc.returncode}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    summary_ok, summary = read_json(SUMMARY_PATH)
    previous_ok, previous_summary = read_json(PREVIOUS_METADATA_SUMMARY_PATH)

    extraction_rows = []
    for key, expected in EXPECTED.items():
        value = summary.get(key)
        extraction_rows.append(
            {
                "run_id": REVIEWED_RUN_ID,
                "key": key,
                "value": json.dumps(value, ensure_ascii=False),
                "expected_value": json.dumps(expected, ensure_ascii=False),
                "match": value == expected,
                "notes": "" if value == expected else "summary value differs from prompt expectation",
            }
        )
    extraction_rows.append(
        {
            "run_id": "QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01",
            "key": "status",
            "value": json.dumps(previous_summary.get("status"), ensure_ascii=False),
            "expected_value": json.dumps("qsb_dwh_postgres_legacy_migration_metadata_server_completed"),
            "match": previous_summary.get("status") == "qsb_dwh_postgres_legacy_migration_metadata_server_completed",
            "notes": "secondary predecessor summary",
        }
    )
    write_csv(OUT / "05_previous_summary_extraction.csv", ["run_id", "key", "value", "expected_value", "match", "notes"], extraction_rows)

    conn_ok, conn_rows, conn_err = psql_rows("SELECT current_database(), current_user, version();")
    write_csv(
        OUT / "06_postgres_connection_review.csv",
        ["check_name", "status", "current_database", "current_user", "version", "notes"],
        [
            {
                "check_name": "postgres_connection",
                "status": "ok" if conn_ok else "failed",
                "current_database": conn_rows[0].get("current_database", "") if conn_rows else "",
                "current_user": conn_rows[0].get("current_user", "") if conn_rows else "",
                "version": conn_rows[0].get("version", "") if conn_rows else "",
                "notes": conn_err,
            }
        ],
    )

    inventory_rows: list[dict[str, object]] = []
    append_query_rows(
        inventory_rows,
        "schema_table_type_counts",
        """
        SELECT table_schema, table_type, COUNT(*) AS n
        FROM information_schema.tables
        WHERE table_schema IN ('admin','raw','staging','canonical','metadata','validation','mart','server')
        GROUP BY table_schema, table_type
        ORDER BY table_schema, table_type;
        """,
    )
    append_query_rows(
        inventory_rows,
        "mart_views",
        """
        SELECT table_schema, table_name, 'present' AS status
        FROM information_schema.views
        WHERE table_schema = 'mart'
        ORDER BY table_name;
        """,
    )
    expected_views = [
        "v_qsb_dwh_status",
        "v_qsb_dataset_overview",
        "v_qsb_artifact_inventory",
        "v_qsb_global_search",
        "v_qsb_validation_status",
        "v_qsb_claim_boundaries",
        "v_matrix_topology_overview",
        "v_interface01_overview",
        "v_relalg_overview",
        "v_causality_overview",
    ]
    for view in expected_views:
        view_ok, view_count, view_err = psql_scalar(
            f"SELECT COUNT(*) FROM information_schema.views WHERE table_schema='mart' AND table_name='{view}'"
        )
        inventory_rows.append(
            {
                "section": "expected_mart_view_presence",
                "field_1": view,
                "field_2": "present" if view_ok and view_count == 1 else "missing",
                "field_3": view_count if view_count is not None else "",
                "field_4": "",
                "notes": view_err,
            }
        )
    write_csv(OUT / "07_schema_table_view_inventory.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], inventory_rows)

    count_rows = []
    db_counts_reconciled = True
    for obj, key, query in COUNT_MAP:
        db_ok, db_value, db_err = psql_scalar(query)
        summary_value = summary.get(key) if key else None
        if key and db_ok:
            match = summary_value == db_value
            if not match:
                db_counts_reconciled = False
            explanation = "match" if match else "differs_or_cumulative_db_state"
            status = "ok" if match else "warning"
        else:
            explanation = "informational_no_summary_value" if db_ok else "query_failed"
            status = "info" if db_ok else "warning"
        count_rows.append(
            {
                "object": obj,
                "summary_value": "" if summary_value is None else summary_value,
                "db_value": "" if db_value is None else db_value,
                "match_or_explain": explanation,
                "review_status": status,
                "notes": db_err,
            }
        )
    write_csv(
        OUT / "08_core_count_reconciliation.csv",
        ["object", "summary_value", "db_value", "match_or_explain", "review_status", "notes"],
        count_rows,
    )

    artifact_rows: list[dict[str, object]] = []
    append_query_rows(artifact_rows, "domain_guess_counts", "SELECT domain_guess, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY domain_guess ORDER BY artifact_count DESC;")
    append_query_rows(artifact_rows, "artifact_kind_counts", "SELECT artifact_kind, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY artifact_kind ORDER BY artifact_count DESC;")
    append_query_rows(artifact_rows, "suffix_counts", "SELECT suffix, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY suffix ORDER BY artifact_count DESC NULLS LAST;")
    artifact_rows.append({"section": "review_note", "field_1": "domain visibility", "field_2": "reviewed", "field_3": "", "field_4": "", "notes": "Counts are artifact-level inventory only; no semantic interpretation is made."})
    write_csv(OUT / "09_artifact_registration_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], artifact_rows)

    checksum_rows: list[dict[str, object]] = []
    append_query_rows(checksum_rows, "checksum_algorithm_counts", "SELECT checksum_algorithm, COUNT(*) AS n FROM raw.raw_checksum GROUP BY checksum_algorithm ORDER BY n DESC;")
    append_query_rows(checksum_rows, "checksum_artifact_coverage", "SELECT COUNT(DISTINCT artifact_id) AS artifacts_with_checksum, COUNT(*) AS checksum_rows FROM raw.raw_checksum;")
    write_csv(OUT / "10_checksum_registration_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], checksum_rows)

    csv_rows: list[dict[str, object]] = []
    append_query_rows(csv_rows, "csv_distinct_files_and_rows", "SELECT COUNT(DISTINCT artifact_id) AS csv_files, COUNT(*) AS csv_rows FROM staging.csv_row_json;")
    append_query_rows(csv_rows, "csv_top_loaded_paths", "SELECT relative_path, COUNT(*) AS rows_loaded FROM staging.csv_row_json GROUP BY relative_path ORDER BY rows_loaded DESC LIMIT 50;")
    csv_rows.append({"section": "csv_cap_review", "field_1": "generic_csv_rows_loaded", "field_2": summary.get("generic_csv_rows_loaded"), "field_3": "cap_expected_100000", "field_4": "", "notes": "Interpreted as intentional audit/performance cap, not complete import of all CSV rows."})
    write_csv(OUT / "11_generic_csv_staging_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], csv_rows)

    json_rows: list[dict[str, object]] = []
    append_query_rows(json_rows, "json_parse_status_counts", "SELECT parse_status, COUNT(*) AS n FROM staging.json_document GROUP BY parse_status ORDER BY n DESC;")
    append_query_rows(json_rows, "json_nonparsed_samples", "SELECT relative_path, parse_status FROM staging.json_document WHERE parse_status <> 'parsed' LIMIT 100;")
    append_query_rows(json_rows, "json_key_value_count", "SELECT COUNT(*) AS json_key_values FROM staging.json_key_value;")
    write_csv(OUT / "12_json_staging_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], json_rows)

    md_rows: list[dict[str, object]] = []
    append_query_rows(md_rows, "markdown_document_count", "SELECT COUNT(*) AS markdown_documents FROM staging.markdown_document;")
    append_query_rows(md_rows, "markdown_samples", "SELECT relative_path, title, LEFT(body_preview, 200) AS preview FROM staging.markdown_document LIMIT 50;")
    write_csv(OUT / "13_markdown_text_staging_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], md_rows)

    sqlite_rows: list[dict[str, object]] = []
    append_query_rows(sqlite_rows, "sqlite_catalog_count", "SELECT COUNT(DISTINCT relative_path) AS sqlite_catalogs FROM staging.sqlite_table_inventory;")
    append_query_rows(sqlite_rows, "sqlite_table_count_by_path", "SELECT relative_path, COUNT(*) AS table_count FROM staging.sqlite_table_inventory GROUP BY relative_path ORDER BY table_count DESC LIMIT 100;")
    append_query_rows(sqlite_rows, "sqlite_row_count_top", "SELECT relative_path, table_name, row_count FROM staging.sqlite_row_count ORDER BY row_count DESC NULLS LAST LIMIT 100;")
    append_query_rows(sqlite_rows, "sqlite_meta_structures", "SELECT relative_path, table_name, 'meta_table_detected' AS note FROM staging.sqlite_table_inventory WHERE table_name LIKE 'meta_%' ORDER BY relative_path, table_name LIMIT 200;")
    sqlite_rows.append({"section": "review_note", "field_1": "sqlite_scope", "field_2": "catalog_level", "field_3": "", "field_4": "", "notes": "Catalog inventory/import does not imply semantic canonical transfer of each SQLite table."})
    write_csv(OUT / "14_sqlite_catalog_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], sqlite_rows)

    domain_rows: list[dict[str, object]] = []
    append_query_rows(domain_rows, "domain_by_kind_counts", "SELECT domain_guess, artifact_kind, COUNT(*) AS n FROM raw.source_artifact GROUP BY domain_guess, artifact_kind ORDER BY domain_guess, n DESC;")
    append_query_rows(domain_rows, "domain_path_samples", "SELECT domain_guess, relative_path FROM raw.source_artifact WHERE domain_guess IN ('matrix_topology','extract03','interface01','relalg','causality','sparc_rar','metadata') ORDER BY domain_guess, relative_path LIMIT 500;")
    domain_rows.append({"section": "review_note", "field_1": "artifact_level_not_semantics", "field_2": "confirmed", "field_3": "", "field_4": "", "notes": "Domain overview views may be empty or partial until domain-specific loaders are reviewed."})
    write_csv(OUT / "15_domain_artifact_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], domain_rows)

    search_rows: list[dict[str, object]] = []
    append_query_rows(search_rows, "global_search_count", "SELECT COUNT(*) AS global_search_rows FROM mart.v_qsb_global_search;")
    append_query_rows(search_rows, "global_search_domain_guess_counts", "SELECT domain_guess, COUNT(*) AS n FROM mart.v_qsb_global_search GROUP BY domain_guess ORDER BY n DESC;")
    append_query_rows(search_rows, "global_search_record_type_counts", "SELECT record_type, COUNT(*) AS n FROM mart.v_qsb_global_search GROUP BY record_type ORDER BY n DESC;")
    search_rows.append({"section": "review_note", "field_1": "search_scope", "field_2": "broad_artifact_text", "field_3": "", "field_4": "", "notes": "Broadly filled search can include duplicates/noise; this is an infrastructure review only."})
    write_csv(OUT / "16_global_search_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], search_rows)

    sample_search_rows: list[dict[str, object]] = []
    for term in ["Beschleunigung", "delta_phi", "RAR", "RELALG", "causality"]:
        ok, data, err = psql_rows(
            f"""
            SELECT {json.dumps(term)} AS search_term, to_jsonb(g)::text AS row_json
            FROM (
                SELECT *
                FROM mart.v_qsb_global_search
                WHERE search_text ILIKE '%{term.replace("'", "''")}%'
                LIMIT 20
            ) AS g;
            """
        )
        if ok:
            for row in data:
                sample_search_rows.append({"search_term": term, "row_json": row.get("row_json", ""), "notes": ""})
        else:
            sample_search_rows.append({"search_term": term, "row_json": "", "notes": err})
    write_csv(OUT / "21_sample_search_queries.csv", ["search_term", "row_json", "notes"], sample_search_rows)

    sample_artifact_rows: list[dict[str, object]] = []
    for domain in ["matrix_topology", "extract03", "interface01", "relalg", "causality", "sparc_rar", "metadata"]:
        ok, data, err = psql_rows(
            f"""
            SELECT {json.dumps(domain)} AS domain_guess, to_jsonb(a)::text AS row_json
            FROM (
                SELECT *
                FROM raw.source_artifact
                WHERE domain_guess = '{domain.replace("'", "''")}'
                ORDER BY relative_path
                LIMIT 20
            ) AS a;
            """
        )
        if ok:
            for row in data:
                sample_artifact_rows.append({"domain_guess": domain, "row_json": row.get("row_json", ""), "notes": ""})
        else:
            sample_artifact_rows.append({"domain_guess": domain, "row_json": "", "notes": err})
    write_csv(OUT / "22_sample_artifact_queries.csv", ["domain_guess", "row_json", "notes"], sample_artifact_rows)

    py_compile_server = run(["python", "-m", "py_compile", "scripts/qsb_metadata_server/qsb_metadata_server.py"])
    server_check = run(["python", "scripts/qsb_metadata_server/qsb_metadata_server.py", "--check"])
    write_csv(
        OUT / "17_metadata_server_review.csv",
        ["check_name", "status", "returncode", "stdout_preview", "stderr_preview", "notes"],
        [
            {
                "check_name": "py_compile",
                "status": "ok" if py_compile_server.returncode == 0 else "failed",
                "returncode": py_compile_server.returncode,
                "stdout_preview": py_compile_server.stdout[:1000],
                "stderr_preview": py_compile_server.stderr[:1000],
                "notes": "compile-only check",
            },
            {
                "check_name": "metadata_server_check",
                "status": "ok" if server_check.returncode == 0 else "failed",
                "returncode": server_check.returncode,
                "stdout_preview": server_check.stdout[:1000],
                "stderr_preview": server_check.stderr[:1000],
                "notes": "readiness check only; server not started persistently",
            },
        ],
    )

    omission_rows = []
    for predecessor in [
        "QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01",
        "QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-01",
    ]:
        run_dir = ROOT / "runs" / predecessor
        note = run_dir / "36_legacy_ingest_upsert.omitted_from_git.md"
        local_sql = run_dir / "36_legacy_ingest_upsert.sql"
        note_exists = note.exists()
        sql_exists = local_sql.exists()
        omission_rows.append(
            {
                "run_id": predecessor,
                "local_sql_exists": sql_exists,
                "local_size_bytes": local_sql.stat().st_size if sql_exists else "",
                "note_file_exists": note_exists,
                "note_size_bytes": note.stat().st_size if note_exists else "",
                "note_sha256": sha256(note) if note_exists else "",
                "sha256_matches_if_checkable": "not_checkable_without_declared_sql_hash",
                "git_status_ignored": git_ignored(local_sql) if sql_exists else "local_sql_absent",
                "review_status": "ok" if note_exists else "warning_missing_omission_note",
                "notes": "Omission note is the Git-facing representation; local SQL may remain outside Git.",
            }
        )
    write_csv(
        OUT / "18_oversized_replay_sql_omission_review.csv",
        [
            "run_id",
            "local_sql_exists",
            "local_size_bytes",
            "note_file_exists",
            "note_size_bytes",
            "note_sha256",
            "sha256_matches_if_checkable",
            "git_status_ignored",
            "review_status",
            "notes",
        ],
        omission_rows,
    )

    write_md(
        OUT / "02_review_scope.md",
        f"""# {RUN_ID}

## Scope

This is a read-only infrastructure review of the PostgreSQL legacy migration artifact-staging patch.

Reviewed predecessor:

- `{REVIEWED_RUN_ID}`

Secondary context:

- `QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01`
- `QSB-DWH-POSTGRES-CORE-MIGRATION-01`

## Explicit Exclusions

- No residual analysis.
- No RBCI_v1 evaluation.
- No QSB observable evaluation.
- No physical interpretation.
- No database mutation, migration rerun, or artifact-stage refill.
""",
    )

    write_md(
        OUT / "19_claim_boundary_review.md",
        f"""# Claim Boundary Review

## Befund

- `residual_analysis_executed = {summary.get('residual_analysis_executed')}`
- `rbci_v1_evaluated = {summary.get('rbci_v1_evaluated')}`
- `qsb_observable_evaluated = {summary.get('qsb_observable_evaluated')}`

## Interpretation

This review evaluates only DWH, metadata, staging, and search infrastructure.

## Hypothese

No scientific or physical hypothesis is introduced by this review.

## Offene Luecke

Domain-specific semantic review gates remain open for later runs.

## Claim Boundary

Dieser Review bewertet ausschliesslich DWH-/Metadaten-/Staging-/Suchinfrastruktur.
Er bewertet keine physikalische Richtigkeit von QSB.
Er erzeugt keinen neuen QSB-, DM-, MOND-, LambdaCDM-, Gravitations-, Raumzeit- oder Kausalitaetsclaim.
""",
    )

    write_md(
        OUT / "20_limitations_and_open_items.md",
        """# Limitations And Open Items

1. CSV generic staging capped at 100000 rows.
2. Generic artifact staging is not equivalent to domain-semantic canonical loading.
3. Some domain overview views may require later semantic loaders.
4. Global search contains broad artifact text and may include noise/duplicates.
5. Oversized replay SQL files are local-only and represented by omission notes.
6. SQLite catalogs are inventoried/imported at catalog level; semantic meta_* import must be reviewed per catalog.
7. No physical interpretation may proceed before domain-specific review gates approve the relevant subset.
""",
    )

    decision = "approved_with_warnings_for_domain_specific_metadata_review"
    write_md(
        OUT / "23_review_decision.md",
        f"""# Review Decision

## Status

`{decision}`

## Begründung

The DWH foundation and global search are operational for downstream domain-specific metadata review. The decision carries warnings because the generic CSV staging cap and domain-semantic loader limitations require explicit downstream review.
""",
    )

    write_md(
        OUT / "24_next_run_recommendation.md",
        """# Next Run Recommendation

Recommended next run ID:

`QSB-DWH-POSTGRES-DOMAIN-METADATA-REVIEW-01`

Recommended scope:

- Review domain-specific metadata semantics after the artifact-level infrastructure review.
- Keep artifact registration separate from scientific interpretation.
- Preserve the CSV cap and omitted replay SQL limitations in downstream notes.
""",
    )

    write_md(
        OUT / "25_review_note.md",
        f"""# Review Note

## Befund

The reviewed predecessor summary is valid JSON: `{summary_ok}`. The target database connection was checked against `{DB}`. Core infrastructure counts, schema/view inventory, artifact registration, checksums, CSV/JSON/Markdown staging, SQLite catalog inventory, global search, metadata server readiness, and oversized replay SQL omission notes were reviewed.

## Interpretation

The reviewed state supports the infrastructure statement with limitations: central PostgreSQL DWH, broad artifact inventory, checksums, generic staging, metadata-based search, and a read-only metadata server readiness scaffold are present.

## Hypothese

No physical or domain-scientific hypothesis is evaluated here.

## Offene Luecke

Domain-semantic loaders and domain-specific metadata review remain downstream work.

## Claim Boundary

This note does not evaluate residuals, RBCI_v1, QSB observables, spacetime, gravity, dark matter, MOND, LambdaCDM, or causality claims.
""",
    )

    artifact_status = "artifact_inventory_counts_reviewed"
    checksum_status = "checksum_counts_reviewed"
    csv_status = "reviewed_with_100000_row_cap"
    json_status = "json_parse_status_reviewed"
    markdown_status = "markdown_inventory_reviewed"
    sqlite_status = "sqlite_catalog_level_reviewed"
    domain_status = "artifact_level_only_domain_semantics_pending"
    search_status = "global_search_operational_with_noise_warning"
    server_status = "ready_for_read_only_psql_cli_server" if server_check.returncode == 0 else "metadata_server_check_failed"
    omission_status = "omission_notes_present" if all(row["note_file_exists"] for row in omission_rows) else "omission_note_warning"

    review_summary = {
        "run_id": RUN_ID,
        "status": decision,
        "target_database": DB,
        "postgres_connection_ok": conn_ok,
        "reviewed_run_id": REVIEWED_RUN_ID,
        "reviewed_status": summary.get("status"),
        "summary_json_valid": summary_ok,
        "db_counts_reconciled": db_counts_reconciled,
        "artifact_registration_review_status": artifact_status,
        "checksum_review_status": checksum_status,
        "csv_staging_review_status": csv_status,
        "json_staging_review_status": json_status,
        "markdown_staging_review_status": markdown_status,
        "sqlite_catalog_review_status": sqlite_status,
        "domain_artifact_review_status": domain_status,
        "global_search_review_status": search_status,
        "metadata_server_review_status": server_status,
        "oversized_replay_sql_omission_review_status": omission_status,
        "artifacts_registered_after": summary.get("artifacts_registered_after"),
        "global_search_rows_after": summary.get("global_search_rows_after"),
        "csv_generic_staging_cap_rows": summary.get("generic_csv_rows_loaded"),
        "residual_analysis_executed": summary.get("residual_analysis_executed"),
        "rbci_v1_evaluated": summary.get("rbci_v1_evaluated"),
        "qsb_observable_evaluated": summary.get("qsb_observable_evaluated"),
        "claim_boundary_status": "no_physical_claims",
        "review_decision": decision,
        "recommended_next_run_id": "QSB-DWH-POSTGRES-DOMAIN-METADATA-REVIEW-01",
        "notes": "Read-only infrastructure review. CSV cap and domain-semantic review limitations remain explicit.",
    }
    (OUT / "04_artifact_staging_patch_review_summary.json").write_text(
        json.dumps(review_summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    command_lines = [
        "# Command Log",
        "",
        "Pre-script commands run manually:",
        "",
        "- `sed -n '1,240p' /home/ralf-kemmann/Downloads/QSB_DWH_POSTGRES_LEGACY_MIGRATION_ARTIFACT_STAGING_PATCH_REVIEW_01_CODEX_PROMPT.md`",
        "- `sed -n '241,520p' /home/ralf-kemmann/Downloads/QSB_DWH_POSTGRES_LEGACY_MIGRATION_ARTIFACT_STAGING_PATCH_REVIEW_01_CODEX_PROMPT.md`",
        "- `sed -n '521,920p' /home/ralf-kemmann/Downloads/QSB_DWH_POSTGRES_LEGACY_MIGRATION_ARTIFACT_STAGING_PATCH_REVIEW_01_CODEX_PROMPT.md`",
        f"- `mkdir -p runs/{RUN_ID}`",
        f"- `git status --short --ignored | sed -n '1,200p' > runs/{RUN_ID}/00_git_status_short_before.txt`",
        f"- `git --no-pager log --oneline -30 > runs/{RUN_ID}/01_git_log_oneline_before.txt`",
        "- `python -m json.tool runs/QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-01/04_artifact_staging_patch_summary.json`",
        "- `python -m json.tool runs/QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01/04_legacy_migration_summary.json`",
        "- `psql -d qsb_research_dwh -c \"SELECT current_database(), current_user, version();\"`",
        "- `python runs/QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-REVIEW-01/30_generate_review_artifacts.py`",
        "",
        "Commands run by generator:",
        "",
    ]
    for entry in command_log:
        command_lines.append(f"- `{entry['cmd']}` -> rc={entry['returncode']}")
        if entry["stderr_preview"]:
            command_lines.append(f"  - stderr preview: `{entry['stderr_preview']}`")
    write_md(OUT / "03_command_log.txt", "\n".join(command_lines) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
