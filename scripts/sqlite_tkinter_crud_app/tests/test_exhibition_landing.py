from __future__ import annotations

import base64
import importlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import exhibition_landing
from src.exhibition_landing import EXHIBIT_CARDS, card_by_id, localized, overview_from_config, scale_to_fit, visual_from_exhibit


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


class ExhibitionLandingTests(unittest.TestCase):
    def test_five_exhibit_cards_map_to_expected_ids(self) -> None:
        self.assertEqual(
            [card.exhibit_id for card in EXHIBIT_CARDS],
            [
                "causality07_reaction_cycle",
                "cycle_control_runs",
                "results_boundaries",
                "physical_quantities",
                "open_questions",
            ],
        )
        self.assertEqual(card_by_id("open_questions").title["en"], "Open Questions")

    def test_german_and_english_labels_render(self) -> None:
        first = EXHIBIT_CARDS[0]
        self.assertEqual(localized(first.title, "de"), "CAUSALITY07 — Reaktionszyklus")
        self.assertEqual(localized(first.title, "en"), "CAUSALITY07 — Reaction Cycle")
        self.assertTrue(localized(first.description, "en"))

    def test_scaling_preserves_aspect_ratio_and_never_enlarges(self) -> None:
        self.assertEqual(scale_to_fit(2000, 1000, 1000, 1000), (1000, 500))
        self.assertEqual(scale_to_fit(2000, 1000, 3000, 3000), (2000, 1000))
        self.assertEqual(scale_to_fit(0, 1000, 1000, 1000), (0, 0))

    def test_source_tree_loader_reads_existing_resource(self) -> None:
        original_path = exhibition_landing.SOURCE_TREE_IMAGE
        try:
            with tempfile.TemporaryDirectory() as tmp:
                image = Path(tmp) / exhibition_landing.OVERVIEW_IMAGE_NAME
                image.write_bytes(PNG_1X1)
                exhibition_landing.SOURCE_TREE_IMAGE = image
                self.assertTrue(exhibition_landing.image_resource_exists())
                self.assertEqual(exhibition_landing.image_resource_bytes(), PNG_1X1)
                self.assertTrue(exhibition_landing.visual_resource_exists(exhibition_landing.OVERVIEW_IMAGE_NAME))
                self.assertEqual(exhibition_landing.visual_resource_bytes(exhibition_landing.OVERVIEW_IMAGE_NAME), PNG_1X1)
        finally:
            exhibition_landing.SOURCE_TREE_IMAGE = original_path

    def test_packaged_resource_loader_reads_from_zip_path(self) -> None:
        original_path = exhibition_landing.SOURCE_TREE_IMAGE
        original_package = exhibition_landing.RESOURCE_PACKAGE
        module_name = "tmp_qsb_resources"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                zip_path = Path(tmp) / "resources_test.pyz"
                with zipfile.ZipFile(zip_path, "w") as archive:
                    archive.writestr(f"{module_name}/__init__.py", "")
                    archive.writestr(f"{module_name}/{exhibition_landing.OVERVIEW_IMAGE_NAME}", PNG_1X1)
                    archive.writestr(f"{module_name}/nested/{exhibition_landing.OVERVIEW_IMAGE_NAME}", PNG_1X1)
                sys.path.insert(0, str(zip_path))
                importlib.invalidate_caches()
                exhibition_landing.SOURCE_TREE_IMAGE = Path(tmp) / "missing.png"
                exhibition_landing.RESOURCE_PACKAGE = module_name
                self.assertTrue(exhibition_landing.image_resource_exists())
                self.assertEqual(exhibition_landing.image_resource_bytes(), PNG_1X1)
                self.assertTrue(exhibition_landing.visual_resource_exists(exhibition_landing.OVERVIEW_IMAGE_NAME))
                self.assertEqual(exhibition_landing.visual_resource_bytes(exhibition_landing.OVERVIEW_IMAGE_NAME), PNG_1X1)
                self.assertTrue(exhibition_landing.visual_resource_exists(f"nested/{exhibition_landing.OVERVIEW_IMAGE_NAME}"))
                self.assertEqual(exhibition_landing.visual_resource_bytes(f"nested/{exhibition_landing.OVERVIEW_IMAGE_NAME}"), PNG_1X1)
        finally:
            exhibition_landing.SOURCE_TREE_IMAGE = original_path
            exhibition_landing.RESOURCE_PACKAGE = original_package
            if str(zip_path) in sys.path:
                sys.path.remove(str(zip_path))
            sys.modules.pop(module_name, None)

    def test_missing_image_falls_back_to_none(self) -> None:
        original_path = exhibition_landing.SOURCE_TREE_IMAGE
        original_package = exhibition_landing.RESOURCE_PACKAGE
        try:
            with tempfile.TemporaryDirectory() as tmp:
                exhibition_landing.SOURCE_TREE_IMAGE = Path(tmp) / "missing.png"
                exhibition_landing.RESOURCE_PACKAGE = "missing_qsb_resources"
                self.assertFalse(exhibition_landing.image_resource_exists())
                self.assertIsNone(exhibition_landing.image_resource_bytes())
        finally:
            exhibition_landing.SOURCE_TREE_IMAGE = original_path
            exhibition_landing.RESOURCE_PACKAGE = original_package

    def test_visual_config_keeps_bilingual_caption_and_fallback(self) -> None:
        exhibit = {
            "visual_panel": {
                "image_resource": "example.png",
                "image_alt_de": "Alt DE",
                "image_alt_en": "Alt EN",
                "caption_de": "Bild",
                "caption_en": "Image",
                "fallback_text_de": "Platzhalter",
                "fallback_text_en": "Placeholder",
                "preferred_layout": "responsive",
                "image_fit_mode": "contain",
                "image_max_width": 760,
                "image_max_height": 520,
            }
        }
        visual = visual_from_exhibit(exhibit)
        self.assertEqual(visual.image_resource, "example.png")
        self.assertEqual(localized(visual.image_alt, "de"), "Alt DE")
        self.assertEqual(localized(visual.caption, "en"), "Image")
        self.assertEqual(localized(visual.fallback_caption, "de"), "Platzhalter")
        self.assertEqual(visual.image_fit_mode, "contain")
        self.assertEqual((visual.image_max_width, visual.image_max_height), (760, 520))

    def test_overview_config_resolves_bilingual_foyer_fields(self) -> None:
        config = {
            "overview": {
                "tab_title": {"de": "Überblick", "en": "Overview"},
                "title": {"de": "QSB Research Data Browser", "en": "QSB Research Data Browser"},
                "subtitle": {"de": "Forschungsdaten", "en": "Research data"},
                "introduction": {"de": "Kurz.", "en": "Short."},
                "image_resource": "overview.png",
                "image_caption": {"de": "Bild", "en": "Image"},
                "fallback_text": {"de": "Fehlt", "en": "Missing"},
                "exhibit_card_order": ["causality07_reaction_cycle"],
                "status_strip_fields": ["mart"],
                "status_labels": {"mart": {"de": "Datamart", "en": "Datamart"}},
                "status_values": {"read_only": {"de": "aktiv", "en": "active"}},
                "expert_navigation_target": "Fachprüfung",
            }
        }
        overview = overview_from_config(config)
        self.assertEqual(localized(overview.tab_title, "de"), "Überblick")
        self.assertEqual(localized(overview.subtitle, "en"), "Research data")
        self.assertEqual(overview.image_resource, "overview.png")
        self.assertEqual(overview.exhibit_card_order, ["causality07_reaction_cycle"])


if __name__ == "__main__":
    unittest.main()
