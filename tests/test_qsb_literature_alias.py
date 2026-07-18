from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from scripts.qsb_literature_metadata.native_contract_constants import ALIAS_SCOPES, LANGUAGE_CODES
from scripts.qsb_literature_metadata.native_metadata_mapping import canonical_collision_key, detect_alias_collisions, normalize_alias, read_registration_plan


PLAN = ROOT / "runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv"


def test_alias_normalization_scope_language_and_reverse_resolution_inputs():
    assert normalize_alias("  A\u0308  ") == "\u00c4"
    assert canonical_collision_key(" Title ") == "title"
    assert "field_label" in ALIAS_SCOPES
    assert set(LANGUAGE_CODES) == {"de", "en"}
    rows = read_registration_plan(PLAN)
    assert detect_alias_collisions(rows) == []


def test_vocabulary_reuse_and_addition_inputs_are_source_supported():
    from scripts.qsb_literature_metadata.native_metadata_mapping import vocabulary_entries

    entries = vocabulary_entries(read_registration_plan(PLAN))
    codes = {row["canonical_code"] for row in entries}
    assert "literature_context_only_no_internal_evidence_no_mechanism_claim" in codes
    assert "primary_literature" in codes
    assert "GREEN" in codes
    assert all(row["definition"] for row in entries)
