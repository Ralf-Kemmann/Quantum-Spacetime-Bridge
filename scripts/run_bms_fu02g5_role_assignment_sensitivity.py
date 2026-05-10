#!/usr/bin/env python3
"""
BMS-FU02g5 — Role-Assignment Sensitivity Controls

Project: Quantum–Spacetime Bridge / Gravitation und RaumZeit
Date: 2026-05-06

Purpose
-------
Test whether role-colored signature behavior is stable or fragile under explicitly
defined role-assignment variants in the C60 face-graph control space.

Claim boundary
--------------
This script performs a combinatorial / methodological sensitivity test only.
It does not infer physical dynamics, physical emergence, or universal uniqueness.

Inputs
------
YAML config with:
- C60 face-graph edge CSV
- FU02f1 reference carrier and role sets
- localized FU02g4c exact patch and transported role sets
- role-assignment variants
- optional connected-patch enumeration window controls

Outputs
-------
- summary.json
- variant_summary.csv
- candidate_pair_summary.csv
- result_note.md
- config_resolved.yaml
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: PyYAML. Install with `python -m pip install pyyaml` "
        "inside the project virtual environment."
    ) from exc

try:
    import networkx as nx  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: networkx. Install with `python -m pip install networkx` "
        "inside the project virtual environment."
    ) from exc


ROLE_MIXED = "mixed_seam_boundary_face"
ROLE_BOUNDARY = "hp_boundary_face"
ROLE_CARRIER_OTHER = "carrier_other"
ROLE_CARRIER = "carrier"
ROLE_OUTSIDE = "outside"
ROLE_HEX = "hexagon_face"
ROLE_PENT = "pentagon_face"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BMS-FU02g5 role-assignment sensitivity controls."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bms_fu02g5_role_assignment_sensitivity_config.yaml",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_yaml(path: Path, obj: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(obj, handle, sort_keys=False, allow_unicode=True)


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_edge_csv(path: Path) -> "nx.Graph":
    if not path.exists():
        raise FileNotFoundError(
            f"C60 face-graph edge CSV not found: {path}. "
            "Edit input.full_face_graph_edges_csv in the FU02g5 config."
        )

    graph = nx.Graph()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or len(reader.fieldnames) < 2:
            raise ValueError(f"Edge CSV has fewer than two columns: {path}")

        fields = list(reader.fieldnames)
        field_set = set(fields)

        preferred_pairs = [
            ("source", "target"),
            ("src", "dst"),
            ("u", "v"),
            ("node_a", "node_b"),
            ("face_a", "face_b"),
        ]

        source_col = None
        target_col = None
        for left, right in preferred_pairs:
            if left in field_set and right in field_set:
                source_col, target_col = left, right
                break

        if source_col is None or target_col is None:
            raise ValueError(
                f"Could not identify edge endpoint columns in {path}. "
                f"Known pairs are {preferred_pairs}; found columns are {fields}."
            )

        for row in reader:
            source = str(row[source_col]).strip()
            target = str(row[target_col]).strip()
            if not source or not target:
                continue
            graph.add_edge(source, target)

    graph.graph["edge_csv_path"] = str(path)
    graph.graph["edge_source_col"] = source_col
    graph.graph["edge_target_col"] = target_col
    return graph


def node_face_type(node: str) -> str:
    if node.startswith("H_"):
        return "H"
    if node.startswith("P_"):
        return "P"
    return "unknown"


def face_type_counts(nodes: Iterable[str]) -> Dict[str, int]:
    return dict(Counter(node_face_type(node) for node in nodes))


def induced_stats(graph: "nx.Graph", nodes: Sequence[str]) -> dict:
    sub = graph.subgraph(nodes).copy()
    missing = sorted(set(nodes) - set(graph.nodes()))
    connected = nx.is_connected(sub) if sub.number_of_nodes() > 0 else False
    return {
        "node_count": len(nodes),
        "edge_count": sub.number_of_edges(),
        "connected": bool(connected),
        "face_type_counts": face_type_counts(nodes),
        "missing_nodes": missing,
    }


def validate_patch_nodes(
    graph: "nx.Graph",
    nodes: Sequence[str],
    expected_size: int,
    label: str,
    warnings: List[str],
) -> None:
    if len(nodes) != expected_size:
        warnings.append(f"{label}: expected {expected_size} nodes, observed {len(nodes)}.")
    missing = sorted(set(nodes) - set(graph.nodes()))
    if missing:
        warnings.append(f"{label}: nodes missing from graph: {missing}.")
    present_nodes = [node for node in nodes if node in graph.nodes()]
    if present_nodes:
        sub = graph.subgraph(present_nodes)
        if not nx.is_connected(sub):
            warnings.append(f"{label}: induced present-node subgraph is not connected.")
    else:
        warnings.append(f"{label}: no nodes are present in the graph.")


def build_role_map(
    *,
    carrier_nodes: Sequence[str],
    mixed_core_nodes: Sequence[str],
    pentagon_boundary_nodes: Sequence[str],
    all_graph_nodes: Sequence[str],
    mode: str,
    random_seed: Optional[int] = None,
) -> Dict[str, str]:
    carrier_set = set(carrier_nodes)
    mixed_set = set(mixed_core_nodes)
    boundary_set = set(pentagon_boundary_nodes)
    role_map: Dict[str, str] = {}

    if mode == "v0_type_preferred":
        for node in all_graph_nodes:
            if node in mixed_set:
                role_map[node] = ROLE_MIXED
            elif node in boundary_set:
                role_map[node] = ROLE_BOUNDARY
            elif node in carrier_set:
                role_map[node] = ROLE_CARRIER_OTHER
            else:
                role_map[node] = ROLE_OUTSIDE

    elif mode == "uncolored_carrier_only":
        for node in all_graph_nodes:
            role_map[node] = ROLE_CARRIER if node in carrier_set else ROLE_OUTSIDE

    elif mode == "face_type_only":
        for node in all_graph_nodes:
            ft = node_face_type(node)
            if ft == "H":
                role_map[node] = ROLE_HEX
            elif ft == "P":
                role_map[node] = ROLE_PENT
            else:
                role_map[node] = "unknown_face"

    elif mode == "swap_core_boundary":
        for node in all_graph_nodes:
            if node in mixed_set:
                role_map[node] = ROLE_BOUNDARY
            elif node in boundary_set:
                role_map[node] = ROLE_MIXED
            elif node in carrier_set:
                role_map[node] = ROLE_CARRIER_OTHER
            else:
                role_map[node] = ROLE_OUTSIDE

    elif mode == "core_erased":
        for node in all_graph_nodes:
            if node in boundary_set:
                role_map[node] = ROLE_BOUNDARY
            elif node in carrier_set:
                role_map[node] = ROLE_CARRIER_OTHER
            else:
                role_map[node] = ROLE_OUTSIDE

    elif mode == "boundary_erased":
        for node in all_graph_nodes:
            if node in mixed_set:
                role_map[node] = ROLE_MIXED
            elif node in carrier_set:
                role_map[node] = ROLE_CARRIER_OTHER
            else:
                role_map[node] = ROLE_OUTSIDE

    elif mode == "random_role_permutation_seeded":
        if random_seed is None:
            raise ValueError("random_role_permutation_seeded requires random_seed.")
        rng = random.Random(random_seed)
        carrier_list = list(carrier_nodes)
        baseline_roles = []
        for node in carrier_list:
            if node in mixed_set:
                baseline_roles.append(ROLE_MIXED)
            elif node in boundary_set:
                baseline_roles.append(ROLE_BOUNDARY)
            else:
                baseline_roles.append(ROLE_CARRIER_OTHER)
        rng.shuffle(baseline_roles)
        shuffled = dict(zip(carrier_list, baseline_roles))
        for node in all_graph_nodes:
            role_map[node] = shuffled.get(node, ROLE_OUTSIDE)

    else:
        raise ValueError(f"Unsupported role assignment mode: {mode}")

    return role_map


def role_degree_histogram(graph: "nx.Graph", nodes: Sequence[str], role_map: Dict[str, str]) -> Counter:
    sub = graph.subgraph(nodes)
    hist: Counter = Counter()
    for node in sub.nodes():
        role = role_map.get(node, ROLE_OUTSIDE)
        degree = sub.degree(node)
        hist[(role, int(degree))] += 1
    return hist


def histogram_distance(a: Counter, b: Counter) -> int:
    keys = set(a.keys()) | set(b.keys())
    return int(sum(abs(a.get(key, 0) - b.get(key, 0)) for key in keys))


def fallback_signature(graph: "nx.Graph", nodes: Sequence[str], role_map: Dict[str, str]) -> str:
    sub = graph.subgraph(nodes)
    degree_sequence = sorted(int(deg) for _, deg in sub.degree())
    hist_items = sorted(
        (str(role), int(degree), int(count))
        for (role, degree), count in role_degree_histogram(graph, nodes, role_map).items()
    )
    edge_count = int(sub.number_of_edges())
    payload = {
        "node_count": len(nodes),
        "edge_count": edge_count,
        "degree_sequence": degree_sequence,
        "role_degree_histogram": hist_items,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "fallback_sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def role_colored_signature(graph: "nx.Graph", nodes: Sequence[str], role_map: Dict[str, str]) -> str:
    sub = graph.subgraph(nodes).copy()
    for node in sub.nodes():
        sub.nodes[node]["role"] = role_map.get(node, ROLE_OUTSIDE)

    try:
        # NetworkX >= 2.8 usually provides this function.
        from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash

        return "wl:" + weisfeiler_lehman_graph_hash(sub, node_attr="role")
    except Exception:
        return fallback_signature(graph, nodes, role_map)


def connected_k_subgraphs(
    graph: "nx.Graph",
    k: int,
    skip_first: int = 0,
    max_count: Optional[int] = None,
    max_wall_seconds: Optional[float] = None,
) -> Iterator[Tuple[int, Tuple[str, ...], bool]]:
    """Yield connected k-node subsets with deterministic duplicate suppression.

    This is a transparent scaffold enumerator, not an optimized orbit-reduced runner.
    For large primary-scale enumeration, use chunking and/or the existing optimized
    project runner family.

    Yields:
        raw_index, node_tuple, partial_stop_flag
    """
    start_time = time.monotonic()
    nodes_sorted = sorted(graph.nodes())
    seen: Set[Tuple[str, ...]] = set()
    raw_index = -1
    emitted = 0

    for root in nodes_sorted:
        root_rank = nodes_sorted.index(root)
        root_allowed = set(nodes_sorted[root_rank:])

        stack: List[Tuple[frozenset, frozenset]] = [
            (frozenset([root]), frozenset(n for n in graph.neighbors(root) if n in root_allowed))
        ]

        while stack:
            if max_wall_seconds is not None and (time.monotonic() - start_time) >= max_wall_seconds:
                return

            current, frontier = stack.pop()
            if len(current) == k:
                patch = tuple(sorted(current))
                if patch in seen:
                    continue
                seen.add(patch)
                raw_index += 1
                if raw_index < skip_first:
                    continue
                if max_count is not None and emitted >= max_count:
                    return
                emitted += 1
                yield raw_index, patch, False
                continue

            # Do not prune on len(current) + len(frontier): frontier is only the
            # current boundary, not the full reachable completion set. In C60 face
            # graphs this premature pruning can eliminate all valid k=17 patches.
            frontier_sorted = sorted(frontier)
            for candidate in frontier_sorted:
                # Enforce root as lexicographic minimum to reduce duplicates.
                if candidate < root:
                    continue
                new_current = set(current)
                new_current.add(candidate)
                new_frontier = set(frontier)
                new_frontier.discard(candidate)
                for neighbor in graph.neighbors(candidate):
                    if neighbor >= root and neighbor not in new_current:
                        new_frontier.add(neighbor)
                if len(new_current) <= k:
                    stack.append((frozenset(new_current), frozenset(new_frontier)))


def evaluate_variant(
    *,
    graph: "nx.Graph",
    variant: dict,
    config: dict,
    reference_nodes: List[str],
    reference_mixed: List[str],
    reference_boundary: List[str],
    localized_nodes: List[str],
    localized_mixed: List[str],
    localized_boundary: List[str],
    warnings: List[str],
) -> dict:
    run_cfg = config["run"]
    patch_size = int(run_cfg.get("patch_size", 17))
    near_threshold = int(run_cfg.get("near_distance_threshold", 2))
    mode = variant["mode"]
    random_seed = variant.get("random_seed")
    all_nodes = sorted(graph.nodes())

    ref_role_map = build_role_map(
        carrier_nodes=reference_nodes,
        mixed_core_nodes=reference_mixed,
        pentagon_boundary_nodes=reference_boundary,
        all_graph_nodes=all_nodes,
        mode=mode,
        random_seed=random_seed,
    )

    cand_role_map = build_role_map(
        carrier_nodes=localized_nodes,
        mixed_core_nodes=localized_mixed,
        pentagon_boundary_nodes=localized_boundary,
        all_graph_nodes=all_nodes,
        mode=mode,
        random_seed=random_seed,
    )

    ref_signature = role_colored_signature(graph, reference_nodes, ref_role_map)
    cand_signature = role_colored_signature(graph, localized_nodes, cand_role_map)
    cand_distance = histogram_distance(
        role_degree_histogram(graph, reference_nodes, ref_role_map),
        role_degree_histogram(graph, localized_nodes, cand_role_map),
    )

    enumerated_patch_count = 0
    enumerated_exact_count = 0
    enumerated_near_count = 0
    partial_run = False
    stop_reason = "not_enumerated"

    if bool(run_cfg.get("enumerate_connected_patches", False)):
        skip_first = int(run_cfg.get("skip_first_connected_patches", 0))
        max_count = run_cfg.get("max_connected_patches_this_run")
        max_count = None if max_count is None else int(max_count)
        max_wall = run_cfg.get("max_wall_seconds")
        max_wall = None if max_wall is None else float(max_wall)
        progress_every = int(run_cfg.get("progress_every", 1000))

        start = time.monotonic()
        for raw_index, patch_nodes, _ in connected_k_subgraphs(
            graph,
            k=patch_size,
            skip_first=skip_first,
            max_count=max_count,
            max_wall_seconds=max_wall,
        ):
            enumerated_patch_count += 1
            patch_role_map = build_role_map(
                carrier_nodes=list(patch_nodes),
                mixed_core_nodes=[],  # Unknown for arbitrary patch under transported role conventions.
                pentagon_boundary_nodes=[],
                all_graph_nodes=all_nodes,
                mode="face_type_only" if mode == "face_type_only" else "uncolored_carrier_only",
                random_seed=random_seed,
            )

            # Important defensive note:
            # For arbitrary enumerated patches, transported mixed/boundary roles are not known
            # without an additional role transport rule. The scaffold therefore uses only modes
            # that can be assigned locally for enumeration unless a future optimized runner adds
            # a patch-level role transport algorithm.
            if mode not in {"uncolored_carrier_only", "face_type_only"}:
                if enumerated_patch_count == 1:
                    warnings.append(
                        f"{variant['variant_id']}: full enumeration under mode '{mode}' "
                        "requires a patch-level role transport rule. Counting uses a conservative "
                        "local carrier/face-type fallback and should be treated as scaffold output."
                    )

            patch_signature = role_colored_signature(graph, list(patch_nodes), patch_role_map)
            patch_distance = histogram_distance(
                role_degree_histogram(graph, reference_nodes, ref_role_map),
                role_degree_histogram(graph, list(patch_nodes), patch_role_map),
            )

            if patch_signature == ref_signature:
                enumerated_exact_count += 1
            if patch_distance <= near_threshold:
                enumerated_near_count += 1

            if progress_every > 0 and enumerated_patch_count % progress_every == 0:
                elapsed = time.monotonic() - start
                print(
                    f"[{variant['variant_id']}] processed={enumerated_patch_count} "
                    f"raw_index={raw_index} elapsed_s={elapsed:.1f}",
                    flush=True,
                )

        if max_count is not None and enumerated_patch_count >= max_count:
            stop_reason = "max_count_reached"
            partial_run = False
        elif enumerated_patch_count == 0:
            stop_reason = "generator_exhausted_or_timeout_before_first_patch"
            partial_run = True
        else:
            stop_reason = "generator_exhausted_or_timeout"
            partial_run = True

    if bool(run_cfg.get("enumerate_connected_patches", False)):
        if max_count is not None and enumerated_patch_count >= max_count:
            stop_reason = "max_count_reached"
            partial_run = False
        elif enumerated_patch_count == 0:
            stop_reason = "generator_exhausted_or_timeout_before_first_patch"
            partial_run = True
        else:
            stop_reason = "generator_exhausted_or_timeout"
            partial_run = True
    else:
        stop_reason = "not_enumerated"
        partial_run = False

    variant_warnings = [w for w in warnings if w.startswith(f"{variant['variant_id']}:")]

    return {
        "run_id": config["run"]["run_id"],
        "case_id": config["run"]["case_id"],
        "variant_id": variant["variant_id"],
        "variant_mode": mode,
        "variant_description": variant.get("description", ""),
        "reference_role_colored_signature": ref_signature,
        "localized_candidate_role_colored_signature": cand_signature,
        "localized_candidate_exact_match": bool(cand_signature == ref_signature),
        "localized_candidate_near_distance": int(cand_distance),
        "localized_candidate_near_match": bool(cand_distance <= near_threshold),
        "enumerated_patch_count": int(enumerated_patch_count),
        "enumerated_exact_match_count": int(enumerated_exact_count),
        "enumerated_near_match_count": int(enumerated_near_count),
        "partial_run": bool(partial_run),
        "stop_reason": stop_reason,
        "warnings_count": int(len(variant_warnings)),
    }


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_result_note(path: Path, summary: dict) -> None:
    variants = summary["variant_results"]
    exact_true = [v["variant_id"] for v in variants if v["localized_candidate_exact_match"]]
    exact_false = [v["variant_id"] for v in variants if not v["localized_candidate_exact_match"]]
    near_true = [v["variant_id"] for v in variants if v["localized_candidate_near_match"]]

    lines = []
    lines.append("# Result Note — BMS-FU02g5 Role-Assignment Sensitivity Controls\n")
    lines.append(f"Date: {summary['metadata']['timestamp_utc']}\n")
    lines.append("## Befund\n")
    lines.append(
        "The FU02g5 scaffold evaluated the FU02f1 reference carrier and the localized "
        "FU02g4c automorphic exact patch under the configured role-assignment variants.\n"
    )
    lines.append(f"- Localized candidate exact-match variants: `{exact_true}`\n")
    lines.append(f"- Localized candidate non-exact variants: `{exact_false}`\n")
    lines.append(f"- Localized candidate near-match variants: `{near_true}`\n")
    lines.append(
        f"- Enumeration enabled: `{summary['config_resolved']['run'].get('enumerate_connected_patches', False)}`\n"
    )
    lines.append("\n## Interpretation\n")
    lines.append(
        "If exact matching survives only under a subset of role variants, the role-colored "
        "signal should be treated as role-assignment sensitive within the tested C60 "
        "face-graph control space. If it survives under broad erasure/swap variants, that "
        "would support a more topology-driven reading within this limited combinatorial scope.\n"
    )
    lines.append("\n## Hypothese\n")
    lines.append(
        "A working hypothesis may be formulated only after inspecting the variant table. "
        "At this scaffold stage, no physical or dynamical hypothesis is inferred from the run itself.\n"
    )
    lines.append("\n## Offene Lücke\n")
    lines.append(
        "- Patch-level transport of mixed_core / pentagon_boundary roles for arbitrary enumerated "
        "patches may require a stricter project-specific rule.\n"
    )
    lines.append("- Near-exact role-colored decoys outside the automorphy class remain a separate inspection task.\n")
    lines.append("- External fullerene / planar / spherical graph controls are still open.\n")
    lines.append("- No physical dynamics or emergence claim follows from this control.\n")
    lines.append("\n## Claim Boundary\n")
    lines.append(
        "FU02g5 tests sensitivity of a combinatorial role-colored signature to explicit "
        "role-assignment variants in the C60 face-graph control space. It is not a proof of "
        "physical emergence, dynamics, or universal uniqueness.\n"
    )
    lines.append("\n## Next Step\n")
    lines.append(
        "If smoke-test results are clean, run small deterministic enumeration windows. "
        "Only then decide whether a primary-scale, chunked, audited FU02g5 enumeration is justified.\n"
    )
    if summary.get("warnings"):
        lines.append("\n## Warnings\n")
        for warning in summary["warnings"]:
            lines.append(f"- {warning}\n")

    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    config = load_yaml(config_path)

    output_dir = Path(config["run"]["output_dir"])
    ensure_output_dir(output_dir)

    warnings: List[str] = []
    graph_path = Path(config["input"]["full_face_graph_edges_csv"])
    graph = read_edge_csv(graph_path)

    patch_size = int(config["run"].get("patch_size", 17))
    reference_nodes = list(config["input"]["reference_carrier_nodes"])
    reference_mixed = list(config["input"]["reference_mixed_core_nodes"])
    reference_boundary = list(config["input"]["reference_pentagon_boundary_nodes"])
    localized_nodes = list(config["input"]["localized_exact_patch_nodes"])
    localized_mixed = list(config["input"]["localized_exact_patch_mixed_core_nodes"])
    localized_boundary = list(config["input"]["localized_exact_patch_pentagon_boundary_nodes"])

    validate_patch_nodes(graph, reference_nodes, patch_size, "reference_carrier", warnings)
    validate_patch_nodes(graph, localized_nodes, patch_size, "localized_exact_patch", warnings)

    variants = [v for v in config.get("role_variants", []) if bool(v.get("enabled", True))]
    if not variants:
        raise ValueError("No enabled role variants configured.")

    variant_results = []
    for variant in variants:
        print(f"Evaluating variant: {variant['variant_id']}", flush=True)
        variant_results.append(
            evaluate_variant(
                graph=graph,
                variant=variant,
                config=config,
                reference_nodes=reference_nodes,
                reference_mixed=reference_mixed,
                reference_boundary=reference_boundary,
                localized_nodes=localized_nodes,
                localized_mixed=localized_mixed,
                localized_boundary=localized_boundary,
                warnings=warnings,
            )
        )

    graph_stats = {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "component_count": nx.number_connected_components(graph),
        "face_type_counts": face_type_counts(graph.nodes()),
    }

    reference_stats = induced_stats(graph, reference_nodes)
    localized_stats = induced_stats(graph, localized_nodes)

    summary = {
        "metadata": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "script": "scripts/run_bms_fu02g5_role_assignment_sensitivity.py",
            "run_id": config["run"]["run_id"],
            "case_id": config["run"]["case_id"],
            "claim_boundary": (
                "Combinatorial role-assignment sensitivity test in the C60 face-graph "
                "control space only; no physical dynamics or emergence claim."
            ),
        },
        "config_resolved": config,
        "graph_stats": graph_stats,
        "reference_stats": reference_stats,
        "localized_candidate_stats": localized_stats,
        "variant_results": variant_results,
        "warnings": warnings,
        "partial_run": any(v["partial_run"] for v in variant_results),
    }

    if bool(config.get("report", {}).get("write_config_resolved", True)):
        write_yaml(output_dir / "config_resolved.yaml", config)

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    variant_fields = [
        "run_id",
        "case_id",
        "variant_id",
        "variant_mode",
        "variant_description",
        "reference_role_colored_signature",
        "localized_candidate_role_colored_signature",
        "localized_candidate_exact_match",
        "localized_candidate_near_distance",
        "localized_candidate_near_match",
        "enumerated_patch_count",
        "enumerated_exact_match_count",
        "enumerated_near_match_count",
        "partial_run",
        "stop_reason",
        "warnings_count",
    ]
    write_csv(output_dir / "variant_summary.csv", variant_results, variant_fields)

    if bool(config.get("report", {}).get("write_candidate_pair_summary", True)):
        pair_rows = []
        for row in variant_results:
            pair_rows.append(
                {
                    "run_id": row["run_id"],
                    "variant_id": row["variant_id"],
                    "reference_node_count": reference_stats["node_count"],
                    "localized_candidate_node_count": localized_stats["node_count"],
                    "reference_edge_count": reference_stats["edge_count"],
                    "localized_candidate_edge_count": localized_stats["edge_count"],
                    "reference_connected": reference_stats["connected"],
                    "localized_candidate_connected": localized_stats["connected"],
                    "exact_match": row["localized_candidate_exact_match"],
                    "near_distance": row["localized_candidate_near_distance"],
                    "near_match": row["localized_candidate_near_match"],
                }
            )
        write_csv(
            output_dir / "candidate_pair_summary.csv",
            pair_rows,
            [
                "run_id",
                "variant_id",
                "reference_node_count",
                "localized_candidate_node_count",
                "reference_edge_count",
                "localized_candidate_edge_count",
                "reference_connected",
                "localized_candidate_connected",
                "exact_match",
                "near_distance",
                "near_match",
            ],
        )

    if bool(config.get("report", {}).get("write_result_note", True)):
        write_result_note(output_dir / "result_note.md", summary)

    print(f"Wrote: {summary_path}")
    print(f"Wrote: {output_dir / 'variant_summary.csv'}")
    print(f"Wrote: {output_dir / 'result_note.md'}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
