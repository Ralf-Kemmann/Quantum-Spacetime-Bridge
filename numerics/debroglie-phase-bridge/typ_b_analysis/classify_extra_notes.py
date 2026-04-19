#!/usr/bin/env python3
"""
Classify extra notes in typ_b_analysis/notes into coarse categories.

This script compares actual notes against the expected core manifest and groups the
extra notes by filename patterns into buckets such as:
- archive_candidate
- bridge
- ring
- review
- compatibility_legacy
- pre_readable_legacy
- type_b_meta
- uncategorized

Usage:
    python classify_extra_notes.py \
      --notes-dir ./typ_b_analysis/notes \
      --manifest ./typ_b_analysis/typ_b_notes_expected_manifest.json \
      --outdir ./typ_b_analysis/results_extra_notes_classification
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple


RULES: List[Tuple[str, List[str]]] = [
    ("ring", ["RING_"]),
    ("bridge", ["BRIDGE_", "BRIDGE_CARRIER_", "BRIDGE_ORIGIN_", "RELATIONAL_BONDING_", "MINIMAL_BRIDGE_", "DEBROGLIE_BRIDGE_"]),
    ("review", ["LOUIS_", "Claude_", "CLAUDE_"]),
    ("compatibility_legacy", ["COMPATIBILITY_"]),
    ("pre_readable_legacy", ["PRE_READABLE_"]),
    ("readability", ["READABILITY_"]),
    ("dlbsr", ["DLBSR_"]),
    ("bindable_overlap", ["BINDABLE_"]),
    ("type_b_meta", ["TYPE_B_", "TYP_B_"]),
]

ARCHIVE_HINTS = [
    "TEMPLATE",
    "INDEX",
    "CURRENT_STATUS",
    "EXECUTIVE_NOTE",
    "EXECUTION_PLAN",
    "WORKFLOW",
    "CHECKLIST",
    "PROVENANCE_CAUTION",
    "PACKLISTE",
    "PRIORITY",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_name(name: str) -> Tuple[str, str]:
    for category, prefixes in RULES:
        if any(name.startswith(prefix) for prefix in prefixes):
            archive_candidate = "yes" if any(hint in name for hint in ARCHIVE_HINTS) else "maybe"
            return category, archive_candidate
    return "uncategorized", "maybe"


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify extra notes beyond the core manifest.")
    parser.add_argument("--notes-dir", required=True, help="Path to notes directory.")
    parser.add_argument("--manifest", required=True, help="Path to expected manifest JSON.")
    parser.add_argument("--outdir", required=True, help="Output directory.")
    args = parser.parse_args()

    notes_dir = Path(args.notes_dir)
    manifest_path = Path(args.manifest)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not notes_dir.is_dir():
        raise SystemExit(f"Notes directory not found: {notes_dir}")
    if not manifest_path.is_file():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    manifest = load_json(manifest_path)
    expected = set()
    for files in manifest["groups"].values():
        expected.update(files)

    actual = sorted(p.name for p in notes_dir.glob("*.md"))
    extras = sorted(set(actual) - expected)

    rows: List[Dict[str, str]] = []
    category_counts: Dict[str, int] = {}

    for name in extras:
        category, archive_candidate = classify_name(name)
        category_counts[category] = category_counts.get(category, 0) + 1
        rows.append({
            "filename": name,
            "category": category,
            "archive_candidate": archive_candidate,
        })

    csv_path = outdir / "extra_notes_classification.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "category", "archive_candidate"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary = {
        "notes_dir": str(notes_dir),
        "manifest": str(manifest_path),
        "extra_count": len(extras),
        "category_counts": dict(sorted(category_counts.items())),
        "extras": rows,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {outdir / 'summary.json'}")
    print("Category counts:")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
