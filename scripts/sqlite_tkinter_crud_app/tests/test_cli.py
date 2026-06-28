from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


APP = Path(__file__).resolve().parent.parent / "main.py"


def make_cli_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE meta_mart(mart_code TEXT);
        CREATE TABLE meta_work_package(work_package_code TEXT);
        CREATE TABLE meta_object(object_code TEXT, status TEXT);
        CREATE VIEW v_de_test AS SELECT object_code, status FROM meta_object;
        INSERT INTO meta_mart VALUES ('QSB-CLI');
        INSERT INTO meta_work_package VALUES ('QSB-CLI-01');
        INSERT INTO meta_object VALUES ('OBJ', 'registered');
        """
    )
    conn.commit()
    conn.close()


class CLITests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(APP), *args], text=True, capture_output=True, check=False)

    def test_help_and_version(self) -> None:
        self.assertEqual(self.run_cli("--help").returncode, 0)
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("QSB-GUI01", result.stdout)
        languages = self.run_cli("--list-languages")
        self.assertEqual(languages.returncode, 0)
        self.assertIn("de", languages.stdout)
        self.assertIn("en", languages.stdout)
        engine = self.run_cli("--chart-engine-info")
        self.assertEqual(engine.returncode, 0)
        self.assertIn("selected_chart_engine", engine.stdout)

    def test_list_views_tables_and_smoke_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "source.sqlite"
            snap_dir = Path(tmp) / "snapshots"
            make_cli_db(db_path)
            views = self.run_cli("--database", str(db_path), "--snapshot-dir", str(snap_dir), "--list-views")
            self.assertEqual(views.returncode, 0, views.stderr)
            self.assertIn("v_de_test", views.stdout)
            tables = self.run_cli("--database", str(db_path), "--snapshot-dir", str(snap_dir), "--list-tables")
            self.assertEqual(tables.returncode, 0, tables.stderr)
            self.assertIn("meta_object", tables.stdout)
            smoke = self.run_cli("--database", str(db_path), "--snapshot-dir", str(snap_dir), "--smoke-test")
            self.assertEqual(smoke.returncode, 0, smoke.stderr)
            self.assertIn("smoke_test_status=passed", smoke.stdout)
            smoke_en = self.run_cli("--database", str(db_path), "--snapshot-dir", str(snap_dir), "--language", "en", "--smoke-test")
            self.assertEqual(smoke_en.returncode, 0, smoke_en.stderr)
            self.assertIn("language=en", smoke_en.stdout)


if __name__ == "__main__":
    unittest.main()
