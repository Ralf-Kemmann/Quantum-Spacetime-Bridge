from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.qsb_literature_metadata.native_metadata_mapping import apply_operations_to_temp_db, build_operation_plan, read_registration_plan


PLAN = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv"
META_DB = ROOT / "runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite"


def test_idempotent_second_application_is_noop(tmp_path):
    db_copy = tmp_path / "metadata.sqlite"
    shutil.copy2(META_DB, db_copy)
    operations = build_operation_plan(read_registration_plan(PLAN))
    with sqlite3.connect(db_copy) as conn:
        conn.execute("BEGIN")
        first = apply_operations_to_temp_db(conn, operations)
        conn.commit()
        conn.execute("BEGIN")
        second = apply_operations_to_temp_db(conn, operations)
        conn.commit()
    assert first["inserted"] == 170
    assert second["inserted"] == 0
    assert second["noop"] == 170


def test_quantity_unit_dimension_policy_preserves_states():
    from scripts.qsb_literature_metadata.native_metadata_mapping import quantity_policy

    rows = read_registration_plan(PLAN)
    policies = {row.field_name: quantity_policy(row) for row in rows}
    assert policies["literature_id"]["semantic_status"] == "identifier"
    assert policies["year"]["semantic_status"] == "temporal"
    assert policies["source_type"]["semantic_status"] == "categorical"
    assert policies["title"]["semantic_status"] == "textual"
    assert {p["unit_original"] for p in policies.values()} == {"not_applicable"}
    assert {p["missing"] for p in policies.values()} == {"preserved_distinct_from_unknown"}
