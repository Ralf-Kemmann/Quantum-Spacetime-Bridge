#!/usr/bin/env python3
"""Validate the prepared QSB/PBR literature metadata seed files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REQUIRED_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"
FORBIDDEN_PHRASES = [
    "supports QSB",
    "proves QSB",
    "confirms mechanism",
    "evidence for QSB",
    "physical discovery",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    data_dir = run_dir / "data"
    sources = read_csv(data_dir / "literature_source_seed.csv")
    tags = read_csv(data_dir / "literature_mechanism_tags.csv")
    boundaries = read_csv(data_dir / "literature_claim_boundaries.csv")
    aliases = read_csv(data_dir / "metadata_server_field_aliases.csv")

    failures: list[str] = []
    source_ids = {row["literature_id"] for row in sources}
    tagged_ids = {row["literature_id"] for row in tags}
    boundary_ids = {row["literature_id"] for row in boundaries}

    if len(sources) != 23:
        failures.append(f"expected 23 sources, observed {len(sources)}")
    if source_ids != boundary_ids:
        failures.append("source IDs and boundary IDs differ")
    missing_tags = sorted(source_ids - tagged_ids)
    if missing_tags:
        failures.append(f"sources without mechanism tags: {';'.join(missing_tags)}")

    for row in sources:
        for field in ("source_class", "author_cluster", "theory_cluster"):
            if not row.get(field):
                failures.append(f"{row['literature_id']} missing {field}")

    for row in boundaries:
        for field in ("internal_evidence_flag", "mechanism_claim_support", "physical_claim_support"):
            if row.get(field) != "0":
                failures.append(f"{row['literature_id']} has nonzero {field}")
        if row.get("claim_boundary") != REQUIRED_BOUNDARY:
            failures.append(f"{row['literature_id']} has wrong claim_boundary")
        if not row.get("allowed_use"):
            failures.append(f"{row['literature_id']} missing allowed_use")

    claim_text = "\n".join(
        " ".join(row.get(field, "") for field in row.keys())
        for row in boundaries
    )
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in claim_text.lower():
            failures.append(f"forbidden phrase present: {phrase}")

    for row in aliases:
        if not row.get("canonical_name"):
            failures.append(f"alias row missing canonical_name: {row}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: literature metadata seed validation passed")
    print(f"sources={len(sources)} tags={len(tags)} claim_boundaries={len(boundaries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
