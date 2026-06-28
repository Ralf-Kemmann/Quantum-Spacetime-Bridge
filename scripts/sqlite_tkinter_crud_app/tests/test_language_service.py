from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.language_service import LanguageService, load_saved_language, resolve_start_language, save_language


class LanguageServiceTests(unittest.TestCase):
    def test_german_default_and_english_selection(self) -> None:
        self.assertEqual(resolve_start_language(None, Path("/tmp/no-such-qsb-settings.json")), "de")
        service = LanguageService("en")
        self.assertEqual(service.field_label("quantity_kind"), "Quantity kind")
        service.set_language("de")
        self.assertEqual(service.field_label("quantity_kind"), "Größenart")

    def test_saved_preference_and_cli_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            save_language("en", path)
            self.assertEqual(load_saved_language(path), "en")
            self.assertEqual(resolve_start_language("de", path), "de")

    def test_alias_precedence_and_fallbacks(self) -> None:
        service = LanguageService("en", {"en": {"quantity_kind": "DB quantity alias"}})
        resolution = service.resolve_field_label("quantity_kind")
        self.assertEqual(resolution.label, "DB quantity alias")
        self.assertEqual(resolution.source, "database_alias")
        self.assertEqual(service.resolve_field_label("unknown_field").source, "readable_format")
        self.assertEqual(service.value_label("model_unit_unmapped"), "model_unit_unmapped")

    def test_canonical_names_remain_available(self) -> None:
        service = LanguageService("en")
        self.assertIn("quantity_kind", service.field_label("quantity_kind", show_canonical=True))
        self.assertEqual("quantity_kind", service.resolve_field_label("quantity_kind").canonical_name)
        self.assertEqual(service.relation_label("v_de_lineage"), "Provenance and lineage")


if __name__ == "__main__":
    unittest.main()
