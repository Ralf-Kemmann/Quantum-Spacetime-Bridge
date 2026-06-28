"""Visual landing-page helpers for the CAUSALITY07 exhibition."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path


RESOURCE_PACKAGE = "resources"
OVERVIEW_IMAGE_NAME = "qsb_causality07_exhibition_overview.png"
SOURCE_TREE_IMAGE = Path(__file__).resolve().parent.parent / "resources" / OVERVIEW_IMAGE_NAME


@dataclass(frozen=True)
class ExhibitCard:
    exhibit_id: str
    title: dict[str, str]
    description: dict[str, str]


@dataclass(frozen=True)
class ExhibitVisual:
    image_resource: str
    image_alt: dict[str, str]
    crop_mode: str
    caption: dict[str, str]
    fallback_caption: dict[str, str]
    preferred_layout_mode: str
    image_fit_mode: str
    image_max_width: int
    image_max_height: int


@dataclass(frozen=True)
class OverviewConfig:
    tab_title: dict[str, str]
    title: dict[str, str]
    subtitle: dict[str, str]
    introduction: dict[str, str]
    image_resource: str
    image_caption: dict[str, str]
    fallback_text: dict[str, str]
    exhibit_card_order: list[str]
    status_strip_fields: list[str]
    status_labels: dict[str, dict[str, str]]
    status_values: dict[str, dict[str, str]]
    expert_navigation_target: str


EXHIBIT_CARDS = [
    ExhibitCard(
        "causality07_reaction_cycle",
        {"de": "CAUSALITY07 — Reaktionszyklus", "en": "CAUSALITY07 — Reaction Cycle"},
        {"de": "Reaktionsschema, Phasenfolge und Evidenzstatus.", "en": "Reaction scheme, phase sequence, and evidence status."},
    ),
    ExhibitCard(
        "cycle_control_runs",
        {"de": "Zyklus und Kontrollläufe", "en": "Cycle and Control Runs"},
        {"de": "Baseline und Negativkontrollen im Vergleich.", "en": "Baseline and negative controls side by side."},
    ),
    ExhibitCard(
        "results_boundaries",
        {"de": "Ergebnisse und Grenzen", "en": "Results and Boundaries"},
        {"de": "Resultate zusammen mit ihren Claim Boundaries.", "en": "Results together with their claim boundaries."},
    ),
    ExhibitCard(
        "physical_quantities",
        {"de": "Physikalische Größen", "en": "Physical Quantities"},
        {"de": "Größen, Einheiten, Dimensionen und offene Mappings.", "en": "Quantities, units, dimensions, and open mappings."},
    ),
    ExhibitCard(
        "open_questions",
        {"de": "Offene Fragen", "en": "Open Questions"},
        {"de": "Aktuelle offene Prüf- und Evidenzpunkte.", "en": "Current open review and evidence items."},
    ),
]


LANDING_TEXT = {
    "caption": {
        "de": "Visuelle Übersicht der fünf CAUSALITY07-Exponate. Die dargestellten Inhalte führen zu den live aus dem Snapshot geladenen Ansichten.",
        "en": "Visual overview of the five CAUSALITY07 exhibits. Each entry opens a live view loaded from the current snapshot.",
    },
    "english_image_note": {
        "de": "",
        "en": "The overview image is currently available in German; all interactive content is shown in English.",
    },
    "fallback": {
        "de": "Die visuelle Übersicht ist in dieser Installation nicht verfügbar. Die fünf Live-Exponate bleiben direkt erreichbar.",
        "en": "The visual overview is not available in this installation. The five live exhibits remain directly accessible.",
    },
    "snapshot": {"de": "Snapshot", "en": "Snapshot"},
    "mart": {"de": "Mart", "en": "Mart"},
    "work_packages": {"de": "Arbeitspakete", "en": "Work packages"},
    "read_only": {"de": "Read-only", "en": "Read-only"},
}


def localized(value: dict[str, str], language: str) -> str:
    return value.get(language) or value.get("de") or value.get("en") or ""


def source_tree_image_path() -> Path:
    return SOURCE_TREE_IMAGE


def image_resource_exists() -> bool:
    return visual_resource_exists(OVERVIEW_IMAGE_NAME)


def visual_resource_exists(resource_name: str) -> bool:
    source_tree_path = SOURCE_TREE_IMAGE.parent / resource_name
    if source_tree_path.exists():
        return True
    try:
        resource = resources.files(RESOURCE_PACKAGE)
        for part in Path(resource_name).parts:
            resource = resource.joinpath(part)
        return resource.is_file()
    except (FileNotFoundError, ModuleNotFoundError):
        return False


def image_resource_bytes() -> bytes | None:
    return visual_resource_bytes(OVERVIEW_IMAGE_NAME)


def visual_resource_bytes(resource_name: str) -> bytes | None:
    source_tree_path = SOURCE_TREE_IMAGE.parent / resource_name
    if source_tree_path.exists():
        return source_tree_path.read_bytes()
    try:
        image = resources.files(RESOURCE_PACKAGE)
        for part in Path(resource_name).parts:
            image = image.joinpath(part)
        if image.is_file():
            return image.read_bytes()
    except (FileNotFoundError, ModuleNotFoundError):
        return None
    return None


def scale_to_fit(original_width: int, original_height: int, max_width: int, max_height: int) -> tuple[int, int]:
    if original_width <= 0 or original_height <= 0 or max_width <= 0 or max_height <= 0:
        return 0, 0
    ratio = min(max_width / original_width, max_height / original_height, 1.0)
    return max(1, int(original_width * ratio)), max(1, int(original_height * ratio))


def card_by_id(exhibit_id: str) -> ExhibitCard:
    for card in EXHIBIT_CARDS:
        if card.exhibit_id == exhibit_id:
            return card
    raise KeyError(exhibit_id)


def visual_from_exhibit(exhibit: dict) -> ExhibitVisual:
    visual = exhibit.get("visual_panel", {})
    caption = {
        "de": visual.get("caption_de", visual.get("caption", {}).get("de", "")),
        "en": visual.get("caption_en", visual.get("caption", {}).get("en", "")),
    }
    fallback = {
        "de": visual.get("fallback_text_de", visual.get("fallback_caption", {}).get("de", caption["de"])),
        "en": visual.get("fallback_text_en", visual.get("fallback_caption", {}).get("en", caption["en"])),
    }
    return ExhibitVisual(
        image_resource=str(visual.get("image_resource", "")),
        image_alt={"de": str(visual.get("image_alt_de", "")), "en": str(visual.get("image_alt_en", ""))},
        crop_mode=str(visual.get("crop_mode", visual.get("image_fit_mode", "contain"))),
        caption=caption,
        fallback_caption=fallback,
        preferred_layout_mode=str(visual.get("preferred_layout", visual.get("preferred_layout_mode", "responsive"))),
        image_fit_mode=str(visual.get("image_fit_mode", "contain")),
        image_max_width=int(visual.get("image_max_width", 760)),
        image_max_height=int(visual.get("image_max_height", 520)),
    )


def overview_from_config(config: dict) -> OverviewConfig:
    overview = config.get("overview", {})
    return OverviewConfig(
        tab_title=dict(overview.get("tab_title", {"de": "Überblick", "en": "Overview"})),
        title=dict(overview.get("title", {"de": "QSB Research Data Browser", "en": "QSB Research Data Browser"})),
        subtitle=dict(overview.get("subtitle", {})),
        introduction=dict(overview.get("introduction", {})),
        image_resource=str(overview.get("image_resource", OVERVIEW_IMAGE_NAME)),
        image_caption=dict(overview.get("image_caption", {})),
        fallback_text=dict(overview.get("fallback_text", LANDING_TEXT["fallback"])),
        exhibit_card_order=list(overview.get("exhibit_card_order", [card.exhibit_id for card in EXHIBIT_CARDS])),
        status_strip_fields=list(overview.get("status_strip_fields", [])),
        status_labels={str(key): dict(value) for key, value in overview.get("status_labels", {}).items()},
        status_values={str(key): dict(value) for key, value in overview.get("status_values", {}).items()},
        expert_navigation_target=str(overview.get("expert_navigation_target", "")),
    )
