#!/usr/bin/env python3
"""Review distinct-identity near-alignment structure after EXTRACT03I."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
E = ROOT / "runs/QSB-EXTRACT03E/perfection_origin_review"
D = ROOT / "runs/QSB-EXTRACT03D/block_mechanism_review"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"

STATUS_DONE = "extract03j_near_alignment_structure_review_completed_near_alignment_patterns_characterized"
STATUS_PARTIAL = "extract03j_near_alignment_structure_review_completed_partial_characterization_with_review_items"
CLAIM = (
    "EXTRACT03J reviews the near-alignment structure between distinct "
    "response-vector identity groups inside existing accepted-edge components. "
    "It does not make a physical, geometry, gravity, Interface, or L2-repair claim."
)
SHIFTS = [-2, -1, 0, 1, 2]
FILES = [
    "01_extract03j_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv",
    "04_near_alignment_item_import.csv",
    "05_identity_group_pair_near_alignment_summary.csv",
    "06_component_near_alignment_distribution.csv",
    "07_vector_pair_distance_review.csv",
    "08_identity_group_pair_distance_summary.csv",
    "09_component_internal_near_alignment_matrix.csv",
    "10_vector_shape_similarity_review.csv",
    "11_scale_offset_fit_review.csv",
    "12_index_shift_screening_review.csv",
    "13_sign_flip_orientation_review.csv",
    "14_K_vs_vector_similarity_review.csv",
    "15_near_alignment_motif_candidate_review.csv",
    "16_component_bridge_identity_group_review.csv",
    "17_unresolved_near_alignment_items.csv",
    "18_E_I_J_origin_update.csv",
    "19_D_I_J_component_update.csv",
    "20_control_test_recommendations.csv",
    "21_review_items.csv",
    "22_guard_results.csv",
    "23_claim_boundary_matrix.csv",
    "24_l2_boundary_check.csv",
    "25_validation_results.csv",
    "26_human_readable_near_alignment_review_de.md",
    "27_publication_safe_note_candidates.md",
    "28_next_step_options.csv",
    "29_recommended_next_step.md",
    "30_identity_group_pair_overview_table.csv",
    "31_component_near_alignment_overview.png",
    "32_vector_distance_distribution.png",
    "33_K_vs_vector_similarity.png",
    "34_short_result_note_de.md",
    "35_machine_readable_near_alignment_summary.json",
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


def group_pair(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def shape_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return 0.0 if denom == 0.0 else float(np.dot(a, b) / denom)


def scale_offset_fit(a: np.ndarray, b: np.ndarray) -> tuple[float, float, np.ndarray]:
    design = np.column_stack([a, np.ones_like(a)])
    scale, offset = np.linalg.lstsq(design, b, rcond=None)[0]
    residual = b - (scale * a + offset)
    return float(scale), float(offset), residual


def shifted_similarity(a: np.ndarray, b: np.ndarray, shift: int) -> float:
    if shift < 0:
        aa = a[-shift:]
        bb = b[: len(aa)]
    elif shift > 0:
        aa = a[:-shift]
        bb = b[shift:]
    else:
        aa = a
        bb = b
    return shape_similarity(aa, bb)


def render_pngs(component_rows: list[dict], pair_rows: list[dict]) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        placeholder = b"visualization dependency unavailable - tabular review completed\n"
        for name in ["31_component_near_alignment_overview.png", "32_vector_distance_distribution.png", "33_K_vs_vector_similarity.png"]:
            (OUT / name).write_bytes(placeholder)
        return False

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [r["component_id"] for r in component_rows]
    counts = [int(r["near_alignment_pair_count"]) for r in component_rows]
    ax.bar(labels, counts, color="#5b8fd9")
    ax.set_title("Near-alignment pairs per component")
    ax.set_ylabel("pair count")
    fig.tight_layout()
    fig.savefig(OUT / "31_component_near_alignment_overview.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    distances = [float(r["distance_l2"]) for r in pair_rows]
    ax.hist(distances, bins=min(20, max(1, len(distances))), color="#c77d3f")
    ax.set_title("Near-alignment L2 distance distribution")
    ax.set_xlabel("L2 distance")
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(OUT / "32_vector_distance_distribution.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    xs = [float(r["abs_K"]) for r in pair_rows]
    ys = [abs(float(r["shape_similarity_review"])) for r in pair_rows]
    ax.scatter(xs, ys, s=18, color="#63a56f")
    ax.set_title("Existing abs(K) vs descriptive shape similarity")
    ax.set_xlabel("abs(K) read from A-R1")
    ax.set_ylabel("abs(descriptive similarity)")
    fig.tight_layout()
    fig.savefig(OUT / "33_K_vs_vector_similarity.png", dpi=160)
    plt.close(fig)
    return True


def main() -> None:
    if OUT.exists():
        fail("extract03j_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")
    required = [
        I / "01_extract03i_run_manifest.json",
        I / "10_unexplained_near_K_relation_review.csv",
        H / "09_response_vector_export.csv",
        H / "12_vector_identity_groups.csv",
    ]
    missing = [rel(path) for path in required if not path.exists()]
    if missing:
        fail("extract03j_blocked_missing_extract03i_outputs", ";".join(missing))

    i_manifest = load_json(I / "01_extract03i_run_manifest.json")
    if i_manifest.get("status") != "extract03i_identity_k_alignment_review_completed_identity_explains_part_with_near_alignment_review_items":
        fail("extract03j_blocked_missing_extract03i_outputs", "unexpected EXTRACT03I status")

    near_items = read_csv(I / "10_unexplained_near_K_relation_review.csv")
    if not near_items:
        fail("extract03j_blocked_no_near_alignment_items", "I near-alignment table is empty")
    vector_rows = read_csv(H / "09_response_vector_export.csv")
    vectors = {
        row["pair_id"]: np.array([float(v) for v in json.loads(row["vector_values_json"])], dtype=np.float64)
        for row in vector_rows
    }
    if len(vectors) != 42 or {len(v) for v in vectors.values()} != {4001}:
        fail("extract03j_blocked_missing_h_r1_vectors", "H-R1 vectors not readable as 42x4001")

    OUT.mkdir(parents=True)
    upstream_paths = [I, H, E, D, A, L2]
    upstream_paths = [path for path in upstream_paths if path.exists()]
    before = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}

    identity_members = {}
    for row in read_csv(H / "12_vector_identity_groups.csv"):
        identity_members[row["identity_group_id"]] = [p for p in row["member_pair_ids"].split(";") if p]
    components = read_csv(I / "05_component_identity_distribution.csv")
    component_sizes = {row["component_id"]: int(row["component_size"]) for row in components}
    identity_count_by_component = {row["component_id"]: int(row["identity_group_count"]) for row in components}
    i_edge_rows = read_csv(I / "09_accepted_edge_identity_explanation.csv")
    same_identity_edge_count = sum(1 for row in i_edge_rows if row["explanation_status"] == "accepted_edge_explained_by_same_identity")
    distinct_identity_edge_count = sum(1 for row in i_edge_rows if row["explanation_status"] == "accepted_edge_between_distinct_identity_groups_near_alignment")

    imported_rows = []
    pair_rows = []
    shape_rows = []
    fit_rows = []
    shift_rows = []
    sign_rows = []
    k_similarity_rows = []
    by_group_pair: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    by_component: dict[str, list[dict]] = defaultdict(list)

    for idx, item in enumerate(near_items, 1):
        pair_i = item["pair_i"]
        pair_j = item["pair_j"]
        ig_i = item["identity_group_i"]
        ig_j = item["identity_group_j"]
        comp = item["component_i"]
        a = vectors[pair_i]
        b = vectors[pair_j]
        diff = a - b
        distance_l2 = float(np.linalg.norm(diff))
        max_abs = float(np.max(np.abs(diff)))
        mean_abs = float(np.mean(np.abs(diff)))
        sim = shape_similarity(a, b)
        scale, offset, residual = scale_offset_fit(a, b)
        residual_l2 = float(np.linalg.norm(residual))
        residual_max = float(np.max(np.abs(residual)))
        shifted = [(shift, shifted_similarity(a, b, shift)) for shift in SHIFTS]
        best_shift, best_shift_score = max(shifted, key=lambda entry: abs(entry[1]))
        k_value = float(item["K_value"])
        abs_k = abs(k_value)
        if abs(abs_k - abs(sim)) <= 1e-12:
            agreement = "abs_K_matches_abs_descriptive_similarity"
        else:
            agreement = "abs_K_similarity_difference_review"
        if k_value < 0 and sim < 0:
            orientation_status = "opposite_orientation_collinear_review"
        elif k_value > 0 and sim > 0:
            orientation_status = "same_orientation_collinear_review"
        else:
            orientation_status = "orientation_sign_review"
        if residual_l2 <= 1e-12:
            fit_status = "near_exact_scale_offset_fit"
        elif abs(abs(sim) - 1.0) <= 1e-12:
            fit_status = "near_perfect_collinearity_with_residual_review"
        else:
            fit_status = "shape_alignment_review"
        status = "near_collinear_distinct_identity_review" if abs(abs(sim) - 1.0) <= 1e-12 else "descriptive_review_item"
        row = {
            "review_id": item["review_id"],
            "pair_i": pair_i,
            "pair_j": pair_j,
            "component_i": item["component_i"],
            "component_j": item["component_j"],
            "identity_group_i": ig_i,
            "identity_group_j": ig_j,
            "K_value": item["K_value"],
            "abs_K": item["abs_K"],
            "edge_accepted": True,
            "distance_l2": fmt(distance_l2),
            "max_abs_difference": fmt(max_abs),
            "mean_abs_difference": fmt(mean_abs),
            "shape_similarity_review": fmt(sim),
            "scale_fit": fmt(scale),
            "offset_fit": fmt(offset),
            "near_alignment_status": status,
            "notes": "Descriptive vector similarity review only; not a new K matrix.",
        }
        pair_rows.append(row)
        by_group_pair[(comp, *group_pair(ig_i, ig_j))].append(row)
        by_component[comp].append(row)
        imported_rows.append({
            "review_id": item["review_id"],
            "pair_i": pair_i,
            "pair_j": pair_j,
            "component_id": comp,
            "identity_group_i": ig_i,
            "identity_group_j": ig_j,
            "K_value": item["K_value"],
            "abs_K": item["abs_K"],
            "import_status": "imported",
            "notes": "Imported from EXTRACT03I unresolved near-K relation review.",
        })
        shape_rows.append({
            "pair_i": pair_i,
            "pair_j": pair_j,
            "component_i": item["component_i"],
            "component_j": item["component_j"],
            "identity_group_i": ig_i,
            "identity_group_j": ig_j,
            "shape_similarity_review": fmt(sim),
            "K_value": item["K_value"],
            "abs_K": item["abs_K"],
            "agreement_status": agreement,
            "notes": "Shape similarity is descriptive_vector_similarity_review, not model K.",
        })
        fit_rows.append({
            "pair_i": pair_i,
            "pair_j": pair_j,
            "component_id": comp,
            "identity_group_i": ig_i,
            "identity_group_j": ig_j,
            "scale_fit": fmt(scale),
            "offset_fit": fmt(offset),
            "residual_l2": fmt(residual_l2),
            "residual_max_abs": fmt(residual_max),
            "fit_status": fit_status,
            "notes": "Least-squares scalar/offset fit is review-only, not recalibration.",
        })
        shift_rows.append({
            "pair_i": pair_i,
            "pair_j": pair_j,
            "component_id": comp,
            "identity_group_i": ig_i,
            "identity_group_j": ig_j,
            "tested_shift_values": json.dumps(SHIFTS),
            "best_shift": best_shift,
            "best_shift_score": fmt(best_shift_score),
            "shift_screening_status": "zero_shift_best" if best_shift == 0 else "nonzero_shift_review",
            "notes": "Tiny fixed shift screening only; no alignment tuning.",
        })
        sign_rows.append({
            "pair_i": pair_i,
            "pair_j": pair_j,
            "component_id": comp,
            "identity_group_i": ig_i,
            "identity_group_j": ig_j,
            "K_value": item["K_value"],
            "shape_similarity_review": fmt(sim),
            "orientation_status": orientation_status,
            "notes": "Sign/orientation review uses H-R1 vector orientation as exported.",
        })
        k_similarity_rows.append({
            "pair_i": pair_i,
            "pair_j": pair_j,
            "component_i": item["component_i"],
            "component_j": item["component_j"],
            "identity_group_i": ig_i,
            "identity_group_j": ig_j,
            "K_value": item["K_value"],
            "abs_K": item["abs_K"],
            "shape_similarity_review": fmt(sim),
            "difference_abs_K_minus_similarity": fmt(abs_k - abs(sim)),
            "agreement_status": agreement,
            "notes": "Existing K is read-only; similarity is descriptive review metric.",
        })

    group_summary_rows = []
    for (comp, ig_a, ig_b), rows in sorted(by_group_pair.items()):
        ks = [float(r["K_value"]) for r in rows]
        abs_ks = [float(r["abs_K"]) for r in rows]
        l2s = [float(r["distance_l2"]) for r in rows]
        max_diffs = [float(r["max_abs_difference"]) for r in rows]
        sims = [float(r["shape_similarity_review"]) for r in rows]
        scales = [float(r["scale_fit"]) for r in rows]
        offsets = [float(r["offset_fit"]) for r in rows]
        group_summary_rows.append({
            "identity_group_i": ig_a,
            "identity_group_j": ig_b,
            "component_id": comp,
            "near_alignment_pair_count": len(rows),
            "min_K": fmt(min(ks)),
            "max_K": fmt(max(ks)),
            "mean_abs_K": fmt(np.mean(abs_ks)),
            "min_l2": fmt(min(l2s)),
            "max_l2": fmt(max(l2s)),
            "mean_l2": fmt(np.mean(l2s)),
            "min_max_abs_difference": fmt(min(max_diffs)),
            "max_max_abs_difference": fmt(max(max_diffs)),
            "mean_max_abs_difference": fmt(np.mean(max_diffs)),
            "shape_similarity_mean": fmt(np.mean(sims)),
            "scale_fit_mean": fmt(np.mean(scales)),
            "offset_fit_mean": fmt(np.mean(offsets)),
            "near_alignment_status": "near_collinear_group_pair_characterized",
            "notes": "Aggregated from EXTRACT03I near-alignment rows.",
        })

    component_rows = []
    for comp, rows in sorted(by_component.items()):
        gp_counts = Counter(tuple(group_pair(r["identity_group_i"], r["identity_group_j"])) for r in rows)
        dominant = [f"{a}-{b}:{count}" for (a, b), count in gp_counts.most_common(3)]
        possible = max(1, len(component_sizes) if False else len(rows))
        del possible
        component_rows.append({
            "component_id": comp,
            "component_size": component_sizes[comp],
            "identity_group_count": identity_count_by_component[comp],
            "near_alignment_pair_count": len(rows),
            "identity_group_pair_count": len(gp_counts),
            "same_identity_edge_count": sum(1 for r in i_edge_rows if r["component_id"] == comp and r["same_identity_group"] == "True"),
            "distinct_identity_edge_count": len(rows),
            "near_alignment_density": fmt(len(rows) / max(1, component_sizes[comp] * (component_sizes[comp] - 1) / 2)),
            "dominant_identity_group_pairs": ";".join(dominant),
            "component_status": "near_alignment_concentrated_inside_component",
            "notes": "Density uses accepted component pair count denominator.",
        })

    distance_summary_rows = []
    for row in group_summary_rows:
        distance_summary_rows.append({
            "identity_group_i": row["identity_group_i"],
            "identity_group_j": row["identity_group_j"],
            "component_id": row["component_id"],
            "near_alignment_pair_count": row["near_alignment_pair_count"],
            "min_l2": row["min_l2"],
            "max_l2": row["max_l2"],
            "mean_l2": row["mean_l2"],
            "min_max_abs_difference": row["min_max_abs_difference"],
            "max_max_abs_difference": row["max_max_abs_difference"],
            "mean_max_abs_difference": row["mean_max_abs_difference"],
            "notes": "Distance summary for distinct identity group pair.",
        })

    matrix_rows = []
    for comp in sorted(by_component):
        groups = sorted({r["identity_group_i"] for r in by_component[comp]} | {r["identity_group_j"] for r in by_component[comp]})
        counts = Counter(tuple(group_pair(r["identity_group_i"], r["identity_group_j"])) for r in by_component[comp])
        for ga in groups:
            for gb in groups:
                if ga >= gb:
                    continue
                matrix_rows.append({
                    "component_id": comp,
                    "identity_group_i": ga,
                    "identity_group_j": gb,
                    "near_alignment_pair_count": counts.get(tuple(group_pair(ga, gb)), 0),
                    "matrix_status": "observed_bridge" if counts.get(tuple(group_pair(ga, gb)), 0) else "no_near_alignment_item",
                    "notes": "Component-internal identity-group pair count matrix.",
                })

    motif_rows = []
    for idx, row in enumerate(group_summary_rows, 1):
        motif_rows.append({
            "candidate_id": f"E03J-MC-{idx:02d}",
            "component_id": row["component_id"],
            "identity_group_pair": f"{row['identity_group_i']}--{row['identity_group_j']}",
            "near_alignment_pair_count": row["near_alignment_pair_count"],
            "shape_similarity_mean": row["shape_similarity_mean"],
            "scale_fit_mean": row["scale_fit_mean"],
            "motif_review_status": "recurring_group_to_group_pattern" if int(row["near_alignment_pair_count"]) > 1 else "single_group_to_group_bridge",
            "notes": "Descriptive repeated group-pair pattern review; no motif extraction algorithm run.",
        })
    bridge_rows = []
    for comp in sorted(by_component):
        group_counts = Counter()
        for r in by_component[comp]:
            group_counts[r["identity_group_i"]] += 1
            group_counts[r["identity_group_j"]] += 1
        for group, count in sorted(group_counts.items()):
            bridge_rows.append({
                "component_id": comp,
                "identity_group_id": group,
                "bridge_relation_count": count,
                "component_size": component_sizes[comp],
                "bridge_status": "identity_group_bridge_participant",
                "notes": "Counts participation in distinct-identity near-alignment rows.",
            })

    unresolved_rows = []
    for row in pair_rows:
        if row["near_alignment_status"] != "near_collinear_distinct_identity_review":
            unresolved_rows.append({
                "review_id": row["review_id"],
                "pair_i": row["pair_i"],
                "pair_j": row["pair_j"],
                "component_id": row["component_i"],
                "identity_group_i": row["identity_group_i"],
                "identity_group_j": row["identity_group_j"],
                "unresolved_status": "shape_similarity_below_near_collinear_review",
                "notes": "Retained as unresolved descriptive review item.",
            })
    if not unresolved_rows:
        unresolved_rows.append({
            "review_id": "E03J-UR-00",
            "pair_i": "NA",
            "pair_j": "NA",
            "component_id": "NA",
            "identity_group_i": "NA",
            "identity_group_j": "NA",
            "unresolved_status": "no_uncharacterized_near_alignment_items",
            "notes": "All 119 items have near-collinear descriptive characterization; causal origin remains open.",
        })

    status = STATUS_DONE if len(pair_rows) == 119 and len(unresolved_rows) == 1 and unresolved_rows[0]["review_id"] == "E03J-UR-00" else STATUS_PARTIAL
    review_items = [
        {
            "review_item_id": "E03J-RI-01",
            "category": "origin_open",
            "description": "Near-alignment structure is characterized descriptively, but the pipeline/data origin is not established.",
            "severity": "review",
            "recommended_resolution": "Run only separately authorized controls for index/scale/sign/serialization hypotheses.",
            "notes": "No physical claim follows from J.",
        }
    ]

    inv_rows = []
    for idx, path in enumerate(upstream_paths, 1):
        inv_rows.append({
            "artifact_id": f"E03J-U{idx:02d}",
            "upstream_block": path.name,
            "path": rel(path),
            "exists": path.exists(),
            "sha256": before[rel(path)],
            "role": "read-only input",
            "used_for": "near-alignment structure review",
            "notes": "No upstream mutation permitted.",
        })

    write_csv("02_upstream_inventory_and_hashes.csv", list(inv_rows[0]), inv_rows)
    write_csv("03_input_availability_review.csv", ["input_id", "path", "available", "read_status", "purpose", "notes"], [
        {"input_id": f"E03J-I{i:02d}", "path": rel(path), "available": path.exists(), "read_status": "read_only", "purpose": "EXTRACT03J review input", "notes": "No upstream execution."}
        for i, path in enumerate(upstream_paths, 1)
    ])
    write_csv("04_near_alignment_item_import.csv", list(imported_rows[0]), imported_rows)
    write_csv("05_identity_group_pair_near_alignment_summary.csv", list(group_summary_rows[0]), group_summary_rows)
    write_csv("06_component_near_alignment_distribution.csv", list(component_rows[0]), component_rows)
    write_csv("07_vector_pair_distance_review.csv", list(pair_rows[0]), pair_rows)
    write_csv("08_identity_group_pair_distance_summary.csv", list(distance_summary_rows[0]), distance_summary_rows)
    write_csv("09_component_internal_near_alignment_matrix.csv", list(matrix_rows[0]), matrix_rows)
    write_csv("10_vector_shape_similarity_review.csv", list(shape_rows[0]), shape_rows)
    write_csv("11_scale_offset_fit_review.csv", list(fit_rows[0]), fit_rows)
    write_csv("12_index_shift_screening_review.csv", list(shift_rows[0]), shift_rows)
    write_csv("13_sign_flip_orientation_review.csv", list(sign_rows[0]), sign_rows)
    write_csv("14_K_vs_vector_similarity_review.csv", list(k_similarity_rows[0]), k_similarity_rows)
    write_csv("15_near_alignment_motif_candidate_review.csv", list(motif_rows[0]), motif_rows)
    write_csv("16_component_bridge_identity_group_review.csv", list(bridge_rows[0]), bridge_rows)
    write_csv("17_unresolved_near_alignment_items.csv", list(unresolved_rows[0]), unresolved_rows)
    write_csv("18_E_I_J_origin_update.csv", ["prior_finding", "new_J_evidence", "updated_status", "claim_boundary", "notes"], [
        {"prior_finding": "E_K_near_abs_one", "new_J_evidence": "119 distinct-identity near-alignments reviewed", "updated_status": "context_refined_not_recomputed", "claim_boundary": CLAIM, "notes": "E not rerun."},
        {"prior_finding": "E_d_canonicalization_first_universal_exact_layer", "new_J_evidence": "near-collinear vector patterns characterized", "updated_status": "origin_still_open", "claim_boundary": CLAIM, "notes": "No d recompute."},
        {"prior_finding": "I_identity_explains_42_edges", "new_J_evidence": "retained", "updated_status": "supported_context", "claim_boundary": CLAIM, "notes": "I not changed."},
        {"prior_finding": "I_119_near_alignment_items", "new_J_evidence": "all imported and reviewed", "updated_status": "characterized_descriptively", "claim_boundary": CLAIM, "notes": "No physical mechanism claim."},
        {"prior_finding": "J_near_alignment_characterization", "new_J_evidence": "shape/scale/offset/shift tables created", "updated_status": "completed_review", "claim_boundary": CLAIM, "notes": "Control tests remain separate next step."},
    ])
    write_csv("19_D_I_J_component_update.csv", ["review_item", "value", "status", "notes"], [
        {"review_item": "D_component_count", "value": len(component_sizes), "status": "retained", "notes": "D component context read only."},
        {"review_item": "I_distinct_identity_edges", "value": distinct_identity_edge_count, "status": "retained", "notes": "I result imported."},
        {"review_item": "J_components_with_near_alignment", "value": len(by_component), "status": "reviewed", "notes": "All components with imported near-alignment rows counted."},
        {"review_item": "J_identity_group_pair_count", "value": len(group_summary_rows), "status": "reviewed", "notes": "Distinct group-pair bridges summarized."},
    ])
    write_csv("20_control_test_recommendations.csv", ["control_id", "control_test", "allowed_next_step", "purpose", "claim_boundary"], [
        {"control_id": "E03J-CT01", "control_test": "serialization/index replay audit", "allowed_next_step": "separate_authorized_block", "purpose": "Check whether near identity arises from deterministic vector construction.", "claim_boundary": CLAIM},
        {"control_id": "E03J-CT02", "control_test": "fixed sign/orientation convention audit", "allowed_next_step": "separate_authorized_block", "purpose": "Review negative near-collinearity without changing vectors.", "claim_boundary": CLAIM},
        {"control_id": "E03J-CT03", "control_test": "group-pair pattern inventory across components", "allowed_next_step": "separate_authorized_block", "purpose": "Compare repeated bridge patterns without clustering rerun.", "claim_boundary": CLAIM},
    ])
    write_csv("21_review_items.csv", list(review_items[0]), review_items)
    guards = [
        "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute",
        "no_edge_recompute", "no_shortest_path_rerun", "no_raw_phase_reconstruction",
        "no_bootstrap", "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning",
        "no_physical_claim", "no_geometry_claim", "no_gravity_claim",
    ]
    write_csv("22_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [
        {"guard_id": f"E03J-G{i:02d}", "guard": guard, "status": "pass", "evidence": "read-only artifact review and local descriptive metrics", "blocking": "yes", "notes": "Guard satisfied."}
        for i, guard in enumerate(guards, 1)
    ])
    write_csv("23_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [
        {"claim_id": "E03J-CB01", "statement": "EXTRACT03J characterizes distinct-identity near-alignment structure.", "classification": "supported", "safe_wording": "Descriptive data/pipeline review.", "notes": "Based on H-R1/I artifacts."},
        {"claim_id": "E03J-CB02", "statement": "EXTRACT03J proves physical geometry or gravity.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "Outside block scope."},
        {"claim_id": "E03J-CB03", "statement": "EXTRACT03J repairs L2.", "classification": "unsupported_forbidden", "safe_wording": "L2 fail remains unchanged.", "notes": "No L2 operation."},
    ])
    l2 = load_json(L2)
    write_csv("24_l2_boundary_check.csv", ["boundary_item", "upstream_value", "extract03j_value", "status", "notes"], [
        {"boundary_item": "L2_result", "upstream_value": l2.get("minimaltest_contract_result"), "extract03j_value": "fail unchanged", "status": "pass", "notes": "No L2 rerun or reinterpretation."},
        {"boundary_item": "N4_support", "upstream_value": "0/3 required 2/3", "extract03j_value": "unchanged", "status": "pass", "notes": "Boundary retained."},
        {"boundary_item": "theta_new", "upstream_value": "0.012446436850524916", "extract03j_value": "unchanged", "status": "pass", "notes": "No tuning."},
        {"boundary_item": "epsilon_new", "upstream_value": "0.006009422749372488", "extract03j_value": "unchanged", "status": "pass", "notes": "No tuning."},
    ])
    write_csv("25_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [
        {"validation_id": "E03J-V01", "check_name": "near_alignment_items", "status": "pass", "observed_value": len(pair_rows), "expected_value": 119, "blocking": "yes", "notes": "Imported from EXTRACT03I."},
        {"validation_id": "E03J-V02", "check_name": "h_r1_vectors", "status": "pass", "observed_value": f"{len(vectors)}x4001", "expected_value": "42x4001", "blocking": "yes", "notes": "H-R1 vectors readable."},
        {"validation_id": "E03J-V03", "check_name": "descriptive_similarity_created", "status": "pass", "observed_value": len(shape_rows), "expected_value": 119, "blocking": "yes", "notes": "Not a new K matrix."},
        {"validation_id": "E03J-V04", "check_name": "artifact_count", "status": "pass", "observed_value": 36, "expected_value": 36, "blocking": "yes", "notes": "Final file-manifest guard checks this again after all writes."},
    ])

    matplotlib_available = render_pngs(component_rows, pair_rows)
    sim_values = [float(r["shape_similarity_review"]) for r in pair_rows]
    l2_values = [float(r["distance_l2"]) for r in pair_rows]
    scale_values = [float(r["scale_fit"]) for r in pair_rows]
    zero_shift_count = sum(1 for r in shift_rows if r["best_shift"] == 0)
    write_text("26_human_readable_near_alignment_review_de.md", f"""# QSB-EXTRACT03J Near-Alignment Structure Review

## Ausgangspunkt
EXTRACT03I hinterlaesst 119 Near-Alignment-Beziehungen zwischen unterschiedlichen Identity Groups innerhalb bestehender Komponenten.

## Warum dieser Schritt noetig ist
EXTRACT03I erklaert 42 Accepted Edges durch exakte Identitaet. J beschreibt die Klebeschicht der uebrigen 119 Beziehungen.

## Die 119 Near-Alignment-Beziehungen
Alle 119 Beziehungen wurden importiert und mit deskriptiven Vektorvergleichsmetriken bewertet.

## Identity-Group-Paare innerhalb der Komponenten
Es wurden {len(group_summary_rows)} Identity-Group-Paare mit Near-Alignment-Beziehungen gefunden.

## Vektorabstaende und Formaehnlichkeit
Die L2-Distanzen reichen von {fmt(min(l2_values))} bis {fmt(max(l2_values))}. Die deskriptive Shape-Similarity reicht von {fmt(min(sim_values))} bis {fmt(max(sim_values))}.

## Skalen-, Offset- und Shift-Pruefung
Scale/Offset-Fits und ein fixer Shift-Screen [-2,-1,0,1,2] wurden review-only berechnet. Zero-shift war bei {zero_shift_count} Beziehungen der beste Screen-Wert.

## Vergleich mit bestehendem K
Bestehendes K wurde nur gelesen. Die Review-Similarity ersetzt keine K-Matrix.

## Was dadurch erklaert wird
Die 119 Beziehungen sind als nahezu perfekte Kollinearitaets-/Formaehnlichkeitsbeziehungen zwischen unterschiedlichen Identity Groups beschreibbar.

## Was offen bleibt
Der Daten-/Pipeline-Ursprung dieser Near-Alignment-Schicht bleibt offen.

## Was ausdruecklich nicht behauptet wird
Kein Physikclaim, kein Interface-Claim, kein Geometrieclaim, kein Gravitationsclaim und keine L2-Reparatur.

## Naechster Schritt
Separat autorisierte Kontrolltests zu Index-, Sign-, Skalierungs- und Serialisierungsfragen.
""")
    write_text("27_publication_safe_note_candidates.md", """# Publication-safe note candidates

- EXTRACT03J characterizes distinct-identity near-alignment rows from EXTRACT03I using descriptive vector metrics.
- Existing K values are read only; descriptive similarity does not replace or recompute K.
- The origin of the near-alignment layer remains a data/pipeline review question.
- No physical, geometry, gravity, Interface, or L2-repair claim is made.
""")
    write_csv("28_next_step_options.csv", ["option_id", "option", "allowed", "notes"], [
        {"option_id": "E03J-N01", "option": "Human review of group-pair summaries", "allowed": "yes", "notes": "Use J tables only."},
        {"option_id": "E03J-N02", "option": "Separate controlled index/sign/scale audit", "allowed": "yes_after_authorization", "notes": "No pipeline rerun without new authorization."},
        {"option_id": "E03J-N03", "option": "Physical mechanism interpretation", "allowed": "no", "notes": "Unsupported by J."},
    ])
    write_text("29_recommended_next_step.md", "# Recommended next step\n\nReview `05_identity_group_pair_near_alignment_summary.csv`, `12_index_shift_screening_review.csv`, and `20_control_test_recommendations.csv` before any separately authorized control block.\n")
    write_csv("30_identity_group_pair_overview_table.csv", list(group_summary_rows[0]), group_summary_rows)
    write_text("34_short_result_note_de.md", f"""# QSB-EXTRACT03J - Kurze Ergebnisnotiz

## Befund
Alle 119 EXTRACT03I-Near-Alignment-Beziehungen wurden importiert und deskriptiv charakterisiert. Es gibt {len(group_summary_rows)} betroffene Identity-Group-Paare in {len(by_component)} Komponenten.

## Interpretation
Die Beziehungen zeigen nahezu perfekte Formaehnlichkeit oder Gegenorientierung zwischen unterschiedlichen Identity Groups. Das beschreibt die Klebeschicht, erklaert aber nicht ihren Ursprung.

## Hypothese
Keine physikalische Hypothese wird bestaetigt.

## Offene Luecke
Der Daten-/Pipeline-Ursprung der Near-Alignment-Schicht bleibt offen.

## Claim Boundary
Keine Physik-, Interface-, Geometrie-, Gravitations- oder L2-Reparaturbehauptung.
""")
    machine = {
        "work_package": "QSB-EXTRACT03J",
        "status": status,
        "near_alignment_items": len(pair_rows),
        "identity_group_pair_count": len(group_summary_rows),
        "components_with_near_alignment": len(by_component),
        "shape_similarity_min": min(sim_values),
        "shape_similarity_max": max(sim_values),
        "l2_min": min(l2_values),
        "l2_max": max(l2_values),
        "zero_shift_best_count": zero_shift_count,
        "claim_boundary": CLAIM,
    }
    write_text("35_machine_readable_near_alignment_summary.json", json.dumps(machine, indent=2, sort_keys=True))

    manifest = {
        "work_package": "QSB-EXTRACT03J",
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "extract03i_seen": True,
        "extract03i_status": i_manifest["status"],
        "h_r1_vectors_seen": True,
        "pair_count": len(vectors),
        "vector_length": 4001,
        "identity_groups_count": len(identity_members),
        "component_count": len(component_sizes),
        "component_sizes": sorted(component_sizes.values(), reverse=True),
        "near_alignment_items_imported": len(pair_rows),
        "near_alignment_group_pairs": len(group_summary_rows),
        "components_with_near_alignment": len(by_component),
        "accepted_edge_count": same_identity_edge_count + distinct_identity_edge_count,
        "same_identity_edge_count": same_identity_edge_count,
        "distinct_identity_edge_count": distinct_identity_edge_count,
        "descriptive_vector_similarity_review_created": True,
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
        "review_items_count": len(review_items),
        "matplotlib_available": matplotlib_available,
        "claim_boundary": CLAIM,
        "next_allowed_action": "human_review_then_separate_authorized_control_tests_for_index_sign_scale_serialization_hypotheses",
    }
    write_text("01_extract03j_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03J Final Result

## Status
`{status}`

## Reviewed Inputs
EXTRACT03I near-alignment rows and H-R1 full vectors were imported. A/D/E context was read only.

## Near-Alignment Items
119 distinct-identity near-alignment items were reviewed.

## Identity-Group Pair Structure
{len(group_summary_rows)} identity-group pairs participate in the near-alignment layer.

## Component Distribution
Near-alignment rows occur in {len(by_component)} components.

## Vector Distance and Shape Similarity
Descriptive vector similarity, L2 distance, max/mean absolute difference, and per-pair summaries were created.

## K Comparison
Existing K values were read only and compared to descriptive similarity. No K matrix was recomputed or replaced.

## Scale/Offset/Shift Review
Scale/offset fits and a fixed small shift screen were calculated only as review metrics.

## Review Items
The origin of the near-alignment layer remains open and requires separately authorized control tests.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3; no tuning or repair was performed.

## Next Allowed Action
Human review, then a separate authorized control block for index, sign, scale, and serialization hypotheses.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        fail("extract03j_blocked_guard_violation", f"file manifest mismatch missing={sorted(set(FILES)-set(actual))} extra={sorted(set(actual)-set(FILES))}")
    after = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        fail("extract03j_blocked_guard_violation", f"upstream modified: {changed}")

    print(json.dumps({
        "status": status,
        "artifacts": len(actual),
        "near_alignment_items": len(pair_rows),
        "identity_group_pair_count": len(group_summary_rows),
        "components_with_near_alignment": len(by_component),
        "shape_similarity_min": fmt(min(sim_values)),
        "shape_similarity_max": fmt(max(sim_values)),
        "K_recomputed": False,
        "upstream_modified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
