import sqlite3
import unittest
from pathlib import Path


SCHEMA = Path(__file__).resolve().parents[1] / "source_hub_schema.sql"


class SourceHubSchemaTests(unittest.TestCase):
    def setUp(self):
        con = sqlite3.connect(":memory:")
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript(SCHEMA.read_text(encoding="utf-8"))
        self.con = con

    def insert_base_rows(self):
        self.con.execute(
            """
            INSERT INTO qsb_source_ingest_event
            (ingest_event_id, input_family, input_path, present, files_read, row_count_total)
            VALUES ('ING-1', 'TEST', 'test', 1, '', 0)
            """
        )
        for object_id, key in (("OBJ-1", "key-1"), ("OBJ-2", "key-2")):
            self.con.execute(
                """
                INSERT INTO qsb_source_object
                (source_object_id, stable_source_key, source_class, source_name, source_status,
                 evidence_status, claim_boundary_status, origin_gap_run, ingest_event_id, primary_declared_path)
                VALUES (?, ?, 'test_class', ?, 'DERIVED_FROM_GAP_OUTPUT',
                        'SOURCE_METADATA_ONLY', 'NOT_ASSESSED', 'TEST', 'ING-1', ?)
                """,
                (object_id, key, object_id, key),
            )
        self.con.execute(
            """
            INSERT INTO qsb_source_file
            (source_file_id, source_object_id, filename, normalized_file_key, declared_path,
             source_status, evidence_status, origin_gap_run, ingest_event_id)
            VALUES ('FILE-1', 'OBJ-1', 'same.txt', 'same.txt', NULL,
                    'DERIVED_FROM_GAP_OUTPUT', 'SOURCE_METADATA_ONLY', 'TEST', 'ING-1')
            """
        )

    def test_schema_applies_and_required_tables_exist(self):
        con = self.con
        tables = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        required = {
            "qsb_source_ingest_event",
            "qsb_source_object",
            "qsb_source_file",
            "qsb_source_archive_entry",
            "qsb_source_relationship",
            "qsb_source_claim_boundary_flag",
            "qsb_source_mart_candidate",
        }
        self.assertTrue(required.issubset(tables))
        self.assertEqual(con.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_requires_human_review_rejects_invalid_values(self):
        self.insert_base_rows()
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                """
                INSERT INTO qsb_source_mart_candidate
                (mart_candidate_id, source_object_id, source_file_id, target_area, candidate_status,
                 requires_human_review, origin_gap_run, ingest_event_id)
                VALUES ('MART-BAD-BOOL', 'OBJ-1', 'FILE-1', 'TEST', 'HOLD_FOR_REVIEW',
                        2, 'TEST', 'ING-1')
                """
            )

    def test_relationship_vocabularies_reject_invalid_values(self):
        self.insert_base_rows()
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                """
                INSERT INTO qsb_source_relationship
                (source_relationship_id, subject_source_object_id, object_source_object_id,
                 relationship_type, relationship_status, origin_gap_run, ingest_event_id)
                VALUES ('REL-BAD-TYPE', 'OBJ-1', 'OBJ-2', 'BAD_TYPE',
                        'INFERRED_REQUIRES_REVIEW', 'TEST', 'ING-1')
                """
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                """
                INSERT INTO qsb_source_relationship
                (source_relationship_id, subject_source_object_id, object_source_object_id,
                 relationship_type, relationship_status, origin_gap_run, ingest_event_id)
                VALUES ('REL-BAD-STATUS', 'OBJ-1', 'OBJ-2', 'RELATED_TO',
                        'BAD_STATUS', 'TEST', 'ING-1')
                """
            )

    def test_duplicate_normalized_file_key_rejects_same_object(self):
        self.insert_base_rows()
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                """
                INSERT INTO qsb_source_file
                (source_file_id, source_object_id, filename, normalized_file_key, declared_path,
                 source_status, evidence_status, origin_gap_run, ingest_event_id)
                VALUES ('FILE-2', 'OBJ-1', 'same.txt', 'same.txt', NULL,
                        'DERIVED_FROM_GAP_OUTPUT', 'SOURCE_METADATA_ONLY', 'TEST', 'ING-1')
                """
            )

    def test_claim_trigger_rejects_file_object_mismatch(self):
        self.insert_base_rows()
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                """
                INSERT INTO qsb_source_claim_boundary_flag
                (claim_flag_id, source_object_id, source_file_id, claim_boundary_status,
                 risk_note, recommended_handling, origin_gap_run, ingest_event_id)
                VALUES ('FLAG-BAD', 'OBJ-2', 'FILE-1', 'NOT_ASSESSED',
                        'risk', 'review', 'TEST', 'ING-1')
                """
            )

    def test_mart_candidate_trigger_rejects_file_object_mismatch(self):
        self.insert_base_rows()
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute(
                """
                INSERT INTO qsb_source_mart_candidate
                (mart_candidate_id, source_object_id, source_file_id, target_area, candidate_status,
                 requires_human_review, origin_gap_run, ingest_event_id)
                VALUES ('MART-BAD-LINK', 'OBJ-2', 'FILE-1', 'TEST', 'HOLD_FOR_REVIEW',
                        1, 'TEST', 'ING-1')
                """
            )


if __name__ == "__main__":
    unittest.main()
