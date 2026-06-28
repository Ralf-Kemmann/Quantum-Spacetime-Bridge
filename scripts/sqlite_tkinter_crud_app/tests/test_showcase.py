from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.qsb_database import QSBMetadataDatabase
from src.showcase import (
    REQUIRED_EXHIBIT_IDS,
    control_chart_config,
    cycle_control_counts,
    exhibit_by_id,
    filter_quantity_rows,
    group_result_rows,
    load_showcase_config,
    localized,
    phase_sequence,
    resolve_reaction_scheme,
    resolve_exhibit,
    select_source,
    validate_showcase_config,
)
from src.snapshot_manager import sha256_file


def make_showcase_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE control_cycle_counts(
            control_id TEXT,
            detected_complete_cycle_count INTEGER,
            validation_status TEXT
        );
        CREATE TABLE fallback_only(
            field_name TEXT,
            issue TEXT
        );
        CREATE TABLE meta_claim_result_link(
            claim_text TEXT,
            relation_type TEXT,
            evidence_class TEXT,
            validation_status TEXT,
            human_review_state TEXT,
            limitation_text TEXT
        );
        CREATE TABLE meta_field(
            quantity_kind TEXT,
            value_original TEXT,
            unit_original TEXT,
            value_calculation TEXT,
            unit_calculation TEXT,
            value_display TEXT,
            unit_display TEXT,
            dimension_vector TEXT,
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
            work_package_code TEXT,
            suggested_next_action TEXT
        );
        CREATE VIEW v_de_causality07_reaktionszyklus AS
            SELECT 'CAUSALITY07' AS mart_code,
                   '07-02' AS work_package_code,
                   'registered sequence from fixture' AS case_description,
                   'P0 -> P1 -> P2' AS phase_sequence,
                   'registered' AS evidence_status;
        INSERT INTO control_cycle_counts VALUES ('baseline', 2, 'passed');
        INSERT INTO control_cycle_counts VALUES ('reverse', 0, 'passed');
        INSERT INTO meta_claim_result_link VALUES ('cycle result', 'supports', 'registered', 'passed', 'reviewed', NULL);
        INSERT INTO meta_claim_result_link VALUES ('boundary result', 'contradictory', 'registered', 'warning', 'review_required', 'fixture limitation');
        INSERT INTO meta_field VALUES ('model time', 't_model', 'model_unit', NULL, NULL, NULL, NULL, NULL, 'model_unit_unmapped', 'unresolved', NULL);
        INSERT INTO meta_field VALUES ('not applicable row', 'not applicable', 'not applicable', NULL, NULL, NULL, NULL, NULL, 'not applicable', 'not applicable', NULL);
        INSERT INTO meta_validation_result VALUES ('missing calibration', 'threshold', 'high', 'open', 'required', 'fixture', '07-03', NULL);
        """
    )
    conn.commit()
    conn.close()


def collect_numbers(value):
    found = []
    if isinstance(value, bool):
        return found
    if isinstance(value, (int, float)):
        return [value]
    if isinstance(value, dict):
        for child in value.values():
            found.extend(collect_numbers(child))
    if isinstance(value, list):
        for child in value:
            found.extend(collect_numbers(child))
    return found


class ShowcaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_showcase_config()
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "showcase.sqlite"
        make_showcase_db(self.db_path)
        self.db = QSBMetadataDatabase(self.db_path)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_config_loads_and_contains_required_bilingual_exhibits(self) -> None:
        validate_showcase_config(self.config)
        ids = {exhibit["id"] for exhibit in self.config["exhibits"]}
        self.assertEqual(REQUIRED_EXHIBIT_IDS - ids, set())
        for exhibit in self.config["exhibits"]:
            self.assertTrue(exhibit["title"]["de"])
            self.assertTrue(exhibit["title"]["en"])
        self.assertEqual(sorted(set(collect_numbers(self.config))), [520, 760])

    def test_landing_defaults_are_exhibition_first(self) -> None:
        self.assertEqual(self.config["default_exhibit_id"], "causality07_reaction_cycle")
        first = self.config["exhibits"][0]
        self.assertEqual(first["id"], "causality07_reaction_cycle")
        self.assertTrue(first["expert_targets"])

    def test_overview_configuration_loads_as_default_foyer(self) -> None:
        overview = self.config["overview"]
        self.assertEqual(overview["tab_title"]["de"], "Überblick")
        self.assertEqual(overview["tab_title"]["en"], "Overview")
        self.assertEqual(overview["title"]["de"], "QSB Research Data Browser")
        self.assertIn("QSB-CAUSALITY07", overview["introduction"]["de"])
        self.assertEqual(overview["image_resource"], "qsb_causality07_exhibition_overview.png")
        self.assertIn("checksum_match", overview["status_strip_fields"])

    def test_overview_cards_match_exhibits_and_inventory_numbers(self) -> None:
        overview = self.config["overview"]
        expected_order = [
            "causality07_reaction_cycle",
            "cycle_control_runs",
            "results_boundaries",
            "physical_quantities",
            "open_questions",
        ]
        self.assertEqual(overview["exhibit_card_order"], expected_order)
        inventories = [exhibit_by_id(self.config, exhibit_id)["museum_label"]["inventory_number"] for exhibit_id in expected_order]
        self.assertEqual(inventories, ["QSB-EXH-C07-01", "QSB-EXH-C07-02", "QSB-EXH-C07-03", "QSB-EXH-C07-04", "QSB-EXH-C07-05"])

    def test_each_exhibit_declares_visual_panel_with_bilingual_captions(self) -> None:
        for exhibit in self.config["exhibits"]:
            visual = exhibit.get("visual_panel", {})
            self.assertIn("caption", visual)
            self.assertIn("fallback_caption", visual)
            self.assertTrue(visual["caption_de"])
            self.assertTrue(visual["caption_en"])
            self.assertTrue(visual["image_alt_de"])
            self.assertTrue(visual["image_alt_en"])
            self.assertTrue(visual["caption"]["de"])
            self.assertTrue(visual["caption"]["en"])
            self.assertTrue(visual["fallback_caption"]["de"])
            self.assertTrue(visual["fallback_caption"]["en"])
            self.assertEqual(visual.get("preferred_layout"), "responsive")
            self.assertEqual(visual.get("image_fit_mode"), "contain")
            self.assertEqual(visual.get("image_max_width"), 760)
            self.assertEqual(visual.get("image_max_height"), 520)

    def test_exhibit_poster_mapping_is_complete_unique_and_source_files_exist(self) -> None:
        expected = {
            "causality07_reaction_cycle": "exhibits/causality_07_reaktionszyklus.png",
            "cycle_control_runs": "exhibits/causality_07_zyklus_und_kontrolllaeufe.png",
            "results_boundaries": "exhibits/causality_07_ergebnisse_und_grenzen.png",
            "physical_quantities": "exhibits/causality_07_physikalische_groessen.png",
            "open_questions": "exhibits/causality_07_offene_fragen.png",
        }
        actual = {
            exhibit["id"]: exhibit["visual_panel"]["image_resource"]
            for exhibit in self.config["exhibits"]
        }
        self.assertEqual(actual, expected)
        self.assertEqual(len(set(actual.values())), 5)
        resource_root = Path(__file__).resolve().parent.parent / "resources"
        for resource in actual.values():
            self.assertTrue((resource_root / resource).is_file(), resource)

    def test_poster_captions_match_approved_bilingual_text(self) -> None:
        expected = {
            "causality07_reaction_cycle": (
                "Vom Reaktionsmodell über den strukturierten Zyklus bis zur möglichen QSB-Interface-Deutung.",
                "From the reaction model through the structured cycle to a possible QSB interface interpretation.",
            ),
            "cycle_control_runs": (
                "Baseline, umgekehrte Folge und verwürfelte Kontrolle im direkten Vergleich.",
                "Direct comparison of baseline, reversed sequence, and scrambled control.",
            ),
            "results_boundaries": (
                "Messbare Ergebnisse, Evidenzgrenzen und klar getrennte Aussagebereiche.",
                "Measured results, evidence boundaries, and clearly separated claim domains.",
            ),
            "physical_quantities": (
                "Physikalische Größen, Einheiten, Dimensionen und SI-Normalisierung.",
                "Physical quantities, units, dimensions, and SI normalization.",
            ),
            "open_questions": (
                "Offene Fragen als strukturierte Forschungsagenda für die nächsten Prüfschritte.",
                "Open questions as a structured research agenda for the next validation steps.",
            ),
        }
        for exhibit_id, (de, en) in expected.items():
            visual = exhibit_by_id(self.config, exhibit_id)["visual_panel"]
            self.assertEqual(visual["caption_de"], de)
            self.assertEqual(visual["caption_en"], en)

    def test_foyer_image_remains_separate_from_exhibit_posters(self) -> None:
        overview_resource = self.config["overview"]["image_resource"]
        poster_resources = {exhibit["visual_panel"]["image_resource"] for exhibit in self.config["exhibits"]}
        self.assertEqual(overview_resource, "qsb_causality07_exhibition_overview.png")
        self.assertNotIn(overview_resource, poster_resources)

    def test_explicit_source_wins_and_phase_sequence_comes_from_data(self) -> None:
        exhibit = exhibit_by_id(self.config, "causality07_reaction_cycle")
        source, used_fallback = select_source(self.db, exhibit)
        self.assertEqual(source, "v_de_causality07_reaktionszyklus")
        self.assertFalse(used_fallback)
        resolution = resolve_exhibit(self.db, self.config, "causality07_reaction_cycle")
        self.assertEqual(phase_sequence(resolution.rows, resolution.columns), ["P0", "P1", "P2"])

    def test_reaction_scheme_uses_explicit_source_and_no_generic_oregonator_equation(self) -> None:
        root = Path(self.tmp.name) / "repo"
        source = root / "data" / "QSB-CAUSALITY07-02" / "oregonator_config.json"
        source.parent.mkdir(parents=True)
        source.write_text(
            """
            {
              "model_equations": {
                "dx_dtau": "(q*y - x*y + x*(1 - x)) / epsilon",
                "dy_dtau": "(-q*y - x*y + f*z) / delta",
                "dz_dtau": "x - z"
              },
              "dimensionless_variables": {
                "x": "activator_related_dimensionless_variable"
              }
            }
            """,
            encoding="utf-8",
        )
        reaction = resolve_reaction_scheme(self.db, self.config, repo_root=root)
        self.assertFalse(reaction.empty)
        self.assertEqual(reaction.representation_type, "model_reaction_scheme")
        self.assertIn("dx/dτ = (q*y - x*y + x*(1 - x)) / epsilon", reaction.lines)
        joined = "\n".join(reaction.lines)
        self.assertNotIn("BrO3", joined)
        self.assertEqual(reaction.legend["x"], "activator_related_dimensionless_variable")

    def test_reaction_scheme_empty_state_when_no_source_exists(self) -> None:
        reaction = resolve_reaction_scheme(self.db, self.config, repo_root=Path(self.tmp.name) / "missing")
        self.assertTrue(reaction.empty)
        self.assertEqual(reaction.status["en"], "Not yet registered in the snapshot")

    def test_fallback_and_missing_source_empty_state(self) -> None:
        custom = {"exhibits": [{"id": "x", "preferred_sources": ["missing"], "fallback_sources": ["fallback_only"]}]}
        source, used_fallback = select_source(self.db, custom["exhibits"][0])
        self.assertEqual(source, "fallback_only")
        self.assertTrue(used_fallback)
        missing = {
            "exhibits": [{"id": "x", "preferred_sources": ["missing"], "fallback_sources": []}],
        }
        resolution = resolve_exhibit(self.db, missing, "x")
        self.assertTrue(resolution.empty)
        self.assertEqual(resolution.rows, [])

    def test_counts_chart_and_result_groups_use_actual_rows(self) -> None:
        resolution = resolve_exhibit(self.db, self.config, "cycle_control_runs")
        self.assertEqual(cycle_control_counts(resolution.rows, resolution.columns), [("baseline", 2.0), ("reverse", 0.0)])
        chart = control_chart_config(resolution)
        self.assertIsNotNone(chart)
        self.assertEqual(chart.y_field, "detected_complete_cycle_count")
        self.assertEqual(chart.y_label, "detected complete cycles")
        grouped = group_result_rows(resolve_exhibit(self.db, self.config, "results_boundaries").rows)
        self.assertEqual(len(grouped["supported"]), 1)
        self.assertEqual(len(grouped["contradictory"]), 1)

    def test_language_titles_keep_same_canonical_exhibit_id(self) -> None:
        exhibit = exhibit_by_id(self.config, "physical_quantities")
        self.assertEqual(localized(exhibit["title"], "de"), "Physikalische Größen")
        self.assertEqual(localized(exhibit["title"], "en"), "Physical Quantities")
        self.assertEqual(exhibit["id"], "physical_quantities")

    def test_physical_quantities_and_open_questions_preserve_boundaries(self) -> None:
        quantities = resolve_exhibit(self.db, self.config, "physical_quantities")
        visible = filter_quantity_rows(quantities.rows, ["unit_status", "dimension_status"])
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0]["quantity_kind"], "model time")
        self.assertEqual(visible[0]["unit_status"], "model_unit_unmapped")
        open_questions = resolve_exhibit(self.db, self.config, "open_questions")
        self.assertEqual(open_questions.rows[0]["review_priority"], "high")
        self.assertIsNone(open_questions.rows[0]["suggested_next_action"])

    def test_read_only_resolution_preserves_database_checksum(self) -> None:
        before = sha256_file(self.db_path)
        for exhibit_id in REQUIRED_EXHIBIT_IDS:
            resolve_exhibit(self.db, self.config, exhibit_id)
        self.assertEqual(sha256_file(self.db_path), before)


if __name__ == "__main__":
    unittest.main()
