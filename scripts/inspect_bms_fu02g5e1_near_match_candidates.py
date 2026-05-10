#!/usr/bin/env python3
"""
BMS-FU02g5e1 - Near-Match Candidate Localization / Photo

This script inspects configured raw-index windows for v0 type-preferred
role-colored near matches. It intentionally labels the default run as
"scaffold localization" because it reconstructs the deterministic enumerator
from the required face_a / face_b adjacency CSV rather than importing the full
FU02g4c input bundle.

Claim boundary: combinatorial / methodological inspection only. No physical
emergence, uniqueness, or spacetime claim is made.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install it in the project environment.") from exc


CANDIDATE_FIELDS = [
    "window_id",
    "raw_index",
    "candidate_nodes",
    "exact_match",
    "near_distance",
    "role_colored_signature",
    "carrier_signature",
    "internal_edge_count",
    "candidate_connected",
    "h_count",
    "p_count",
    "warnings",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect BMS-FU02g5e1 near-match localization windows."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bms_fu02g5e1_near_match_localization_config.yaml",
    )
    return parser.parse_args()


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root / path


def label_cell_type(node: str) -> str:
    if node.startswith("H_"):
        return "hexagon"
    if node.startswith("P_"):
        return "pentagon"
    return "unknown"


def read_face_graph(path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Face adjacency CSV not found: {path}")

    adj: Dict[str, Set[str]] = defaultdict(set)
    ctypes: Dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        missing = {"face_a", "face_b"} - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"CSV must contain face_a / face_b columns; missing {sorted(missing)}"
            )

        for row in reader:
            face_a = str(row["face_a"]).strip()
            face_b = str(row["face_b"]).strip()
            if not face_a or not face_b:
                continue
            adj[face_a].add(face_b)
            adj[face_b].add(face_a)
            ctypes[face_a] = label_cell_type(face_a)
            ctypes[face_b] = label_cell_type(face_b)

    return dict(adj), ctypes


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")


def components(nodes: Set[str], adj: Dict[str, Set[str]]) -> List[Set[str]]:
    seen: Set[str] = set()
    comps: List[Set[str]] = []
    for node in sorted(nodes):
        if node in seen:
            continue
        queue = deque([node])
        seen.add(node)
        comp = {node}
        while queue:
            current = queue.popleft()
            for nb in adj.get(current, set()):
                if nb in nodes and nb not in seen:
                    seen.add(nb)
                    comp.add(nb)
                    queue.append(nb)
        comps.append(comp)
    return comps


def is_connected(nodes: Set[str], adj: Dict[str, Set[str]]) -> bool:
    return bool(nodes) and len(components(nodes, adj)) == 1


def adjacency_counts(carriers: Set[str], adj: Dict[str, Set[str]]) -> Tuple[int, int, int]:
    internal = 0
    boundary = 0
    external: Set[str] = set()
    seen: Set[Tuple[str, str]] = set()
    for node in carriers:
        for nb in adj.get(node, set()):
            pair = tuple(sorted((node, nb)))
            if pair in seen:
                continue
            seen.add(pair)
            if nb in carriers:
                internal += 1
            else:
                boundary += 1
                external.add(nb)
    return internal, boundary, len(external)


def induced_degree_hist(nodes: Set[str], adj: Dict[str, Set[str]]) -> Dict[str, int]:
    counts = Counter()
    for node in nodes:
        degree = sum(1 for nb in adj.get(node, set()) if nb in nodes)
        counts[degree] += 1
    return {str(key): value for key, value in sorted(counts.items())}


def boundary_neighbor_type_counts(
    carriers: Set[str],
    ctypes: Dict[str, str],
    adj: Dict[str, Set[str]],
) -> Dict[str, int]:
    counts = Counter()
    for node in carriers:
        for nb in adj.get(node, set()):
            if nb not in carriers:
                counts[ctypes.get(nb, "unknown")] += 1
    return dict(sorted(counts.items()))


def role_adjacency_counts(
    mixed: Set[str],
    pent: Set[str],
    adj: Dict[str, Set[str]],
) -> Tuple[int, int, int]:
    role = {node: "mixed" for node in mixed}
    role.update({node: "pentagon_boundary" for node in pent})
    seen: Set[Tuple[str, str]] = set()
    mixed_internal = 0
    pent_internal = 0
    cross = 0
    for node in role:
        for nb in adj.get(node, set()):
            if nb not in role:
                continue
            pair = tuple(sorted((node, nb)))
            if pair in seen:
                continue
            seen.add(pair)
            if role[node] == role[nb] == "mixed":
                mixed_internal += 1
            elif role[node] == role[nb] == "pentagon_boundary":
                pent_internal += 1
            else:
                cross += 1
    return mixed_internal, pent_internal, cross


def carrier_signature_string(sig: Dict[str, Any]) -> str:
    return "|".join(
        [
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
        ]
    )


def role_signature_string(sig: Dict[str, Any]) -> str:
    return "|".join(
        [
            carrier_signature_string(sig),
            f"mixed={sig['mixed_core_count']}",
            f"pentrole={sig['pentagon_boundary_count']}",
            f"mixint={sig['mixed_core_internal_adjacency_count']}",
            f"pentint={sig['pentagon_boundary_internal_adjacency_count']}",
            f"mixpent={sig['mixed_to_pentagon_boundary_adjacency_count']}",
            f"mixdeg={json.dumps(sig['mixed_core_induced_degree_histogram'], sort_keys=True)}",
            f"pentdeg={json.dumps(sig['pentagon_boundary_induced_degree_histogram'], sort_keys=True)}",
        ]
    )


def patch_signature(
    carriers: Set[str],
    mixed: Set[str],
    pent: Set[str],
    ctypes: Dict[str, str],
    adj: Dict[str, Set[str]],
) -> Dict[str, Any]:
    comps = components(carriers, adj)
    internal, boundary, external = adjacency_counts(carriers, adj)
    mixint, pentint, cross = role_adjacency_counts(mixed, pent, adj)
    sig: Dict[str, Any] = {
        "carrier_face_count": len(carriers),
        "carrier_hexagon_count": sum(1 for node in carriers if ctypes.get(node) == "hexagon"),
        "carrier_pentagon_count": sum(1 for node in carriers if ctypes.get(node) == "pentagon"),
        "carrier_component_count": len(comps),
        "largest_carrier_component_count": max((len(comp) for comp in comps), default=0),
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
        "carrier_hexagon_count",
        "carrier_pentagon_count",
        "carrier_component_count",
        "largest_carrier_component_count",
        "carrier_internal_adjacency_count",
        "carrier_boundary_adjacency_count",
        "carrier_external_neighbor_count",
    ]
    if role:
        keys += [
            "mixed_core_count",
            "pentagon_boundary_count",
            "mixed_core_internal_adjacency_count",
            "pentagon_boundary_internal_adjacency_count",
            "mixed_to_pentagon_boundary_adjacency_count",
        ]
    return sum(abs(int(a.get(key, 0)) - int(b.get(key, 0))) for key in keys)


def assign_roles_type_preferred(
    patch: Set[str],
    ctypes: Dict[str, str],
    ref_mixed_count: int,
    ref_pent_count: int,
) -> Tuple[Set[str], Set[str]]:
    patch_sorted = sorted(patch)
    hexes = [node for node in patch_sorted if ctypes.get(node) == "hexagon"]

    mixed = set(hexes[:ref_mixed_count])
    if len(mixed) < ref_mixed_count:
        for node in patch_sorted:
            if node not in mixed:
                mixed.add(node)
                if len(mixed) == ref_mixed_count:
                    break

    remaining = [node for node in patch_sorted if node not in mixed]
    rem_pents = [node for node in remaining if ctypes.get(node) == "pentagon"]
    pent_role = set(rem_pents[:ref_pent_count])
    if len(pent_role) < ref_pent_count:
        for node in remaining:
            if node not in pent_role:
                pent_role.add(node)
                if len(pent_role) == ref_pent_count:
                    break
    return mixed, pent_role


def enumerate_connected_subsets(
    vertices: List[str],
    adj: Dict[str, Set[str]],
    target_size: int,
) -> Iterator[Set[str]]:
    order = {vertex: index for index, vertex in enumerate(vertices)}
    seen: Set[Tuple[str, ...]] = set()

    def extend(
        root_idx: int,
        current: Set[str],
        candidates: Set[str],
        excluded: Set[str],
    ) -> Iterator[Set[str]]:
        if len(current) == target_size:
            key = tuple(sorted(current, key=lambda item: order[item]))
            if key not in seen:
                seen.add(key)
                yield set(current)
            return

        cand_list = sorted(candidates, key=lambda item: order[item])
        local_excluded = set(excluded)

        for vertex in cand_list:
            if vertex in local_excluded or vertex in current:
                continue

            new_current = set(current)
            new_current.add(vertex)

            new_candidates = set(candidates)
            new_candidates.discard(vertex)

            for nb in adj.get(vertex, set()):
                if (
                    order[nb] >= root_idx
                    and nb not in new_current
                    and nb not in local_excluded
                ):
                    new_candidates.add(nb)

            yield from extend(root_idx, new_current, new_candidates, local_excluded)
            local_excluded.add(vertex)

    for root_idx, root in enumerate(vertices):
        candidates = {nb for nb in adj.get(root, set()) if order[nb] >= root_idx}
        yield from extend(root_idx, {root}, candidates, set())


def normalize_windows(windows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for window in windows:
        start = int(window["skip_first_raw_patches"])
        count = int(window["max_raw_patches_this_run"])
        out.append(
            {
                "window_id": str(window["window_id"]),
                "start": start,
                "end_exclusive": start + count,
                "max_raw_patches_this_run": count,
            }
        )
    return sorted(out, key=lambda item: item["start"])


def candidate_warnings(patch: Set[str], patch_size: int, adj: Dict[str, Set[str]]) -> List[str]:
    warnings: List[str] = []
    if len(patch) != patch_size:
        warnings.append(f"patch_size_observed={len(patch)} expected={patch_size}")
    if not is_connected(patch, adj):
        warnings.append("candidate_not_connected")
    return warnings


def make_candidate_row(
    window_id: str,
    raw_index: int,
    patch: Set[str],
    sig: Dict[str, Any],
    exact_match: bool,
    near_distance: int,
    patch_size: int,
    adj: Dict[str, Set[str]],
) -> Dict[str, Any]:
    warnings = candidate_warnings(patch, patch_size, adj)
    return {
        "window_id": window_id,
        "raw_index": raw_index,
        "candidate_nodes": ";".join(sorted(patch)),
        "exact_match": exact_match,
        "near_distance": near_distance,
        "role_colored_signature": sig["role_colored_signature_string"],
        "carrier_signature": sig["carrier_signature_string"],
        "internal_edge_count": sig["carrier_internal_adjacency_count"],
        "candidate_connected": is_connected(patch, adj),
        "h_count": sig["carrier_hexagon_count"],
        "p_count": sig["carrier_pentagon_count"],
        "warnings": ";".join(warnings),
    }


def build_result_note(summary: Dict[str, Any]) -> str:
    mode_label = summary["metadata"]["mode_label"]
    total_candidates = summary["summary"]["near_match_candidate_count"]
    exact_count = summary["summary"]["exact_match_count"]
    max_index = summary["summary"]["max_raw_index_visited"]
    order_guarantee = summary["method"]["fu02g4c_order_guarantee"]

    return f"""# BMS-FU02g5e1 - Near-Match Localization Result Note

Datum: {summary["metadata"]["created_at_utc"][:10]}

## Befund

Run label:

```text
{mode_label}
```

Targeted raw-index windows were inspected with the v0 type-preferred
role-colored diagnostic.

```text
near_match_candidate_count = {total_candidates}
exact_match_count = {exact_count}
max_raw_index_visited = {max_index}
fu02g4c_order_guarantee = {order_guarantee}
```

## Interpretation

The script reuses the FU02g4c-style sorted-root connected 17-face patch
enumerator and the v0 type-preferred role assignment. However, this run is fed
from the repaired `face_a` / `face_b` adjacency CSV. Because that is not the
full original FU02g4c input bundle, exact FU02g4c replay order is not claimed.

Therefore this output is a scaffold localization/photo pass, not a final
FU02g4c replay audit.

## Hypothese

The localized near-match candidates are candidate objects for a later
order-audited replay. If the exact FU02g4c input ordering is re-established,
the same windows should be rerun with a replay label rather than scaffold label.

## Offene Luecke

The open methodological gap is exact raw-order certification against the
original FU02g4c enumeration inputs. Until that is closed, raw indices in this
note are scaffold-enumerator indices.

## Claim Boundary

This note reports a combinatorial diagnostic only.

Not claimed:

```text
physical emergence
spacetime emergence
uniqueness
FU02g4c exact replay certification
```
"""


def run(config_path: Path) -> None:
    repo_root = Path.cwd()
    cfg = read_yaml(config_path)
    run_cfg = cfg["run"]
    input_cfg = cfg["input"]
    output_dir = resolve_path(repo_root, run_cfg["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    adj, ctypes = read_face_graph(resolve_path(repo_root, input_cfg["full_face_graph_edges_csv"]))
    vertices = sorted(ctypes)
    patch_size = int(run_cfg.get("patch_size", 17))
    progress_every = int(run_cfg.get("progress_every", 0))
    windows = normalize_windows(cfg["windows"])
    max_end = max(window["end_exclusive"] for window in windows)

    ref_carrier = {str(node) for node in input_cfg["reference_carrier_nodes"]}
    ref_mixed = {str(node) for node in input_cfg["reference_mixed_core_nodes"]}
    ref_pent = {str(node) for node in input_cfg["reference_pentagon_boundary_nodes"]}
    ref_sig = patch_signature(ref_carrier, ref_mixed, ref_pent, ctypes, adj)
    near_threshold = int(cfg["near_signature"]["near_signature_max_abs_difference_sum"])

    rows: List[Dict[str, Any]] = []
    window_counts = {window["window_id"]: 0 for window in windows}
    exact_count = 0
    started = time.time()
    max_raw_index_visited = -1

    active_window_idx = 0
    for raw_index, patch in enumerate(enumerate_connected_subsets(vertices, adj, patch_size)):
        if raw_index >= max_end:
            break
        max_raw_index_visited = raw_index

        while (
            active_window_idx < len(windows)
            and raw_index >= windows[active_window_idx]["end_exclusive"]
        ):
            active_window_idx += 1
        if active_window_idx >= len(windows):
            break

        window = windows[active_window_idx]
        if raw_index < window["start"]:
            if progress_every and raw_index > 0 and raw_index % progress_every == 0:
                print(f"visited_raw_index={raw_index} candidates={len(rows)}")
            continue

        mixed, pent = assign_roles_type_preferred(
            patch,
            ctypes,
            len(ref_mixed),
            len(ref_pent),
        )
        sig = patch_signature(patch, mixed, pent, ctypes, adj)
        near_distance = signature_distance(sig, ref_sig, role=True)
        exact_match = (
            sig["role_colored_signature_string"] == ref_sig["role_colored_signature_string"]
        )
        if near_distance <= near_threshold:
            row = make_candidate_row(
                window["window_id"],
                raw_index,
                patch,
                sig,
                exact_match,
                near_distance,
                patch_size,
                adj,
            )
            rows.append(row)
            window_counts[window["window_id"]] += 1
            exact_count += int(exact_match)

        if progress_every and raw_index > 0 and raw_index % progress_every == 0:
            print(f"visited_raw_index={raw_index} candidates={len(rows)}")

    elapsed = time.time() - started
    summary = {
        "metadata": {
            "run_id": run_cfg["run_id"],
            "case_id": run_cfg["case_id"],
            "mode_label": run_cfg.get("mode_label", "scaffold localization"),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "script": "scripts/inspect_bms_fu02g5e1_near_match_candidates.py",
        },
        "method": {
            "enumerator": "FU02g4c-style sorted-root connected-subset scaffold",
            "role_assignment": "v0 type-preferred",
            "fu02g4c_order_guarantee": False,
            "order_boundary": (
                "Exact FU02g4c order is not guaranteed because this run uses "
                "the required face_a/face_b adjacency CSV as its graph source."
            ),
        },
        "input": {
            "full_face_graph_edges_csv": str(
                resolve_path(repo_root, input_cfg["full_face_graph_edges_csv"])
            ),
            "reference_carrier_nodes": sorted(ref_carrier),
            "reference_mixed_core_nodes": sorted(ref_mixed),
            "reference_pentagon_boundary_nodes": sorted(ref_pent),
            "near_signature_max_abs_difference_sum": near_threshold,
            "windows": windows,
        },
        "summary": {
            "near_match_candidate_count": len(rows),
            "exact_match_count": exact_count,
            "candidate_count_by_window": window_counts,
            "max_raw_index_visited": max_raw_index_visited,
            "elapsed_seconds": elapsed,
        },
        "claim_boundary": {
            "physical_emergence_claim": False,
            "spacetime_claim": False,
            "uniqueness_claim": False,
        },
        "candidates": rows,
    }

    write_csv(output_dir / "near_match_candidates.csv", rows, CANDIDATE_FIELDS)
    write_json(output_dir / "near_match_candidates.json", summary)
    with (output_dir / "result_note.md").open("w", encoding="utf-8") as handle:
        handle.write(build_result_note(summary))

    print(
        "BMS-FU02g5e1 complete: "
        f"candidates={len(rows)}, exact={exact_count}, output_dir={output_dir}"
    )


def main() -> int:
    args = parse_args()
    run(Path(args.config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
