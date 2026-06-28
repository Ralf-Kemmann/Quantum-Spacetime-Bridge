from __future__ import annotations

import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.export_service import ExportError, export_rows_to_csv
from src.snapshot_manager import sha256_file


class ExportServiceTests(unittest.TestCase):
    def test_csv_export_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "source.sqlite"
            sqlite3.connect(db_path).execute("CREATE TABLE t(id INTEGER)").connection.close()
            before = sha256_file(db_path)
            destination = Path(tmp) / "export.csv"
            export_rows_to_csv(
                destination,
                ["a", "b"],
                [{"a": "1", "b": None}],
                {"snapshot_sha256": "abc"},
                "v_de_test",
                {"quick": "x"},
                write_manifest=True,
            )
            with destination.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["a"], "1")
            manifest = json.loads(destination.with_suffix(".csv.manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_relation"], "v_de_test")
            self.assertEqual(sha256_file(db_path), before)

    def test_export_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ExportError):
                export_rows_to_csv(Path(tmp) / "x.csv", ["a"], [{"a": i} for i in range(3)], {}, "t", row_limit=2)


if __name__ == "__main__":
    unittest.main()
