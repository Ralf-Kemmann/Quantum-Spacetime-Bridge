#!/usr/bin/env python3
"""
BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration

Purpose:
  Process deterministic chunks of connected same-size C60 face patches and
  optionally canonicalize patches under face-type-preserving automorphisms.

Scope:
  A single run is a chunk unless enumeration_status == complete.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterable, Iterator, List, Optional, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc

try:
    import networkx as nx
    from networkx.algorithms import isomorphism as nx_iso
except Exception:
    nx = None
    nx_iso = None


MATCH_FIELDS = [
    "scope", "match_type", "patch_faces", "canonical_patch_faces",
    "signature_distance", "role_signature_distance",
    "carrier_hexagon_count", "carrier_pentagon_count",
    "carrier_internal_adjacency_count",
    "carrier_boundary_adjacency_count", "carrier_external_neighbor_count",
]
COUNT_FIELDS = ["scope", "signature_kind", "signature_string", "count"]


def read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


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


def parse_roles(rows: List[Dict[str, str]], cfg_roles: Dict[str, str]) -> Dict[str, str]:
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


def is_connected(nodes: Set[str], adj: Dict[str, Set[str]]) -> bool:
    return bool(nodes) and len(components(nodes, adj)) == 1


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
    c = Counter()
    for n in nodes:
        c[sum(1 for nb in adj.get(n, set()) if nb in nodes)] += 1
    return {str(k): v for k, v in sorted(c.items())}


def boundary_neighbor_type_counts(carriers: Set[str], ctypes: Dict[str, str], adj: Dict[str, Set[str]]) -> Dict[str, int]:
    c = Counter()
    for n in carriers:
        for nb in adj.get(n, set()):
            if nb not in carriers:
                c[ctypes.get(nb, "unknown")] += 1
    return dict(sorted(c.items()))


def role_adjacency_counts(mixed: Set[str], pent: Set[str], adj: Dict[str, Set[str]]) -> Tuple[int, int, int]:
    role = {n: "mixed" for n in mixed}
    role.update({n: "pentagon_boundary" for n in pent})
    seen = set()
    mixed_internal = 0
    pent_internal = 0
    cross = 0
    for a in role:
        for b in adj.get(a, set()):
            if b not in role:
                continue
            pair = tuple(sorted((a, b)))
            if pair in seen:
                continue
            seen.add(pair)
            if role[a] == role[b] == "mixed":
                mixed_internal += 1
            elif role[a] == role[b] == "pentagon_boundary":
                pent_internal += 1
            else:
                cross += 1
    return mixed_internal, pent_internal, cross


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


def patch_signature(carriers: Set[str], mixed: Set[str], pent: Set[str], ctypes: Dict[str, str], adj: Dict[str, Set[str]]) -> Dict[str, Any]:
    comps = components(carriers, adj)
    internal, boundary, external = adjacency_counts(carriers, adj)
    mixint, pentint, cross = role_adjacency_counts(mixed, pent, adj)
    sig = {
        "carrier_face_count": len(carriers),
        "carrier_hexagon_count": sum(1 for c in carriers if ctypes.get(c) == "hexagon"),
        "carrier_pentagon_count": sum(1 for c in carriers if ctypes.get(c) == "pentagon"),
        "carrier_component_count": len(comps),
        "largest_carrier_component_count": max((len(c) for c in comps), default=0),
        "carrier_internal_adjacency_count": internal,
        "carrier_boundary_adjacency_count": boundary,
        "carrier_external_neighbor_count": external,
        "carrier_induced_degree_histogram": induced_degree_hist(carriers, adj),
        "boundary_neighbor_type_counts": boundary_neighbor_type_counts(carriers, ctypes, adj),
        "mixed_core_count": len(mixed),
        "pentagon_boundary_count": len(pent),
        "mixed_core_internal_adjacency_count": mixint,
        "pentagon_boundary_internal_adjacency_count": pentint,
        "mixed_to_pentagon_boundary_adjacency_count": cross,
        "mixed_core_induced_degree_histogram": induced_degree_hist(mixed, adj),
        "pentagon_boundary_induced_degree_histogram": induced_degree_hist(pent, adj),
    }
    sig["carrier_signature_string"] = carrier_signature_string(sig)
    sig["role_colored_signature_string"] = role_signature_string(sig)
    return sig


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


def assign_roles_type_preferred(patch: Set[str], ctypes: Dict[str, str], ref_mixed_count: int, ref_pent_count: int) -> Tuple[Set[str], Set[str]]:
    patch_sorted = sorted(patch)
    hexes = [c for c in patch_sorted if ctypes.get(c) == "hexagon"]

    mixed = set(hexes[:ref_mixed_count])
    if len(mixed) < ref_mixed_count:
        for c in patch_sorted:
            if c not in mixed:
                mixed.add(c)
                if len(mixed) == ref_mixed_count:
                    break

    remaining = [c for c in patch_sorted if c not in mixed]
    rem_pents = [c for c in remaining if ctypes.get(c) == "pentagon"]
    pent_role = set(rem_pents[:ref_pent_count])
    if len(pent_role) < ref_pent_count:
        for c in remaining:
            if c not in pent_role:
                pent_role.add(c)
                if len(pent_role) == ref_pent_count:
                    break
    return mixed, pent_role


def enumerate_connected_subsets(
    vertices: List[str],
    adj: Dict[str, Set[str]],
    target_size: int,
) -> Iterator[Set[str]]:
    order = {v: i for i, v in enumerate(vertices)}
    seen: Set[Tuple[str, ...]] = set()

    def extend(root_idx: int, current: Set[str], candidates: Set[str], excluded: Set[str]) -> Iterator[Set[str]]:
        if len(current) == target_size:
            key = tuple(sorted(current, key=lambda x: order[x]))
            if key not in seen:
                seen.add(key)
                yield set(current)
            return

        cand_list = sorted(candidates, key=lambda x: order[x])
        local_excluded = set(excluded)

        for v in cand_list:
            if v in local_excluded or v in current:
                continue

            new_current = set(current)
            new_current.add(v)

            new_candidates = set(candidates)
            new_candidates.discard(v)

            for nb in adj.get(v, set()):
                if order[nb] >= root_idx and nb not in new_current and nb not in local_excluded:
                    new_candidates.add(nb)

            yield from extend(root_idx, new_current, new_candidates, local_excluded)
            local_excluded.add(v)

    for root_idx, root in enumerate(vertices):
        candidates = {nb for nb in adj.get(root, set()) if order[nb] >= root_idx}
        yield from extend(root_idx, {root}, candidates, set())


def compute_automorphisms(vertices: List[str], adj: Dict[str, Set[str]], ctypes: Dict[str, str], cfg: Dict[str, Any], warnings: List[Dict[str, str]]) -> List[Dict[str, str]]:
    if not cfg.get("enabled", False):
        return []
    if nx is None or nx_iso is None:
        msg = "networkx unavailable; orbit reduction disabled."
        if cfg.get("require_networkx_for_orbit_reduction", False):
            raise RuntimeError(msg)
        warnings.append({"severity": "warning", "message": msg})
        return []

    max_autos = int(cfg.get("max_automorphisms", 200000))
    timeout = float(cfg.get("timeout_seconds_soft", 60))
    start = time.time()

    G = nx.Graph()
    for v in vertices:
        G.add_node(v, cell_type=ctypes.get(v, "unknown"))
    for a in vertices:
        for b in adj.get(a, set()):
            if a < b:
                G.add_edge(a, b)

    nm = nx_iso.categorical_node_match("cell_type", "unknown")
    gm = nx_iso.GraphMatcher(G, G, node_match=nm)

    autos: List[Dict[str, str]] = []
    for m in gm.isomorphisms_iter():
        autos.append(dict(m))
        if len(autos) >= max_autos:
            warnings.append({"severity": "warning", "message": f"Automorphism enumeration stopped at max_automorphisms={max_autos}."})
            break
        if time.time() - start > timeout:
            warnings.append({"severity": "warning", "message": f"Automorphism enumeration stopped at soft timeout {timeout}s."})
            break
    return autos


def canonical_patch_key(patch: Set[str], automorphisms: List[Dict[str, str]], order: Dict[str, int]) -> Tuple[str, ...]:
    if not automorphisms:
        return tuple(sorted(patch, key=lambda x: order[x]))
    best: Optional[Tuple[str, ...]] = None
    for m in automorphisms:
        image = tuple(sorted((m[x] for x in patch), key=lambda x: order[x]))
        if best is None or image < best:
            best = image
    assert best is not None
    return best


def add_match_example(
    examples: List[Dict[str, Any]],
    max_examples: int,
    scope: str,
    match_type: str,
    patch: Set[str],
    canonical_key: Optional[Tuple[str, ...]],
    sig: Dict[str, Any],
    cdist: int,
    rdist: int,
) -> None:
    if len(examples) >= max_examples:
        return
    examples.append({
        "scope": scope,
        "match_type": match_type,
        "patch_faces": ";".join(sorted(patch)),
        "canonical_patch_faces": ";".join(canonical_key) if canonical_key else "",
        "signature_distance": cdist,
        "role_signature_distance": rdist,
        "carrier_hexagon_count": sig["carrier_hexagon_count"],
        "carrier_pentagon_count": sig["carrier_pentagon_count"],
        "carrier_internal_adjacency_count": sig["carrier_internal_adjacency_count"],
        "carrier_boundary_adjacency_count": sig["carrier_boundary_adjacency_count"],
        "carrier_external_neighbor_count": sig["carrier_external_neighbor_count"],
    })


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    out_dir = root / cfg["run"]["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[Dict[str, str]] = []

    cells = read_csv(root / cfg["inputs"]["c60_cells_csv"])
    edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    frows = read_csv(root / cfg["inputs"]["fu02f1_face_layout_csv"])

    ctypes = {c["cell_id"]: c.get("cell_type", "") for c in cells}
    adj = build_face_graph(edges)
    vertices = sorted(ctypes)
    order = {v: i for i, v in enumerate(vertices)}

    roles = parse_roles(frows, cfg["reference_roles"])
    ref_mixed = {c for c, r in roles.items() if r == "mixed_core"}
    ref_pent = {c for c, r in roles.items() if r == "pentagon_boundary"}
    ref_carriers = ref_mixed | ref_pent
    target_size = len(ref_carriers) if cfg["enumeration"].get("target_patch_size") == "reference" else int(cfg["enumeration"]["target_patch_size"])

    ref_is_connected = is_connected(ref_carriers, adj)
    ref_sig = patch_signature(ref_carriers, ref_mixed, ref_pent, ctypes, adj)
    ref_sig["carrier_set"] = sorted(ref_carriers)
    ref_sig["mixed_core_set"] = sorted(ref_mixed)
    ref_sig["pentagon_boundary_set"] = sorted(ref_pent)
    ref_sig["reference_is_connected"] = ref_is_connected
    write_json(out_dir / "bms_fu02g4c_reference_patch_signature.json", ref_sig)

    autos = compute_automorphisms(vertices, adj, ctypes, cfg.get("orbit_reduction", {}), warnings)
    orbit_enabled_actual = bool(autos)
    orbit_summary = {
        "orbit_reduction_requested": bool(cfg.get("orbit_reduction", {}).get("enabled", False)),
        "orbit_reduction_enabled_actual": orbit_enabled_actual,
        "automorphism_count_used": len(autos),
        "scope_note": "Patch canonical key is minimum sorted automorphic image if automorphisms are available.",
    }

    skip = int(cfg["enumeration"].get("skip_first_raw_patches", 0))
    max_this = int(cfg["enumeration"].get("max_raw_patches_this_run", 1000000))
    timeout = float(cfg["enumeration"].get("timeout_seconds", 900))
    progress_every = int(cfg["enumeration"].get("progress_every", 100000))
    near_threshold = int(cfg["near_signature"].get("max_abs_difference_sum", 2))
    max_examples = int(cfg["enumeration"].get("max_match_examples", 200))
    store_counts = bool(cfg["enumeration"].get("store_signature_counts", True))
    store_orbit_counts = bool(cfg["enumeration"].get("store_orbit_signature_counts", True))

    raw_seen = 0
    raw_processed = 0
    skipped = 0
    status = "complete"
    started = time.time()

    carrier_counts = Counter()
    role_counts = Counter()
    orbit_carrier_counts = Counter()
    orbit_role_counts = Counter()

    unique_orbit_patch_keys: Set[Tuple[str, ...]] = set()
    orbit_match_seen: Set[Tuple[str, ...]] = set()

    raw_counts = Counter()
    orbit_counts = Counter()

    examples: List[Dict[str, Any]] = []
    orbit_examples: List[Dict[str, Any]] = []

    try:
        for patch in enumerate_connected_subsets(vertices, adj, target_size):
            raw_seen += 1

            if raw_seen <= skip:
                skipped += 1
                continue

            if raw_processed >= max_this:
                status = "partial_chunk_limit_reached"
                break
            if time.time() - started > timeout:
                status = "partial_timeout_reached"
                break

            raw_processed += 1
            mixed, pent = assign_roles_type_preferred(patch, ctypes, len(ref_mixed), len(ref_pent))
            sig = patch_signature(patch, mixed, pent, ctypes, adj)
            cdist = signature_distance(sig, ref_sig, role=False)
            rdist = signature_distance(sig, ref_sig, role=True)
            c_exact = sig["carrier_signature_string"] == ref_sig["carrier_signature_string"]
            r_exact = sig["role_colored_signature_string"] == ref_sig["role_colored_signature_string"]
            c_near = cdist <= near_threshold
            r_near = rdist <= near_threshold

            raw_counts["carrier_exact"] += int(c_exact)
            raw_counts["carrier_near"] += int(c_near)
            raw_counts["role_exact"] += int(r_exact)
            raw_counts["role_near"] += int(r_near)

            if store_counts:
                carrier_counts[sig["carrier_signature_string"]] += 1
                role_counts[sig["role_colored_signature_string"]] += 1

            if c_exact or c_near or r_exact or r_near:
                if r_exact:
                    mt = "role_exact"
                elif r_near:
                    mt = "role_near"
                elif c_exact:
                    mt = "carrier_exact"
                else:
                    mt = "carrier_near"
                add_match_example(examples, max_examples, "raw", mt, patch, None, sig, cdist, rdist)

            canonical_key = canonical_patch_key(patch, autos, order) if orbit_enabled_actual else None
            is_new_orbit_class = False
            if canonical_key is not None and canonical_key not in unique_orbit_patch_keys:
                unique_orbit_patch_keys.add(canonical_key)
                is_new_orbit_class = True

                # Use the original patch's signature as class signature proxy. The uncolored
                # signature is automorphism invariant. The deterministic role assignment is
                # label/order dependent, so role-colored orbit counts are best interpreted as
                # v0 canonical-class counts under this assignment, not all possible role colorings.
                orbit_counts["carrier_exact"] += int(c_exact)
                orbit_counts["carrier_near"] += int(c_near)
                orbit_counts["role_exact"] += int(r_exact)
                orbit_counts["role_near"] += int(r_near)

                if store_orbit_counts:
                    orbit_carrier_counts[sig["carrier_signature_string"]] += 1
                    orbit_role_counts[sig["role_colored_signature_string"]] += 1

                if c_exact or c_near or r_exact or r_near:
                    if r_exact:
                        mt = "role_exact"
                    elif r_near:
                        mt = "role_near"
                    elif c_exact:
                        mt = "carrier_exact"
                    else:
                        mt = "carrier_near"
                    add_match_example(orbit_examples, max_examples, "orbit_class", mt, patch, canonical_key, sig, cdist, rdist)

            if progress_every and raw_processed % progress_every == 0:
                print(
                    f"processed={raw_processed} raw_seen={raw_seen} "
                    f"raw_carrier_exact={raw_counts['carrier_exact']} raw_role_exact={raw_counts['role_exact']} "
                    f"orbit_classes={len(unique_orbit_patch_keys)}"
                )

        else:
            status = "complete"

    except Exception as exc:
        status = "partial_runtime_error"
        warnings.append({"severity": "error", "message": f"Runtime error: {exc}"})

    elapsed = time.time() - started

    def frac(n: int, d: int) -> float:
        return n / d if d else 0.0

    chunk_summary = {
        "chunk_id": cfg["run"].get("chunk_id", ""),
        "enumeration_status": status,
        "elapsed_seconds": elapsed,
        "target_patch_size": target_size,
        "reference_is_connected": ref_is_connected,
        "skip_first_raw_patches": skip,
        "raw_patch_count_seen_including_skipped": raw_seen,
        "raw_patch_count_skipped": skipped,
        "raw_connected_patch_count_processed": raw_processed,
        "raw_carrier_signature_exact_match_count": raw_counts["carrier_exact"],
        "raw_carrier_signature_exact_match_fraction": frac(raw_counts["carrier_exact"], raw_processed),
        "raw_carrier_signature_near_match_count": raw_counts["carrier_near"],
        "raw_carrier_signature_near_match_fraction": frac(raw_counts["carrier_near"], raw_processed),
        "raw_role_colored_signature_exact_match_count": raw_counts["role_exact"],
        "raw_role_colored_signature_exact_match_fraction": frac(raw_counts["role_exact"], raw_processed),
        "raw_role_colored_signature_near_match_count": raw_counts["role_near"],
        "raw_role_colored_signature_near_match_fraction": frac(raw_counts["role_near"], raw_processed),
        "near_signature_max_abs_difference_sum": near_threshold,
        "orbit_reduction_enabled_actual": orbit_enabled_actual,
        "automorphism_count_used": len(autos),
        "unique_orbit_patch_count_processed": len(unique_orbit_patch_keys) if orbit_enabled_actual else None,
        "orbit_carrier_signature_exact_match_class_count": orbit_counts["carrier_exact"] if orbit_enabled_actual else None,
        "orbit_carrier_signature_near_match_class_count": orbit_counts["carrier_near"] if orbit_enabled_actual else None,
        "orbit_role_colored_signature_exact_match_class_count": orbit_counts["role_exact"] if orbit_enabled_actual else None,
        "orbit_role_colored_signature_near_match_class_count": orbit_counts["role_near"] if orbit_enabled_actual else None,
        "unique_raw_carrier_signature_count": len(carrier_counts) if store_counts else "",
        "unique_raw_role_colored_signature_count": len(role_counts) if store_counts else "",
        "unique_orbit_carrier_signature_count": len(orbit_carrier_counts) if store_orbit_counts and orbit_enabled_actual else "",
        "unique_orbit_role_colored_signature_count": len(orbit_role_counts) if store_orbit_counts and orbit_enabled_actual else "",
        "scope_note": "Chunk result. Exhaustive only after chunk coverage reaches enumerator completion.",
        "role_assignment_note": "type_preferred_role_assignment; role-colored orbit-class counts are v0 assignment-dependent.",
    }

    write_json(out_dir / "bms_fu02g4c_chunk_summary.json", chunk_summary)
    write_json(out_dir / "bms_fu02g4c_orbit_reduction_summary.json", orbit_summary)
    write_csv(out_dir / "bms_fu02g4c_match_examples.csv", examples, MATCH_FIELDS)
    write_csv(out_dir / "bms_fu02g4c_orbit_match_examples.csv", orbit_examples, MATCH_FIELDS)

    count_rows = []
    if store_counts:
        for sig, count in carrier_counts.most_common():
            count_rows.append({"scope": "raw", "signature_kind": "carrier", "signature_string": sig, "count": count})
        for sig, count in role_counts.most_common():
            count_rows.append({"scope": "raw", "signature_kind": "role_colored", "signature_string": sig, "count": count})
    if store_orbit_counts and orbit_enabled_actual:
        for sig, count in orbit_carrier_counts.most_common():
            count_rows.append({"scope": "orbit_class", "signature_kind": "carrier", "signature_string": sig, "count": count})
        for sig, count in orbit_role_counts.most_common():
            count_rows.append({"scope": "orbit_class", "signature_kind": "role_colored", "signature_string": sig, "count": count})
    if count_rows:
        write_csv(out_dir / "bms_fu02g4c_signature_counts.csv", count_rows, COUNT_FIELDS)

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "chunk_id": cfg["run"].get("chunk_id", ""),
        "output_dir": str(out_dir),
        "enumeration_status": status,
        "target_patch_size": target_size,
        "reference_is_connected": ref_is_connected,
        "skip_first_raw_patches": skip,
        "raw_connected_patch_count_processed": raw_processed,
        "raw_patch_count_seen_including_skipped": raw_seen,
        "orbit_reduction_enabled_actual": orbit_enabled_actual,
        "unique_orbit_patch_count_processed": len(unique_orbit_patch_keys) if orbit_enabled_actual else None,
        "warnings_count": len(warnings),
        "scope_note": "Resumable chunk enumeration. Complete only if enumeration_status == complete and all prior skip ranges are covered.",
    }
    write_json(out_dir / "bms_fu02g4c_run_manifest.json", manifest)
    write_json(out_dir / "bms_fu02g4c_warnings.json", warnings)
    (out_dir / "bms_fu02g4c_config_resolved.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps(chunk_summary, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(w["severity"], "-", w["message"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02g4c orbit-reduced resumable connected patch enumeration.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
