from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.qsb_literature_metadata.native_metadata_mapping import apply_operations_to_temp_db, build_operation_plan, read_registration_plan


PLAN = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv"
META_DB = ROOT / "runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite"


def test_rollback_restores_temp_transaction(tmp_path):
    db_copy = tmp_path / "metadata.sqlite"
    shutil.copy2(META_DB, db_copy)
    operations = build_operation_plan(read_registration_plan(PLAN))
    with sqlite3.connect(db_copy) as conn:
        conn.execute("BEGIN")
        apply_operations_to_temp_db(conn, operations)
        conn.commit()
        before = conn.execute("SELECT COUNT(*) FROM qsb_literature_native_operation_dryrun").fetchone()[0]
        conn.execute("BEGIN")
        conn.execute("INSERT INTO qsb_literature_native_validation_dryrun VALUES (?,?,?)", ("probe", "pass", "temporary"))
        conn.rollback()
        after = conn.execute("SELECT COUNT(*) FROM qsb_literature_native_operation_dryrun").fetchone()[0]
    assert before == after == 170


def test_alias_collision_policy_is_deterministic():
    from scripts.qsb_literature_metadata.native_metadata_mapping import RegistrationPlanRow, detect_alias_collisions

    base = {
        "table_name": "t",
        "field_name": "a",
        "de_label": "Label",
        "en_label": "Label",
        "description_de": "",
        "description_en": "",
        "data_type": "TEXT",
        "allowed_values": "",
        "lineage_note": "",
        "claim_boundary_note": "",
    }
    rows = [
        RegistrationPlanRow("RP01", canonical_name="a", **base),
        RegistrationPlanRow("RP02", canonical_name="b", **base),
    ]
    assert detect_alias_collisions(rows)
