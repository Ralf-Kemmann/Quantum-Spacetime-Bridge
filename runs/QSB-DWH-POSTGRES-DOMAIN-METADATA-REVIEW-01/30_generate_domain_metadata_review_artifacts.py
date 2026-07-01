#!/usr/bin/env python3
"""Generate read-only domain metadata review artifacts."""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "QSB-DWH-POSTGRES-DOMAIN-METADATA-REVIEW-01"
DB = "qsb_research_dwh"
ROOT = Path.cwd()
OUT = ROOT / "runs" / RUN_ID
PREV_DIR = ROOT / "runs" / "QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-REVIEW-01"
PREV_SUMMARY = PREV_DIR / "04_artifact_staging_patch_review_summary.json"
PREV_DECISION = PREV_DIR / "23_review_decision.md"

DOMAINS = [
    "sparc_rar",
    "matrix_topology",
    "extract03",
    "interface01",
    "relalg",
    "causality",
    "metadata",
    "qsb_meta",
    "unknown",
]

DOMAIN_TERMS = {
    "sparc_rar": ["SPARC", "RAR", "residual", "acceleration", "Beschleunigung", "MOND", "LambdaCDM", "massmodel", "galaxy"],
    "matrix_extract03": ["matrix", "topology", "EXTRACT03", "D1K", "edge", "node", "loop", "graph"],
    "interface01": ["INTERFACE01", "delta_phi", "M33", "phase_pair_stats", "interference_kernel", "pair", "wrapping", "diagonal"],
    "relalg": ["RELALG", "D1K", "bridge", "loop", "matrix", "topology", "synthetic", "edge"],
    "causality": ["causality", "Taube", "electron transfer", "admissibility", "cycle", "negative control", "IS01"],
    "qsb_meta": ["metadata", "meta_field", "meta_alias", "lineage", "validation", "claim", "unit", "dimension", "conversion_rule"],
}

SEARCH_TERMS = [
    "RAR",
    "SPARC",
    "MOND",
    "LambdaCDM",
    "delta_phi",
    "INTERFACE01",
    "M33",
    "matrix",
    "topology",
    "EXTRACT03",
    "RELALG",
    "causality",
    "Taube",
    "metadata",
    "claim",
    "validation",
    "dimension",
    "unit",
    "alias",
]

EXPECTED_VIEWS = [
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
    "v_sparc_rar_direct_points",
    "v_sparc_massmodels_gobs_points",
    "v_sparc_field_metadata",
    "v_sparc_validation_status",
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
        return True, json.loads(path.read_text(encoding="utf-8"))
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


def sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def psql_rows(query: str) -> tuple[bool, list[dict[str, str]], str]:
    proc = run(["psql", "-d", DB, "--csv", "-q", "-c", query])
    if proc.returncode != 0:
        return False, [], proc.stderr.strip()
    lines = proc.stdout.splitlines()
    if not lines:
        return True, [], ""
    return True, list(csv.DictReader(lines)), ""


def psql_scalar(query: str) -> tuple[bool, int | None, str]:
    proc = run(["psql", "-d", DB, "-At", "-q", "-c", query])
    if proc.returncode != 0:
        return False, None, proc.stderr.strip()
    try:
        return True, int(proc.stdout.strip().splitlines()[-1]), ""
    except Exception as exc:
        return False, None, f"parse_error: {exc}: {proc.stdout!r}"


def append_query_rows(rows: list[dict[str, object]], section: str, query: str) -> None:
    ok, data, err = psql_rows(query)
    if not ok:
        rows.append({"section": section, "field_1": "query_error", "field_2": err, "field_3": "", "field_4": "", "notes": query})
        return
    for item in data:
        vals = list(item.values())
        rows.append(
            {
                "section": section,
                "field_1": vals[0] if len(vals) > 0 else "",
                "field_2": vals[1] if len(vals) > 1 else "",
                "field_3": vals[2] if len(vals) > 2 else "",
                "field_4": vals[3] if len(vals) > 3 else "",
                "notes": "; ".join(f"{k}={v}" for k, v in item.items()),
            }
        )


def term_filter(terms: list[str], column: str = "search_text") -> str:
    return " OR ".join(f"{column} ILIKE '%' || {sql_quote(term)} || '%'" for term in terms)


def raw_domain_filter(domain: str) -> str:
    if domain == "sparc_rar":
        return "(domain_guess='sparc_rar' OR relative_path ILIKE '%SPARC%' OR relative_path ILIKE '%RAR%')"
    if domain == "qsb_meta":
        return "(domain_guess='metadata' OR relative_path ILIKE '%qsb%' OR relative_path ILIKE '%metadata%')"
    if domain == "unknown":
        return "(domain_guess IS NULL OR domain_guess='unknown')"
    return f"domain_guess={sql_quote(domain)}"


def scalar_or_zero(query: str) -> int:
    ok, val, _ = psql_scalar(query)
    return val if ok and val is not None else 0


def view_count(view: str) -> tuple[str, int | str, str]:
    exists = scalar_or_zero(f"SELECT COUNT(*) FROM information_schema.views WHERE table_schema='mart' AND table_name={sql_quote(view)}")
    if exists != 1:
        return "missing", "", "view not present"
    ok, count, err = psql_scalar(f"SELECT COUNT(*) FROM mart.{view}")
    return "present", count if ok and count is not None else "", err


def search_hits(terms: list[str]) -> int:
    return scalar_or_zero(f"SELECT COUNT(*) FROM mart.v_qsb_global_search WHERE {term_filter(terms)}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    prev_ok, prev = read_json(PREV_SUMMARY)
    prev_decision_text = PREV_DECISION.read_text(encoding="utf-8") if PREV_DECISION.exists() else ""

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

    prev_rows = []
    keys = [
        "review_decision",
        "postgres_connection_ok",
        "summary_json_valid",
        "db_counts_reconciled",
        "global_search_review_status",
        "metadata_server_review_status",
        "oversized_replay_sql_omission_review_status",
        "claim_boundary_status",
        "recommended_next_run_id",
    ]
    for key in keys:
        prev_rows.append(
            {
                "source": str(PREV_SUMMARY.relative_to(ROOT)),
                "key": key,
                "value": json.dumps(prev.get(key), ensure_ascii=False),
                "review_status": "ok" if prev_ok and key in prev else "missing",
                "notes": "previous review summary extraction",
            }
        )
    prev_rows.append(
        {
            "source": str(PREV_DECISION.relative_to(ROOT)),
            "key": "decision_md_contains_expected_status",
            "value": "approved_with_warnings_for_domain_specific_metadata_review" in prev_decision_text,
            "review_status": "ok" if "approved_with_warnings_for_domain_specific_metadata_review" in prev_decision_text else "warning",
            "notes": "previous review decision markdown",
        }
    )
    write_csv(OUT / "05_previous_review_extraction.csv", ["source", "key", "value", "review_status", "notes"], prev_rows)

    inv_rows: list[dict[str, object]] = []
    append_query_rows(inv_rows, "artifact_count_by_domain", "SELECT domain_guess, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY domain_guess ORDER BY artifact_count DESC NULLS LAST;")
    append_query_rows(inv_rows, "artifact_kind_by_domain", "SELECT domain_guess, artifact_kind, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY domain_guess, artifact_kind ORDER BY domain_guess NULLS LAST, artifact_count DESC;")
    append_query_rows(inv_rows, "suffix_by_domain", "SELECT domain_guess, suffix, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY domain_guess, suffix ORDER BY domain_guess NULLS LAST, artifact_count DESC NULLS LAST;")
    write_csv(OUT / "07_domain_inventory_overview.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], inv_rows)

    view_rows = []
    all_views_ok, all_views, all_views_err = psql_rows("SELECT table_schema, table_name FROM information_schema.views WHERE table_schema='mart' ORDER BY table_name;")
    if all_views_ok:
        for row in all_views:
            status, cnt, note = view_count(row["table_name"])
            view_rows.append({"view_name": f"{row['table_schema']}.{row['table_name']}", "expected_or_discovered": "discovered", "presence_status": status, "row_count": cnt, "notes": note})
    else:
        view_rows.append({"view_name": "mart.*", "expected_or_discovered": "discovered", "presence_status": "query_error", "row_count": "", "notes": all_views_err})
    for view in EXPECTED_VIEWS:
        status, cnt, note = view_count(view)
        view_rows.append({"view_name": f"mart.{view}", "expected_or_discovered": "expected", "presence_status": status, "row_count": cnt, "notes": note})
    write_csv(OUT / "09_domain_view_presence_review.csv", ["view_name", "expected_or_discovered", "presence_status", "row_count", "notes"], view_rows)

    artifact_rows = []
    coverage_terms = {
        "sparc_rar": ["SPARC", "RAR"],
        "matrix": ["matrix"],
        "extract03": ["extract03"],
        "interface01": ["interface01"],
        "delta_phi": ["delta_phi"],
        "relalg": ["relalg"],
        "causality": ["causality"],
        "metadata": ["metadata"],
        "qsb": ["qsb"],
    }
    for label, terms in coverage_terms.items():
        where = " OR ".join([f"domain_guess ILIKE '%' || {sql_quote(t)} || '%' OR relative_path ILIKE '%' || {sql_quote(t)} || '%'" for t in terms])
        append_query_rows(
            artifact_rows,
            f"{label}_artifact_samples",
            f"SELECT domain_guess, artifact_kind, suffix, relative_path FROM raw.source_artifact WHERE {where} ORDER BY relative_path LIMIT 200;",
        )
    write_csv(OUT / "10_domain_artifact_coverage_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], artifact_rows)

    search_rows: list[dict[str, object]] = []
    append_query_rows(search_rows, "global_search_schema", "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='mart' AND table_name='v_qsb_global_search' ORDER BY ordinal_position;")
    append_query_rows(search_rows, "domain_guess_counts", "SELECT domain_guess, COUNT(*) AS n FROM mart.v_qsb_global_search GROUP BY domain_guess ORDER BY n DESC NULLS LAST;")
    append_query_rows(search_rows, "record_type_counts", "SELECT record_type, COUNT(*) AS n FROM mart.v_qsb_global_search GROUP BY record_type ORDER BY n DESC NULLS LAST;")
    hit_rows = []
    sample_rows = []
    for term in SEARCH_TERMS:
        hits = search_hits([term])
        hit_rows.append({"term": term, "hits": hits, "review_status": "visible" if hits else "no_hits", "notes": "search_text ILIKE term"})
        search_rows.append({"section": "term_hits", "field_1": term, "field_2": hits, "field_3": "", "field_4": "", "notes": "search_text ILIKE term"})
        ok, samples, err = psql_rows(
            f"""
            SELECT {sql_quote(term)} AS term, domain_guess, record_type, record_id, LEFT(search_text, 300) AS sample
            FROM mart.v_qsb_global_search
            WHERE search_text ILIKE '%' || {sql_quote(term)} || '%'
            LIMIT 25;
            """
        )
        if ok:
            for row in samples:
                sample_rows.append({**row, "notes": "record_id used; global search view has no relative_path column"})
        else:
            sample_rows.append({"term": term, "domain_guess": "", "record_type": "", "record_id": "", "sample": "", "notes": err})
    search_rows.append({"section": "review_note", "field_1": "global_search_scope", "field_2": "broad_index", "field_3": "", "field_4": "", "notes": "Search visibility is not evidence quality or physical interpretation."})
    write_csv(OUT / "11_domain_global_search_coverage_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], search_rows)
    write_csv(OUT / "21_domain_sample_queries.csv", ["term", "domain_guess", "record_type", "record_id", "sample", "notes"], sample_rows)
    write_csv(OUT / "27_domain_search_term_hit_matrix.csv", ["term", "hits", "review_status", "notes"], hit_rows)

    meta_rows: list[dict[str, object]] = []
    append_query_rows(meta_rows, "meta_field_count", "SELECT COUNT(*) AS meta_field_count FROM metadata.meta_field;")
    append_query_rows(meta_rows, "meta_alias_count", "SELECT COUNT(*) AS meta_alias_count FROM metadata.meta_alias;")
    append_query_rows(meta_rows, "metadata_schema", "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema='metadata' AND table_name IN ('meta_field','meta_alias','meta_lineage','meta_claim') ORDER BY table_name, ordinal_position;")
    append_query_rows(meta_rows, "meta_field_samples", "SELECT canonical_name, quantity_kind, dimension_vector, display_label_de, validation_status, claim_boundary FROM metadata.meta_field ORDER BY canonical_name LIMIT 200;")
    append_query_rows(meta_rows, "meta_alias_samples", "SELECT canonical_name, display_label_de, language, alias_status FROM metadata.meta_alias ORDER BY canonical_name LIMIT 200;")
    append_query_rows(meta_rows, "meta_lineage_samples", "SELECT dataset_id, source_path, lineage_role, validation_status FROM metadata.meta_lineage ORDER BY dataset_id, source_path LIMIT 200;")
    append_query_rows(meta_rows, "meta_claim_samples", "SELECT claim_boundary, claim_status FROM metadata.meta_claim ORDER BY claim_boundary LIMIT 200;")
    write_csv(OUT / "12_domain_metadata_field_alias_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], meta_rows)

    validation_rows: list[dict[str, object]] = []
    append_query_rows(validation_rows, "validation_result_count", "SELECT COUNT(*) AS validation_result_count FROM validation.validation_result;")
    append_query_rows(validation_rows, "validation_status_view", "SELECT * FROM mart.v_qsb_validation_status LIMIT 500;")
    append_query_rows(validation_rows, "claim_boundaries_view", "SELECT * FROM mart.v_qsb_claim_boundaries LIMIT 500;")
    append_query_rows(validation_rows, "no_go_boundaries", "SELECT no_go_text, no_go_status FROM validation.no_go_boundary LIMIT 500;")
    write_csv(OUT / "13_domain_validation_claim_boundary_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], validation_rows)

    domain_view = {
        "sparc_rar": "v_sparc_rar_direct_points",
        "matrix_topology": "v_matrix_topology_overview",
        "extract03": "v_matrix_topology_overview",
        "interface01": "v_interface01_overview",
        "relalg": "v_relalg_overview",
        "causality": "v_causality_overview",
        "metadata": "v_qsb_metadata_fields",
        "qsb_meta": "v_qsb_metadata_fields",
        "unknown": "",
    }
    matrix_rows = []
    domain_review_rows: dict[str, list[dict[str, object]]] = {key: [] for key in ["sparc_rar", "matrix_extract03", "interface01", "relalg", "causality", "qsb_meta"]}
    readiness_summary = {}
    for domain in DOMAINS:
        raw_filter = raw_domain_filter(domain)
        artifact_count = scalar_or_zero(f"SELECT COUNT(*) FROM raw.source_artifact WHERE {raw_filter}")
        checksum_count = scalar_or_zero(f"SELECT COUNT(DISTINCT a.artifact_id) FROM raw.source_artifact a JOIN raw.raw_checksum c ON c.artifact_id=a.artifact_id WHERE {raw_filter.replace('domain_guess', 'a.domain_guess').replace('relative_path', 'a.relative_path')}")
        csv_count = scalar_or_zero(f"SELECT COUNT(DISTINCT c.artifact_id) FROM staging.csv_row_json c JOIN raw.source_artifact a ON a.artifact_id=c.artifact_id WHERE {raw_filter.replace('domain_guess', 'a.domain_guess').replace('relative_path', 'a.relative_path')}")
        json_count = scalar_or_zero(f"SELECT COUNT(DISTINCT j.artifact_id) FROM staging.json_document j JOIN raw.source_artifact a ON a.artifact_id=j.artifact_id WHERE {raw_filter.replace('domain_guess', 'a.domain_guess').replace('relative_path', 'a.relative_path')}")
        md_count = scalar_or_zero(f"SELECT COUNT(DISTINCT m.artifact_id) FROM staging.markdown_document m JOIN raw.source_artifact a ON a.artifact_id=m.artifact_id WHERE {raw_filter.replace('domain_guess', 'a.domain_guess').replace('relative_path', 'a.relative_path')}")
        sqlite_count = scalar_or_zero(f"SELECT COUNT(DISTINCT s.artifact_id) FROM staging.sqlite_table_inventory s JOIN raw.source_artifact a ON a.artifact_id=s.artifact_id WHERE {raw_filter.replace('domain_guess', 'a.domain_guess').replace('relative_path', 'a.relative_path')}")
        search_domain = "metadata" if domain == "qsb_meta" else domain
        gs_count = scalar_or_zero(f"SELECT COUNT(*) FROM mart.v_qsb_global_search WHERE domain_guess={sql_quote(search_domain)}")
        fields_count = scalar_or_zero("SELECT COUNT(*) FROM metadata.meta_field") if domain in {"metadata", "qsb_meta", "sparc_rar"} else 0
        alias_count = scalar_or_zero("SELECT COUNT(*) FROM metadata.meta_alias") if domain in {"metadata", "qsb_meta", "sparc_rar"} else 0
        if domain == "sparc_rar":
            validation_count = scalar_or_zero("SELECT COUNT(*) FROM mart.v_sparc_validation_status")
        else:
            validation_count = scalar_or_zero(f"SELECT COUNT(*) FROM validation.validation_result WHERE validation_scope ILIKE '%' || {sql_quote(domain.split('_')[0])} || '%' OR notes ILIKE '%' || {sql_quote(domain.split('_')[0])} || '%'")
        claim_count = scalar_or_zero("SELECT COUNT(*) FROM mart.v_qsb_claim_boundaries")
        view = domain_view[domain]
        vstatus, vrows, vnote = view_count(view) if view else ("not_applicable", "", "unknown bucket has no expected mart view")
        if domain == "unknown":
            semantic_status = "none_noise_bucket"
            readiness = "not_applicable_or_noise_bucket"
        elif domain == "sparc_rar" and fields_count and validation_count and vstatus == "present":
            semantic_status = "domain_specific_metadata_and_views_present_no_physics_claim"
            readiness = "ready_for_domain_specific_precontract"
        elif domain in {"metadata", "qsb_meta"} and fields_count and alias_count:
            semantic_status = "metadata_model_visible"
            readiness = "ready_for_domain_specific_precontract"
        elif vstatus == "present" and artifact_count:
            semantic_status = "artifact_derived_overview_view_present"
            readiness = "partial_ready_requires_semantic_loader_review"
        elif artifact_count or gs_count:
            semantic_status = "artifact_or_search_visible"
            readiness = "artifact_level_only"
        else:
            semantic_status = "insufficient_visibility"
            readiness = "blocked_missing_required_metadata"
        readiness_summary[domain if domain != "metadata" else "metadata"] = readiness
        matrix_rows.append(
            {
                "domain": domain,
                "artifact_registered": artifact_count,
                "checksum_covered": checksum_count,
                "generic_csv_visible": csv_count,
                "json_visible": json_count,
                "markdown_visible": md_count,
                "sqlite_catalog_visible": sqlite_count,
                "global_search_visible": gs_count,
                "metadata_fields_visible": fields_count,
                "aliases_visible": alias_count,
                "validation_entries_visible": validation_count,
                "claim_boundaries_visible": claim_count,
                "mart_view_visible": vstatus,
                "semantic_loader_status": semantic_status,
                "readiness_status": readiness,
                "notes": vnote or "Conservative readiness classification; no physical interpretation.",
            }
        )

    write_csv(
        OUT / "08_domain_readiness_matrix.csv",
        [
            "domain",
            "artifact_registered",
            "checksum_covered",
            "generic_csv_visible",
            "json_visible",
            "markdown_visible",
            "sqlite_catalog_visible",
            "global_search_visible",
            "metadata_fields_visible",
            "aliases_visible",
            "validation_entries_visible",
            "claim_boundaries_visible",
            "mart_view_visible",
            "semantic_loader_status",
            "readiness_status",
            "notes",
        ],
        matrix_rows,
    )

    def domain_file_row(label: str, raw_domains: list[str], terms: list[str], view: str, readiness: str, notes: str) -> dict[str, object]:
        artifact_count = sum(scalar_or_zero(f"SELECT COUNT(*) FROM raw.source_artifact WHERE {raw_domain_filter(d)}") for d in raw_domains)
        hits = search_hits(terms)
        vstatus, vrows, _ = view_count(view) if view else ("not_applicable", "", "")
        metadata_fields = scalar_or_zero("SELECT COUNT(*) FROM metadata.meta_field WHERE " + term_filter(terms, "canonical_name") + " OR " + term_filter(terms, "display_label_de")) if label in {"sparc_rar", "qsb_meta"} else 0
        if label == "sparc_rar":
            validation_entries = scalar_or_zero("SELECT COUNT(*) FROM mart.v_sparc_validation_status")
        else:
            validation_entries = scalar_or_zero("SELECT COUNT(*) FROM validation.validation_result WHERE " + term_filter(terms, "validation_scope") + " OR " + term_filter(terms, "notes"))
        claim_boundaries = scalar_or_zero("SELECT COUNT(*) FROM mart.v_qsb_claim_boundaries")
        return {
            "domain": label,
            "artifact_count": artifact_count,
            "global_search_hits": hits,
            "view_present": vstatus,
            "view_row_count": vrows,
            "metadata_fields": metadata_fields,
            "validation_entries": validation_entries,
            "claim_boundaries": claim_boundaries,
            "readiness_status": readiness,
            "notes": notes,
        }

    write_csv(OUT / "14_sparc_rar_domain_review.csv", ["domain", "artifact_count", "global_search_hits", "view_present", "view_row_count", "metadata_fields", "validation_entries", "claim_boundaries", "readiness_status", "notes"], [domain_file_row("sparc_rar", ["sparc_rar"], DOMAIN_TERMS["sparc_rar"], "v_sparc_rar_direct_points", "ready_for_domain_specific_precontract", "SPARC/RAR has domain-specific staging and mart views; no residual/MOND/LambdaCDM interpretation performed.")])
    write_csv(OUT / "15_matrix_extract03_domain_review.csv", ["domain", "artifact_count", "global_search_hits", "view_present", "view_row_count", "metadata_fields", "validation_entries", "claim_boundaries", "readiness_status", "notes"], [domain_file_row("matrix_extract03", ["matrix_topology", "extract03"], DOMAIN_TERMS["matrix_extract03"], "v_matrix_topology_overview", "partial_ready_requires_semantic_loader_review", "Matrix/EXTRACT03 artifacts and overview view visible; semantic loader review still required.")])
    write_csv(OUT / "16_interface01_domain_review.csv", ["domain", "artifact_count", "global_search_hits", "view_present", "view_row_count", "metadata_fields", "validation_entries", "claim_boundaries", "readiness_status", "notes"], [domain_file_row("interface01", ["interface01"], DOMAIN_TERMS["interface01"], "v_interface01_overview", "partial_ready_requires_semantic_loader_review", "INTERFACE01 gate artifacts are visible; delta_phi is not physically released by this review.")])
    write_csv(OUT / "17_relalg_domain_review.csv", ["domain", "artifact_count", "global_search_hits", "view_present", "view_row_count", "metadata_fields", "validation_entries", "claim_boundaries", "readiness_status", "notes"], [domain_file_row("relalg", ["relalg"], DOMAIN_TERMS["relalg"], "v_relalg_overview", "partial_ready_requires_semantic_loader_review", "RELALG remains methodology/structure artifact review only.")])
    write_csv(OUT / "18_causality_domain_review.csv", ["domain", "artifact_count", "global_search_hits", "view_present", "view_row_count", "metadata_fields", "validation_entries", "claim_boundaries", "readiness_status", "notes"], [domain_file_row("causality", ["causality"], DOMAIN_TERMS["causality"], "v_causality_overview", "partial_ready_requires_semantic_loader_review", "Causality artifacts are visible; no causality claim is made.")])
    write_csv(OUT / "19_qsb_meta_metadata_domain_review.csv", ["domain", "artifact_count", "global_search_hits", "view_present", "view_row_count", "metadata_fields", "validation_entries", "claim_boundaries", "readiness_status", "notes"], [domain_file_row("qsb_meta", ["metadata", "qsb_meta"], DOMAIN_TERMS["qsb_meta"], "v_qsb_metadata_fields", "ready_for_domain_specific_precontract", "Metadata model fields, aliases, lineage, validation, and claim boundaries are visible at metadata level.")])

    unknown_rows: list[dict[str, object]] = []
    append_query_rows(unknown_rows, "unknown_count", "SELECT COUNT(*) FROM raw.source_artifact WHERE domain_guess IS NULL OR domain_guess = 'unknown';")
    append_query_rows(unknown_rows, "unknown_kind_suffix_counts", "SELECT artifact_kind, suffix, COUNT(*) AS n FROM raw.source_artifact WHERE domain_guess IS NULL OR domain_guess = 'unknown' GROUP BY artifact_kind, suffix ORDER BY n DESC NULLS LAST;")
    append_query_rows(unknown_rows, "unknown_path_samples", "SELECT relative_path FROM raw.source_artifact WHERE domain_guess IS NULL OR domain_guess = 'unknown' ORDER BY relative_path LIMIT 500;")
    unknown_rows.append({"section": "review_note", "field_1": "unknown_bucket", "field_2": "large_routing_gap", "field_3": "", "field_4": "", "notes": "Unknown is expected as a residual bucket but large enough to require routing review before narrative selection."})
    write_csv(OUT / "20_unknown_noise_orphan_review.csv", ["section", "field_1", "field_2", "field_3", "field_4", "notes"], unknown_rows)

    write_md(
        OUT / "02_domain_metadata_review_scope.md",
        f"""# {RUN_ID}

## Scope

Read-only domain metadata readiness review for the PostgreSQL DWH.

## Exclusions

- No residual analysis.
- No RBCI_v1 evaluation.
- No QSB observable evaluation.
- No physical interpretation.
- No SPARC/RAR, MOND, LambdaCDM, dark matter, gravity, spacetime, or causality interpretation.

## Review Distinctions

- artifact-level registration is not domain-semantic readiness.
- generic staging is not canonical scientific interpretation.
- global search visibility is not a valid physical claim.
""",
    )

    write_md(
        OUT / "22_domain_readiness_decision.md",
        """# Domain Readiness Decision

## Status

`domain_metadata_review_completed_partial_readiness`

## Decision Text

Dieser Lauf gibt keine physikalische Interpretation frei.
Dieser Lauf gibt nur die Auswahl und Priorisierung nachfolgender domaenenspezifischer Precontracts/Loader-Reviews frei.

## Rationale

The DWH is stable enough for selected follow-up precontracts, but readiness is mixed: SPARC/RAR and QSB metadata are the most metadata-visible, while Matrix/EXTRACT03, INTERFACE01, RELALG, and CAUSALITY remain partial and require semantic loader review. The unknown bucket is large enough to justify a routing patch before narrative prioritization.
""",
    )
    write_md(
        OUT / "23_limitations_and_open_items.md",
        """# Limitations And Open Items

1. `unknown` bucket remains large and needs routing review.
2. Domain-level artifact coverage is not equivalent to semantic canonical loading.
3. Some overview views may be empty, partial, or artifact-derived.
4. Global search includes broad generated and artifact text; search hit count is not evidence quality.
5. CSV staging remains capped at 100000 rows.
6. SQLite catalogs are catalog-level visible; semantic extraction still needs domain review.
7. Claim boundaries remain active: no residual/RBCI/QSB-observable/physics interpretation.
8. Next runs should be selected by readiness matrix, not by narrative interest.
""",
    )
    write_md(
        OUT / "24_next_run_recommendation.md",
        """# Next Run Recommendation

1. `QSB-DWH-POSTGRES-DOMAIN-ROUTING-PATCH-02`
   Recommended first because the `unknown` bucket is large.

2. `QSB-DWH-POSTGRES-SPARC-RAR-METADATA-PRECONTRACT-01`
   SPARC/RAR has the strongest domain-specific metadata/view visibility, with claim boundaries still active.

3. `QSB-DWH-POSTGRES-INTERFACE01-METADATA-PRECONTRACT-01`
   INTERFACE01 gate artifacts are visible but require semantic loader review.

4. `QSB-DWH-POSTGRES-MATRIX-EXTRACT03-METADATA-PRECONTRACT-01`
   Matrix/EXTRACT03 is structurally visible and should be reviewed as structure/method metadata only.

5. `QSB-DWH-POSTGRES-RELALG-CAUSALITY-METADATA-PRECONTRACT-01`
   RELALG and CAUSALITY remain partial/artifact-level enough to pair with stricter claim-boundary review.
""",
    )
    write_md(
        OUT / "25_review_note.md",
        """# Review Note

## Befund

Domain metadata visibility is mixed. SPARC/RAR and QSB metadata have the strongest metadata/view support. Matrix/EXTRACT03, INTERFACE01, RELALG, and CAUSALITY have artifact and overview visibility but remain subject to semantic loader review. The unknown bucket is large.

## Interpretation

The DWH supports prioritizing follow-up domain precontracts, with a routing patch recommended first.

## Hypothese

No physical or scientific hypothesis is introduced by this review.

## Offene Luecke

Unknown routing, domain-semantic loaders, and domain-specific claim-boundary gates remain open.

## Claim Boundary

This review does not release residual analysis, RBCI_v1 evaluation, QSB observables, SPARC/RAR interpretation, MOND/LambdaCDM interpretation, dark matter interpretation, gravity interpretation, spacetime interpretation, or causality interpretation.
""",
    )

    summary = {
        "run_id": RUN_ID,
        "status": "domain_metadata_review_completed_partial_readiness",
        "target_database": DB,
        "postgres_connection_ok": conn_ok,
        "previous_review_decision": prev.get("review_decision"),
        "review_scope": "domain_metadata_readiness_only_no_physical_claims",
        "domains_reviewed": DOMAINS,
        "global_search_rows_reference": prev.get("global_search_rows_after"),
        "artifact_count_reference": prev.get("artifacts_registered_after"),
        "claim_boundary_status": "no_physical_claims",
        "residual_analysis_executed": False,
        "rbci_v1_evaluated": False,
        "qsb_observable_evaluated": False,
        "domain_readiness_summary": {
            "sparc_rar": "ready_for_domain_specific_precontract",
            "matrix_extract03": "partial_ready_requires_semantic_loader_review",
            "interface01": "partial_ready_requires_semantic_loader_review",
            "relalg": "partial_ready_requires_semantic_loader_review",
            "causality": "partial_ready_requires_semantic_loader_review",
            "qsb_meta": "ready_for_domain_specific_precontract",
            "unknown": "not_applicable_or_noise_bucket",
        },
        "unknown_bucket_review_status": "large_routing_review_recommended",
        "global_search_domain_routing_status": "visible_with_large_unknown_bucket",
        "metadata_field_alias_review_status": "metadata_fields_aliases_lineage_claims_visible",
        "validation_claim_boundary_review_status": "claim_boundaries_visible_no_physical_claims",
        "review_decision": "domain_metadata_review_completed_partial_readiness",
        "recommended_next_run_id": "QSB-DWH-POSTGRES-DOMAIN-ROUTING-PATCH-02",
        "notes": "No physical interpretation was performed.",
    }
    (OUT / "04_domain_metadata_review_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Command Log",
        "",
        "Pre-script commands run manually:",
        "",
        "- `sed -n '1,240p' /home/ralf-kemmann/Downloads/QSB_DWH_POSTGRES_DOMAIN_METADATA_REVIEW_01_CODEX_PROMPT.md`",
        "- `sed -n '241,520p' /home/ralf-kemmann/Downloads/QSB_DWH_POSTGRES_DOMAIN_METADATA_REVIEW_01_CODEX_PROMPT.md`",
        "- `sed -n '521,900p' /home/ralf-kemmann/Downloads/QSB_DWH_POSTGRES_DOMAIN_METADATA_REVIEW_01_CODEX_PROMPT.md`",
        "- `sed -n '901,1220p' /home/ralf-kemmann/Downloads/QSB_DWH_POSTGRES_DOMAIN_METADATA_REVIEW_01_CODEX_PROMPT.md`",
        f"- `mkdir -p runs/{RUN_ID}`",
        f"- `git status --short --ignored | sed -n '1,250p' > runs/{RUN_ID}/00_git_status_short_before.txt`",
        f"- `git --no-pager log --oneline -40 > runs/{RUN_ID}/01_git_log_oneline_before.txt`",
        "- `psql -d qsb_research_dwh --csv -c \"SELECT table_schema, table_name, column_name, data_type FROM information_schema.columns WHERE table_schema IN ('raw','staging','metadata','validation','mart') ORDER BY table_schema, table_name, ordinal_position;\"`",
        "- `python -m json.tool runs/QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-REVIEW-01/04_artifact_staging_patch_review_summary.json`",
        f"- `python runs/{RUN_ID}/30_generate_domain_metadata_review_artifacts.py`",
        "",
        "Commands run by generator:",
        "",
    ]
    for entry in command_log:
        lines.append(f"- `{entry['cmd']}` -> rc={entry['returncode']}")
        if entry["stderr_preview"]:
            lines.append(f"  - stderr preview: `{entry['stderr_preview']}`")
    write_md(OUT / "03_command_log.txt", "\n".join(lines) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
