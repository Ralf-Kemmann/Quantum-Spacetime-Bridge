#!/usr/bin/env python3
"""
Convert project NPZ matrix artifacts into a real-export-style JSON for the
compatibility first-pass runner.

Current first-pass strategy:
- use kbar as the primary relational carrier
- derive pair-level local units from off-diagonal entries
- derive support_strength from |kbar_ij|
- derive support_sector from sign(kbar_ij)
- derive immediate neighbors by shared endpoint among pair-units
- optionally filter units by G / adjacency support

Usage:
    python convert_npz_to_local_export.py \
      --input ./results/a1_probe/k0/negative/matrices.npz \
      --output ./real_local_export_from_npz.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


def pair_id(i: int, j: int) -> str:
    a, b = sorted((i, j))
    return f"p{a}_{b}"


def endpoints_from_pair_id(pid: str) -> Tuple[int, int]:
    body = pid[1:]
    a, b = body.split("_")
    return int(a), int(b)


def share_endpoint(pid1: str, pid2: str) -> bool:
    a1, b1 = endpoints_from_pair_id(pid1)
    a2, b2 = endpoints_from_pair_id(pid2)
    return len({a1, b1}.intersection({a2, b2})) > 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert NPZ matrices into local export JSON.")
    parser.add_argument("--input", required=True, help="Path to matrices.npz")
    parser.add_argument("--output", required=True, help="Path to output export JSON")
    parser.add_argument(
        "--mode",
        choices=["kbar_all", "g_nonzero", "adjacency_nonzero"],
        default="g_nonzero",
        help="How to decide which pair-units are exported.",
    )
    args = parser.parse_args()

    path = Path(args.input)
    data = np.load(path, allow_pickle=True)

    required = ["kbar", "G", "adjacency"]
    missing = [k for k in required if k not in data.files]
    if missing:
        raise SystemExit(f"Missing required NPZ arrays: {', '.join(missing)}")

    kbar = np.asarray(data["kbar"], dtype=float)
    G = np.asarray(data["G"], dtype=float)
    adjacency = np.asarray(data["adjacency"], dtype=int)

    if kbar.ndim != 2 or kbar.shape[0] != kbar.shape[1]:
        raise SystemExit("kbar must be a square matrix")
    n = kbar.shape[0]

    units: List[Dict[str, Any]] = []

    selected_pair_ids: List[str] = []
    for i in range(n):
        for j in range(i + 1, n):
            keep = False
            if args.mode == "kbar_all":
                keep = True
            elif args.mode == "g_nonzero":
                keep = bool(abs(G[i, j]) > 0.0)
            elif args.mode == "adjacency_nonzero":
                keep = bool(adjacency[i, j] != 0)

            if keep:
                selected_pair_ids.append(pair_id(i, j))

    selected_set = set(selected_pair_ids)

    for pid in selected_pair_ids:
        i, j = endpoints_from_pair_id(pid)
        neighbors = [
            other for other in selected_pair_ids
            if other != pid and share_endpoint(pid, other)
        ]

        value = float(abs(kbar[i, j]))
        sector = 1 if float(kbar[i, j]) >= 0 else -1

        units.append(
            {
                "unit": {
                    "uid": pid,
                    "kind": "pair_unit",
                    "endpoints": [i, j],
                },
                "metrics": {
                    "support_strength": value,
                    "raw_kbar_value": float(kbar[i, j]),
                    "g_value": float(G[i, j]),
                    "adjacency_value": int(adjacency[i, j]),
                },
                "structure": {
                    "support_sector": sector,
                },
                "topology": {
                    "immediate_neighbors": neighbors,
                },
            }
        )

    export = {
        "export_id": path.stem + "_local_export",
        "source_npz": str(path),
        "conversion_mode": args.mode,
        "n_nodes": int(n),
        "unit_count": len(units),
        "units": units,
    }

    out = Path(args.output)
    out.write_text(json.dumps(export, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote: {out}")
    print(f"Units: {len(units)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
