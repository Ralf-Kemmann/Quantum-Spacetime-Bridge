from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


GUI_SOURCE = Path(__file__).resolve().parent.parent / "src" / "qsb_gui.py"


class GuiLayoutStaticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = GUI_SOURCE.read_text(encoding="utf-8")

    def test_only_card_navigation_remains_for_primary_exhibits(self) -> None:
        self.assertIn("self.exhibit_card_buttons", self.source)
        self.assertNotIn("self.exhibit_buttons", self.source)
        self.assertNotIn("nav = ttk.LabelFrame", self.source)

    def test_overview_tab_is_first_and_default_startup_tab(self) -> None:
        self.assertIn("self.overview_tab = ttk.Frame(notebook)", self.source)
        self.assertLess(
            self.source.index("notebook.add(self.overview_tab"),
            self.source.index("notebook.add(self.exhibition_tab"),
        )
        self.assertIn("notebook.select(self.overview_tab)", self.source)

    def test_overview_cards_open_live_exhibition(self) -> None:
        self.assertIn("self.notebook.select(self.exhibition_tab)", self.source)
        self.assertIn("self.exhibit_body.select(self.exhibit_summary_tab)", self.source)

    def test_overview_has_scrollable_foyer_and_status_footer(self) -> None:
        self.assertIn("self.overview_status_var", self.source)
        self.assertIn("self._format_overview_status", self.source)
        self.assertIn("self.landing_canvas.itemconfigure", self.source)
        self.assertIn("_layout_overview_cards", self.source)

    def test_exhibition_tab_no_longer_contains_foyer_landing(self) -> None:
        self.assertNotIn("self._build_exhibition_landing", self.source)
        self.assertIn("self._build_foyer_overview", self.source)

    def test_summary_uses_scrollable_canvas_and_updates_scrollregion(self) -> None:
        self.assertIn("self.exhibit_summary_canvas", self.source)
        self.assertIn("scrollregion=self.exhibit_summary_canvas.bbox", self.source)
        self.assertIn("self.after_idle(self._update_exhibit_summary_scrollregion)", self.source)

    def test_large_summary_text_panel_was_removed(self) -> None:
        self.assertNotIn("self.exhibit_text = tk.Text", self.source)
        self.assertIn("summary no longer uses a large prose panel", self.source)

    def test_responsive_summary_stacks_at_small_width(self) -> None:
        self.assertIn("stacked = width < 980", self.source)
        self.assertIn("self.exhibit_visual_panel.grid_configure", self.source)
        self.assertIn("self.museum_label_panel.grid_configure", self.source)

    def test_visual_panel_has_image_and_placeholder_paths(self) -> None:
        self.assertIn("visual_resource_bytes", self.source)
        self.assertIn("_render_exhibit_visual_placeholder", self.source)
        self.assertIn("self.exhibit_visual_caption_var", self.source)

    def test_exhibit_poster_resize_is_debounced(self) -> None:
        self.assertIn("self._exhibit_visual_resize_job", self.source)
        self.assertIn("self.after_cancel(self._exhibit_visual_resize_job)", self.source)
        self.assertIn("self.after(120", self.source)


if __name__ == "__main__":
    unittest.main()
