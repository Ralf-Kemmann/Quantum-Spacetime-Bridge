"""German field-label resolution for presentation-only GUI aliases."""

from __future__ import annotations

from dataclasses import dataclass, field

from .qsb_database import QSBMetadataDatabase


GERMAN_FIELD_FALLBACKS = {
    "object_code": "Objektcode",
    "mart_code": "Mart-Code",
    "mart_name": "Mart-Name",
    "work_package_code": "Arbeitspaket-Code",
    "work_package_name": "Arbeitspaket-Name",
    "work_package_status": "Arbeitspaket-Status",
    "table_role": "Tabellenrolle",
    "source_result_key": "Ergebnis-Schlüssel",
    "result_class": "Ergebnisklasse",
    "comparability_status": "Vergleichbarkeitsstatus",
    "formal_validation_status": "Formaler Validierungsstatus",
    "physical_validation_status": "Physikalischer Validierungsstatus",
    "record_lineage_mode": "Datensatz-Lineage-Modus",
    "object_title": "Objekttitel",
    "repository_path": "Repository-Pfad",
    "object_name": "Objektname",
    "object_type": "Objekttyp",
    "canonical_field_name": "Kanonischer Feldname",
    "alias_text": "Deutsche Bezeichnung",
    "alias_language": "Sprache",
    "language_code": "Sprache",
    "source_code": "Quellcode",
    "source_name": "Quellenname",
    "source_type": "Quellentyp",
    "table_name": "Tabellenname",
    "view_name": "Viewname",
    "column_name": "Spaltenname",
    "field_name": "Feldname",
    "field_description": "Feldbeschreibung",
    "description": "Beschreibung",
    "quantity_kind": "Größenart",
    "unit_symbol": "Einheit",
    "unit_name": "Einheitenname",
    "dimension_vector": "Dimensionsvektor",
    "conversion_rule_id": "Umrechnungsregel",
    "transformation_rule_id": "Transformationsregel",
    "lineage_id": "Lineage-ID",
    "provenance": "Herkunft",
    "validation_layer": "Validierungsebene",
    "validation_status": "Validierungsstatus",
    "validation_message": "Validierungshinweis",
    "message": "Hinweis",
    "evidence_class": "Evidenzklasse",
    "evidence_status": "Evidenzstatus",
    "claim_text": "Wissenschaftliche Aussage",
    "result_status": "Ergebnisstatus",
    "created_at": "Erstellt am",
    "updated_at": "Aktualisiert am",
    "source": "Metadatenquelle",
    "matched_field": "Getroffenes Metadatenfeld",
    "matched_value": "Gefundener Wert",
    "relation_name": "Relationsname",
    "table_or_view_name": "Tabelle oder View",
    "label_or_alias": "Bezeichnung oder Alias",
    "unit": "Einheit",
    "dimension": "Dimension",
    "related_view": "Zugeordnete View",
    "status": "Status",
    "severity": "Schweregrad",
    "human_review_state": "Menschlicher Prüfstatus",
    "presentation_scope": "Anzeigebereich",
    "canonical_object_type": "Kanonischer Objekttyp",
    "canonical_object_id": "Kanonische Objekt-ID",
}

ALREADY_READABLE_GERMAN = {
    "aussage",
    "anzeigeeinheit",
    "beobachtung",
    "berechnungseinheit",
    "beziehung",
    "dimensionsstatus",
    "dimensionsvektor",
    "einheitenstatus",
    "ergebniszeile",
    "groessenart",
    "meldung",
    "offener_pruefpunkt",
    "originaleinheit",
    "pruefebene",
    "pruefregel",
    "quellfeld",
    "quellobjekt",
    "schweregrad",
    "zielfeld",
    "zielobjekt",
}

GERMAN_WORDS = {
    "alias": "Alias",
    "calculation": "Berechnung",
    "canonical": "Kanonisch",
    "checksum": "Prüfsumme",
    "claim": "Aussage",
    "class": "Klasse",
    "code": "Code",
    "comparison": "Vergleich",
    "conversion": "Umrechnung",
    "created": "Erstellt",
    "data": "Daten",
    "description": "Beschreibung",
    "dimension": "Dimension",
    "display": "Anzeige",
    "evidence": "Evidenz",
    "field": "Feld",
    "id": "ID",
    "key": "Schlüssel",
    "kind": "Art",
    "language": "Sprache",
    "layer": "Ebene",
    "lineage": "Lineage",
    "link": "Link",
    "mart": "Mart",
    "mode": "Modus",
    "name": "Name",
    "object": "Objekt",
    "original": "Original",
    "package": "Paket",
    "path": "Pfad",
    "quantity": "Größe",
    "record": "Datensatz",
    "relation": "Beziehung",
    "result": "Ergebnis",
    "rule": "Regel",
    "scope": "Umfang",
    "source": "Quelle",
    "status": "Status",
    "table": "Tabelle",
    "target": "Ziel",
    "text": "Text",
    "type": "Typ",
    "unit": "Einheit",
    "updated": "Aktualisiert",
    "validation": "Validierung",
    "value": "Wert",
    "vector": "Vektor",
    "version": "Version",
    "view": "View",
    "work": "Arbeit",
}


@dataclass
class FieldLabelResolver:
    relation_aliases: dict[tuple[str, str], str] = field(default_factory=dict)
    general_aliases: dict[str, str] = field(default_factory=dict)
    fallback_labels: dict[str, str] = field(default_factory=lambda: dict(GERMAN_FIELD_FALLBACKS))

    @classmethod
    def from_database(cls, database: QSBMetadataDatabase) -> "FieldLabelResolver":
        resolver = cls()
        if "meta_alias" not in database.list_tables():
            return resolver
        rows = database.execute_read_only(
            """
            SELECT canonical_object_id, language_code, alias_text, presentation_scope
            FROM meta_alias
            WHERE canonical_object_type = ?
              AND language_code = ?
            ORDER BY presentation_scope, canonical_object_id
            """,
            ("field", "de"),
        )
        for row in rows:
            canonical = str(row["canonical_object_id"])
            alias = str(row["alias_text"])
            if "." in canonical:
                relation, field_name = canonical.split(".", 1)
                resolver.relation_aliases[(relation, field_name)] = alias
            else:
                resolver.general_aliases[canonical] = alias
        return resolver

    def display_label(self, canonical_name: str, relation_name: str | None = None) -> str:
        if relation_name and (relation_name, canonical_name) in self.relation_aliases:
            return self.relation_aliases[(relation_name, canonical_name)]
        if canonical_name in self.general_aliases:
            return self.general_aliases[canonical_name]
        if canonical_name in self.fallback_labels:
            return self.fallback_labels[canonical_name]
        if canonical_name.casefold() in ALREADY_READABLE_GERMAN:
            return readable_existing_german(canonical_name)
        return readable_german_fallback(canonical_name)

    def mapping_for(self, canonical_names: list[str], relation_name: str | None = None) -> tuple[dict[str, str], dict[str, str]]:
        canonical_to_display: dict[str, str] = {}
        display_to_canonical: dict[str, str] = {}
        counts: dict[str, int] = {}
        for canonical in canonical_names:
            base = self.display_label(canonical, relation_name)
            counts[base] = counts.get(base, 0) + 1
            display = base if counts[base] == 1 else f"{base} ({canonical})"
            canonical_to_display[canonical] = display
            display_to_canonical[display] = canonical
        return canonical_to_display, display_to_canonical

    def canonical_for_display(self, display_label: str, canonical_names: list[str], relation_name: str | None = None) -> str:
        _canonical_to_display, display_to_canonical = self.mapping_for(canonical_names, relation_name)
        return display_to_canonical.get(display_label, display_label)


def readable_existing_german(name: str) -> str:
    special = {
        "groessenart": "Größenart",
        "pruefebene": "Prüfebene",
        "pruefregel": "Prüfregel",
        "quellobjekt": "Quellobjekt",
        "zielobjekt": "Zielobjekt",
        "quellfeld": "Quellfeld",
        "zielfeld": "Zielfeld",
    }
    return special.get(name.casefold(), name.replace("_", " ").capitalize())


def readable_german_fallback(name: str) -> str:
    words = [part for part in name.replace("-", "_").split("_") if part]
    if not words:
        return "Unbenanntes Feld"
    translated = [GERMAN_WORDS.get(word.casefold(), word.capitalize()) for word in words]
    return " ".join(translated)
