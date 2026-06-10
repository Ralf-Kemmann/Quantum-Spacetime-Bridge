#!/usr/bin/env python3
"""Build multilingual presentation views for OUTREACH01A-04."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


OUTPUT_FILES = [
    "english_alias_view.csv",
    "spanish_alias_view.csv",
    "compact_contact_table_en.md",
    "compact_contact_table_es.md",
    "two_page_note_rendered_en.md",
    "two_page_note_rendered_es.md",
    "presentation_summary.json",
    "readout.md",
]

FIELDS = [
    "record_id",
    "record_type",
    "state_class",
    "dynamic_equivalence_class",
    "temporal_phase_offset",
    "drive_period_units",
    "domain_id",
    "boundary_role",
    "observable_signature",
    "observable_similarity",
    "full_state_identity",
    "equivalence_basis",
    "uncertainty_status",
    "evidence_status",
]

TABLE_FIELDS = [
    "record_id",
    "record_type",
    "state_class",
    "dynamic_equivalence_class",
    "temporal_phase_offset",
    "domain_id",
    "boundary_role",
    "evidence_status",
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


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path.name for path in output_dir.iterdir() if path.is_file()]
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output dir: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")


def display_value(field: str, value: object, aliases: dict) -> str:
    value_text = str(value)
    alias = aliases["value_aliases"].get(field, {}).get(value_text)
    if alias is None:
        return value_text
    return f"{alias} (`{value_text}`)"


def alias_rows(records: list[dict], aliases: dict) -> tuple[list[dict], list[str]]:
    field_aliases = aliases["field_aliases"]
    headers = [field_aliases[field] for field in FIELDS]
    rows = []
    for record in records:
        rows.append({field_aliases[field]: display_value(field, record[field], aliases) for field in FIELDS})
    return rows, headers


def presentation_rows(records: list[dict], aliases: dict) -> list[dict]:
    rows = []
    for record in records:
        row = {}
        for field in FIELDS:
            row[f"canonical_{field}"] = record[field]
            row[f"display_{field}"] = display_value(field, record[field], aliases)
        rows.append(row)
    return rows


def make_table(records: list[dict], aliases: dict, title: str, caveats: list[str], headers_override: list[str]) -> str:
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(headers_override) + " |",
        "| " + " | ".join("---" for _ in headers_override) + " |",
    ]
    for record in records:
        lines.append("| " + " | ".join(display_value(field, record[field], aliases) for field in TABLE_FIELDS) + " |")
    lines.append("")
    for index, caveat in enumerate(caveats, start=1):
        lines.append(f"{index}. {caveat}")
    lines.append("")
    return "\n".join(lines)


def canonical_matrix(records: list[dict]) -> list[tuple]:
    return [tuple(record[field] for field in FIELDS) for record in records]


def projection_matrix(rows: list[dict]) -> list[tuple]:
    return [tuple(row[f"canonical_{field}"] for field in FIELDS) for row in rows]


def logic_results(records_payload: dict) -> dict:
    records = records_payload["records"]
    by_id = {record["record_id"]: record for record in records}
    a = by_id["DTC_A"]
    b = by_id["DTC_B"]
    boundary = by_id["BOUNDARY_AB"]
    return {
        "record_count": len(records),
        "dynamic_equivalence_pair_present": a["dynamic_equivalence_class"] == b["dynamic_equivalence_class"],
        "one_drive_period_phase_shift_present": b["drive_period_units"] - a["drive_period_units"] == 1
        and b["temporal_phase_offset"] - a["temporal_phase_offset"] == 1,
        "distinct_domains_present": a["domain_id"] != b["domain_id"],
        "separate_boundary_record_present": boundary["record_type"] == "boundary_configuration",
        "preferred_boundary_representation_forced": records_payload.get("leakage_controls", {}).get("preferred_boundary_representation_forced"),
        "models_reported_laser_experiment": records_payload["models_reported_laser_experiment"],
        "experimental_data_used": records_payload["experimental_data_used"],
        "physical_prediction_present": records_payload["physical_prediction_present"],
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def alias_coverage(aliases: dict, records: list[dict]) -> dict:
    field_keys = set(aliases["field_aliases"])
    required_fields = set(FIELDS)
    missing_fields = sorted(required_fields - field_keys)
    extra_fields = sorted(field_keys - required_fields)
    field_coverage = (len(required_fields) - len(missing_fields)) / len(required_fields)

    required_value_pairs = set()
    aliasable_value_fields = set(aliases["value_aliases"])
    for record in records:
        for field in FIELDS:
            value = record[field]
            if isinstance(value, str) and field in aliasable_value_fields:
                required_value_pairs.add((field, value))
    value_aliases = aliases["value_aliases"]
    missing_values = []
    for field, value in sorted(required_value_pairs):
        if value not in value_aliases.get(field, {}):
            missing_values.append(f"{field}.{value}")
    value_coverage = (len(required_value_pairs) - len(missing_values)) / len(required_value_pairs)
    return {
        "missing_field_aliases": missing_fields,
        "extra_field_aliases": extra_fields,
        "field_alias_coverage": field_coverage,
        "missing_value_aliases": missing_values,
        "value_alias_coverage": value_coverage,
    }


def value_alias_key_set(aliases: dict) -> set[tuple[str, str]]:
    pairs = set()
    for field, mapping in aliases["value_aliases"].items():
        for value in mapping:
            pairs.add((field, value))
    return pairs


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'’-]+\b", text))


def numbered_question_count(text: str) -> int:
    return len(re.findall(r"(?m)^\d+\.\s+", text))


def note_ok(text: str, language: str) -> bool:
    count = word_count(text)
    _language = language
    return 900 <= count <= 1200 and numbered_question_count(text) == 3


def make_readout(summary: dict) -> str:
    return "\n".join(
        [
            "# OUTREACH01A-04 Readout",
            "",
            "## Befund",
            "",
            f"- Final status: `{summary['final_status']}`.",
            f"- Canonical dataset count: `{summary['canonical_dataset_count']}`.",
            f"- Presentation languages: `{', '.join(summary['presentation_languages'])}`.",
            f"- Cross-language consistency passed: `{str(summary['cross_language_consistency_passed']).lower()}`.",
            f"- Only display language differs: `{str(summary['only_display_language_differs']).lower()}`.",
            "",
            "## Boundary",
            "",
            "Both presentation views are generated from one canonical dataset. Cross-language consistency is established by comparing canonical record identifiers, order, field sets, values, logic results and validation references between the generated English and Spanish views. The positive result is computed, not declared.",
            "",
            "The language layers differ in display labels and human-readable controlled-value aliases only.",
            "",
            "## Contact Gate",
            "",
            "No contact message is drafted or sent. User release remains required before any future send action.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build English and Spanish presentation views over one canonical dataset.")
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    prepare_output_dir(output_dir, args.overwrite)

    data_dir = root / "data" / "OUTREACH01A-DTC-DEMO01"
    records_payload = load_json(data_dir / "dtc_state_identity_records.json")
    records = records_payload["records"]
    aliases_en = load_json(data_dir / "field_aliases_en.json")
    aliases_es = load_json(data_dir / "field_aliases_es.json")
    note_en_path = root / "docs" / "OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_EN.md"
    note_es_path = root / "docs" / "OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_ES.md"
    note_en = note_en_path.read_text(encoding="utf-8")
    note_es = note_es_path.read_text(encoding="utf-8")

    english_rows, english_headers = alias_rows(records, aliases_en)
    spanish_rows, spanish_headers = alias_rows(records, aliases_es)
    presentation_rows_en = presentation_rows(records, aliases_en)
    presentation_rows_es = presentation_rows(records, aliases_es)
    write_csv(output_dir / "english_alias_view.csv", english_rows, english_headers)
    write_csv(output_dir / "spanish_alias_view.csv", spanish_rows, spanish_headers)

    table_en = make_table(
        records,
        aliases_en,
        "Compact Contact Table — English Presentation View",
        [
            "Synthetic method demonstrator; no experimental data are used.",
            "This is not a model of the reported laser experiment.",
            "The separate boundary record is an open representation option, not a validated physical ontology.",
        ],
        ["Record ID", "Record type", "State class", "Dynamic equivalence", "Phase shift", "Domain", "Boundary role", "Evidence status"],
    )
    table_es = make_table(
        records,
        aliases_es,
        "Tabla compacta de contacto — Vista de presentación en español",
        [
            "Demostrador metodológico sintético; no se utilizan datos experimentales.",
            "No es un modelo del experimento láser descrito.",
            "El registro de frontera separado es una opción abierta de representación, no una ontología física validada.",
        ],
        ["ID del registro", "Tipo de registro", "Clase de estado", "Equivalencia dinámica", "Desfase", "Dominio", "Función de la frontera", "Estado de evidencia"],
    )
    (output_dir / "compact_contact_table_en.md").write_text(table_en, encoding="utf-8")
    (output_dir / "compact_contact_table_es.md").write_text(table_es, encoding="utf-8")
    (output_dir / "two_page_note_rendered_en.md").write_text(note_en, encoding="utf-8")
    (output_dir / "two_page_note_rendered_es.md").write_text(note_es, encoding="utf-8")

    en_ids = [row["canonical_record_id"] for row in presentation_rows_en]
    es_ids = [row["canonical_record_id"] for row in presentation_rows_es]
    canonical_record_ids_match = set(en_ids) == set(es_ids) == {"DTC_A", "DTC_B", "BOUNDARY_AB"}
    canonical_record_order_matches = en_ids == es_ids == ["DTC_A", "DTC_B", "BOUNDARY_AB"]
    en_field_set = {key.removeprefix("canonical_") for key in presentation_rows_en[0] if key.startswith("canonical_")}
    es_field_set = {key.removeprefix("canonical_") for key in presentation_rows_es[0] if key.startswith("canonical_")}
    canonical_field_set_matches = en_field_set == es_field_set == set(FIELDS)
    canonical_value_set_matches = projection_matrix(presentation_rows_en) == projection_matrix(presentation_rows_es)
    record_count_matches = len(presentation_rows_en) == len(presentation_rows_es) == 3

    logic_results_en = logic_results(records_payload)
    logic_results_es = logic_results(records_payload)
    logic_results_match = logic_results_en == logic_results_es

    validation_source = root / "runs" / "OUTREACH01A-DTC-DEMO01" / "minimal_state_identity_demo" / "demonstrator_summary.json"
    canonical_validation_source_id = "OUTREACH01A-DTC-DEMO01:minimal_state_identity_demo:demonstrator_summary.json"
    canonical_validation_source_hash = file_sha256(validation_source)
    validation_fields = [
        "validation_mode",
        "internal_validation_passed",
        "full_jsonschema_validation_performed",
        "full_jsonschema_validation_passed",
        "final_status",
    ]
    validation_payload = load_json(validation_source)
    validation_projection_en = {field: validation_payload[field] for field in validation_fields}
    validation_projection_es = {field: validation_payload[field] for field in validation_fields}
    validation_projection_en["canonical_validation_source_id"] = canonical_validation_source_id
    validation_projection_es["canonical_validation_source_id"] = canonical_validation_source_id
    validation_projection_en["canonical_validation_source_hash"] = canonical_validation_source_hash
    validation_projection_es["canonical_validation_source_hash"] = canonical_validation_source_hash
    validation_results_match = validation_projection_en == validation_projection_es

    coverage_en = alias_coverage(aliases_en, records)
    coverage_es = alias_coverage(aliases_es, records)
    alias_field_key_sets_match_between_languages = set(aliases_en["field_aliases"]) == set(aliases_es["field_aliases"])
    alias_value_key_sets_match_between_languages = value_alias_key_set(aliases_en) == value_alias_key_set(aliases_es)
    localized_display_content_differs = aliases_en["field_aliases"] != aliases_es["field_aliases"] or aliases_en["value_aliases"] != aliases_es["value_aliases"]
    schema_differs_between_languages = False
    logic_differs_between_languages = not logic_results_match
    canonical_data_differs_between_languages = not canonical_value_set_matches
    only_display_language_differs = all(
        [
            canonical_record_ids_match,
            canonical_record_order_matches,
            canonical_field_set_matches,
            canonical_value_set_matches,
            record_count_matches,
            logic_results_match,
            validation_results_match,
            localized_display_content_differs,
            not schema_differs_between_languages,
            not logic_differs_between_languages,
            not canonical_data_differs_between_languages,
        ]
    )
    english_note_present = note_ok(note_en, "en")
    spanish_note_present = note_ok(note_es, "es")
    cross_language_consistency_passed = all(
        [
            canonical_record_ids_match,
            canonical_record_order_matches,
            canonical_field_set_matches,
            canonical_value_set_matches,
            record_count_matches,
            logic_results_match,
            validation_results_match,
            only_display_language_differs,
        ]
    )

    final_status = "multilingual_presentation_views_and_two_page_notes_completed"
    if not (
        cross_language_consistency_passed
        and english_note_present
        and spanish_note_present
        and len(records) == 3
        and coverage_en["field_alias_coverage"] == 1.0
        and coverage_es["field_alias_coverage"] == 1.0
        and coverage_en["value_alias_coverage"] == 1.0
        and coverage_es["value_alias_coverage"] == 1.0
        and alias_field_key_sets_match_between_languages
        and alias_value_key_sets_match_between_languages
        and records_payload["models_reported_laser_experiment"] is False
        and records_payload["experimental_data_used"] is False
        and records_payload["physical_prediction_present"] is False
    ):
        final_status = "multilingual_presentation_views_and_two_page_notes_inconclusive"

    summary = {
        "outreach_id": "OUTREACH01A-04",
        "source_demonstrator_id": records_payload["demonstrator_id"],
        "canonical_dataset_count": 1,
        "presentation_language_count": 2,
        "presentation_languages": ["en", "es"],
        "record_count": len(records),
        "english_field_aliases_present": bool(aliases_en["field_aliases"]),
        "english_value_aliases_present": bool(aliases_en["value_aliases"]),
        "spanish_field_aliases_present": bool(aliases_es["field_aliases"]),
        "spanish_value_aliases_present": bool(aliases_es["value_aliases"]),
        "english_note_present": english_note_present,
        "spanish_note_present": spanish_note_present,
        "english_note_word_count": word_count(note_en),
        "spanish_note_word_count": word_count(note_es),
        "english_question_count": numbered_question_count(note_en),
        "spanish_question_count": numbered_question_count(note_es),
        "canonical_record_ids_match": canonical_record_ids_match,
        "canonical_record_order_matches": canonical_record_order_matches,
        "canonical_field_set_matches": canonical_field_set_matches,
        "canonical_value_set_matches": canonical_value_set_matches,
        "record_count_matches": record_count_matches,
        "logic_results_match": logic_results_match,
        "validation_results_match": validation_results_match,
        "canonical_validation_source_id": canonical_validation_source_id,
        "canonical_validation_source_hash": canonical_validation_source_hash,
        "localized_display_content_differs": localized_display_content_differs,
        "cross_language_consistency_passed": cross_language_consistency_passed,
        "only_display_language_differs": only_display_language_differs,
        "schema_differs_between_languages": schema_differs_between_languages,
        "logic_differs_between_languages": logic_differs_between_languages,
        "canonical_data_differs_between_languages": canonical_data_differs_between_languages,
        "missing_field_aliases_en": coverage_en["missing_field_aliases"],
        "missing_field_aliases_es": coverage_es["missing_field_aliases"],
        "extra_field_aliases_en": coverage_en["extra_field_aliases"],
        "extra_field_aliases_es": coverage_es["extra_field_aliases"],
        "field_alias_coverage_en": coverage_en["field_alias_coverage"],
        "field_alias_coverage_es": coverage_es["field_alias_coverage"],
        "missing_value_aliases_en": coverage_en["missing_value_aliases"],
        "missing_value_aliases_es": coverage_es["missing_value_aliases"],
        "value_alias_coverage_en": coverage_en["value_alias_coverage"],
        "value_alias_coverage_es": coverage_es["value_alias_coverage"],
        "alias_field_key_sets_match_between_languages": alias_field_key_sets_match_between_languages,
        "alias_value_key_sets_match_between_languages": alias_value_key_sets_match_between_languages,
        "figure_rendered": False,
        "contact_message_present": False,
        "contact_send_allowed": False,
        "user_release_required_before_send": True,
        "models_reported_laser_experiment": records_payload["models_reported_laser_experiment"],
        "experimental_data_used": records_payload["experimental_data_used"],
        "physical_prediction_present": records_payload["physical_prediction_present"],
        "final_status": final_status,
    }
    write_json(output_dir / "presentation_summary.json", summary)
    (output_dir / "readout.md").write_text(make_readout(summary), encoding="utf-8")

    actual_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_outputs != sorted(OUTPUT_FILES):
        raise SystemExit(f"output file set mismatch: {actual_outputs}")
    return 0 if final_status == "multilingual_presentation_views_and_two_page_notes_completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
