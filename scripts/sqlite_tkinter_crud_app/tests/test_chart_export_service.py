from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chart_export_service import export_plotted_csv, write_chart_manifest
from src.chart_models import ChartConfig, PreparedChart


class ChartExportServiceTests(unittest.TestCase):
    def test_csv_and_manifest(self) -> None:
        chart = PreparedChart(
            config=ChartConfig("v_chart", "bar", "category", "value", language="en", title="Test"),
            rows=[{"category": "a", "value": 1.0}],
            x_values=["a"],
            y_values=[1.0],
            unit_metadata={"value": "resolved"},
            dimension_metadata={"value": "[0,0,0,0,0,0,0]"},
            chart_engine="matplotlib",
        )
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = export_plotted_csv(Path(tmp) / "chart.csv", chart)
            manifest_path = write_chart_manifest(
                csv_path,
                chart,
                {"snapshot_path": "snapshot.sqlite", "snapshot_sha256": "abc"},
                {"x": "Category", "y": "Value"},
            )
            self.assertTrue(csv_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_snapshot_sha256"], "abc")
            self.assertEqual(manifest["canonical_x_field"], "category")
            self.assertEqual(manifest["chart_engine"], "matplotlib")


if __name__ == "__main__":
    unittest.main()
