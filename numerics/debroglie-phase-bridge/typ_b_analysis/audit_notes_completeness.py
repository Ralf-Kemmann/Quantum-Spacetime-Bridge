#!/usr/bin/env python3
"""
Audit typ_b_analysis/notes completeness against an expected manifest.

Usage:
    python audit_notes_completeness.py \
      --notes-dir ./typ_b_analysis/notes \
      --manifest ./typ_b_notes_expected_manifest.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit notes completeness against an expected manifest.")
    parser.add_argument("--notes-dir", required=True, help="Path to notes directory.")
    parser.add_argument("--manifest", required=True, help="Path to expected manifest JSON.")
    args = parser.parse_args()

    notes_dir = Path(args.notes_dir)
    manifest_path = Path(args.manifest)

    if not notes_dir.is_dir():
        raise SystemExit(f"Notes directory not found or not a directory: {notes_dir}")
    if not manifest_path.is_file():
        raise SystemExit(f"Manifest file not found: {manifest_path}")

    manifest = load_json(manifest_path)
    groups: Dict[str, List[str]] = manifest["groups"]

    actual_files = sorted(p.name for p in notes_dir.glob("*.md"))
    actual_set = set(actual_files)

    expected_all: List[str] = []
    for group_files in groups.values():
        expected_all.extend(group_files)
    expected_set = set(expected_all)

    missing_global = sorted(expected_set - actual_set)
    extra_global = sorted(actual_set - expected_set)

    print("=== NOTES COMPLETENESS AUDIT ===")
    print(f"notes_dir: {notes_dir}")
    print(f"manifest:  {manifest_path}")
    print(f"expected_count: {len(expected_set)}")
    print(f"actual_md_count: {len(actual_set)}")
    print()

    for group_name, group_files in groups.items():
        group_set = set(group_files)
        present = sorted(group_set & actual_set)
        missing = sorted(group_set - actual_set)

        print(f"[GROUP] {group_name}")
        print(f"  expected: {len(group_set)}")
        print(f"  present:  {len(present)}")
        print(f"  missing:  {len(missing)}")
        if missing:
            for fn in missing:
                print(f"    MISSING: {fn}")
        print()

    print("[GLOBAL]")
    print(f"  missing_total: {len(missing_global)}")
    if missing_global:
        for fn in missing_global:
            print(f"    MISSING: {fn}")

    print(f"  extra_total:   {len(extra_global)}")
    if extra_global:
        for fn in extra_global:
            print(f"    EXTRA: {fn}")

    if not missing_global:
        print()
        print("STATUS: expected notes set is complete.")
    else:
        print()
        print("STATUS: notes set is incomplete.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
