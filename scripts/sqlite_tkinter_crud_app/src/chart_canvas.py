"""Tkinter chart rendering with matplotlib when available and Canvas fallback."""

from __future__ import annotations

import os
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .chart_models import PreparedChart
from .chart_service import chart_engine_info


class ChartRenderer:
    def __init__(self, parent: ttk.Frame) -> None:
        self.parent = parent
        self.canvas_widget: tk.Widget | None = None
        self.figure = None
        self.engine_info = chart_engine_info()

    def clear(self) -> None:
        if self.canvas_widget is not None:
            self.canvas_widget.destroy()
            self.canvas_widget = None
        self.figure = None

    def render(self, chart: PreparedChart) -> None:
        self.clear()
        if self.engine_info["selected_chart_engine"] == "matplotlib":
            self._render_matplotlib(chart)
        else:
            self._render_canvas(chart)

    def _render_matplotlib(self, chart: PreparedChart) -> None:
        os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="qsb_mpl_"))
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
        from matplotlib.figure import Figure  # type: ignore

        fig = Figure(figsize=(7.5, 4.6), dpi=100)
        ax = fig.add_subplot(111)
        title = chart.config.title or chart.config.chart_type.title()
        x_label = chart.config.x_label or chart.config.x_field
        y_label = chart.config.y_label or chart.config.y_field or "count"
        if chart.config.chart_type == "bar":
            ax.bar([str(x) for x in chart.x_values], chart.y_values)
        elif chart.config.chart_type == "line":
            ax.plot(chart.x_values, chart.y_values, marker="o", label=y_label)
        elif chart.config.chart_type == "scatter":
            ax.scatter(chart.x_values, chart.y_values, label=y_label)
        elif chart.config.chart_type == "pie":
            ax.pie(chart.y_values, labels=[str(x) for x in chart.x_values], autopct="%1.0f%%")
        elif chart.config.chart_type == "histogram":
            ax.hist(chart.y_values, bins=min(20, max(5, len(chart.y_values))))
        if chart.config.chart_type != "pie":
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
        ax.set_title(title)
        if chart.config.show_legend and chart.config.chart_type in {"line", "scatter"}:
            ax.legend()
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.parent)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.grid(row=0, column=0, sticky="nsew")
        self.figure = fig
        self.canvas_widget = widget

    def _render_canvas(self, chart: PreparedChart) -> None:
        canvas = tk.Canvas(self.parent, background="white")
        canvas.grid(row=0, column=0, sticky="nsew")
        width, height = 760, 420
        canvas.config(width=width, height=height)
        values = chart.y_values or [1.0]
        max_value = max(values) if values else 1.0
        max_value = max_value if max_value else 1.0
        canvas.create_text(width // 2, 20, text=chart.config.title or chart.config.chart_type.title(), font=("TkDefaultFont", 12, "bold"))
        if chart.config.chart_type == "scatter":
            xs = [float(x) for x in chart.x_values if _is_number(x)]
            ys = values[: len(xs)]
            if xs and ys:
                min_x, max_x = min(xs), max(xs)
                span_x = max(max_x - min_x, 1.0)
                for x, y in zip(xs, ys):
                    px = 60 + ((x - min_x) / span_x) * (width - 100)
                    py = height - 50 - (y / max_value) * (height - 100)
                    canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#356a9a", outline="")
        elif chart.config.chart_type == "line":
            points = []
            for idx, value in enumerate(values):
                px = 60 + idx * ((width - 100) / max(1, len(values) - 1))
                py = height - 50 - (value / max_value) * (height - 100)
                points.extend([px, py])
            if len(points) >= 4:
                canvas.create_line(*points, fill="#356a9a", width=2)
        else:
            bar_width = max(8, int((width - 100) / max(1, len(values))))
            for idx, value in enumerate(values):
                x0 = 50 + idx * bar_width
                y0 = height - 50 - (value / max_value) * (height - 100)
                canvas.create_rectangle(x0, y0, x0 + bar_width - 2, height - 50, fill="#5a7c8f", outline="")
        canvas.create_line(45, height - 50, width - 30, height - 50)
        canvas.create_line(50, 45, 50, height - 45)
        self.canvas_widget = canvas

    def export_image(self, path: Path) -> Path:
        if self.figure is not None:
            self.figure.savefig(path)
            return path
        if self.canvas_widget is None:
            raise RuntimeError("No chart rendered.")
        if path.suffix.lower() == ".svg":
            path.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"><text x=\"10\" y=\"20\">Canvas chart export placeholder</text></svg>\n", encoding="utf-8")
            return path
        raise RuntimeError("PNG export requires matplotlib.")


def _is_number(value) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
