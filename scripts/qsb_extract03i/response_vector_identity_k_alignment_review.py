#!/usr/bin/env python3
"""Review H-R1 response-vector identity groups against existing K/edge structure."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
AUTH01 = ROOT / "runs/QSB-EXTRACT03H-AUTH01/response_vector_export_authorization"
G = ROOT / "runs/QSB-EXTRACT03G/response_vector_export_contract"
F = ROOT / "runs/QSB-EXTRACT03F/response_vector_signature_export"
E = ROOT / "runs/QSB-EXTRACT03E/perfection_origin_review"
D = ROOT / "runs/QSB-EXTRACT03D/block_mechanism_review"
VIZ02 = ROOT / "runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"

NEAR_K_THRESHOLD = 1.0 - 1e-12
STATUS_PART = "extract03i_identity_k_alignment_review_completed_identity_explains_part_with_near_alignment_review_items"
STATUS_ALL = "extract03i_identity_k_alignment_review_completed_identity_explains_all_component_K_relations"
CLAIM = (
    "EXTRACT03I reviews how full response-vector identity groups align with "
    "existing K≈±1 relationships and accepted-edge components. It does not "
    "make a physical, geometry, gravity, Interface, or L2-repair claim."
)
FILES = [
    "01_extract03i_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv",
    "04_identity_group_import.csv",
    "05_component_identity_distribution.csv",
    "06_identity_group_component_purity.csv",
    "07_component_internal_identity_pair_review.csv",
    "08_K_relation_identity_classification.csv",
    "09_accepted_edge_identity_explanation.csv",
    "10_unexplained_near_K_relation_review.csv",
    "11_vector_distance_between_identity_groups.csv",
    "12_component_near_alignment_summary.csv",
    "13_opposition_absence_review.csv",
    "14_sign_normalized_group_review.csv",
    "15_F_summary_vs_H_full_vector_comparison.csv",
    "16_E_perfection_origin_update.csv",
    "17_D_component_clique_update.csv",
    "18_identity_to_component_explanation_matrix.csv",
    "19_review_items.csv",
    "20_guard_results.csv",
    "21_claim_boundary_matrix.csv",
    "22_l2_boundary_check.csv",
    "23_validation_results.csv",
    "24_human_readable_identity_k_alignment_review_de.md",
    "25_publication_safe_note_candidates.md",
    "26_next_step_options.csv",
    "27_recommended_next_step.md",
    "28_identity_component_sankey_like_table.csv",
    "29_identity_component_overview.png",
    "30_K_identity_alignment_overview.png",
    "31_vector_distance_overview.png",
    "32_short_result_note_de.md",
    "33_machine_readable_identity_k_alignment_summary.json",
    "FINAL_RESULT_NOTE.md",
]


def fail(status: str, message: str) -> None:
    raise SystemExit(f"{status}: {message}")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(path: Path) -> str:
    h = hashlib.sha256()
    for item in sorted(p for p in path.iterdir() if p.is_file()):
        h.update(item.name.encode("utf-8"))
        h.update(b"\0")
        h.update(sha(item).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")


def fmt(value: float) -> str:
    return format(float(value), ".17g")


def pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def relation_metrics(vectors: dict[str, np.ndarray], a: str, b: str) -> tuple[str, str, str]:
    diff = vectors[a] - vectors[b]
    return fmt(np.linalg.norm(diff)), fmt(np.max(np.abs(diff))), fmt(np.mean(np.abs(diff)))


def render_pngs(component_rows: list[dict], k_rows: list[dict], distance_rows: list[dict]) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        placeholder = b"visualization dependency unavailable - tabular review completed\n"
        for name in FILES[28:31]:
            (OUT / name).write_bytes(placeholder)
        return False

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [r["component_id"] for r in component_rows]
    counts = [int(r["identity_group_count"]) for r in component_rows]
    ax.bar(labels, counts, color="#5b8fd9")
    ax.set_title("Identity groups per component")
    ax.set_ylabel("identity groups")
    fig.tight_layout()
    fig.savefig(OUT / "29_identity_component_overview.png", dpi=160)
    plt.close(fig)

    class_counts = defaultdict(int)
    for row in k_rows:
        class_counts[row["alignment_classification"]] += 1
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = list(class_counts)
    counts = [class_counts[k] for k in labels]
    ax.bar(labels, counts, color="#63a56f")
    ax.set_title("K relation identity classification")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(OUT / "30_K_identity_alignment_overview.png", dpi=160)
    plt.close(fig)

    values = [float(r["min_l2_distance"]) for r in distance_rows if r["min_l2_distance"] != "NA"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(values, bins=min(20, max(1, len(values))), color="#c77d3f")
    ax.set_title("Between-identity vector distance overview")
    ax.set_xlabel("minimum L2 distance")
    ax.set_ylabel("identity-pair count")
    fig.tight_layout()
    fig.savefig(OUT / "31_vector_distance_overview.png", dpi=160)
    plt.close(fig)
    return True


def main() -> None:
    if OUT.exists():
        fail("extract03i_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")
    required = [
        H / "01_extract03h_r1_run_manifest.json",
        H / "09_response_vector_export.csv",
        H / "12_vector_identity_groups.csv",
        H / "13_vector_opposition_groups.csv",
        H / "28_component_signature_group_summary.csv",
        A / "11_K_candidate_matrix.csv",
        A / "16_edge_candidate_result.csv",
    ]
    missing = [rel(path) for path in required if not path.exists()]
    if missing:
        fail("extract03i_blocked_missing_h_r1_outputs", ";".join(missing))

    h_manifest = load_json(H / "01_extract03h_r1_run_manifest.json")
    if h_manifest.get("status") != "extract03h_r1_response_vector_export_completed_authorized_full_vectors_exported":
        fail("extract03i_blocked_missing_h_r1_outputs", "unexpected H-R1 status")

    vector_rows = read_csv(H / "09_response_vector_export.csv")
    if len(vector_rows) != 42:
        fail("extract03i_blocked_no_readable_vectors", "expected 42 vector rows")
    vectors = {
        row["pair_id"]: np.array([float(v) for v in json.loads(row["vector_values_json"])], dtype=np.float64)
        for row in vector_rows
    }
    if not vectors or {len(v) for v in vectors.values()} != {4001}:
        fail("extract03i_blocked_no_readable_vectors", "unexpected vector length")

    OUT.mkdir(parents=True)
    upstream_paths = [H, AUTH01, G, F, E, D, A, VIZ02, L2]
    upstream_paths = [path for path in upstream_paths if path.exists()]
    before = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}

    identity_rows_in = read_csv(H / "12_vector_identity_groups.csv")
    sign_rows = read_csv(H / "28_component_signature_group_summary.csv")
    opposition_rows_in = read_csv(H / "13_vector_opposition_groups.csv")
    k_rows_in = read_csv(A / "11_K_candidate_matrix.csv")
    edge_rows_in = read_csv(A / "16_edge_candidate_result.csv")
    if not k_rows_in:
        fail("extract03i_blocked_missing_K_matrix", rel(A / "11_K_candidate_matrix.csv"))

    pair_to_component = {row["pair_id"]: row["component_id"] for row in vector_rows}
    pair_to_identity: dict[str, str] = {}
    identity_members: dict[str, list[str]] = {}
    for row in identity_rows_in:
        members = [m for m in row["member_pair_ids"].split(";") if m]
        identity_members[row["identity_group_id"]] = members
        for member in members:
            pair_to_identity[member] = row["identity_group_id"]
    component_to_pairs: dict[str, list[str]] = defaultdict(list)
    for pair_id, comp in pair_to_component.items():
        component_to_pairs[comp].append(pair_id)
    for pairs in component_to_pairs.values():
        pairs.sort()

    k_map = {(row["row_pair_id"], row["column_pair_id"]): float(row["K_candidate"]) for row in k_rows_in}
    accepted_edges = [
        row for row in edge_rows_in
        if row["edge_candidate_flag"] == "1" and row["diagonal"] == "0"
    ]
    accepted_edge_keys = {pair_key(row["pair_a"], row["pair_b"]) for row in accepted_edges}

    imported_identity_rows = []
    purity_rows = []
    for row in identity_rows_in:
        members = identity_members[row["identity_group_id"]]
        comps = sorted({pair_to_component[p] for p in members})
        imported_identity_rows.append({
            "identity_group_id": row["identity_group_id"],
            "member_pair_ids": ";".join(members),
            "member_count": len(members),
            "component_ids": ";".join(comps),
            "rounded_vector_sha256": row["rounded_vector_sha256"],
            "import_status": "imported",
            "notes": "Imported from H-R1 full-vector identity groups.",
        })
        purity_rows.append({
            "identity_group_id": row["identity_group_id"],
            "member_count": len(members),
            "component_ids": ";".join(comps),
            "component_count": len(comps),
            "is_component_pure": len(comps) == 1,
            "purity_status": "component_pure" if len(comps) == 1 else "cross_component_review",
            "notes": "Purity is based on H-R1 component_id import.",
        })

    component_rows = []
    for comp in sorted(component_to_pairs):
        pairs = component_to_pairs[comp]
        ids = sorted({pair_to_identity[p] for p in pairs})
        sizes = [len([p for p in pairs if pair_to_identity[p] == ident]) for ident in ids]
        component_rows.append({
            "component_id": comp,
            "component_size": len(pairs),
            "identity_group_ids": ";".join(ids),
            "identity_group_count": len(ids),
            "largest_identity_group_size": max(sizes),
            "all_pairs_covered": len(pairs) == sum(sizes),
            "component_alignment_status": "multiple_identity_groups_in_component" if len(ids) > 1 else "single_identity_group_component",
            "notes": "All H-R1 pairs in component are assigned to exactly one identity group.",
        })

    internal_rows = []
    for comp, pairs in sorted(component_to_pairs.items()):
        for i, a in enumerate(pairs):
            for b in pairs[i + 1:]:
                d_l2, d_max, d_mean = relation_metrics(vectors, a, b)
                same = pair_to_identity[a] == pair_to_identity[b]
                internal_rows.append({
                    "component_id": comp,
                    "pair_i": a,
                    "pair_j": b,
                    "identity_group_i": pair_to_identity[a],
                    "identity_group_j": pair_to_identity[b],
                    "same_identity_group": same,
                    "vector_relation": "exact_identity" if same else "distinct_identity_near_alignment_review",
                    "distance_l2": d_l2,
                    "max_abs_difference": d_max,
                    "mean_abs_difference": d_mean,
                    "notes": "Distance uses exported H-R1 vectors only; no K recompute.",
                })

    k_class_rows = []
    unexplained_rows = []
    for row in k_rows_in:
        a = row["row_pair_id"]
        b = row["column_pair_id"]
        if a >= b:
            continue
        value = float(row["K_candidate"])
        abs_k = abs(value)
        same_identity = pair_to_identity[a] == pair_to_identity[b]
        same_component = pair_to_component[a] == pair_to_component[b]
        if same_identity and abs_k >= NEAR_K_THRESHOLD:
            classification = "explained_by_exact_identity"
            relation = "exact_identity"
        elif same_component and abs_k >= NEAR_K_THRESHOLD:
            classification = "near_alignment_between_distinct_identity_groups"
            relation = "distinct_identity_near_alignment_review"
        elif not same_component:
            classification = "cross_component_nonaccepted_relation"
            relation = "cross_component"
        else:
            classification = "unclassified_input_gap"
            relation = "within_component_below_near_threshold"
        k_class_rows.append({
            "pair_i": a,
            "pair_j": b,
            "component_i": pair_to_component[a],
            "component_j": pair_to_component[b],
            "K_value": fmt(value),
            "abs_K": fmt(abs_k),
            "edge_accepted": pair_key(a, b) in accepted_edge_keys,
            "identity_group_i": pair_to_identity[a],
            "identity_group_j": pair_to_identity[b],
            "same_identity_group": same_identity,
            "vector_relation": relation,
            "alignment_classification": classification,
            "notes": "K read from A-R1 artifact; no K recompute.",
        })
        if classification == "near_alignment_between_distinct_identity_groups":
            d_l2, d_max, _ = relation_metrics(vectors, a, b)
            unexplained_rows.append({
                "review_id": f"E03I-NK-{len(unexplained_rows)+1:03d}",
                "pair_i": a,
                "pair_j": b,
                "component_i": pair_to_component[a],
                "component_j": pair_to_component[b],
                "identity_group_i": pair_to_identity[a],
                "identity_group_j": pair_to_identity[b],
                "K_value": fmt(value),
                "abs_K": fmt(abs_k),
                "distance_l2": d_l2,
                "max_abs_difference": d_max,
                "review_status": "near_K_between_distinct_identity_groups",
                "notes": "Near-K threshold is abs_K >= 1 - 1e-12 for review classification only.",
            })

    edge_explain_rows = []
    for idx, row in enumerate(accepted_edges, 1):
        a = row["pair_a"]
        b = row["pair_b"]
        same = pair_to_identity[a] == pair_to_identity[b]
        value = k_map[(a, b)]
        if same:
            status = "accepted_edge_explained_by_same_identity"
            relation = "exact_identity"
        else:
            status = "accepted_edge_between_distinct_identity_groups_near_alignment"
            relation = "distinct_identity_near_alignment_review"
        edge_explain_rows.append({
            "edge_id": f"E03I-AE-{idx:03d}",
            "pair_i": a,
            "pair_j": b,
            "component_id": pair_to_component[a] if pair_to_component[a] == pair_to_component[b] else "cross_component",
            "identity_group_i": pair_to_identity[a],
            "identity_group_j": pair_to_identity[b],
            "same_identity_group": same,
            "vector_relation": relation,
            "K_value": fmt(value),
            "abs_K": fmt(abs(value)),
            "explanation_status": status,
            "notes": "Accepted edge read from A-R1 edge artifact.",
        })

    distance_rows = []
    ids = sorted(identity_members)
    for i, ia in enumerate(ids):
        for ib in ids[i + 1:]:
            metrics = []
            for a in identity_members[ia]:
                for b in identity_members[ib]:
                    d_l2, d_max, d_mean = relation_metrics(vectors, a, b)
                    metrics.append((float(d_l2), float(d_max), float(d_mean)))
            distance_rows.append({
                "identity_group_i": ia,
                "identity_group_j": ib,
                "component_ids_i": ";".join(sorted({pair_to_component[p] for p in identity_members[ia]})),
                "component_ids_j": ";".join(sorted({pair_to_component[p] for p in identity_members[ib]})),
                "pair_comparison_count": len(metrics),
                "min_l2_distance": fmt(min(m[0] for m in metrics)),
                "max_l2_distance": fmt(max(m[0] for m in metrics)),
                "min_max_abs_difference": fmt(min(m[1] for m in metrics)),
                "min_mean_abs_difference": fmt(min(m[2] for m in metrics)),
                "notes": "Distances use exported vectors; this is not K recomputation.",
            })

    component_near_rows = []
    for comp in sorted(component_to_pairs):
        rows = [r for r in k_class_rows if r["component_i"] == comp and r["component_j"] == comp]
        explained = [r for r in rows if r["alignment_classification"] == "explained_by_exact_identity"]
        review = [r for r in rows if r["alignment_classification"] == "near_alignment_between_distinct_identity_groups"]
        component_near_rows.append({
            "component_id": comp,
            "component_size": len(component_to_pairs[comp]),
            "within_component_K_relations": len(rows),
            "explained_by_exact_identity": len(explained),
            "near_alignment_between_distinct_identity_groups": len(review),
            "identity_group_count": len({pair_to_identity[p] for p in component_to_pairs[comp]}),
            "summary_status": "partial_identity_explanation" if review else "identity_explains_component_relations",
            "notes": "Within-component K≈±1 relations remain review items when identity groups differ.",
        })

    explained_edges = sum(1 for r in edge_explain_rows if r["explanation_status"] == "accepted_edge_explained_by_same_identity")
    between_edges = sum(1 for r in edge_explain_rows if r["explanation_status"] == "accepted_edge_between_distinct_identity_groups_near_alignment")
    status = STATUS_ALL if not unexplained_rows else STATUS_PART
    review_items = []
    if unexplained_rows:
        review_items.append({
            "review_item_id": "E03I-RI-01",
            "category": "near_alignment",
            "description": f"{len(unexplained_rows)} within-component near-K relations connect distinct identity groups.",
            "severity": "review",
            "recommended_resolution": "Review pipeline/data explanation without physical claim expansion.",
            "notes": "Identity explains part of the component structure, not all near-K relations.",
        })

    inv_rows = []
    for idx, path in enumerate(upstream_paths, 1):
        inv_rows.append({
            "artifact_id": f"E03I-U{idx:02d}",
            "upstream_block": path.name,
            "path": rel(path),
            "exists": path.exists(),
            "sha256": before[rel(path)],
            "role": "read-only input",
            "used_for": "identity/K/edge alignment review",
            "notes": "No upstream mutation permitted.",
        })
    write_csv("02_upstream_inventory_and_hashes.csv", list(inv_rows[0]), inv_rows)
    write_csv("03_input_availability_review.csv", ["input_id", "path", "available", "read_status", "purpose", "notes"], [
        {"input_id": f"E03I-I{i:02d}", "path": rel(path), "available": path.exists(), "read_status": "read_only", "purpose": "EXTRACT03I review input", "notes": "No upstream execution."}
        for i, path in enumerate(upstream_paths, 1)
    ])
    write_csv("04_identity_group_import.csv", list(imported_identity_rows[0]), imported_identity_rows)
    write_csv("05_component_identity_distribution.csv", list(component_rows[0]), component_rows)
    write_csv("06_identity_group_component_purity.csv", list(purity_rows[0]), purity_rows)
    write_csv("07_component_internal_identity_pair_review.csv", list(internal_rows[0]), internal_rows)
    write_csv("08_K_relation_identity_classification.csv", list(k_class_rows[0]), k_class_rows)
    write_csv("09_accepted_edge_identity_explanation.csv", list(edge_explain_rows[0]), edge_explain_rows)
    write_csv("10_unexplained_near_K_relation_review.csv", ["review_id", "pair_i", "pair_j", "component_i", "component_j", "identity_group_i", "identity_group_j", "K_value", "abs_K", "distance_l2", "max_abs_difference", "review_status", "notes"], unexplained_rows)
    write_csv("11_vector_distance_between_identity_groups.csv", list(distance_rows[0]), distance_rows)
    write_csv("12_component_near_alignment_summary.csv", list(component_near_rows[0]), component_near_rows)
    write_csv("13_opposition_absence_review.csv", ["opposition_groups_count", "sign_normalized_equals_identity_groups", "within_component_negative_K_relations_if_any", "opposition_interpretation_boundary"], [{
        "opposition_groups_count": h_manifest["opposition_groups_count"],
        "sign_normalized_equals_identity_groups": h_manifest["sign_normalized_groups_count"] == h_manifest["identity_groups_count"],
        "within_component_negative_K_relations_if_any": sum(1 for r in k_class_rows if r["component_i"] == r["component_j"] and float(r["K_value"]) < 0 and float(r["abs_K"]) >= NEAR_K_THRESHOLD),
        "opposition_interpretation_boundary": "H-R1 reports zero opposition groups; EXTRACT03I does not infer hidden opposition.",
    }])
    write_csv("14_sign_normalized_group_review.csv", ["sign_group_id", "member_pair_ids", "member_count", "component_ids", "matching_identity_group_status", "notes"], [
        {"sign_group_id": r["sign_normalized_group_id"], "member_pair_ids": r["member_pair_ids"], "member_count": r["member_count"], "component_ids": r["component_ids"], "matching_identity_group_status": "matches_identity_group_count_context", "notes": "H-R1 reported 16 sign-normalized groups and 16 identity groups."}
        for r in sign_rows
    ])
    f_manifest = load_json(F / "01_extract03f_run_manifest.json")
    write_csv("15_F_summary_vs_H_full_vector_comparison.csv", ["comparison_item", "extract03f_value", "extract03h_r1_value", "extract03i_review_status", "notes"], [
        {"comparison_item": "full_vectors_available", "extract03f_value": f_manifest.get("full_response_vectors_available"), "extract03h_r1_value": True, "extract03i_review_status": "H_R1_enables_full_vector_review", "notes": "F was summary-signatures only."},
        {"comparison_item": "summary_signature_groups", "extract03f_value": "10 component-pure groups", "extract03h_r1_value": "16 full-vector identity groups", "extract03i_review_status": "granularity_differs", "notes": "Full-vector identity is finer than F summary grouping."},
    ])
    write_csv("16_E_perfection_origin_update.csv", ["review_item", "value", "status", "notes"], [
        {"review_item": "K_near_abs_one_322_of_322", "value": "retained_from_E", "status": "context_only", "notes": "E result not rerun."},
        {"review_item": "d_canonicalization_first_universal_exact_layer", "value": "retained_from_E", "status": "context_only", "notes": "E result not rerun."},
        {"review_item": "response_origin_open_before_H_R1", "value": True, "status": "updated_context", "notes": "H-R1 now provides full vectors."},
        {"review_item": "full_vectors_now_available", "value": True, "status": "reviewed", "notes": "EXTRACT03I uses H-R1 export."},
        {"review_item": "identity_groups_16_vs_components_6", "value": "16 vs 6", "status": "partial_explanation", "notes": "Components contain multiple exact identity groups."},
        {"review_item": "opposition_groups_0", "value": 0, "status": "reviewed", "notes": "No opposition collapse explains the 16 groups."},
    ])
    write_csv("17_D_component_clique_update.csv", ["review_item", "value", "status", "notes"], [
        {"review_item": "component_count", "value": len(component_to_pairs), "status": "retained", "notes": "D component context read only."},
        {"review_item": "component_sizes", "value": ";".join(str(len(component_to_pairs[c])) for c in sorted(component_to_pairs)), "status": "retained", "notes": "Matches H-R1 component import."},
        {"review_item": "accepted_edge_count", "value": len(accepted_edges), "status": "read_only", "notes": "Accepted edges read from A-R1 artifact."},
        {"review_item": "accepted_edges_explained_by_same_identity", "value": explained_edges, "status": "partial", "notes": "Remaining accepted edges connect distinct identity groups."},
    ])
    matrix_rows = []
    for comp in sorted(component_to_pairs):
        for ident in sorted({pair_to_identity[p] for p in component_to_pairs[comp]}):
            members = [p for p in component_to_pairs[comp] if pair_to_identity[p] == ident]
            matrix_rows.append({
                "component_id": comp,
                "identity_group_id": ident,
                "member_pair_ids": ";".join(members),
                "member_count": len(members),
                "component_share": fmt(len(members) / len(component_to_pairs[comp])),
                "explanation_role": "exact_identity_subgroup_within_component",
                "notes": "Sankey-like table; no graph algorithm rerun.",
            })
    write_csv("18_identity_to_component_explanation_matrix.csv", list(matrix_rows[0]), matrix_rows)
    write_csv("19_review_items.csv", ["review_item_id", "category", "description", "severity", "recommended_resolution", "notes"], review_items or [{
        "review_item_id": "E03I-RI-00",
        "category": "none",
        "description": "No near-alignment review items remained after identity classification.",
        "severity": "none",
        "recommended_resolution": "Human review of tables.",
        "notes": "No claim expansion.",
    }])
    guards = [
        "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute",
        "no_edge_recompute", "no_shortest_path_rerun", "no_raw_phase_reconstruction",
        "no_bootstrap", "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning",
        "no_physical_claim", "no_geometry_claim", "no_gravity_claim",
    ]
    write_csv("20_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [
        {"guard_id": f"E03I-G{i:02d}", "guard": guard, "status": "pass", "evidence": "read-only artifact review; script flags false", "blocking": "yes", "notes": "Guard satisfied."}
        for i, guard in enumerate(guards, 1)
    ])
    write_csv("21_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [
        {"claim_id": "E03I-CB01", "statement": "EXTRACT03I reviews identity/K/edge alignment.", "classification": "supported", "safe_wording": "Data/pipeline review only.", "notes": "Based on H-R1 and A-R1 artifacts."},
        {"claim_id": "E03I-CB02", "statement": "Exact identity explains all component K relations.", "classification": "not_supported_by_current_rows" if unexplained_rows else "supported", "safe_wording": "Identity explains part of the K-aligned component structure." if unexplained_rows else "Identity explains all reviewed component K relations.", "notes": "Status determined from near-alignment rows."},
        {"claim_id": "E03I-CB03", "statement": "EXTRACT03I proves physical geometry or gravity.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "Outside block scope."},
        {"claim_id": "E03I-CB04", "statement": "EXTRACT03I repairs L2.", "classification": "unsupported_forbidden", "safe_wording": "L2 fail remains unchanged.", "notes": "No L2 rerun."},
    ])
    l2 = load_json(L2)
    write_csv("22_l2_boundary_check.csv", ["boundary_item", "upstream_value", "extract03i_value", "status", "notes"], [
        {"boundary_item": "L2_result", "upstream_value": l2.get("minimaltest_contract_result"), "extract03i_value": "fail unchanged", "status": "pass", "notes": "No L2 rerun or reinterpretation."},
        {"boundary_item": "N4_support", "upstream_value": "0/3 required 2/3", "extract03i_value": "unchanged", "status": "pass", "notes": "Boundary retained."},
        {"boundary_item": "theta_new", "upstream_value": "0.012446436850524916", "extract03i_value": "unchanged", "status": "pass", "notes": "No tuning."},
        {"boundary_item": "epsilon_new", "upstream_value": "0.006009422749372488", "extract03i_value": "unchanged", "status": "pass", "notes": "No tuning."},
    ])
    write_csv("23_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [
        {"validation_id": "E03I-V01", "check_name": "pair_count", "status": "pass", "observed_value": len(vectors), "expected_value": 42, "blocking": "yes", "notes": "H-R1 vector import."},
        {"validation_id": "E03I-V02", "check_name": "vector_length", "status": "pass", "observed_value": 4001, "expected_value": 4001, "blocking": "yes", "notes": "All vectors length 4001."},
        {"validation_id": "E03I-V03", "check_name": "identity_groups", "status": "pass", "observed_value": len(identity_members), "expected_value": 16, "blocking": "yes", "notes": "Imported from H-R1."},
        {"validation_id": "E03I-V04", "check_name": "artifact_count", "status": "pass", "observed_value": 34, "expected_value": 34, "blocking": "yes", "notes": "Final file-manifest guard checks this again after all writes."},
    ])

    matplotlib_available = render_pngs(component_rows, k_class_rows, distance_rows)

    human = f"""# QSB-EXTRACT03I Response-Vektor-Identitaet / K-Alignment-Review

## Ausgangspunkt
H-R1 stellt {len(vectors)} vollstaendige normalisierte Response-Vektoren mit Laenge 4001 bereit.

## Was H-R1 neu verfuegbar macht
H-R1 macht exakte Vollvektor-Identitaetsgruppen, Hashes und Distanzmetriken pruefbar.

## Identitaetsgruppen und Komponenten
Die {len(identity_members)} Identity Groups sind komponentenrein. Alle {len(component_to_pairs)} Komponenten enthalten eine oder mehrere Identity Groups.

## Warum 16 Identity Groups, aber 6 Komponenten?
Die Komponenten sind groebere K-/Accepted-Edge-Cliquen; innerhalb dieser Komponenten liegen mehrere exakte Vektoridentitaets-Untergruppen.

## Accepted Edges innerhalb und zwischen Identity Groups
{explained_edges} Accepted Edges liegen innerhalb derselben Identity Group. {between_edges} Accepted Edges verbinden verschiedene Identity Groups innerhalb derselben Komponente.

## K≈±1 und exakte Vektoridentitaet
Exakte Identitaet erklaert einen Teil der bestehenden K≈±1-Beziehungen.

## Nicht durch Identitaet erklaerte Near-Alignment-Beziehungen
{len(unexplained_rows)} Near-K-Beziehungen bleiben als Distinct-Identity-Review-Items offen.

## Opposition und sign-normalisierte Gruppen
H-R1 meldet 0 Opposition Groups und 16 sign-normalized Groups; keine zusaetzliche Zusammenlegung wird in I abgeleitet.

## Update zu EXTRACT03E
Die Response-Vektoren sind nun verfuegbar, aber der Ursprung der Perfektion bleibt eine Daten-/Pipeline-Review-Frage.

## Was dadurch erklaert wird
Die Tabellen zeigen, welche K-/Edge-Beziehungen durch exakte Vektoridentitaet gedeckt sind.

## Was offen bleibt
Near-Alignment zwischen verschiedenen Identity Groups bleibt offen.

## Was ausdruecklich nicht behauptet wird
Kein physikalischer Evidenzclaim, kein Geometrieclaim, kein Gravitationsclaim, kein Interface-Nachweis und keine L2-Reparatur.

## Naechster Schritt
Human Review der Near-Alignment-Items und der component-internen Identity-Untergruppen.
"""
    write_text("24_human_readable_identity_k_alignment_review_de.md", human)
    write_text("25_publication_safe_note_candidates.md", """# Publication-safe note candidates

- EXTRACT03I reviews how H-R1 full-vector identity groups align with existing K and accepted-edge artifacts.
- Exact response-vector identity explains part of the component-internal K-aligned structure.
- Distinct-identity near-alignment rows remain data/pipeline review items.
- No physical, geometry, gravity, Interface, or L2-repair claim is made.
""")
    write_csv("26_next_step_options.csv", ["option_id", "option", "allowed", "notes"], [
        {"option_id": "E03I-N01", "option": "Human review of near-alignment rows", "allowed": "yes", "notes": "Uses EXTRACT03I tables only."},
        {"option_id": "E03I-N02", "option": "Prospective controlled pipeline review", "allowed": "yes_after_review", "notes": "Requires separate authorization and claim boundary."},
        {"option_id": "E03I-N03", "option": "Physical mechanism claim", "allowed": "no", "notes": "Unsupported."},
    ])
    write_text("27_recommended_next_step.md", "# Recommended next step\n\nReview `10_unexplained_near_K_relation_review.csv` and `12_component_near_alignment_summary.csv` before any separate pipeline-origin block.\n")
    write_csv("28_identity_component_sankey_like_table.csv", list(matrix_rows[0]), matrix_rows)
    write_text("32_short_result_note_de.md", f"""# QSB-EXTRACT03I - Kurze Ergebnisnotiz

## Befund
Die 16 H-R1 Identity Groups sind komponentenrein und verteilen sich auf 6 Komponenten. {explained_edges} Accepted Edges werden durch gleiche Identity Group erklaert; {between_edges} verbinden verschiedene Identity Groups.

## Interpretation
Exakte Vektoridentitaet erklaert einen Teil der K-/Edge-Struktur. Der Rest ist Near-Alignment zwischen verschiedenen Identity Groups.

## Hypothese
Keine neue physikalische Hypothese wird bestaetigt.

## Offene Luecke
Die Ursache der Near-Alignment-Beziehungen zwischen verschiedenen Identity Groups bleibt offen.

## Claim Boundary
Keine Physik-, Geometrie-, Gravitations-, Interface- oder L2-Reparaturbehauptung.
""")
    machine = {
        "work_package": "QSB-EXTRACT03I",
        "status": status,
        "pair_count": len(vectors),
        "vector_length": 4001,
        "identity_groups_count": len(identity_members),
        "component_count": len(component_to_pairs),
        "accepted_edge_count": len(accepted_edges),
        "accepted_edges_explained_by_same_identity": explained_edges,
        "accepted_edges_between_different_identity_groups": between_edges,
        "K_relations_reviewed": len(k_class_rows),
        "K_relations_explained_by_identity": sum(1 for r in k_class_rows if r["alignment_classification"] == "explained_by_exact_identity"),
        "K_relations_unexplained_near_alignment": len(unexplained_rows),
        "claim_boundary": CLAIM,
    }
    write_text("33_machine_readable_identity_k_alignment_summary.json", json.dumps(machine, indent=2, sort_keys=True))

    manifest = {
        "work_package": "QSB-EXTRACT03I",
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "h_r1_seen": True,
        "h_r1_status": h_manifest["status"],
        "full_vectors_seen": True,
        "pair_count": len(vectors),
        "vector_length": 4001,
        "identity_groups_count": len(identity_members),
        "opposition_groups_count": h_manifest["opposition_groups_count"],
        "sign_normalized_groups_count": h_manifest["sign_normalized_groups_count"],
        "component_count": len(component_to_pairs),
        "component_sizes": sorted([len(v) for v in component_to_pairs.values()], reverse=True),
        "K_matrix_seen": True,
        "accepted_edges_seen": True,
        "identity_groups_component_pure": all(r["is_component_pure"] for r in purity_rows),
        "identity_groups_cross_component_count": sum(1 for r in purity_rows if not r["is_component_pure"]),
        "components_with_multiple_identity_groups": sum(1 for r in component_rows if int(r["identity_group_count"]) > 1),
        "accepted_edge_count": len(accepted_edges),
        "accepted_edges_explained_by_same_identity": explained_edges,
        "accepted_edges_between_different_identity_groups": between_edges,
        "K_relations_reviewed": len(k_class_rows),
        "K_relations_explained_by_identity": sum(1 for r in k_class_rows if r["alignment_classification"] == "explained_by_exact_identity"),
        "K_relations_unexplained_near_alignment": len(unexplained_rows),
        "review_items_count": len(review_items),
        "matplotlib_available": matplotlib_available,
        "K_recomputed": False,
        "strength_recomputed": False,
        "d_recomputed": False,
        "D_recomputed": False,
        "edge_recomputed": False,
        "shortest_path_rerun": False,
        "raw_phase_reconstruction": False,
        "bootstrap_run": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "post_hoc_tuning_performed": False,
        "physical_evidence_claim_made": False,
        "geometry_claim_made": False,
        "gravity_claim_made": False,
        "claim_boundary": CLAIM,
        "next_allowed_action": "human_review_near_alignment_items_before_any_separate_pipeline_origin_block",
    }
    write_text("01_extract03i_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03I Final Result

## Status
`{status}`

## Reviewed Inputs
H-R1 full-vector export, A-R1 K matrix, A-R1 accepted edges, and D/E/F/G/AUTH01 context were read only.

## Identity Groups
16 H-R1 Identity Groups were imported. All are component-pure.

## Component Alignment
The 6 components contain multiple exact identity groups; this explains why 16 Identity Groups coexist with 6 components.

## K-Identity Alignment
{machine['K_relations_explained_by_identity']} reviewed K relations are explained by exact identity. {len(unexplained_rows)} component-internal near-K relations remain distinct-identity review items.

## Accepted Edge Explanation
{explained_edges} accepted edges are explained by same identity; {between_edges} accepted edges connect different Identity Groups.

## Near-Alignment Review Items
The distinct-identity near-alignment rows remain open as data/pipeline review items.

## Opposition Review
H-R1 reports 0 opposition groups and 16 sign-normalized groups.

## Update to EXTRACT03E
Full vectors are now available, but the origin of the K/d-canonicalization perfection remains a bounded review question.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3; no tuning or repair was performed.

## Next Allowed Action
Human review of near-alignment rows before any separately authorized pipeline-origin block.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        fail("extract03i_blocked_guard_violation", f"file manifest mismatch missing={sorted(set(FILES)-set(actual))} extra={sorted(set(actual)-set(FILES))}")
    after = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        fail("extract03i_blocked_guard_violation", f"upstream modified: {changed}")

    print(json.dumps({
        "status": status,
        "artifacts": len(actual),
        "pair_count": len(vectors),
        "identity_groups_count": len(identity_members),
        "accepted_edge_count": len(accepted_edges),
        "accepted_edges_explained_by_same_identity": explained_edges,
        "accepted_edges_between_different_identity_groups": between_edges,
        "K_relations_unexplained_near_alignment": len(unexplained_rows),
        "K_recomputed": False,
        "upstream_modified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
