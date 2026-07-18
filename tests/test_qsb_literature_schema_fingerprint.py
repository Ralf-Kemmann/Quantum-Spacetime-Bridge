from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.qsb_literature_metadata.native_contract_constants import CONFLICT_CLASSES, LOOKUP_OUTCOMES, OPERATION_TYPES
from scripts.qsb_literature_metadata.native_metadata_mapping import schema_fingerprint, validate_required_schema


META_DB = ROOT / "runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite"


def test_all_lookup_outcomes_conflict_classes_and_operation_types_declared():
    assert set(LOOKUP_OUTCOMES) == {
        "resolved_existing",
        "resolved_create_candidate",
        "resolved_noop",
        "blocked_missing_parent",
        "blocked_multiple_matches",
        "blocked_contract_violation",
    }
    assert set(OPERATION_TYPES) == {"lookup", "insert_candidate", "update_candidate", "no_op_candidate", "block"}
    assert "blocked_claim_boundary_mismatch" in CONFLICT_CLASSES
    assert "vocabulary_entry_addition_candidate" in CONFLICT_CLASSES


def test_schema_fingerprint_mismatch_is_detectable(tmp_path):
    with sqlite3.connect(f"file:{META_DB.resolve().as_posix()}?mode=ro", uri=True) as conn:
        original = schema_fingerprint(conn)
    temp = tmp_path / "empty.sqlite"
    with sqlite3.connect(temp) as conn:
        conn.execute("CREATE TABLE only_fixture(id TEXT PRIMARY KEY)")
        changed = schema_fingerprint(conn)
        missing = validate_required_schema(conn)
    assert original != changed
    assert "meta_object" in missing
