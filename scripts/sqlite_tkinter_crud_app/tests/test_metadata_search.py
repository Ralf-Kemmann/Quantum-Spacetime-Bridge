from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.metadata_search import MetadataSearchAdapter, detect_metadata_sources
from src.qsb_database import QSBMetadataDatabase


def make_search_db(path: Path, include_metadata: bool = True, include_view: bool = True) -> None:
    conn = sqlite3.connect(path)
    if include_metadata:
        conn.executescript(
            """
            CREATE TABLE meta_object (
                object_id TEXT PRIMARY KEY,
                object_code TEXT,
                canonical_name TEXT,
                repository_path TEXT,
                status TEXT
            );
            CREATE TABLE meta_field (
                field_id TEXT PRIMARY KEY,
                object_id TEXT,
                canonical_field_name TEXT,
                unit_status TEXT,
                dimension_status TEXT,
                description TEXT
            );
            INSERT INTO meta_object VALUES
                ('OBJ1', 'CATALOG.VIEW', 'v_catalog', 'runs/example.csv', 'registered');
            INSERT INTO meta_field VALUES
                ('FIELD1', 'OBJ1', 'quantity_kind', 'model_unit_unmapped', 'dimension_unmapped', 'Einheit Dimension Causality07');
            """
        )
    else:
        conn.execute("CREATE TABLE ordinary(id INTEGER, value TEXT)")
    if include_view:
        conn.execute("CREATE VIEW v_catalog AS SELECT object_code, canonical_name, status FROM meta_object")
    conn.commit()
    conn.close()


class MetadataSearchTests(unittest.TestCase):
    def test_detect_metadata_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_search_db(path)
            db = QSBMetadataDatabase(path)
            names = [source.name for source in detect_metadata_sources(db)]
            self.assertIn("meta_object", names)
            self.assertIn("meta_field", names)

    def test_search_across_multiple_text_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_search_db(path)
            db = QSBMetadataDatabase(path)
            results = MetadataSearchAdapter(db).search("Einheit Dimension")
            self.assertTrue(results)
            self.assertTrue(any(result.source == "meta_field" for result in results))
            self.assertTrue(any(result.matched_field in {"description", "dimension_status"} for result in results))

    def test_parameterized_search_blocks_injection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_search_db(path)
            db = QSBMetadataDatabase(path)
            results = MetadataSearchAdapter(db).search("x%' OR 1=1 --")
            self.assertEqual(results, [])
            with db.connect() as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM meta_object").fetchone()[0], 1)

    def test_result_resolves_existing_view(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_search_db(path)
            db = QSBMetadataDatabase(path)
            results = MetadataSearchAdapter(db).search("v_catalog")
            self.assertTrue(any(result.related_view == "v_catalog" for result in results))

    def test_empty_database_and_missing_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.sqlite"
            sqlite3.connect(path).close()
            db = QSBMetadataDatabase(path)
            self.assertEqual(db.list_views(), [])
            self.assertEqual(detect_metadata_sources(db), [])
            self.assertEqual(MetadataSearchAdapter(db).search("anything"), [])

    def test_no_metadata_relations_and_no_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ordinary.sqlite"
            make_search_db(path, include_metadata=False, include_view=False)
            db = QSBMetadataDatabase(path)
            self.assertEqual(detect_metadata_sources(db), [])
            self.assertEqual(MetadataSearchAdapter(db).search("value"), [])

    def test_null_values_do_not_break_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_search_db(path)
            db = QSBMetadataDatabase(path)
            results = MetadataSearchAdapter(db).search("quantity_kind")
            self.assertTrue(results)


if __name__ == "__main__":
    unittest.main()
