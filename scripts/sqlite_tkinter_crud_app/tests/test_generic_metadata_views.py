from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.qsb_database import QSBMetadataDatabase


def make_corrcore_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE meta_mart (
            mart_id TEXT PRIMARY KEY,
            mart_code TEXT NOT NULL,
            canonical_namespace TEXT NOT NULL,
            mart_name TEXT NOT NULL,
            scope_status TEXT NOT NULL,
            schema_version TEXT
        );
        CREATE TABLE meta_work_package (
            work_package_id TEXT PRIMARY KEY,
            mart_id TEXT NOT NULL,
            work_package_code TEXT NOT NULL,
            canonical_namespace TEXT,
            work_package_name TEXT NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE meta_object (
            object_id TEXT PRIMARY KEY,
            mart_id TEXT NOT NULL,
            work_package_id TEXT,
            object_code TEXT,
            object_type TEXT,
            canonical_name TEXT,
            repository_path TEXT,
            status TEXT
        );
        CREATE TABLE meta_result_table (
            result_table_id TEXT PRIMARY KEY,
            mart_id TEXT NOT NULL,
            object_id TEXT NOT NULL,
            table_role TEXT NOT NULL,
            record_lineage_mode TEXT NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE meta_result_record (
            result_record_id TEXT PRIMARY KEY,
            result_table_id TEXT NOT NULL,
            mart_id TEXT NOT NULL,
            source_result_key TEXT NOT NULL,
            result_class TEXT NOT NULL,
            comparability_status TEXT NOT NULL,
            formal_validation_status TEXT NOT NULL,
            physical_validation_status TEXT NOT NULL,
            evidence_class TEXT NOT NULL
        );
        CREATE VIEW v_de_test AS SELECT mart_code FROM meta_mart;

        INSERT INTO meta_mart VALUES
            ('MART_QSB_CORRCORE01', 'QSB-CORRCORE01', 'qsb.corrcore01', 'Korrelationskern / Correlation Core', 'registered', 'test');
        INSERT INTO meta_work_package VALUES
            ('WP_QSB_CORRCORE01', 'MART_QSB_CORRCORE01', 'QSB-CORRCORE01', 'qsb.corrcore01', 'Korrelationskern / Correlation Core', 'registered');
        INSERT INTO meta_object VALUES
            ('OBJ_RT', 'MART_QSB_CORRCORE01', 'WP_QSB_CORRCORE01', 'CORRCORE01.result_records', 'run_output', 'correlation_core_objects', 'runs/QSB-CORRCORE01/correlation_core_dwh_seed/correlation_core_objects.csv', 'registered');
        """
    )
    roles = [
        "source_documents",
        "central_objects",
        "equations",
        "quantities",
        "claim_boundaries",
        "cross_strand_relationships",
        "validation_results",
    ]
    for role in roles:
        conn.execute(
            "INSERT INTO meta_result_table VALUES (?, ?, ?, ?, ?, ?)",
            (f"RT_{role}", "MART_QSB_CORRCORE01", "OBJ_RT", role, "materialized", "registered"),
        )
    for key, role in [
        ("correlation_matrix_Kij", "central_objects"),
        ("effective_distance_dij", "central_objects"),
        ("Kij_definition", "equations"),
    ]:
        conn.execute(
            "INSERT INTO meta_result_record VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"RR_{key}", f"RT_{role}", "MART_QSB_CORRCORE01", key, "neutral", "comparable", "passed", "not_applicable", "neutral"),
        )
    conn.commit()
    conn.close()


class GenericMetadataViewTests(unittest.TestCase):
    def test_generic_queries_discover_corrcore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "corrcore.sqlite"
            make_corrcore_db(path)
            db = QSBMetadataDatabase(path)
            mart_page = db.generic_mart_work_packages()
            self.assertEqual(mart_page.rows[0]["mart_code"], "QSB-CORRCORE01")
            table_page = db.generic_result_tables()
            self.assertIn("central_objects", {row["table_role"] for row in table_page.rows})
            record_page = db.generic_result_records(mart_code="QSB-CORRCORE01", table_role="central_objects", search="Kij")
            self.assertEqual(record_page.rows[0]["source_result_key"], "correlation_matrix_Kij")

    def test_corrcore_visibility_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "corrcore.sqlite"
            make_corrcore_db(path)
            status = QSBMetadataDatabase(path).corrcore_visibility_status()
            self.assertTrue(all(status.values()), status)


if __name__ == "__main__":
    unittest.main()
