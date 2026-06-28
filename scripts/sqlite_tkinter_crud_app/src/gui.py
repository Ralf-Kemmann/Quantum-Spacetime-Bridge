"""Tkinter user interface."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk

from .config import ALLOWED_STATUSES, APP_TITLE
from .models import Item
from .services import DuplicateNameError, ItemNotFoundError, ItemService, ValidationError


LOGGER = logging.getLogger(__name__)


class ItemApp(tk.Tk):
    def __init__(self, service: ItemService) -> None:
        super().__init__()
        self.service = service
        self.selected_id: int | None = None
        self.sort_by = "name"
        self.sort_descending = False

        self.title(APP_TITLE)
        self.geometry("1050x650")
        self.minsize(850, 520)
        self._create_variables()
        self._build_layout()
        self._bind_shortcuts()
        self.refresh_items()

    def _create_variables(self) -> None:
        self.search_var = tk.StringVar()
        self.filter_status_var = tk.StringVar(value="")
        self.name_var = tk.StringVar()
        self.status_var = tk.StringVar(value=ALLOWED_STATUSES[0])
        self.status_line_var = tk.StringVar(value="Bereit")

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        search_frame = ttk.LabelFrame(self, text="Suche und Filter")
        search_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Suche").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        ttk.Label(search_frame, text="Status").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        status_filter = ttk.Combobox(
            search_frame,
            textvariable=self.filter_status_var,
            values=("", *ALLOWED_STATUSES),
            state="readonly",
            width=14,
        )
        status_filter.grid(row=0, column=3, padx=6, pady=6, sticky="w")
        ttk.Button(search_frame, text="Aktualisieren", command=self.refresh_items).grid(row=0, column=4, padx=6, pady=6)

        form_frame = ttk.LabelFrame(self, text="Datensatz")
        form_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        ttk.Label(form_frame, text="Status").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ttk.Combobox(form_frame, textvariable=self.status_var, values=ALLOWED_STATUSES, state="readonly", width=14).grid(
            row=0, column=3, padx=6, pady=6, sticky="w"
        )
        ttk.Label(form_frame, text="Beschreibung").grid(row=1, column=0, padx=6, pady=6, sticky="nw")
        self.description_text = tk.Text(form_frame, height=4, wrap="word")
        self.description_text.grid(row=1, column=1, columnspan=3, padx=6, pady=6, sticky="ew")

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, padx=6, pady=6, sticky="ew")
        for idx in range(6):
            button_frame.columnconfigure(idx, weight=1)
        ttk.Button(button_frame, text="Neu", command=self.clear_form).grid(row=0, column=0, padx=3, sticky="ew")
        ttk.Button(button_frame, text="Speichern", command=self.save_item).grid(row=0, column=1, padx=3, sticky="ew")
        ttk.Button(button_frame, text="Aktualisieren", command=self.refresh_items).grid(row=0, column=2, padx=3, sticky="ew")
        ttk.Button(button_frame, text="Löschen", command=self.delete_selected).grid(row=0, column=3, padx=3, sticky="ew")
        ttk.Button(button_frame, text="Zurücksetzen", command=self.reset_view).grid(row=0, column=4, padx=3, sticky="ew")
        ttk.Button(button_frame, text="Beenden", command=self.destroy).grid(row=0, column=5, padx=3, sticky="ew")

        table_frame = ttk.Frame(self)
        table_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("id", "name", "description", "status", "created_at", "updated_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        labels = {
            "id": "ID",
            "name": "Name",
            "description": "Beschreibung",
            "status": "Status",
            "created_at": "Erstellt",
            "updated_at": "Geändert",
        }
        widths = {"id": 70, "name": 180, "description": 320, "status": 110, "created_at": 170, "updated_at": 170}
        for col in columns:
            self.tree.heading(col, text=labels[col], command=lambda c=col: self.change_sort(c))
            self.tree.column(col, width=widths[col], minwidth=60, anchor="w", stretch=True)
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        status_bar = ttk.Label(self, textvariable=self.status_line_var, anchor="w", relief="sunken")
        status_bar.grid(row=3, column=0, sticky="ew")

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-s>", lambda _event: self.save_item())
        self.bind("<Control-f>", lambda _event: self.search_entry.focus_set())
        self.bind("<Delete>", lambda _event: self.delete_selected())
        self.tree.bind("<Double-1>", lambda _event: self.load_selected())
        self.search_entry.bind("<Return>", lambda _event: self.refresh_items())

    def get_description(self) -> str:
        return self.description_text.get("1.0", "end").strip()

    def set_description(self, value: str) -> None:
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", value)

    def show_error(self, title: str, message: str) -> None:
        messagebox.showerror(title, message)
        self.status_line_var.set(message)

    def refresh_items(self) -> None:
        try:
            items = self.service.list_items(
                query=self.search_var.get(),
                status=self.filter_status_var.get(),
                sort_by=self.sort_by,
                descending=self.sort_descending,
            )
        except Exception:
            LOGGER.exception("Unexpected refresh error")
            self.show_error("Fehler", "Datensätze konnten nicht geladen werden. Details stehen in der Logdatei.")
            return
        self.tree.delete(*self.tree.get_children())
        for item in items:
            self.tree.insert(
                "",
                "end",
                iid=str(item.id),
                values=(item.id, item.name, item.description, item.status, item.created_at, item.updated_at),
            )
        self.status_line_var.set(f"{len(items)} Datensatz/Datensätze angezeigt")

    def save_item(self) -> None:
        try:
            if self.selected_id is None:
                item = self.service.create_item(self.name_var.get(), self.get_description(), self.status_var.get())
                messagebox.showinfo("Gespeichert", f"Datensatz '{item.name}' wurde angelegt.")
            else:
                item = self.service.update_item(
                    self.selected_id, self.name_var.get(), self.get_description(), self.status_var.get()
                )
                messagebox.showinfo("Gespeichert", f"Datensatz '{item.name}' wurde aktualisiert.")
            self.clear_form()
            self.refresh_items()
        except ValidationError as exc:
            self.show_error("Ungültige Eingabe", "\n".join(f"{field}: {msg}" for field, msg in exc.errors.items()))
        except (DuplicateNameError, ItemNotFoundError) as exc:
            self.show_error("Hinweis", str(exc))
            self.refresh_items()
        except Exception:
            LOGGER.exception("Unexpected save error")
            self.show_error("Fehler", "Datensatz konnte nicht gespeichert werden. Details stehen in der Logdatei.")

    def load_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        try:
            item = self.service.get_item(int(selected[0]))
        except ItemNotFoundError as exc:
            self.show_error("Hinweis", str(exc))
            self.refresh_items()
            return
        except Exception:
            LOGGER.exception("Unexpected load error")
            self.show_error("Fehler", "Datensatz konnte nicht geladen werden. Details stehen in der Logdatei.")
            return
        self.selected_id = item.id
        self.name_var.set(item.name)
        self.status_var.set(item.status)
        self.set_description(item.description)
        self.status_line_var.set(f"Datensatz {item.id} geladen")

    def delete_selected(self) -> None:
        selected_id = self.selected_id
        tree_selection = self.tree.selection()
        if selected_id is None and tree_selection:
            selected_id = int(tree_selection[0])
        if selected_id is None:
            self.show_error("Hinweis", "Bitte zuerst einen Datensatz auswählen.")
            return
        if not messagebox.askyesno("Löschen bestätigen", "Soll der ausgewählte Datensatz wirklich gelöscht werden?"):
            return
        try:
            self.service.delete_item(selected_id)
            self.clear_form()
            self.refresh_items()
            messagebox.showinfo("Gelöscht", "Datensatz wurde gelöscht.")
        except ItemNotFoundError as exc:
            self.show_error("Hinweis", str(exc))
            self.refresh_items()
        except Exception:
            LOGGER.exception("Unexpected delete error")
            self.show_error("Fehler", "Datensatz konnte nicht gelöscht werden. Details stehen in der Logdatei.")

    def clear_form(self) -> None:
        self.selected_id = None
        self.name_var.set("")
        self.status_var.set(ALLOWED_STATUSES[0])
        self.set_description("")
        self.tree.selection_remove(self.tree.selection())
        self.status_line_var.set("Formular geleert")

    def reset_view(self) -> None:
        self.search_var.set("")
        self.filter_status_var.set("")
        self.clear_form()
        self.refresh_items()

    def change_sort(self, column: str) -> None:
        if self.sort_by == column:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_by = column
            self.sort_descending = False
        self.refresh_items()


def run_app(service: ItemService) -> None:
    app = ItemApp(service)
    app.mainloop()
