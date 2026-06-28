import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
LOADER = REPO_ROOT / "scripts/qsb_source_hub/source_hub_dry_run_loader.py"


class SourceHubDryRunLoaderTests(unittest.TestCase):
    def test_loader_runs_without_gap01b_and_creates_safe_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            db = out / "qsb_source_hub_dry_run.sqlite"
            subprocess.run(
                [
                    str(REPO_ROOT / ".venv/bin/python"),
                    str(LOADER),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--output-dir",
                    str(out),
                    "--db",
                    str(db),
                ],
                check=True,
                cwd=REPO_ROOT,
            )
            expected = {
                "01_gap02a_loader_input_register.csv",
                "02_gap02a_source_object_load_summary.csv",
                "03_gap02a_source_file_load_summary.csv",
                "04_gap02a_archive_entry_load_summary.csv",
                "05_gap02a_mart_candidate_load_summary.csv",
                "06_gap02a_claim_boundary_flag_summary.csv",
                "07_gap02a_deduplication_register.csv",
                "08_gap02a_unresolved_reference_register.csv",
                "09_gap02a_db_integrity_checks.md",
                "10_gap02a_final_assessment.md",
                "11_gap02a_run_manifest.json",
                "qsb_source_hub_dry_run.sqlite",
            }
            self.assertEqual(expected, {p.name for p in out.glob("*") if p.is_file()})
            con = sqlite3.connect(db)
            con.execute("PRAGMA foreign_keys=ON")
            tables = {
                row[0]
                for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            self.assertNotIn("canonical", tables)
            self.assertNotIn("result_record", tables)
            bad = con.execute(
                """
                SELECT evidence_status FROM qsb_source_object
                WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
                UNION
                SELECT evidence_status FROM qsb_source_file
                WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
                UNION
                SELECT evidence_status FROM qsb_source_archive_entry
                WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
                """
            ).fetchall()
            self.assertEqual([], bad)

    def test_loader_creates_gap02c_hardened_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "QSB-GAP02C" / "source_hub_schema_hardening"
            db = out / "qsb_source_hub_hardened_dry_run.sqlite"
            subprocess.run(
                [
                    str(REPO_ROOT / ".venv/bin/python"),
                    str(LOADER),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--output-dir",
                    str(out),
                    "--db",
                    str(db),
                ],
                check=True,
                cwd=REPO_ROOT,
            )
            expected = {
                "01_gap02c_schema_hardening_change_log.csv",
                "02_gap02c_hardened_loader_input_register.csv",
                "03_gap02c_hardened_source_object_summary.csv",
                "04_gap02c_hardened_source_file_summary.csv",
                "05_gap02c_relationship_vocab_summary.csv",
                "06_gap02c_boolean_normalization_summary.csv",
                "07_gap02c_trigger_integrity_summary.csv",
                "08_gap02c_db_integrity_checks.md",
                "09_gap02c_final_assessment.md",
                "10_gap02c_run_manifest.json",
                "qsb_source_hub_hardened_dry_run.sqlite",
            }
            self.assertEqual(expected, {p.name for p in out.glob("*") if p.is_file()})
            con = sqlite3.connect(db)
            con.execute("PRAGMA foreign_keys=ON")
            tables = {
                row[0]
                for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            self.assertNotIn("canonical", tables)
            self.assertNotIn("result_record", tables)
            bad = con.execute(
                """
                SELECT evidence_status FROM qsb_source_object
                WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
                UNION
                SELECT evidence_status FROM qsb_source_file
                WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
                UNION
                SELECT evidence_status FROM qsb_source_archive_entry
                WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
                """
            ).fetchall()
            self.assertEqual([], bad)
            bad_bool = con.execute(
                "SELECT COUNT(*) FROM qsb_source_mart_candidate WHERE requires_human_review NOT IN (0, 1)"
            ).fetchone()[0]
            self.assertEqual(0, bad_bool)
            triggers = {
                row[0]
                for row in con.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
            }
            self.assertTrue({
                "trg_claim_boundary_file_matches_object_insert",
                "trg_claim_boundary_file_matches_object_update",
                "trg_mart_candidate_file_matches_object_insert",
                "trg_mart_candidate_file_matches_object_update",
            }.issubset(triggers))


if __name__ == "__main__":
    unittest.main()
