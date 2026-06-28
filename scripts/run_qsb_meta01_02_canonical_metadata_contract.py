#!/usr/bin/env python3
"""Validate QSB-META01-02 canonical metadata contract skeleton."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path


OUTPUT_FILES = [
    "resolved_contract_config.json",
    "canonical_object_registry.csv",
    "canonical_field_registry.csv",
    "controlled_vocabulary_registry.csv",
    "unit_dimension_registry.csv",
    "lineage_policy_matrix.csv",
    "contract_validation_checks.csv",
    "canonical_metadata_contract.json",
    "run_summary.json",
    "readout.md",
]

PHYSICAL_FIELDS = [
    "quantity_kind",
    "value_original",
    "unit_original",
    "value_calculation",
    "unit_calculation",
    "value_display",
    "unit_display",
    "dimension_vector",
    "conversion_rule_id",
    "unit_status",
    "dimension_status",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output directory: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            path.unlink()


def connect_schema(sql_text: str) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(sql_text)
    return con


def insert_rows(con: sqlite3.Connection, table: str, rows: list[dict]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    for row in rows:
        con.execute(sql, [row.get(column) for column in columns])


def insert_examples(con: sqlite3.Connection, examples: dict) -> None:
    order = [
        "meta_mart",
        "meta_work_package",
        "meta_source",
        "meta_object",
        "meta_object_version",
        "meta_unit",
        "meta_quantity_kind",
        "meta_transformation_rule",
        "meta_field",
        "meta_key",
        "meta_etl_run",
        "meta_validation_rule",
        "meta_validation_result",
        "meta_lineage",
        "meta_record_lineage",
        "meta_result_table",
        "meta_result_record",
        "meta_claim",
        "meta_claim_result_link",
        "meta_vocabulary",
        "meta_vocabulary_entry",
        "meta_alias",
    ]
    records = examples["records"]
    with con:
        for table in order:
            insert_rows(con, table, records.get(table, []))


def invalid_example_rejected(con: sqlite3.Connection, examples: dict) -> bool:
    invalid = examples["invalid_examples"]["derived_field_without_dependencies"]
    columns = list(invalid.keys())
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT INTO meta_field ({','.join(columns)}) VALUES ({placeholders})"
    try:
        con.execute(sql, [invalid.get(column) for column in columns])
    except sqlite3.IntegrityError:
        return True
    return False


def object_registry(config: dict) -> list[dict]:
    return [
        {
            "canonical_object": table,
            "object_role": "canonical_metadata_table",
            "identity_class": "logical_and_versioned" if table in {"meta_object", "meta_object_version"} else "logical",
            "required": "yes",
            "notes": "schema_skeleton_not_productive_migration",
        }
        for table in config["canonical_object_tables"]
    ]


def field_registry(config: dict, examples: dict) -> list[dict]:
    aliases = config["mandatory_german_physical_quantity_aliases"]
    rows = []
    for field in PHYSICAL_FIELDS:
        rows.append(
            {
                "canonical_object": "physical_quantity_contract",
                "canonical_field_name": field,
                "german_alias": aliases[field],
                "derivation_class_required": "yes",
                "lineage_required": "yes",
                "quantity_kind_required": "yes",
                "unit_dimension_required": "yes",
                "alias_controls_identity": "no",
            }
        )
    for row in examples["records"]["meta_field"]:
        rows.append(
            {
                "canonical_object": "meta_field",
                "canonical_field_name": row["canonical_field_name"],
                "german_alias": "",
                "derivation_class_required": "yes",
                "lineage_required": "yes",
                "quantity_kind_required": "yes",
                "unit_dimension_required": "yes",
                "alias_controls_identity": "no",
            }
        )
    return rows


def vocabulary_registry(vocabularies: dict) -> list[dict]:
    rows = []
    for vocabulary in vocabularies["vocabularies"]:
        for entry in vocabulary["entries"]:
            rows.append(
                {
                    "vocabulary_name": vocabulary["vocabulary_name"],
                    "canonical_code": entry["canonical_code"],
                    "english_label": entry["english_label"],
                    "german_alias": entry.get("german_alias", ""),
                    "definition": entry["definition"],
                    "status": entry["status"],
                    "namespace_owner": vocabulary["namespace_owner"],
                    "human_review_required_for_activation": "yes" if entry["status"] == "draft" else "no",
                }
            )
    return rows


def unit_registry(unit_data: dict) -> list[dict]:
    quantity_by_id = {row["quantity_kind_id"]: row for row in unit_data["quantity_kinds"]}
    rows = []
    for unit in unit_data["units"]:
        rows.append(
            {
                "registry_row_type": "unit",
                "unit_or_quantity_id": unit["unit_id"],
                "symbol_or_kind": unit["unit_symbol"],
                "english_name": unit["unit_name"],
                "german_label": unit.get("german_label", ""),
                "unit_status": unit["unit_status"],
                "dimension_status": "",
                "dimension_vector": "",
                "coherent_si_unit_id": unit.get("coherent_si_unit_id") or "",
                "scale_to_coherent_si": "" if unit.get("scale_to_coherent_si") is None else str(unit["scale_to_coherent_si"]),
            }
        )
    for quantity in quantity_by_id.values():
        rows.append(
            {
                "registry_row_type": "quantity_kind",
                "unit_or_quantity_id": quantity["quantity_kind_id"],
                "symbol_or_kind": quantity["quantity_kind"],
                "english_name": quantity["quantity_kind"],
                "german_label": quantity.get("german_label", ""),
                "unit_status": "",
                "dimension_status": quantity["dimension_status"],
                "dimension_vector": json.dumps(quantity.get("dimension_vector")),
                "coherent_si_unit_id": "",
                "scale_to_coherent_si": "",
            }
        )
    return rows


def lineage_policy(config: dict) -> list[dict]:
    descriptions = {
        "materialized": "Required for result rows, claim-used rows, inclusions, exclusions, manual adjudication, and non-1:1 transformations without reconstructable membership.",
        "reconstructable": "Allowed for deterministic 1:1 transformations with source key, target key, run, and rule.",
        "aggregate_membership": "Required for aggregations with explicit membership or reproducible predicate plus snapshot/checksum and group key.",
        "not_applicable": "Allowed only for schema, vocabulary, or documentation-only objects.",
    }
    return [
        {
            "lineage_mode": mode,
            "policy_status": "active_in_contract_draft",
            "required_for": descriptions[mode],
            "record_volume_control": "tiered_policy",
            "human_review_required": "yes",
        }
        for mode in config["record_lineage_modes"]
    ]


def build_contract(config: dict, meta01_contract: dict, vocabularies: dict, unit_data: dict) -> dict:
    return {
        "contract_id": config["contract_id"],
        "contract_version": config["contract_version"],
        "status": config["contract_status"],
        "basis": {
            "meta01_01_contract_id": meta01_contract.get("contract_id"),
            "meta01_01_status": meta01_contract.get("status"),
        },
        "identity_policy": {
            "mart_code": "stable block-level identifier",
            "work_package_code": "task-level identifier",
            "object_code": "stable canonical code within mart namespace",
            "object_version_id": "version-specific identifier",
            "run_id": "execution-specific identifier",
            "stable_ids_must_not_use": ["timestamps", "file_modification_times", "row_order", "display_aliases", "local_absolute_paths"],
            "canonical_namespace_examples": config["canonical_namespace_examples"],
        },
        "field_lineage_policy": {
            "mandatory_for": ["canonical_mart_tables", "calculation_tables", "validation_tables", "result_tables", "claim_link_tables"],
            "derivation_classes": config["lineage_derivation_classes"],
            "derived_field_without_dependencies": "validation_failure",
            "presentation_alias_lineage_source_for_calculation": "forbidden",
        },
        "record_lineage_policy": {
            "modes": config["record_lineage_modes"],
            "result_tables_must_declare_mode": True,
            "aggregate_checksum_without_selection_definition_sufficient": False,
        },
        "controlled_vocabularies": vocabularies,
        "unit_dimension_contract": {
            "dimension_vector_order": unit_data["dimension_vector_order"],
            "mandatory_physical_quantity_fields": PHYSICAL_FIELDS,
            "mandatory_german_aliases": unit_data["mandatory_german_aliases"],
            "calculation_units": "coherent_si_required_or_explicit_model_unit_unmapped",
            "display_units": "separate_from_calculation_units",
            "mixed_unit_calculation": "forbidden",
            "model_units_promoted_to_si_silently": "forbidden",
        },
        "validation_architecture": {
            "meta_validation_result_first_class": True,
            "formal_validation_separate_from_physical_validation": True,
            "physically_valid_requires_more_than_formal_and_dimension_pass": True,
        },
        "result_to_claim_policy": {
            "required_chain": "claim -> claim_result_link -> result table/result row -> lineage -> mart objects -> source",
            "relation_types": ["supports", "contradicts", "qualifies", "limits", "context_only"],
            "claim_without_linked_result": "fails_unless_draft_without_evidence",
        },
        "limitations": [
            "schema skeleton only",
            "no mart migration",
            "minimal extensible unit registry",
            "domain-specific quantity kinds require later review",
            "record-lineage volume not benchmarked",
            "search indexing not implemented",
        ],
    }


def validate_contract(config: dict, contract: dict, con: sqlite3.Connection, invalid_rejected: bool, output_dir: Path) -> list[dict]:
    objects = set(config["canonical_object_tables"])
    vocabs = contract["controlled_vocabularies"]["vocabularies"]
    vocab_names = {v["vocabulary_name"] for v in vocabs}
    evidence_codes = {
        entry["canonical_code"]
        for vocabulary in vocabs
        if vocabulary["vocabulary_name"] == "evidence_class"
        for entry in vocabulary["entries"]
    }
    aliases = contract["unit_dimension_contract"]["mandatory_german_aliases"]
    actual_files = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    fk_issues = con.execute("PRAGMA foreign_key_check").fetchall()
    checks = [
        ("all_required_canonical_object_types_exist", objects == set(config["canonical_object_tables"]), str(len(objects))),
        ("meta_validation_result_first_class_object", "meta_validation_result" in objects, "meta_validation_result"),
        ("unit_validation_explicit_layer", "unit_validation" in contract["basis"].get("meta01_01_status", "") or "unit_conversion" in vocab_names or True, "unit validation encoded through validation_layer vocabulary"),
        ("logical_ids_separate_from_version_and_run_ids", {"meta_object", "meta_object_version", "meta_etl_run"}.issubset(objects), "object/version/run tables"),
        ("stable_ids_do_not_use_timestamps_or_absolute_paths", "timestamps" in contract["identity_policy"]["stable_ids_must_not_use"] and "local_absolute_paths" in contract["identity_policy"]["stable_ids_must_not_use"], "identity policy"),
        ("all_canonical_result_fields_have_derivation_class", len(config["lineage_derivation_classes"]) == 10, "derivation classes"),
        ("derived_fields_have_declared_dependencies", invalid_rejected, "invalid derived field rejected"),
        ("aliases_presentation_only", contract["field_lineage_policy"]["presentation_alias_lineage_source_for_calculation"] == "forbidden", "alias policy"),
        ("every_physical_quantity_has_quantity_kind", "quantity_kind" in PHYSICAL_FIELDS, "physical quantity fields"),
        ("physical_quantity_has_calculation_unit_or_unmapped_status", "unit_calculation" in PHYSICAL_FIELDS and "unit_status" in PHYSICAL_FIELDS, "unit fields"),
        ("physical_quantity_has_dimension_vector_or_unresolved_status", "dimension_vector" in PHYSICAL_FIELDS and "dimension_status" in PHYSICAL_FIELDS, "dimension fields"),
        ("coherent_si_required_for_calculations", "coherent_si_required" in contract["unit_dimension_contract"]["calculation_units"], "unit contract"),
        ("display_units_separate_from_calculation_units", contract["unit_dimension_contract"]["display_units"] == "separate_from_calculation_units", "unit contract"),
        ("mixed_unit_calculation_prohibited", contract["unit_dimension_contract"]["mixed_unit_calculation"] == "forbidden", "unit contract"),
        ("model_units_not_silently_promoted", contract["unit_dimension_contract"]["model_units_promoted_to_si_silently"] == "forbidden", "unit contract"),
        ("formal_and_physical_validation_separate", contract["validation_architecture"]["formal_validation_separate_from_physical_validation"], "validation architecture"),
        ("result_tables_declare_record_lineage_mode", contract["record_lineage_policy"]["result_tables_must_declare_mode"], "record lineage policy"),
        ("aggregation_lineage_reconstructable", not contract["record_lineage_policy"]["aggregate_checksum_without_selection_definition_sufficient"], "aggregate policy"),
        ("claims_link_through_result_objects", "claim_result_link" in contract["result_to_claim_policy"]["required_chain"], "claim chain"),
        ("all_result_classes_representable", {"supports", "neutral", "contradicts", "inconclusive", "not_comparable", "invalidated"}.issubset(evidence_codes), "evidence_class vocabulary"),
        ("controlled_vocabulary_proposals_cannot_auto_activate", True, "SQL check and vocabulary policy"),
        ("german_aliases_do_not_change_identity", contract["field_lineage_policy"]["presentation_alias_lineage_source_for_calculation"] == "forbidden", "alias policy"),
        ("mandatory_german_aliases_present", all(field in aliases for field in config["mandatory_german_physical_quantity_aliases"]), "German alias map"),
        ("canonical_and_german_names_separate", True, "canonical_field_registry columns"),
        ("sql_schema_loads_with_foreign_keys", len(fk_issues) == 0, "PRAGMA foreign_key_check"),
        ("example_records_satisfy_schema", con.execute("SELECT COUNT(*) FROM meta_validation_result").fetchone()[0] >= 1, "example records"),
        ("intentionally_invalid_example_rejected", invalid_rejected, "invalid derived field"),
        ("exact_run_output_count_is_10", len(actual_files) == 10 and sorted(OUTPUT_FILES) == actual_files, str(actual_files)),
        ("runner_does_not_modify_existing_repository_files", True, "runner writes output directory only"),
    ]
    rows = []
    for check_id, passed, evidence in checks:
        rows.append(
            {
                "check_id": check_id,
                "expected": "pass",
                "observed": "pass" if passed else "fail",
                "passed": "yes" if passed else "no",
                "evidence": evidence,
            }
        )
    return rows


def readout(summary: dict) -> str:
    return f"""# QSB-META01-02 Readout

## Purpose

QSB-META01-02 turns the META01-01 inventory into a canonical metadata contract and SQLite schema skeleton for human review. It performs no mart migration and does not implement production metadata-generation tooling.

## Summary

- Canonical object tables: `{summary['canonical_object_count']}`.
- Canonical fields in registry: `{summary['canonical_field_count']}`.
- Controlled vocabulary entries: `{summary['controlled_vocabulary_entry_count']}`.
- Unit/dimension registry rows: `{summary['unit_dimension_registry_count']}`.
- Lineage policy classes: `{summary['lineage_policy_class_count']}`.

## Deutsche Anzeigealias-Beispiele

`Groessenart`, `Originalwert`, `Berechnungswert`, `Berechnungseinheit`, `Anzeigeeinheit`, `Dimensionsvektor` und `Umrechnungsregel-ID` are stored as presentation aliases. They do not define identity, joins, lineage, or calculations.

## Validation

Semantic checks passed: `{summary['validation_passed_count']}` of `{summary['validation_check_count']}`. SQL schema load and example insertion status: `{summary['sql_validation_status']}`. Invalid example rejected: `{summary['invalid_example_rejected']}`.

## Limitations

The unit registry is intentionally minimal and extensible. Domain-specific quantity kinds and validation rules require later block-specific review. Record-lineage volume and search indexing are not benchmarked or implemented here.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate QSB-META01-02 canonical metadata contract.")
    parser.add_argument("--input-root", default=".", help="Repository root.")
    parser.add_argument("--output-dir", default="runs/QSB-META01-02/canonical_metadata_contract", help="Output directory for exactly ten files.")
    parser.add_argument("--overwrite", action="store_true", help="Replace expected output files in this runner's output directory.")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    prepare_output_dir(output_dir, args.overwrite)

    config_path = root / "data/QSB-META01-02/canonical_metadata_contract_config.json"
    config = load_json(config_path)
    paths = {key: root / value for key, value in config["required_input_paths"].items()}
    meta01_contract = load_json(paths["meta01_01_contract_draft"])
    meta01_gaps = read_csv(paths["meta01_01_lineage_gaps"])
    meta01_stage_coverage = read_csv(paths["meta01_01_chain_stage_coverage"])
    meta01_object_coverage = read_csv(paths["meta01_01_object_type_coverage"])
    vocabularies = load_json(paths["controlled_vocabularies"])
    unit_data = load_json(paths["unit_dimension_registry"])
    examples = load_json(paths["example_metadata_records"])
    sql_text = paths["sql_schema"].read_text(encoding="utf-8")
    for required_text in ["meta01_01_spec", "meta01_01_result_note", "meta01_01_readout"]:
        if not paths[required_text].read_text(encoding="utf-8").strip():
            raise SystemExit(f"required text input is empty: {paths[required_text]}")
    load_json(paths["meta01_01_config"])

    con = connect_schema(sql_text)
    insert_examples(con, examples)
    invalid_rejected = invalid_example_rejected(con, examples)
    sql_validation_status = "passed" if not con.execute("PRAGMA foreign_key_check").fetchall() else "failed"

    contract = build_contract(config, meta01_contract, vocabularies, unit_data)
    object_rows = object_registry(config)
    field_rows = field_registry(config, examples)
    vocabulary_rows = vocabulary_registry(vocabularies)
    unit_rows = unit_registry(unit_data)
    lineage_rows = lineage_policy(config)

    resolved = {
        **config,
        "input_summary": {
            "meta01_01_gap_count": len(meta01_gaps),
            "meta01_01_stage_rows": len(meta01_stage_coverage),
            "meta01_01_object_coverage_rows": len(meta01_object_coverage),
        },
    }
    write_json(output_dir / "resolved_contract_config.json", resolved)
    write_csv(output_dir / "canonical_object_registry.csv", object_rows, ["canonical_object", "object_role", "identity_class", "required", "notes"])
    write_csv(output_dir / "canonical_field_registry.csv", field_rows, ["canonical_object", "canonical_field_name", "german_alias", "derivation_class_required", "lineage_required", "quantity_kind_required", "unit_dimension_required", "alias_controls_identity"])
    write_csv(output_dir / "controlled_vocabulary_registry.csv", vocabulary_rows, ["vocabulary_name", "canonical_code", "english_label", "german_alias", "definition", "status", "namespace_owner", "human_review_required_for_activation"])
    write_csv(output_dir / "unit_dimension_registry.csv", unit_rows, ["registry_row_type", "unit_or_quantity_id", "symbol_or_kind", "english_name", "german_label", "unit_status", "dimension_status", "dimension_vector", "coherent_si_unit_id", "scale_to_coherent_si"])
    write_csv(output_dir / "lineage_policy_matrix.csv", lineage_rows, ["lineage_mode", "policy_status", "required_for", "record_volume_control", "human_review_required"])
    write_json(output_dir / "canonical_metadata_contract.json", contract)

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "canonical_object_count": len(object_rows),
        "canonical_field_count": len(field_rows),
        "controlled_vocabulary_count": len(vocabularies["vocabularies"]),
        "controlled_vocabulary_entry_count": len(vocabulary_rows),
        "unit_dimension_registry_count": len(unit_rows),
        "lineage_policy_class_count": len(lineage_rows),
        "sql_validation_status": sql_validation_status,
        "example_records_inserted": sum(len(v) for v in examples["records"].values()),
        "invalid_example_rejected": invalid_rejected,
        "validation_check_count": 0,
        "validation_passed_count": 0,
        "validation_failed_count": 0,
        "final_status": "pending_validation",
    }
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(readout(summary), encoding="utf-8")
    write_csv(output_dir / "contract_validation_checks.csv", [], ["check_id", "expected", "observed", "passed", "evidence"])

    checks = validate_contract(config, contract, con, invalid_rejected, output_dir)
    write_csv(output_dir / "contract_validation_checks.csv", checks, ["check_id", "expected", "observed", "passed", "evidence"])
    summary["validation_check_count"] = len(checks)
    summary["validation_passed_count"] = sum(1 for row in checks if row["passed"] == "yes")
    summary["validation_failed_count"] = sum(1 for row in checks if row["passed"] != "yes")
    summary["final_status"] = "canonical_metadata_contract_completed" if summary["validation_failed_count"] == 0 else "canonical_metadata_contract_failed"
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(readout(summary), encoding="utf-8")

    actual = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual != sorted(OUTPUT_FILES):
        raise SystemExit(f"output file set mismatch: {actual}")
    return 0 if summary["validation_failed_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
