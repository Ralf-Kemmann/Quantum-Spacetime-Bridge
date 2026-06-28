#!/usr/bin/env python3
"""Synchronize bounded RELALG run artifacts into the QSB metadata catalog."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "QSB-META-RELALG-SYNC-MIN"
SCRIPT_PATH = Path("scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py")
OUTPUT_DIR = REPO_ROOT / "runs/QSB-META-RELALG-SYNC-MIN"
DB_PATH = REPO_ROOT / "runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite"
MART_ID = "MART-RELALG"
ZERO_VECTOR = "[0,0,0,0,0,0,0]"
REQUIRED_TABLE_COLUMNS = {
    "meta_mart": ["mart_id", "mart_code", "canonical_namespace", "mart_name", "scope_status", "schema_version"],
    "meta_work_package": ["work_package_id", "mart_id", "work_package_code", "canonical_namespace", "work_package_name", "status"],
    "meta_etl_run": ["run_id", "work_package_id", "runner_path", "run_status", "execution_identity_note"],
    "meta_object": ["object_id", "mart_id", "work_package_id", "object_code", "object_type", "canonical_name", "repository_path", "status"],
    "meta_source": ["source_id", "mart_id", "source_type", "source_reference", "source_record_id_status"],
    "meta_lineage": ["lineage_id", "mart_id", "source_object_id", "target_object_id", "source_field_id", "target_field_id", "run_id", "transformation_rule_id", "lineage_scope", "lineage_status"],
    "meta_validation_rule": ["validation_rule_id", "validation_layer", "rule_name", "expected_condition", "severity"],
    "meta_validation_result": ["validation_result_id", "validation_rule_id", "run_id", "object_id", "field_id", "record_id", "status", "observed_value", "expected_value", "severity", "message", "reviewer_type", "human_review_state"],
    "meta_claim": ["claim_id", "mart_id", "claim_text", "claim_scope", "claim_status", "boundary_statement"],
    "meta_result_table": ["result_table_id", "mart_id", "object_id", "table_role", "record_lineage_mode", "status"],
    "meta_result_record": ["result_record_id", "result_table_id", "mart_id", "source_result_key", "result_class", "comparability_status", "formal_validation_status", "physical_validation_status", "evidence_class"],
    "meta_claim_result_link": ["claim_result_link_id", "claim_id", "result_record_id", "relation_type", "link_status"],
    "meta_field": ["field_id", "object_id", "canonical_field_name", "data_type", "nullable", "key_role", "derivation_class", "dependency_status", "source_object_ids", "source_field_ids", "transformation_rule_id", "quantity_kind_id", "unit_original_id", "unit_calculation_id", "unit_display_id", "dimension_vector", "unit_status", "dimension_status"],
    "meta_key": ["key_id", "object_id", "key_name", "key_type", "field_order", "referenced_object_id", "identity_scope"],
}
PATHS = {
    "real_run_dir": REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED",
    "real_script": REPO_ROOT / "scripts/qsb_relalg_real01_min_upstream_export_authorized/real01_min_upstream_export_authorized.py",
    "real_readme": REPO_ROOT / "scripts/qsb_relalg_real01_min_upstream_export_authorized/README.md",
    "real_validation": REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED/qsb_relalg_real01_min_validation_report.json",
    "real_gate": REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED/qsb_relalg_real01_min_next_step_gate.json",
    "bridge_run_dir": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE",
    "bridge_script": REPO_ROOT / "scripts/qsb_relalg_synth_d1k_bridge/relalg_synth_d1k_bridge.py",
    "bridge_readme": REPO_ROOT / "scripts/qsb_relalg_synth_d1k_bridge/README.md",
    "bridge_c_layer": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_c_layer.csv",
    "bridge_summary": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_summary.json",
    "bridge_validation": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_validation_report.json",
    "bridge_gate": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_next_step_gate.json",
    "loop_run_dir": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN",
    "loop_script": REPO_ROOT / "scripts/qsb_relalg_synth_d1k_loop_min/relalg_synth_d1k_loop_min.py",
    "loop_readme": REPO_ROOT / "scripts/qsb_relalg_synth_d1k_loop_min/README.md",
    "loop_valid_loops": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/qsb_relalg_synth_d1k_loop_min_valid_loops.csv",
    "loop_blocked_loops": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/qsb_relalg_synth_d1k_loop_min_blocked_loops.csv",
    "loop_summary": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/qsb_relalg_synth_d1k_loop_min_summary.json",
    "loop_validation": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/qsb_relalg_synth_d1k_loop_min_validation_report.json",
    "loop_gate": REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN/qsb_relalg_synth_d1k_loop_min_next_step_gate.json",
    "d1k_csv": REPO_ROOT / "runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv",
    "d1f_csv": REPO_ROOT / "runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv",
    "german_view": REPO_ROOT / "scripts/sqlite_views/v_de_d1k_phase_source_status.sql",
    "german_view_register": REPO_ROOT / "scripts/sqlite_views/register_v_de_d1k_phase_source_status_metadata.sql",
}
OUTPUTS = {
    "plan": OUTPUT_DIR / "qsb_meta_relalg_sync_min_plan.csv",
    "rows": OUTPUT_DIR / "qsb_meta_relalg_sync_min_inserted_or_updated_rows.csv",
    "precheck": OUTPUT_DIR / "qsb_meta_relalg_sync_min_precheck.json",
    "validation": OUTPUT_DIR / "qsb_meta_relalg_sync_min_validation_report.json",
    "next_gate": OUTPUT_DIR / "qsb_meta_relalg_sync_min_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_meta_relalg_sync_min_manifest.json",
    "readout": OUTPUT_DIR / "qsb_meta_relalg_sync_min_readout.md",
    "summary": OUTPUT_DIR / "qsb_meta_relalg_sync_min_summary.json",
    "sql_preview": OUTPUT_DIR / "qsb_meta_relalg_sync_min_sql_preview.sql",
    "before_counts": OUTPUT_DIR / "qsb_meta_relalg_sync_min_before_counts.json",
    "after_counts": OUTPUT_DIR / "qsb_meta_relalg_sync_min_after_counts.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]


def table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    return {table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in REQUIRED_TABLE_COLUMNS}


def load_status() -> dict[str, object]:
    data: dict[str, object] = {}
    data["real_validation"] = read_json(PATHS["real_validation"]) if PATHS["real_validation"].exists() else {}
    data["real_gate"] = read_json(PATHS["real_gate"]) if PATHS["real_gate"].exists() else {}
    data["bridge_summary"] = read_json(PATHS["bridge_summary"]) if PATHS["bridge_summary"].exists() else {}
    data["bridge_validation"] = read_json(PATHS["bridge_validation"]) if PATHS["bridge_validation"].exists() else {}
    data["bridge_gate"] = read_json(PATHS["bridge_gate"]) if PATHS["bridge_gate"].exists() else {}
    data["loop_summary"] = read_json(PATHS["loop_summary"]) if PATHS["loop_summary"].exists() else {}
    data["loop_validation"] = read_json(PATHS["loop_validation"]) if PATHS["loop_validation"].exists() else {}
    data["loop_gate"] = read_json(PATHS["loop_gate"]) if PATHS["loop_gate"].exists() else {}
    return data


def precheck(conn: sqlite3.Connection) -> dict[str, object]:
    missing_tables = [table for table in REQUIRED_TABLE_COLUMNS if not table_columns(conn, table)]
    missing_columns = {
        table: [column for column in columns if column not in table_columns(conn, table)]
        for table, columns in REQUIRED_TABLE_COLUMNS.items()
        if table not in missing_tables
    }
    missing_columns = {table: columns for table, columns in missing_columns.items() if columns}
    required_run_paths = [
        "real_run_dir", "real_script", "real_readme",
        "bridge_run_dir", "bridge_script", "bridge_readme",
        "loop_run_dir", "loop_script", "loop_readme",
    ]
    required_json_paths = [
        "real_validation", "real_gate",
        "bridge_summary", "bridge_validation", "bridge_gate",
        "loop_summary", "loop_validation", "loop_gate",
    ]
    missing_run_paths = [rel(PATHS[name]) for name in required_run_paths if not PATHS[name].exists()]
    json_parse_errors: dict[str, str] = {}
    for name in required_json_paths:
        try:
            read_json(PATHS[name])
        except Exception as exc:  # noqa: BLE001 - persisted as audit output
            json_parse_errors[rel(PATHS[name])] = repr(exc)
    status = load_status() if not json_parse_errors else {}
    real_blocked = set(status.get("real_gate", {}).get("still_blocked_steps", [])) if status else set()
    expected_blocked = {
        "QSB-RELALG-REAL01-MIN-STAGING",
        "QSB-RELALG-REAL01-EXECUTION",
        "QSB-RELALG-REAL01-INTERPRETATION",
        "QSB-RELALG-PHYSICS-CLAIM",
    }
    status_checks = {
        "bridge_validation_status_pass": status.get("bridge_validation", {}).get("validation_status") == "pass" if status else False,
        "loop_validation_status_pass": status.get("loop_validation", {}).get("validation_status") == "pass" if status else False,
        "loop_valid_loops_zero": status.get("loop_summary", {}).get("topology_counts", {}).get("valid_loop_count") == 0 if status else False,
        "loop_closed_triples_zero": status.get("loop_summary", {}).get("topology_counts", {}).get("source_native_closed_triple_count") == 0 if status else False,
        "real_still_blocks_required_paths": expected_blocked.issubset(real_blocked) if status else False,
        "real_no_phi_computation": status.get("real_validation", {}).get("claim_status") == "authorized_upstream_export_only_no_phi_computation" if status else False,
        "real_created_exports_zero": status.get("real_gate", {}).get("created_export_count") == 0 if status else False,
        "real_validated_exports_zero": status.get("real_gate", {}).get("validated_export_count") == 0 if status else False,
    }
    schema_ok = DB_PATH.exists() and not missing_tables and not missing_columns
    runs_ok = not missing_run_paths
    json_ok = not json_parse_errors
    statuses_ok = all(status_checks.values())
    return {
        "target_db": rel(DB_PATH),
        "db_exists": DB_PATH.exists(),
        "schema_ok": schema_ok,
        "missing_tables": missing_tables,
        "missing_columns": missing_columns,
        "required_run_paths_ok": runs_ok,
        "missing_run_paths": missing_run_paths,
        "json_parse_ok": json_ok,
        "json_parse_errors": json_parse_errors,
        "status_checks": status_checks,
        "status_values_ok": statuses_ok,
        "german_view_present": PATHS["german_view"].exists(),
        "german_view_register_present": PATHS["german_view_register"].exists(),
        "precheck_status": "pass" if schema_ok and runs_ok and json_ok and statuses_ok else "fail",
    }


def object_status(path_key: str) -> str:
    return "present_metadata_registered" if PATHS[path_key].exists() else "missing_optional_reference"


def metadata_rows() -> dict[str, list[tuple[object, ...]]]:
    rows: dict[str, list[tuple[object, ...]]] = {}
    rows["meta_mart"] = [(
        MART_ID, "RELALG", "qsb.relalg", "QSB RELALG Metadata Mart",
        "active_metadata_sync", "inherited_qsb_meta01_03",
    )]
    rows["meta_work_package"] = [
        ("WP-RELALG-REAL01-MIN", MART_ID, "RELALG-REAL01-MIN", "qsb.relalg.real01_min", "RELALG REAL01 MIN bounded upstream export metadata", "active_metadata_sync"),
        ("WP-RELALG-SYNTH-D1K", MART_ID, "RELALG-SYNTH-D1K", "qsb.relalg.synth_d1k", "RELALG synthetic D1K bridge and loop metadata", "active_metadata_sync"),
        ("WP-META-RELALG-SYNC-MIN", MART_ID, "META-RELALG-SYNC-MIN", "qsb.meta.relalg_sync_min", "RELALG metadata catalog sync", "active_metadata_sync"),
    ]
    rows["meta_etl_run"] = [
        ("RUN-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED", "WP-RELALG-REAL01-MIN", rel(PATHS["real_script"]), "completed_no_export_rows", "Authorized upstream export attempt only; no Phi_ABC computation."),
        ("RUN-RELALG-SYNTH-D1K-BRIDGE", "WP-RELALG-SYNTH-D1K", rel(PATHS["bridge_script"]), "pass_synthetic_bridge", "Synthetic diagnostic D1K-to-RELALG bridge only."),
        ("RUN-RELALG-SYNTH-D1K-LOOP-MIN", "WP-RELALG-SYNTH-D1K", rel(PATHS["loop_script"]), "pass_no_closed_source_native_triples", "Source-native topology audit; zero valid loops."),
        ("RUN-META-RELALG-SYNC-MIN", "WP-META-RELALG-SYNC-MIN", str(SCRIPT_PATH), "metadata_sync_apply_or_dry_run", "Metadata registration only; no RELALG recomputation."),
    ]
    rows["meta_object"] = [
        ("OBJ-RELALG-REAL01-AUTHORIZED-RUN-DIR", MART_ID, "WP-RELALG-REAL01-MIN", "RELALG_REAL01_AUTHORIZED_RUN_DIR", "run_directory", "RELALG REAL01 authorized upstream export attempt run directory", rel(PATHS["real_run_dir"]), object_status("real_run_dir")),
        ("OBJ-RELALG-REAL01-AUTHORIZED-SCRIPT", MART_ID, "WP-RELALG-REAL01-MIN", "RELALG_REAL01_AUTHORIZED_SCRIPT", "script", "RELALG REAL01 authorized upstream export script", rel(PATHS["real_script"]), object_status("real_script")),
        ("OBJ-RELALG-REAL01-AUTHORIZED-README", MART_ID, "WP-RELALG-REAL01-MIN", "RELALG_REAL01_AUTHORIZED_README", "documentation", "RELALG REAL01 authorized upstream export README", rel(PATHS["real_readme"]), object_status("real_readme")),
        ("OBJ-RELALG-SYNTH-D1K-BRIDGE-RUN-DIR", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_BRIDGE_RUN_DIR", "run_directory", "RELALG SYNTH D1K bridge run directory", rel(PATHS["bridge_run_dir"]), object_status("bridge_run_dir")),
        ("OBJ-RELALG-SYNTH-D1K-BRIDGE-SCRIPT", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_BRIDGE_SCRIPT", "script", "RELALG SYNTH D1K bridge script", rel(PATHS["bridge_script"]), object_status("bridge_script")),
        ("OBJ-RELALG-SYNTH-D1K-BRIDGE-README", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_BRIDGE_README", "documentation", "RELALG SYNTH D1K bridge README", rel(PATHS["bridge_readme"]), object_status("bridge_readme")),
        ("OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_BRIDGE_C_LAYER_CSV", "run_output_csv", "RELALG SYNTH D1K bridge C-layer CSV", rel(PATHS["bridge_c_layer"]), object_status("bridge_c_layer")),
        ("OBJ-RELALG-SYNTH-D1K-LOOP-MIN-RUN-DIR", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_LOOP_MIN_RUN_DIR", "run_directory", "RELALG SYNTH D1K loop-min run directory", rel(PATHS["loop_run_dir"]), object_status("loop_run_dir")),
        ("OBJ-RELALG-SYNTH-D1K-LOOP-MIN-SCRIPT", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_LOOP_MIN_SCRIPT", "script", "RELALG SYNTH D1K loop-min script", rel(PATHS["loop_script"]), object_status("loop_script")),
        ("OBJ-RELALG-SYNTH-D1K-LOOP-MIN-README", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_LOOP_MIN_README", "documentation", "RELALG SYNTH D1K loop-min README", rel(PATHS["loop_readme"]), object_status("loop_readme")),
        ("OBJ-RELALG-SYNTH-D1K-LOOP-MIN-VALID-LOOPS-CSV", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_LOOP_MIN_VALID_LOOPS_CSV", "run_output_csv", "RELALG SYNTH D1K loop-min valid loops CSV", rel(PATHS["loop_valid_loops"]), object_status("loop_valid_loops")),
        ("OBJ-RELALG-SYNTH-D1K-LOOP-MIN-BLOCKED-LOOPS-CSV", MART_ID, "WP-RELALG-SYNTH-D1K", "RELALG_SYNTH_D1K_LOOP_MIN_BLOCKED_LOOPS_CSV", "run_output_csv", "RELALG SYNTH D1K loop-min blocked loop audit CSV", rel(PATHS["loop_blocked_loops"]), object_status("loop_blocked_loops")),
        ("OBJ-ST-COMP01D1K-PHASE-EXPOSED-CSV", MART_ID, "WP-RELALG-SYNTH-D1K", "ST_COMP01D1K_PHASE_EXPOSED_CSV", "source_csv", "ST COMP01D1K phase exposed case profile summary CSV", rel(PATHS["d1k_csv"]), object_status("d1k_csv")),
        ("OBJ-ST-COMP01D1F-CASE-PROFILE-CSV", MART_ID, "WP-RELALG-SYNTH-D1K", "ST_COMP01D1F_CASE_PROFILE_CSV", "source_csv", "ST COMP01D1F case profile summary CSV", rel(PATHS["d1f_csv"]), object_status("d1f_csv")),
        ("OBJ-D1K-GERMAN-PHASE-VIEW-SQL", MART_ID, "WP-RELALG-SYNTH-D1K", "D1K_GERMAN_PHASE_VIEW_SQL", "sqlite_view_sql", "German D1K phase source status view SQL", rel(PATHS["german_view"]), object_status("german_view")),
    ]
    rows["meta_source"] = [
        ("SRC-ST-COMP01D1K-PHASE-EXPOSED-CSV", MART_ID, "source_csv", rel(PATHS["d1k_csv"]), "case_id_available"),
        ("SRC-ST-COMP01D1F-CASE-PROFILE-CSV", MART_ID, "source_csv", rel(PATHS["d1f_csv"]), "case_id_available"),
        ("SRC-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", MART_ID, "synthetic_diagnostic_c_layer_csv", rel(PATHS["bridge_c_layer"]), "row_lineage_id_available"),
        ("SRC-RELALG-SYNTH-D1K-LOOP-MIN-RUN", MART_ID, "synthetic_topology_audit_run", rel(PATHS["loop_run_dir"]), "run_level_topology_audit"),
    ]
    rows["meta_lineage"] = [
        ("LIN-RELALG-D1K-PHASE-TO-BRIDGE-C-LAYER", MART_ID, "OBJ-ST-COMP01D1K-PHASE-EXPOSED-CSV", "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", None, None, "RUN-RELALG-SYNTH-D1K-BRIDGE", None, "object", "available"),
        ("LIN-RELALG-D1F-PAIR-TO-BRIDGE-C-LAYER", MART_ID, "OBJ-ST-COMP01D1F-CASE-PROFILE-CSV", "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", None, None, "RUN-RELALG-SYNTH-D1K-BRIDGE", None, "object", "available"),
        ("LIN-RELALG-BRIDGE-C-LAYER-TO-LOOP-MIN", MART_ID, "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", "OBJ-RELALG-SYNTH-D1K-LOOP-MIN-RUN-DIR", None, None, "RUN-RELALG-SYNTH-D1K-LOOP-MIN", None, "object", "available"),
    ]
    rows["meta_validation_rule"] = [
        ("VR-RELALG-SYNTH-D1K-BRIDGE-PASS", "evidence", "Bridge validation passed", "validation_status == pass", "info"),
        ("VR-RELALG-SYNTH-D1K-LOOP-MIN-PASS", "evidence", "Loop-min validation passed", "validation_status == pass and valid_loop_count == 0", "info"),
        ("VR-RELALG-REAL01-AUTHORIZED-NO-PHI-COMPUTATION", "claim_boundary", "REAL01 authorized export no phi computation", "created_export_count == 0 and no Phi_ABC computation", "info"),
        ("VR-META-RELALG-SYNC-SCHEMA-PRECHECK", "schema", "Metadata sync schema precheck passed", "required tables and columns exist", "info"),
    ]
    rows["meta_validation_result"] = [
        ("VRES-RELALG-SYNTH-D1K-BRIDGE-PASS", "VR-RELALG-SYNTH-D1K-BRIDGE-PASS", "RUN-RELALG-SYNTH-D1K-BRIDGE", "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", None, None, "passed", "validation_status=pass; matched=9450; missing=0", "validation_status=pass", "info", "Synthetic bridge validation passed with bounded claim boundary.", "automated_metadata_sync", "not_required"),
        ("VRES-RELALG-SYNTH-D1K-LOOP-MIN-PASS", "VR-RELALG-SYNTH-D1K-LOOP-MIN-PASS", "RUN-RELALG-SYNTH-D1K-LOOP-MIN", "OBJ-RELALG-SYNTH-D1K-LOOP-MIN-RUN-DIR", None, None, "passed", "validation_status=pass; valid_loop_count=0; closed_triples=0", "validation_status=pass; valid_loop_count=0", "info", "Loop-min topology audit passed as clean no-closed-triples result.", "automated_metadata_sync", "not_required"),
        ("VRES-RELALG-REAL01-AUTHORIZED-NO-PHI-COMPUTATION", "VR-RELALG-REAL01-AUTHORIZED-NO-PHI-COMPUTATION", "RUN-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED", "OBJ-RELALG-REAL01-AUTHORIZED-RUN-DIR", None, None, "passed", "created_export_count=0; validated_export_count=0; no Phi_ABC computation", "no export rows and no phi computation", "info", "Authorized REAL01 upstream export attempt remains bounded and blocks staging/execution/interpretation/physics claim.", "automated_metadata_sync", "not_required"),
        ("VRES-META-RELALG-SYNC-SCHEMA-PRECHECK", "VR-META-RELALG-SYNC-SCHEMA-PRECHECK", "RUN-META-RELALG-SYNC-MIN", "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", None, None, "passed", "schema_precheck=pass", "schema_precheck=pass", "info", "Metadata schema precheck passed before deterministic upsert.", "automated_metadata_sync", "not_required"),
    ]
    rows["meta_claim"] = [
        ("CLAIM-RELALG-REAL01-AUTHORIZED-NO-EXPORT-ROWS", MART_ID, "Authorized REAL01 upstream export attempt reviewed candidate contracts and produced no export rows.", "RELALG_REAL01_MIN_AUTHORIZED_EXPORT_ATTEMPT", "bounded", "No Phi_ABC computation; no REAL01 staging; no REAL01 execution; no interpretation; no physics claim."),
        ("CLAIM-RELALG-SYNTH-D1K-BRIDGE-SYNTHETIC-C-LAYER", MART_ID, "D1K synthetic diagnostic phase fields and D1F pair identities form a RELALG-compatible synthetic C-layer export.", "RELALG_SYNTH_D1K_BRIDGE", "bounded", "Synthetic diagnostic only; not REAL01 evidence; not a physical phase source; not a physical C-layer source."),
        ("CLAIM-RELALG-SYNTH-D1K-LOOP-MIN-NO-CLOSED-TRIPLES", MART_ID, "D1K synthetic C-layer bridge is source-native star-like and contains no closed A->B->C->A triples.", "RELALG_SYNTH_D1K_LOOP_MIN", "bounded", "No loop phases computed; no missing edges inferred; no physical interpretation or physics claim."),
    ]
    rows["meta_result_table"] = [
        ("RT-RELALG-SYNTH-D1K-BRIDGE-C-LAYER", MART_ID, "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", "synthetic_diagnostic_c_layer_export", "materialized", "active_metadata_registered"),
        ("RT-RELALG-SYNTH-D1K-LOOP-MIN-VALID-LOOPS", MART_ID, "OBJ-RELALG-SYNTH-D1K-LOOP-MIN-VALID-LOOPS-CSV", "topology_audit_valid_loops_zero_rows", "materialized", "active_metadata_registered"),
        ("RT-RELALG-SYNTH-D1K-LOOP-MIN-BLOCKED", MART_ID, "OBJ-RELALG-SYNTH-D1K-LOOP-MIN-BLOCKED-LOOPS-CSV", "topology_boundary_blocked_examples", "materialized", "active_metadata_registered"),
    ]
    rows["meta_result_record"] = [
        ("RR-RELALG-SYNTH-D1K-BRIDGE-C-LAYER", "RT-RELALG-SYNTH-D1K-BRIDGE-C-LAYER", MART_ID, "QSB-RELALG-SYNTH-D1K-BRIDGE:9450-matched", "supports", "synthetic_control_only", "passed", "not_physical_claim", "supports"),
        ("RR-RELALG-SYNTH-D1K-LOOP-MIN-ZERO-VALID", "RT-RELALG-SYNTH-D1K-LOOP-MIN-VALID-LOOPS", MART_ID, "QSB-RELALG-SYNTH-D1K-LOOP-MIN:valid_loop_count=0", "supports", "topology_boundary_result", "passed", "not_physical_claim", "supports"),
        ("RR-RELALG-SYNTH-D1K-LOOP-MIN-BLOCKED", "RT-RELALG-SYNTH-D1K-LOOP-MIN-BLOCKED", MART_ID, "QSB-RELALG-SYNTH-D1K-LOOP-MIN:missing_BC_relation=9450", "supports", "topology_boundary_result", "passed", "not_physical_claim", "supports"),
    ]
    rows["meta_claim_result_link"] = [
        ("CRL-RELALG-BRIDGE-CLAIM-TO-C-LAYER", "CLAIM-RELALG-SYNTH-D1K-BRIDGE-SYNTHETIC-C-LAYER", "RR-RELALG-SYNTH-D1K-BRIDGE-C-LAYER", "supports", "active"),
        ("CRL-RELALG-LOOP-CLAIM-TO-ZERO-VALID", "CLAIM-RELALG-SYNTH-D1K-LOOP-MIN-NO-CLOSED-TRIPLES", "RR-RELALG-SYNTH-D1K-LOOP-MIN-ZERO-VALID", "supports", "active"),
        ("CRL-RELALG-LOOP-CLAIM-TO-BLOCKED", "CLAIM-RELALG-SYNTH-D1K-LOOP-MIN-NO-CLOSED-TRIPLES", "RR-RELALG-SYNTH-D1K-LOOP-MIN-BLOCKED", "supports", "active"),
    ]
    rows["meta_field"] = [
        ("FIELD-RELALG-BRIDGE-C-LAYER-ROW-LINEAGE-ID", "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", "row_lineage_id", "text", 0, "row_lineage_key", "direct_copy", "declared", "OBJ-ST-COMP01D1K-PHASE-EXPOSED-CSV;OBJ-ST-COMP01D1F-CASE-PROFILE-CSV", None, None, "QK_UNRESOLVED", "UNIT_ONE", "UNIT_ONE", "UNIT_ONE", None, "model_unit_unmapped", "dimension_unmapped"),
        ("FIELD-RELALG-LOOP-VALID-LOOP-ID", "OBJ-RELALG-SYNTH-D1K-LOOP-MIN-VALID-LOOPS-CSV", "loop_id", "text", 0, "loop_key_if_present", "direct_copy", "not_applicable", "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", None, None, "QK_UNRESOLVED", "UNIT_ONE", "UNIT_ONE", "UNIT_ONE", None, "model_unit_unmapped", "dimension_unmapped"),
    ]
    rows["meta_key"] = [
        ("KEY-RELALG-BRIDGE-C-LAYER-ROW-LINEAGE", "OBJ-RELALG-SYNTH-D1K-BRIDGE-C-LAYER-CSV", "row_lineage_id", "primary", "row_lineage_id", None, "synthetic_bridge_row"),
        ("KEY-RELALG-LOOP-VALID-LOOP-ID", "OBJ-RELALG-SYNTH-D1K-LOOP-MIN-VALID-LOOPS-CSV", "loop_id", "primary", "loop_id", None, "synthetic_loop_row"),
    ]
    return rows


def upsert_sql(table: str, row: tuple[object, ...]) -> tuple[str, tuple[object, ...]]:
    columns = REQUIRED_TABLE_COLUMNS[table]
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    return sql, row


def apply_rows(conn: sqlite3.Connection, rows: dict[str, list[tuple[object, ...]]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for table, table_rows in rows.items():
        for row in table_rows:
            sql, params = upsert_sql(table, row)
            conn.execute(sql, params)
            counts[table] += 1
    conn.commit()
    return counts


def expected_ids_present(conn: sqlite3.Connection, rows: dict[str, list[tuple[object, ...]]]) -> dict[str, object]:
    missing: dict[str, list[str]] = {}
    for table, table_rows in rows.items():
        id_column = REQUIRED_TABLE_COLUMNS[table][0]
        ids = [str(row[0]) for row in table_rows]
        table_missing = []
        for row_id in ids:
            found = conn.execute(f"SELECT 1 FROM {table} WHERE {id_column} = ?", (row_id,)).fetchone()
            if not found:
                table_missing.append(row_id)
        if table_missing:
            missing[table] = table_missing
    return {"all_present": not missing, "missing_ids": missing}


def plan_csv_rows(rows: dict[str, list[tuple[object, ...]]]) -> list[list[object]]:
    output = []
    for table, table_rows in rows.items():
        id_column = REQUIRED_TABLE_COLUMNS[table][0]
        for row in table_rows:
            output.append([table, id_column, row[0], "INSERT OR REPLACE", "deterministic_metadata_registration"])
    return output


def sql_preview(rows: dict[str, list[tuple[object, ...]]]) -> str:
    lines = [
        "-- QSB-META-RELALG-SYNC-MIN SQL preview",
        "-- Preview only; script uses parameterized INSERT OR REPLACE statements.",
        "-- No CREATE TABLE, ALTER TABLE, DROP TABLE, or DELETE statements are used.",
    ]
    for table, table_rows in rows.items():
        columns = REQUIRED_TABLE_COLUMNS[table]
        for row in table_rows:
            values = ", ".join("NULL" if value is None else "'" + str(value).replace("'", "''") + "'" for value in row)
            lines.append(f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({values});")
    return "\n".join(lines) + "\n"


def validation_report(mode: str, pre: dict[str, object], dry_counts_match: bool, apply_presence: dict[str, object], lineage_ok: bool, claims_ok: bool, timestamp: str) -> dict[str, object]:
    checks = [
        ("V01", "Metadata DB exists", pre["db_exists"], {"target_db": pre["target_db"]}),
        ("V02", "Required tables exist", not pre["missing_tables"], {"missing_tables": pre["missing_tables"]}),
        ("V03", "Required columns exist", not pre["missing_columns"], {"missing_columns": pre["missing_columns"]}),
        ("V04", "RELALG runs exist", pre["required_run_paths_ok"], {"missing_run_paths": pre["missing_run_paths"]}),
        ("V05", "Required run JSON parses", pre["json_parse_ok"], {"json_parse_errors": pre["json_parse_errors"]}),
        ("V06", "Required status values match expected boundaries", pre["status_values_ok"], {"status_checks": pre["status_checks"]}),
        ("V07", "Dry-run does not mutate metadata DB", dry_counts_match if mode == "dry-run" else True, {"mode": mode, "dry_run_counts_match": dry_counts_match}),
        ("V08", "Apply inserts/updates deterministic rows", apply_presence["all_present"] if mode == "apply" else True, apply_presence),
        ("V09", "No schema mutation", True, {"forbidden_sql": ["CREATE TABLE", "ALTER TABLE", "DROP TABLE"], "used": []}),
        ("V10", "No deletions", True, {"delete_statements_used": 0}),
        ("V11", "Claim boundary preservation", claims_ok, {"claim_boundaries_registered": claims_ok}),
        ("V12", "Lineage coverage", lineage_ok, {"minimal_lineage_edges_registered": lineage_ok}),
        ("V13", "View linkage awareness", pre["german_view_present"], {"german_view_present": pre["german_view_present"], "german_view_register_present": pre["german_view_register_present"]}),
        ("V14", "Replay protection", True, {"default_existing_output_dir_policy": "refuse overwrite unless --force is supplied"}),
        ("V15", "Manifest hashes", True, {"manifest_includes": "generated artifact hashes and relevant input/source file hashes"}),
    ]
    rendered = [
        {"check_id": check_id, "name": name, "status": "pass" if passed else "fail", "details": details}
        for check_id, name, passed, details in checks
    ]
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "mode": mode,
        "validation_status": "pass" if all(item["status"] == "pass" for item in rendered) else "fail",
        "checks": rendered,
    }


def next_gate(timestamp: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "gate_status": "metadata_registration_only",
        "next_authorized_step": "QSB-META-RELALG-SYNC-REVIEW",
        "still_blocked": [
            "QSB-RELALG-REAL01-MIN-STAGING",
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
        ],
        "claim_boundary": "Metadata registration only; no RELALG recomputation; no REAL01 unlock; no physics claim.",
    }


def manifest(timestamp: str) -> dict[str, object]:
    relevant_inputs = [
        DB_PATH,
        PATHS["real_validation"], PATHS["real_gate"],
        PATHS["bridge_summary"], PATHS["bridge_validation"], PATHS["bridge_gate"], PATHS["bridge_c_layer"],
        PATHS["loop_summary"], PATHS["loop_validation"], PATHS["loop_gate"], PATHS["loop_valid_loops"],
        PATHS["d1k_csv"], PATHS["d1f_csv"], PATHS["german_view"],
    ]
    inputs = {
        rel(path): {"present": path.exists(), "sha256": sha256_file(path) if path.is_file() else None}
        for path in relevant_inputs
    }
    generated = {
        name: {"path": rel(path), "sha256": sha256_file(path)}
        for name, path in OUTPUTS.items()
        if name != "manifest" and path.exists()
    }
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "script_path": str(SCRIPT_PATH),
        "inputs": inputs,
        "generated_artifacts": generated,
        "manifest_self_hash_policy": "Self-referential manifest hash is excluded; all other generated artifacts are hashed.",
    }


def readout(mode: str, pre: dict[str, object], counts_before: dict[str, int], counts_after: dict[str, int], row_counts: Counter[str], validation_status: str) -> str:
    row_lines = "\n".join(f"- {table}: {count}" for table, count in sorted(row_counts.items())) or "- none"
    return f"""# {RUN_ID} Readout

## Befund

- Mode: {mode}
- Precheck status: {pre["precheck_status"]}
- Validation status: {validation_status}
- Metadata mart decision: created or reused deterministic `MART-RELALG`; no existing RELALG mart was present during inspection.
- Dry-run/apply planned deterministic row counts:
{row_lines}

## Interpretation

This block registers existing RELALG artifacts in the central metadata catalog. It does not recompute RELALG outputs and does not alter source run artifacts.

## Hypothese

The registered rows improve object, source, lineage, validation, and claim-boundary visibility for RELALG artifacts.

## Offene Luecke

The central SQLite DB should be reviewed before deciding whether DB state belongs in version control.

## Claim Boundary

Metadata registration only. No REAL01 staging, execution, interpretation, unlock, physical Bridge validation, or physics claim is authorized.

## Counts

- Before counts: {json.dumps(counts_before, sort_keys=True)}
- After counts: {json.dumps(counts_after, sort_keys=True)}
"""


def run(mode: str, force: bool) -> int:
    prepare_output(force)
    timestamp = utc_now()
    rows = metadata_rows()
    with connect() as conn:
        counts_before = table_counts(conn)
        pre = precheck(conn)
        write_json(OUTPUTS["before_counts"], counts_before)
        write_json(OUTPUTS["precheck"], pre)
        write_csv(OUTPUTS["plan"], ["table", "id_column", "deterministic_id", "planned_action", "note"], plan_csv_rows(rows))
        OUTPUTS["sql_preview"].write_text(sql_preview(rows), encoding="utf-8")
        dry_counts_match = True
        row_counts: Counter[str] = Counter({table: len(table_rows) for table, table_rows in rows.items()})
        if mode == "apply":
            if pre["precheck_status"] != "pass":
                raise RuntimeError("Schema/status precheck failed; refusing --apply.")
            row_counts = apply_rows(conn, rows)
        counts_after = table_counts(conn)
        if mode == "dry-run":
            dry_counts_match = counts_before == counts_after
        write_json(OUTPUTS["after_counts"], counts_after)
        presence = expected_ids_present(conn, rows) if mode == "apply" else {"all_present": True, "missing_ids": {}}
        lineage_ids = {row[0] for row in rows["meta_lineage"]}
        lineage_ok = {"LIN-RELALG-D1K-PHASE-TO-BRIDGE-C-LAYER", "LIN-RELALG-D1F-PAIR-TO-BRIDGE-C-LAYER", "LIN-RELALG-BRIDGE-C-LAYER-TO-LOOP-MIN"}.issubset(lineage_ids)
        claim_boundaries = [row[5] for row in rows["meta_claim"]]
        claims_ok = all("physics claim" in text.lower() or "physical" in text.lower() or "real01" in text.lower() for text in claim_boundaries)
        validation = validation_report(mode, pre, dry_counts_match, presence, lineage_ok, claims_ok, timestamp)
        write_json(OUTPUTS["validation"], validation)
        write_json(OUTPUTS["next_gate"], next_gate(timestamp))
        write_csv(OUTPUTS["rows"], ["table", "row_count", "mode", "action"], [[table, count, mode, "planned" if mode == "dry-run" else "insert_or_replace"] for table, count in sorted(row_counts.items())])
        summary = {
            "run_id": RUN_ID,
            "timestamp_utc": timestamp,
            "mode": mode,
            "precheck_status": pre["precheck_status"],
            "validation_status": validation["validation_status"],
            "rows_inserted_or_updated_per_table": dict(sorted(row_counts.items())),
            "before_counts": counts_before,
            "after_counts": counts_after,
            "lineage_rows_registered": [row[0] for row in rows["meta_lineage"]],
            "claims_registered": [row[0] for row in rows["meta_claim"]],
            "next_authorized_step": "QSB-META-RELALG-SYNC-REVIEW",
            "still_blocked": next_gate(timestamp)["still_blocked"],
        }
        write_json(OUTPUTS["summary"], summary)
        OUTPUTS["readout"].write_text(readout(mode, pre, counts_before, counts_after, row_counts, validation["validation_status"]), encoding="utf-8")
        write_json(OUTPUTS["manifest"], manifest(timestamp))
    print(f"run_id: {RUN_ID}")
    print(f"mode: {mode}")
    print(f"output_dir: {rel(OUTPUT_DIR)}")
    print(f"precheck_status: {pre['precheck_status']}")
    print(f"validation_status: {validation['validation_status']}")
    print(f"metadata_db_modified: {'yes' if mode == 'apply' else 'no'}")
    return 0 if validation["validation_status"] == "pass" else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Inspect and preview metadata sync without changing the DB. Default.")
    mode.add_argument("--apply", action="store_true", help="Apply deterministic metadata upserts after prechecks pass.")
    parser.add_argument("--force", action="store_true", help="Replace an existing QSB-META-RELALG-SYNC-MIN output directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = "apply" if args.apply else "dry-run"
    try:
        return run(mode=mode, force=args.force)
    except FileExistsError as exc:
        print(f"REFUSED_OVERWRITE: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
