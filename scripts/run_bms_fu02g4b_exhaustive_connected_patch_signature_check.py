#!/usr/bin/env python3
"""
# PATCH_MARKER: FU02G4B_ENUMERATOR_PATCHED_V2_REFERENCE_CONNECTED_GUARD

BMS-FU02g4b — Exhaustive Connected Patch Signature Check

Patched version 2026-05-03.

Purpose:
  Enumerate connected same-size C60 face patches and count exact/near reference
  patch-signature matches.

Important:
  Exhaustive only if enumeration_status == complete.
  If zero patches are emitted although the reference patch is connected, the run
  is marked partial_runtime_error rather than complete.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterable, Iterator, List, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


MATCH_FIELDS = [
    "match_type", "patch_faces", "carrier_signature_string",
    "role_colored_signature_string", "signature_distance",
    "role_signature_distance", "carrier_hexagon_count",
    "carrier_pentagon_count", "carrier_internal_adjacency_count",
    "carrier_boundary_adjacency_count", "carrier_external_neighbor_count",
]
COUNT_FIELDS = [
    "signature_kind", "signature_string", "count",
]


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
    max_patches: int,
    timeout_seconds: float,
) -> Iterator[Set[str]]:
    """
    Enumerate connected vertex subsets of target_size.

    Patch note:
      The previous v0 pruned on len(current)+len(frontier), which is invalid
      because a frontier can grow. That made the run emit zero patches. This
      implementation does not use that invalid prune.

    Duplicate control:
      - root is the minimum ordered vertex of the patch
      - a seen key suppresses duplicate emissions across expansion orders
    """
    order = {v: i for i, v in enumerate(vertices)}
    seen: Set[Tuple[str, ...]] = set()
    start = time.time()

    def extend(root_idx: int, current: Set[str], candidates: Set[str], excluded: Set[str]) -> Iterator[Set[str]]:
        if len(current) == target_size:
            key = tuple(sorted(current, key=lambda x: order[x]))
            if key not in seen:
                seen.add(key)
                yield set(current)
            return

        # Hard time/cap control is checked by caller too; local time check
        # prevents deep recursion from running far beyond timeout.
        if time.time() - start > timeout_seconds:
            return

        # Deterministic branch order.
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
                if (
                    order[nb] >= root_idx
                    and nb not in new_current
                    and nb not in local_excluded
                ):
                    new_candidates.add(nb)

            yield from extend(root_idx, new_current, new_candidates, local_excluded)

            # Exclude v for subsequent sibling branches at this recursion level.
            local_excluded.add(v)

    emitted = 0
    for root_idx, root in enumerate(vertices):
        candidates = {nb for nb in adj.get(root, set()) if order[nb] >= root_idx}
        for patch in extend(root_idx, {root}, candidates, set()):
            yield patch
            emitted += 1
            if emitted >= max_patches:
                return
            if time.time() - start > timeout_seconds:
                return


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

    roles = parse_roles(frows, cfg["reference_roles"])
    ref_mixed = {c for c, r in roles.items() if r == "mixed_core"}
    ref_pent = {c for c, r in roles.items() if r == "pentagon_boundary"}
    ref_carriers = ref_mixed | ref_pent
    target_size = len(ref_carriers) if cfg["enumeration"].get("target_patch_size") == "reference" else int(cfg["enumeration"]["target_patch_size"])

    ref_is_connected = is_connected(ref_carriers, adj)
    if not ref_is_connected:
        warnings.append({"severity": "warning", "message": "Reference carrier set is not connected under current face adjacency graph."})

    ref_sig = patch_signature(ref_carriers, ref_mixed, ref_pent, ctypes, adj)
    ref_sig["carrier_set"] = sorted(ref_carriers)
    ref_sig["mixed_core_set"] = sorted(ref_mixed)
    ref_sig["pentagon_boundary_set"] = sorted(ref_pent)
    ref_sig["reference_is_connected"] = ref_is_connected
    write_json(out_dir / "bms_fu02g4b_reference_patch_signature.json", ref_sig)

    max_patches = int(cfg["enumeration"].get("max_patches", 5000000))
    timeout_seconds = float(cfg["enumeration"].get("timeout_seconds", 900))
    progress_every = int(cfg["enumeration"].get("progress_every", 100000))
    near_threshold = int(cfg["near_signature"].get("max_abs_difference_sum", 2))
    max_examples = int(cfg["enumeration"].get("max_match_examples", 200))
    store_counts = bool(cfg["enumeration"].get("store_patch_signature_counts", True))

    carrier_counts = Counter()
    role_counts = Counter()
    match_examples: List[Dict[str, Any]] = []
    total = 0
    carrier_exact = 0
    carrier_near = 0
    role_exact = 0
    role_near = 0
    status = "complete"
    started = time.time()

    try:
        for patch in enumerate_connected_subsets(vertices, adj, target_size, max_patches, timeout_seconds):
            total += 1
            mixed, pent = assign_roles_type_preferred(patch, ctypes, len(ref_mixed), len(ref_pent))
            sig = patch_signature(patch, mixed, pent, ctypes, adj)
            cdist = signature_distance(sig, ref_sig, role=False)
            rdist = signature_distance(sig, ref_sig, role=True)
            c_exact = sig["carrier_signature_string"] == ref_sig["carrier_signature_string"]
            r_exact = sig["role_colored_signature_string"] == ref_sig["role_colored_signature_string"]
            c_near = cdist <= near_threshold
            r_near = rdist <= near_threshold

            carrier_exact += int(c_exact)
            carrier_near += int(c_near)
            role_exact += int(r_exact)
            role_near += int(r_near)

            if store_counts:
                carrier_counts[sig["carrier_signature_string"]] += 1
                role_counts[sig["role_colored_signature_string"]] += 1

            if (c_exact or r_exact or c_near or r_near) and len(match_examples) < max_examples:
                if r_exact:
                    mtype = "role_exact"
                elif r_near:
                    mtype = "role_near"
                elif c_exact:
                    mtype = "carrier_exact"
                else:
                    mtype = "carrier_near"
                match_examples.append({
                    "match_type": mtype,
                    "patch_faces": ";".join(sorted(patch)),
                    "carrier_signature_string": sig["carrier_signature_string"],
                    "role_colored_signature_string": sig["role_colored_signature_string"],
                    "signature_distance": cdist,
                    "role_signature_distance": rdist,
                    "carrier_hexagon_count": sig["carrier_hexagon_count"],
                    "carrier_pentagon_count": sig["carrier_pentagon_count"],
                    "carrier_internal_adjacency_count": sig["carrier_internal_adjacency_count"],
                    "carrier_boundary_adjacency_count": sig["carrier_boundary_adjacency_count"],
                    "carrier_external_neighbor_count": sig["carrier_external_neighbor_count"],
                })

            if progress_every and total % progress_every == 0:
                print(f"enumerated={total} carrier_exact={carrier_exact} role_exact={role_exact}")

            if total >= max_patches:
                status = "partial_max_patches_reached"
                break
            if time.time() - started > timeout_seconds:
                status = "partial_timeout_reached"
                break

    except Exception as exc:
        status = "partial_runtime_error"
        warnings.append({"severity": "error", "message": f"Enumeration runtime error: {exc}"})

    elapsed = time.time() - started

    # Guard against the previous false-complete failure mode.
    if total == 0 and ref_is_connected:
        status = "partial_runtime_error"
        warnings.append({
            "severity": "error",
            "message": "Enumerator emitted zero patches although reference carrier set is connected. Result is not interpretable."
        })

    if status == "complete":
        diagnostic_label = "complete_no_role_signature_match" if role_exact == 0 and role_near == 0 else "complete_role_signature_reproduced"
    else:
        diagnostic_label = "partial_no_role_signature_match_so_far" if role_exact == 0 and role_near == 0 else "partial_role_signature_reproduced"

    enumeration_summary = {
        "enumeration_status": status,
        "elapsed_seconds": elapsed,
        "target_patch_size": target_size,
        "reference_is_connected": ref_is_connected,
        "enumerated_connected_patch_count": total,
        "carrier_signature_exact_match_count": carrier_exact,
        "carrier_signature_exact_match_fraction": carrier_exact / total if total else 0.0,
        "carrier_signature_near_match_count": carrier_near,
        "carrier_signature_near_match_fraction": carrier_near / total if total else 0.0,
        "role_colored_signature_exact_match_count": role_exact,
        "role_colored_signature_exact_match_fraction": role_exact / total if total else 0.0,
        "role_colored_signature_near_match_count": role_near,
        "role_colored_signature_near_match_fraction": role_near / total if total else 0.0,
        "near_signature_max_abs_difference_sum": near_threshold,
        "unique_carrier_signature_count": len(carrier_counts) if store_counts else "",
        "unique_role_colored_signature_count": len(role_counts) if store_counts else "",
        "diagnostic_label": diagnostic_label,
        "scope_note": "Exhaustive only if enumeration_status == complete. Role assignment is deterministic type-preferred v0.",
    }
    write_json(out_dir / "bms_fu02g4b_enumeration_summary.json", enumeration_summary)
    write_csv(out_dir / "bms_fu02g4b_match_examples.csv", match_examples, MATCH_FIELDS)

    count_rows = []
    if store_counts:
        for sig, count in carrier_counts.most_common():
            count_rows.append({"signature_kind": "carrier", "signature_string": sig, "count": count})
        for sig, count in role_counts.most_common():
            count_rows.append({"signature_kind": "role_colored", "signature_string": sig, "count": count})
        write_csv(out_dir / "bms_fu02g4b_patch_signature_counts.csv", count_rows, COUNT_FIELDS)

    sig_count_summary = {
        "store_patch_signature_counts": store_counts,
        "unique_carrier_signature_count": len(carrier_counts) if store_counts else None,
        "unique_role_colored_signature_count": len(role_counts) if store_counts else None,
        "top_carrier_signatures": carrier_counts.most_common(10) if store_counts else [],
        "top_role_colored_signatures": role_counts.most_common(10) if store_counts else [],
    }
    write_json(out_dir / "bms_fu02g4b_signature_count_summary.json", sig_count_summary)

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": str(out_dir),
        "enumeration_status": status,
        "target_patch_size": target_size,
        "reference_is_connected": ref_is_connected,
        "enumerated_connected_patch_count": total,
        "warnings_count": len(warnings),
        "scope_note": "Exhaustive connected-patch signature check if status is complete; otherwise bounded enumeration.",
    }
    write_json(out_dir / "bms_fu02g4b_run_manifest.json", manifest)
    write_json(out_dir / "bms_fu02g4b_warnings.json", warnings)
    (out_dir / "bms_fu02g4b_config_resolved.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps(enumeration_summary, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(w["severity"], "-", w["message"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02g4b exhaustive connected patch signature check.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
