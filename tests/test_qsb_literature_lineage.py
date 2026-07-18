from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.qsb_literature_metadata.native_contract_constants import CLAIM_BOUNDARY
from scripts.qsb_literature_metadata.native_metadata_mapping import build_operation_plan, lineage_validation, read_registration_plan


PLAN = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv"


def test_lineage_reconstructs_every_operation_to_plan_row():
    operations = build_operation_plan(read_registration_plan(PLAN))
    lineage_rows = lineage_validation(operations)
    assert len(lineage_rows) == 170
    assert all(row["status"] == "pass" for row in lineage_rows)
    assert {row["registration_plan_row_id"] for row in lineage_rows} == {f"RP{i:02d}" for i in range(1, 18)}
    assert all(row["claim_boundary"] == CLAIM_BOUNDARY for row in lineage_rows)


def test_negative_neutral_unmapped_future_cube_and_planck_states_are_preserved():
    from scripts.qsb_literature_metadata.native_contract_constants import CUBE_COMPATIBILITY_STATES, OBSERVATION_STATES, PLANCK_SPACE_COMPATIBILITY_STATES

    for state in ["negative", "neutral", "rejected", "ambiguous", "unmapped"]:
        assert state in OBSERVATION_STATES
    assert "future_cube_role" in CUBE_COMPATIBILITY_STATES
    assert "coordinate_definition_id" in PLANCK_SPACE_COMPATIBILITY_STATES
