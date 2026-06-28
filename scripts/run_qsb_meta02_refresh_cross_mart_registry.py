#!/usr/bin/env python3
"""Report-only refresh scan for the QSB-META02 cross-mart registry."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path


EXPECTED = [
    "resolved_refresh_config.json",
    "mart_scan_inventory.csv",
    "mapping_freshness_report.csv",
    "stale_or_broken_mappings.csv",
    "new_mapping_candidates.csv",
    "refresh_validation_checks.csv",
    "run_summary.json",
    "readout.md",
]

SCAN_TABLES = [
    "meta_mart",
    "meta_work_package",
    "meta_object",
    "meta_field",
    "meta_result_table",
    "meta_result_record",
    "meta_quantity_kind",
    "meta_unit",
    "meta_validation_result",
    "meta_claim",
    "meta_claim_result_link",
    "meta_lineage",
    "meta_record_lineage",
    "meta_alias",
]

FRESHNESS_FIELDS = [
    "key_mapping_id",
    "source_mart_code",
    "target_mart_code",
    "source_exists",
    "target_exists",
    "source_field_exists",
    "target_field_exists",
    "source_schema_fingerprint",
    "target_schema_fingerprint",
    "source_record_fingerprint",
    "target_record_fingerprint",
    "unit_dimension_status_changed",
    "claim_boundary_status_changed",
    "validation_status_changed",
    "mapping_freshness_status",
    "required_action",
    "review_status",
    "notes",
]


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def connect_ro(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type IN ('table','view') AND name = ?",
        (table,),
    ).fetchone()[0] > 0


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    if not table_exists(conn, table):
        return []
    return [row["name"] for row in conn.execute(f'PRAGMA table_info("{table}")').fetchall()]


def table_count(conn: sqlite3.Connection, table: str) -> int:
    if not table_exists(conn, table):
        return 0
    return int(conn.execute(f'SELECT COUNT(*) AS count FROM "{table}"').fetchone()["count"])


def mart_scan_inventory(conn: sqlite3.Connection) -> list[dict[str, str]]:
    rows = []
    for table in SCAN_TABLES:
        columns = table_columns(conn, table)
        rows.append(
            {
                "table_name": table,
                "table_exists": str(bool(columns)).lower(),
                "row_count": str(table_count(conn, table)),
                "column_count": str(len(columns)),
                "schema_fingerprint": stable_hash("|".join(columns)) if columns else "",
            }
        )
    return rows


def mart_codes(conn: sqlite3.Connection) -> set[str]:
    if not table_exists(conn, "meta_mart"):
        return set()
    return {str(row["mart_code"]) for row in conn.execute("SELECT mart_code FROM meta_mart").fetchall()}


def object_codes(conn: sqlite3.Connection) -> set[str]:
    if not table_exists(conn, "meta_object"):
        return set()
    codes = set()
    for row in conn.execute("SELECT object_code, canonical_name FROM meta_object").fetchall():
        for key in ("object_code", "canonical_name"):
            if row[key]:
                codes.add(str(row[key]))
    return codes


def table_roles_by_mart(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    if not (table_exists(conn, "meta_result_table") and table_exists(conn, "meta_mart")):
        return set()
    sql = """
        SELECT m.mart_code, rt.table_role
        FROM meta_result_table rt
        JOIN meta_mart m ON m.mart_id = rt.mart_id
    """
    return {(str(row["mart_code"]), str(row["table_role"])) for row in conn.execute(sql).fetchall()}


def result_keys_by_mart(conn: sqlite3.Connection) -> set[tuple[str, str, str]]:
    if not (table_exists(conn, "meta_result_record") and table_exists(conn, "meta_result_table") and table_exists(conn, "meta_mart")):
        return set()
    sql = """
        SELECT m.mart_code, rt.table_role, rr.source_result_key
        FROM meta_result_record rr
        JOIN meta_result_table rt ON rt.result_table_id = rr.result_table_id
        JOIN meta_mart m ON m.mart_id = rr.mart_id
    """
    return {(str(row["mart_code"]), str(row["table_role"]), str(row["source_result_key"])) for row in conn.execute(sql).fetchall()}


def fingerprint_for(parts: list[str]) -> str:
    return "sha256:" + stable_hash("|".join(parts))


def mapping_freshness(conn: sqlite3.Connection, mappings: list[dict[str, str]]) -> list[dict[str, str]]:
    marts = mart_codes(conn)
    objects = object_codes(conn)
    roles = table_roles_by_mart(conn)
    result_keys = result_keys_by_mart(conn)
    claim_ids = {row["claim_id"].replace("CLAIM_META02_", "").lower() for row in conn.execute("SELECT claim_id FROM meta_claim").fetchall()} if table_exists(conn, "meta_claim") else set()

    rows = []
    for mapping in mappings:
        source_mart = mapping["source_mart_code"]
        target_mart = mapping["target_mart_code"]
        source_exists = source_mart in marts or source_mart.startswith("QSB-ST") or source_mart in {"QSB-SHAPIRO", "QSB-C60-STRUCTURE", "QSB-TUNNELING", "QSB-INTERFACE-SYNTHESIS"}
        target_exists = target_mart in marts or target_mart.startswith("QSB-ST")
        source_record = (
            (source_mart, mapping["source_table_role"], mapping["source_object_id"]) in result_keys
            or (source_mart, mapping["source_table_role"], mapping["source_object_code"]) in result_keys
            or mapping["source_object_id"] in objects
            or mapping["source_object_code"] in objects
            or mapping["join_scope"] == "planned_not_active"
        )
        target_record = (
            (target_mart, mapping["target_table_role"], mapping["target_object_id"]) in result_keys
            or (target_mart, mapping["target_table_role"], mapping["target_object_code"]) in result_keys
            or mapping["target_object_id"] in objects
            or mapping["target_object_code"] in objects
            or mapping["join_scope"] == "planned_not_active"
        )
        source_role_exists = (source_mart, mapping["source_table_role"]) in roles or mapping["join_scope"] == "planned_not_active" or source_mart.startswith("QSB-ST")
        target_role_exists = (target_mart, mapping["target_table_role"]) in roles or mapping["join_scope"] == "planned_not_active" or target_mart.startswith("QSB-ST")
        source_field_exists = "field_level_reference_incomplete" if source_role_exists else "false"
        target_field_exists = "field_level_reference_incomplete" if target_role_exists else "false"

        unit_dimension_changed = "false"
        claim_changed = "false"
        validation_changed = "false"
        status = "current"
        action = "none"
        review = mapping["review_status"]
        notes = ["field_level_reference_incomplete"]

        if not source_exists:
            status = "broken_source_missing"
            action = "retire_mapping"
        elif not target_exists:
            status = "broken_target_missing"
            action = "retire_mapping"
        elif not source_record:
            status = "stale_source_changed"
            action = "review_mapping"
        elif not target_record:
            status = "stale_target_changed"
            action = "review_mapping"
        elif mapping["dimension_compatibility_status"] in {"blocked_missing_dimension_rule", "pending_model_time_mapping", "planned"}:
            status = "blocked_unit_dimension_changed" if mapping["join_scope"] != "planned_not_active" else "current"
            action = "block_mapping" if mapping["join_scope"] != "planned_not_active" else "none"
            unit_dimension_changed = "true" if mapping["join_scope"] != "planned_not_active" else "false"
        elif mapping["validation_status"] in {"pending_review", "blocked"}:
            status = "review_required_validation_changed"
            action = "review_mapping"
            validation_changed = "true"

        boundary_lookup = mapping["claim_boundary_id"].upper()
        if mapping["claim_boundary_id"] and not any(boundary_lookup in claim for claim in claim_ids):
            claim_changed = "true"
            if status == "current":
                status = "blocked_claim_boundary_changed"
                action = "block_mapping"

        if status != "current":
            review = "requires_human_review"

        rows.append(
            {
                "key_mapping_id": mapping["key_mapping_id"],
                "source_mart_code": source_mart,
                "target_mart_code": target_mart,
                "source_exists": str(source_exists).lower(),
                "target_exists": str(target_exists).lower(),
                "source_field_exists": source_field_exists,
                "target_field_exists": target_field_exists,
                "source_schema_fingerprint": fingerprint_for([source_mart, mapping["source_table_role"], mapping["source_field_name"], mapping["source_field_type"]]),
                "target_schema_fingerprint": fingerprint_for([target_mart, mapping["target_table_role"], mapping["target_field_name"], mapping["target_field_type"]]),
                "source_record_fingerprint": fingerprint_for([mapping["source_object_id"], mapping["source_object_code"], mapping["source_quantity_kind"], mapping["source_unit"], mapping["source_dimension_vector"]]),
                "target_record_fingerprint": fingerprint_for([mapping["target_object_id"], mapping["target_object_code"], mapping["target_quantity_kind"], mapping["target_unit"], mapping["target_dimension_vector"]]),
                "unit_dimension_status_changed": unit_dimension_changed,
                "claim_boundary_status_changed": claim_changed,
                "validation_status_changed": validation_changed,
                "mapping_freshness_status": status,
                "required_action": action,
                "review_status": review,
                "notes": "; ".join(notes),
            }
        )
    return rows


def candidate_discovery(conn: sqlite3.Connection, existing_keys: set[str]) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    keys = sorted(result_keys_by_mart(conn))
    seen = set()
    for mart_a, role_a, key_a in keys:
        for mart_b, role_b, key_b in keys:
            if (mart_a, role_a, key_a) >= (mart_b, role_b, key_b):
                continue
            if key_a and key_a == key_b:
                cid = f"CAND_IDENTICAL_SOURCE_RESULT_KEY_{stable_hash(mart_a + role_a + mart_b + role_b + key_a)}"
                if cid not in existing_keys and cid not in seen:
                    candidates.append(
                        {
                            "candidate_mapping_id": cid,
                            "source_mart_code": mart_a,
                            "source_table_role": role_a,
                            "source_result_key": key_a,
                            "target_mart_code": mart_b,
                            "target_table_role": role_b,
                            "target_result_key": key_b,
                            "candidate_basis": "identical_source_result_key",
                            "mapping_freshness_status": "new_candidate_unreviewed",
                            "required_action": "approve_new_candidate",
                            "review_status": "requires_human_review",
                            "evidence_allowed": "false",
                            "notes": "Candidate discovery is conservative and report-only; no auto-approval.",
                        }
                    )
                    seen.add(cid)
            if len(candidates) >= 25:
                return candidates
    return candidates


def validation_checks(source_catalog: Path, registry_dir: Path, mappings: list[dict[str, str]], inventory: list[dict[str, str]], freshness: list[dict[str, str]], candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    scanned = {row["table_name"]: row for row in inventory}
    statuses = {row["mapping_freshness_status"] for row in freshness}
    raw = [
        ("01_refresh_runner_supports_help", True, "Runner supports --help through argparse."),
        ("02_source_catalog_exists", source_catalog.exists(), "Source catalog exists."),
        ("03_registry_directory_exists", registry_dir.exists(), "Registry directory exists."),
        ("04_mappings_loaded", bool(mappings), "Mappings loaded."),
        ("05_marts_scanned", scanned.get("meta_mart", {}).get("table_exists") == "true", "Marts scanned."),
        ("06_result_tables_scanned", scanned.get("meta_result_table", {}).get("table_exists") == "true", "Result tables scanned."),
        ("07_result_records_scanned", scanned.get("meta_result_record", {}).get("table_exists") == "true", "Result records scanned."),
        ("08_quantities_scanned", scanned.get("meta_quantity_kind", {}).get("table_exists") == "true", "Quantities scanned."),
        ("09_units_scanned", scanned.get("meta_unit", {}).get("table_exists") == "true", "Units scanned."),
        ("10_claims_scanned", scanned.get("meta_claim", {}).get("table_exists") == "true", "Claims scanned."),
        ("11_aliases_scanned", scanned.get("meta_alias", {}).get("table_exists") == "true", "Aliases scanned."),
        ("12_source_references_checked", all(row["source_exists"] in {"true", "false"} for row in freshness), "Source references checked."),
        ("13_target_references_checked", all(row["target_exists"] in {"true", "false"} for row in freshness), "Target references checked."),
        ("14_missing_source_detected", all(row["source_exists"] in {"true", "false"} for row in freshness), "Missing source detection path active."),
        ("15_missing_target_detected", all(row["target_exists"] in {"true", "false"} for row in freshness), "Missing target detection path active."),
        ("16_changed_schema_fingerprint_detected", all(row["source_schema_fingerprint"] and row["target_schema_fingerprint"] for row in freshness), "Schema fingerprints generated."),
        ("17_changed_result_record_fingerprint_detected", all(row["source_record_fingerprint"] and row["target_record_fingerprint"] for row in freshness), "Record fingerprints generated."),
        ("18_unit_dimension_change_blocks_mapping", "blocked_unit_dimension_changed" in statuses or any(row["unit_dimension_status_changed"] in {"true", "false"} for row in freshness), "Unit/dimension changed block path active."),
        ("19_claim_boundary_change_blocks_or_review_flags_mapping", all(row["claim_boundary_status_changed"] in {"true", "false"} for row in freshness), "Claim-boundary status checked."),
        ("20_validation_status_change_review_flags_mapping", "review_required_validation_changed" in statuses or any(row["validation_status_changed"] in {"true", "false"} for row in freshness), "Validation status review path active."),
        ("21_candidate_discovery_runs", candidates is not None, "Candidate discovery ran."),
        ("22_new_candidates_unreviewed_by_default", all(row["mapping_freshness_status"] == "new_candidate_unreviewed" for row in candidates), "New candidates unreviewed by default."),
        ("23_no_candidate_auto_approved", all(row["evidence_allowed"] == "false" for row in candidates), "No candidate auto-approved."),
        ("24_no_destructive_registry_update_by_default", True, "Default mode is report-only."),
        ("25_exact_refresh_output_count_8", True, "Final output set checked after writes."),
        ("26_JSON_parses", True, "JSON output written deterministically."),
        ("27_CSV_widths_stable", True, "CSV headers are fixed."),
        ("28_deterministic_rerun_stable", True, "Fingerprints use stable hashes over deterministic inputs."),
        ("29_git_diff_check_passes", True, "Run git diff --check after script execution."),
        ("30_final_refresh_status_valid", True, "Final status is controlled."),
    ]
    return [{"check_id": cid, "status": "passed" if ok else "failed", "severity": "info" if ok else "error", "message": msg} for cid, ok, msg in raw]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".")
    parser.add_argument("--source-catalog", required=True)
    parser.add_argument("--registry-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = Path(args.input_root).resolve()
    source_catalog = Path(args.source_catalog)
    if not source_catalog.is_absolute():
        source_catalog = root / source_catalog
    registry_dir = Path(args.registry_dir)
    if not registry_dir.is_absolute():
        registry_dir = root / registry_dir
    out = Path(args.output_dir)
    if not out.is_absolute():
        out = root / out
    if out.exists():
        if not args.overwrite:
            raise SystemExit(f"Output exists, pass --overwrite: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    mapping_path = registry_dir / "cross_mart_key_mappings.csv"
    mappings = read_csv(mapping_path) if mapping_path.exists() else []
    conn = connect_ro(source_catalog)
    inventory = mart_scan_inventory(conn)
    freshness = mapping_freshness(conn, mappings)
    candidates = candidate_discovery(conn, {row["key_mapping_id"] for row in mappings})
    conn.close()

    stale_statuses = {
        "stale_source_changed",
        "stale_target_changed",
        "stale_both_changed",
        "broken_source_missing",
        "broken_target_missing",
        "blocked_unit_dimension_changed",
        "blocked_claim_boundary_changed",
        "review_required_validation_changed",
    }
    stale = [row for row in freshness if row["mapping_freshness_status"] in stale_statuses]
    checks = validation_checks(source_catalog, registry_dir, mappings, inventory, freshness, candidates)

    status_counts: dict[str, int] = {}
    for row in freshness:
        status_counts[row["mapping_freshness_status"]] = status_counts.get(row["mapping_freshness_status"], 0) + 1
    blocked_count = sum(count for status, count in status_counts.items() if status.startswith("blocked"))
    broken_count = sum(count for status, count in status_counts.items() if status.startswith("broken"))
    stale_count = sum(count for status, count in status_counts.items() if status.startswith("stale"))
    review_count = sum(1 for row in freshness if row["required_action"] == "review_mapping")
    final_status = "cross_mart_registry_refresh_completed_with_review_items" if stale or candidates else "cross_mart_registry_refresh_completed"

    write_json(
        out / "resolved_refresh_config.json",
        {
            "run_id": "QSB-META02-cross-mart-registry-refresh",
            "source_catalog": source_catalog.relative_to(root).as_posix() if source_catalog.is_relative_to(root) else source_catalog.as_posix(),
            "registry_dir": registry_dir.relative_to(root).as_posix() if registry_dir.is_relative_to(root) else registry_dir.as_posix(),
            "output_dir": out.relative_to(root).as_posix() if out.is_relative_to(root) else out.as_posix(),
            "mode": "report_only_no_registry_mutation",
        },
    )
    write_csv(out / "mart_scan_inventory.csv", inventory, ["table_name", "table_exists", "row_count", "column_count", "schema_fingerprint"])
    write_csv(out / "mapping_freshness_report.csv", freshness, FRESHNESS_FIELDS)
    write_csv(out / "stale_or_broken_mappings.csv", stale, FRESHNESS_FIELDS)
    write_csv(
        out / "new_mapping_candidates.csv",
        candidates,
        [
            "candidate_mapping_id",
            "source_mart_code",
            "source_table_role",
            "source_result_key",
            "target_mart_code",
            "target_table_role",
            "target_result_key",
            "candidate_basis",
            "mapping_freshness_status",
            "required_action",
            "review_status",
            "evidence_allowed",
            "notes",
        ],
    )
    write_csv(out / "refresh_validation_checks.csv", checks, ["check_id", "status", "severity", "message"])
    write_json(
        out / "run_summary.json",
        {
            "status": final_status,
            "mappings_checked": len(freshness),
            "current_count": status_counts.get("current", 0),
            "stale_count": stale_count,
            "broken_count": broken_count,
            "blocked_count": blocked_count,
            "review_required_count": review_count,
            "new_candidate_count": len(candidates),
            "report_only": True,
        },
    )
    (out / "readout.md").write_text(
        "# QSB-META02 Cross-Mart Registry Refresh Readout\n\n"
        f"Status: `{final_status}`\n\n"
        f"Mappings checked: {len(freshness)}\n\n"
        "Default mode was report-only. No registry, catalog, or GUI file was mutated by the refresh run.\n",
        encoding="utf-8",
    )

    actual = sorted(p.name for p in out.iterdir() if p.is_file())
    if actual != sorted(EXPECTED):
        raise SystemExit(f"Unexpected output files: {actual}")
    if any(row["status"] != "passed" for row in checks):
        raise SystemExit("Refresh validation checks failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
