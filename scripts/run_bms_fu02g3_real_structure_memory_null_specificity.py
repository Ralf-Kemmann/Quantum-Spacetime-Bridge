#!/usr/bin/env python3
"""
BMS-FU02g3 — Real-Structure Memory Comparison and Null Specificity

Purpose:
  Test whether the FU02f1 C60 role-colored carrier region is cheap or rare
  under selected same-C60 face-graph null patch families.

Scope:
  Construction-qualified null comparison only. No universal p-values.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


REPLICATE_FIELDS = [
    "null_family", "replicate_id", "carrier_face_count", "mixed_core_count",
    "pentagon_boundary_count", "carrier_hexagon_count", "carrier_pentagon_count",
    "carrier_overlap_count", "carrier_overlap_fraction",
    "mixed_core_overlap_count", "mixed_core_overlap_fraction",
    "pentagon_boundary_overlap_count", "pentagon_boundary_overlap_fraction",
    "role_balance_deviation", "carrier_component_count",
    "largest_carrier_component_count", "compactness_proxy",
    "carrier_internal_adjacency_count", "carrier_boundary_adjacency_count",
    "carrier_external_neighbor_count", "near_reference", "strict_near_reference",
]
SUMMARY_FIELDS = [
    "null_family", "replicate_count", "near_reference_count",
    "near_reference_fraction", "strict_near_reference_count",
    "strict_near_reference_fraction", "median_carrier_overlap_fraction",
    "max_carrier_overlap_fraction", "min_role_balance_deviation",
    "median_role_balance_deviation", "median_compactness_proxy",
    "max_compactness_proxy", "diagnostic_label",
]
PROXY_FIELDS = [
    "structure_id", "carrier_count", "carrier_overlap_count",
    "carrier_overlap_fraction", "mixed_core_overlap_count",
    "pentagon_boundary_overlap_count", "role_balance_deviation",
    "note",
]


def read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def parse_list(v: Any) -> List[str]:
    s = str(v or "").strip()
    if not s:
        return []
    for ch in "[]{}()'\"":
        s = s.replace(ch, "")
    out = []
    for p in s.replace(",", ";").replace("|", ";").split(";"):
        p = p.strip()
        if p:
            out.append(p)
    return out


def median(xs: List[float]) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    n = len(ys)
    mid = n // 2
    if n % 2:
        return ys[mid]
    return 0.5 * (ys[mid - 1] + ys[mid])


def build_face_graph(edges: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    adj: Dict[str, Set[str]] = defaultdict(set)
    for e in edges:
        a = e.get("cell_left", "")
        b = e.get("cell_right", "")
        if a:
            adj.setdefault(a, set())
        if b:
            adj.setdefault(b, set())
        if a and b and a != b:
            adj[a].add(b)
            adj[b].add(a)
    return adj


def components(nodes: Set[str], adj: Dict[str, Set[str]]) -> List[Set[str]]:
    seen: Set[str] = set()
    comps: List[Set[str]] = []
    for n in sorted(nodes):
        if n in seen:
            continue
        q = deque([n])
        seen.add(n)
        comp = {n}
        while q:
            u = q.popleft()
            for v in adj.get(u, set()):
                if v in nodes and v not in seen:
                    seen.add(v)
                    comp.add(v)
                    q.append(v)
        comps.append(comp)
    return comps


def adjacency_counts(carriers: Set[str], adj: Dict[str, Set[str]]) -> Tuple[int, int, int]:
    internal = 0
    boundary = 0
    external: Set[str] = set()
    seen = set()
    for a in carriers:
        for b in adj.get(a, set()):
            pair = tuple(sorted((a, b)))
            if pair in seen:
                continue
            seen.add(pair)
            if b in carriers:
                internal += 1
            else:
                boundary += 1
                external.add(b)
    return internal, boundary, len(external)


def role_map_from_fu02f1(rows: List[Dict[str, str]], cfg_roles: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for r in rows:
        fid = r.get("face_id") or r.get("cell_id")
        label = r.get("layout_role_shell") or r.get("face_carrier_role_label") or ""
        if not fid:
            continue
        if label == cfg_roles["mixed_core_role"]:
            out[fid] = "mixed_core"
        elif label == cfg_roles["pentagon_boundary_role"]:
            out[fid] = "pentagon_boundary"
        elif label == cfg_roles["adjacent_shell_role"]:
            out[fid] = "adjacent_shell"
        elif label == cfg_roles["noncarrier_role"]:
            out[fid] = "noncarrier"
        else:
            out[fid] = label or "unknown"
    return out


def cell_type_map(cells: List[Dict[str, str]]) -> Dict[str, str]:
    out = {}
    for c in cells:
        cid = c.get("cell_id")
        ctype = c.get("cell_type", "")
        out[cid] = ctype
    return out


def evaluate_patch(
    family: str,
    rep_id: int,
    carriers: Set[str],
    mixed_core: Set[str],
    pentagon_boundary: Set[str],
    ref: Dict[str, Any],
    ctypes: Dict[str, str],
    adj: Dict[str, Set[str]],
    near_cfg: Dict[str, Any],
    strict_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    ref_carriers: Set[str] = ref["carrier_set"]
    ref_mixed: Set[str] = ref["mixed_core_set"]
    ref_pent: Set[str] = ref["pentagon_boundary_set"]

    comps = components(carriers, adj)
    largest = max((len(c) for c in comps), default=0)
    compactness = largest / len(carriers) if carriers else 0.0
    internal, boundary, external_n = adjacency_counts(carriers, adj)

    carrier_overlap = len(carriers & ref_carriers)
    mixed_overlap = len(mixed_core & ref_mixed)
    pent_overlap = len(pentagon_boundary & ref_pent)

    carrier_hex = sum(1 for c in carriers if ctypes.get(c) == "hexagon")
    carrier_pent = sum(1 for c in carriers if ctypes.get(c) == "pentagon")

    role_dev = (
        abs(len(mixed_core) - len(ref_mixed))
        + abs(len(pentagon_boundary) - len(ref_pent))
        + abs(carrier_hex - ref["carrier_hexagon_count"])
        + abs(carrier_pent - ref["carrier_pentagon_count"])
    )

    carrier_overlap_frac = carrier_overlap / len(ref_carriers) if ref_carriers else 0.0
    mixed_overlap_frac = mixed_overlap / len(ref_mixed) if ref_mixed else 0.0
    pent_overlap_frac = pent_overlap / len(ref_pent) if ref_pent else 0.0

    near = (
        carrier_overlap_frac >= float(near_cfg["carrier_overlap_fraction_min"])
        and role_dev <= int(near_cfg["role_balance_deviation_max"])
        and (not near_cfg.get("require_connected", True) or len(comps) == 1)
        and compactness >= float(near_cfg["compactness_min"])
    )
    strict = (
        carrier_overlap_frac >= float(strict_cfg["carrier_overlap_fraction_min"])
        and role_dev <= int(strict_cfg["role_balance_deviation_max"])
        and (not strict_cfg.get("require_connected", True) or len(comps) == 1)
        and compactness >= float(strict_cfg["compactness_min"])
    )

    return {
        "null_family": family,
        "replicate_id": rep_id,
        "carrier_face_count": len(carriers),
        "mixed_core_count": len(mixed_core),
        "pentagon_boundary_count": len(pentagon_boundary),
        "carrier_hexagon_count": carrier_hex,
        "carrier_pentagon_count": carrier_pent,
        "carrier_overlap_count": carrier_overlap,
        "carrier_overlap_fraction": carrier_overlap_frac,
        "mixed_core_overlap_count": mixed_overlap,
        "mixed_core_overlap_fraction": mixed_overlap_frac,
        "pentagon_boundary_overlap_count": pent_overlap,
        "pentagon_boundary_overlap_fraction": pent_overlap_frac,
        "role_balance_deviation": role_dev,
        "carrier_component_count": len(comps),
        "largest_carrier_component_count": largest,
        "compactness_proxy": compactness,
        "carrier_internal_adjacency_count": internal,
        "carrier_boundary_adjacency_count": boundary,
        "carrier_external_neighbor_count": external_n,
        "near_reference": int(near),
        "strict_near_reference": int(strict),
    }


def random_connected_patch(all_cells: List[str], size: int, adj: Dict[str, Set[str]], rng: random.Random) -> Set[str]:
    for _ in range(2000):
        seed = rng.choice(all_cells)
        patch = {seed}
        frontier = list(adj.get(seed, set()))
        while len(patch) < size and frontier:
            x = rng.choice(frontier)
            frontier.remove(x)
            if x in patch:
                continue
            patch.add(x)
            for nb in adj.get(x, set()):
                if nb not in patch and nb not in frontier:
                    frontier.append(nb)
        if len(patch) == size:
            return patch
    # Fallback should be rare; return random sample if graph growth failed.
    return set(rng.sample(all_cells, size))


def summarize_family(family: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    near = sum(int(r["near_reference"]) for r in rows)
    strict = sum(int(r["strict_near_reference"]) for r in rows)
    ovs = [float(r["carrier_overlap_fraction"]) for r in rows]
    devs = [float(r["role_balance_deviation"]) for r in rows]
    comps = [float(r["compactness_proxy"]) for r in rows]
    n = len(rows)
    if near == 0:
        label = "near_reference_profiles_absent"
    elif near / n < 0.05:
        label = "near_reference_profiles_rare"
    else:
        label = "near_reference_profiles_reproduced"

    return {
        "null_family": family,
        "replicate_count": n,
        "near_reference_count": near,
        "near_reference_fraction": near / n if n else 0.0,
        "strict_near_reference_count": strict,
        "strict_near_reference_fraction": strict / n if n else 0.0,
        "median_carrier_overlap_fraction": median(ovs),
        "max_carrier_overlap_fraction": max(ovs) if ovs else 0.0,
        "min_role_balance_deviation": min(devs) if devs else 0.0,
        "median_role_balance_deviation": median(devs),
        "median_compactness_proxy": median(comps),
        "max_compactness_proxy": max(comps) if comps else 0.0,
        "diagnostic_label": label,
    }


def compare_fu02g2_proxy(root: Path, path: Path, ref: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = read_csv(path)
    c60_carriers = {r["cell_id"] for r in rows if r.get("structure_id") == "c60_reference" and str(r.get("is_carrier_cell")) == "1"}
    if not c60_carriers:
        return []
    ref_carriers = ref["carrier_set"]
    mixed = ref["mixed_core_set"]
    pent = ref["pentagon_boundary_set"]
    return [{
        "structure_id": "c60_reference",
        "carrier_count": len(c60_carriers),
        "carrier_overlap_count": len(c60_carriers & ref_carriers),
        "carrier_overlap_fraction": len(c60_carriers & ref_carriers) / len(ref_carriers) if ref_carriers else 0.0,
        "mixed_core_overlap_count": len(c60_carriers & mixed),
        "pentagon_boundary_overlap_count": len(c60_carriers & pent),
        "role_balance_deviation": "not_applicable_generic_proxy_roles_absent",
        "note": "Overlap of FU02g2 generic proxy carrier cells with FU02f1 reference carrier set.",
    }]


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    rng = random.Random(int(cfg["run"].get("random_seed", 260503)))
    out_dir = root / cfg["run"]["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[Dict[str, str]] = []

    cells = read_csv(root / cfg["inputs"]["c60_cells_csv"])
    edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    fu02f1 = read_csv(root / cfg["inputs"]["fu02f1_face_layout_csv"])

    ctypes = cell_type_map(cells)
    adj = build_face_graph(edges)
    all_cells = sorted(ctypes.keys())

    roles = role_map_from_fu02f1(fu02f1, cfg["reference_roles"])
    mixed_core = {c for c, r in roles.items() if r == "mixed_core"}
    pent_boundary = {c for c, r in roles.items() if r == "pentagon_boundary"}
    carrier_set = mixed_core | pent_boundary
    adjacent_shell = {c for c, r in roles.items() if r == "adjacent_shell"}
    noncarrier = {c for c, r in roles.items() if r == "noncarrier"}

    if not carrier_set:
        raise SystemExit("No FU02f1 reference carrier set found. Check face layout path/columns.")

    ref_comps = components(carrier_set, adj)
    ref_internal, ref_boundary, ref_external = adjacency_counts(carrier_set, adj)
    ref = {
        "carrier_set": carrier_set,
        "mixed_core_set": mixed_core,
        "pentagon_boundary_set": pent_boundary,
        "adjacent_shell_set": adjacent_shell,
        "noncarrier_set": noncarrier,
        "carrier_face_count": len(carrier_set),
        "mixed_core_count": len(mixed_core),
        "pentagon_boundary_count": len(pent_boundary),
        "carrier_hexagon_count": sum(1 for c in carrier_set if ctypes.get(c) == "hexagon"),
        "carrier_pentagon_count": sum(1 for c in carrier_set if ctypes.get(c) == "pentagon"),
        "carrier_component_count": len(ref_comps),
        "largest_carrier_component_count": max((len(c) for c in ref_comps), default=0),
        "compactness_proxy": max((len(c) for c in ref_comps), default=0) / len(carrier_set),
        "carrier_internal_adjacency_count": ref_internal,
        "carrier_boundary_adjacency_count": ref_boundary,
        "carrier_external_neighbor_count": ref_external,
        "role_mapping_note": "FU02f1 mixed_seam_boundary_face + hp_boundary_face treated as reference carrier set.",
    }
    write_json(out_dir / "bms_fu02g3_reference_profile.json", {k: sorted(v) if isinstance(v, set) else v for k, v in ref.items()})

    repeats = int(cfg["nulls"]["repeats_per_family"])
    near_cfg = cfg["near_reference"]
    strict_cfg = cfg["strict_near_reference"]
    replicate_rows: List[Dict[str, Any]] = []

    hex_cells = [c for c in all_cells if ctypes.get(c) == "hexagon"]
    pent_cells = [c for c in all_cells if ctypes.get(c) == "pentagon"]
    ref_hex_count = ref["carrier_hexagon_count"]
    ref_pent_count = ref["carrier_pentagon_count"]
    size = len(carrier_set)

    for family, fcfg in cfg["nulls"]["families"].items():
        if not fcfg.get("enabled", False):
            continue
        for i in range(repeats):
            if family == "carrier_count_random_patch":
                carriers = set(rng.sample(all_cells, size))
                # Randomly assign roles with reference role counts within carrier set.
                mixed = set(rng.sample(sorted(carriers), len(mixed_core)))
                remaining = sorted(carriers - mixed)
                pent = set(rng.sample(remaining, min(len(pent_boundary), len(remaining))))
            elif family == "type_count_preserving_patch":
                carriers = set(rng.sample(hex_cells, ref_hex_count)) | set(rng.sample(pent_cells, ref_pent_count))
                mixed = set(rng.sample(sorted(carriers), len(mixed_core)))
                remaining = sorted(carriers - mixed)
                pent = set(rng.sample(remaining, min(len(pent_boundary), len(remaining))))
            elif family == "connected_patch_seeded":
                carriers = random_connected_patch(all_cells, size, adj, rng)
                mixed = set(rng.sample(sorted(carriers), len(mixed_core)))
                remaining = sorted(carriers - mixed)
                pent = set(rng.sample(remaining, min(len(pent_boundary), len(remaining))))
            elif family == "role_count_preserving_connected_patch":
                carriers = random_connected_patch(all_cells, size, adj, rng)
                # Strong decoy: prefer hexagons for mixed_core and pentagons for pent_boundary where possible.
                candidate_hex = sorted([c for c in carriers if ctypes.get(c) == "hexagon"])
                candidate_pent = sorted([c for c in carriers if ctypes.get(c) == "pentagon"])
                if len(candidate_hex) >= len(mixed_core):
                    mixed = set(rng.sample(candidate_hex, len(mixed_core)))
                else:
                    mixed = set(candidate_hex) | set(rng.sample(sorted(carriers - set(candidate_hex)), len(mixed_core) - len(candidate_hex)))
                remaining = carriers - mixed
                rem_pent = sorted([c for c in remaining if ctypes.get(c) == "pentagon"])
                if len(rem_pent) >= len(pent_boundary):
                    pent = set(rng.sample(rem_pent, len(pent_boundary)))
                else:
                    need = len(pent_boundary) - len(rem_pent)
                    pent = set(rem_pent) | set(rng.sample(sorted(remaining - set(rem_pent)), min(need, len(remaining - set(rem_pent)))))
            else:
                warnings.append({"severity": "warning", "message": f"Unknown null family skipped: {family}"})
                continue

            replicate_rows.append(evaluate_patch(family, i, carriers, mixed, pent, ref, ctypes, adj, near_cfg, strict_cfg))

    by_family: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in replicate_rows:
        by_family[r["null_family"]].append(r)
    summary_rows = [summarize_family(fam, rows) for fam, rows in sorted(by_family.items())]

    proxy_rows = compare_fu02g2_proxy(root, root / cfg["inputs"]["fu02g2_cell_diagnostics_csv"], ref)

    write_csv(out_dir / "bms_fu02g3_null_replicates.csv", replicate_rows, REPLICATE_FIELDS)
    write_csv(out_dir / "bms_fu02g3_null_family_summary.csv", summary_rows, SUMMARY_FIELDS)
    write_csv(out_dir / "bms_fu02g3_generic_proxy_reference_overlap.csv", proxy_rows, PROXY_FIELDS)

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": str(out_dir),
        "reference_carrier_face_count": len(carrier_set),
        "reference_mixed_core_count": len(mixed_core),
        "reference_pentagon_boundary_count": len(pent_boundary),
        "null_family_count": len(summary_rows),
        "replicate_count_total": len(replicate_rows),
        "warnings_count": len(warnings),
        "generic_proxy_overlap_rows": len(proxy_rows),
        "scope_note": "Construction-qualified same-C60 face-graph null specificity test; no universal p-value or final physics claim.",
    }
    write_json(out_dir / "bms_fu02g3_run_manifest.json", manifest)
    write_json(out_dir / "bms_fu02g3_warnings.json", warnings)
    (out_dir / "bms_fu02g3_config_resolved.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(w["severity"], "-", w["message"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02g3 real-structure memory null specificity.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
