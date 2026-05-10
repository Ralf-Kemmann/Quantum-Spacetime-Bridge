#!/usr/bin/env python3
"""
BMS-FU02g4c single exact-patch photo / inspection wrapper.

Purpose
-------
Run the existing FU02g4c resumable connected-patch enumerator on exactly one
raw connected patch and capture the actual patch object that is otherwise only
counted by the runner.

This script deliberately does not modify the original runner.  It imports the
runner as a module, monkey-patches patch_signature() to photograph the reference
patch and the inspected candidate patch, then writes explicit JSON/CSV/MD
inspection artifacts.

Default target is the currently localized role-colored exact match:
    skip_first_raw_patches = 26187175
    max_raw_patches_this_run = 1

Run from the repository root, with .venv active:
    source .venv/bin/activate
    python scripts/inspect_bms_fu02g4c_single_exact_patch.py
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import sys
from copy import deepcopy
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover - user environment check
    raise SystemExit(
        "ERROR: PyYAML is required. Activate the project .venv first: "
        "source .venv/bin/activate"
    ) from exc


DEFAULT_REPO_ROOT = Path.cwd()
DEFAULT_RUNNER = Path("scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py")
DEFAULT_BASE_CONFIG = Path("data/bms_fu02g4c_orbit_reduced_resumable_config.yaml")
DEFAULT_SKIP = 26_187_175
DEFAULT_MAX_PATCHES = 1
DEFAULT_OUTPUT_DIR = Path("runs/BMS-FU02g4c/patch_photos")
DEFAULT_CHUNK_ID = "single_exact_patch_26187175_26187176"


@dataclass
class SignatureEvent:
    ordinal: int
    patch_size: int
    carriers: List[str]
    mixed: List[str]
    pent: List[str]
    signature: Dict[str, Any]
    carrier_signature_string: Optional[str]
    role_signature_string: Optional[str]


def load_runner(runner_path: Path):
    if not runner_path.exists():
        raise FileNotFoundError(f"Runner not found: {runner_path}")
    spec = importlib.util.spec_from_file_location("fu02g4c_runner_for_photo", runner_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import runner from {runner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML config did not parse to a dict: {path}")
    return data


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def stable_list(values: Iterable[str]) -> List[str]:
    return sorted(str(v) for v in values)


def configure_single_patch_run(
    base_cfg: Dict[str, Any],
    chunk_id: str,
    skip_first_raw_patches: int,
    max_raw_patches: int,
    timeout_seconds: Optional[int],
) -> Dict[str, Any]:
    cfg = deepcopy(base_cfg)
    cfg.setdefault("run", {})["chunk_id"] = chunk_id
    cfg.setdefault("enumeration", {})["skip_first_raw_patches"] = int(skip_first_raw_patches)
    cfg.setdefault("enumeration", {})["max_raw_patches_this_run"] = int(max_raw_patches)
    if timeout_seconds is not None:
        cfg.setdefault("enumeration", {})["timeout_seconds"] = int(timeout_seconds)
    cfg.setdefault("orbit_reduction", {})["enabled"] = True
    return cfg


def graph_rows_from_patch(patch: Set[str], mixed: Set[str], pent: Set[str], ctypes: Dict[str, str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for node in stable_list(patch):
        if node in mixed:
            role = "mixed_core"
        elif node in pent:
            role = "pentagon_boundary"
        else:
            role = "unassigned_or_other"
        rows.append(
            {
                "node_id": node,
                "in_patch": True,
                "role": role,
                "cell_type": ctypes.get(node, ""),
            }
        )
    return rows


def internal_edge_rows(patch: Set[str], adj: Dict[str, Set[str]], mixed: Set[str], pent: Set[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen: Set[Tuple[str, str]] = set()
    for a in patch:
        for b in adj.get(a, set()):
            if b not in patch:
                continue
            edge = tuple(sorted((str(a), str(b))))
            if edge in seen:
                continue
            seen.add(edge)
            ra = "mixed_core" if a in mixed else "pentagon_boundary" if a in pent else "unassigned_or_other"
            rb = "mixed_core" if b in mixed else "pentagon_boundary" if b in pent else "unassigned_or_other"
            rows.append({"source": edge[0], "target": edge[1], "source_role": ra, "target_role": rb})
    return sorted(rows, key=lambda r: (r["source"], r["target"]))


def try_automorphy_checks(
    ref: SignatureEvent,
    cand: SignatureEvent,
    adj: Dict[str, Set[str]],
) -> Dict[str, Any]:
    """Return cautious automorphy checks using networkx when available.

    The check builds two labelings of the same full face graph:
      - reference labeling
      - candidate labeling
    and asks whether a graph automorphism maps one labeling into the other.
    """
    try:
        import networkx as nx  # type: ignore
        from networkx.algorithms import isomorphism as iso  # type: ignore
    except Exception as exc:
        return {
            "networkx_available": False,
            "uncolored_patch_automorphic_to_reference": None,
            "role_colored_patch_automorphic_to_reference": None,
            "note": f"Automorphy checks skipped: {exc}",
        }

    vertices = sorted(adj.keys())

    def make_graph(label_mode: str, event: SignatureEvent):
        G = nx.Graph()
        patch = set(event.carriers)
        mixed = set(event.mixed)
        pent = set(event.pent)
        for v in vertices:
            if label_mode == "uncolored":
                label = "patch" if v in patch else "outside"
            else:
                if v in mixed:
                    label = "mixed_core"
                elif v in pent:
                    label = "pentagon_boundary"
                elif v in patch:
                    label = "patch_other"
                else:
                    label = "outside"
            G.add_node(v, label=label)
        for a in vertices:
            for b in adj.get(a, set()):
                if str(a) < str(b):
                    G.add_edge(a, b)
        return G

    out: Dict[str, Any] = {"networkx_available": True}
    for mode, key in [
        ("uncolored", "uncolored_patch_automorphic_to_reference"),
        ("role_colored", "role_colored_patch_automorphic_to_reference"),
    ]:
        G_ref = make_graph(mode, ref)
        G_cand = make_graph(mode, cand)
        nm = iso.categorical_node_match("label", "")
        gm = iso.GraphMatcher(G_ref, G_cand, node_match=nm)
        out[key] = bool(gm.is_isomorphic())
    out["note"] = (
        "Automorphy check compares labeled full face graphs. True means the candidate is "
        "automorphic to the FU02f1 reference under the tested labeling."
    )
    return out


def make_result_note(
    path: Path,
    *,
    photo_json_name: str,
    nodes_csv_name: str,
    edges_csv_name: str,
    ref: SignatureEvent,
    cand: SignatureEvent,
    skip: int,
    automorphy: Dict[str, Any],
) -> None:
    lines = [
        "# BMS-FU02g4c Single Exact-Patch Photo",
        "",
        "## Purpose",
        "",
        "This note records the explicit patch object behind the previously counted `raw_role_colored_signature_exact_match_count = 1` event.",
        "The script imports the existing FU02g4c runner and captures the inspected patch without modifying the original runner.",
        "",
        "## Inspection target",
        "",
        f"- `skip_first_raw_patches`: `{skip}`",
        "- `max_raw_patches_this_run`: `1`",
        f"- candidate window: `{skip} -> {skip + 1}`",
        "",
        "## Captured candidate",
        "",
        f"- patch size: `{cand.patch_size}`",
        f"- mixed-core count: `{len(cand.mixed)}`",
        f"- pentagon-boundary count: `{len(cand.pent)}`",
        f"- carrier signature string: `{cand.carrier_signature_string}`",
        f"- role signature string: `{cand.role_signature_string}`",
        "",
        "## Automorphy checks",
        "",
        f"- networkx available: `{automorphy.get('networkx_available')}`",
        f"- uncolored patch automorphic to reference: `{automorphy.get('uncolored_patch_automorphic_to_reference')}`",
        f"- role-colored patch automorphic to reference: `{automorphy.get('role_colored_patch_automorphic_to_reference')}`",
        "",
        "## Output files",
        "",
        f"- `{photo_json_name}`: full JSON photo with signatures, nodes, edges, and automorphy checks",
        f"- `{nodes_csv_name}`: one row per candidate face/node with role and cell type",
        f"- `{edges_csv_name}`: internal candidate-patch adjacency edges",
        "",
        "## Defensive interpretation",
        "",
        "This is an inspection artifact, not a new physics claim. It identifies the concrete connected 17-face patch that reproduced the FU02f1 role-colored signature in the audited replay window.",
        "The next scientific question is whether this patch is merely an automorphic reference twin or a non-reference signaturally equivalent decoy, and how sensitive that conclusion is to the v0 role-assignment rule.",
        "",
        "## Claim boundary",
        "",
        "The patch is photographed within the existing FU02g4c connected-patch enumeration logic. Role-colored results remain assignment-dependent under the current `type_preferred_role_assignment` rule.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Photograph one FU02g4c connected patch by wrapping the existing runner.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--base-config", type=Path, default=DEFAULT_BASE_CONFIG)
    parser.add_argument("--skip", type=int, default=DEFAULT_SKIP)
    parser.add_argument("--max-raw-patches", type=int, default=DEFAULT_MAX_PATCHES)
    parser.add_argument("--chunk-id", default=DEFAULT_CHUNK_ID)
    parser.add_argument("--timeout-seconds", type=int, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    runner_path = (repo_root / args.runner).resolve() if not args.runner.is_absolute() else args.runner
    base_config_path = (repo_root / args.base_config).resolve() if not args.base_config.is_absolute() else args.base_config
    output_dir = (repo_root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(repo_root))
    runner = load_runner(runner_path)

    required = [
        "run",
        "patch_signature",
        "carrier_signature_string",
        "role_signature_string",
    ]
    missing = [name for name in required if not hasattr(runner, name)]
    if missing:
        raise RuntimeError(f"Runner is missing required callable(s): {missing}")

    captured: List[SignatureEvent] = []
    original_patch_signature = runner.patch_signature

    def photo_patch_signature(carriers, mixed, pent, ctypes, adj):  # noqa: ANN001 - runner-compatible wrapper
        sig = original_patch_signature(carriers, mixed, pent, ctypes, adj)
        ordinal = len(captured)
        try:
            carrier_s = runner.carrier_signature_string(sig)
        except Exception:
            carrier_s = None
        try:
            role_s = runner.role_signature_string(sig)
        except Exception:
            role_s = None
        captured.append(
            SignatureEvent(
                ordinal=ordinal,
                patch_size=len(set(carriers)),
                carriers=stable_list(set(carriers)),
                mixed=stable_list(set(mixed)),
                pent=stable_list(set(pent)),
                signature=deepcopy(sig),
                carrier_signature_string=carrier_s,
                role_signature_string=role_s,
            )
        )
        # Store latest graph context for CSV edge extraction.
        photo_patch_signature.last_ctypes = dict(ctypes)
        photo_patch_signature.last_adj = {str(k): set(str(x) for x in v) for k, v in adj.items()}
        return sig

    photo_patch_signature.last_ctypes = {}
    photo_patch_signature.last_adj = {}
    runner.patch_signature = photo_patch_signature

    base_cfg = read_yaml(base_config_path)
    single_cfg = configure_single_patch_run(
        base_cfg,
        chunk_id=args.chunk_id,
        skip_first_raw_patches=args.skip,
        max_raw_patches=args.max_raw_patches,
        timeout_seconds=args.timeout_seconds,
    )
    temp_cfg_path = output_dir / f"{args.chunk_id}.yaml"
    write_yaml(temp_cfg_path, single_cfg)

    print(f"[photo] repo_root={repo_root}")
    print(f"[photo] runner={runner_path}")
    print(f"[photo] config={temp_cfg_path}")
    print(f"[photo] output_dir={output_dir}")
    runner.run(temp_cfg_path)

    if len(captured) < 2:
        raise RuntimeError(
            "Expected at least two patch_signature calls: reference + candidate. "
            f"Captured {len(captured)}. Cannot identify candidate photo safely."
        )

    # In the existing runner, reference signature is written before enumeration.
    ref = captured[0]
    # With max_raw_patches_this_run=1, the last captured non-reference event is the inspected candidate.
    cand = captured[-1]

    ctypes = photo_patch_signature.last_ctypes
    adj = photo_patch_signature.last_adj
    node_rows = graph_rows_from_patch(set(cand.carriers), set(cand.mixed), set(cand.pent), ctypes)
    edge_rows = internal_edge_rows(set(cand.carriers), adj, set(cand.mixed), set(cand.pent))
    automorphy = try_automorphy_checks(ref, cand, adj)

    prefix = f"bms_fu02g4c_exact_patch_{args.skip}"
    photo_json = output_dir / f"{prefix}.json"
    nodes_csv = output_dir / f"{prefix}_nodes.csv"
    edges_csv = output_dir / f"{prefix}_edges.csv"
    note_md = output_dir / f"{prefix}_result_note.md"

    photo = {
        "artifact_type": "BMS-FU02g4c single exact-patch photo",
        "runner_path": str(runner_path.relative_to(repo_root) if runner_path.is_relative_to(repo_root) else runner_path),
        "base_config_path": str(base_config_path.relative_to(repo_root) if base_config_path.is_relative_to(repo_root) else base_config_path),
        "generated_config_path": str(temp_cfg_path.relative_to(repo_root) if temp_cfg_path.is_relative_to(repo_root) else temp_cfg_path),
        "skip_first_raw_patches": args.skip,
        "max_raw_patches_this_run": args.max_raw_patches,
        "candidate_window_start": args.skip,
        "candidate_window_end_exclusive": args.skip + args.max_raw_patches,
        "reference_event": asdict(ref),
        "candidate_event": asdict(cand),
        "candidate_nodes": node_rows,
        "candidate_internal_edges": edge_rows,
        "automorphy_checks": automorphy,
        "claim_boundary": (
            "Inspection artifact only. This identifies the concrete connected 17-face patch behind the localized "
            "FU02g4c role-colored exact match. Role-colored results remain v0 assignment-dependent."
        ),
    }

    write_json(photo_json, photo)
    write_csv(nodes_csv, node_rows, ["node_id", "in_patch", "role", "cell_type"])
    write_csv(edges_csv, edge_rows, ["source", "target", "source_role", "target_role"])
    make_result_note(
        note_md,
        photo_json_name=photo_json.name,
        nodes_csv_name=nodes_csv.name,
        edges_csv_name=edges_csv.name,
        ref=ref,
        cand=cand,
        skip=args.skip,
        automorphy=automorphy,
    )

    print("[photo] wrote:")
    for p in [photo_json, nodes_csv, edges_csv, note_md, temp_cfg_path]:
        try:
            rel = p.relative_to(repo_root)
        except ValueError:
            rel = p
        print(f"  - {rel}")
    print("[photo] candidate carriers:", ";".join(cand.carriers))
    print("[photo] candidate mixed_core:", ";".join(cand.mixed))
    print("[photo] candidate pentagon_boundary:", ";".join(cand.pent))
    print("[photo] automorphy:", json.dumps(automorphy, sort_keys=True))


if __name__ == "__main__":
    main()
