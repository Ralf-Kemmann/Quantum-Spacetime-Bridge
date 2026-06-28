"""Bilingual presentation-label service for the QSB browser."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .field_labels import FieldLabelResolver
from .ui_labels import FIELD_LABELS, UI_TEXT, VIEW_LABELS, readable_identifier


SETTINGS_DIR = Path.home() / ".config" / "qsb_research_data_browser"
SETTINGS_PATH = SETTINGS_DIR / "settings.json"
SUPPORTED_LANGUAGES = ("de", "en")


class LanguageError(Exception):
    """Raised for unsupported language selections."""


def normalize_language(language: str | None) -> str:
    if not language:
        return "de"
    value = language.strip().lower()
    if value not in SUPPORTED_LANGUAGES:
        raise LanguageError(f"Unsupported language: {language}")
    return value


def load_saved_language(path: Path = SETTINGS_PATH) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return normalize_language(data.get("language"))
    except (OSError, json.JSONDecodeError, LanguageError):
        return "de"


def save_language(language: str, path: Path = SETTINGS_PATH) -> None:
    normalized = normalize_language(language)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"language": normalized}, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_start_language(cli_language: str | None, path: Path = SETTINGS_PATH) -> str:
    return normalize_language(cli_language) if cli_language else load_saved_language(path)


@dataclass(frozen=True)
class LabelResolution:
    label: str
    source: str
    canonical_name: str


class LanguageService:
    def __init__(
        self,
        language: str = "de",
        database_aliases: dict[str, dict[str, str]] | None = None,
        field_label_resolver: FieldLabelResolver | None = None,
    ) -> None:
        self.language = normalize_language(language)
        self.database_aliases = database_aliases or {}
        self.field_label_resolver = field_label_resolver or FieldLabelResolver()

    def set_language(self, language: str) -> None:
        self.language = normalize_language(language)

    def text(self, key: str) -> str:
        return UI_TEXT.get(key, {}).get(self.language, key)

    def field_label(self, canonical_name: str, show_canonical: bool = False, relation_name: str | None = None) -> str:
        resolution = self.resolve_field_label(canonical_name, relation_name)
        if show_canonical and resolution.label != canonical_name:
            return f"{resolution.label}\n({canonical_name})"
        return resolution.label

    def resolve_field_label(self, canonical_name: str, relation_name: str | None = None) -> LabelResolution:
        if self.language == "de":
            return LabelResolution(self.field_label_resolver.display_label(canonical_name, relation_name), "field_label_resolver", canonical_name)
        alias = self.database_aliases.get(self.language, {}).get(canonical_name)
        if alias:
            return LabelResolution(alias, "database_alias", canonical_name)
        mapped = FIELD_LABELS.get(canonical_name, {}).get(self.language)
        if mapped:
            return LabelResolution(mapped, "application_registry", canonical_name)
        readable = readable_identifier(canonical_name)
        if readable != canonical_name:
            return LabelResolution(readable, "readable_format", canonical_name)
        return LabelResolution(canonical_name, "canonical_fallback", canonical_name)

    def relation_label(self, canonical_name: str, show_canonical: bool = False) -> str:
        label = VIEW_LABELS.get(canonical_name, {}).get(self.language) or readable_identifier(canonical_name)
        if show_canonical and label != canonical_name:
            return f"{label}  ({canonical_name})"
        return label

    def value_label(self, canonical_value: Any) -> str:
        if canonical_value is None:
            return ""
        return str(canonical_value)
