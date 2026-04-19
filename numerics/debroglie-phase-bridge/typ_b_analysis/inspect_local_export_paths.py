#!/usr/bin/env python3
"""
Inspect a project export JSON and print candidate dotted field paths.

Usage:
    python inspect_local_export_paths.py --input your_export.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, List, Tuple

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def walk(obj: Any, prefix: str = "") -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            rows.append((path, type(v).__name__))
            rows.extend(walk(v, path))
    elif isinstance(obj, list):
        rows.append((prefix + "[]", "list"))
        if obj:
            rows.extend(walk(obj[0], prefix + "[]"))
    return rows

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    data = load_json(Path(args.input))
    rows = walk(data)

    print("=== Candidate dotted paths ===")
    for path, typ in rows:
        print(f"{path} : {typ}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
