#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_COLUMNS = [
    "node_id",
    "node_family",
    "node_label",
    "L_major_raw",
    "L_minor_raw",
    "m_ref_raw",
    "feature_mode_frequency",
    "feature_length_scale",
    "origin_tag",
]

ALLOWED_FAMILIES = {"RING", "CAVITY", "MEMBRANE"}
FAMILY_TO_SHELL = {"RING": 0, "CAVITY": 1, "MEMBRANE": 2}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build open BMC-08a realdata input files from a flat feature table."
    )
    parser.add_argument(
        "--input",
        default="data/bmc08a_real_units_feature_table.csv",
        help="Path to source feature table CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory where output files are written.",
    )
    parser.add_argument(
        "--dataset-id",
        default="BMC08a_realdata_v1",
        help="Dataset identifier for the manifest.",
    )
    parser.add_argument(
        "--dataset-version",
        default="v1",
        help="Dataset version for the manifest.",
    )
    return parser.parse_args()


def load_feature_rows(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns in feature table: {missing}")
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError("Feature table is empty.")
    return rows


def require_finite_positive(value: str, field_name: str, node_id: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(f"{field_name} for node '{node_id}' is not numeric: {value}") from exc
    if not math.isfinite(x):
        raise ValueError(f"{field_name} for node '{node_id}' is not finite: {value}")
    if x <= 0:
        raise ValueError(f"{field_name} for node '{node_id}' must be > 0: {value}")
    return x


def require_finite(value: str, field_name: str, node_id: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(f"{field_name} for node '{node_id}' is not numeric: {value}") from exc
    if not math.isfinite(x):
        raise ValueError(f"{field_name} for node '{node_id}' is not finite: {value}")
    return x


def standardize_matrix(rows: List[dict], feature_cols: List[str]) -> Dict[str, Dict[str, float]]:
    values: Dict[str, List[float]] = {col: [] for col in feature_cols}
    for row in rows:
        node_id = row["node_id"]
        for col in feature_cols:
            values[col].append(require_finite(row[col], col, node_id))
    means = {col: sum(vals) / len(vals) for col, vals in values.items()}
    stds = {}
    for col, vals in values.items():
        mean = means[col]
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        std = math.sqrt(var)
        stds[col] = std if std > 0 else 1.0

    zmap: Dict[str, Dict[str, float]] = {}
    for row in rows:
        node_id = row["node_id"]
        zmap[node_id] = {}
        for col in feature_cols:
            x = float(row[col])
            zmap[node_id][col] = (x - means[col]) / stds[col]
    return zmap


def build_node_metadata(rows: List[dict]) -> List[dict]:
    out = []
    seen = set()
    for row in rows:
        node_id = row["node_id"].strip()
        if node_id in seen:
            raise ValueError(f"Duplicate node_id in feature table: {node_id}")
        seen.add(node_id)

        family = row["node_family"].strip().upper()
        if family not in ALLOWED_FAMILIES:
            raise ValueError(f"Unsupported node_family for '{node_id}': {family}")

        l_major = require_finite_positive(row["L_major_raw"], "L_major_raw", node_id)
        l_minor = require_finite_positive(row["L_minor_raw"], "L_minor_raw", node_id)
        if l_major < l_minor:
            l_major, l_minor = l_minor, l_major

        require_finite_positive(row["feature_mode_frequency"], "feature_mode_frequency", node_id)
        require_finite_positive(row["feature_length_scale"], "feature_length_scale", node_id)
        m_ref_raw = require_finite_positive(row["m_ref_raw"], "m_ref_raw", node_id)

        feature_shape_factor = l_major / l_minor
        feature_spectral_index = m_ref_raw

        out.append(
            {
                "node_id": node_id,
                "shell_index": FAMILY_TO_SHELL[family],
                "node_label": row["node_label"].strip(),
                "node_family": family,
                "origin_tag": row["origin_tag"].strip(),
                "comment": row.get("comment", "").strip(),
                "feature_shape_factor": f"{feature_shape_factor:.12g}",
                "feature_spectral_index": f"{feature_spectral_index:.12g}",
            }
        )
    return out


def euclidean_distance(a: Dict[str, float], b: Dict[str, float], feature_cols: List[str]) -> float:
    return math.sqrt(sum((a[col] - b[col]) ** 2 for col in feature_cols))


def build_edge_table(rows: List[dict], zmap: Dict[str, Dict[str, float]], feature_cols: List[str]) -> List[dict]:
    family_by_id = {row["node_id"].strip(): row["node_family"].strip().upper() for row in rows}
    origin_by_id = {row["node_id"].strip(): row["origin_tag"].strip() for row in rows}
    node_ids = [row["node_id"].strip() for row in rows]

    edges = []
    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            source = node_ids[i]
            target = node_ids[j]
            d = euclidean_distance(zmap[source], zmap[target], feature_cols)
            weight = 1.0 / (1.0 + d)
            source_family = family_by_id[source]
            target_family = family_by_id[target]
            edge_family = "intra_family" if source_family == target_family else "cross_family"
            evidence_tag = "bmc08a_feature_v1"
            comment = f"{source_family}-{target_family} similarity from z-scored feature distance"
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "weight": f"{weight:.12g}",
                    "edge_family": edge_family,
                    "relation_type": "euclidean_similarity",
                    "source_family": source_family,
                    "target_family": target_family,
                    "evidence_tag": evidence_tag,
                    "comment": comment,
                }
            )
    return edges


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_manifest(args: argparse.Namespace, source_file: str, row_count: int) -> dict:
    return {
        "dataset_id": args.dataset_id,
        "dataset_version": args.dataset_version,
        "source_artifacts": [source_file],
        "node_semantics": "single physical instances from ring/cavity/membrane block",
        "edge_semantics": "pairwise similarity between standardized feature vectors",
        "feature_set": [
            "feature_mode_frequency",
            "feature_length_scale",
            "feature_shape_factor",
            "feature_spectral_index",
        ],
        "weight_rule": "1 / (1 + euclidean_distance(z-scored features))",
        "shell_rule": "family shell: RING=0, CAVITY=1, MEMBRANE=2",
        "ring_l_major_rule": "outer_diameter or major_extent",
        "ring_l_minor_rule": "ring_width or minor_extent",
        "ring_m_ref_rule": "fundamental_mode_or_lowest_consistent_reference",
        "cavity_l_major_rule": "cavity_length or major_extent",
        "cavity_l_minor_rule": "cavity_width or minor_extent",
        "cavity_m_ref_rule": "fundamental_mode_or_lowest_consistent_reference",
        "membrane_l_major_rule": "membrane_span or major_extent",
        "membrane_l_minor_rule": "membrane_width or minor_extent",
        "membrane_m_ref_rule": "fundamental_mode_or_lowest_consistent_reference",
        "record_count": row_count,
        "notes": [
            "Open build artifact for BMC-08a.",
            "No hidden standardization in the runner.",
            "Same-shells are family-defined in version 1.",
        ],
    }


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    rows = load_feature_rows(input_path)
    feature_cols = [
        "feature_mode_frequency",
        "feature_length_scale",
        "feature_shape_factor",
        "feature_spectral_index",
    ]

    node_metadata = build_node_metadata(rows)

    # Build an enriched internal row view after open feature derivation
    enriched_rows = []
    for row, node_row in zip(rows, node_metadata):
        enriched = dict(row)
        enriched["feature_shape_factor"] = node_row["feature_shape_factor"]
        enriched["feature_spectral_index"] = node_row["feature_spectral_index"]
        enriched_rows.append(enriched)

    zmap = standardize_matrix(enriched_rows, feature_cols)
    edge_table = build_edge_table(enriched_rows, zmap, feature_cols)

    baseline_path = output_dir / "baseline_relational_table_real.csv"
    node_path = output_dir / "node_metadata_real.csv"
    manifest_path = output_dir / "bmc08_dataset_manifest.json"

    write_csv(
        baseline_path,
        edge_table,
        [
            "source", "target", "weight", "edge_family", "relation_type",
            "source_family", "target_family", "evidence_tag", "comment"
        ],
    )
    write_csv(
        node_path,
        node_metadata,
        [
            "node_id", "shell_index", "node_label", "node_family",
            "origin_tag", "comment", "feature_shape_factor", "feature_spectral_index"
        ],
    )
    manifest = build_manifest(args, str(input_path), len(rows))
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote: {baseline_path}")
    print(f"Wrote: {node_path}")
    print(f"Wrote: {manifest_path}")


if __name__ == "__main__":
    main()
