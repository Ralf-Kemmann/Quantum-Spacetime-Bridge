from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chart_models import ChartConfig
from src.chart_service import ChartError, ChartService, chart_engine_info, chart_presets, detect_categorical_fields, detect_numeric_fields, is_ordered_axis
from src.qsb_database import QSBMetadataDatabase
from src.snapshot_manager import sha256_file


def make_chart_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE meta_field(canonical_field_name TEXT, unit_status TEXT, dimension_status TEXT, dimension_vector TEXT);
        CREATE TABLE chart_data(idx INTEGER, category TEXT, value REAL, value2 REAL, negative REAL);
        CREATE VIEW v_chart AS SELECT idx, category, value, value2, negative FROM chart_data;
        INSERT INTO meta_field VALUES ('value', 'resolved', 'resolved', '[0,0,0,0,0,0,0]');
        INSERT INTO meta_field VALUES ('value2', 'resolved', 'other_dimension', '[1,0,0,0,0,0,0]');
        INSERT INTO chart_data VALUES (1, 'a', 2.0, 3.0, -1.0);
        INSERT INTO chart_data VALUES (2, 'b', 4.0, 5.0, 2.0);
        INSERT INTO chart_data VALUES (3, NULL, NULL, 6.0, 3.0);
        """
    )
    conn.commit()
    conn.close()


class ChartServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "chart.sqlite"
        make_chart_db(self.db_path)
        self.db = QSBMetadataDatabase(self.db_path)
        self.db.list_views()
        self.service = ChartService(self.db)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_numeric_categorical_and_ordered_detection(self) -> None:
        rows = self.db.load_view_page("v_chart").rows
        columns = self.db.columns_for_relation("v_chart")
        self.assertIn("value", detect_numeric_fields(rows, columns))
        self.assertIn("category", detect_categorical_fields(rows, columns))
        self.assertTrue(is_ordered_axis("idx", rows))

    def test_aggregation_and_null_handling(self) -> None:
        chart = self.service.prepare(ChartConfig("v_chart", "bar", "category", "value", aggregation="count"))
        self.assertEqual(chart.excluded_null_rows, 1)
        self.assertEqual(sum(chart.y_values), 2.0)

    def test_scatter_histogram_pie_and_line_safeguards(self) -> None:
        with self.assertRaises(ChartError):
            self.service.prepare(ChartConfig("v_chart", "scatter", "category", "value"))
        with self.assertRaises(ChartError):
            self.service.prepare(ChartConfig("v_chart", "histogram", "category"))
        with self.assertRaises(ChartError):
            self.service.prepare(ChartConfig("v_chart", "pie", "category", "negative"))
        with self.assertRaises(ChartError):
            self.service.prepare(ChartConfig("v_chart", "line", "category", "value"))

    def test_dimension_incompatibility_and_no_source_write(self) -> None:
        before = sha256_file(self.db_path)
        with self.assertRaises(ChartError):
            self.service.prepare(ChartConfig("v_chart", "bar", "idx", "value", y2_field="value2"))
        self.assertEqual(sha256_file(self.db_path), before)

    def test_presets_and_engine_info(self) -> None:
        self.assertTrue(chart_engine_info()["svg_export_available"])
        presets = chart_presets(["unit_status", "dimension_status"])
        self.assertTrue(any(preset["id"] == "fields_by_unit_status" for preset in presets))


if __name__ == "__main__":
    unittest.main()
