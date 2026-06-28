from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.field_labels import FieldLabelResolver
from src.qsb_database import QSBMetadataDatabase


def make_alias_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE meta_alias (
            alias_id TEXT PRIMARY KEY,
            canonical_object_type TEXT NOT NULL,
            canonical_object_id TEXT NOT NULL,
            language_code TEXT NOT NULL,
            alias_text TEXT NOT NULL,
            presentation_scope TEXT NOT NULL
        );
        INSERT INTO meta_alias VALUES
            ('A1', 'field', 'canonical_field_name', 'de', 'Alias aus Katalog', 'presentation'),
            ('A2', 'field', 'v_test.object_code', 'de', 'Relationsobjektcode', 'presentation'),
            ('A3', 'field', 'object_code', 'de', 'Allgemeiner Objektcode', 'presentation');
        CREATE VIEW v_test AS SELECT 1 AS object_code, 2 AS canonical_field_name;
        """
    )
    conn.commit()
    conn.close()


class FieldLabelResolverTests(unittest.TestCase):
    def test_alias_from_meta_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "aliases.sqlite"
            make_alias_db(path)
            resolver = FieldLabelResolver.from_database(QSBMetadataDatabase(path))
            self.assertEqual(resolver.display_label("canonical_field_name"), "Alias aus Katalog")

    def test_relation_specific_alias_wins_over_general_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "aliases.sqlite"
            make_alias_db(path)
            resolver = FieldLabelResolver.from_database(QSBMetadataDatabase(path))
            self.assertEqual(resolver.display_label("object_code", "v_test"), "Relationsobjektcode")
            self.assertEqual(resolver.display_label("object_code", "other"), "Allgemeiner Objektcode")

    def test_fallback_dictionary_and_unknown_field(self) -> None:
        resolver = FieldLabelResolver()
        self.assertEqual(resolver.display_label("dimension_vector"), "Dimensionsvektor")
        self.assertEqual(resolver.display_label("source_result_key"), "Ergebnis-Schlüssel")
        self.assertEqual(resolver.display_label("physical_validation_status"), "Physikalischer Validierungsstatus")
        self.assertEqual(resolver.display_label("some_new_field"), "Some New Feld")

    def test_reverse_mapping_and_duplicate_display_labels(self) -> None:
        resolver = FieldLabelResolver(fallback_labels={"a": "Gleich", "b": "Gleich"})
        canonical_to_display, display_to_canonical = resolver.mapping_for(["a", "b"])
        self.assertEqual(display_to_canonical[canonical_to_display["a"]], "a")
        self.assertEqual(display_to_canonical[canonical_to_display["b"]], "b")

    def test_same_technical_name_in_different_relations(self) -> None:
        resolver = FieldLabelResolver(
            relation_aliases={("r1", "status"): "Status R1", ("r2", "status"): "Status R2"},
            fallback_labels={"status": "Status"},
        )
        self.assertEqual(resolver.display_label("status", "r1"), "Status R1")
        self.assertEqual(resolver.display_label("status", "r2"), "Status R2")

    def test_existing_german_column_is_not_double_translated(self) -> None:
        resolver = FieldLabelResolver()
        self.assertEqual(resolver.display_label("quellobjekt"), "Quellobjekt")
        self.assertEqual(resolver.display_label("groessenart"), "Größenart")


if __name__ == "__main__":
    unittest.main()
