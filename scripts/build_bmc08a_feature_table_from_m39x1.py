#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build BMC-08a real-units feature table from M39x1 families.yaml."
    )
    parser.add_argument(
        "--config",
        default="data/bmc08a_m39x1_featuretable_config.yaml",
        help="Path to YAML config for families input and output CSV.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require_key(obj: dict, key: str, context: str) -> Any:
    if key not in obj:
        raise ValueError(f"Missing key '{key}' in {context}")
    return obj[key]


def ring_rows(family: dict) -> List[dict]:
    family_id = require_key(family, "family_id", "ring family")
    family_label = require_key(family, "family_label", "ring family")
    source_tag = require_key(family, "source_tag", "ring family")
    values = require_key(require_key(family, "base_spectrum", "ring family"), "values", "ring base_spectrum")

    rows: List[dict] = []
    abs_values_sorted = sorted(sorted({abs(float(v)) for v in values if float(v) != 0.0}))
    abs_rank = {v: i + 1 for i, v in enumerate(abs_values_sorted)}

    for p_raw in values:
        p = float(p_raw)
        node_id = f"ring_p_{int(p) if p.is_integer() else str(p).replace('.', '_')}"
        node_label = f"{family_label}: p={p_raw}"
        l_major = 1.0
        l_minor = 1.0
        m_ref = abs_rank[abs(p)]
        feature_mode_frequency = (p ** 2) / 2.0
        feature_length_scale = 1.0 / abs(p)
        rows.append(
            {
                "node_id": node_id,
                "node_family": "RING",
                "node_label": node_label,
                "L_major_raw": f"{l_major:.12g}",
                "L_minor_raw": f"{l_minor:.12g}",
                "m_ref_raw": str(m_ref),
                "feature_mode_frequency": f"{feature_mode_frequency:.12g}",
                "feature_length_scale": f"{feature_length_scale:.12g}",
                "origin_tag": source_tag,
                "comment": f"{family_id}; p={p_raw}; E_quad=p^2/2; shape neutralized to 1.0",
            }
        )
    return rows


def cavity_k(mode: List[int], geometry: dict) -> float:
    n, m, l = [float(x) for x in mode]
    a = float(require_key(geometry, "a", "cavity geometry"))
    b = float(require_key(geometry, "b", "cavity geometry"))
    d = float(require_key(geometry, "d", "cavity geometry"))
    return math.sqrt((n / a) ** 2 + (m / b) ** 2 + (l / d) ** 2)


def cavity_rows(family: dict) -> List[dict]:
    family_id = require_key(family, "family_id", "cavity family")
    family_label = require_key(family, "family_label", "cavity family")
    source_tag = require_key(family, "source_tag", "cavity family")
    mode_table = require_key(family, "mode_table", "cavity family")
    geometry = require_key(mode_table, "geometry", "cavity mode_table")
    modes = require_key(mode_table, "mode_indices", "cavity mode_table")

    enriched: List[Tuple[List[int], float]] = []
    for mode in modes:
        if len(mode) != 3:
            raise ValueError(f"Cavity mode must have length 3, got {mode}")
        k = cavity_k(mode, geometry)
        enriched.append((mode, k))

    sorted_modes = sorted(enriched, key=lambda x: (x[1], tuple(x[0])))
    rank_map = {tuple(mode): i + 1 for i, (mode, _) in enumerate(sorted_modes)}

    rows: List[dict] = []
    for mode, k in enriched:
        n, m, l = mode
        node_id = f"cavity_{n}_{m}_{l}"
        node_label = f"{family_label}: mode=({n},{m},{l})"
        a = float(geometry["a"])
        b = float(geometry["b"])
        d = float(geometry["d"])
        lengths = sorted([a, b, d], reverse=True)
        l_major = lengths[0]
        l_minor = lengths[-1]
        m_ref = rank_map[tuple(mode)]
        feature_mode_frequency = k
        feature_length_scale = 1.0 / k
        rows.append(
            {
                "node_id": node_id,
                "node_family": "CAVITY",
                "node_label": node_label,
                "L_major_raw": f"{l_major:.12g}",
                "L_minor_raw": f"{l_minor:.12g}",
                "m_ref_raw": str(m_ref),
                "feature_mode_frequency": f"{feature_mode_frequency:.12g}",
                "feature_length_scale": f"{feature_length_scale:.12g}",
                "origin_tag": source_tag,
                "comment": f"{family_id}; mode=({n},{m},{l}); k from rectangular cavity geometry",
            }
        )
    return rows


BESSEL_ZERO_APPROX: Dict[Tuple[int, int], float] = {
    (0, 1): 2.4048255577,
    (1, 1): 3.8317059702,
    (2, 1): 5.1356223018,
    (0, 2): 5.5200781103,
    (3, 1): 6.3801618952,
    (1, 2): 7.0155866698,
    (2, 2): 8.4172441404,
    (0, 3): 8.6537279129,
}


def membrane_rows(family: dict, membrane_radius: float) -> List[dict]:
    family_id = require_key(family, "family_id", "membrane family")
    family_label = require_key(family, "family_label", "membrane family")
    source_tag = require_key(family, "source_tag", "membrane family")
    mode_table = require_key(family, "mode_table", "membrane family")
    modes = require_key(mode_table, "mode_indices", "membrane mode_table")

    enriched: List[Tuple[List[int], float]] = []
    for mode in modes:
        if len(mode) != 2:
            raise ValueError(f"Membrane mode must have length 2, got {mode}")
        key = (int(mode[0]), int(mode[1]))
        if key not in BESSEL_ZERO_APPROX:
            raise ValueError(f"No hard-coded Bessel zero available for membrane mode {key}")
        k = BESSEL_ZERO_APPROX[key] / membrane_radius
        enriched.append((mode, k))

    sorted_modes = sorted(enriched, key=lambda x: (x[1], tuple(x[0])))
    rank_map = {tuple(mode): i + 1 for i, (mode, _) in enumerate(sorted_modes)}

    rows: List[dict] = []
    for mode, k in enriched:
        m, n = mode
        node_id = f"membrane_{m}_{n}"
        node_label = f"{family_label}: mode=({m},{n})"
        l_major = 2.0 * membrane_radius
        l_minor = 2.0 * membrane_radius
        m_ref = rank_map[tuple(mode)]
        feature_mode_frequency = k
        feature_length_scale = 1.0 / k
        rows.append(
            {
                "node_id": node_id,
                "node_family": "MEMBRANE",
                "node_label": node_label,
                "L_major_raw": f"{l_major:.12g}",
                "L_minor_raw": f"{l_minor:.12g}",
                "m_ref_raw": str(m_ref),
                "feature_mode_frequency": f"{feature_mode_frequency:.12g}",
                "feature_length_scale": f"{feature_length_scale:.12g}",
                "origin_tag": source_tag,
                "comment": f"{family_id}; mode=({m},{n}); k from hard-coded Bessel zero / radius",
            }
        )
    return rows


def build_rows(cfg: dict, families_doc: dict) -> List[dict]:
    families = require_key(families_doc, "families", "families yaml")
    family_ids = cfg["input"].get("family_ids", ["ER1_RING", "ER2_CAVITY", "ER3_MEMBRANE"])
    selected = [fam for fam in families if fam.get("family_id") in family_ids]
    if not selected:
        raise ValueError(f"No families selected from ids={family_ids}")

    membrane_radius = float(cfg.get("constants", {}).get("membrane_radius", 1.0))

    rows: List[dict] = []
    for family in selected:
        family_id = family.get("family_id")
        if family_id == "ER1_RING":
            rows.extend(ring_rows(family))
        elif family_id == "ER2_CAVITY":
            rows.extend(cavity_rows(family))
        elif family_id == "ER3_MEMBRANE":
            rows.extend(membrane_rows(family, membrane_radius=membrane_radius))
        else:
            raise ValueError(f"Unsupported family_id for BMC-08a start block: {family_id}")
    return rows


def write_csv(path: Path, rows: List[dict]) -> None:
    fieldnames = [
        "node_id",
        "node_family",
        "node_label",
        "L_major_raw",
        "L_minor_raw",
        "m_ref_raw",
        "feature_mode_frequency",
        "feature_length_scale",
        "origin_tag",
        "comment",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    cfg = load_yaml(config_path)

    families_path = Path(cfg["input"]["families_yaml"])
    output_csv = Path(cfg["output"]["feature_table_csv"])

    families_doc = load_yaml(families_path)
    rows = build_rows(cfg, families_doc)
    write_csv(output_csv, rows)

    print(f"Wrote: {output_csv}")
    print(f"Row count: {len(rows)}")


if __name__ == "__main__":
    main()
