"""Tkinter GUI for the QSB Research Data Browser."""

from __future__ import annotations

import json
import logging
import tkinter as tk
from io import BytesIO
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

try:
    from PIL import Image, ImageTk
except ImportError:  # pragma: no cover - exercised only in installations without Pillow
    Image = None  # type: ignore[assignment]
    ImageTk = None  # type: ignore[assignment]

from .chart_canvas import ChartRenderer
from .chart_export_service import export_plotted_csv, write_chart_manifest
from .chart_models import AGGREGATIONS, CHART_TYPES, ChartConfig
from .chart_service import ChartError, ChartService, chart_engine_info, chart_presets
from .config import ALLOWED_PAGE_SIZES, APP_SUBTITLE_DE, APP_TITLE, PAGE_SIZE_DEFAULT
from .export_service import ExportError, export_rows_to_csv
from .exhibition_landing import (
    EXHIBIT_CARDS,
    LANDING_TEXT,
    image_resource_bytes,
    localized as landing_localized,
    overview_from_config,
    scale_to_fit,
    visual_from_exhibit,
    visual_resource_bytes,
)
from .exhibit_labels import MuseumLabel, resolve_museum_label
from .field_labels import FieldLabelResolver
from .language_service import LanguageService, save_language
from .metadata_search import MetadataSearchAdapter, SearchResult, group_results_by_source
from .qsb_database import QSBDatabaseError, QSBMetadataDatabase, ViewPage
from .showcase import (
    CONFIG_PATH,
    control_chart_config,
    cycle_control_counts,
    exhibit_by_id,
    filter_quantity_rows,
    group_result_rows,
    load_showcase_config,
    localized,
    phase_sequence,
    resolve_exhibit,
    resolve_reaction_scheme,
    validate_showcase_config,
    visible_fields,
)
from .showcase_style import BLUE, CYAN, DIVIDER, GOLD, MUTED, PANEL_BG, PANEL_BG_2, TEXT
from .ui_labels import VIEW_LABELS, label_for_identifier


LOGGER = logging.getLogger(__name__)
NULL_DISPLAY = "<NULL>"
MAX_CELL_LENGTH = 180
REQUIRED_GERMAN_VIEWS = list(VIEW_LABELS)


def display_value(value: Any) -> str:
    if value is None:
        return NULL_DISPLAY
    text = str(value)
    return text if len(text) <= MAX_CELL_LENGTH else text[: MAX_CELL_LENGTH - 1] + "…"


class QSBMetadataBrowser(tk.Tk):
    def __init__(self, database: QSBMetadataDatabase, language: str = "de") -> None:
        super().__init__()
        self.database = database
        self.field_label_resolver = FieldLabelResolver.from_database(database)
        self.language_service = LanguageService(language, field_label_resolver=self.field_label_resolver)
        self.search_adapter = MetadataSearchAdapter(database)
        self.chart_service = ChartService(database)
        self.views: list[str] = []
        self.tables: list[str] = []
        self.current_relation = ""
        self.current_columns: list[str] = []
        self.current_rows: list[dict[str, Any]] = []
        self.current_offset = 0
        self.current_total = 0
        self.current_sort = ""
        self.sort_descending = False
        self.search_results: list[SearchResult] = []
        self._search_iid_map: dict[str, SearchResult] = {}
        self._filter_column_display_map: dict[str, str] = {}
        self.prepared_chart = None
        self.showcase_config = load_showcase_config(CONFIG_PATH)
        validate_showcase_config(self.showcase_config)
        self.current_exhibit_id = self.showcase_config.get("default_exhibit_id", "causality07_reaction_cycle")
        self.overview_config = overview_from_config(self.showcase_config)
        self.exhibit_detail_trees: dict[str, ttk.Treeview] = {}
        self.exhibit_card_buttons: dict[str, tk.Frame] = {}
        self.exhibit_card_titles: dict[str, tk.Label] = {}
        self.exhibit_card_descriptions: dict[str, tk.Label] = {}
        self.exhibit_card_inventory: dict[str, tk.Label] = {}
        self.show_na_quantities_var = tk.BooleanVar(value=False)
        self._landing_image_original = None
        self._landing_photo = None
        self._exhibit_visual_original = None
        self._exhibit_visual_photo = None
        self._exhibit_visual_config = None
        self._exhibit_visual_cache: dict[str, Any] = {}
        self._exhibit_visual_resize_job: str | None = None
        self._summary_stacked = False

        self.title(APP_TITLE)
        self.geometry(self._load_geometry())
        self.minsize(1100, 700)
        self._create_variables()
        self._build_layout()
        self._bind_shortcuts()
        self.reload_catalog()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _geometry_file(self) -> Path:
        path = Path.home() / ".config" / "qsb_research_data_browser"
        path.mkdir(parents=True, exist_ok=True)
        return path / "geometry.txt"

    def _load_geometry(self) -> str:
        try:
            return self._geometry_file().read_text(encoding="utf-8").strip() or "1280x820"
        except OSError:
            return "1280x820"

    def _save_geometry(self) -> None:
        try:
            self._geometry_file().write_text(self.geometry(), encoding="utf-8")
        except OSError:
            LOGGER.exception("Could not save window geometry")

    def _create_variables(self) -> None:
        self.snapshot_path_var = tk.StringVar(value=str(self.database.database_path))
        self.source_path_var = tk.StringVar(value=str(self.database.manifest.get("source_database_path", "")))
        self.catalog_identity_var = tk.StringVar()
        self.catalog_mode_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Bereit")
        self.relation_var = tk.StringVar()
        self.page_size_var = tk.IntVar(value=PAGE_SIZE_DEFAULT)
        self.quick_filter_var = tk.StringVar()
        self.filter_column_var = tk.StringVar()
        self.filter_value_var = tk.StringVar()
        self.search_query_var = tk.StringVar()
        self.search_mart_var = tk.StringVar()
        self.search_wp_var = tk.StringVar()
        self.search_object_type_var = tk.StringVar()
        self.search_evidence_var = tk.StringVar()
        self.search_detail_var = tk.StringVar(value="")
        self.result_record_mart_filter_var = tk.StringVar()
        self.result_record_table_role_filter_var = tk.StringVar()
        self.result_record_text_filter_var = tk.StringVar()
        self.language_var = tk.StringVar(value="Deutsch" if self.language_service.language == "de" else "English")
        self.show_canonical_var = tk.BooleanVar(value=False)
        self.chart_source_var = tk.StringVar()
        self.chart_type_var = tk.StringVar(value="bar")
        self.chart_x_var = tk.StringVar()
        self.chart_y_var = tk.StringVar()
        self.chart_y2_var = tk.StringVar()
        self.chart_group_var = tk.StringVar()
        self.chart_aggregation_var = tk.StringVar(value="count")
        self.chart_max_rows_var = tk.IntVar(value=2000)
        self.chart_title_var = tk.StringVar()
        self.chart_status_var = tk.StringVar(value="")
        self.exhibit_title_var = tk.StringVar()
        self.exhibit_subtitle_var = tk.StringVar()
        self.exhibit_status_var = tk.StringVar()
        self.exhibit_facts_var = tk.StringVar()
        self.reaction_label_var = tk.StringVar()
        self.reaction_status_var = tk.StringVar()
        self.reaction_source_var = tk.StringVar()
        self.landing_caption_var = tk.StringVar()
        self.landing_image_note_var = tk.StringVar()
        self.landing_snapshot_status_var = tk.StringVar()
        self.overview_title_var = tk.StringVar()
        self.overview_subtitle_var = tk.StringVar()
        self.overview_intro_var = tk.StringVar()
        self.overview_image_caption_var = tk.StringVar()
        self.overview_status_var = tk.StringVar()
        self.exhibit_visual_caption_var = tk.StringVar()
        self.museum_label_title_var = tk.StringVar()
        self.museum_label_subtitle_var = tk.StringVar()
        self.museum_label_ribbon_var = tk.StringVar()
        self.museum_technical_visible_var = tk.BooleanVar(value=False)
        self.museum_technical_button_var = tk.StringVar()
        self.reaction_copy_text = ""

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=4)
        toolbar.columnconfigure(1, weight=1)
        toolbar.columnconfigure(5, weight=1)
        ttk.Label(toolbar, text=APP_TITLE, font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, padx=4, sticky="w")
        ttk.Label(toolbar, text=APP_SUBTITLE_DE).grid(row=0, column=1, padx=8, sticky="w")
        ttk.Label(toolbar, text=self.language_service.text("language")).grid(row=0, column=2, padx=4)
        self.language_combo = ttk.Combobox(toolbar, textvariable=self.language_var, values=("Deutsch", "English"), state="readonly", width=10)
        self.language_combo.grid(row=0, column=3, padx=4)
        self.language_combo.bind("<<ComboboxSelected>>", lambda _event: self.change_language())
        ttk.Checkbutton(toolbar, text="Canonical", variable=self.show_canonical_var, command=self.refresh_presentation_labels).grid(row=0, column=4, padx=4)
        ttk.Label(toolbar, textvariable=self.catalog_identity_var, anchor="e").grid(row=0, column=5, padx=8, sticky="e")
        ttk.Label(toolbar, textvariable=self.catalog_mode_var, anchor="e").grid(row=1, column=0, columnspan=6, padx=4, sticky="ew")
        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew")
        self.notebook = notebook
        self.overview_tab = ttk.Frame(notebook)
        self.exhibition_tab = ttk.Frame(notebook)
        self.expert_tab = ttk.Frame(notebook)
        notebook.add(self.overview_tab, text=landing_localized(self.overview_config.tab_title, self.language_service.language))
        notebook.add(self.exhibition_tab, text=self.language_service.text("exhibition"))
        notebook.add(self.expert_tab, text=self.language_service.text("expert_inspection"))
        self.expert_tab.columnconfigure(0, weight=1)
        self.expert_tab.rowconfigure(0, weight=1)
        expert_notebook = ttk.Notebook(self.expert_tab)
        expert_notebook.grid(row=0, column=0, sticky="nsew")
        self.expert_notebook = expert_notebook
        self.tabs = {name: ttk.Frame(expert_notebook) for name in [
            "Übersicht",
            "Forschungsansichten",
            "Marts & Work Packages",
            "Result Tables",
            "Result Records",
            "Metadatensuche",
            "Diagramme",
            "Herkunft / Lineage",
            "Validierungen",
            "Claims und Ergebnisse",
            "Offene Prüfpunkte",
            "Datenbankinfo",
        ]}
        for name, frame in self.tabs.items():
            expert_notebook.add(frame, text=name)
        self._build_foyer_overview()
        self._build_exhibition()
        self._build_overview()
        self._build_views_tab()
        self._build_generic_marts_tab()
        self._build_generic_result_tables_tab()
        self._build_generic_result_records_tab()
        self._build_search_tab()
        self._build_charts_tab()
        self._build_relation_tab("Herkunft / Lineage", ["v_de_lineage", "meta_lineage", "meta_record_lineage"])
        self._build_relation_tab("Validierungen", ["v_de_validierungsergebnisse", "meta_validation_result", "meta_validation_rule"])
        self._build_relation_tab("Claims und Ergebnisse", ["v_de_ergebnis_claim_beziehungen", "meta_claim", "meta_claim_result_link", "meta_result_record"])
        self._build_relation_tab("Offene Prüfpunkte", ["v_de_offene_pruefpunkte", "meta_validation_result", "v_de_physikalische_groessen"])
        self._build_db_info()
        ttk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken").grid(row=2, column=0, sticky="ew")
        notebook.select(self.overview_tab)

    def _build_exhibition(self) -> None:
        tab = self.exhibition_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        live = ttk.Frame(tab)
        live.grid(row=0, column=0, padx=8, pady=4, sticky="nsew")
        live.columnconfigure(0, weight=1)
        live.rowconfigure(1, weight=1)
        self.exhibition_live_frame = live

        tab = live
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        header = ttk.Frame(tab)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, textvariable=self.exhibit_title_var, font=("TkDefaultFont", 15, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.exhibit_subtitle_var, wraplength=900, justify="left").grid(row=1, column=0, pady=4, sticky="ew")
        ttk.Label(header, textvariable=self.exhibit_status_var, wraplength=900, justify="left").grid(row=2, column=0, sticky="ew")

        body = ttk.Notebook(tab)
        body.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.exhibit_body = body
        self.exhibit_summary_tab = ttk.Frame(body)
        self.exhibit_table_tab = ttk.Frame(body)
        self.exhibit_chart_tab = ttk.Frame(body)
        body.add(self.exhibit_summary_tab, text="Exponat")
        body.add(self.exhibit_table_tab, text="Daten")
        body.add(self.exhibit_chart_tab, text="Diagramm")

        self.exhibit_summary_tab.columnconfigure(0, weight=1)
        self.exhibit_summary_tab.rowconfigure(0, weight=1)
        self._build_exhibit_summary_scroll_frame()
        summary = self.exhibit_summary_content
        summary.columnconfigure(0, weight=1)
        summary.columnconfigure(1, weight=1)

        self._build_exhibit_visual_panel(summary)
        self._build_museum_label_panel(summary)
        reaction_frame = ttk.LabelFrame(summary, text="")
        reaction_frame.grid(row=1, column=0, columnspan=2, padx=12, pady=10, sticky="ew")
        self.reaction_frame = reaction_frame
        reaction_frame.columnconfigure(0, weight=1)
        ttk.Label(reaction_frame, textvariable=self.reaction_status_var, font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=0, padx=8, pady=4, sticky="w"
        )
        self.reaction_text = tk.Text(reaction_frame, wrap="word", height=5, font=("TkFixedFont", 12))
        self.reaction_text.grid(row=1, column=0, columnspan=3, padx=8, pady=5, sticky="ew")
        ttk.Label(reaction_frame, textvariable=self.reaction_source_var, wraplength=840, justify="left").grid(
            row=2, column=0, padx=8, pady=4, sticky="ew"
        )
        ttk.Button(reaction_frame, text="Kopieren", command=self.copy_reaction_scheme).grid(row=2, column=1, padx=4, pady=4)
        ttk.Button(reaction_frame, text="Quelle", command=self.copy_reaction_source).grid(row=2, column=2, padx=4, pady=4)
        self.exhibit_facts_label = ttk.Label(summary, textvariable=self.exhibit_facts_var, wraplength=920, justify="left")
        self.exhibit_facts_label.grid(
            row=2, column=0, columnspan=2, padx=12, pady=10, sticky="ew"
        )

        self.exhibit_table_tab.columnconfigure(0, weight=1)
        self.exhibit_table_tab.rowconfigure(1, weight=1)
        self.show_na_check = ttk.Checkbutton(
            self.exhibit_table_tab,
            text="Nicht anwendbare Felder zeigen",
            variable=self.show_na_quantities_var,
            command=self.refresh_current_exhibit,
        )
        self.show_na_check.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        table_frame = ttk.Frame(self.exhibit_table_tab)
        table_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.exhibit_tree = ttk.Treeview(table_frame, show="headings")
        self.exhibit_tree.grid(row=0, column=0, sticky="nsew")
        ttk.Scrollbar(table_frame, orient="vertical", command=self.exhibit_tree.yview).grid(row=0, column=1, sticky="ns")
        ttk.Scrollbar(table_frame, orient="horizontal", command=self.exhibit_tree.xview).grid(row=1, column=0, sticky="ew")

        self.exhibit_chart_tab.columnconfigure(0, weight=1)
        self.exhibit_chart_tab.rowconfigure(1, weight=1)
        actions = ttk.Frame(self.exhibit_chart_tab)
        actions.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(actions, text="Diagramm aus Auswahl", command=self.open_chart_from_exhibit).grid(row=0, column=0, padx=4)
        self.exhibit_chart_status_var = tk.StringVar()
        ttk.Label(actions, textvariable=self.exhibit_chart_status_var).grid(row=0, column=1, padx=8, sticky="w")
        chart_frame = ttk.Frame(self.exhibit_chart_tab)
        chart_frame.grid(row=1, column=0, padx=10, pady=8, sticky="nsew")
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        self.exhibit_chart_renderer = ChartRenderer(chart_frame)
        self.refresh_landing_labels()

    def _build_exhibit_summary_scroll_frame(self) -> None:
        canvas = tk.Canvas(self.exhibit_summary_tab, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.exhibit_summary_tab, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        content = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")
        self.exhibit_summary_canvas = canvas
        self.exhibit_summary_window_id = window_id
        self.exhibit_summary_content = content
        content.bind("<Configure>", lambda _event: self._update_exhibit_summary_scrollregion())
        canvas.bind("<Configure>", lambda event: self._on_exhibit_summary_canvas_configure(event.width))

    def _build_exhibit_visual_panel(self, parent: ttk.Frame) -> None:
        panel = tk.Frame(parent, bg=PANEL_BG, highlightbackground=BLUE, highlightthickness=1, bd=0)
        panel.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        self.exhibit_visual_panel = panel
        tk.Label(panel, text="VISUAL", bg=PANEL_BG_2, fg=GOLD, anchor="w", padx=10, pady=4).grid(row=0, column=0, sticky="ew")
        self.exhibit_visual_image_label = tk.Label(panel, bg=PANEL_BG, fg=TEXT, anchor="center", justify="center")
        self.exhibit_visual_image_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.exhibit_visual_canvas = tk.Canvas(panel, height=230, bg=PANEL_BG, highlightthickness=0)
        self.exhibit_visual_canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.exhibit_visual_canvas.grid_remove()
        tk.Label(
            panel,
            textvariable=self.exhibit_visual_caption_var,
            bg=PANEL_BG,
            fg=MUTED,
            anchor="w",
            justify="left",
            wraplength=520,
            padx=10,
            pady=8,
        ).grid(row=2, column=0, sticky="ew")

    def _update_exhibit_summary_scrollregion(self) -> None:
        self.exhibit_summary_canvas.configure(scrollregion=self.exhibit_summary_canvas.bbox("all"))

    def _on_exhibit_summary_canvas_configure(self, width: int) -> None:
        self.exhibit_summary_canvas.itemconfigure(self.exhibit_summary_window_id, width=max(1, width - 20))
        stacked = width < 980
        if stacked != self._summary_stacked:
            self._summary_stacked = stacked
            self._place_summary_primary_panels(stacked)
        if self._exhibit_visual_resize_job:
            self.after_cancel(self._exhibit_visual_resize_job)
        self._exhibit_visual_resize_job = self.after(120, lambda: self._render_exhibit_visual(max_width=width - 80))
        self._update_exhibit_summary_scrollregion()

    def _place_summary_primary_panels(self, stacked: bool) -> None:
        if stacked:
            self.exhibit_visual_panel.grid_configure(row=0, column=0, columnspan=2, sticky="ew")
            self.museum_label_panel.grid_configure(row=1, column=0, columnspan=2, sticky="ew")
            self.reaction_frame.grid_configure(row=2, column=0, columnspan=2)
            self.exhibit_facts_label.grid_configure(row=3, column=0, columnspan=2)
        else:
            self.exhibit_visual_panel.grid_configure(row=0, column=0, columnspan=1, sticky="nsew")
            self.museum_label_panel.grid_configure(row=0, column=1, columnspan=1, sticky="nsew")
            self.reaction_frame.grid_configure(row=1, column=0, columnspan=2)
            self.exhibit_facts_label.grid_configure(row=2, column=0, columnspan=2)

    def _build_museum_label_panel(self, parent: ttk.Frame) -> None:
        panel = tk.Frame(parent, bg=PANEL_BG, highlightbackground=CYAN, highlightthickness=1, bd=0)
        panel.grid(row=0, column=1, padx=12, pady=(10, 4), sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(4, weight=1)
        self.museum_label_panel = panel

        ribbon = tk.Label(panel, textvariable=self.museum_label_ribbon_var, bg=PANEL_BG_2, fg=GOLD, anchor="w", padx=10, pady=4)
        ribbon.grid(row=0, column=0, columnspan=2, sticky="ew")
        title = tk.Label(panel, textvariable=self.museum_label_title_var, bg=PANEL_BG, fg=TEXT, font=("TkDefaultFont", 13, "bold"), anchor="w")
        title.grid(row=1, column=0, columnspan=2, padx=10, pady=(8, 1), sticky="ew")
        subtitle = tk.Label(panel, textvariable=self.museum_label_subtitle_var, bg=PANEL_BG, fg=MUTED, anchor="w", justify="left", wraplength=900)
        subtitle.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")
        divider = tk.Frame(panel, bg=DIVIDER, height=1)
        divider.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10)
        self.museum_fields_frame = tk.Frame(panel, bg=PANEL_BG)
        self.museum_fields_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=8, sticky="ew")
        self.museum_fields_frame.columnconfigure(1, weight=1)
        self.museum_technical_button = ttk.Button(panel, textvariable=self.museum_technical_button_var, command=self.toggle_museum_technical)
        self.museum_technical_button.grid(row=5, column=0, padx=10, pady=(0, 8), sticky="w")
        self.museum_technical_text = tk.Text(panel, height=5, wrap="word", bg="#06111f", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.museum_technical_text.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.museum_technical_text.grid_remove()

    def _build_foyer_overview(self) -> None:
        tab = self.overview_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        canvas = tk.Canvas(tab, bg="#040d19", highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scroll.set)
        content = tk.Frame(canvas, bg="#040d19")
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")
        self.landing_canvas = canvas
        self.landing_window_id = window_id
        content.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: self._on_landing_canvas_configure(event.width))

        content.columnconfigure(0, weight=1)
        hero = tk.Frame(content, bg="#040d19")
        hero.grid(row=0, column=0, padx=26, pady=(24, 10), sticky="ew")
        hero.columnconfigure(0, weight=1)
        tk.Label(hero, textvariable=self.overview_title_var, bg="#040d19", fg=TEXT, font=("TkDefaultFont", 24, "bold"), anchor="w").grid(
            row=0, column=0, sticky="ew"
        )
        tk.Label(hero, textvariable=self.overview_subtitle_var, bg="#040d19", fg=MUTED, font=("TkDefaultFont", 13), anchor="w").grid(
            row=1, column=0, pady=(4, 0), sticky="ew"
        )

        image_box = tk.Frame(content, bg=PANEL_BG, highlightbackground=CYAN, highlightthickness=1, bd=0)
        image_box.grid(row=1, column=0, padx=26, pady=12, sticky="ew")
        image_box.columnconfigure(0, weight=1)
        self.landing_image_label = tk.Label(image_box, bg=PANEL_BG, fg=TEXT, anchor="center", justify="center")
        self.landing_image_label.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        tk.Label(
            image_box,
            textvariable=self.overview_image_caption_var,
            bg=PANEL_BG,
            fg=MUTED,
            wraplength=980,
            justify="left",
            anchor="w",
            padx=12,
        ).grid(row=1, column=0, pady=(0, 10), sticky="ew")

        tk.Label(
            content,
            textvariable=self.overview_intro_var,
            bg="#040d19",
            fg=TEXT,
            font=("TkDefaultFont", 13),
            wraplength=980,
            justify="left",
            anchor="w",
        ).grid(row=2, column=0, padx=26, pady=(4, 14), sticky="ew")

        cards = tk.Frame(content, bg="#040d19")
        cards.grid(row=3, column=0, padx=22, pady=6, sticky="ew")
        self.overview_cards_frame = cards
        for column in range(5):
            cards.columnconfigure(column, weight=1)
        for idx, exhibit_id in enumerate(self.overview_config.exhibit_card_order):
            self._build_overview_card(cards, exhibit_id, idx)

        footer = tk.Frame(content, bg=PANEL_BG_2, highlightbackground=DIVIDER, highlightthickness=1, bd=0)
        footer.grid(row=4, column=0, padx=26, pady=(16, 26), sticky="ew")
        footer.columnconfigure(0, weight=1)
        tk.Label(
            footer,
            textvariable=self.overview_status_var,
            bg=PANEL_BG_2,
            fg=MUTED,
            anchor="w",
            justify="left",
            wraplength=1000,
            padx=12,
            pady=8,
        ).grid(row=0, column=0, sticky="ew")
        self._load_landing_image()
        self.refresh_landing_labels()

    def _build_overview_card(self, parent: tk.Frame, exhibit_id: str, index: int) -> None:
        card = tk.Frame(parent, bg=PANEL_BG, highlightbackground=DIVIDER, highlightthickness=1, bd=0, takefocus=1)
        card.grid(row=0, column=index, padx=4, pady=4, sticky="nsew")
        card.columnconfigure(0, weight=1)
        inventory = tk.Label(card, bg=PANEL_BG, fg=GOLD, anchor="w", font=("TkDefaultFont", 9, "bold"))
        inventory.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="ew")
        title = tk.Label(card, bg=PANEL_BG, fg=TEXT, anchor="w", justify="left", wraplength=190, font=("TkDefaultFont", 11, "bold"))
        title.grid(row=1, column=0, padx=10, pady=(0, 4), sticky="ew")
        desc = tk.Label(card, bg=PANEL_BG, fg=MUTED, anchor="nw", justify="left", wraplength=190)
        desc.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.exhibit_card_buttons[exhibit_id] = card
        self.exhibit_card_inventory[exhibit_id] = inventory
        self.exhibit_card_titles[exhibit_id] = title
        self.exhibit_card_descriptions[exhibit_id] = desc
        for widget in (card, inventory, title, desc):
            widget.bind("<Button-1>", lambda _event, selected=exhibit_id: self.open_exhibit_card(selected))
        card.bind("<Return>", lambda _event, selected=exhibit_id: self.open_exhibit_card(selected))
        card.bind("<space>", lambda _event, selected=exhibit_id: self.open_exhibit_card(selected))
        card.bind("<Left>", lambda _event, delta=-1: self.focus_exhibit_card(delta))
        card.bind("<Right>", lambda _event, delta=1: self.focus_exhibit_card(delta))
        card.bind("<Up>", lambda _event, delta=-1: self.focus_exhibit_card(delta))
        card.bind("<Down>", lambda _event, delta=1: self.focus_exhibit_card(delta))
        card.bind("<Enter>", lambda _event, selected=exhibit_id: self._set_overview_card_state(selected, hover=True))
        card.bind("<Leave>", lambda _event, selected=exhibit_id: self._set_overview_card_state(selected, hover=False))
        card.bind("<FocusIn>", lambda _event, selected=exhibit_id: self._set_overview_card_state(selected, focus=True))
        card.bind("<FocusOut>", lambda _event, selected=exhibit_id: self._set_overview_card_state(selected, focus=False))

    def _load_landing_image(self) -> None:
        data = visual_resource_bytes(self.overview_config.image_resource) if self.overview_config.image_resource else image_resource_bytes()
        if data is None or Image is None or ImageTk is None:
            self._landing_image_original = None
            self.landing_image_label.configure(text=landing_localized(self.overview_config.fallback_text, self.language_service.language), image="")
            return
        try:
            image = Image.open(BytesIO(data))
            image.load()
            self._landing_image_original = image
            self._render_landing_image()
        except Exception:
            LOGGER.exception("Could not decode exhibition overview image")
            self._landing_image_original = None
            self.landing_image_label.configure(text=landing_localized(self.overview_config.fallback_text, self.language_service.language), image="")

    def _on_landing_canvas_configure(self, width: int) -> None:
        self.landing_canvas.itemconfigure(self.landing_window_id, width=max(1, width - 24))
        self._layout_overview_cards(width)
        self._render_landing_image(max_width=max(320, width - 90))

    def _render_landing_image(self, max_width: int = 900) -> None:
        if self._landing_image_original is None:
            return
        width, height = scale_to_fit(self._landing_image_original.width, self._landing_image_original.height, max_width, 430)
        if width <= 0 or height <= 0:
            return
        resized = self._landing_image_original.resize((width, height), Image.Resampling.LANCZOS)
        self._landing_photo = ImageTk.PhotoImage(resized)
        self.landing_image_label.configure(image=self._landing_photo, text="")

    def _layout_overview_cards(self, width: int) -> None:
        if not hasattr(self, "overview_cards_frame"):
            return
        columns = 1 if width < 720 else 2 if width < 1040 else 5
        for idx, exhibit_id in enumerate(self.overview_config.exhibit_card_order):
            card = self.exhibit_card_buttons.get(exhibit_id)
            if card:
                card.grid_configure(row=idx // columns, column=idx % columns)
        for column in range(5):
            self.overview_cards_frame.columnconfigure(column, weight=1 if column < columns else 0)

    def _set_overview_card_state(self, exhibit_id: str, hover: bool | None = None, focus: bool | None = None) -> None:
        card = self.exhibit_card_buttons.get(exhibit_id)
        if not card:
            return
        if hover is not None:
            setattr(card, "_qsb_hover", hover)
        if focus is not None:
            setattr(card, "_qsb_focus", focus)
        active = exhibit_id == self.current_exhibit_id
        highlighted = bool(getattr(card, "_qsb_hover", False) or getattr(card, "_qsb_focus", False) or active)
        card.configure(highlightbackground=GOLD if highlighted else DIVIDER, highlightthickness=2 if highlighted else 1)
        for widget in (card, self.exhibit_card_inventory[exhibit_id], self.exhibit_card_titles[exhibit_id], self.exhibit_card_descriptions[exhibit_id]):
            widget.configure(bg=PANEL_BG_2 if highlighted else PANEL_BG)

    def _load_exhibit_visual(self, exhibit: dict[str, Any]) -> None:
        visual = visual_from_exhibit(exhibit)
        self._exhibit_visual_config = visual
        language = self.language_service.language
        data = visual_resource_bytes(visual.image_resource) if visual.image_resource else None
        if data is None or Image is None or ImageTk is None:
            self._exhibit_visual_original = None
            self.exhibit_visual_caption_var.set(landing_localized(visual.fallback_caption, language))
            self.exhibit_visual_image_label.configure(text=landing_localized(visual.image_alt, language))
            self._render_exhibit_visual_placeholder()
            return
        try:
            image = self._exhibit_visual_cache.get(visual.image_resource)
            if image is None:
                image = Image.open(BytesIO(data))
                image.load()
                self._exhibit_visual_cache[visual.image_resource] = image
            self._exhibit_visual_original = image
            self.exhibit_visual_caption_var.set(landing_localized(visual.caption, language))
            self._render_exhibit_visual()
        except Exception:
            LOGGER.exception("Could not decode exhibit visual resource")
            self._exhibit_visual_original = None
            self.exhibit_visual_caption_var.set(landing_localized(visual.fallback_caption, language))
            self.exhibit_visual_image_label.configure(text=landing_localized(visual.image_alt, language))
            self._render_exhibit_visual_placeholder()

    def _render_exhibit_visual(self, max_width: int = 520) -> None:
        if self._exhibit_visual_original is None:
            self._render_exhibit_visual_placeholder()
            return
        self.exhibit_visual_canvas.grid_remove()
        self.exhibit_visual_image_label.grid()
        visual = self._exhibit_visual_config
        configured_width = visual.image_max_width if visual else 760
        configured_height = visual.image_max_height if visual else 520
        width, height = scale_to_fit(
            self._exhibit_visual_original.width,
            self._exhibit_visual_original.height,
            min(max_width, configured_width),
            configured_height,
        )
        if width <= 0 or height <= 0:
            return
        resized = self._exhibit_visual_original.resize((width, height), Image.Resampling.LANCZOS)
        self._exhibit_visual_photo = ImageTk.PhotoImage(resized)
        alt = landing_localized(visual.image_alt, self.language_service.language) if visual else ""
        self.exhibit_visual_image_label.configure(image=self._exhibit_visual_photo, text="", width=width, height=height)
        self.exhibit_visual_image_label._qsb_alt_text = alt

    def _render_exhibit_visual_placeholder(self) -> None:
        self.exhibit_visual_image_label.grid_remove()
        self.exhibit_visual_canvas.grid()
        canvas = self.exhibit_visual_canvas
        canvas.delete("all")
        width = max(360, canvas.winfo_width() or 520)
        height = 230
        canvas.configure(height=height)
        language = self.language_service.language
        exhibit = exhibit_by_id(self.showcase_config, self.current_exhibit_id)
        title = localized(exhibit["title"], language)
        canvas.create_rectangle(10, 10, width - 10, height - 10, outline=DIVIDER, fill=PANEL_BG_2, width=1)
        colors = [CYAN, BLUE, GOLD]
        points = [(70, 76), (width // 2, 48), (width - 80, 94), (width // 2 + 40, 164), (100, 152)]
        for start, end in zip(points, points[1:] + points[:1]):
            canvas.create_line(start[0], start[1], end[0], end[1], fill=DIVIDER, width=2)
        for idx, (x, y) in enumerate(points):
            canvas.create_oval(x - 17, y - 17, x + 17, y + 17, outline=colors[idx % len(colors)], width=2, fill=PANEL_BG)
        canvas.create_text(28, height - 46, anchor="w", fill=TEXT, font=("TkDefaultFont", 12, "bold"), text=title, width=width - 56)
        note = "Platzhalter-Visual" if language == "de" else "Placeholder visual"
        canvas.create_text(28, height - 24, anchor="w", fill=MUTED, font=("TkDefaultFont", 10), text=note, width=width - 56)

    def _build_overview(self) -> None:
        frame = self.tabs["Übersicht"]
        frame.columnconfigure(0, weight=1)
        text = tk.Text(frame, wrap="word", height=28)
        text.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        self.overview_text = text

    def _build_views_tab(self) -> None:
        tab = self.tabs["Forschungsansichten"]
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)

        controls = ttk.LabelFrame(tab, text="Forschungsansichten")
        controls.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Ansicht").grid(row=0, column=0, padx=6, pady=5, sticky="w")
        self.relation_combo = ttk.Combobox(controls, textvariable=self.relation_var, state="readonly")
        self.relation_combo.grid(row=0, column=1, padx=6, pady=5, sticky="ew")
        self.relation_combo.bind("<<ComboboxSelected>>", lambda _event: self.open_selected_relation())
        ttk.Label(controls, text="Seitengröße").grid(row=0, column=2, padx=6, pady=5)
        ttk.Combobox(controls, textvariable=self.page_size_var, values=ALLOWED_PAGE_SIZES, state="readonly", width=8).grid(
            row=0, column=3, padx=6, pady=5
        )
        ttk.Button(controls, text="Aktualisieren", command=self.reload_catalog).grid(row=0, column=4, padx=6, pady=5)

        filters = ttk.LabelFrame(tab, text="Filter in aktueller Ansicht")
        filters.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        filters.columnconfigure(1, weight=1)
        filters.columnconfigure(4, weight=1)
        ttk.Label(filters, text="Schnellfilter").grid(row=0, column=0, padx=6, pady=5)
        ttk.Entry(filters, textvariable=self.quick_filter_var).grid(row=0, column=1, padx=6, pady=5, sticky="ew")
        ttk.Label(filters, text="Spalte").grid(row=0, column=2, padx=6, pady=5)
        self.filter_column_combo = ttk.Combobox(filters, textvariable=self.filter_column_var, state="readonly", width=22)
        self.filter_column_combo.grid(row=0, column=3, padx=6, pady=5)
        ttk.Entry(filters, textvariable=self.filter_value_var).grid(row=0, column=4, padx=6, pady=5, sticky="ew")
        ttk.Button(filters, text="Anwenden", command=self.apply_filter).grid(row=0, column=5, padx=6, pady=5)
        ttk.Button(filters, text="Zurücksetzen", command=self.clear_filter).grid(row=0, column=6, padx=6, pady=5)

        table_frame = ttk.Frame(tab)
        table_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.view_tree = ttk.Treeview(table_frame, show="headings")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.view_tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.view_tree.xview)
        self.view_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.view_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        actions = ttk.Frame(tab)
        actions.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        for idx, (label, command) in enumerate([
            ("Erste Seite", self.first_page),
            ("Vorherige", self.previous_page),
            ("Nächste", self.next_page),
            ("Letzte Seite", self.last_page),
            ("Zelle kopieren", self.copy_selected_cell),
            ("Zeile kopieren", self.copy_selected_row),
            ("Seite als CSV exportieren", self.export_current_page),
        ]):
            ttk.Button(actions, text=label, command=command).grid(row=0, column=idx, padx=3)

    def _build_generic_marts_tab(self) -> None:
        frame = self.tabs["Marts & Work Packages"]
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        ttk.Label(
            frame,
            text="Generische read-only Übersicht aus meta_mart und meta_work_package.",
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.generic_marts_tree = ttk.Treeview(frame, show="headings")
        self.generic_marts_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        ttk.Scrollbar(frame, orient="vertical", command=self.generic_marts_tree.yview).grid(row=1, column=1, sticky="ns")
        ttk.Scrollbar(frame, orient="horizontal", command=self.generic_marts_tree.xview).grid(row=2, column=0, sticky="ew")

    def _build_generic_result_tables_tab(self) -> None:
        frame = self.tabs["Result Tables"]
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        ttk.Label(
            frame,
            text="Generische read-only Übersicht aller registrierten Result Tables.",
        ).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.generic_result_tables_tree = ttk.Treeview(frame, show="headings")
        self.generic_result_tables_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        ttk.Scrollbar(frame, orient="vertical", command=self.generic_result_tables_tree.yview).grid(row=1, column=1, sticky="ns")
        ttk.Scrollbar(frame, orient="horizontal", command=self.generic_result_tables_tree.xview).grid(row=2, column=0, sticky="ew")

    def _build_generic_result_records_tab(self) -> None:
        frame = self.tabs["Result Records"]
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        controls = ttk.LabelFrame(frame, text="Result Records")
        controls.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)
        controls.columnconfigure(5, weight=1)
        ttk.Label(controls, text="Mart").grid(row=0, column=0, padx=5, pady=5)
        self.result_record_mart_combo = ttk.Combobox(controls, textvariable=self.result_record_mart_filter_var, state="normal")
        self.result_record_mart_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(controls, text="Tabellenrolle").grid(row=0, column=2, padx=5, pady=5)
        self.result_record_table_role_combo = ttk.Combobox(controls, textvariable=self.result_record_table_role_filter_var, state="normal")
        self.result_record_table_role_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ttk.Label(controls, text="Freitext").grid(row=0, column=4, padx=5, pady=5)
        ttk.Entry(controls, textvariable=self.result_record_text_filter_var).grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        ttk.Button(controls, text="Filtern", command=self.populate_generic_result_records).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(controls, text="QSB-CORRCORE01", command=self.apply_corrcore_quick_filter).grid(row=0, column=7, padx=5, pady=5)
        ttk.Button(controls, text="Zurücksetzen", command=self.clear_result_record_filters).grid(row=0, column=8, padx=5, pady=5)

        self.generic_result_records_tree = ttk.Treeview(frame, show="headings")
        self.generic_result_records_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        ttk.Scrollbar(frame, orient="vertical", command=self.generic_result_records_tree.yview).grid(row=1, column=1, sticky="ns")
        ttk.Scrollbar(frame, orient="horizontal", command=self.generic_result_records_tree.xview).grid(row=2, column=0, sticky="ew")

    def _build_search_tab(self) -> None:
        tab = self.tabs["Metadatensuche"]
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        controls = ttk.LabelFrame(tab, text="Strukturierte Metadatensuche")
        controls.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Suchbegriffe").grid(row=0, column=0, padx=6, pady=5)
        ttk.Entry(controls, textvariable=self.search_query_var).grid(row=0, column=1, padx=6, pady=5, sticky="ew")
        for idx, (label, var) in enumerate([
            ("Mart", self.search_mart_var),
            ("Arbeitspaket", self.search_wp_var),
            ("Objekttyp", self.search_object_type_var),
            ("Evidenz", self.search_evidence_var),
        ], start=2):
            ttk.Label(controls, text=label).grid(row=0, column=idx * 2 - 2, padx=4, pady=5)
            ttk.Entry(controls, textvariable=var, width=14).grid(row=0, column=idx * 2 - 1, padx=4, pady=5)
        ttk.Button(controls, text="Suchen", command=self.run_metadata_search).grid(row=1, column=0, padx=6, pady=5)
        ttk.Button(controls, text="Zurücksetzen", command=self.reset_metadata_search).grid(row=1, column=1, padx=6, pady=5, sticky="w")
        ttk.Button(controls, text="Quelle öffnen", command=self.open_search_source).grid(row=1, column=2, padx=6, pady=5)

        result_frame = ttk.Frame(tab)
        result_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        columns = ("source", "matched_field", "matched_value", "field_name", "label_or_alias", "unit", "dimension", "evidence_status", "related_view")
        self.search_tree = ttk.Treeview(result_frame, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.search_tree.heading(column, text=self.field_label_resolver.display_label(column))
            self.search_tree.column(column, width=150, minwidth=90, anchor="w")
        self.search_tree.grid(row=0, column=0, sticky="nsew")
        ttk.Scrollbar(result_frame, orient="vertical", command=self.search_tree.yview).grid(row=0, column=1, sticky="ns")
        ttk.Scrollbar(result_frame, orient="horizontal", command=self.search_tree.xview).grid(row=1, column=0, sticky="ew")
        self.search_tree.bind("<<TreeviewSelect>>", lambda _event: self.update_search_detail())
        self.search_tree.bind("<Double-1>", lambda _event: self.open_search_source())
        ttk.Label(tab, textvariable=self.search_detail_var, wraplength=1100, justify="left").grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    def _build_charts_tab(self) -> None:
        tab = self.tabs["Diagramme"]
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        controls = ttk.LabelFrame(tab, text=self.language_service.text("charts"))
        controls.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        for idx in range(8):
            controls.columnconfigure(idx, weight=1 if idx in {1, 3, 5, 7} else 0)
        ttk.Label(controls, text="Source").grid(row=0, column=0, padx=4, pady=4)
        self.chart_source_combo = ttk.Combobox(controls, textvariable=self.chart_source_var, state="readonly")
        self.chart_source_combo.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.chart_source_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_chart_fields())
        ttk.Label(controls, text="Type").grid(row=0, column=2, padx=4, pady=4)
        ttk.Combobox(controls, textvariable=self.chart_type_var, values=CHART_TYPES, state="readonly").grid(row=0, column=3, padx=4, pady=4)
        ttk.Label(controls, text="X").grid(row=1, column=0, padx=4, pady=4)
        self.chart_x_combo = ttk.Combobox(controls, textvariable=self.chart_x_var, state="readonly")
        self.chart_x_combo.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        ttk.Label(controls, text="Y").grid(row=1, column=2, padx=4, pady=4)
        self.chart_y_combo = ttk.Combobox(controls, textvariable=self.chart_y_var, state="readonly")
        self.chart_y_combo.grid(row=1, column=3, padx=4, pady=4, sticky="ew")
        ttk.Label(controls, text="Group").grid(row=1, column=4, padx=4, pady=4)
        self.chart_group_combo = ttk.Combobox(controls, textvariable=self.chart_group_var, state="readonly")
        self.chart_group_combo.grid(row=1, column=5, padx=4, pady=4, sticky="ew")
        ttk.Label(controls, text="Aggregation").grid(row=1, column=6, padx=4, pady=4)
        ttk.Combobox(controls, textvariable=self.chart_aggregation_var, values=AGGREGATIONS, state="readonly").grid(row=1, column=7, padx=4, pady=4)
        ttk.Label(controls, text="Title").grid(row=2, column=0, padx=4, pady=4)
        ttk.Entry(controls, textvariable=self.chart_title_var).grid(row=2, column=1, columnspan=3, padx=4, pady=4, sticky="ew")
        ttk.Label(controls, text="Max rows").grid(row=2, column=4, padx=4, pady=4)
        ttk.Entry(controls, textvariable=self.chart_max_rows_var, width=8).grid(row=2, column=5, padx=4, pady=4)
        ttk.Button(controls, text=self.language_service.text("generate_chart"), command=self.generate_chart).grid(row=2, column=6, padx=4, pady=4)
        ttk.Button(controls, text=self.language_service.text("export_chart"), command=self.export_chart).grid(row=2, column=7, padx=4, pady=4)
        self.chart_info_label = ttk.Label(tab, textvariable=self.chart_status_var, wraplength=1100, justify="left")
        self.chart_info_label.grid(row=1, column=0, padx=10, pady=4, sticky="ew")
        chart_frame = ttk.Frame(tab)
        chart_frame.grid(row=2, column=0, padx=10, pady=8, sticky="nsew")
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        self.chart_renderer = ChartRenderer(chart_frame)

    def _build_relation_tab(self, tab_name: str, preferred_relations: list[str]) -> None:
        frame = self.tabs[tab_name]
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        ttk.Label(frame, text="Geführte, lesende Katalogansicht. Vollständigkeit hängt vom Kataloginhalt ab.").grid(
            row=0, column=0, padx=10, pady=8, sticky="w"
        )
        tree = ttk.Treeview(frame, show="headings")
        tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        ttk.Scrollbar(frame, orient="vertical", command=tree.yview).grid(row=1, column=1, sticky="ns")
        setattr(self, f"{tab_name}_tree", tree)
        setattr(self, f"{tab_name}_preferred", preferred_relations)

    def _build_db_info(self) -> None:
        frame = self.tabs["Datenbankinfo"]
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.db_info_text = tk.Text(frame, wrap="none")
        self.db_info_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-f>", lambda _event: self.focus_search())
        self.bind("<Control-c>", lambda _event: self.copy_selected_row())
        self.search_tree.bind("<<TreeviewSelect>>", lambda _event: self.update_search_detail())

    def focus_search(self) -> None:
        self.search_query_var.set(self.search_query_var.get())

    def busy(self, func, *args):
        try:
            self.configure(cursor="watch")
            self.update_idletasks()
            return func(*args)
        finally:
            self.configure(cursor="")

    def reload_catalog(self) -> None:
        self.busy(self._reload_catalog)

    def _reload_catalog(self) -> None:
        try:
            self.views = self.database.list_views()
            self.tables = self.database.list_tables()
            ordered_views = sorted(self.views, key=lambda name: (0 if name.startswith("v_de_") else 1, self.language_service.relation_label(name)))
            self.relation_combo["values"] = [f"{self.language_service.relation_label(name)}  ({name})" for name in ordered_views]
            self._relation_display_map = {f"{self.language_service.relation_label(name)}  ({name})": name for name in ordered_views}
            self.chart_source_combo["values"] = [f"{self.language_service.relation_label(name)}  ({name})" for name in ordered_views]
            if ordered_views and not self.current_relation:
                display = f"{self.language_service.relation_label(ordered_views[0])}  ({ordered_views[0]})"
                self.relation_var.set(display)
                self.chart_source_var.set(display)
                self.current_relation = ordered_views[0]
                self.load_current_page()
                self.refresh_chart_fields()
            self.populate_overview()
            self.populate_catalog_identity()
            self.populate_generic_metadata_tabs()
            self.populate_guided_tabs()
            self.populate_db_info()
            self.refresh_landing_status()
            self.refresh_current_exhibit()
            self.status_var.set("Katalog geladen; Verbindung ist read-only." if self.language_service.language == "de" else "Catalog loaded; connection is read-only.")
        except Exception as exc:
            LOGGER.exception("Catalog reload failed")
            messagebox.showerror("Katalog laden", str(exc))

    def populate_overview(self) -> None:
        manifest = self.database.manifest
        required = [name for name in REQUIRED_GERMAN_VIEWS if name in self.views]
        text = [
            APP_TITLE,
            APP_SUBTITLE_DE,
            "",
            f"Snapshot: {self.database.database_path}",
            f"Quelle: {manifest.get('source_database_path', '')}",
            f"Snapshot-Zeit: {manifest.get('creation_timestamp', '')}",
            f"SHA-256 Status: {manifest.get('snapshot_status', '')}",
            f"Quell-Checksumme: {manifest.get('source_sha256', '')}",
            f"Snapshot-Checksumme: {manifest.get('snapshot_sha256', '')}",
            f"Marts: {', '.join(manifest.get('detected_mart_codes', []))}",
            f"Arbeitspakete: {', '.join(manifest.get('detected_work_package_codes', []))}",
            f"Tabellen: {len(self.tables)}",
            f"Views: {len(self.views)}",
            f"Erkannte deutsche Views: {', '.join(required)}",
            f"Read-only: {self.database.assert_read_only()}",
            "",
            "Navigation: Forschungsansichten zeigen lesbare Views. Metadatensuche durchsucht Katalogtabellen und deutsche Views. Herkunft, Validierungen, Claims und offene Prüfpunkte sind geführte Ausschnitte derselben read-only Datenbank.",
        ]
        self.overview_text.delete("1.0", "end")
        self.overview_text.insert("1.0", "\n".join(text))
        self.overview_text.configure(state="disabled")

    def populate_catalog_identity(self) -> None:
        source = self.database.manifest.get("source_database_path") or str(self.database.database_path)
        filename = Path(source).name or self.database.database_path.name
        path_text = str(source)
        if len(path_text) > 92:
            path_text = "..." + path_text[-89:]
        self.catalog_identity_var.set(f"Catalog: {filename}")
        self.catalog_mode_var.set(f"Path: {path_text} | Mode: read-only snapshot | {self.database.assert_read_only()}")

    def populate_generic_metadata_tabs(self) -> None:
        mart_page = self.database.generic_mart_work_packages()
        table_page = self.database.generic_result_tables()
        self.populate_tree_for_relation(self.generic_marts_tree, mart_page.columns, mart_page.rows, "generic_mart_work_packages")
        self.populate_tree_for_relation(self.generic_result_tables_tree, table_page.columns, table_page.rows, "generic_result_tables")
        mart_values = sorted({str(row.get("mart_code", "")) for row in mart_page.rows if row.get("mart_code")})
        role_values = sorted({str(row.get("table_role", "")) for row in table_page.rows if row.get("table_role")})
        quick_terms = self.database.quick_filter_terms()
        self.result_record_mart_combo["values"] = [""] + mart_values + [term for term in quick_terms if term not in mart_values]
        self.result_record_table_role_combo["values"] = [""] + role_values
        self.populate_generic_result_records()

    def populate_generic_result_records(self) -> None:
        page = self.database.generic_result_records(
            mart_code=self.result_record_mart_filter_var.get(),
            table_role=self.result_record_table_role_filter_var.get(),
            search=self.result_record_text_filter_var.get(),
            limit=1000,
        )
        self.populate_tree_for_relation(self.generic_result_records_tree, page.columns, page.rows, "generic_result_records")
        self.status_var.set(f"Result Records: {page.total_count} Zeilen")

    def apply_corrcore_quick_filter(self) -> None:
        self.result_record_mart_filter_var.set("QSB-CORRCORE01")
        self.result_record_table_role_filter_var.set("")
        self.result_record_text_filter_var.set("")
        self.populate_generic_result_records()
        self.expert_notebook.select(self.tabs["Result Records"])

    def clear_result_record_filters(self) -> None:
        self.result_record_mart_filter_var.set("")
        self.result_record_table_role_filter_var.set("")
        self.result_record_text_filter_var.set("")
        self.populate_generic_result_records()

    def populate_guided_tabs(self) -> None:
        for tab_name in ["Herkunft / Lineage", "Validierungen", "Claims und Ergebnisse", "Offene Prüfpunkte"]:
            preferred = getattr(self, f"{tab_name}_preferred")
            relation = next((name for name in preferred if name in self.views or name in self.tables), "")
            if relation:
                page = self.database.load_relation_page(relation, limit=100)
                tree = getattr(self, f"{tab_name}_tree")
                self.populate_tree(tree, page.columns, page.rows)

    def populate_db_info(self) -> None:
        lines = ["Manifest", json.dumps(self.database.manifest, indent=2, sort_keys=True), "", "Relationen"]
        for relation in self.database.list_relations():
            lines.append(f"{relation['type']}: {relation['name']}")
            for col in self.database.columns_for_relation(relation["name"]):
                lines.append(f"  - {col}")
        self.db_info_text.delete("1.0", "end")
        self.db_info_text.insert("1.0", "\n".join(lines))
        self.db_info_text.configure(state="disabled")

    def open_selected_relation(self) -> None:
        display = self.relation_var.get()
        self.current_relation = getattr(self, "_relation_display_map", {}).get(display, display)
        self.current_offset = 0
        self.load_current_page()

    def load_current_page(self) -> None:
        if not self.current_relation:
            return
        page = self.database.load_relation_page(
            self.current_relation,
            offset=self.current_offset,
            limit=int(self.page_size_var.get()),
            filter_column=self.current_filter_column(),
            filter_value=self.filter_value_var.get(),
            quick_filter=self.quick_filter_var.get(),
            sort_column=self.current_sort or None,
            sort_descending=self.sort_descending,
            include_tables=False,
        )
        self.current_columns = page.columns
        self.current_rows = page.rows
        self.current_total = page.total_count
        canonical_to_display, display_to_canonical = self.field_label_resolver.mapping_for(page.columns, self.current_relation)
        self._filter_column_display_map = display_to_canonical
        self.filter_column_combo["values"] = list(display_to_canonical)
        if page.columns and self.filter_column_var.get() not in display_to_canonical:
            self.filter_column_var.set(canonical_to_display[page.columns[0]])
        self.populate_tree(self.view_tree, page.columns, page.rows)
        end_row = min(page.offset + len(page.rows), page.total_count)
        self.status_var.set(f"{self.language_service.relation_label(page.view_name)}: {page.offset + 1 if page.total_count else 0}-{end_row} von {page.total_count}")

    def populate_tree(self, tree: ttk.Treeview, columns: list[str], rows: list[dict[str, Any]]) -> None:
        self.populate_tree_for_relation(tree, columns, rows, self.current_relation)

    def populate_tree_for_relation(self, tree: ttk.Treeview, columns: list[str], rows: list[dict[str, Any]], relation_name: str = "") -> None:
        tree.delete(*tree.get_children())
        tree["columns"] = columns
        for column in columns:
            tree.heading(
                column,
                text=self.language_service.field_label(column, self.show_canonical_var.get(), relation_name=relation_name),
                command=lambda c=column: self.sort_by_column(c),
            )
            tree.column(column, width=max(120, min(280, len(column) * 12)), minwidth=80, anchor="w")
        for idx, row in enumerate(rows):
            tree.insert("", "end", iid=str(idx), values=[display_value(row.get(column)) for column in columns])

    def sort_by_column(self, column: str) -> None:
        if self.current_sort == column:
            self.sort_descending = not self.sort_descending
        else:
            self.current_sort = column
            self.sort_descending = False
        self.current_offset = 0
        self.load_current_page()

    def apply_filter(self) -> None:
        self.current_offset = 0
        self.load_current_page()

    def clear_filter(self) -> None:
        self.quick_filter_var.set("")
        self.filter_value_var.set("")
        self.current_offset = 0
        self.load_current_page()

    def first_page(self) -> None:
        self.current_offset = 0
        self.load_current_page()

    def previous_page(self) -> None:
        self.current_offset = max(0, self.current_offset - int(self.page_size_var.get()))
        self.load_current_page()

    def next_page(self) -> None:
        if self.current_offset + int(self.page_size_var.get()) < self.current_total:
            self.current_offset += int(self.page_size_var.get())
            self.load_current_page()

    def last_page(self) -> None:
        page_size = int(self.page_size_var.get())
        if self.current_total:
            self.current_offset = ((self.current_total - 1) // page_size) * page_size
            self.load_current_page()

    def copy_selected_cell(self) -> None:
        selected = self.view_tree.selection()
        focus_col = self.view_tree.focus()
        if not selected or not focus_col:
            return
        values = self.view_tree.item(selected[0], "values")
        column_index = 0
        if values:
            self.clipboard_clear()
            self.clipboard_append(str(values[column_index]))

    def copy_selected_row(self) -> None:
        selected = self.view_tree.selection()
        if selected:
            values = self.view_tree.item(selected[0], "values")
            self.clipboard_clear()
            self.clipboard_append("\t".join(map(str, values)))

    def export_current_page(self) -> None:
        if not self.current_rows:
            messagebox.showinfo("Export", "Keine Zeilen zum Exportieren.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            export_rows_to_csv(
                Path(path),
                self.current_columns,
                self.current_rows,
                self.database.manifest,
                self.current_relation,
                active_filters={"quick": self.quick_filter_var.get(), "column": self.current_filter_column() or "", "value": self.filter_value_var.get()},
                write_manifest=True,
            )
            self.status_var.set(f"CSV exportiert: {path}" if self.language_service.language == "de" else f"CSV exported: {path}")
        except ExportError as exc:
            messagebox.showerror("Export", str(exc))

    def run_metadata_search(self) -> None:
        results = self.search_adapter.search(
            self.search_query_var.get(),
            mart=self.search_mart_var.get(),
            work_package=self.search_wp_var.get(),
            object_type=self.search_object_type_var.get(),
            evidence_class=self.search_evidence_var.get(),
        )
        self.search_results = results
        self._search_iid_map = {}
        self.search_tree.delete(*self.search_tree.get_children())
        grouped = group_results_by_source(results)
        for source, rows in grouped.items():
            parent = self.search_tree.insert("", "end", text=source, values=(source, "", f"{len(rows)} Treffer", "", "", "", "", "", ""))
            for result in rows:
                iid = str(len(self.search_tree.get_children(""))) + "_" + str(rows.index(result))
                self._search_iid_map[iid] = result
                self.search_tree.insert(
                    parent,
                    "end",
                    iid=iid,
                    values=(
                        result.source,
                        self.field_label_resolver.display_label(result.matched_field, result.source),
                        display_value(result.matched_value),
                        display_value(self.field_label_resolver.display_label(result.field_name, result.source) if result.field_name else ""),
                        display_value(result.label_or_alias),
                        display_value(result.unit),
                        display_value(result.dimension),
                        display_value(result.evidence_status),
                        result.related_view,
                    ),
                )
        self.status_var.set(f"{len(results)} Metadatentreffer")

    def change_language(self) -> None:
        language = "en" if self.language_var.get() == "English" else "de"
        self.language_service.set_language(language)
        save_language(language)
        self.refresh_presentation_labels()

    def refresh_presentation_labels(self) -> None:
        current_tab = self.notebook.select()
        self.notebook.tab(self.overview_tab, text=landing_localized(self.overview_config.tab_title, self.language_service.language))
        self.notebook.tab(self.exhibition_tab, text="Ausstellung" if self.language_service.language == "de" else "Exhibition")
        self.notebook.tab(self.expert_tab, text="Fachprüfung" if self.language_service.language == "de" else "Expert inspection")
        self.refresh_landing_labels()
        self._refresh_exhibit_navigation_labels()
        self.reload_catalog()
        if self.current_columns:
            self.populate_tree(self.view_tree, self.current_columns, self.current_rows)
        if current_tab:
            self.notebook.select(current_tab)

    def refresh_landing_labels(self) -> None:
        language = self.language_service.language
        self.overview_title_var.set(landing_localized(self.overview_config.title, language))
        self.overview_subtitle_var.set(landing_localized(self.overview_config.subtitle, language))
        self.overview_intro_var.set(landing_localized(self.overview_config.introduction, language))
        self.overview_image_caption_var.set(landing_localized(self.overview_config.image_caption, language))
        self.landing_caption_var.set(landing_localized(self.overview_config.image_caption, language))
        self.landing_image_note_var.set(landing_localized(LANDING_TEXT["english_image_note"], language))
        self._refresh_exhibit_card_labels()
        if hasattr(self, "exhibit_visual_caption_var"):
            exhibit = exhibit_by_id(self.showcase_config, self.current_exhibit_id)
            visual = visual_from_exhibit(exhibit)
            caption = visual.caption if self._exhibit_visual_original is not None else visual.fallback_caption
            self.exhibit_visual_caption_var.set(landing_localized(caption, language))
            if self._exhibit_visual_original is None and hasattr(self, "exhibit_visual_canvas"):
                self._render_exhibit_visual_placeholder()
        if self._landing_image_original is None:
            self.landing_image_label.configure(text=landing_localized(self.overview_config.fallback_text, language), image="")

    def _refresh_exhibit_card_labels(self) -> None:
        language = self.language_service.language
        cards_by_id = {card.exhibit_id: card for card in EXHIBIT_CARDS}
        for exhibit_id in self.overview_config.exhibit_card_order:
            card = cards_by_id[exhibit_id]
            exhibit = exhibit_by_id(self.showcase_config, exhibit_id)
            self.exhibit_card_inventory[exhibit_id].configure(text=exhibit.get("museum_label", {}).get("inventory_number", ""))
            self.exhibit_card_titles[exhibit_id].configure(text=landing_localized(card.title, language))
            self.exhibit_card_descriptions[exhibit_id].configure(text=landing_localized(card.description, language))
            self._set_overview_card_state(exhibit_id)

    def refresh_landing_status(self) -> None:
        language = self.language_service.language
        manifest = self.database.manifest
        mart = ", ".join(manifest.get("detected_mart_codes", [])) or "CAUSALITY07"
        work_packages = ", ".join(manifest.get("detected_work_package_codes", [])) or "07-01, 07-02, 07-03"
        read_only = self.database.assert_read_only()
        status = [
            f"{landing_localized(LANDING_TEXT['snapshot'], language)}: {manifest.get('snapshot_status', 'verified')}",
            f"{landing_localized(LANDING_TEXT['mart'], language)}: {mart}",
            f"{landing_localized(LANDING_TEXT['work_packages'], language)}: {work_packages}",
            f"{landing_localized(LANDING_TEXT['read_only'], language)}: {read_only}",
        ]
        self.landing_snapshot_status_var.set(" | ".join(status))
        self.overview_status_var.set(self._format_overview_status())

    def _format_overview_status(self) -> str:
        language = self.language_service.language
        manifest = self.database.manifest
        mart = ", ".join(manifest.get("detected_mart_codes", [])) or "QSB-CAUSALITY07"
        work_packages = ", ".join(manifest.get("detected_work_package_codes", [])) or "07-01 bis 07-03"
        checksum_match = manifest.get("source_sha256") == manifest.get("snapshot_sha256") if manifest else False
        raw_values = {
            "mart": mart,
            "work_packages": work_packages,
            "snapshot_status": manifest.get("snapshot_status", "verified"),
            "read_only": landing_localized(self.overview_config.status_values.get("read_only", {}), language),
            "creation_timestamp": manifest.get("creation_timestamp", ""),
            "checksum_match": landing_localized(
                self.overview_config.status_values.get("checksum_match_true" if checksum_match else "checksum_match_false", {}),
                language,
            ),
        }
        parts = []
        for field in self.overview_config.status_strip_fields:
            label = landing_localized(self.overview_config.status_labels.get(field, {"de": field, "en": field}), language)
            value = raw_values.get(field, "")
            if value:
                parts.append(f"{label}: {value}")
        return " | ".join(parts)

    def _refresh_exhibit_navigation_labels(self) -> None:
        self._refresh_exhibit_card_labels()

    def focus_exhibit_card(self, delta: int) -> str:
        ids = list(self.overview_config.exhibit_card_order)
        if self.current_exhibit_id not in ids:
            return "break"
        next_id = ids[(ids.index(self.current_exhibit_id) + delta) % len(ids)]
        self.current_exhibit_id = next_id
        self.exhibit_card_buttons[next_id].focus_set()
        self.refresh_current_exhibit()
        return "break"

    def open_exhibit_card(self, exhibit_id: str) -> None:
        self.select_exhibit(exhibit_id)
        self.notebook.select(self.exhibition_tab)
        self.exhibit_body.select(self.exhibit_summary_tab)
        self.exhibit_body.focus_set()

    def select_exhibit(self, exhibit_id: str) -> None:
        self.current_exhibit_id = exhibit_id
        self.refresh_current_exhibit()
        self._refresh_exhibit_card_labels()

    def refresh_current_exhibit(self) -> None:
        if not self.views and not self.tables:
            return
        language = self.language_service.language
        exhibit = exhibit_by_id(self.showcase_config, self.current_exhibit_id)
        resolution = resolve_exhibit(self.database, self.showcase_config, self.current_exhibit_id)
        self.exhibit_title_var.set(localized(exhibit["title"], language))
        self.exhibit_subtitle_var.set(localized(exhibit["subtitle"], language))
        self._load_exhibit_visual(exhibit)
        self._refresh_exhibit_card_labels()
        source_note = resolution.source or ", ".join(exhibit.get("preferred_sources", [])[:2])
        if resolution.empty:
            empty = localized(self.showcase_config["empty_state"], language)
            self.exhibit_status_var.set(f"{empty} Quelle: {source_note}")
            self.exhibit_facts_var.set(f"Snapshot: {self.database.database_path}")
            self.populate_tree(self.exhibit_tree, [], [])
            self.refresh_museum_label()
            self._refresh_reaction_scheme()
            self._set_exhibit_text("")
            self.exhibit_chart_status_var.set("")
            return

        fields = visible_fields(resolution.columns, exhibit.get("preferred_fields", []))
        rows = resolution.rows
        if self.current_exhibit_id == "physical_quantities":
            rows = filter_quantity_rows(rows, fields, self.show_na_quantities_var.get())
            self.show_na_check.state(["!disabled"])
        else:
            self.show_na_check.state(["disabled"])
        self.populate_tree(self.exhibit_tree, fields, [{field: row.get(field) for field in fields} for row in rows])
        facts, detail = self._format_exhibit_content(exhibit, resolution, rows, fields)
        fallback = "Fallback" if resolution.used_fallback else "Quelle"
        self.exhibit_status_var.set(f"{fallback}: {resolution.source}; Zeilen: {len(rows)}")
        self.exhibit_facts_var.set(facts)
        self.refresh_museum_label()
        self._refresh_reaction_scheme()
        self._set_exhibit_text(detail)
        self._render_exhibit_chart(exhibit, resolution)

    def _set_exhibit_text(self, text: str) -> None:
        # Detail rows remain available in the data tab; the summary no longer uses a large prose panel.
        return

    def refresh_museum_label(self) -> None:
        label = resolve_museum_label(self.database, self.showcase_config, self.current_exhibit_id, self.language_service.language)
        self.render_museum_label(label)

    def render_museum_label(self, label: MuseumLabel) -> None:
        language = self.language_service.language
        exhibit_number = label.inventory_number.rsplit("-", 1)[-1] if label.inventory_number else ""
        prefix = "Exponat" if language == "de" else "Exhibit"
        self.museum_label_ribbon_var.set(f"{prefix} {exhibit_number} / {label.inventory_number}")
        self.museum_label_title_var.set(label.title)
        self.museum_label_subtitle_var.set(label.subtitle)
        for child in self.museum_fields_frame.winfo_children():
            child.destroy()
        for idx, field in enumerate(label.fields):
            key = tk.Label(self.museum_fields_frame, text=field.label.upper(), bg=PANEL_BG, fg=CYAN, anchor="nw", width=26)
            key.grid(row=idx, column=0, padx=(0, 10), pady=2, sticky="nw")
            value_fg = GOLD if field.key in {"inventory_number", "status", "evidence_class"} else TEXT
            value = tk.Label(self.museum_fields_frame, text=field.value, bg=PANEL_BG, fg=value_fg, anchor="nw", justify="left", wraplength=760)
            value.grid(row=idx, column=1, pady=2, sticky="ew")
        technical_lines = [f"{field.label}: {field.value}" for field in label.technical_fields]
        self.museum_technical_text.configure(state="normal")
        self.museum_technical_text.delete("1.0", "end")
        self.museum_technical_text.insert("1.0", "\n".join(technical_lines))
        self.museum_technical_text.configure(state="disabled")
        self.museum_technical_button_var.set("Technische Herkunft ausblenden" if language == "de" and self.museum_technical_visible_var.get() else "Technische Herkunft anzeigen" if language == "de" else "Hide technical provenance" if self.museum_technical_visible_var.get() else "Show technical provenance")
        if hasattr(self, "exhibit_summary_canvas"):
            self.after_idle(self._update_exhibit_summary_scrollregion)

    def toggle_museum_technical(self) -> None:
        visible = not self.museum_technical_visible_var.get()
        self.museum_technical_visible_var.set(visible)
        if visible:
            self.museum_technical_text.grid()
        else:
            self.museum_technical_text.grid_remove()
        self.refresh_museum_label()
        self.after_idle(self._update_exhibit_summary_scrollregion)

    def _refresh_reaction_scheme(self) -> None:
        if self.current_exhibit_id != "causality07_reaction_cycle":
            self.reaction_label_var.set("")
            self.reaction_status_var.set("")
            self.reaction_source_var.set("")
            self.reaction_copy_text = ""
            self._set_reaction_text("")
            return
        language = self.language_service.language
        reaction = resolve_reaction_scheme(self.database, self.showcase_config)
        self.reaction_label_var.set(localized(reaction.label, language))
        self.reaction_frame.configure(text=self.reaction_label_var.get())
        self.reaction_status_var.set(localized(reaction.status, language))
        if reaction.empty:
            self.reaction_source_var.set(localized(self.showcase_config["reaction_empty_state"], language))
            self.reaction_copy_text = ""
            self._set_reaction_text("")
            return
        legend_lines = [f"{key}: {value}" for key, value in reaction.legend.items()]
        visible_text = "\n".join(reaction.lines + (["", "Legend:"] + legend_lines if legend_lines else []))
        self.reaction_copy_text = visible_text
        self._set_reaction_text(visible_text)
        self.reaction_source_var.set(f"Source: {reaction.source_reference}; Evidence: {reaction.evidence_reference}")

    def _set_reaction_text(self, text: str) -> None:
        self.reaction_text.configure(state="normal")
        self.reaction_text.delete("1.0", "end")
        self.reaction_text.insert("1.0", text)
        self.reaction_text.configure(state="disabled")

    def copy_reaction_scheme(self) -> None:
        if self.reaction_copy_text:
            self.clipboard_clear()
            self.clipboard_append(self.reaction_copy_text)
            self.status_var.set("Reaktionsschema kopiert." if self.language_service.language == "de" else "Reaction scheme copied.")

    def copy_reaction_source(self) -> None:
        source = self.reaction_source_var.get()
        if source:
            self.clipboard_clear()
            self.clipboard_append(source)
            self.status_var.set("Quellenreferenz kopiert." if self.language_service.language == "de" else "Source reference copied.")

    def _format_exhibit_content(
        self,
        exhibit: dict[str, Any],
        resolution,
        rows: list[dict[str, Any]],
        fields: list[str],
    ) -> tuple[str, str]:
        language = self.language_service.language
        if self.current_exhibit_id == "causality07_reaction_cycle":
            sequence = phase_sequence(resolution.rows, resolution.columns)
            facts = [
                "Phasenfolge: " + (" -> ".join(sequence) if sequence else "nicht im Snapshot registriert"),
                f"Quelle: {resolution.source}",
            ]
            return "\n".join(facts), self._rows_as_lines(rows[:8], fields)
        if self.current_exhibit_id == "cycle_control_runs":
            counts = cycle_control_counts(resolution.rows, resolution.columns)
            facts = [f"{label}: {value:g} count" for label, value in counts] or ["Kontrollzählwerte sind nicht vollständig registriert."]
            return "\n".join(facts), self._rows_as_lines(rows[:8], fields)
        if self.current_exhibit_id == "results_boundaries":
            grouped = group_result_rows(rows)
            labels = self.showcase_config.get("group_labels", {})
            facts = [
                f"{localized(labels.get(group, group), language)}: {len(items)}"
                for group, items in grouped.items()
                if items
            ]
            detail = []
            for group, items in grouped.items():
                if items:
                    detail.append(localized(labels.get(group, group), language))
                    detail.append(self._rows_as_lines(items[:6], fields))
            return "\n".join(facts), "\n\n".join(detail)
        if self.current_exhibit_id == "open_questions":
            return f"Offene Einträge: {len(rows)}", self._rows_as_lines(rows[:20], fields)
        return f"Registrierte Zeilen: {len(rows)}", self._rows_as_lines(rows[:12], fields)

    def _rows_as_lines(self, rows: list[dict[str, Any]], fields: list[str]) -> str:
        lines: list[str] = []
        for row in rows:
            parts = []
            for field in fields:
                value = row.get(field)
                if value not in (None, ""):
                    parts.append(f"{self.language_service.field_label(field, relation_name=self.current_relation)}: {display_value(value)}")
            if parts:
                lines.append(" | ".join(parts))
        return "\n".join(lines)

    def _render_exhibit_chart(self, exhibit: dict[str, Any], resolution) -> None:
        if self.current_exhibit_id != "cycle_control_runs":
            self.exhibit_chart_status_var.set("Kein Standarddiagramm für dieses Exponat.")
            return
        title = localized(exhibit.get("chart_presets", [{}])[0].get("title", ""), self.language_service.language) if exhibit.get("chart_presets") else ""
        config = control_chart_config(resolution, title=title)
        if config is None:
            self.exhibit_chart_status_var.set("Standarddiagramm: benötigte Zählfelder fehlen.")
            return
        try:
            chart = self.chart_service.prepare(config)
            self.exhibit_chart_renderer.render(chart)
            self.exhibit_chart_status_var.set("Y-Achse: detected complete cycles; Einheit: count.")
        except ChartError as exc:
            self.exhibit_chart_status_var.set(str(exc))

    def open_chart_from_exhibit(self) -> None:
        resolution = resolve_exhibit(self.database, self.showcase_config, self.current_exhibit_id)
        config = control_chart_config(resolution)
        if config:
            display = next((key for key, value in getattr(self, "_relation_display_map", {}).items() if value == config.source_relation), config.source_relation)
            self.chart_source_var.set(display)
            self.refresh_chart_fields()
            self.chart_type_var.set(config.chart_type)
            self.chart_title_var.set(config.title)
            self.chart_x_var.set(next((key for key, value in getattr(self, "_chart_field_map", {}).items() if value == config.x_field), config.x_field))
            self.chart_y_var.set(next((key for key, value in getattr(self, "_chart_field_map", {}).items() if value == config.y_field), config.y_field))
        self.notebook.select(self.expert_tab)
        self.expert_notebook.select(self.tabs["Diagramme"])

    def refresh_chart_fields(self) -> None:
        source = getattr(self, "_relation_display_map", {}).get(self.chart_source_var.get(), self.chart_source_var.get())
        if not source:
            return
        columns = self.database.columns_for_relation(source)
        display_values = [f"{self.language_service.field_label(column, relation_name=source)}  ({column})" for column in columns]
        self._chart_field_map = dict(zip(display_values, columns))
        for combo in [self.chart_x_combo, self.chart_y_combo, self.chart_group_combo]:
            combo["values"] = [""] + display_values
        if display_values:
            self.chart_x_var.set(display_values[0])
            if len(display_values) > 1:
                self.chart_y_var.set(display_values[1])
        presets = chart_presets(columns)
        if presets and not self.chart_title_var.get():
            self.chart_title_var.set(presets[0]["title"])

    def chart_field(self, value: str) -> str:
        return getattr(self, "_chart_field_map", {}).get(value, value)

    def generate_chart(self) -> None:
        source = getattr(self, "_relation_display_map", {}).get(self.chart_source_var.get(), self.chart_source_var.get())
        config = ChartConfig(
            source_relation=source,
            chart_type=self.chart_type_var.get(),
            x_field=self.chart_field(self.chart_x_var.get()),
            y_field=self.chart_field(self.chart_y_var.get()),
            group_field=self.chart_field(self.chart_group_var.get()),
            aggregation=self.chart_aggregation_var.get(),
            max_rows=int(self.chart_max_rows_var.get()),
            title=self.chart_title_var.get(),
            x_label=self.language_service.field_label(self.chart_field(self.chart_x_var.get()), relation_name=source),
            y_label=self.language_service.field_label(self.chart_field(self.chart_y_var.get()), relation_name=source) if self.chart_y_var.get() else "",
            language=self.language_service.language,
        )
        try:
            self.prepared_chart = self.chart_service.prepare(
                config,
                quick_filter=self.quick_filter_var.get(),
                filter_column=self.current_filter_column() or "",
                filter_value=self.filter_value_var.get(),
            )
            self.chart_renderer.render(self.prepared_chart)
            warning_text = "; ".join(self.prepared_chart.warnings)
            self.chart_status_var.set(
                f"{self.language_service.text('chart_note')}\nRows: {len(self.prepared_chart.rows)}; Excluded null rows: {self.prepared_chart.excluded_null_rows}; Engine: {self.prepared_chart.chart_engine}. {warning_text}"
            )
        except ChartError as exc:
            messagebox.showwarning("Chart", str(exc))
        except Exception as exc:
            LOGGER.exception("Chart generation failed")
            messagebox.showerror("Chart", str(exc))

    def export_chart(self) -> None:
        if self.prepared_chart is None:
            messagebox.showinfo("Chart", "No chart generated yet.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG", "*.svg"), ("PNG", "*.png"), ("CSV", "*.csv")])
        if not path:
            return
        target = Path(path)
        labels = {
            "x": self.language_service.field_label(self.prepared_chart.config.x_field, relation_name=self.prepared_chart.config.source_relation),
            "y": self.language_service.field_label(self.prepared_chart.config.y_field, relation_name=self.prepared_chart.config.source_relation) if self.prepared_chart.config.y_field else "",
        }
        if target.suffix.lower() == ".csv":
            export_plotted_csv(target, self.prepared_chart)
        else:
            self.chart_renderer.export_image(target)
        write_chart_manifest(target, self.prepared_chart, self.database.manifest, labels)
        self.status_var.set(f"Chart exported: {target}")

    def current_filter_column(self) -> str | None:
        display = self.filter_column_var.get()
        if not display:
            return None
        return self._filter_column_display_map.get(display, display)

    def reset_metadata_search(self) -> None:
        self.search_query_var.set("")
        self.search_tree.delete(*self.search_tree.get_children())
        self.search_detail_var.set("")
        self.search_results = []
        self._search_iid_map = {}

    def selected_search_result(self) -> SearchResult | None:
        selected = self.search_tree.selection()
        if not selected:
            return None
        return self._search_iid_map.get(selected[0])

    def update_search_detail(self) -> None:
        result = self.selected_search_result()
        self.search_detail_var.set(self.format_search_detail(result) if result else "")

    def format_search_detail(self, result: SearchResult) -> str:
        parts = [
            f"{self.field_label_resolver.display_label('source')}: {result.source}",
            f"{self.field_label_resolver.display_label('matched_field')}: {self.field_label_resolver.display_label(result.matched_field, result.source)}",
            f"{self.field_label_resolver.display_label('matched_value')}: {result.matched_value}",
        ]
        for canonical, value in [
            ("relation_name", result.relation_name),
            ("table_or_view_name", result.table_or_view_name),
            ("field_name", result.field_name),
            ("label_or_alias", result.label_or_alias),
            ("unit", result.unit),
            ("dimension", result.dimension),
            ("validation_status", result.validation_status),
            ("evidence_status", result.evidence_status),
            ("related_view", result.related_view),
        ]:
            if value:
                parts.append(f"{self.field_label_resolver.display_label(canonical)}: {value}")
        return "\n".join(parts)

    def open_search_source(self) -> None:
        result = self.selected_search_result()
        if not result:
            return
        target = result.related_view or result.source
        if target in self.views:
            display = next((key for key, value in getattr(self, "_relation_display_map", {}).items() if value == target), target)
            self.relation_var.set(display)
            self.current_relation = target
            self.current_offset = 0
            self.load_current_page()
        else:
            messagebox.showinfo("Quelle öffnen", "Der Treffer ist keiner vorhandenen Forschungsansicht eindeutig zugeordnet.")

    def on_close(self) -> None:
        self._save_geometry()
        self.destroy()


def run_qsb_browser(database: QSBMetadataDatabase, language: str = "de") -> None:
    app = QSBMetadataBrowser(database, language=language)
    app.mainloop()
