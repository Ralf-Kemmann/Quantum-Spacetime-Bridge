from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError:
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
    pass


def discover_export_files(
    export_root: Path,
    export_class: str,
    export_pattern: str,
    search_mode: str = "direct",
) -> list[Path]:
    source_dir = export_root / export_class

    if not source_dir.exists():
        return []

    if search_mode == "direct":
        return sorted(source_dir.glob(export_pattern))
    if search_mode == "recursive":
        return sorted(source_dir.rglob(export_pattern))

    raise LoaderError(
        f"Unsupported search_mode={search_mode!r}. Expected 'direct' or 'recursive'."
    )


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


def _upper_triangle_pairs(n: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def _topk_pairs_from_matrix(
    matrix: Any,
    k: int,
    use_absolute_value: bool = True,
) -> set[tuple[int, int]]:
    n_rows, n_cols = matrix.shape
    if n_rows != n_cols:
        raise LoaderError(f"Top-k score matrix must be square, got shape={matrix.shape}")

    scored_pairs: list[tuple[tuple[int, int], float]] = []
    for i, j in _upper_triangle_pairs(n_rows):
        raw = float(matrix[i, j])
        score = abs(raw) if use_absolute_value else raw
        scored_pairs.append(((i, j), score))

    scored_pairs.sort(key=lambda x: x[1], reverse=True)
    return {pair for pair, _ in scored_pairs[:k]}


def _select_weight_matrix(
    npz_data: Any,
    preferred_field: str | None,
    fallback_field: str | None,
    expected_shape: tuple[int, int],
) -> tuple[Any | None, str | None]:
    for field_name in [preferred_field, fallback_field]:
        if not field_name:
            continue
        if field_name in npz_data:
            candidate = npz_data[field_name]
            if getattr(candidate, "shape", None) == expected_shape:
                return candidate, field_name
    return None, None


def _normalize_pair_units_from_explicit_layout(
    npz_data: Any,
    source_file: Path,
) -> list[PairUnit]:
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
            "source_path": str(source_file),
            "row_index": idx,
            "loader_mode": "explicit_pair_units",
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


def _normalize_pair_units_from_matrix_layout(
    npz_data: Any,
    source_file: Path,
) -> list[PairUnit]:
    if "adjacency" not in npz_data:
        raise LoaderError(
            f"Matrix layout requires 'adjacency' in {source_file.name}"
        )

    adjacency = npz_data["adjacency"]
    if getattr(adjacency, "ndim", None) != 2:
        raise LoaderError(
            f"'adjacency' must be a 2D matrix in {source_file.name}, got ndim={getattr(adjacency, 'ndim', None)}"
        )

    n_rows, n_cols = adjacency.shape
    if n_rows != n_cols:
        raise LoaderError(
            f"'adjacency' must be square in {source_file.name}, got shape={adjacency.shape}"
        )

    # Loader config is passed via synthetic key from outer wrapper
    loader_cfg = npz_data["_loader_cfg"].item() if "_loader_cfg" in npz_data else {}
    pair_unit_cfg = loader_cfg.get("pair_unit", {})

    matrix_pair_mode = pair_unit_cfg.get("matrix_pair_mode", "adjacency_only")

    matrix_fields = pair_unit_cfg.get("matrix_fields", {})
    adjacency_field = matrix_fields.get("adjacency", "adjacency")
    primary_score_field = matrix_fields.get("primary_score", "G")
    secondary_score_field = matrix_fields.get("secondary_score", "kbar")
    edge_length_field = matrix_fields.get("edge_length", "edge_length")
    d_rel_field = matrix_fields.get("d_rel", "d_rel")

    if adjacency_field != "adjacency":
        raise LoaderError(
            f"Custom adjacency field names are not yet supported; expected 'adjacency', got {adjacency_field!r}"
        )

    adjacency_pairs = {
        (i, j)
        for i, j in _upper_triangle_pairs(n_rows)
        if adjacency[i, j] != 0
    }

    selected_pairs: set[tuple[int, int]] = set(adjacency_pairs)
    pair_origin: dict[tuple[int, int], dict[str, bool]] = {
        pair: {"adjacency_hit": True, "topk_hit": False, "threshold_hit": False}
        for pair in adjacency_pairs
    }

    if matrix_pair_mode == "adjacency_only":
        pass

    elif matrix_pair_mode == "adjacency_or_topk":
        topk_cfg = pair_unit_cfg.get("topk", {})
        topk_enabled = bool(topk_cfg.get("enabled", True))
        topk_k = int(topk_cfg.get("k", 3))
        topk_score_field = topk_cfg.get("score_field", primary_score_field)
        topk_abs = bool(topk_cfg.get("use_absolute_value", True))

        if topk_enabled:
            if topk_score_field not in npz_data:
                raise LoaderError(
                    f"Top-k score field {topk_score_field!r} not found in {source_file.name}"
                )
            score_matrix = npz_data[topk_score_field]
            if getattr(score_matrix, "shape", None) != adjacency.shape:
                raise LoaderError(
                    f"Top-k score field {topk_score_field!r} shape mismatch in {source_file.name}: "
                    f"expected {adjacency.shape}, got {getattr(score_matrix, 'shape', None)}"
                )

            topk_pairs = _topk_pairs_from_matrix(
                score_matrix,
                k=topk_k,
                use_absolute_value=topk_abs,
            )
            for pair in topk_pairs:
                selected_pairs.add(pair)
                origin = pair_origin.setdefault(
                    pair,
                    {"adjacency_hit": False, "topk_hit": False, "threshold_hit": False},
                )
                origin["topk_hit"] = True

        for pair in adjacency_pairs:
            origin = pair_origin.setdefault(
                pair,
                {"adjacency_hit": False, "topk_hit": False, "threshold_hit": False},
            )
            origin["adjacency_hit"] = True

    elif matrix_pair_mode == "adjacency_plus_threshold":
        threshold_cfg = pair_unit_cfg.get("threshold", {})
        threshold_enabled = bool(threshold_cfg.get("enabled", True))
        threshold_tau = float(threshold_cfg.get("tau", 0.5))
        threshold_score_field = threshold_cfg.get("score_field", primary_score_field)
        threshold_abs = bool(threshold_cfg.get("use_absolute_value", True))

        if threshold_enabled:
            if threshold_score_field not in npz_data:
                raise LoaderError(
                    f"Threshold score field {threshold_score_field!r} not found in {source_file.name}"
                )
            score_matrix = npz_data[threshold_score_field]
            if getattr(score_matrix, "shape", None) != adjacency.shape:
                raise LoaderError(
                    f"Threshold score field {threshold_score_field!r} shape mismatch in {source_file.name}: "
                    f"expected {adjacency.shape}, got {getattr(score_matrix, 'shape', None)}"
                )

            threshold_pairs: set[tuple[int, int]] = set()
            for i, j in _upper_triangle_pairs(n_rows):
                raw = float(score_matrix[i, j])
                score = abs(raw) if threshold_abs else raw
                if score >= threshold_tau:
                    threshold_pairs.add((i, j))

            for pair in threshold_pairs:
                selected_pairs.add(pair)
                origin = pair_origin.setdefault(
                    pair,
                    {"adjacency_hit": False, "topk_hit": False, "threshold_hit": False},
                )
                origin["threshold_hit"] = True

        for pair in adjacency_pairs:
            origin = pair_origin.setdefault(
                pair,
                {"adjacency_hit": False, "topk_hit": False, "threshold_hit": False},
            )
            origin["adjacency_hit"] = True

    else:
        raise LoaderError(
            f"Unsupported matrix_pair_mode={matrix_pair_mode!r} in {source_file.name}"
        )

    weights_cfg = pair_unit_cfg.get("weights", {})
    preferred_weight_field = (
        edge_length_field if weights_cfg.get("use_edge_length_as_weight", True) else None
    )
    fallback_weight_field = weights_cfg.get("fallback_weight_field", primary_score_field)

    weight_matrix, weight_source = _select_weight_matrix(
        npz_data=npz_data,
        preferred_field=preferred_weight_field,
        fallback_field=fallback_weight_field,
        expected_shape=adjacency.shape,
    )

    pair_units: list[PairUnit] = []
    for i, j in sorted(selected_pairs):
        weight = None
        if weight_matrix is not None:
            weight = _safe_float(weight_matrix[i, j])

        origin = pair_origin.get(
            (i, j),
            {"adjacency_hit": False, "topk_hit": False, "threshold_hit": False},
        )

        attrs: dict[str, Any] = {
            "source_file": source_file.name,
            "source_path": str(source_file),
            "i": i,
            "j": j,
            "loader_mode": matrix_pair_mode,
            "adjacency_hit": origin["adjacency_hit"],
            "topk_hit": origin["topk_hit"],
            "threshold_hit": origin["threshold_hit"],
            "weight_source": weight_source,
            "primary_score_field": primary_score_field,
            "secondary_score_field": secondary_score_field,
            "d_rel_field": d_rel_field,
        }

        pair_units.append(
            PairUnit(
                pair_id=f"p_{i}_{j}",
                endpoint_a=f"n_{i}",
                endpoint_b=f"n_{j}",
                weight=weight,
                attributes=attrs,
            )
        )

    return pair_units


def _normalize_pair_units_from_npz(
    npz_data: Any,
    source_file: Path,
) -> list[PairUnit]:
    if all(key in npz_data for key in ["pair_ids", "endpoint_a", "endpoint_b"]):
        return _normalize_pair_units_from_explicit_layout(npz_data, source_file)

    if "adjacency" in npz_data:
        return _normalize_pair_units_from_matrix_layout(npz_data, source_file)

    raise LoaderError(
        f"Missing supported NPZ layout in {source_file.name}. "
        f"Expected either explicit pair-unit keys "
        f"['pair_ids', 'endpoint_a', 'endpoint_b'] "
        f"or matrix key ['adjacency']."
    )


def load_npz_file(path: Path, loader_cfg: dict[str, Any] | None = None) -> list[PairUnit]:
    if np is None:
        raise LoaderError("numpy is required to load NPZ exports but is not installed.")

    try:
        with np.load(path, allow_pickle=True) as data:
            wrapped = dict(data.items())
            wrapped["_loader_cfg"] = np.array(loader_cfg or {}, dtype=object)
            return _normalize_pair_units_from_npz(wrapped, path)
    except Exception as exc:
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
    search_mode: str = "direct",
    loader_cfg: dict[str, Any] | None = None,
) -> ExportClassData:
    files = discover_export_files(
        export_root=export_root,
        export_class=export_class,
        export_pattern=export_pattern,
        search_mode=search_mode,
    )

    pair_units: list[PairUnit] = []
    for file_path in files:
        pair_units.extend(load_npz_file(file_path, loader_cfg=loader_cfg))

    validate_pair_units(pair_units, export_class)

    return ExportClassData(
        export_class=export_class,
        source_files=files,
        pair_units=pair_units,
        metadata={
            "file_count": len(files),
            "pair_unit_count": len(pair_units),
            "search_mode": search_mode,
            "loader_cfg": loader_cfg or {},
        },
    )