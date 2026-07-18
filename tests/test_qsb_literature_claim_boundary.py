from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.qsb_literature_metadata.native_contract_constants import CLAIM_BOUNDARY, EXECUTION_IMPORT_AUTHORIZED
from scripts.qsb_literature_metadata.native_metadata_mapping import MappingError, build_operation_plan, read_registration_plan


PLAN = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv"
DATA_DB = ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db"
META_DB = ROOT / "runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite"
IMPORTER = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py"


def test_claim_boundary_mismatch_blocks_planning():
    rows = read_registration_plan(PLAN)
    bad = [replace(rows[0], claim_boundary="wrong_boundary"), *rows[1:]]
    try:
        build_operation_plan(bad)
    except MappingError as exc:
        assert "blocked_claim_boundary_mismatch" in str(exc)
    else:
        raise AssertionError("claim-boundary mismatch did not block")


def test_execute_authorization_and_deprecated_single_db_are_blocked():
    assert EXECUTION_IMPORT_AUTHORIZED == "false"
    execute = subprocess.run(
        [
            sys.executable,
            str(IMPORTER),
            "--data-db",
            str(DATA_DB),
            "--metadata-db",
            str(META_DB),
            "--mode",
            "execute",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert execute.returncode == 2
    assert "execution_import_authorized=false" in execute.stdout
    deprecated = subprocess.run(
        [sys.executable, str(IMPORTER), "--db", str(DATA_DB), "--mode", "execute"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert deprecated.returncode == 2
    assert "single_db_mode_deprecated_for_two_db_architecture" in deprecated.stdout
    assert CLAIM_BOUNDARY in {row.claim_boundary for row in read_registration_plan(PLAN)}
