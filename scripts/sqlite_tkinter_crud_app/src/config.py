"""Central application configuration."""

from __future__ import annotations

import sys
from pathlib import Path


APP_TITLE = "QSB Research Data Browser"
APP_SUBTITLE_DE = "Forschungsdaten, Metadaten und Herkunftsnachweise"
APP_VERSION = "QSB-GUI01A-0.1"
PAGE_SIZE_DEFAULT = 100
ALLOWED_PAGE_SIZES = (50, 100, 250, 500)
EXPORT_SAFE_ROW_LIMIT = 10_000
SNAPSHOT_DIR = Path(
    "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/"
    "runs/qsb_research_data_browser/snapshots"
)
HARDENED_QSB_METADATA_DB = Path(
    "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/"
    "runs/QSB-META01-03A/unit_dimension_applicability_hardening/qsb_metadata_catalog_hardened.sqlite"
)
DEFAULT_QSB_METADATA_DB = Path(
    "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/"
    "runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite"
)


def _base_dir() -> Path:
    source_path = Path(__file__).resolve()
    for parent in (source_path, *source_path.parents):
        if parent.suffix == ".pyz":
            return parent.with_suffix("")
    if Path(sys.argv[0]).suffix == ".pyz":
        return Path(sys.argv[0]).resolve().with_suffix("")
    return source_path.parent.parent


BASE_DIR = _base_dir()
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
LOG_PATH = DATA_DIR / "app.log"
ALLOWED_STATUSES = ("active", "inactive", "archived")
DESCRIPTION_MAX_LENGTH = 2000
SCHEMA_VERSION = 1
