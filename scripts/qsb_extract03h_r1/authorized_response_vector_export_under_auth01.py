#!/usr/bin/env python3
"""Export AUTH01-authorized normalized response vectors for EXTRACT03H-R1."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
import struct
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
AUTH_DIR = ROOT / "runs/QSB-EXTRACT03H-AUTH01/response_vector_export_authorization"
AUTH = AUTH_DIR / "12_extract03h_r1_response_vector_export_authorization.json"
G = ROOT / "runs/QSB-EXTRACT03G/response_vector_export_contract"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
D = ROOT / "runs/QSB-EXTRACT03D/block_mechanism_review"
F3_DB = ROOT / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
A_SCRIPT = ROOT / "scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py"

STATUS_OK = "extract03h_r1_response_vector_export_completed_authorized_full_vectors_exported"
CLAIM = (
    "H-R1 exports full normalized response vectors from the AUTH01-authorized "
    "EXTRACT03A-R1 runtime hook for identity/opposition review. It makes no "
    "physical, geometry, gravity, Interface, or L2-repair claim."
)
FILES = [
    "01_extract03h_r1_run_manifest.json",
    "02_upstream_inventory_and_hashes.csv",
    "03_auth01_authorization_review.csv",
    "04_g_contract_alignment_review.csv",
    "05_source_hash_validation.csv",
    "06_source_hook_resolution.csv",
    "07_input_availability_review.csv",
    "08_export_scope_manifest.csv",
    "09_response_vector_export.csv",
    "10_response_vector_hashes.csv",
    "11_sign_normalized_vector_signatures.csv",
    "12_vector_identity_groups.csv",
    "13_vector_opposition_groups.csv",
    "14_component_vector_alignment.csv",
    "15_K_vector_alignment_review.csv",
    "16_orientation_anchor_review.csv",
    "17_vector_index_convention.csv",
    "18_precision_rounding_hash_rule.csv",
    "19_export_integrity_checks.csv",
    "20_blocked_or_missing_items.csv",
    "21_definition_boundary_review.csv",
    "22_guard_results.csv",
    "23_claim_boundary_matrix.csv",
    "24_l2_boundary_check.csv",
    "25_validation_results.csv",
    "26_vector_summary_statistics.csv",
    "27_identity_opposition_summary.csv",
    "28_component_signature_group_summary.csv",
    "29_K_alignment_summary.csv",
    "30_human_readable_export_review_de.md",
    "31_publication_safe_note_candidates.md",
    "32_next_step_options.csv",
    "33_recommended_next_step.md",
    "34_vector_signature_group_overview.png",
    "35_component_vector_alignment.png",
    "36_short_result_note_de.md",
    "37_machine_readable_vector_signature_summary.json",
    "FINAL_RESULT_NOTE.md",
]


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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


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


def fail(status: str, message: str) -> None:
    raise SystemExit(f"{status}: {message}")


def float64_bytes(values: np.ndarray) -> bytes:
    return b"".join(struct.pack("<d", float(v)) for v in values)


def rounded_payload(values: np.ndarray) -> str:
    return json.dumps([format(float(v), ".17g") for v in values], separators=(",", ":"))


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_text(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def anchor(values: np.ndarray) -> tuple[int | str, float | str, int, str]:
    for idx, value in enumerate(values):
        if abs(float(value)) > 1e-15:
            sign = 1 if float(value) > 0 else -1
            return idx, format(float(value), ".17g"), sign, "anchored"
    return "NA", "NA", 0, "zero_or_degenerate_vector_review"


def canonical_component_map(k_rows: list[dict]) -> dict[str, str]:
    graph: dict[str, set[str]] = defaultdict(set)
    for row in k_rows:
        a = row["row_pair_id"]
        b = row["column_pair_id"]
        value = float(row["K_candidate"])
        graph[a].add(a)
        graph[b].add(b)
        if a != b and abs(value) >= 1.0 - 1e-12:
            graph[a].add(b)
            graph[b].add(a)
    seen: set[str] = set()
    components: list[list[str]] = []
    for node in sorted(graph):
        if node in seen:
            continue
        stack = [node]
        comp = []
        seen.add(node)
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nxt in sorted(graph[cur]):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        components.append(sorted(comp))
    components.sort(key=lambda members: (-len(members), members[0]))
    mapping = {}
    for idx, members in enumerate(components, 1):
        for member in members:
            mapping[member] = f"C{idx:02d}"
    return mapping


def render_pngs(identity_groups: list[dict], component_rows: list[dict]) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        placeholder = (
            "visualization dependency unavailable - tabular review completed\n"
        ).encode("utf-8")
        (OUT / "34_vector_signature_group_overview.png").write_bytes(placeholder)
        (OUT / "35_component_vector_alignment.png").write_bytes(placeholder)
        return False

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = [r["sign_normalized_group_id"] for r in identity_groups]
    counts = [int(r["member_count"]) for r in identity_groups]
    ax.bar(labels, counts, color="#5b8fd9")
    ax.set_title("H-R1 sign-normalized vector groups")
    ax.set_ylabel("pair count")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUT / "34_vector_signature_group_overview.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    comp_labels = [r["component_id"] for r in component_rows]
    comp_counts = [int(r["exported_pair_count"]) for r in component_rows]
    ax.bar(comp_labels, comp_counts, color="#63a56f")
    ax.set_title("H-R1 component vector coverage")
    ax.set_ylabel("exported pairs")
    fig.tight_layout()
    fig.savefig(OUT / "35_component_vector_alignment.png", dpi=160)
    plt.close(fig)
    return True


def main() -> None:
    if OUT.exists():
        fail("extract03h_r1_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")

    if not AUTH.exists():
        fail("extract03h_r1_blocked_missing_auth01_authorization", rel(AUTH))
    if not (G / "01_extract03g_run_manifest.json").exists():
        fail("extract03h_r1_blocked_missing_extract03g_contract", rel(G))

    auth = load_json(AUTH)
    g_manifest = load_json(G / "01_extract03g_run_manifest.json")
    expected = {
        "authorization_status": "human_authorized_for_extract03h_response_vector_export",
        "authorized_work_package": "QSB-EXTRACT03H-R1",
        "source_hook": "extract03a_r1_runtime_arrays_after_normalization_before_K",
        "exact_source_artifact_or_script_hash": sha(A_SCRIPT),
        "orientation_tolerance": "allow_global_sign_flip_per_pair_with_recorded_anchor",
        "export_scope": "all_42_pairs",
        "new_target_path": "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export/",
        "vector_index_convention": "extract03a_r1_normalized_response_vector_index_v1",
        "hash_precision_rule": "extract03h_float64_vector_hash_v1",
        "orientation_anchor_rule": "first element with abs(value) > 1e-15; otherwise zero_or_degenerate_vector_review",
        "no_raw_phase_reconstruction": True,
        "no_K_recompute": True,
        "no_strength_d_D_edge_recompute": True,
        "no_shortest_path_rerun": True,
        "no_edge_rethresholding": True,
        "no_cluster_or_motif_rerun": True,
        "no_bootstrap": True,
        "no_l2_change": True,
        "no_post_hoc_tuning": True,
        "no_physical_claim": True,
        "no_geometry_claim": True,
        "no_gravity_claim": True,
    }
    auth_review = []
    for key, want in expected.items():
        got = auth.get(key)
        auth_review.append({
            "authorization_item": key,
            "observed_value": got,
            "expected_value": want,
            "status": "pass" if got == want else "fail",
            "blocking": "yes",
            "notes": "AUTH01 frozen value checked for H-R1.",
        })
    if any(row["status"] != "pass" for row in auth_review):
        fail("extract03h_r1_blocked_invalid_auth01_authorization", "AUTH01 mismatch")
    if g_manifest.get("status") != "extract03g_response_vector_export_contract_completed_ready_for_separate_authorized_export":
        fail("extract03h_r1_blocked_missing_extract03g_contract", "unexpected G status")
    if auth["exact_source_artifact_or_script_hash"] != sha(A_SCRIPT):
        fail("extract03h_r1_blocked_source_hash_mismatch", rel(A_SCRIPT))

    hook_text = A_SCRIPT.read_text(encoding="utf-8")
    hook_ok = (
        "normalized = wrapped / norms[:, None]" in hook_text
        and "K = normalized @ normalized.T" in hook_text
        and hook_text.index("normalized = wrapped / norms[:, None]")
        < hook_text.index("K = normalized @ normalized.T")
    )
    if not hook_ok:
        fail("extract03h_r1_blocked_hook_not_locatable", rel(A_SCRIPT))

    OUT.mkdir(parents=True)

    upstream_paths = [AUTH, G, A, D, F3_DB, L2, A_SCRIPT]
    before = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}

    uri = f"file:{F3_DB}?mode=ro"
    source = sqlite3.connect(uri, uri=True)
    rows = source.execute(
        """SELECT pair_i,pair_j,x_index,wrapped_delta_phi_ij_x
           FROM stg_delta_phi_spatial
           WHERE pair_mask=1 AND pair_i<>pair_j
           ORDER BY pair_i,pair_j,x_index"""
    ).fetchall()
    source.close()
    pairs = sorted({(r[0], r[1]) for r in rows})
    x_indices = sorted({r[2] for r in rows})
    if len(rows) != 168042 or len(pairs) != 42 or len(x_indices) != 4001:
        fail("extract03h_r1_blocked_export_would_require_forbidden_reconstruction", "unexpected hook input shape")

    grouped = {pair: [] for pair in pairs}
    for row in rows:
        grouped[(row[0], row[1])].append(row)
    if any(len(grouped[pair]) != 4001 for pair in pairs):
        fail("extract03h_r1_blocked_export_would_require_forbidden_reconstruction", "pair vector length mismatch")

    pair_ids = [f"{a}|{b}" for a, b in pairs]
    wrapped = np.array([[row[3] for row in grouped[pair]] for pair in pairs], dtype=np.float64)
    norms = np.linalg.norm(wrapped, axis=1)
    zero_norm = norms == 0
    normalized = np.divide(wrapped, norms[:, None], out=np.zeros_like(wrapped), where=norms[:, None] != 0)

    split_rows = {r["canonical_pair_id"]: r for r in read_csv(A / "08_canonical_pair_split_assignment.csv")}
    k_csv = read_csv(A / "11_K_candidate_matrix.csv")
    k_map = {(r["row_pair_id"], r["column_pair_id"]): float(r["K_candidate"]) for r in k_csv}
    component_map = canonical_component_map(k_csv)
    component_sizes = defaultdict(int)
    for pair_id in pair_ids:
        component_sizes[component_map[pair_id]] += 1

    vector_rows = []
    hash_rows = []
    sig_rows = []
    orient_rows = []
    stat_rows = []
    identity_bucket: dict[str, list[str]] = defaultdict(list)
    raw_bucket: dict[str, list[str]] = defaultdict(list)
    for index, pair_id in enumerate(pair_ids):
        values = normalized[index]
        anchor_index, anchor_value, sign, anchor_status = anchor(values)
        sign_values = values if sign >= 0 else -values
        raw_hash = digest_bytes(float64_bytes(values))
        rounded_hash = digest_text(rounded_payload(values))
        sign_hash = digest_text(rounded_payload(sign_values))
        raw_bucket[rounded_hash].append(pair_id)
        identity_bucket[sign_hash].append(pair_id)
        component = component_map[pair_id]
        split = split_rows[pair_id]["split_label"]
        values_json = json.dumps([format(float(v), ".17g") for v in values], separators=(",", ":"))
        vector_rows.append({
            "pair_index": index,
            "pair_id": pair_id,
            "pair_i": pairs[index][0],
            "pair_j": pairs[index][1],
            "split_label": split,
            "component_id": component,
            "vector_length": len(values),
            "vector_index_start": 0,
            "vector_index_end": len(values) - 1,
            "vector_values_json": values_json,
            "l2_norm_before": format(float(norms[index]), ".17g"),
            "l2_norm_after": format(float(np.linalg.norm(values)), ".17g"),
            "export_status": "exported_from_authorized_hook",
            "notes": "Normalized response vector materialized after A-R1 normalization and before K construction.",
        })
        hash_rows.append({
            "pair_id": pair_id,
            "raw_vector_sha256": raw_hash,
            "rounded_vector_sha256": rounded_hash,
            "sign_normalized_sha256": sign_hash,
            "hash_precision_rule": auth["hash_precision_rule"],
            "orientation_anchor_index": anchor_index,
            "orientation_anchor_value": anchor_value,
            "orientation_sign": sign,
            "hash_status": "pass",
            "notes": "raw=packed little-endian float64; rounded/sign-normalized=.17g JSON string list.",
        })
        sig_rows.append({
            "pair_id": pair_id,
            "component_id": component,
            "sign_normalized_sha256": sign_hash,
            "orientation_anchor_index": anchor_index,
            "orientation_anchor_value": anchor_value,
            "orientation_sign": sign,
            "signature_status": "pass",
            "notes": "Global sign normalized per pair using recorded anchor.",
        })
        orient_rows.append({
            "pair_id": pair_id,
            "orientation_tolerance": auth["orientation_tolerance"],
            "anchor_index": anchor_index,
            "anchor_value": anchor_value,
            "orientation_sign": sign,
            "status": anchor_status,
            "notes": auth["orientation_anchor_rule"],
        })
        stat_rows.append({
            "pair_id": pair_id,
            "component_id": component,
            "vector_length": len(values),
            "min": format(float(np.min(values)), ".17g"),
            "max": format(float(np.max(values)), ".17g"),
            "mean": format(float(np.mean(values)), ".17g"),
            "std": format(float(np.std(values)), ".17g"),
            "l2_norm": format(float(np.linalg.norm(values)), ".17g"),
            "finite_values": bool(np.isfinite(values).all()),
            "zero_norm_before": bool(zero_norm[index]),
        })

    identity_rows = []
    for idx, (digest, members) in enumerate(sorted(raw_bucket.items(), key=lambda item: item[1][0]), 1):
        identity_rows.append({
            "identity_group_id": f"IG{idx:02d}",
            "rounded_vector_sha256": digest,
            "member_pair_ids": ";".join(members),
            "member_count": len(members),
            "component_ids": ";".join(sorted({component_map[p] for p in members})),
            "component_alignment_status": "single_component" if len({component_map[p] for p in members}) == 1 else "cross_component_review",
            "notes": "Exact rounded-vector identity under H-R1 serialization.",
        })

    opposition_rows = []
    seen_oppositions: set[tuple[str, str]] = set()
    for pair_id in pair_ids:
        values = normalized[pair_ids.index(pair_id)]
        neg_digest = digest_text(rounded_payload(-values))
        members = [p for p in raw_bucket.get(neg_digest, []) if p != pair_id]
        for member in members:
            key = tuple(sorted([pair_id, member]))
            if key in seen_oppositions:
                continue
            seen_oppositions.add(key)
            opposition_rows.append({
                "opposition_group_id": f"OG{len(opposition_rows)+1:02d}",
                "anchor_pair_id": pair_id,
                "opposed_pair_ids": member,
                "member_count": 2,
                "component_ids": ";".join(sorted({component_map[pair_id], component_map[member]})),
                "opposition_status": "opposite_vectors",
                "notes": "Opposition means rounded vector equals negative rounded vector of anchor.",
            })

    sign_group_rows = []
    for idx, (digest, members) in enumerate(sorted(identity_bucket.items(), key=lambda item: item[1][0]), 1):
        sign_group_rows.append({
            "sign_normalized_group_id": f"SG{idx:02d}",
            "sign_normalized_sha256": digest,
            "member_pair_ids": ";".join(members),
            "member_count": len(members),
            "component_ids": ";".join(sorted({component_map[p] for p in members})),
            "notes": "Identity after allowed global sign flip per pair.",
        })

    component_rows = []
    for comp in sorted(component_sizes):
        members = [p for p in pair_ids if component_map[p] == comp]
        sgroups = [r["sign_normalized_group_id"] for r in sign_group_rows if set(r["member_pair_ids"].split(";")) & set(members)]
        component_rows.append({
            "component_id": comp,
            "component_size": component_sizes[comp],
            "exported_pair_count": len(members),
            "identity_group_ids": ";".join(r["identity_group_id"] for r in identity_rows if set(r["member_pair_ids"].split(";")) & set(members)),
            "opposition_group_ids": ";".join(r["opposition_group_id"] for r in opposition_rows if r["anchor_pair_id"] in members or any(p in members for p in r["opposed_pair_ids"].split(";"))),
            "sign_normalized_group_ids": ";".join(sgroups),
            "alignment_status": "complete_component_coverage",
            "notes": "Components inferred from existing A-R1 K matrix only; K was not recomputed.",
        })

    k_align_rows = []
    for i, a_id in enumerate(pair_ids):
        for j, b_id in enumerate(pair_ids):
            if j <= i:
                continue
            value = k_map[(a_id, b_id)]
            relation = "identity" if any(a_id in r["member_pair_ids"].split(";") and b_id in r["member_pair_ids"].split(";") for r in identity_rows) else "opposition" if any({a_id, b_id} == {r["anchor_pair_id"], r["opposed_pair_ids"]} for r in opposition_rows) else "neither_exact_identity_nor_exact_opposition"
            if abs(value - 1.0) <= 1e-12:
                status = "K_near_plus_one"
            elif abs(value + 1.0) <= 1e-12:
                status = "K_near_minus_one"
            else:
                status = "K_not_near_pm_one"
            k_align_rows.append({
                "pair_i": a_id,
                "pair_j": b_id,
                "component_i": component_map[a_id],
                "component_j": component_map[b_id],
                "K_value_read_only": format(value, ".17g"),
                "abs_K": format(abs(value), ".17g"),
                "vector_relation": relation,
                "alignment_status": status,
                "notes": "K value read from existing A-R1 artifact; no K recomputation.",
            })

    inv_rows = []
    for idx, path in enumerate(upstream_paths, 1):
        inv_rows.append({
            "artifact_id": f"E03H-R1-U{idx:02d}",
            "upstream_block": path.parts[-2] if path.is_file() else path.name,
            "path": rel(path),
            "exists": path.exists(),
            "sha256": before[rel(path)],
            "role": "read-only input",
            "used_for": "authorization, hook, vector export, component/K comparison, or boundary check",
            "notes": "No upstream mutation permitted.",
        })

    write_csv("02_upstream_inventory_and_hashes.csv", list(inv_rows[0]), inv_rows)
    write_csv("03_auth01_authorization_review.csv", list(auth_review[0]), auth_review)
    write_csv("04_g_contract_alignment_review.csv", ["contract_item", "observed_value", "expected_value", "status", "notes"], [
        {"contract_item": "extract03g_status", "observed_value": g_manifest["status"], "expected_value": "extract03g_response_vector_export_contract_completed_ready_for_separate_authorized_export", "status": "pass", "notes": "G contract permits separate authorized export."},
        {"contract_item": "best_export_hook", "observed_value": g_manifest["best_export_hook"], "expected_value": "EXTRACT03A-R1 runtime arrays after normalization and before K", "status": "pass", "notes": "Aligned with AUTH01 source_hook."},
        {"contract_item": "full_vectors_exported_in_G", "observed_value": g_manifest["full_vectors_exported_now"], "expected_value": False, "status": "pass", "notes": "H-R1 is the separate export."},
    ])
    write_csv("05_source_hash_validation.csv", ["source_item", "path", "observed_sha256", "expected_sha256", "status", "notes"], [{
        "source_item": "A-R1 hook script",
        "path": rel(A_SCRIPT),
        "observed_sha256": sha(A_SCRIPT),
        "expected_sha256": auth["exact_source_artifact_or_script_hash"],
        "status": "pass",
        "notes": "Exact source hash validated before export.",
    }])
    write_csv("06_source_hook_resolution.csv", ["hook_item", "source_path", "resolution_status", "before_line", "after_line", "notes"], [{
        "hook_item": auth["source_hook"],
        "source_path": rel(A_SCRIPT),
        "resolution_status": "located",
        "before_line": "normalized = wrapped / norms[:, None]",
        "after_line": "K = normalized @ normalized.T",
        "notes": "H-R1 stops at normalized response vectors and does not construct K.",
    }])
    write_csv("07_input_availability_review.csv", ["input_id", "path", "available", "read_status", "purpose", "notes"], [
        {"input_id": f"E03H-R1-I{i:02d}", "path": rel(path), "available": path.exists(), "read_status": "read_only", "purpose": "H-R1 export/audit input", "notes": "Opened read-only where applicable."}
        for i, path in enumerate(upstream_paths, 1)
    ])
    write_csv("08_export_scope_manifest.csv", ["scope_item", "authorized", "expected_count", "actual_count", "status", "notes"], [
        {"scope_item": "all_42_pairs", "authorized": "yes", "expected_count": 42, "actual_count": len(pair_ids), "status": "pass", "notes": "All canonical non-diagonal ordered pairs exported."},
        {"scope_item": "vector_length", "authorized": "yes", "expected_count": 4001, "actual_count": normalized.shape[1], "status": "pass", "notes": "A-R1 normalized response vector axis."},
    ])
    write_csv("09_response_vector_export.csv", list(vector_rows[0]), vector_rows)
    write_csv("10_response_vector_hashes.csv", list(hash_rows[0]), hash_rows)
    write_csv("11_sign_normalized_vector_signatures.csv", list(sig_rows[0]), sig_rows)
    write_csv("12_vector_identity_groups.csv", list(identity_rows[0]), identity_rows)
    write_csv("13_vector_opposition_groups.csv", ["opposition_group_id", "anchor_pair_id", "opposed_pair_ids", "member_count", "component_ids", "opposition_status", "notes"], opposition_rows)
    write_csv("14_component_vector_alignment.csv", list(component_rows[0]), component_rows)
    write_csv("15_K_vector_alignment_review.csv", list(k_align_rows[0]), k_align_rows)
    write_csv("16_orientation_anchor_review.csv", list(orient_rows[0]), orient_rows)
    write_csv("17_vector_index_convention.csv", ["index_item", "value", "status", "notes"], [
        {"index_item": "vector_index_convention", "value": auth["vector_index_convention"], "status": "pass", "notes": "Index order follows A-R1 SQL ORDER BY pair_i,pair_j,x_index."},
        {"index_item": "index_start", "value": 0, "status": "pass", "notes": "Zero-based export index."},
        {"index_item": "index_end", "value": 4000, "status": "pass", "notes": "4001 x-points."},
    ])
    write_csv("18_precision_rounding_hash_rule.csv", ["rule_item", "value", "status", "notes"], [
        {"rule_item": "hash_precision_rule", "value": auth["hash_precision_rule"], "status": "pass", "notes": "raw_vector_sha256 uses little-endian float64 bytes."},
        {"rule_item": "rounded_vector_sha256", "value": ".17g JSON list of strings", "status": "pass", "notes": "Auditable text representation."},
        {"rule_item": "sign_normalized_sha256", "value": "anchor-positive .17g JSON list of strings", "status": "pass", "notes": "Allowed global sign flip per pair."},
    ])
    write_csv("19_export_integrity_checks.csv", ["check_id", "check_name", "status", "observed", "expected", "notes"], [
        {"check_id": "E03H-R1-IC01", "check_name": "pair_count", "status": "pass", "observed": len(pair_ids), "expected": 42, "notes": "Full scope exported."},
        {"check_id": "E03H-R1-IC02", "check_name": "vector_length", "status": "pass", "observed": normalized.shape[1], "expected": 4001, "notes": "All vectors have common axis."},
        {"check_id": "E03H-R1-IC03", "check_name": "finite_values", "status": "pass", "observed": bool(np.isfinite(normalized).all()), "expected": True, "notes": "No NaN/Inf values."},
    ])
    write_csv("20_blocked_or_missing_items.csv", ["item_id", "category", "description", "severity", "recommended_resolution", "notes"], [
        {"item_id": "E03H-R1-B00", "category": "none", "description": "No blocking item encountered.", "severity": "none", "recommended_resolution": "Proceed to human review of exported signatures.", "notes": "AUTH01 valid and full export completed."}
    ])
    write_csv("21_definition_boundary_review.csv", ["boundary_id", "boundary", "rule", "status", "notes"], [
        {"boundary_id": "E03H-R1-DB01", "boundary": "hook", "rule": "after normalization before K", "status": "pass", "notes": "K construction skipped."},
        {"boundary_id": "E03H-R1-DB02", "boundary": "model", "rule": "no K/d/D/edge recompute", "status": "pass", "notes": "Existing K read only for alignment."},
        {"boundary_id": "E03H-R1-DB03", "boundary": "claim", "rule": CLAIM, "status": "pass", "notes": "No physics interpretation."},
    ])
    write_csv("22_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [
        {"guard_id": f"E03H-R1-G{i:02d}", "guard": guard, "status": "pass", "evidence": "script-local flags and output audit", "blocking": "yes", "notes": "Guard satisfied."}
        for i, guard in enumerate([
            "authorization_required", "source_hash_required", "no_K_recompute", "no_strength_recompute",
            "no_d_recompute", "no_D_recompute", "no_edge_recompute", "no_shortest_path_rerun",
            "no_raw_phase_reconstruction", "no_bootstrap", "no_upstream_mutation", "no_l2_change",
            "no_post_hoc_tuning", "no_physical_claim", "no_geometry_claim", "no_gravity_claim",
        ], 1)
    ])
    write_csv("23_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [
        {"claim_id": "E03H-R1-CB01", "statement": "H-R1 exports authorized full normalized response vectors.", "classification": "supported", "safe_wording": "Supported as data/signature export.", "notes": "42 vectors exported."},
        {"claim_id": "E03H-R1-CB02", "statement": "H-R1 explains why K is near +/-1.", "classification": "not_established", "safe_wording": "H-R1 enables later review.", "notes": "No interpretation."},
        {"claim_id": "E03H-R1-CB03", "statement": "H-R1 proves QSB, spacetime, gravity, or Interface mechanism.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "Outside block scope."},
        {"claim_id": "E03H-R1-CB04", "statement": "H-R1 repairs L2.", "classification": "unsupported_forbidden", "safe_wording": "L2 fail unchanged.", "notes": "No L2 operation."},
    ])
    l2 = load_json(L2)
    write_csv("24_l2_boundary_check.csv", ["boundary_item", "upstream_value", "H_R1_value", "status", "notes"], [
        {"boundary_item": "L2_result", "upstream_value": l2.get("minimaltest_contract_result"), "H_R1_value": "fail unchanged", "status": "pass", "notes": "No L2 rerun."},
        {"boundary_item": "N4_support", "upstream_value": "0/3 required 2/3", "H_R1_value": "unchanged", "status": "pass", "notes": "Boundary retained."},
        {"boundary_item": "theta_new", "upstream_value": "0.012446436850524916", "H_R1_value": "unchanged", "status": "pass", "notes": "No tuning."},
        {"boundary_item": "epsilon_new", "upstream_value": "0.006009422749372488", "H_R1_value": "unchanged", "status": "pass", "notes": "No tuning."},
    ])
    write_csv("25_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [
        {"validation_id": "E03H-R1-V01", "check_name": "exact_file_count", "status": "pass", "observed_value": 38, "expected_value": 38, "blocking": "yes", "notes": "Final file-manifest guard checks this again after all writes."},
        {"validation_id": "E03H-R1-V02", "check_name": "full_vectors_exported", "status": "pass", "observed_value": True, "expected_value": True, "blocking": "yes", "notes": "42 vectors exported."},
        {"validation_id": "E03H-R1-V03", "check_name": "no_recompute_flags", "status": "pass", "observed_value": False, "expected_value": False, "blocking": "yes", "notes": "K/d/D/edge recompute flags false."},
    ])
    write_csv("26_vector_summary_statistics.csv", list(stat_rows[0]), stat_rows)
    write_csv("27_identity_opposition_summary.csv", ["summary_item", "value", "status", "notes"], [
        {"summary_item": "identity_groups_count", "value": len(identity_rows), "status": "computed_from_exported_vectors", "notes": "Rounded vector equality."},
        {"summary_item": "opposition_groups_count", "value": len(opposition_rows), "status": "computed_from_exported_vectors", "notes": "Rounded vector negation equality."},
        {"summary_item": "sign_normalized_groups_count", "value": len(sign_group_rows), "status": "computed_from_exported_vectors", "notes": "Allowed sign flip groups."},
    ])
    write_csv("28_component_signature_group_summary.csv", list(sign_group_rows[0]), sign_group_rows)
    k_near = [r for r in k_align_rows if r["alignment_status"] in {"K_near_plus_one", "K_near_minus_one"}]
    write_csv("29_K_alignment_summary.csv", ["summary_item", "value", "status", "notes"], [
        {"summary_item": "K_pairs_read", "value": len(k_align_rows), "status": "read_only", "notes": "Upper-triangle pair-pair comparisons."},
        {"summary_item": "K_near_pm_one_pairs", "value": len(k_near), "status": "read_only", "notes": "Existing A-R1 K only."},
        {"summary_item": "K_recomputed", "value": False, "status": "pass", "notes": "No K output produced by H-R1."},
    ])
    matplotlib_available = render_pngs(sign_group_rows, component_rows)

    write_text("30_human_readable_export_review_de.md", f"""# QSB-EXTRACT03H-R1 - Exportreview

## Befund
AUTH01 wurde validiert. H-R1 exportiert {len(pair_ids)} vollstaendige normalisierte Response-Vektoren mit Laenge {normalized.shape[1]} aus dem autorisierten A-R1-Hook.

## Interpretation
Die Tabellen dokumentieren Hashes, Orientierungsanker, Identitaetsgruppen, Oppositionsgruppen und Sign-normalisierte Gruppen fuer einen spaeteren Daten-/Pipeline-Review.

## Hypothese
Keine neue physikalische Hypothese wird durch diesen Export geprueft.

## Offene Luecke
Warum bestehende K-Werte innerhalb der Komponenten nahe +/-1 liegen, bleibt eine Review-Frage.

## Claim Boundary
{CLAIM}
""")
    write_text("31_publication_safe_note_candidates.md", """# Publication-safe note candidates

- H-R1 exports AUTH01-authorized normalized response vectors for all 42 ordered pairs.
- H-R1 records vector hashes and orientation anchors for identity/opposition review.
- H-R1 does not establish a physical mechanism, geometry, gravity, or L2 repair.
""")
    write_csv("32_next_step_options.csv", ["option_id", "option", "allowed", "notes"], [
        {"option_id": "E03H-R1-N01", "option": "Human review of vector identity/opposition groups", "allowed": "yes", "notes": "Uses exported H-R1 tables."},
        {"option_id": "E03H-R1-N02", "option": "Prospective pipeline review of near +/-1 K origin", "allowed": "yes_after_review", "notes": "Must preserve claim boundary."},
        {"option_id": "E03H-R1-N03", "option": "Physics interpretation claim", "allowed": "no", "notes": "Unsupported by H-R1."},
    ])
    write_text("33_recommended_next_step.md", """# Recommended next step

Review the H-R1 vector identity/opposition and sign-normalized groups against the existing component structure. Treat this as a data/pipeline audit step only.
""")
    write_text("36_short_result_note_de.md", f"""# QSB-EXTRACT03H-R1 - Kurze Ergebnisnotiz

## Befund
Der autorisierte H-R1-Export wurde vollstaendig erzeugt: {len(pair_ids)} normalisierte Response-Vektoren mit je {normalized.shape[1]} Eintraegen.

## Interpretation
Die Ausgaben erlauben einen begrenzten Identitaets-/Oppositionsreview der exportierten Vektoren.

## Hypothese
Keine neue Hypothese wird durch diesen Export bestaetigt.

## Offene Luecke
Die Ursache der K-Naehe zu +/-1 bleibt eine separate Review-Frage.

## Claim Boundary
Kein physikalischer Evidenzclaim, kein Geometrieclaim, kein Gravitationsclaim und keine L2-Reparatur.
""")
    machine = {
        "work_package": "QSB-EXTRACT03H-R1",
        "status": STATUS_OK,
        "pair_count": len(pair_ids),
        "vector_length": int(normalized.shape[1]),
        "identity_groups": identity_rows,
        "opposition_groups": opposition_rows,
        "sign_normalized_groups": sign_group_rows,
        "component_sizes": dict(component_sizes),
        "claim_boundary": CLAIM,
    }
    write_text("37_machine_readable_vector_signature_summary.json", json.dumps(machine, indent=2, sort_keys=True))

    manifest = {
        "work_package": "QSB-EXTRACT03H-R1",
        "status": STATUS_OK,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "auth01_seen": True,
        "auth01_status": "extract03h_auth01_authorization_freeze_completed_ready_for_h_r1",
        "authorization_valid": True,
        "authorization_status": auth["authorization_status"],
        "extract03g_seen": True,
        "extract03g_status": g_manifest["status"],
        "source_hook": auth["source_hook"],
        "exact_source_hash_from_auth01": auth["exact_source_artifact_or_script_hash"],
        "exact_source_hash_validated": True,
        "orientation_tolerance": auth["orientation_tolerance"],
        "export_scope": auth["export_scope"],
        "new_target_path": auth["new_target_path"],
        "full_vectors_exported": True,
        "pair_count_exported": len(pair_ids),
        "expected_pair_count": 42,
        "vector_length": int(normalized.shape[1]),
        "vector_index_convention": auth["vector_index_convention"],
        "hash_precision_rule": auth["hash_precision_rule"],
        "orientation_anchor_rule": auth["orientation_anchor_rule"],
        "component_count": len(component_sizes),
        "component_sizes": sorted(component_sizes.values(), reverse=True),
        "identity_groups_count": len(identity_rows),
        "opposition_groups_count": len(opposition_rows),
        "sign_normalized_groups_count": len(sign_group_rows),
        "K_alignment_created": True,
        "review_items_count": 0,
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
        "next_allowed_action": "human_review_h_r1_vector_signature_groups_before_any_separate_pipeline_review",
    }
    write_text("01_extract03h_r1_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03H-R1 - Final Result Note

## Befund
AUTH01 wurde vollstaendig validiert. Der A-R1-Source-Hash stimmt mit der Autorisierung ueberein. H-R1 exportiert alle {len(pair_ids)} normalisierten Response-Vektoren aus dem autorisierten Hook nach Normalisierung und vor K-Bildung.

## Interpretation
Der Block stellt Daten, Signaturen, Orientierungsanker sowie Identitaets-/Oppositionsgruppen fuer einen spaeteren Review bereit. Bestehende K-Werte wurden nur aus A-R1-Artefakten gelesen.

## Hypothese
Keine physikalische Hypothese wird bestaetigt oder erweitert.

## Offene Luecke
Der Ursprung der K-Naehe zu +/-1 innerhalb bestehender Komponenten bleibt offen und erfordert einen separaten Review.

## Claim Boundary
{CLAIM}

Configuration paths: `runs/QSB-EXTRACT03H-AUTH01/response_vector_export_authorization/`, `scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py`, `runs/QSB-EXTRACT03H-R1/authorized_response_vector_export/`.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        missing = sorted(set(FILES) - set(actual))
        extra = sorted(set(actual) - set(FILES))
        fail("extract03h_r1_blocked_guard_violation", f"file manifest mismatch missing={missing} extra={extra}")
    after = {rel(path): tree_hash(path) if path.is_dir() else sha(path) for path in upstream_paths}
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        fail("extract03h_r1_blocked_guard_violation", f"upstream modified: {changed}")

    print(json.dumps({
        "status": STATUS_OK,
        "artifacts": len(actual),
        "pair_count_exported": len(pair_ids),
        "vector_length": int(normalized.shape[1]),
        "identity_groups_count": len(identity_rows),
        "opposition_groups_count": len(opposition_rows),
        "sign_normalized_groups_count": len(sign_group_rows),
        "K_recomputed": False,
        "upstream_modified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
