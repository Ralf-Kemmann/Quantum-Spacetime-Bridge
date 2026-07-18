from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.qsb_literature_metadata.native_contract_constants import CLAIM_BOUNDARY
from scripts.qsb_literature_metadata.native_metadata_mapping import build_operation_plan, read_registration_plan, validate_required_schema


PLAN = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv"
DATA_DB = ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db"
META_DB = ROOT / "runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite"
IMPORTER = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py"


def test_17_row_planning_and_170_operations():
    rows = read_registration_plan(PLAN)
    ops = build_operation_plan(rows)
    assert len(rows) == 17
    assert len(ops) == 170
    assert [op.operation_sequence for op in ops] == list(range(1, 171))
    assert all(op.claim_boundary_state == CLAIM_BOUNDARY and op.lineage_key for op in ops)


def test_object_version_work_package_and_field_mapping():
    rows = read_registration_plan(PLAN)
    ops = build_operation_plan(rows)
    first_objects = [op.native_object for op in ops[:10]]
    assert first_objects[:3] == ["meta_work_package", "meta_object", "meta_object_version"]
    assert "meta_field" in first_objects
    assert all(op.parent_dependency for op in ops)


def test_two_db_temp_dryrun_writes_reports_and_not_real_targets(tmp_path):
    before_data = DATA_DB.stat().st_mtime_ns
    before_meta = META_DB.stat().st_mtime_ns
    out = tmp_path / "reports"
    result = subprocess.run(
        [
            sys.executable,
            str(IMPORTER),
            "--data-db",
            str(DATA_DB),
            "--metadata-db",
            str(META_DB),
            "--output-dir",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "native_operation_count=170" in result.stdout
    assert (out / "native_operation_plan.csv").is_file()
    assert DATA_DB.stat().st_mtime_ns == before_data
    assert META_DB.stat().st_mtime_ns == before_meta


def test_metadata_schema_contains_required_native_tables():
    with sqlite3.connect(f"file:{META_DB.resolve().as_posix()}?mode=ro", uri=True) as conn:
        assert validate_required_schema(conn) == []
