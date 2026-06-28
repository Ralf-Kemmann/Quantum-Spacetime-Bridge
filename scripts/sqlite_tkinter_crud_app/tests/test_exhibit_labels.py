from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.exhibit_labels import FIELD_LABELS, resolve_museum_label
from src.qsb_database import QSBMetadataDatabase
from src.showcase import load_showcase_config
from src.snapshot_manager import sha256_file


def make_label_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE control_cycle_counts(
            control_id TEXT,
            detected_complete_cycle_count INTEGER,
            validation_status TEXT,
            control_status TEXT
        );
        CREATE TABLE meta_claim_result_link(
            claim_text TEXT,
            relation_type TEXT,
            evidence_class TEXT,
            validation_status TEXT,
            human_review_state TEXT,
            limitation_text TEXT,
            work_package_code TEXT
        );
        CREATE TABLE meta_field(
            quantity_kind TEXT,
            unit_status TEXT,
            dimension_status TEXT,
            conversion_rule_id TEXT
        );
        CREATE TABLE meta_validation_result(
            issue TEXT,
            affected_object TEXT,
            review_priority TEXT,
            current_status TEXT,
            human_review_state TEXT,
            evidence_reference TEXT,
            work_package_code TEXT
        );
        CREATE VIEW v_de_causality07_reaktionszyklus AS
            SELECT 'QSB-CAUSALITY07' AS mart_code,
                   '07-02' AS work_package_code,
                   'registered' AS evidence_status,
                   'source_inventory' AS sequence_definition_source;
        CREATE VIEW v_de_ergebnis_claim_beziehungen AS SELECT * FROM meta_claim_result_link;
        CREATE VIEW v_de_physikalische_groessen AS SELECT * FROM meta_field;
        CREATE VIEW v_de_offene_pruefpunkte AS SELECT * FROM meta_validation_result;
        INSERT INTO control_cycle_counts VALUES ('baseline', 2, 'passed', 'controlled comparison');
        INSERT INTO meta_claim_result_link VALUES ('claim', 'supports', 'registered', 'passed', 'reviewed', 'limited scope', '07-03');
        INSERT INTO meta_field VALUES ('model time', 'model_unit_unmapped', 'unresolved', NULL);
        INSERT INTO meta_validation_result VALUES ('missing calibration', 'threshold', 'high', 'open', 'required', 'fixture', '07-03');
        """
    )
    conn.commit()
    conn.close()


class ExhibitLabelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_showcase_config()
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "labels.sqlite"
        make_label_db(self.db_path)
        manifest = {
            "detected_mart_codes": ["QSB-CAUSALITY07"],
            "detected_work_package_codes": ["07-01", "07-02", "07-03"],
            "snapshot_sha256": "snapshot-fixture",
        }
        self.db = QSBMetadataDatabase(self.db_path, manifest=manifest)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_all_inventory_numbers_exist_and_are_unique(self) -> None:
        numbers = [exhibit["museum_label"]["inventory_number"] for exhibit in self.config["exhibits"]]
        self.assertEqual(numbers, ["QSB-EXH-C07-01", "QSB-EXH-C07-02", "QSB-EXH-C07-03", "QSB-EXH-C07-04", "QSB-EXH-C07-05"])
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_bilingual_field_labels_exist(self) -> None:
        for labels in FIELD_LABELS.values():
            self.assertTrue(labels["de"])
            self.assertTrue(labels["en"])

    def test_unavailable_fields_are_omitted_and_no_empty_rows_render(self) -> None:
        label = resolve_museum_label(self.db, self.config, "causality07_reaction_cycle", "de")
        self.assertTrue(label.fields)
        self.assertTrue(all(field.value for field in label.fields))
        keys = {field.key for field in label.fields}
        self.assertNotIn("unit_status", keys)
        self.assertNotIn("dimension_status", keys)

    def test_canonical_ids_and_technical_provenance_are_preserved(self) -> None:
        label = resolve_museum_label(self.db, self.config, "causality07_reaction_cycle", "en")
        technical = {field.key: field.value for field in label.technical_fields}
        self.assertEqual(technical["canonical_mart_code"], "QSB-CAUSALITY07")
        self.assertIn("07-02", technical["work_package_code"])
        self.assertEqual(technical["source_relation"], "v_de_causality07_reaktionszyklus")
        self.assertEqual(technical["snapshot_checksum"], "snapshot-fixture")

    def test_data_driven_status_evidence_and_unresolved_values_resolve(self) -> None:
        result_label = resolve_museum_label(self.db, self.config, "results_boundaries", "en")
        result_values = {field.key: field.value for field in result_label.fields}
        self.assertEqual(result_values["status"], "passed")
        self.assertEqual(result_values["evidence_class"], "registered")
        quantity_label = resolve_museum_label(self.db, self.config, "physical_quantities", "en")
        quantity_values = {field.key: field.value for field in quantity_label.fields}
        self.assertEqual(quantity_values["unit_status"], "model_unit_unmapped")
        self.assertEqual(quantity_values["dimension_status"], "unresolved")

    def test_reaction_cycle_provenance_and_open_question_priority(self) -> None:
        reaction_label = resolve_museum_label(self.db, self.config, "causality07_reaction_cycle", "de")
        self.assertIn("source_inventory", {field.key: field.value for field in reaction_label.fields}["provenance"])
        open_label = resolve_museum_label(self.db, self.config, "open_questions", "en")
        open_values = {field.key: field.value for field in open_label.fields}
        self.assertEqual(open_values["open_question"], "missing calibration")
        self.assertEqual(open_values["status"], "open")

    def test_read_only_resolution_preserves_checksum(self) -> None:
        before = sha256_file(self.db_path)
        for exhibit in self.config["exhibits"]:
            resolve_museum_label(self.db, self.config, exhibit["id"], "de")
        self.assertEqual(sha256_file(self.db_path), before)


if __name__ == "__main__":
    unittest.main()
