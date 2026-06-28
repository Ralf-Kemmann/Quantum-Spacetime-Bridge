"""Presentation labels for the QSB browser."""

from __future__ import annotations


FIELD_LABELS = {
    "quantity_kind": {"de": "Größenart", "en": "Quantity kind"},
    "value_original": {"de": "Originalwert", "en": "Original value"},
    "unit_original": {"de": "Originaleinheit", "en": "Original unit"},
    "value_calculation": {"de": "Berechnungswert", "en": "Calculation value"},
    "unit_calculation": {"de": "Berechnungseinheit", "en": "Calculation unit"},
    "value_display": {"de": "Anzeigewert", "en": "Display value"},
    "unit_display": {"de": "Anzeigeeinheit", "en": "Display unit"},
    "dimension_vector": {"de": "Dimensionsvektor", "en": "Dimension vector"},
    "conversion_rule_id": {"de": "Umrechnungsregel-ID", "en": "Conversion rule ID"},
    "unit_status": {"de": "Einheitenstatus", "en": "Unit status"},
    "dimension_status": {"de": "Dimensionsstatus", "en": "Dimension status"},
    "validation_layer": {"de": "Validierungsebene", "en": "Validation layer"},
    "validation_status": {"de": "Validierungsstatus", "en": "Validation status"},
    "evidence_class": {"de": "Evidenzklasse", "en": "Evidence class"},
    "claim_text": {"de": "Wissenschaftliche Aussage", "en": "Scientific claim"},
    "relation_type": {"de": "Beziehungsart", "en": "Relation type"},
    "review_priority": {"de": "Prüfpriorität", "en": "Review priority"},
    "human_review_state": {"de": "Menschlicher Prüfstatus", "en": "Human review state"},
    "source_object": {"de": "Quellobjekt", "en": "Source object"},
    "target_object": {"de": "Zielobjekt", "en": "Target object"},
    "source_field": {"de": "Quellfeld", "en": "Source field"},
    "target_field": {"de": "Zielfeld", "en": "Target field"},
    "transformation_rule": {"de": "Transformationsregel", "en": "Transformation rule"},
    "mart_code": {"de": "Datamart", "en": "Datamart"},
    "work_package_code": {"de": "Arbeitspaket", "en": "Work package"},
    "matched_field": {"de": "Trefferfeld", "en": "Matched field"},
    "matched_value": {"de": "Trefferwert", "en": "Matched value"},
    "field_name": {"de": "Feldname", "en": "Field name"},
    "label_or_alias": {"de": "Label oder Alias", "en": "Label or alias"},
    "unit": {"de": "Einheit", "en": "Unit"},
    "dimension": {"de": "Dimension", "en": "Dimension"},
    "related_view": {"de": "Zugeordnete View", "en": "Related view"},
}


VIEW_LABELS = {
    "v_de_physikalische_groessen": {"de": "Physikalische Größen", "en": "Physical quantities"},
    "v_de_lineage": {"de": "Herkunft und Lineage", "en": "Provenance and lineage"},
    "v_de_validierungsergebnisse": {"de": "Validierungsergebnisse", "en": "Validation results"},
    "v_de_ergebnis_claim_beziehungen": {"de": "Ergebnisse und Aussagen", "en": "Results and claims"},
    "v_de_offene_pruefpunkte": {"de": "Offene Prüfpunkte", "en": "Open review items"},
}

UI_TEXT = {
    "overview": {"de": "Übersicht", "en": "Overview"},
    "exhibition": {"de": "Ausstellung", "en": "Exhibition"},
    "expert_inspection": {"de": "Fachprüfung", "en": "Expert inspection"},
    "research_views": {"de": "Forschungsansichten", "en": "Research views"},
    "metadata_search": {"de": "Metadatensuche", "en": "Metadata search"},
    "lineage": {"de": "Herkunft / Lineage", "en": "Provenance / lineage"},
    "validations": {"de": "Validierungen", "en": "Validations"},
    "claims_results": {"de": "Claims und Ergebnisse", "en": "Claims and results"},
    "open_items": {"de": "Offene Prüfpunkte", "en": "Open review items"},
    "database_info": {"de": "Datenbankinfo", "en": "Database info"},
    "charts": {"de": "Diagramme", "en": "Charts"},
    "language": {"de": "Sprache", "en": "Language"},
    "generate_chart": {"de": "Diagramm erzeugen", "en": "Generate chart"},
    "export_chart": {"de": "Diagramm exportieren", "en": "Export chart"},
    "source": {"de": "Quelle", "en": "Source"},
    "chart_note": {
        "de": "Diagramm aus dem gewählten Snapshot und den angezeigten Filtern. Keine eigenständige wissenschaftliche Aussage.",
        "en": "Chart generated from the selected snapshot and active filters. It is not an independent scientific claim.",
    },
}

GERMAN_LABELS = {key: value["de"] for key, value in FIELD_LABELS.items()}

def readable_identifier(identifier: str) -> str:
    return identifier.replace("_", " ").strip().capitalize()

def label_for_identifier(identifier: str) -> str:
    if identifier in VIEW_LABELS:
        return VIEW_LABELS[identifier]["de"]
    if identifier in GERMAN_LABELS:
        return GERMAN_LABELS[identifier]
    return readable_identifier(identifier)
