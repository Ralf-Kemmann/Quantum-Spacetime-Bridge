#!/usr/bin/env python3
"""
BMS-FU02g4 — Symmetry-Orbit Inspection of the C60 Reference Carrier Region

Purpose:
  Inspect automorphism/orbit and patch-signature properties of the FU02f1 C60
  reference carrier region.

Scope:
  Graph/symmetry diagnostics only. No physical spacetime or chemistry claim.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc

try:
    import networkx as nx
    from networkx.algorithms import isomorphism as iso
except Exception:
    nx = None
    iso = None


SAMPLE_FIELDS = [
    "sample_id", "carrier_faces", "carrier_signature_string",
    "role_colored_signature_string", "carrier_signature_match",
    "role_colored_signature_match", "near_carrier_signature",
    "near_role_colored_signature", "carrier_hexagon_count",
    "carrier_pentagon_count", "carrier_component_count",
    "largest_carrier_component_count", "carrier_internal_adjacency_count",
    "carrier_boundary_adjacency_count", "carrier_external_neighbor_count",
]


def read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def parse_role_rows(rows: List[Dict[str, str]], cfg_roles: Dict[str, Any]) -> Dict[str, str]:
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


def induced_degree_hist(nodes: Set[str], adj: Dict[str, Set[str]]) -> Dict[str, int]:
    degs = Counter()
    for n in nodes:
        degs[sum(1 for nb in adj.get(n, set()) if nb in nodes)] += 1
    return {str(k): v for k, v in sorted(degs.items())}


def boundary_neighbor_type_counts(carriers: Set[str], ctypes: Dict[str, str], adj: Dict[str, Set[str]]) -> Dict[str, int]:
    out = Counter()
    for c in carriers:
        for nb in adj.get(c, set()):
            if nb not in carriers:
                out[ctypes.get(nb, "unknown")] += 1
    return dict(sorted(out.items()))


def role_adjacency_counts(mixed: Set[str], pent: Set[str], adj: Dict[str, Set[str]]) -> Tuple[int, int, int]:
    mixed_internal = 0
    pent_internal = 0
    mixed_pent = 0
    seen = set()
    roles = {c: "mixed" for c in mixed}
    roles.update({c: "pent" for c in pent})
    for a in sorted(roles):
        for b in adj.get(a, set()):
            if b not in roles:
                continue
            pair = tuple(sorted((a, b)))
            if pair in seen:
                continue
            seen.add(pair)
            ra, rb = roles[a], roles[b]
            if ra == rb == "mixed":
                mixed_internal += 1
            elif ra == rb == "pent":
                pent_internal += 1
            else:
                mixed_pent += 1
    return mixed_internal, pent_internal, mixed_pent


def patch_signature(carriers: Set[str], mixed: Set[str], pent: Set[str], ctypes: Dict[str, str], adj: Dict[str, Set[str]]) -> Dict[str, Any]:
    comps = components(carriers, adj)
    internal, boundary, external_n = adjacency_counts(carriers, adj)
    mi, pi, mp = role_adjacency_counts(mixed, pent, adj)
    carrier_hex = sum(1 for c in carriers if ctypes.get(c) == "hexagon")
    carrier_pent = sum(1 for c in carriers if ctypes.get(c) == "pentagon")

    sig = {
        "carrier_face_count": len(carriers),
        "carrier_hexagon_count": carrier_hex,
        "carrier_pentagon_count": carrier_pent,
        "carrier_component_count": len(comps),
        "largest_carrier_component_count": max((len(c) for c in comps), default=0),
        "carrier_internal_adjacency_count": internal,
        "carrier_boundary_adjacency_count": boundary,
        "carrier_external_neighbor_count": external_n,
        "carrier_induced_degree_histogram": induced_degree_hist(carriers, adj),
        "boundary_neighbor_type_counts": boundary_neighbor_type_counts(carriers, ctypes, adj),
        "mixed_core_count": len(mixed),
        "pentagon_boundary_count": len(pent),
        "mixed_core_internal_adjacency_count": mi,
        "pentagon_boundary_internal_adjacency_count": pi,
        "mixed_to_pentagon_boundary_adjacency_count": mp,
        "mixed_core_induced_degree_histogram": induced_degree_hist(mixed, adj),
        "pentagon_boundary_induced_degree_histogram": induced_degree_hist(pent, adj),
    }
    sig["carrier_signature_string"] = carrier_signature_string(sig)
    sig["role_colored_signature_string"] = role_signature_string(sig)
    return sig


def carrier_signature_string(sig: Dict[str, Any]) -> str:
    return "|".join([
        f"n={sig['carrier_face_count']}",
        f"H={sig['carrier_hexagon_count']}",
        f"P={sig['carrier_pentagon_count']}",
        f"comp={sig['carrier_component_count']}",
        f"largest={sig['largest_carrier_component_count']}",
        f"int={sig['carrier_internal_adjacency_count']}",
        f"bd={sig['carrier_boundary_adjacency_count']}",
        f"ext={sig['carrier_external_neighbor_count']}",
        f"deg={json.dumps(sig['carrier_induced_degree_histogram'], sort_keys=True)}",
        f"nbtype={json.dumps(sig['boundary_neighbor_type_counts'], sort_keys=True)}",
    ])


def role_signature_string(sig: Dict[str, Any]) -> str:
    return "|".join([
        carrier_signature_string(sig),
        f"mixed={sig['mixed_core_count']}",
        f"pentrole={sig['pentagon_boundary_count']}",
        f"mixint={sig['mixed_core_internal_adjacency_count']}",
        f"pentint={sig['pentagon_boundary_internal_adjacency_count']}",
        f"mixpent={sig['mixed_to_pentagon_boundary_adjacency_count']}",
        f"mixdeg={json.dumps(sig['mixed_core_induced_degree_histogram'], sort_keys=True)}",
        f"pentdeg={json.dumps(sig['pentagon_boundary_induced_degree_histogram'], sort_keys=True)}",
    ])


def signature_distance(a: Dict[str, Any], b: Dict[str, Any], role: bool = False) -> int:
    keys = [
        "carrier_hexagon_count", "carrier_pentagon_count", "carrier_component_count",
        "largest_carrier_component_count", "carrier_internal_adjacency_count",
        "carrier_boundary_adjacency_count", "carrier_external_neighbor_count",
    ]
    if role:
        keys += [
            "mixed_core_count", "pentagon_boundary_count",
            "mixed_core_internal_adjacency_count",
            "pentagon_boundary_internal_adjacency_count",
            "mixed_to_pentagon_boundary_adjacency_count",
        ]
    return sum(abs(int(a.get(k, 0)) - int(b.get(k, 0))) for k in keys)


def random_connected_patch(all_cells: List[str], size: int, adj: Dict[str, Set[str]], rng: random.Random) -> Set[str]:
    for _ in range(5000):
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
    return set(rng.sample(all_cells, size))


def automorphism_summary(adj: Dict[str, Set[str]], ctypes: Dict[str, str], carriers: Set[str], mixed: Set[str], pent: Set[str], cfg: Dict[str, Any], warnings: List[Dict[str, str]]) -> Dict[str, Any]:
    if not cfg.get("enabled", True):
        return {"enabled": False, "status": "disabled"}
    if nx is None or iso is None:
        warnings.append({"severity": "warning", "message": "networkx unavailable; automorphism orbit summary skipped."})
        return {"enabled": True, "status": "skipped_networkx_unavailable"}

    G = nx.Graph()
    for n in adj:
        G.add_node(n, cell_type=ctypes.get(n, "unknown"))
    for a, nbs in adj.items():
        for b in nbs:
            if a < b:
                G.add_edge(a, b)

    # Preserve face type for automorphisms.
    nm = iso.categorical_node_match("cell_type", "unknown")
    matcher = iso.GraphMatcher(G, G, node_match=nm)

    max_auto = int(cfg.get("max_automorphisms", 200000))
    soft_timeout = float(cfg.get("timeout_seconds_soft", 30))
    t0 = time.time()

    auto_count = 0
    carrier_images: Set[Tuple[str, ...]] = set()
    role_images: Set[Tuple[Tuple[str, str], ...]] = set()
    carrier_stab = 0
    role_stab = 0
    stopped_reason = "complete"

    ref_carrier_tuple = tuple(sorted(carriers))
    ref_role_tuple = tuple(sorted([(c, "mixed") for c in mixed] + [(c, "pentagon_boundary") for c in pent]))

    for mapping in matcher.isomorphisms_iter():
        auto_count += 1
        img_carrier = tuple(sorted(mapping[c] for c in carriers))
        carrier_images.add(img_carrier)

        img_role_items = []
        for c in mixed:
            img_role_items.append((mapping[c], "mixed"))
        for c in pent:
            img_role_items.append((mapping[c], "pentagon_boundary"))
        img_role = tuple(sorted(img_role_items))
        role_images.add(img_role)

        if img_carrier == ref_carrier_tuple:
            carrier_stab += 1
        if img_role == ref_role_tuple:
            role_stab += 1

        if auto_count >= max_auto:
            stopped_reason = "max_automorphisms_reached"
            break
        if time.time() - t0 > soft_timeout:
            stopped_reason = "soft_timeout_reached"
            break

    if stopped_reason != "complete":
        warnings.append({"severity": "warning", "message": f"Automorphism enumeration stopped early: {stopped_reason} after {auto_count} automorphisms."})

    return {
        "enabled": True,
        "status": "complete" if stopped_reason == "complete" else "partial",
        "stopped_reason": stopped_reason,
        "automorphism_count_observed": auto_count,
        "carrier_orbit_size_observed": len(carrier_images),
        "role_colored_orbit_size_observed": len(role_images),
        "carrier_stabilizer_size_observed": carrier_stab,
        "role_colored_stabilizer_size_observed": role_stab,
        "node_match_preserves_cell_type": True,
        "scope_note": "Automorphisms are face-adjacency graph automorphisms preserving cell_type.",
    }


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    rng = random.Random(int(cfg["run"]["random_seed"]))
    out_dir = root / cfg["run"]["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[Dict[str, str]] = []

    cells = read_csv(root / cfg["inputs"]["c60_cells_csv"])
    edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    fu02f1 = read_csv(root / cfg["inputs"]["fu02f1_face_layout_csv"])

    ctypes = {c["cell_id"]: c.get("cell_type", "") for c in cells}
    adj = build_face_graph(edges)
    all_cells = sorted(ctypes)

    roles = parse_role_rows(fu02f1, cfg["reference_roles"])
    mixed = {c for c, r in roles.items() if r == "mixed_core"}
    pent = {c for c, r in roles.items() if r == "pentagon_boundary"}
    carriers = mixed | pent
    if not carriers:
        raise SystemExit("No reference carrier region found from FU02f1 roles.")

    ref_sig = patch_signature(carriers, mixed, pent, ctypes, adj)
    ref_sig["carrier_set"] = sorted(carriers)
    ref_sig["mixed_core_set"] = sorted(mixed)
    ref_sig["pentagon_boundary_set"] = sorted(pent)
    write_json(out_dir / "bms_fu02g4_reference_patch_signature.json", ref_sig)

    auto = automorphism_summary(adj, ctypes, carriers, mixed, pent, cfg.get("automorphism", {}), warnings)
    write_json(out_dir / "bms_fu02g4_automorphism_orbit_summary.json", auto)

    sample_rows: List[Dict[str, Any]] = []
    match_carrier = 0
    match_role = 0
    near_carrier = 0
    near_role = 0
    sample_count = int(cfg["connected_patch_sampling"].get("sample_count", 5000))
    threshold = int(cfg["near_signature"].get("max_abs_difference_sum", 2))
    size = len(carriers)

    for i in range(sample_count):
        patch = random_connected_patch(all_cells, size, adj, rng)
        # Assign role counts heuristically by cell type preference, analogous to strong decoy:
        hexes = [c for c in sorted(patch) if ctypes.get(c) == "hexagon"]
        pents = [c for c in sorted(patch) if ctypes.get(c) == "pentagon"]
        if len(hexes) >= len(mixed):
            smixed = set(rng.sample(hexes, len(mixed)))
        else:
            smixed = set(hexes) | set(rng.sample(sorted(patch - set(hexes)), len(mixed) - len(hexes)))
        remaining = patch - smixed
        rem_pents = [c for c in sorted(remaining) if ctypes.get(c) == "pentagon"]
        if len(rem_pents) >= len(pent):
            spent = set(rng.sample(rem_pents, len(pent)))
        else:
            need = len(pent) - len(rem_pents)
            pool = sorted(remaining - set(rem_pents))
            spent = set(rem_pents) | set(rng.sample(pool, min(need, len(pool))))

        sig = patch_signature(patch, smixed, spent, ctypes, adj)
        cmatch = sig["carrier_signature_string"] == ref_sig["carrier_signature_string"]
        rmatch = sig["role_colored_signature_string"] == ref_sig["role_colored_signature_string"]
        cnear = signature_distance(sig, ref_sig, role=False) <= threshold
        rnear = signature_distance(sig, ref_sig, role=True) <= threshold
        match_carrier += int(cmatch)
        match_role += int(rmatch)
        near_carrier += int(cnear)
        near_role += int(rnear)
        sample_rows.append({
            "sample_id": i,
            "carrier_faces": ";".join(sorted(patch)),
            "carrier_signature_string": sig["carrier_signature_string"],
            "role_colored_signature_string": sig["role_colored_signature_string"],
            "carrier_signature_match": int(cmatch),
            "role_colored_signature_match": int(rmatch),
            "near_carrier_signature": int(cnear),
            "near_role_colored_signature": int(rnear),
            "carrier_hexagon_count": sig["carrier_hexagon_count"],
            "carrier_pentagon_count": sig["carrier_pentagon_count"],
            "carrier_component_count": sig["carrier_component_count"],
            "largest_carrier_component_count": sig["largest_carrier_component_count"],
            "carrier_internal_adjacency_count": sig["carrier_internal_adjacency_count"],
            "carrier_boundary_adjacency_count": sig["carrier_boundary_adjacency_count"],
            "carrier_external_neighbor_count": sig["carrier_external_neighbor_count"],
        })

    write_csv(out_dir / "bms_fu02g4_connected_patch_signature_samples.csv", sample_rows, SAMPLE_FIELDS)

    match_summary = {
        "sample_count": sample_count,
        "carrier_signature_match_count": match_carrier,
        "carrier_signature_match_fraction": match_carrier / sample_count if sample_count else 0,
        "role_colored_signature_match_count": match_role,
        "role_colored_signature_match_fraction": match_role / sample_count if sample_count else 0,
        "near_carrier_signature_count": near_carrier,
        "near_carrier_signature_fraction": near_carrier / sample_count if sample_count else 0,
        "near_role_colored_signature_count": near_role,
        "near_role_colored_signature_fraction": near_role / sample_count if sample_count else 0,
        "near_signature_max_abs_difference_sum": threshold,
        "diagnostic_label": (
            "role_signature_not_reproduced_in_samples" if match_role == 0
            else "role_signature_reproduced_in_samples"
        ),
        "scope_note": "Sampled connected same-size patches; not exhaustive unless stated elsewhere.",
    }
    write_json(out_dir / "bms_fu02g4_signature_match_summary.json", match_summary)

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": str(out_dir),
        "reference_carrier_face_count": len(carriers),
        "reference_mixed_core_count": len(mixed),
        "reference_pentagon_boundary_count": len(pent),
        "automorphism_status": auto.get("status"),
        "connected_patch_sample_count": sample_count,
        "warnings_count": len(warnings),
        "scope_note": "Symmetry-orbit and patch-signature inspection only; no final physics claim.",
    }
    write_json(out_dir / "bms_fu02g4_run_manifest.json", manifest)
    write_json(out_dir / "bms_fu02g4_warnings.json", warnings)
    (out_dir / "bms_fu02g4_config_resolved.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(w["severity"], "-", w["message"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02g4 symmetry-orbit inspection.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
