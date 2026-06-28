from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.snapshot_manager import SnapshotError, create_verified_snapshot, sha256_file, validate_sqlite_database


def make_source(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE meta_mart(mart_code TEXT);
        CREATE TABLE meta_work_package(work_package_code TEXT);
        CREATE VIEW v_de_test AS SELECT mart_code FROM meta_mart;
        INSERT INTO meta_mart VALUES ('QSB-TEST');
        INSERT INTO meta_work_package VALUES ('QSB-TEST-01');
        """
    )
    conn.commit()
    conn.close()


class SnapshotManagerTests(unittest.TestCase):
    def test_source_copied_manifest_written_and_checksums_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.sqlite"
            snapshot_dir = Path(tmp) / "snapshots"
            make_source(source)
            original_checksum = sha256_file(source)
            info = create_verified_snapshot(source, snapshot_dir=snapshot_dir, timestamp="20260615_120000")
            self.assertTrue(info.snapshot_path.exists())
            self.assertTrue(info.manifest_path.exists())
            self.assertEqual(info.manifest["source_sha256"], info.manifest["snapshot_sha256"])
            self.assertEqual(sha256_file(source), original_checksum)
            manifest = json.loads(info.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["detected_mart_codes"], ["QSB-TEST"])

    def test_invalid_sqlite_source_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "not.sqlite"
            source.write_text("not sqlite", encoding="utf-8")
            with self.assertRaises(SnapshotError):
                validate_sqlite_database(source)

    def test_overwrite_protection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.sqlite"
            snapshot_dir = Path(tmp) / "snapshots"
            make_source(source)
            create_verified_snapshot(source, snapshot_dir=snapshot_dir, timestamp="fixed")
            with self.assertRaises(SnapshotError):
                create_verified_snapshot(source, snapshot_dir=snapshot_dir, timestamp="fixed")
            info = create_verified_snapshot(source, snapshot_dir=snapshot_dir, timestamp="fixed", overwrite_snapshot=True)
            self.assertTrue(info.snapshot_path.exists())


if __name__ == "__main__":
    unittest.main()
