"""Data-driven exhibit resolution for the QSB browser landing layer."""

from __future__ import annotations

import json
import re
from importlib import resources
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .chart_models import ChartConfig
from .qsb_database import QSBMetadataDatabase


CONFIG_PATH = Path(__file__).resolve().parent.parent / "resources" / "showcase_exhibits.json"
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_ ]*$")
REQUIRED_EXHIBIT_IDS = {
    "causality07_reaction_cycle",
    "cycle_control_runs",
    "results_boundaries",
    "physical_quantities",
    "open_questions",
}
RESULT_GROUPS = ("supported", "qualified", "limited", "contradictory", "unresolved", "context")
GROUP_KEYWORDS = {
    "supported": ("support", "stütz", "gestützt", "passed", "positive"),
    "qualified": ("qualif", "einschränk", "qualification"),
    "limited": ("limit", "begrenz", "boundary", "negative"),
    "contradictory": ("contradict", "widerspruch", "gegen"),
    "unresolved": ("unresolved", "offen", "unklar", "review", "warning"),
}
NA_MARKERS = {"", "n/a", "na", "not applicable", "nicht anwendbar", "not_applicable"}


@dataclass(frozen=True)
class ExhibitResolution:
    exhibit_id: str
    source: str
    columns: list[str]
    rows: list[dict[str, Any]]
    empty: bool
    used_fallback: bool = False


@dataclass(frozen=True)
class ReactionSchemeResolution:
    label: dict[str, str]
    status: dict[str, str]
    representation_type: str
    lines: list[str]
    source_reference: str
    evidence_reference: str
    legend: dict[str, str]
    canonical_representation: str
    empty: bool


def load_showcase_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    text = resources.files("resources").joinpath("showcase_exhibits.json").read_text(encoding="utf-8")
    return json.loads(text)


def localized(value: dict[str, str] | str, language: str) -> str:
    if isinstance(value, dict):
        return value.get(language) or value.get("de") or value.get("en") or ""
    return value


def validate_showcase_config(config: dict[str, Any]) -> None:
    overview = config.get("overview", {})
    for key in ("tab_title", "title", "subtitle", "introduction", "image_caption", "fallback_text"):
        for language in ("de", "en"):
            if not overview.get(key, {}).get(language):
                raise ValueError(f"Missing overview {key} for {language}")
    if overview.get("exhibit_card_order") != [item.get("id") for item in config.get("exhibits", [])]:
        raise ValueError("Overview exhibit card order must match configured exhibits")
    exhibits = config.get("exhibits", [])
    ids = {item.get("id") for item in exhibits}
    missing = REQUIRED_EXHIBIT_IDS - ids
    if missing:
        raise ValueError(f"Missing exhibit IDs: {sorted(missing)}")
    for exhibit in exhibits:
        for language in ("de", "en"):
            if not exhibit.get("title", {}).get(language):
                raise ValueError(f"Missing {language} title for {exhibit.get('id')}")
        for key in ("preferred_sources", "fallback_sources", "preferred_fields"):
            for identifier in exhibit.get(key, []):
                if not SAFE_IDENTIFIER.match(identifier):
                    raise ValueError(f"Unsafe identifier in {exhibit.get('id')}: {identifier}")
        for preset in exhibit.get("chart_presets", []):
            for key in ("x_field", "y_field"):
                identifier = preset.get(key, "")
                if identifier and not SAFE_IDENTIFIER.match(identifier):
                    raise ValueError(f"Unsafe chart field in {exhibit.get('id')}: {identifier}")
        reaction = exhibit.get("reaction_scheme")
        if reaction:
            for key in ("representation_type", "rendering_mode"):
                identifier = reaction.get(key, "")
                if identifier and not SAFE_IDENTIFIER.match(identifier):
                    raise ValueError(f"Unsafe reaction configuration in {exhibit.get('id')}: {identifier}")
        visual = exhibit.get("visual_panel", {})
        for key in (
            "image_resource",
            "image_alt_de",
            "image_alt_en",
            "caption_de",
            "caption_en",
            "preferred_layout",
            "image_fit_mode",
            "image_max_width",
            "image_max_height",
            "fallback_text_de",
            "fallback_text_en",
        ):
            if visual.get(key) in (None, ""):
                raise ValueError(f"Missing visual field {key} for {exhibit.get('id')}")
        if visual.get("image_fit_mode") != "contain":
            raise ValueError(f"Unsupported image_fit_mode for {exhibit.get('id')}: {visual.get('image_fit_mode')}")


def exhibit_by_id(config: dict[str, Any], exhibit_id: str) -> dict[str, Any]:
    for exhibit in config.get("exhibits", []):
        if exhibit.get("id") == exhibit_id:
            return exhibit
    raise KeyError(exhibit_id)


def select_source(database: QSBMetadataDatabase, exhibit: dict[str, Any]) -> tuple[str, bool]:
    available = set(database.list_views()) | set(database.list_tables())
    for source in exhibit.get("preferred_sources", []):
        if source in available:
            return source, False
    for source in exhibit.get("fallback_sources", []):
        if source in available:
            return source, True
    return "", False


def resolve_exhibit(database: QSBMetadataDatabase, config: dict[str, Any], exhibit_id: str, limit: int = 100) -> ExhibitResolution:
    exhibit = exhibit_by_id(config, exhibit_id)
    source, used_fallback = select_source(database, exhibit)
    if not source:
        return ExhibitResolution(exhibit_id, "", [], [], True)
    page = database.load_relation_page(source, limit=limit, include_tables=True)
    return ExhibitResolution(exhibit_id, source, page.columns, page.rows, not bool(page.rows), used_fallback)


def _value_at_path(data: Any, path: list[str]) -> Any:
    value = data
    for part in path:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _format_equation_dict(equations: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in equations.items():
        left = key.replace("_dtau", "/dτ").replace("_dt", "/dt")
        lines.append(f"{left} = {value}")
    return lines


def _reaction_from_rows(exhibit: dict[str, Any], resolution: ExhibitResolution) -> ReactionSchemeResolution | None:
    fields = ["reaction_scheme", "reaction_equation", "model_equations", "equation_text", "scheme_text"]
    for row in resolution.rows:
        for field in fields:
            value = row.get(field)
            if value not in (None, ""):
                lines = str(value).splitlines()
                return ReactionSchemeResolution(
                    label=exhibit.get("reaction_scheme", {}).get("label", {"de": "Reaktionsschema", "en": "Reaction scheme"}),
                    status=exhibit.get("reaction_scheme", {}).get("status", {"de": "Quellenbelegt", "en": "Source supported"}),
                    representation_type=exhibit.get("reaction_scheme", {}).get("representation_type", "reaction_scheme"),
                    lines=lines,
                    source_reference=resolution.source,
                    evidence_reference=resolution.source,
                    legend={},
                    canonical_representation=str(value),
                    empty=False,
                )
    return None


def resolve_reaction_scheme(
    database: QSBMetadataDatabase,
    config: dict[str, Any],
    exhibit_id: str = "causality07_reaction_cycle",
    repo_root: Path | None = None,
) -> ReactionSchemeResolution:
    exhibit = exhibit_by_id(config, exhibit_id)
    resolution = resolve_exhibit(database, config, exhibit_id)
    from_rows = _reaction_from_rows(exhibit, resolution)
    if from_rows is not None:
        return from_rows

    reaction = exhibit.get("reaction_scheme", {})
    source_path = reaction.get("source_path", "")
    root = repo_root or Path.cwd()
    source = (root / source_path).resolve() if source_path else None
    if source and source.exists() and reaction.get("json_path"):
        data = json.loads(source.read_text(encoding="utf-8"))
        value = _value_at_path(data, reaction.get("json_path", []))
        legend_value = _value_at_path(data, reaction.get("legend_json_path", []))
        if isinstance(value, dict):
            lines = _format_equation_dict(value)
            canonical = json.dumps(value, indent=2, sort_keys=True)
        elif isinstance(value, list):
            lines = [str(item) for item in value]
            canonical = json.dumps(value, indent=2, sort_keys=True)
        elif value not in (None, ""):
            lines = str(value).splitlines()
            canonical = str(value)
        else:
            lines = []
            canonical = ""
        if lines:
            return ReactionSchemeResolution(
                label=reaction.get("label", {"de": "Reaktionsschema", "en": "Reaction scheme"}),
                status=reaction.get("status", {"de": "Modellreaktionsschema", "en": "Model reaction scheme"}),
                representation_type=reaction.get("representation_type", "model_reaction_scheme"),
                lines=lines,
                source_reference=source_path,
                evidence_reference=reaction.get("evidence_reference", source_path),
                legend={str(key): str(value) for key, value in legend_value.items()} if isinstance(legend_value, dict) else {},
                canonical_representation=canonical,
                empty=False,
            )

    return ReactionSchemeResolution(
        label=reaction.get("label", {"de": "Reaktionsschema", "en": "Reaction scheme"}),
        status={"de": "Noch nicht im Snapshot registriert", "en": "Not yet registered in the snapshot"},
        representation_type=reaction.get("representation_type", ""),
        lines=[],
        source_reference=source_path,
        evidence_reference=reaction.get("evidence_reference", ""),
        legend={},
        canonical_representation="",
        empty=True,
    )


def visible_fields(columns: list[str], preferred_fields: list[str]) -> list[str]:
    selected = [field for field in preferred_fields if field in columns]
    if selected:
        return selected
    return columns[: min(8, len(columns))]


def row_has_not_applicable_only(row: dict[str, Any], fields: list[str]) -> bool:
    values = [str(row.get(field, "")).strip().lower() for field in fields]
    return bool(values) and all(value in NA_MARKERS for value in values)


def filter_quantity_rows(rows: list[dict[str, Any]], fields: list[str], show_not_applicable: bool = False) -> list[dict[str, Any]]:
    if show_not_applicable:
        return rows
    return [row for row in rows if not row_has_not_applicable_only(row, fields)]


def first_present(row: dict[str, Any], candidates: list[str]) -> Any:
    for candidate in candidates:
        value = row.get(candidate)
        if value not in (None, ""):
            return value
    return None


def phase_sequence(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    sequence_fields = ["phase_sequence", "detected_phase_sequence", "sequence", "phase_path"]
    for row in rows:
        value = first_present(row, sequence_fields)
        if value:
            text = str(value)
            if "->" in text:
                return [part.strip() for part in text.split("->") if part.strip()]
            if "," in text:
                return [part.strip() for part in text.split(",") if part.strip()]
    if "phase_label" not in columns:
        return []
    ordered_rows = list(rows)
    if "phase_index" in columns:
        ordered_rows.sort(key=lambda item: item.get("phase_index") if item.get("phase_index") is not None else 10**9)
    seen: list[str] = []
    for row in ordered_rows:
        label = row.get("phase_label")
        if label not in (None, "") and str(label) not in seen:
            seen.append(str(label))
    return seen


def cycle_control_counts(rows: list[dict[str, Any]], columns: list[str]) -> list[tuple[str, float]]:
    label_field = next((field for field in ("control_id", "control_type", "run_type", "case_id") if field in columns), "")
    count_field = next((field for field in ("detected_complete_cycle_count", "complete_cycle_count", "cycle_count") if field in columns), "")
    if not label_field or not count_field:
        return []
    counts: list[tuple[str, float]] = []
    for row in rows:
        label = row.get(label_field)
        value = row.get(count_field)
        if label in (None, "") or value in (None, ""):
            continue
        try:
            counts.append((str(label), float(value)))
        except (TypeError, ValueError):
            continue
    return counts


def control_chart_config(resolution: ExhibitResolution, title: str = "") -> ChartConfig | None:
    if resolution.empty:
        return None
    fields = resolution.columns
    label_field = next((field for field in ("control_id", "control_type", "run_type", "case_id") if field in fields), "")
    count_field = next((field for field in ("detected_complete_cycle_count", "complete_cycle_count", "cycle_count") if field in fields), "")
    if not label_field or not count_field:
        return None
    return ChartConfig(
        source_relation=resolution.source,
        chart_type="bar",
        x_field=label_field,
        y_field=count_field,
        aggregation="sum",
        title=title,
        y_label="detected complete cycles",
    )


def result_group_key(row: dict[str, Any]) -> str:
    text = " ".join(str(row.get(field, "")) for field in ("relation_type", "evidence_class", "validation_status", "human_review_state")).lower()
    for group, keywords in GROUP_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return group
    return "context"


def group_result_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped = {group: [] for group in RESULT_GROUPS}
    for row in rows:
        grouped[result_group_key(row)].append(row)
    return grouped
