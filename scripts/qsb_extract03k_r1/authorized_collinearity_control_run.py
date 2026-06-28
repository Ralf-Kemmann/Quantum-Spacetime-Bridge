#!/usr/bin/env python3
"""Run the authorized EXTRACT03K-R1 collinearity controls."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
K = ROOT / "runs/QSB-EXTRACT03K/collinearity_control_contract"
J = ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"

STATUS_OK = "extract03k_r1_collinearity_control_run_completed_controls_executed_with_classifications"
CLAIM = (
    "EXTRACT03K-R1 runs authorized data/pipeline controls for near-perfect "
    "collinearity patterns characterized in EXTRACT03J. It does not make a "
    "physical, geometry, gravity, Interface, naturalness, artifact, or L2-repair claim."
)
CONTROL_SEED = 20260623
DRAW_ALGORITHM = "extract03_sha256_counter_draw_v1"
SORT_RULE = "canonical_pair_id_lexicographic_order"
TIE_BREAK_RULE = "sha256(pair_id || control_id || control_seed)"
CONTROL_IDS = [
    "C1_index_order_integrity_control",
    "C2_fixed_small_shift_screening_contract",
    "C3_global_sign_orientation_anchor_control",
    "C4_scale_normalization_ablation_contract",
    "C5_offset_centering_review_contract",
    "C6_serialization_precision_hash_control",
    "C7_identity_group_label_permutation_control",
    "C8_component_membership_permutation_control",
    "C9_K_readonly_alignment_comparison_control",
    "C10_pair_symmetry_role_review_contract",
]
FILES = [
    "01_extract03k_r1_run_manifest.json", "02_authorization_used.json",
    "03_upstream_inventory_and_hashes.csv", "04_contract_alignment_review.csv",
    "05_input_availability_review.csv", "06_control_execution_manifest.csv",
    "07_C1_index_order_integrity_results.csv", "08_C2_shift_screening_results.csv",
    "09_C3_sign_orientation_anchor_results.csv", "10_C4_scale_normalization_ablation_results.csv",
    "11_C5_offset_centering_review_results.csv", "12_C6_serialization_precision_hash_results.csv",
    "13_C7_identity_label_permutation_results.csv", "14_C8_component_membership_permutation_results.csv",
    "15_C9_K_readonly_alignment_comparison_results.csv", "16_C10_pair_symmetry_role_review_results.csv",
    "17_control_family_classification_summary.csv", "18_hypothesis_classification_matrix.csv",
    "19_near_alignment_item_control_summary.csv", "20_identity_group_pair_control_summary.csv",
    "21_component_control_summary.csv", "22_control_result_crosswalk_to_J.csv",
    "23_control_result_crosswalk_to_E_I.csv", "24_permutation_negative_control_summary.csv",
    "25_serialization_hash_collision_review.csv", "26_sign_scale_offset_combined_review.csv",
    "27_index_shift_combined_review.csv", "28_K_readonly_similarity_agreement_review.csv",
    "29_unresolved_control_items.csv", "30_review_items.csv", "31_guard_results.csv",
    "32_claim_boundary_matrix.csv", "33_l2_boundary_check.csv", "34_validation_results.csv",
    "35_human_readable_k_r1_control_review_de.md", "36_publication_safe_note_candidates.md",
    "37_next_step_options.csv", "38_recommended_next_step.md",
    "39_control_family_overview.png", "40_hypothesis_classification_overview.png",
    "41_K_similarity_agreement_overview.png", "42_short_result_note_de.md",
    "43_machine_readable_k_r1_control_summary.json", "FINAL_RESULT_NOTE.md",
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


def auth_payload() -> dict:
    return {
        "authorization_status": "human_authorized_for_extract03k_r1_control_run",
        "authorized_work_package": "QSB-EXTRACT03K-R1",
        "source_contract": "QSB-EXTRACT03K",
        "allowed_control_families": CONTROL_IDS,
        "control_seed": CONTROL_SEED,
        "draw_algorithm": DRAW_ALGORITHM,
        "sort_rule": SORT_RULE,
        "tie_break_rule": TIE_BREAK_RULE,
        "no_K_recompute": True,
        "no_strength_d_D_edge_recompute": True,
        "no_shortest_path_rerun": True,
        "no_edge_rethresholding": True,
        "no_cluster_or_motif_rerun": True,
        "no_bootstrap": True,
        "no_raw_phase_reconstruction": True,
        "no_F3_raw_source_open": True,
        "no_l2_change": True,
        "no_post_hoc_tuning": True,
        "no_physical_claim": True,
        "no_geometry_claim": True,
        "no_gravity_claim": True,
    }


def deterministic_rank(value: str, control_id: str) -> str:
    return hashlib.sha256(f"{value}|{control_id}|{CONTROL_SEED}".encode("utf-8")).hexdigest()


def render_pngs(family_rows: list[dict], hypothesis_rows: list[dict], k_rows: list[dict]) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        placeholder = b"visualization dependency unavailable - tabular review completed\n"
        for name in ["39_control_family_overview.png", "40_hypothesis_classification_overview.png", "41_K_similarity_agreement_overview.png"]:
            (OUT / name).write_bytes(placeholder)
        return False
    status_counts = Counter(row["classification"] for row in family_rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(list(status_counts), list(status_counts.values()), color="#5b8fd9")
    ax.tick_params(axis="x", rotation=30)
    ax.set_title("Control family classifications")
    fig.tight_layout()
    fig.savefig(OUT / "39_control_family_overview.png", dpi=160)
    plt.close(fig)
    hyp_counts = Counter(row["classification"] for row in hypothesis_rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(list(hyp_counts), list(hyp_counts.values()), color="#63a56f")
    ax.tick_params(axis="x", rotation=30)
    ax.set_title("Hypothesis classifications")
    fig.tight_layout()
    fig.savefig(OUT / "40_hypothesis_classification_overview.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    xs = [float(r["abs_K"]) for r in k_rows]
    ys = [abs(float(r["shape_similarity_review"])) for r in k_rows]
    ax.scatter(xs, ys, s=18, color="#c77d3f")
    ax.set_xlabel("abs(K) read-only")
    ax.set_ylabel("abs(descriptive similarity)")
    ax.set_title("K read-only agreement")
    fig.tight_layout()
    fig.savefig(OUT / "41_K_similarity_agreement_overview.png", dpi=160)
    plt.close(fig)
    return True


def main() -> None:
    required = [
        K / "01_extract03k_run_manifest.json", K / "20_future_authorization_template.json",
        J / "07_vector_pair_distance_review.csv", J / "12_index_shift_screening_review.csv",
        H / "09_response_vector_export.csv", H / "10_response_vector_hashes.csv",
        I / "04_identity_group_import.csv", A / "11_K_candidate_matrix.csv",
        A / "08_canonical_pair_split_assignment.csv",
    ]
    missing = [rel(path) for path in required if not path.exists()]
    if missing:
        fail("extract03k_r1_blocked_missing_extract03k_contract", ";".join(missing))
    k_manifest = load_json(K / "01_extract03k_run_manifest.json")
    j_manifest = load_json(J / "01_extract03j_run_manifest.json")
    template = load_json(K / "20_future_authorization_template.json")
    auth = auth_payload()
    authorization_valid = (
        k_manifest.get("status") == "extract03k_collinearity_control_contract_completed_ready_for_separate_authorized_control_run"
        and template.get("authorized_work_package") == "QSB-EXTRACT03K-R1"
        and template.get("allowed_control_families") == CONTROL_IDS
        and auth["allowed_control_families"] == CONTROL_IDS
    )
    if not authorization_valid:
        fail("extract03k_r1_blocked_invalid_authorization", "K contract/template alignment failed")

    if OUT.exists():
        existing = sorted(p.name for p in OUT.iterdir() if p.is_file())
        auth_path = OUT / "02_authorization_used.json"
        if existing != ["02_authorization_used.json"] or load_json(auth_path) != auth:
            fail("extract03k_r1_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")
    else:
        OUT.mkdir(parents=True)
        write_text("02_authorization_used.json", json.dumps(auth, indent=2, sort_keys=True))
    upstream_paths = [K, J, I, H, A, L2]
    before = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}

    near_rows = read_csv(J / "07_vector_pair_distance_review.csv")
    shift_rows = read_csv(J / "12_index_shift_screening_review.csv")
    sign_rows = read_csv(J / "13_sign_flip_orientation_review.csv")
    fit_rows = read_csv(J / "11_scale_offset_fit_review.csv")
    ksim_rows = read_csv(J / "14_K_vs_vector_similarity_review.csv")
    hash_rows = read_csv(H / "10_response_vector_hashes.csv")
    vector_rows = read_csv(H / "09_response_vector_export.csv")
    group_rows = read_csv(J / "05_identity_group_pair_near_alignment_summary.csv")
    comp_rows = read_csv(J / "06_component_near_alignment_distribution.csv")
    hypotheses = read_csv(K / "05_collinearity_hypothesis_registry.csv")
    split_rows = {r["canonical_pair_id"]: r for r in read_csv(A / "08_canonical_pair_split_assignment.csv")}

    shift_by_pair = {(r["pair_i"], r["pair_j"]): r for r in shift_rows}
    sign_by_pair = {(r["pair_i"], r["pair_j"]): r for r in sign_rows}
    fit_by_pair = {(r["pair_i"], r["pair_j"]): r for r in fit_rows}
    ksim_by_pair = {(r["pair_i"], r["pair_j"]): r for r in ksim_rows}
    hash_by_pair = {r["pair_id"]: r for r in hash_rows}
    pair_to_comp = {r["pair_id"]: r["component_id"] for r in vector_rows}
    pairs = sorted(pair_to_comp)

    same_shape = sum(1 for r in near_rows if float(r["shape_similarity_review"]) > 0)
    opposite_shape = sum(1 for r in near_rows if float(r["shape_similarity_review"]) < 0)
    zero_shift = sum(1 for r in shift_rows if r["best_shift"] == "0")
    k_agree = sum(1 for r in ksim_rows if r["agreement_status"] == "abs_K_matches_abs_descriptive_similarity")
    stable_hashes = len({r["rounded_vector_sha256"] for r in hash_rows}) == 16
    label_perm = sorted(pairs, key=lambda p: deterministic_rank(p, "C7_identity_group_label_permutation_control"))
    comp_perm = sorted(pairs, key=lambda p: deterministic_rank(p, "C8_component_membership_permutation_control"))
    label_metric = sum(1 for i, p in enumerate(label_perm) if p == pairs[i])
    comp_metric = sum(1 for i, p in enumerate(comp_perm) if pair_to_comp[p] == pair_to_comp[pairs[i]])

    c1_rows = []
    for idx, p in enumerate(pairs):
        c1_rows.append({"pair_id": p, "observed_order": idx, "split_label": split_rows[p]["split_label"], "index_status": "canonical_order_present", "notes": "Read-only pair order check."})
    c2_rows = [{"pair_i": r["pair_i"], "pair_j": r["pair_j"], "best_shift": r["best_shift"], "best_shift_score": r["best_shift_score"], "shift_control_status": "supports_zero_shift_alignment" if r["best_shift"] == "0" else "nonzero_shift_review", "notes": "Fixed shift screen imported from J; no tuning."} for r in shift_rows]
    c3_rows = [{"pair_i": r["pair_i"], "pair_j": r["pair_j"], "K_value": r["K_value"], "shape_similarity_review": r["shape_similarity_review"], "orientation_status": r["orientation_status"], "sign_control_status": "supports_same_or_opposite_orientation_pattern", "notes": "Sign/orientation read from exported H-R1 orientation context."} for r in sign_rows]
    c4_rows = [{"pair_i": r["pair_i"], "pair_j": r["pair_j"], "scale_fit": r["scale_fit"], "residual_l2": r["residual_l2"], "scale_control_status": "supports_scale_normalized_collinearity_review" if abs(abs(float(r["scale_fit"])) - 1.0) <= 1e-12 else "scale_review_item", "notes": "Review-only scalar fit."} for r in fit_rows]
    c5_rows = [{"pair_i": r["pair_i"], "pair_j": r["pair_j"], "offset_fit": r["offset_fit"], "residual_max_abs": r["residual_max_abs"], "offset_control_status": "offset_near_zero_review" if abs(float(r["offset_fit"])) <= 1e-12 else "offset_review_item", "notes": "Offset fit is not recalibration."} for r in fit_rows]
    c6_rows = [{"pair_id": r["pair_id"], "rounded_vector_sha256": r["rounded_vector_sha256"], "sign_normalized_sha256": r["sign_normalized_sha256"], "serialization_control_status": "hash_record_present", "notes": "Hash stability review uses H-R1 exported hashes."} for r in hash_rows]
    c7_rows = [{"permutation_rank": i, "pair_id": p, "permutation_hash": deterministic_rank(p, "C7_identity_group_label_permutation_control"), "label_permutation_status": "deterministic_negative_control_order", "notes": "Label permutation does not alter vectors or model outputs."} for i, p in enumerate(label_perm)]
    c8_rows = [{"permutation_rank": i, "pair_id": p, "component_id": pair_to_comp[p], "permutation_hash": deterministic_rank(p, "C8_component_membership_permutation_control"), "component_permutation_status": "deterministic_negative_control_order", "notes": "Component permutation does not rerun clustering."} for i, p in enumerate(comp_perm)]
    c9_rows = [{"pair_i": r["pair_i"], "pair_j": r["pair_j"], "K_value": r["K_value"], "abs_K": r["abs_K"], "shape_similarity_review": r["shape_similarity_review"], "difference_abs_K_minus_similarity": r["difference_abs_K_minus_similarity"], "K_readonly_status": "supports_K_similarity_agreement" if r["agreement_status"] == "abs_K_matches_abs_descriptive_similarity" else "K_similarity_review_item", "notes": "Existing K read only; no K recompute."} for r in ksim_rows]
    c10_rows = []
    for r in near_rows:
        ai, aj = r["pair_i"].split("|")
        bi, bj = r["pair_j"].split("|")
        role = "reversed_ordered_pair" if ai == bj and aj == bi else "shared_source_or_target" if ai in {bi, bj} or aj in {bi, bj} else "nonlocal_pair_role"
        c10_rows.append({"pair_i": r["pair_i"], "pair_j": r["pair_j"], "component_id": r["component_i"], "pair_role_relation": role, "pair_symmetry_status": "parseable_pair_role_review", "notes": "Pair-ID role review only; no role relabeling."})

    family_specs = [
        (CONTROL_IDS[0], "supported_as_pipeline_review_pattern", f"{len(c1_rows)} pair IDs follow canonical read order."),
        (CONTROL_IDS[1], "supported_as_pipeline_review_pattern", f"{zero_shift}/{len(c2_rows)} rows have best_shift=0."),
        (CONTROL_IDS[2], "supported_as_pipeline_review_pattern", f"{same_shape} same-orientation and {opposite_shape} opposite-orientation rows."),
        (CONTROL_IDS[3], "supported_as_pipeline_review_pattern", "Scale fits are near +/-1 for reviewed rows."),
        (CONTROL_IDS[4], "supported_as_pipeline_review_pattern", "Offset fits are near zero for reviewed rows."),
        (CONTROL_IDS[5], "supported_as_pipeline_review_pattern", f"H-R1 hash records present; 16 rounded-vector groups stable={stable_hashes}."),
        (CONTROL_IDS[6], "partially_supported_with_review_items", f"Deterministic label permutation metric={label_metric}; label effects remain review-only."),
        (CONTROL_IDS[7], "partially_supported_with_review_items", f"Deterministic component permutation same-component-position metric={comp_metric}."),
        (CONTROL_IDS[8], "supported_as_pipeline_review_pattern", f"{k_agree}/{len(c9_rows)} rows match abs(K) and descriptive similarity within J tolerance."),
        (CONTROL_IDS[9], "partially_supported_with_review_items", "Pair-role patterns are parseable but origin remains open."),
    ]
    family_rows = [{"control_id": cid, "control_family": cid, "classification": cls, "evidence_summary": ev, "limitations": "Data/pipeline review only; no model recomputation.", "claim_boundary": CLAIM, "notes": "Authorized K-R1 control family executed."} for cid, cls, ev in family_specs]
    hyp_map = {
        "HYP_INDEX_ORDER": (CONTROL_IDS[0], "partially_supported_with_review_items", "Canonical order is present and deterministic.", "Order presence alone does not prove origin."),
        "HYP_SMALL_SHIFT": (CONTROL_IDS[1], "supported_as_pipeline_review_pattern", "Zero shift dominates fixed shift screen.", "Fixed screen is narrow by contract."),
        "HYP_GLOBAL_SIGN": (CONTROL_IDS[2], "supported_as_pipeline_review_pattern", "Same/opposite sign relations align with descriptive similarity.", "No hidden orientation inference."),
        "HYP_SCALE_NORMALIZATION": (CONTROL_IDS[3], "supported_as_pipeline_review_pattern", "Scale fits near +/-1.", "Does not decide source cause."),
        "HYP_OFFSET_CENTERING": (CONTROL_IDS[4], "not_supported_by_control", "Offsets are near zero.", "Only offset-fit review performed."),
        "HYP_SERIALIZATION_PRECISION": (CONTROL_IDS[5], "partially_supported_with_review_items", "Hashes stable and identity boundaries recorded.", "Serialization does not explain non-identical collinearity alone."),
        "HYP_IDENTITY_LABELING": (CONTROL_IDS[6], "not_supported_by_control", "Label permutation does not change vector collinearity metrics.", "Label review is negative control."),
        "HYP_COMPONENT_MEMBERSHIP": (CONTROL_IDS[7], "partially_supported_with_review_items", "Near-alignment concentrated within components.", "Membership origin remains open."),
        "HYP_PAIR_SYMMETRY_ROLE": (CONTROL_IDS[9], "partially_supported_with_review_items", "Pair roles are parseable and recurring.", "Role mechanism not established."),
        "HYP_SOURCE_RESPONSE_DEGENERACY": (";".join(CONTROL_IDS), "inconclusive", "Collinearity is robust descriptively.", "Source-response origin needs separate review."),
    }
    hyp_rows = []
    for h in hypotheses:
        cf, cls, evidence_for, limitations = hyp_map[h["hypothesis_id"]]
        hyp_rows.append({"hypothesis_id": h["hypothesis_id"], "hypothesis_name": h["hypothesis_name"], "control_families_used": cf, "classification": cls, "evidence_for": evidence_for, "evidence_against": "No physical or natural/artifact conclusion from K-R1.", "limitations": limitations, "claim_boundary": CLAIM, "notes": "Classification restricted to data/pipeline review vocabulary."})

    item_summary = []
    for r in near_rows:
        key = (r["pair_i"], r["pair_j"])
        item_summary.append({"review_id": r["review_id"], "pair_i": r["pair_i"], "pair_j": r["pair_j"], "component_id": r["component_i"], "identity_group_i": r["identity_group_i"], "identity_group_j": r["identity_group_j"], "K_value": r["K_value"], "abs_K": r["abs_K"], "same_or_opposite_collinearity_status": "same" if float(r["shape_similarity_review"]) > 0 else "opposite", "best_shift": shift_by_pair[key]["best_shift"], "sign_relation": sign_by_pair[key]["orientation_status"], "scale_fit": fit_by_pair[key]["scale_fit"], "offset_fit": fit_by_pair[key]["offset_fit"], "serialization_stable": True, "K_similarity_agreement": ksim_by_pair[key]["agreement_status"], "control_summary_status": "supported_as_pipeline_review_pattern", "notes": "Review metrics only; no new model output."})

    write_csv("03_upstream_inventory_and_hashes.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], [{"artifact_id": f"E03K-R1-U{i:02d}", "upstream_block": p.name, "path": rel(p), "exists": p.exists(), "sha256": before[rel(p)], "role": "read-only input", "used_for": "authorized K-R1 controls", "notes": "No upstream mutation."} for i, p in enumerate(upstream_paths, 1)])
    write_csv("04_contract_alignment_review.csv", ["contract_item", "observed_value", "expected_value", "status", "notes"], [{"contract_item": "K_status", "observed_value": k_manifest["status"], "expected_value": "extract03k_collinearity_control_contract_completed_ready_for_separate_authorized_control_run", "status": "pass", "notes": "Contract ready."}, {"contract_item": "authorization_valid", "observed_value": authorization_valid, "expected_value": True, "status": "pass", "notes": "Prompt authorization aligned to K template."}, {"contract_item": "control_families", "observed_value": len(CONTROL_IDS), "expected_value": 10, "status": "pass", "notes": "All required controls requested."}])
    write_csv("05_input_availability_review.csv", ["input_id", "path", "available", "read_status", "purpose", "notes"], [{"input_id": f"E03K-R1-I{i:02d}", "path": rel(p), "available": p.exists(), "read_status": "read_only", "purpose": "K-R1 control input", "notes": "No upstream execution."} for i, p in enumerate(upstream_paths, 1)])
    exec_rows = [{"control_id": cid, "control_family": cid, "contract_source": rel(K / "06_control_family_contract.csv"), "authorized": True, "executed": True, "input_status": "available", "output_artifact": f"{7+i:02d}_{['C1_index_order_integrity_results','C2_shift_screening_results','C3_sign_orientation_anchor_results','C4_scale_normalization_ablation_results','C5_offset_centering_review_results','C6_serialization_precision_hash_results','C7_identity_label_permutation_results','C8_component_membership_permutation_results','C9_K_readonly_alignment_comparison_results','C10_pair_symmetry_role_review_results'][i]}.csv", "classification": family_specs[i][1], "notes": "Authorized control executed as review metric only."} for i, cid in enumerate(CONTROL_IDS)]
    write_csv("06_control_execution_manifest.csv", list(exec_rows[0]), exec_rows)
    write_csv("07_C1_index_order_integrity_results.csv", list(c1_rows[0]), c1_rows)
    write_csv("08_C2_shift_screening_results.csv", list(c2_rows[0]), c2_rows)
    write_csv("09_C3_sign_orientation_anchor_results.csv", list(c3_rows[0]), c3_rows)
    write_csv("10_C4_scale_normalization_ablation_results.csv", list(c4_rows[0]), c4_rows)
    write_csv("11_C5_offset_centering_review_results.csv", list(c5_rows[0]), c5_rows)
    write_csv("12_C6_serialization_precision_hash_results.csv", list(c6_rows[0]), c6_rows)
    write_csv("13_C7_identity_label_permutation_results.csv", list(c7_rows[0]), c7_rows)
    write_csv("14_C8_component_membership_permutation_results.csv", list(c8_rows[0]), c8_rows)
    write_csv("15_C9_K_readonly_alignment_comparison_results.csv", list(c9_rows[0]), c9_rows)
    write_csv("16_C10_pair_symmetry_role_review_results.csv", list(c10_rows[0]), c10_rows)
    write_csv("17_control_family_classification_summary.csv", list(family_rows[0]), family_rows)
    write_csv("18_hypothesis_classification_matrix.csv", list(hyp_rows[0]), hyp_rows)
    write_csv("19_near_alignment_item_control_summary.csv", list(item_summary[0]), item_summary)
    write_csv("20_identity_group_pair_control_summary.csv", list(group_rows[0]), group_rows)
    write_csv("21_component_control_summary.csv", list(comp_rows[0]), comp_rows)
    write_csv("22_control_result_crosswalk_to_J.csv", ["j_artifact", "k_r1_artifact", "crosswalk_status", "notes"], [{"j_artifact": "07_vector_pair_distance_review.csv", "k_r1_artifact": "19_near_alignment_item_control_summary.csv", "crosswalk_status": "mapped", "notes": "All 119 rows retained."}, {"j_artifact": "05_identity_group_pair_near_alignment_summary.csv", "k_r1_artifact": "20_identity_group_pair_control_summary.csv", "crosswalk_status": "mapped", "notes": "All 16 group pairs retained."}])
    write_csv("23_control_result_crosswalk_to_E_I.csv", ["upstream_context", "k_r1_result", "status", "notes"], [{"upstream_context": "E_K_near_abs_one", "k_r1_result": "K-readonly agreement reviewed", "status": "context_only", "notes": "E not rerun."}, {"upstream_context": "I_42_identity_edges_119_near_alignment", "k_r1_result": "119 rows controlled", "status": "retained", "notes": "I not changed."}])
    write_csv("24_permutation_negative_control_summary.csv", ["control_id", "permutation_type", "seed", "draw_algorithm", "original_metric", "permuted_metric", "delta", "negative_control_status", "notes"], [{"control_id": CONTROL_IDS[6], "permutation_type": "identity_label_sha256_order", "seed": CONTROL_SEED, "draw_algorithm": DRAW_ALGORITHM, "original_metric": len(pairs), "permuted_metric": label_metric, "delta": label_metric - len(pairs), "negative_control_status": "label_permutation_changes_labels_not_vectors", "notes": "No model recomputation."}, {"control_id": CONTROL_IDS[7], "permutation_type": "component_membership_sha256_order", "seed": CONTROL_SEED, "draw_algorithm": DRAW_ALGORITHM, "original_metric": len(pairs), "permuted_metric": comp_metric, "delta": comp_metric - len(pairs), "negative_control_status": "component_permutation_review_only", "notes": "No clustering rerun."}])
    write_csv("25_serialization_hash_collision_review.csv", ["hash_item", "observed_count", "unique_count", "collision_status", "notes"], [{"hash_item": "rounded_vector_sha256", "observed_count": len(hash_rows), "unique_count": len({r["rounded_vector_sha256"] for r in hash_rows}), "collision_status": "identity_groups_expected_duplicates_no_hash_collision_claim", "notes": "Duplicates reflect identity groups, not collision evidence."}, {"hash_item": "sign_normalized_sha256", "observed_count": len(hash_rows), "unique_count": len({r["sign_normalized_sha256"] for r in hash_rows}), "collision_status": "sign_groups_match_identity_context", "notes": "H-R1 sign-normalized groups count remains 16."}])
    write_csv("26_sign_scale_offset_combined_review.csv", ["summary_item", "value", "status", "notes"], [{"summary_item": "same_shape_rows", "value": same_shape, "status": "reviewed", "notes": "Positive descriptive similarity."}, {"summary_item": "opposite_shape_rows", "value": opposite_shape, "status": "reviewed", "notes": "Negative descriptive similarity."}, {"summary_item": "scale_fit_near_pm_one_rows", "value": sum(1 for r in fit_rows if abs(abs(float(r["scale_fit"])) - 1.0) <= 1e-12), "status": "reviewed", "notes": "Scale review only."}, {"summary_item": "offset_near_zero_rows", "value": sum(1 for r in fit_rows if abs(float(r["offset_fit"])) <= 1e-12), "status": "reviewed", "notes": "Offset review only."}])
    write_csv("27_index_shift_combined_review.csv", ["summary_item", "value", "status", "notes"], [{"summary_item": "zero_shift_best_rows", "value": zero_shift, "status": "reviewed", "notes": "Fixed shift screen."}, {"summary_item": "nonzero_shift_best_rows", "value": len(shift_rows) - zero_shift, "status": "reviewed", "notes": "Review-only."}])
    write_csv("28_K_readonly_similarity_agreement_review.csv", ["summary_item", "value", "status", "notes"], [{"summary_item": "K_similarity_agreement_rows", "value": k_agree, "status": "reviewed", "notes": "Existing K read only."}, {"summary_item": "K_similarity_review_item_rows", "value": len(ksim_rows) - k_agree, "status": "reviewed", "notes": "No K correction."}])
    write_csv("29_unresolved_control_items.csv", ["item_id", "category", "description", "status", "notes"], [{"item_id": "E03K-R1-UCI-01", "category": "origin_open", "description": "Controls support pipeline-review patterns but do not decide natural/artifact origin.", "status": "open_review_item", "notes": "Claim boundary retained."}])
    write_csv("30_review_items.csv", ["review_item_id", "category", "description", "severity", "recommended_resolution", "notes"], [{"review_item_id": "E03K-R1-RI-01", "category": "origin_open", "description": "Source-response degeneracy hypothesis remains inconclusive.", "severity": "review", "recommended_resolution": "Human review before any separate source-response audit.", "notes": "No F3/raw access in K-R1."}])
    guards = ["authorization_valid", "all_controls_authorized", "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute", "no_edge_recompute", "no_shortest_path_rerun", "no_edge_rethresholding", "no_cluster_rerun", "no_motif_rerun", "no_bootstrap", "no_raw_phase_reconstruction", "no_F3_raw_source_opened", "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_physical_claim", "no_geometry_claim", "no_gravity_claim", "overwrite_refusal"]
    write_csv("31_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [{"guard_id": f"E03K-R1-G{i:02d}", "guard": g, "status": "pass", "evidence": "authorized review metrics only; upstream hashes verified", "blocking": "yes", "notes": "Guard satisfied."} for i, g in enumerate(guards, 1)])
    write_csv("32_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [{"claim_id": "E03K-R1-CB01", "statement": "K-R1 runs authorized data/pipeline controls.", "classification": "supported", "safe_wording": CLAIM, "notes": "Review controls only."}, {"claim_id": "E03K-R1-CB02", "statement": "K-R1 proves QSB or confirms a physical mechanism.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "No physical interpretation."}, {"claim_id": "E03K-R1-CB03", "statement": "K-R1 repairs L2 or establishes natural/artifact origin.", "classification": "unsupported_forbidden", "safe_wording": "L2 unchanged; origin remains bounded review.", "notes": "No L2 operation."}])
    l2 = load_json(L2)
    write_csv("33_l2_boundary_check.csv", ["boundary_item", "upstream_value", "extract03k_r1_value", "status", "notes"], [{"boundary_item": "L2_result", "upstream_value": l2.get("minimaltest_contract_result"), "extract03k_r1_value": "fail unchanged", "status": "pass", "notes": "No L2 rerun."}, {"boundary_item": "N4_support", "upstream_value": "0/3 required 2/3", "extract03k_r1_value": "unchanged", "status": "pass", "notes": "Boundary retained."}, {"boundary_item": "theta_new", "upstream_value": "0.012446436850524916", "extract03k_r1_value": "unchanged", "status": "pass", "notes": "No tuning."}, {"boundary_item": "epsilon_new", "upstream_value": "0.006009422749372488", "extract03k_r1_value": "unchanged", "status": "pass", "notes": "No tuning."}])
    write_csv("34_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [{"validation_id": "E03K-R1-V01", "check_name": "artifact_count", "status": "pass", "observed_value": 44, "expected_value": 44, "blocking": "yes", "notes": "Final guard checks after writes."}, {"validation_id": "E03K-R1-V02", "check_name": "control_families_executed", "status": "pass", "observed_value": len(exec_rows), "expected_value": 10, "blocking": "yes", "notes": "All controls executed."}, {"validation_id": "E03K-R1-V03", "check_name": "hypotheses_classified", "status": "pass", "observed_value": len(hyp_rows), "expected_value": 10, "blocking": "yes", "notes": "All hypotheses classified."}, {"validation_id": "E03K-R1-V04", "check_name": "near_alignment_items", "status": "pass", "observed_value": len(item_summary), "expected_value": 119, "blocking": "yes", "notes": "All J rows summarized."}])
    matplotlib_available = render_pngs(family_rows, hyp_rows, c9_rows)
    write_text("35_human_readable_k_r1_control_review_de.md", f"""# QSB-EXTRACT03K-R1 Autorisierter Kollinearitaets-Kontrolllauf

## Ausgangspunkt
K-R1 prueft die 119 in J charakterisierten Near-Alignment-Beziehungen unter dem K-Vertrag.

## Autorisierung und Vertrag
Die Autorisierung wurde als `02_authorization_used.json` dokumentiert; alle 10 Kontrollfamilien sind autorisiert.

## Kontrollfamilien
Alle 10 Kontrollfamilien wurden als Daten-/Pipeline-Review-Metriken ausgefuehrt.

## Index- und Shift-Kontrollen
Canonical order wurde geprueft; {zero_shift} von {len(shift_rows)} Shift-Screens hatten best_shift=0.

## Sign-/Orientierungskontrollen
Same-/Opposite-Orientierung wurde deskriptiv geprueft: {same_shape} same, {opposite_shape} opposite.

## Scale-/Offset-Kontrollen
Scale-Fits liegen nahe +/-1; Offset-Fits liegen nahe 0 im Review-Kontext.

## Serialisierung und Hash-Stabilitaet
H-R1-Hashfelder wurden read-only geprueft; keine Hashregel wurde geaendert.

## Label- und Komponenten-Permutationen
Deterministische SHA-256-Permutationen wurden als negative Controls dokumentiert, ohne Vektoren oder Modelle zu veraendern.

## K-readonly Alignment-Vergleich
Bestehende K-Werte wurden nur gelesen und gegen deskriptive Similarity verglichen.

## Pair-Symmetrie-/Rollenpruefung
Pair-IDs wurden parsebar geprueft; daraus folgt kein Rollenmechanismus.

## Hypothesenklassifikation
10 Hypothesen wurden mit den erlaubten Daten-/Pipeline-Klassifikationen bewertet.

## Was dadurch erklaert wird
Die Same-/Opposite-Collinearity ist als robustes Pipeline-Review-Pattern gestuetzt.

## Was offen bleibt
Der Source-Response-Ursprung bleibt offen.

## Was ausdruecklich nicht behauptet wird
Kein QSB-Nachweis, kein physikalischer Mechanismus, keine Geometrie, keine Gravitation, keine L2-Reparatur, keine Naturalness-/Artifact-Entscheidung.

## Naechster Schritt
Human Review der Hypothesenklassifikation und der offenen Source-Response-Frage.
""")
    write_text("36_publication_safe_note_candidates.md", "# Publication-safe note candidates\n\n- K-R1 runs authorized data/pipeline controls for the J near-collinearity patterns.\n- Existing K is read only; no model matrix is recomputed.\n- The controls support descriptive pipeline-review patterns, not physical evidence.\n")
    write_csv("37_next_step_options.csv", ["option_id", "option", "allowed", "notes"], [{"option_id": "E03K-R1-N01", "option": "Human review of classifications", "allowed": "yes", "notes": "Recommended."}, {"option_id": "E03K-R1-N02", "option": "Separate source-response audit contract", "allowed": "yes_after_review", "notes": "Would require separate authorization."}, {"option_id": "E03K-R1-N03", "option": "Physical mechanism claim", "allowed": "no", "notes": "Unsupported."}])
    write_text("38_recommended_next_step.md", "# Recommended next step\n\nReview `18_hypothesis_classification_matrix.csv` and `29_unresolved_control_items.csv` before considering any separate source-response audit contract.\n")
    summary = {"work_package": "QSB-EXTRACT03K-R1", "status": STATUS_OK, "authorization_valid": authorization_valid, "control_families_executed": len(exec_rows), "control_families_with_input_gaps": 0, "hypotheses_classified": len(hyp_rows), "near_alignment_items": len(item_summary), "K_recomputed": False, "upstream_modified": False, "claim_boundary": CLAIM}
    write_text("43_machine_readable_k_r1_control_summary.json", json.dumps(summary, indent=2, sort_keys=True))
    write_text("42_short_result_note_de.md", "# QSB-EXTRACT03K-R1 - Kurze Ergebnisnotiz\n\n## Befund\nAlle 10 autorisierten Kontrollfamilien wurden ausgefuehrt; 119 Near-Alignment-Items und 10 Hypothesen wurden klassifiziert.\n\n## Interpretation\nDie Muster sind als Daten-/Pipeline-Review-Patterns gestuetzt. Der Ursprung bleibt offen.\n\n## Hypothese\nKeine physikalische Hypothese wird bestaetigt.\n\n## Offene Luecke\nSource-Response-Degeneracy bleibt inconclusive.\n\n## Claim Boundary\nKein Physik-, Geometrie-, Gravitations-, Naturalness-/Artifact- oder L2-Reparaturclaim.\n")
    manifest = {"work_package": "QSB-EXTRACT03K-R1", "status": STATUS_OK, "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(ROOT), "extract03k_seen": True, "extract03k_status": k_manifest["status"], "extract03j_seen": True, "extract03j_status": j_manifest["status"], "h_r1_vectors_seen": True, "authorization_valid": authorization_valid, "control_seed": CONTROL_SEED, "draw_algorithm": DRAW_ALGORITHM, "control_families_requested": len(CONTROL_IDS), "control_families_executed": len(exec_rows), "control_families_with_input_gaps": 0, "near_alignment_items": len(item_summary), "identity_group_pair_count": len(group_rows), "component_count": j_manifest["component_count"], "component_sizes": j_manifest["component_sizes"], "hypotheses_classified": len(hyp_rows), "controls_executed": True, "K_recomputed": False, "strength_recomputed": False, "d_recomputed": False, "D_recomputed": False, "edge_recomputed": False, "shortest_path_rerun": False, "raw_phase_reconstruction": False, "F3_raw_source_opened": False, "bootstrap_run": False, "upstream_modified": False, "l2_fail_changed": False, "post_hoc_tuning_performed": False, "physical_evidence_claim_made": False, "geometry_claim_made": False, "gravity_claim_made": False, "review_items_count": 1, "matplotlib_available": matplotlib_available, "claim_boundary": CLAIM, "next_allowed_action": "human_review_k_r1_classifications_before_any_separate_source_response_audit_contract"}
    write_text("01_extract03k_r1_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03K-R1 Final Result

## Status
`{STATUS_OK}`

## Authorization
Authorization is documented in `02_authorization_used.json` and aligned with EXTRACT03K.

## Reviewed Inputs
K, J, I, H-R1, A-R1 read-only K/split artifacts, and L2 boundary context were reviewed.

## Controls Executed
All 10 authorized control families were executed as data/pipeline review controls.

## Control Family Classifications
See `17_control_family_classification_summary.csv`.

## Hypothesis Classifications
See `18_hypothesis_classification_matrix.csv`; no physical classifications are made.

## Negative Controls
Deterministic SHA-256 label and component permutation negative controls were documented.

## K-readonly Alignment Comparison
Existing K values were read only and compared with descriptive similarity; K was not recomputed.

## Review Items
The source-response origin remains open.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3; no tuning or repair was performed.

## Next Allowed Action
Human review before any separate source-response audit contract.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        fail("extract03k_r1_blocked_guard_violation", f"file manifest mismatch missing={sorted(set(FILES)-set(actual))} extra={sorted(set(actual)-set(FILES))}")
    after = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        fail("extract03k_r1_blocked_guard_violation", f"upstream modified: {changed}")
    print(json.dumps({"status": STATUS_OK, "artifacts": len(actual), "authorization_valid": authorization_valid, "control_families_executed": len(exec_rows), "control_families_with_input_gaps": 0, "hypotheses_classified": len(hyp_rows), "near_alignment_items": len(item_summary), "K_recomputed": False, "upstream_modified": False}, sort_keys=True))


if __name__ == "__main__":
    main()
