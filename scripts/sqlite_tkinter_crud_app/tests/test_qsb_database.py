from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DEFAULT_QSB_METADATA_DB
from src.qsb_database import QSBDatabaseError, QSBMetadataDatabase, quote_identifier, resolve_database_path


def make_test_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE "meta weird" (
            id INTEGER PRIMARY KEY,
            view_name TEXT,
            object_name TEXT,
            field_name TEXT,
            description TEXT,
            unit TEXT,
            dimension TEXT,
            validation_status TEXT,
            evidence_status TEXT
        );
        INSERT INTO "meta weird"
            (view_name, object_name, field_name, description, unit, dimension, validation_status, evidence_status)
        VALUES
            ('v items', 'item table', 'quantity_kind', 'Dimension und Einheit Causality07', 's', '[0,0,1,0,0,0,0]', 'passed', 'supports'),
            ('v items', 'item table', 'alias', NULL, NULL, NULL, 'warning', 'neutral');
        CREATE VIEW "v items" AS SELECT id, object_name, field_name, description FROM "meta weird";
        """
    )
    conn.commit()
    conn.close()


class QSBDatabaseTests(unittest.TestCase):
    def test_database_path_priority(self) -> None:
        env_path = "/tmp/env.sqlite"
        cli_path = "/tmp/cli.sqlite"
        self.assertEqual(resolve_database_path(cli_path, {"QSB_METADATA_DB": env_path}), Path(cli_path))
        self.assertEqual(resolve_database_path(None, {"QSB_METADATA_DB": env_path}), Path(env_path))
        self.assertEqual(resolve_database_path(None, {}), DEFAULT_QSB_METADATA_DB)

    def test_missing_database_raises(self) -> None:
        db = QSBMetadataDatabase(Path("/tmp/does-not-exist-qsb.sqlite"))
        with self.assertRaises(QSBDatabaseError):
            db.connect()

    def test_read_only_connection_rejects_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_test_db(path)
            db = QSBMetadataDatabase(path)
            with db.connect() as conn:
                with self.assertRaises(sqlite3.OperationalError):
                    conn.execute('INSERT INTO "meta weird"(description) VALUES (?)', ("write",))

    def test_dynamic_view_discovery_and_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_test_db(path)
            db = QSBMetadataDatabase(path)
            self.assertEqual(db.list_views(), ["v items"])
            self.assertIn("description", db.columns_for_relation("v items"))

    def test_identifier_quoting(self) -> None:
        self.assertEqual(quote_identifier('a"b'), '"a""b"')
        with self.assertRaises(ValueError):
            quote_identifier("")

    def test_load_view_page_and_pagination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_test_db(path)
            db = QSBMetadataDatabase(path)
            db.list_views()
            page = db.load_view_page("v items", offset=0, limit=1)
            self.assertEqual(page.total_count, 2)
            self.assertEqual(page.columns, ["id", "object_name", "field_name", "description"])
            self.assertEqual(len(page.rows), 1)
            second = db.load_view_page("v items", offset=1, limit=1)
            self.assertEqual(second.rows[0]["field_name"], "alias")

    def test_filter_current_view(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.sqlite"
            make_test_db(path)
            db = QSBMetadataDatabase(path)
            db.list_views()
            page = db.load_view_page("v items", filter_column="field_name", filter_value="quantity")
            self.assertEqual(page.total_count, 1)
            self.assertEqual(page.rows[0]["field_name"], "quantity_kind")


if __name__ == "__main__":
    unittest.main()
