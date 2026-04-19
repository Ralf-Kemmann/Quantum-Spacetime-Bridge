from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


@dataclass(slots=True)
class PairUnit:
    pair_id: str
    endpoint_a: str
    endpoint_b: str
    weight: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExportClassData:
    export_class: str
    source_files: list[Path]
    pair_units: list[PairUnit]
    metadata: dict[str, Any] = field(default_factory=dict)


class LoaderError(RuntimeError):
    """Raised when export loading or normalization fails."""


def discover_export_files(
    export_root: Path,
    export_class: str,
    export_pattern: str,
) -> list[Path]:
    source_dir = export_root / export_class
    return sorted(source_dir.glob(export_pattern))


def _as_str(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_pair_units_from_npz(npz_data: Any, source_file: Path) -> list[PairUnit]:
    """
    Expected canonical NPZ field layout for the generic loader:

    Required:
      - pair_ids: shape (n,)
      - endpoint_a: shape (n,)
      - endpoint_b: shape (n,)

    Optional:
      - weights: shape (n,)
      - attributes: object array / dict-like payload

    If your project uses a different layout, adapt this function only.
    """
    required = ["pair_ids", "endpoint_a", "endpoint_b"]
    missing = [key for key in required if key not in npz_data]
    if missing:
        raise LoaderError(
            f"Missing required NPZ keys in {source_file.name}: {missing}"
        )

    pair_ids = npz_data["pair_ids"]
    endpoint_a = npz_data["endpoint_a"]
    endpoint_b = npz_data["endpoint_b"]

    n = len(pair_ids)
    if len(endpoint_a) != n or len(endpoint_b) != n:
        raise LoaderError(
            f"Inconsistent array lengths in {source_file.name}: "
            f"pair_ids={len(pair_ids)}, endpoint_a={len(endpoint_a)}, endpoint_b={len(endpoint_b)}"
        )

    weights = npz_data["weights"] if "weights" in npz_data else None
    if weights is not None and len(weights) != n:
        raise LoaderError(
            f"Inconsistent weights length in {source_file.name}: "
            f"weights={len(weights)} expected={n}"
        )

    pair_units: list[PairUnit] = []
    for idx in range(n):
        attrs: dict[str, Any] = {
            "source_file": source_file.name,
            "row_index": idx,
        }
        pair_units.append(
            PairUnit(
                pair_id=_as_str(pair_ids[idx]),
                endpoint_a=_as_str(endpoint_a[idx]),
                endpoint_b=_as_str(endpoint_b[idx]),
                weight=_safe_float(weights[idx]) if weights is not None else None,
                attributes=attrs,
            )
        )

    return pair_units


def load_npz_file(path: Path) -> list[PairUnit]:
    if np is None:
        raise LoaderError(
            "numpy is required to load NPZ exports but is not installed."
        )

    try:
        with np.load(path, allow_pickle=True) as data:
            return _normalize_pair_units_from_npz(data, path)
    except Exception as exc:  # pragma: no cover
        raise LoaderError(f"Failed to load NPZ file {path}: {exc}") from exc


def validate_pair_units(pair_units: list[PairUnit], export_class: str) -> None:
    seen_ids: set[str] = set()
    for pu in pair_units:
        if not pu.pair_id:
            raise LoaderError(f"{export_class}: empty pair_id encountered")
        if not pu.endpoint_a or not pu.endpoint_b:
            raise LoaderError(
                f"{export_class}: empty endpoint detected in pair {pu.pair_id}"
            )
        if pu.pair_id in seen_ids:
            raise LoaderError(
                f"{export_class}: duplicate pair_id encountered: {pu.pair_id}"
            )
        seen_ids.add(pu.pair_id)


def load_export_class_data(
    export_root: Path,
    export_class: str,
    export_pattern: str,
) -> ExportClassData:
    files = discover_export_files(export_root, export_class, export_pattern)

    pair_units: list[PairUnit] = []
    for file_path in files:
        pair_units.extend(load_npz_file(file_path))

    validate_pair_units(pair_units, export_class)

    return ExportClassData(
        export_class=export_class,
        source_files=files,
        pair_units=pair_units,
        metadata={
            "file_count": len(files),
            "pair_unit_count": len(pair_units),
        },
    )