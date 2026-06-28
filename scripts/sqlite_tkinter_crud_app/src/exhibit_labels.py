"""Museum-style exhibit label model and data resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .qsb_database import QSBMetadataDatabase
from .showcase import exhibit_by_id, localized, resolve_exhibit, resolve_reaction_scheme


FIELD_LABELS = {
    "exhibit": {"de": "Exponat", "en": "Exhibit"},
    "name": {"de": "Name", "en": "Name"},
    "object_type": {"de": "Objekttyp", "en": "Object type"},
    "physical_domain": {"de": "Physikalische Domäne", "en": "Physical domain"},
    "model_system": {"de": "Modell / System", "en": "Model / system"},
    "datamart": {"de": "Datamart", "en": "Datamart"},
    "work_packages": {"de": "Arbeitspakete", "en": "Work packages"},
    "data_state": {"de": "Datenstand", "en": "Data state"},
    "status": {"de": "Status", "en": "Status"},
    "evidence_class": {"de": "Evidenzklasse", "en": "Evidence class"},
    "unit_status": {"de": "Einheitenstatus", "en": "Unit status"},
    "dimension_status": {"de": "Dimensionsstatus", "en": "Dimension status"},
    "provenance": {"de": "Quelle / Herkunft", "en": "Source / provenance"},
    "open_question": {"de": "Offene Frage", "en": "Open question"},
    "qsb_interface_relation": {"de": "Bezug zur QSB-Interface-Schicht", "en": "Relation to the QSB interface layer"},
    "inventory_number": {"de": "Inventarnummer", "en": "Inventory number"},
}


TECHNICAL_LABELS = {
    "technical_provenance": {"de": "Technische Herkunft", "en": "Technical provenance"},
    "canonical_mart_code": {"de": "Canonical Mart-Code", "en": "Canonical mart code"},
    "work_package_code": {"de": "Work-Package-Code", "en": "Work-package code"},
    "source_relation": {"de": "Quellrelation", "en": "Source relation"},
    "source_fields": {"de": "Quellfelder", "en": "Source fields"},
    "snapshot_checksum": {"de": "Snapshot-Checksumme", "en": "Snapshot checksum"},
}


@dataclass(frozen=True)
class LabelField:
    key: str
    label: str
    value: str


@dataclass(frozen=True)
class MuseumLabel:
    exhibit_id: str
    inventory_number: str
    title: str
    subtitle: str
    fields: list[LabelField]
    technical_fields: list[LabelField]


def _first_row_value(rows: list[dict[str, Any]], candidates: list[str]) -> str:
    for row in rows:
        for field in candidates:
            value = row.get(field)
            if value not in (None, ""):
                return str(value)
    return ""


def _manifest_list(manifest: dict[str, Any], key: str) -> str:
    value = manifest.get(key, [])
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item not in (None, ""))
    return str(value) if value not in (None, "") else ""


def _add_field(fields: list[LabelField], key: str, value: str, language: str) -> None:
    if value:
        fields.append(LabelField(key, localized(FIELD_LABELS[key], language), value))


def _add_technical(fields: list[LabelField], key: str, value: str, language: str) -> None:
    if value:
        fields.append(LabelField(key, localized(TECHNICAL_LABELS[key], language), value))


def resolve_museum_label(database: QSBMetadataDatabase, config: dict[str, Any], exhibit_id: str, language: str = "de") -> MuseumLabel:
    exhibit = exhibit_by_id(config, exhibit_id)
    label_config = exhibit.get("museum_label", {})
    resolution = resolve_exhibit(database, config, exhibit_id)
    rows = resolution.rows
    manifest = database.manifest
    omitted = set(label_config.get("omitted_fields", []))

    title = localized(exhibit.get("title", {}), language)
    subtitle = localized(exhibit.get("subtitle", {}), language)
    inventory = label_config.get("inventory_number", "")
    fields: list[LabelField] = []

    _add_field(fields, "inventory_number", inventory, language)
    _add_field(fields, "name", title, language)
    _add_field(fields, "object_type", localized(label_config.get("object_type", {}), language), language)
    _add_field(fields, "physical_domain", localized(label_config.get("physical_domain", {}), language), language)
    _add_field(fields, "model_system", localized(label_config.get("model_system", {}), language), language)

    mart = _first_row_value(rows, ["mart_code", "datamart", "mart"]) or _manifest_list(manifest, "detected_mart_codes")
    work_packages = _first_row_value(rows, ["work_package_code", "work_package", "source_work_package"]) or _manifest_list(
        manifest, "detected_work_package_codes"
    )
    _add_field(fields, "datamart", mart or "QSB-CAUSALITY07", language)
    _add_field(fields, "work_packages", work_packages, language)
    _add_field(fields, "data_state", localized(label_config.get("data_state", {}), language), language)

    status = _first_row_value(rows, label_config.get("preferred_status_fields", []))
    evidence = _first_row_value(rows, label_config.get("preferred_evidence_fields", []))
    unit_status = _first_row_value(rows, label_config.get("preferred_unit_status_fields", ["unit_status"]))
    dimension_status = _first_row_value(rows, label_config.get("preferred_dimension_status_fields", ["dimension_status"]))
    provenance = _first_row_value(rows, label_config.get("preferred_provenance_fields", []))
    open_question = _first_row_value(rows, label_config.get("preferred_open_question_fields", []))

    if exhibit_id == "causality07_reaction_cycle" and not provenance:
        reaction = resolve_reaction_scheme(database, config)
        provenance = reaction.evidence_reference

    _add_field(fields, "status", status, language)
    _add_field(fields, "evidence_class", evidence, language)
    if "unit_status" not in omitted:
        _add_field(fields, "unit_status", unit_status, language)
    if "dimension_status" not in omitted:
        _add_field(fields, "dimension_status", dimension_status, language)
    _add_field(fields, "provenance", provenance or resolution.source, language)
    _add_field(fields, "open_question", open_question, language)
    _add_field(fields, "qsb_interface_relation", localized(label_config.get("qsb_interface_relation", {}), language), language)

    technical: list[LabelField] = []
    _add_technical(technical, "canonical_mart_code", mart or "QSB-CAUSALITY07", language)
    _add_technical(technical, "work_package_code", work_packages, language)
    _add_technical(technical, "source_relation", resolution.source, language)
    _add_technical(technical, "source_fields", ", ".join(resolution.columns), language)
    _add_technical(technical, "snapshot_checksum", str(manifest.get("snapshot_sha256") or manifest.get("source_sha256") or ""), language)

    return MuseumLabel(
        exhibit_id=exhibit_id,
        inventory_number=inventory,
        title=title,
        subtitle=subtitle,
        fields=fields,
        technical_fields=technical,
    )
