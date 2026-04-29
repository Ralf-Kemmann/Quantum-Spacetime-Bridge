#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import yaml

BESSEL_ZERO_APPROX = {
    (0, 1): 2.4048255577,
    (1, 1): 3.8317059702,
    (2, 1): 5.1356223018,
    (0, 2): 5.5200781103,
    (3, 1): 6.3801618952,
    (1, 2): 7.0155866698,
    (2, 2): 8.4172441404,
    (0, 3): 8.6537279129,
}

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def ring_rows(family):
    values = family["base_spectrum"]["values"]
    abs_vals = sorted({abs(v) for v in values if v != 0})
    rank = {v: i + 1 for i, v in enumerate(abs_vals)}

    rows = []
    for p in values:
        rows.append({
            "node_id": f"ring_p_{p}".replace("-", "m"),
            "node_family": "RING",
            "node_label": f"p={p}",
            "L_major_raw": "1",
            "L_minor_raw": "1",
            "m_ref_raw": str(rank[abs(p)]),
            "feature_mode_frequency": str(p),
            "feature_length_scale": str(1 / abs(p)),
            "origin_tag": family["source_tag"],
            "comment": "sign-sensitive ring"
        })
    return rows

def cavity_rows(family):
    geom = family["mode_table"]["geometry"]
    modes = family["mode_table"]["mode_indices"]

    def k(m):
        n, m2, l = m
        return math.sqrt((n/geom["a"])**2 + (m2/geom["b"])**2 + (l/geom["d"])**2)

    sorted_modes = sorted(modes, key=lambda m: k(m))
    rank = {tuple(m): i + 1 for i, m in enumerate(sorted_modes)}

    rows = []
    for m in modes:
        kval = k(m)
        rows.append({
            "node_id": f"cavity_{m[0]}_{m[1]}_{m[2]}",
            "node_family": "CAVITY",
            "node_label": str(m),
            "L_major_raw": str(max(geom.values())),
            "L_minor_raw": str(min(geom.values())),
            "m_ref_raw": str(rank[tuple(m)]),
            "feature_mode_frequency": str(kval),
            "feature_length_scale": str(1/kval),
            "origin_tag": family["source_tag"],
            "comment": "cavity"
        })
    return rows

def membrane_rows(family):
    modes = family["mode_table"]["mode_indices"]
    rows = []
    for m in modes:
        k = BESSEL_ZERO_APPROX[(m[0], m[1])]
        rows.append({
            "node_id": f"membrane_{m[0]}_{m[1]}",
            "node_family": "MEMBRANE",
            "node_label": str(m),
            "L_major_raw": "2",
            "L_minor_raw": "2",
            "m_ref_raw": str(m[1]),
            "feature_mode_frequency": str(k),
            "feature_length_scale": str(1/k),
            "origin_tag": family["source_tag"],
            "comment": "membrane"
        })
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="data/bmc08c_m39x1_sign_sensitive_ring_config.yaml")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    fams = load_yaml(cfg["input"]["families_yaml"])["families"]

    rows = []
    for f in fams:
        if f["family_id"] == "ER1_RING":
            rows += ring_rows(f)
        elif f["family_id"] == "ER2_CAVITY":
            rows += cavity_rows(f)
        elif f["family_id"] == "ER3_MEMBRANE":
            rows += membrane_rows(f)

    out = Path(cfg["output"]["feature_table_csv"])
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("Wrote:", out)

if __name__ == "__main__":
    main()