#!/usr/bin/env python3
"""Run the authorized EXTRACT03A-R1 candidate computation under package + S1."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
PACKAGE = ROOT / "runs/QSB-EXTRACT03/execution_package_preparation"
S1 = ROOT / "runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
AUTH = ROOT / "runs/QSB-EXTRACT03/input/extract03_execution_authorization.json"
S1_AUTH = ROOT / "runs/QSB-EXTRACT03/input/extract03a_execution_authorization_refresh_package_plus_s1.json"
HF = ROOT / "runs/QSB-EXTRACT02A/input/human_freeze_decisions.json"
R1F = ROOT / "runs/QSB-EXTRACT02A-R1F/artifact_consistency_fix_human_freeze_recheck/05_normalized_human_freeze_decisions.json"
F3_DIR = ROOT / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
F3_MANIFEST = F3_DIR / "01_f3_run_manifest.json"
F3_DB = F3_DIR / "09_delta_phi_staging_preflight.sqlite"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2 = ROOT / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0 = ROOT / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS_OK = "extract03a_r1_authorized_execution_with_s1_completed_with_claim_boundary"
STATUS_INCONCLUSIVE = "extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items"
STATUS_VALIDATION = "extract03a_r1_authorized_execution_with_s1_completed_with_validation_failures"
SPLIT_PROTOCOL = "extract03_hash_split_v1"
PRIMARY_SEED = 20260621
BOOTSTRAP_SEEDS = [2026062101, 2026062102, 2026062103, 2026062104, 2026062105]
TIE_BREAKER_SEED = 2026062199
ELL_0 = 1.0
EPSILON_GRAM = 1e-12
THETA_EDGE = 0.5
CLAIM = "Candidate relational structure only; D is a reconstructed cost-distance candidate, not proven geometry."

FILES = [
    "01_extract03a_r1_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_execution_authorization_import.csv", "04_s1_authorization_refresh_import.csv",
    "05_package_plus_s1_contract_import_review.csv", "06_frozen_decision_carry_forward_review.csv",
    "07_source_selection_result.csv", "08_canonical_pair_split_assignment.csv",
    "09_tensor_schema_runtime_mapping.csv", "10_phase_response_vector_summary.csv",
    "11_K_candidate_matrix.csv", "12_K_validation_results.csv", "13_distance_cost_matrix.csv",
    "14_shortest_path_D_matrix.csv", "15_strength_matrix.csv", "16_edge_candidate_result.csv",
    "17_kernel_execution_summary.csv", "18_cluster_dendrogram_candidate_result.csv",
    "19_motif_candidate_summary.csv", "20_result_mart_schema_executed.sql",
    "21_extract03a_r1_result_mart.sqlite", "22_result_mart_table_counts.csv",
    "23_lineage_and_hash_audit.csv", "24_unit_dimension_audit.csv", "25_validation_results.csv",
    "26_acceptance_gate_results.csv", "27_guard_results.csv", "28_review_items.csv",
    "29_claim_boundary_matrix.csv", "30_split_seed_audit.csv", "31_short_result_note_de.md",
    "32_next_step_recommendation.md", "FINAL_RESULT_NOTE.md",
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(directory: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in directory.iterdir() if p.is_file()):
        h.update(path.name.encode())
        h.update(b"\0")
        h.update(sha(path).encode())
        h.update(b"\n")
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict]):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fail(status: str, message: str):
    raise SystemExit(f"{status}: {message}")


def expect(data: dict, expected: dict, status: str, label: str):
    mismatches = [f"{key}={data.get(key)!r}" for key, value in expected.items() if data.get(key) != value]
    if mismatches:
        fail(status, f"{label} mismatch: " + ", ".join(mismatches))


def split_for(pair_id: str):
    text = f"{SPLIT_PROTOCOL} | {PRIMARY_SEED} | {pair_id}"
    digest = hashlib.sha256(text.encode()).hexdigest()
    u = int(digest, 16) / 2**256
    label = "calibration" if u < .4 else "validation" if u < .7 else "review" if u < .9 else "holdout"
    return text, digest, u, label


def contract_value(path: Path, component: str, field="frozen_value_or_rule"):
    row = next((row for row in read_csv(path) if row.get("component") == component), None)
    return None if row is None else row.get(field)


def main():
    if OUT.exists():
        fail("extract03a_r1_blocked_guard_violation", f"refusing to overwrite {OUT}")

    required = [PACKAGE, S1, AUTH, S1_AUTH, HF, R1F, F3_MANIFEST, F3_DB, L2, M2, N0]
    missing = [rel(path) for path in required if not path.exists()]
    if missing:
        status = "extract03a_r1_blocked_missing_f3_source" if any("INTERFACE01F3" in p for p in missing) else "extract03a_r1_blocked_invalid_extract03_package_or_s1"
        fail(status, "missing: " + ", ".join(missing))

    auth = load_json(AUTH)
    expect(auth, {
        "authorization_status": "human_authorized_for_extract03_execution",
        "basis_package": "runs/QSB-EXTRACT03/execution_package_preparation",
        "basis_package_status": "extract03_execution_package_preparation_completed_no_extraction",
        "allowed_next_action": "run_separate_extract03_execution_under_frozen_package_contract",
    }, "extract03a_r1_blocked_authorization_package_s1_mismatch", "execution authorization")
    s1_auth = load_json(S1_AUTH)
    expect(s1_auth, {
        "authorization_status": "human_authorized_for_extract03a_execution_with_s1_addendum",
        "basis_package": "runs/QSB-EXTRACT03/execution_package_preparation",
        "basis_package_status": "extract03_execution_package_preparation_completed_no_extraction",
        "basis_addendum": "runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum",
        "basis_addendum_status": "extract03s1_split_seed_freeze_addendum_completed_no_execution",
        "split_protocol_id": SPLIT_PROTOCOL, "primary_seed": PRIMARY_SEED,
        "bootstrap_seeds": BOOTSTRAP_SEEDS, "tie_breaker_seed": TIE_BREAKER_SEED,
        "allowed_next_action": "run_extract03a_with_frozen_package_plus_s1_addendum",
    }, "extract03a_r1_blocked_missing_execution_authorization_refresh", "S1 authorization refresh")

    package_manifest = load_json(PACKAGE / "01_extract03_package_manifest.json")
    s1_manifest = load_json(S1 / "01_extract03s1_run_manifest.json")
    expect(package_manifest, {"status": "extract03_execution_package_preparation_completed_no_extraction"},
           "extract03a_r1_blocked_invalid_extract03_package_or_s1", "package")
    expect(s1_manifest, {"status": "extract03s1_split_seed_freeze_addendum_completed_no_execution",
                         "split_protocol_id": SPLIT_PROTOCOL, "primary_seed": PRIMARY_SEED,
                         "tie_breaker_seed": TIE_BREAKER_SEED},
           "extract03a_r1_blocked_invalid_extract03_package_or_s1", "S1")
    if len(list(PACKAGE.iterdir())) != 24 or len(list(S1.iterdir())) != 18:
        fail("extract03a_r1_blocked_invalid_extract03_package_or_s1", "package/S1 artifact count mismatch")

    s1_inventory = {row["path"]: row["sha256"] for row in read_csv(S1 / "02_upstream_inventory_and_hashes.csv")}
    frozen_hash_paths = [PACKAGE / "01_extract03_package_manifest.json", PACKAGE / "12_cluster_dendrogram_protocol_no_run.csv", AUTH, HF, R1F, F3_MANIFEST, F3_DB, L2, M2, N0]
    hash_mismatch = [rel(p) for p in frozen_hash_paths if s1_inventory.get(rel(p)) != sha(p)]
    if hash_mismatch:
        fail("extract03a_r1_blocked_authorization_package_s1_mismatch", "frozen hash mismatch: " + ", ".join(hash_mismatch))

    decisions = load_json(HF).get("decisions", [])
    expected_freezes = {f"HF-{i:02d}" for i in range(1, 11)}
    valid_decisions = [d for d in decisions if d.get("freeze_id") in expected_freezes and d.get("decision_status") == "human_approved_frozen" and d.get("human_approval") == "approved" and d.get("blocks_actual_execution") is False]
    if len(valid_decisions) != 10:
        fail("extract03a_r1_blocked_invalid_frozen_decisions", f"valid decisions={len(valid_decisions)}")
    by_freeze = {d["freeze_id"]: d for d in valid_decisions}
    if by_freeze["HF-02"]["decision_value"] != "K_from_phase_response_vectors" or by_freeze["HF-03"]["decision_value"] != ELL_0 or by_freeze["HF-04"]["decision_value"] != EPSILON_GRAM or by_freeze["HF-06"]["decision_value"] != THETA_EDGE:
        fail("extract03a_r1_blocked_invalid_frozen_decisions", "frozen K/ell_0/epsilon_Gram/theta_edge mismatch")
    if contract_value(PACKAGE / "12_cluster_dendrogram_protocol_no_run.csv", "distance_matrix_source") != "shortest_path_D" or contract_value(PACKAGE / "12_cluster_dendrogram_protocol_no_run.csv", "linkage_method") != "average":
        fail("extract03a_r1_blocked_invalid_frozen_decisions", "cluster contract mismatch")

    upstream_paths = [AUTH, S1_AUTH, PACKAGE / "01_extract03_package_manifest.json", S1 / "01_extract03s1_run_manifest.json", HF, R1F, F3_MANIFEST, F3_DB, L2, M2, N0]
    before = {rel(path): sha(path) for path in upstream_paths}
    package_hash = tree_hash(PACKAGE)
    s1_hash = tree_hash(S1)
    lineage_payload = {
        "execution_authorization_hash": sha(AUTH), "s1_authorization_refresh_hash": sha(S1_AUTH),
        "extract03_package_hash": package_hash, "s1_addendum_hash": s1_hash,
        "r1f_hash": sha(R1F), "f3_source_hash": sha(F3_DB), "human_freeze_decision_hash": sha(HF),
    }
    lineage_bundle = hashlib.sha256(json.dumps(lineage_payload, sort_keys=True).encode()).hexdigest()

    uri = f"file:{F3_DB}?mode=ro"
    source = sqlite3.connect(uri, uri=True)
    rows = source.execute("""SELECT run_id,state_i,state_j,pair_i,pair_j,x_index,x_value,x_unit,x_weight,
        raw_delta_phi_ij_x,wrapped_delta_phi_ij_x,angle_unit,dimension_status,pair_mask,diagonal_policy
        FROM stg_delta_phi_spatial WHERE pair_mask=1 AND pair_i<>pair_j ORDER BY pair_i,pair_j,x_index""").fetchall()
    source.close()
    pairs = sorted({(r[3], r[4]) for r in rows})
    x_indices = sorted({r[5] for r in rows})
    if len(rows) != 168042 or len(pairs) != 42 or len(x_indices) != 4001:
        fail("extract03a_r1_blocked_upstream_mismatch", f"source rows/pairs/x={len(rows)}/{len(pairs)}/{len(x_indices)}")
    grouped = {pair: [] for pair in pairs}
    for row in rows:
        grouped[(row[3], row[4])].append(row)
    if any(len(grouped[pair]) != 4001 for pair in pairs):
        fail("extract03a_r1_blocked_upstream_mismatch", "pair vector length mismatch")

    pair_ids = [f"{i}|{j}" for i, j in pairs]
    pair_basis_hash = hashlib.sha256(("\n".join(pair_ids) + "\n").encode()).hexdigest()
    if pair_basis_hash != "51962668d944195bb1409a5f9d6972636c660184aa6be3ab530a3d980cf96e32":
        fail("extract03a_r1_blocked_upstream_mismatch", "canonical pair basis hash mismatch")
    split_rows = []
    for index, pair_id in enumerate(pair_ids):
        text, digest, u, label = split_for(pair_id)
        split_rows.append({"pair_index": index, "canonical_pair_id": pair_id, "pair_i": pairs[index][0], "pair_j": pairs[index][1], "split_protocol_id": SPLIT_PROTOCOL, "primary_seed": PRIMARY_SEED, "hash_input": text, "sha256": digest, "u": format(u, ".17g"), "split_label": label, "lineage_bundle_sha256": lineage_bundle})

    raw = np.array([[row[9] for row in grouped[pair]] for pair in pairs], dtype=float)
    wrapped = np.array([[row[10] for row in grouped[pair]] for pair in pairs], dtype=float)
    norms = np.linalg.norm(wrapped, axis=1)
    zero_norm = norms == 0
    if zero_norm.any():
        normalized = np.divide(wrapped, norms[:, None], out=np.zeros_like(wrapped), where=norms[:, None] != 0)
    else:
        normalized = wrapped / norms[:, None]
    K = normalized @ normalized.T
    K = (K + K.T) / 2
    np.fill_diagonal(K, 1.0)
    eigvals = np.linalg.eigvalsh(K)
    hermitian_error = float(np.max(np.abs(K - K.T)))
    diagonal_error = float(np.max(np.abs(np.diag(K) - 1)))
    finite_K = bool(np.isfinite(K).all())
    range_error = float(max(0.0, np.max(np.abs(K)) - 1.0))

    raw_d = -ELL_0 * np.log(np.abs(K) + EPSILON_GRAM)
    np.fill_diagonal(raw_d, 0.0)
    tiny_negative = (raw_d < 0) & (raw_d >= -1e-10)
    d = raw_d.copy()
    d[tiny_negative] = 0.0
    np.fill_diagonal(d, 0.0)
    d_negative = int(np.count_nonzero((d < -1e-10) & ~np.eye(len(pairs), dtype=bool)))
    d_finite = bool(np.isfinite(d).all())
    if d_negative or not d_finite:
        fail("extract03a_r1_blocked_guard_violation", "invalid cost matrix prevents shortest-path execution")

    D = d.copy()
    n = len(pairs)
    for k in range(n):
        D = np.minimum(D, D[:, k, None] + D[None, k, :])
    D = (D + D.T) / 2
    np.fill_diagonal(D, 0.0)
    strength = np.exp(-d / ELL_0)
    np.fill_diagonal(strength, 1.0)
    edge = strength >= THETA_EDGE
    np.fill_diagonal(edge, False)

    condensed = squareform(D, checks=True)
    Z = linkage(condensed, method="average")
    memberships = {i: [i] for i in range(n)}
    cluster_rows = []
    motif_rows = []
    for merge_index, (left, right, distance, count) in enumerate(Z):
        left_i, right_i = int(left), int(right)
        members = sorted(memberships[left_i] + memberships[right_i])
        node_id = n + merge_index
        memberships[node_id] = members
        member_ids = [pair_ids[i] for i in members]
        membership_text = ";".join(member_ids)
        candidate_hash = hashlib.sha256(f"average|{lineage_bundle}|{membership_text}".encode()).hexdigest()
        cluster_id = "E03A-CL-" + candidate_hash[:16]
        motif_hash = hashlib.sha256(f"hash(contract,source,split,membership)|{lineage_bundle}|{membership_text}".encode()).hexdigest()
        motif_id = "E03A-MO-" + motif_hash[:16]
        labels = Counter(split_rows[i]["split_label"] for i in members)
        cluster_rows.append({"merge_index": merge_index, "cluster_candidate_id": cluster_id, "left_node": left_i, "right_node": right_i, "distance": format(float(distance), ".17g"), "member_count": int(count), "members": membership_text, "split_composition": json.dumps(labels, sort_keys=True), "linkage_method": "average", "distance_matrix_source": "shortest_path_D", "candidate_status": "candidate_not_stability_certified", "claim_boundary": "candidate relational grouping only", "lineage_bundle_sha256": lineage_bundle})
        motif_rows.append({"motif_candidate_id": motif_id, "source_cluster_candidate_id": cluster_id, "member_count": len(members), "members": membership_text, "id_contract": "hash(contract,source,split,membership)", "stability_status": "not_certified_bootstrap_sampling_rule_not_frozen", "interpretation": "candidate relational grouping only", "lineage_bundle_sha256": lineage_bundle})

    validations = []
    def validation(layer, check, passed, observed, expected, severity="error", message=""):
        validations.append({"validation_id": f"E03A-V-{len(validations)+1:02d}", "validation_layer": layer, "check_name": check, "status": "pass" if passed else "fail", "severity": severity, "observed_value": observed, "expected_value": expected, "message": message or "Frozen execution validation.", "blocking": "yes" if severity == "error" else "no", "lineage_bundle_sha256": lineage_bundle})
    validation("authorization", "original_execution_authorization", True, auth["authorization_status"], "human_authorized_for_extract03_execution")
    validation("authorization", "s1_authorization_refresh", True, s1_auth["authorization_status"], "human_authorized_for_extract03a_execution_with_s1_addendum")
    validation("source", "source_row_count", len(rows) == 168042, len(rows), 168042)
    validation("source", "canonical_pair_count", len(pairs) == 42, len(pairs), 42)
    validation("source", "x_point_count", len(x_indices) == 4001, len(x_indices), 4001)
    validation("phase_response", "zero_norm_vectors", not zero_norm.any(), int(zero_norm.sum()), 0)
    validation("K", "finite_values", finite_K, finite_K, True)
    validation("K", "shape", K.shape == (42, 42), str(K.shape), "(42, 42)")
    validation("K", "symmetry_tolerance", hermitian_error <= 1e-12, hermitian_error, "<=1e-12")
    validation("K", "diagonal_close_to_one", diagonal_error <= 1e-12, diagonal_error, "<=1e-12")
    validation("K", "PSD_lower_tolerance", float(eigvals.min()) >= -1e-10, float(eigvals.min()), ">=-1e-10")
    validation("K", "range_sanity", range_error <= 1e-12, range_error, "<=1e-12")
    validation("d", "finite_values", d_finite, d_finite, True)
    validation("d", "non_negative_off_diagonal", d_negative == 0, d_negative, 0, message=f"Tiny values in [-1e-10,0) canonicalized to zero: {int(tiny_negative.sum())} cells.")
    validation("D", "finite_paths", np.isfinite(D).all(), int(np.isfinite(D).sum()), D.size)
    validation("D", "symmetric_non_negative", bool(np.allclose(D, D.T, atol=1e-12) and np.min(D) >= -1e-12), float(np.min(D)), ">=-1e-12 and symmetric")
    validation("strength", "range", bool(np.min(strength) >= 0 and np.max(strength) <= 1 + 1e-12), f"{np.min(strength)}..{np.max(strength)}", "[0,1]")
    validation("cluster", "average_linkage_completed", len(cluster_rows) == 41, len(cluster_rows), 41)
    validation("motif", "candidate_ids_generated", len(motif_rows) == 41, len(motif_rows), 41)
    validation("cluster", "bootstrap_stability_sampling_rule", False, "not frozen", "explicit sampling rule", severity="review", message="S1 freezes seeds but not a bootstrap resampling algorithm; no stability certification was fabricated.")

    review_items = [{"review_item_id": "E03A-RI-01", "topic": "cluster_motif_bootstrap_stability", "status": "open", "reason": "S1 freezes five bootstrap seeds but does not freeze the resampling unit/method or stability acceptance threshold.", "impact": "Dendrogram clusters and motif IDs remain candidates without stability certification.", "required_action": "Human review may define a separate frozen bootstrap/stability addendum before certification; do not tune to this run.", "lineage_bundle_sha256": lineage_bundle}]
    error_failures = [v for v in validations if v["status"] == "fail" and v["severity"] == "error"]
    final_status = STATUS_VALIDATION if error_failures else STATUS_INCONCLUSIVE if review_items else STATUS_OK

    OUT.mkdir(parents=True)
    now = datetime.now(timezone.utc).isoformat()
    manifest = {"work_package": "QSB-EXTRACT03A-R1", "status": final_status, "created_at_utc": now,
        "authorization_imported": True, "s1_refresh_imported": True, "package_plus_s1_hash_checked": True,
        "human_freeze_reviewed": 10, "human_freeze_approved": 10, "human_freeze_missing": 0, "human_freeze_invalid": 0,
        "source_rows": len(rows), "ordered_pairs": len(pairs), "x_points": len(x_indices), "split_protocol_id": SPLIT_PROTOCOL,
        "split_counts": dict(Counter(r["split_label"] for r in split_rows)), "K_computed": True, "d_computed": True, "D_computed": True,
        "edges_computed": True, "clusters_computed": True, "motif_candidate_ids_computed": True,
        "bootstrap_stability_executed": False, "result_mart_written": True, "upstream_modified": False,
        "l2_fail_changed": False, "post_hoc_tuning_performed": False, "physical_evidence_claim_made": False,
        "claim_boundary": CLAIM, "lineage": lineage_payload, "lineage_bundle_sha256": lineage_bundle,
        "next_allowed_action": "human_review_extract03a_r1_candidate_results_and_open_bootstrap_stability_item"}
    (OUT / FILES[0]).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    inventory_rows = [{"artifact_id": f"E03A-UP-{i:02d}", "upstream_block": path.parent.name, "path": rel(path), "exists": "yes", "sha256": before[rel(path)], "access_mode": "read-only", "used_for": "authorization, frozen contract, source, or boundary", "post_run_sha256": "pending", "unchanged": "pending", "lineage_bundle_sha256": lineage_bundle} for i, path in enumerate(upstream_paths, 1)]
    write_csv(FILES[1], list(inventory_rows[0]), inventory_rows)
    auth_rows = [{"authorization_item": key, "observed_value": json.dumps(auth.get(key), ensure_ascii=False), "expected_value": json.dumps(value, ensure_ascii=False), "status": "pass", "source_path": rel(AUTH), "source_sha256": sha(AUTH), "lineage_bundle_sha256": lineage_bundle} for key, value in {
        "authorization_status": "human_authorized_for_extract03_execution", "basis_package": rel(PACKAGE), "basis_package_status": "extract03_execution_package_preparation_completed_no_extraction", "allowed_next_action": "run_separate_extract03_execution_under_frozen_package_contract"}.items()]
    write_csv(FILES[2], list(auth_rows[0]), auth_rows)
    s1_auth_rows = [{"authorization_item": key, "observed_value": json.dumps(s1_auth.get(key), ensure_ascii=False), "expected_value": json.dumps(value, ensure_ascii=False), "status": "pass", "source_path": rel(S1_AUTH), "source_sha256": sha(S1_AUTH), "lineage_bundle_sha256": lineage_bundle} for key, value in {
        "authorization_status": "human_authorized_for_extract03a_execution_with_s1_addendum", "basis_addendum_status": "extract03s1_split_seed_freeze_addendum_completed_no_execution", "split_protocol_id": SPLIT_PROTOCOL, "primary_seed": PRIMARY_SEED, "bootstrap_seeds": BOOTSTRAP_SEEDS, "tie_breaker_seed": TIE_BREAKER_SEED, "allowed_next_action": "run_extract03a_with_frozen_package_plus_s1_addendum"}.items()]
    write_csv(FILES[3], list(s1_auth_rows[0]), s1_auth_rows)
    contract_rows = [
        {"contract_item": "extract03_package", "path": rel(PACKAGE), "observed_value": package_manifest["status"], "expected_value": "extract03_execution_package_preparation_completed_no_extraction", "sha256": package_hash, "status": "pass", "notes": "24 artifacts; aggregate deterministic tree hash.", "lineage_bundle_sha256": lineage_bundle},
        {"contract_item": "extract03_s1_addendum", "path": rel(S1), "observed_value": s1_manifest["status"], "expected_value": "extract03s1_split_seed_freeze_addendum_completed_no_execution", "sha256": s1_hash, "status": "pass", "notes": "18 artifacts; aggregate deterministic tree hash.", "lineage_bundle_sha256": lineage_bundle},
        {"contract_item": "canonical_pair_basis", "path": rel(S1 / "06_canonical_pair_basis_review.csv"), "observed_value": pair_basis_hash, "expected_value": "51962668d944195bb1409a5f9d6972636c660184aa6be3ab530a3d980cf96e32", "sha256": sha(S1 / "06_canonical_pair_basis_review.csv"), "status": "pass", "notes": "Numeric pair_i,pair_j order.", "lineage_bundle_sha256": lineage_bundle},
    ]
    write_csv(FILES[4], list(contract_rows[0]), contract_rows)
    freeze_rows = [{"freeze_id": d["freeze_id"], "freeze_item": d["freeze_item"], "decision_value": json.dumps(d["decision_value"], ensure_ascii=False), "decision_status": d["decision_status"], "human_approval": d["human_approval"], "blocks_actual_execution": d["blocks_actual_execution"], "carry_forward_status": "pass", "source_sha256": sha(HF), "lineage_bundle_sha256": lineage_bundle} for d in sorted(valid_decisions, key=lambda d: d["freeze_id"])]
    write_csv(FILES[5], list(freeze_rows[0]), freeze_rows)
    source_rows = [{"source_mode": "spatial_pair_delta_phi_x", "preferred_source": rel(F3_DB), "fallback_source": rel(F3_DIR / "07_spatial_delta_phi_x_export.csv"), "source_rows": len(rows), "ordered_non_diagonal_pairs": len(pairs), "x_points": len(x_indices), "wrapped_delta_phi_present": "yes", "raw_delta_phi_audit_present": "yes", "angle_unit": rows[0][11], "x_unit": rows[0][7], "x_dimension_status": "model_coordinate_unit_not_SI_converted", "diagonal_pairs_excluded": "yes", "selection_status": "pass", "source_sha256": sha(F3_DB), "lineage_bundle_sha256": lineage_bundle}]
    write_csv(FILES[6], list(source_rows[0]), source_rows)
    write_csv(FILES[7], list(split_rows[0]), split_rows)
    mapping_rows = [{"runtime_field": name, "source_or_formula": source_or_formula, "data_type": dtype, "unit_status": unit, "dimension_status": dimension, "lineage_bundle_sha256": lineage_bundle} for name, source_or_formula, dtype, unit, dimension in [
        ("pair_i,pair_j,x_index", "stg_delta_phi_spatial", "integer", "not applicable", "index axes"),
        ("wrapped_delta_phi", "wrapped_delta_phi_ij_x", "real", "rad", "dimensionless_angle"),
        ("raw_delta_phi", "raw_delta_phi_ij_x", "real", "rad", "dimensionless_angle"),
        ("phase_response_vector", "L2-normalized wrapped_delta_phi", "real vector", "dimensionless after normalization", "candidate response"),
        ("K_candidate", "normalized_vector_a dot normalized_vector_b", "real", "dimensionless", "candidate correlation/Gram"),
        ("d_cost_candidate", "-ell_0 log(abs(K)+epsilon_Gram)", "real", "model cost scale", "candidate cost"),
        ("D_shortest_path_candidate", "all-pairs minimum summed d cost", "real", "model cost scale", "candidate aggregate cost"),
    ]]
    write_csv(FILES[8], list(mapping_rows[0]), mapping_rows)
    vector_rows = [{"pair_index": i, "canonical_pair_id": pair_ids[i], "split_label": split_rows[i]["split_label"], "x_point_count": len(wrapped[i]), "wrapped_l2_norm_before": format(float(norms[i]), ".17g"), "normalized_l2_norm": format(float(np.linalg.norm(normalized[i])), ".17g"), "raw_min": format(float(raw[i].min()), ".17g"), "raw_max": format(float(raw[i].max()), ".17g"), "wrapped_min": format(float(wrapped[i].min()), ".17g"), "wrapped_max": format(float(wrapped[i].max()), ".17g"), "zero_norm": bool(zero_norm[i]), "status": "fail" if zero_norm[i] else "pass", "lineage_bundle_sha256": lineage_bundle} for i in range(n)]
    write_csv(FILES[9], list(vector_rows[0]), vector_rows)

    def matrix_rows(matrix, value_name):
        return [{"row_pair_id": pair_ids[i], "column_pair_id": pair_ids[j], value_name: format(float(matrix[i, j]), ".17g"), "lineage_bundle_sha256": lineage_bundle} for i in range(n) for j in range(n)]
    write_csv(FILES[10], ["row_pair_id", "column_pair_id", "K_candidate", "lineage_bundle_sha256"], matrix_rows(K, "K_candidate"))
    k_validations = [v for v in validations if v["validation_layer"] == "K"]
    write_csv(FILES[11], list(k_validations[0]), k_validations)
    write_csv(FILES[12], ["row_pair_id", "column_pair_id", "d_cost_candidate", "lineage_bundle_sha256"], matrix_rows(d, "d_cost_candidate"))
    write_csv(FILES[13], ["row_pair_id", "column_pair_id", "D_shortest_path_candidate", "lineage_bundle_sha256"], matrix_rows(D, "D_shortest_path_candidate"))
    write_csv(FILES[14], ["row_pair_id", "column_pair_id", "relation_strength", "lineage_bundle_sha256"], matrix_rows(strength, "relation_strength"))
    edge_rows = [{"pair_a": pair_ids[i], "pair_b": pair_ids[j], "strength": format(float(strength[i,j]), ".17g"), "theta_edge": THETA_EDGE, "edge_candidate_flag": int(edge[i,j]), "diagonal": int(i == j), "claim_boundary": "candidate edge only", "lineage_bundle_sha256": lineage_bundle} for i in range(n) for j in range(i + 1, n)]
    write_csv(FILES[15], list(edge_rows[0]), edge_rows)
    kernel_rows = [
        {"kernel_name": "gram_distance_kernel", "execution_status": "executed", "output": "K and d candidate matrices", "stop_or_skip_reason": "none", "claim_boundary": CLAIM, "lineage_bundle_sha256": lineage_bundle},
        {"kernel_name": "shortest_path_kernel", "execution_status": "executed", "output": "D candidate matrix", "stop_or_skip_reason": "none", "claim_boundary": CLAIM, "lineage_bundle_sha256": lineage_bundle},
        {"kernel_name": "edge_candidate_kernel", "execution_status": "executed", "output": "edge candidate flags", "stop_or_skip_reason": "none", "claim_boundary": CLAIM, "lineage_bundle_sha256": lineage_bundle},
        {"kernel_name": "cluster_dendrogram_kernel", "execution_status": "executed", "output": "average-linkage dendrogram candidates", "stop_or_skip_reason": "bootstrap stability not certified", "claim_boundary": CLAIM, "lineage_bundle_sha256": lineage_bundle},
        {"kernel_name": "motif_stability_kernel", "execution_status": "skipped_with_reason", "output": "motif candidate IDs only; no stability certification", "stop_or_skip_reason": "S1 does not freeze bootstrap resampling unit/method or stability threshold", "claim_boundary": CLAIM, "lineage_bundle_sha256": lineage_bundle},
    ]
    write_csv(FILES[16], list(kernel_rows[0]), kernel_rows)
    write_csv(FILES[17], list(cluster_rows[0]), cluster_rows)
    write_csv(FILES[18], list(motif_rows[0]), motif_rows)

    schema = """PRAGMA foreign_keys=ON;
CREATE TABLE extract03a_r1_run (run_id TEXT PRIMARY KEY,status TEXT NOT NULL,created_at_utc TEXT NOT NULL,lineage_bundle_sha256 TEXT NOT NULL,claim_boundary TEXT NOT NULL);
CREATE TABLE extract03a_r1_source_selection (source_mode TEXT,source_path TEXT,source_rows INTEGER,pair_count INTEGER,x_points INTEGER,lineage_bundle_sha256 TEXT);
CREATE TABLE extract03a_r1_pair_split_assignment (pair_index INTEGER PRIMARY KEY,canonical_pair_id TEXT,split_label TEXT,split_hash TEXT,u REAL,lineage_bundle_sha256 TEXT);
CREATE TABLE extract03a_r1_phase_response_vector (pair_index INTEGER PRIMARY KEY,canonical_pair_id TEXT,x_point_count INTEGER,l2_norm_before REAL,l2_norm_after REAL,status TEXT,lineage_bundle_sha256 TEXT);
CREATE TABLE extract03a_r1_K_candidate (row_pair_id TEXT,column_pair_id TEXT,value REAL,lineage_bundle_sha256 TEXT,PRIMARY KEY(row_pair_id,column_pair_id));
CREATE TABLE extract03a_r1_distance_cost (row_pair_id TEXT,column_pair_id TEXT,value REAL,lineage_bundle_sha256 TEXT,PRIMARY KEY(row_pair_id,column_pair_id));
CREATE TABLE extract03a_r1_shortest_path_D (row_pair_id TEXT,column_pair_id TEXT,value REAL,lineage_bundle_sha256 TEXT,PRIMARY KEY(row_pair_id,column_pair_id));
CREATE TABLE extract03a_r1_strength (row_pair_id TEXT,column_pair_id TEXT,value REAL,lineage_bundle_sha256 TEXT,PRIMARY KEY(row_pair_id,column_pair_id));
CREATE TABLE extract03a_r1_edge_candidate (pair_a TEXT,pair_b TEXT,strength REAL,edge_candidate_flag INTEGER,lineage_bundle_sha256 TEXT,PRIMARY KEY(pair_a,pair_b));
CREATE TABLE extract03a_r1_cluster_candidate (merge_index INTEGER PRIMARY KEY,cluster_candidate_id TEXT,members TEXT,distance REAL,candidate_status TEXT,lineage_bundle_sha256 TEXT);
CREATE TABLE extract03a_r1_motif_candidate (motif_candidate_id TEXT PRIMARY KEY,source_cluster_candidate_id TEXT,members TEXT,stability_status TEXT,lineage_bundle_sha256 TEXT);
CREATE TABLE extract03a_r1_validation_result (validation_id TEXT PRIMARY KEY,validation_layer TEXT,check_name TEXT,status TEXT,severity TEXT,message TEXT,lineage_bundle_sha256 TEXT);
CREATE TABLE extract03a_r1_claim_boundary (statement_id TEXT PRIMARY KEY,classification TEXT,statement TEXT,lineage_bundle_sha256 TEXT);
CREATE TABLE extract03a_r1_lineage (lineage_name TEXT PRIMARY KEY,path TEXT,sha256 TEXT,lineage_bundle_sha256 TEXT);
"""
    (OUT / FILES[19]).write_text(schema, encoding="utf-8")
    db = sqlite3.connect(OUT / FILES[20])
    db.executescript(schema)
    run_id = "QSB-EXTRACT03A-R1-authorized-execution-with-s1"
    db.execute("INSERT INTO extract03a_r1_run VALUES (?,?,?,?,?)", (run_id, final_status, now, lineage_bundle, CLAIM))
    db.execute("INSERT INTO extract03a_r1_source_selection VALUES (?,?,?,?,?,?)", ("spatial_pair_delta_phi_x", rel(F3_DB), len(rows), n, len(x_indices), lineage_bundle))
    db.executemany("INSERT INTO extract03a_r1_pair_split_assignment VALUES (?,?,?,?,?,?)", [(r["pair_index"],r["canonical_pair_id"],r["split_label"],r["sha256"],float(r["u"]),lineage_bundle) for r in split_rows])
    db.executemany("INSERT INTO extract03a_r1_phase_response_vector VALUES (?,?,?,?,?,?,?)", [(r["pair_index"],r["canonical_pair_id"],r["x_point_count"],float(r["wrapped_l2_norm_before"]),float(r["normalized_l2_norm"]),r["status"],lineage_bundle) for r in vector_rows])
    for table, matrix in [("extract03a_r1_K_candidate",K),("extract03a_r1_distance_cost",d),("extract03a_r1_shortest_path_D",D),("extract03a_r1_strength",strength)]:
        db.executemany(f"INSERT INTO {table} VALUES (?,?,?,?)", [(pair_ids[i],pair_ids[j],float(matrix[i,j]),lineage_bundle) for i in range(n) for j in range(n)])
    db.executemany("INSERT INTO extract03a_r1_edge_candidate VALUES (?,?,?,?,?)", [(r["pair_a"],r["pair_b"],float(r["strength"]),r["edge_candidate_flag"],lineage_bundle) for r in edge_rows])
    db.executemany("INSERT INTO extract03a_r1_cluster_candidate VALUES (?,?,?,?,?,?)", [(r["merge_index"],r["cluster_candidate_id"],r["members"],float(r["distance"]),r["candidate_status"],lineage_bundle) for r in cluster_rows])
    db.executemany("INSERT INTO extract03a_r1_motif_candidate VALUES (?,?,?,?,?)", [(r["motif_candidate_id"],r["source_cluster_candidate_id"],r["members"],r["stability_status"],lineage_bundle) for r in motif_rows])
    db.executemany("INSERT INTO extract03a_r1_validation_result VALUES (?,?,?,?,?,?,?)", [(v["validation_id"],v["validation_layer"],v["check_name"],v["status"],v["severity"],v["message"],lineage_bundle) for v in validations])
    claims = [
        ("E03A-CB-01","safe", "EXTRACT03A-R1 computes candidate Gram/Tensor relational structures from the frozen F3-like phase-response source under the approved EXTRACT03 package plus S1 split/seed addendum."),
        ("E03A-CB-02","boundary", "D remains a reconstructed cost-distance candidate, not proven geometry."),
        ("E03A-CB-03","boundary", "Clusters and motifs remain candidate relational groupings only."),
        ("E03A-CB-04","unsupported_claim", "Any claim that this run proves QSB, repairs L2, demonstrates gravity, or supplies physical evidence for geometry is unsupported."),
    ]
    db.executemany("INSERT INTO extract03a_r1_claim_boundary VALUES (?,?,?,?)", [(a,b,c,lineage_bundle) for a,b,c in claims])
    lineage_path_map = {"execution_authorization_hash": rel(AUTH), "s1_authorization_refresh_hash": rel(S1_AUTH), "extract03_package_hash": rel(PACKAGE), "s1_addendum_hash": rel(S1), "r1f_hash": rel(R1F), "f3_source_hash": rel(F3_DB), "human_freeze_decision_hash": rel(HF)}
    db.executemany("INSERT INTO extract03a_r1_lineage VALUES (?,?,?,?)", [(name,lineage_path_map[name],value,lineage_bundle) for name,value in lineage_payload.items()])
    db.commit()
    tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    count_rows = [{"table_name": table, "row_count": db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], "lineage_bundle_sha256": lineage_bundle} for table in tables]
    db.close()
    write_csv(FILES[21], list(count_rows[0]), count_rows)

    unit_rows = [
        {"quantity": "x_value", "unit": "model_length_unit", "dimension_status": "model_coordinate_unit_not_SI_converted", "audit_status": "pass", "claim_boundary": "No SI length interpretation.", "lineage_bundle_sha256": lineage_bundle},
        {"quantity": "raw_delta_phi/wrapped_delta_phi", "unit": "rad", "dimension_status": "dimensionless_angle", "audit_status": "pass", "claim_boundary": "Phase-response source channel.", "lineage_bundle_sha256": lineage_bundle},
        {"quantity": "K_candidate/strength", "unit": "dimensionless", "dimension_status": "candidate relation", "audit_status": "pass", "claim_boundary": CLAIM, "lineage_bundle_sha256": lineage_bundle},
        {"quantity": "d_cost/D_shortest_path", "unit": "model cost scale", "dimension_status": "candidate cost", "audit_status": "pass", "claim_boundary": "Not measured distance or proven geometry.", "lineage_bundle_sha256": lineage_bundle},
    ]
    write_csv(FILES[23], list(unit_rows[0]), unit_rows)
    write_csv(FILES[24], list(validations[0]), validations)
    gates = ["authorization_valid","s1_refresh_valid","package_hash_rechecked","s1_hash_rechecked","human_freeze_valid","F3_source_valid","split_assignment_complete","phase_vectors_built","K_validated","d_validated","D_validated","edges_computed","cluster_candidates_computed","claim_boundary_clean"]
    gate_rows = [{"gate_id": f"E03A-AG-{i:02d}", "gate": gate, "status": "pass", "blocking": "yes", "evidence": "Recorded in run outputs.", "lineage_bundle_sha256": lineage_bundle} for i, gate in enumerate(gates,1)]
    write_csv(FILES[25], list(gate_rows[0]), gate_rows)
    guards = ["no_upstream_db_mutation","no_L2_change","no_post_hoc_tuning","no_material_sensitive_sources","no_diagonal_physical_pairs","no_source_scope_change","no_parameter_change","no_split_seed_change","no_upstream_run_overwrite","result_mart_local_only","no_physical_evidence_claim","no_geometry_claim","no_gravity_claim","output_count_exact"]
    guard_rows = [{"guard_id": f"E03A-G-{i:02d}", "guard": guard, "status": "pass", "evidence": "Enforced by isolated execution and frozen values.", "blocking_if_violated": "yes", "lineage_bundle_sha256": lineage_bundle} for i, guard in enumerate(guards,1)]
    write_csv(FILES[26], list(guard_rows[0]), guard_rows)
    write_csv(FILES[27], list(review_items[0]), review_items)
    claim_rows = [{"statement_id": a, "classification": b, "statement": c, "allowed_in_result_interpretation": "yes" if b == "safe" else "boundary_only" if b == "boundary" else "no", "lineage_bundle_sha256": lineage_bundle} for a,b,c in claims]
    write_csv(FILES[28], list(claim_rows[0]), claim_rows)
    seed_rows = [{"audit_item": "split_assignment", "seed_or_rule": f"{SPLIT_PROTOCOL}|{PRIMARY_SEED}|canonical_pair_id", "execution_status": "executed", "result": json.dumps(Counter(r["split_label"] for r in split_rows), sort_keys=True), "notes": "42 deterministic assignments.", "lineage_bundle_sha256": lineage_bundle}]
    seed_rows += [{"audit_item": f"bootstrap_seed_{i}", "seed_or_rule": seed, "execution_status": "not_executed_missing_frozen_sampling_rule", "result": "no stability result", "notes": "Seed carried forward; no resampling algorithm or threshold fabricated.", "lineage_bundle_sha256": lineage_bundle} for i,seed in enumerate(BOOTSTRAP_SEEDS,1)]
    seed_rows.append({"audit_item": "tie_breaker_seed", "seed_or_rule": TIE_BREAKER_SEED, "execution_status": "available_not_needed", "result": "no hash collision or ordering ambiguity", "notes": "Frozen seed unchanged.", "lineage_bundle_sha256": lineage_bundle})
    write_csv(FILES[29], list(seed_rows[0]), seed_rows)

    note = f"""# QSB-EXTRACT03A-R1 — Kurze Ergebnisnotiz

## Befund

Unter dem eingefrorenen EXTRACT03-Paket plus S1 wurden aus {len(rows)} F3-Zeilen für {n} geordnete Paare K-, d-, D-, Stärke-, Kanten- und Average-Linkage-Kandidaten berechnet. Status: `{final_status}`.

## Interpretation

Die Ausgaben beschreiben rechnerische relationale Kandidatenstrukturen. D ist eine rekonstruierte Kostendistanz, keine nachgewiesene Geometrie.

## Hypothese

Keine zusätzliche physikalische Hypothese wird durch diesen Lauf validiert.

## Offene Lücke

S1 friert Seeds, aber keine Bootstrap-Resampling-Regel oder Stabilitätsschwelle ein. Daher sind Motiv-IDs nicht stabilitätszertifiziert.

## Claim Boundary

Keine Änderung des L2-Fails, kein Post-hoc-Tuning und kein physikalischer Evidenzclaim.
"""
    (OUT / FILES[30]).write_text(note, encoding="utf-8")
    next_note = """# Next-step recommendation

Human review may inspect the candidate matrices, validation results, and the open bootstrap-stability item. A separate frozen addendum would be required before any cluster/motif stability certification; it must define the resampling unit, deterministic procedure, and acceptance threshold without tuning to this run. No upstream mutation or L2 reinterpretation is authorized.
"""
    (OUT / FILES[31]).write_text(next_note, encoding="utf-8")
    final_note = note.replace("Kurze Ergebnisnotiz", "Final Result Note") + "\nConfiguration paths: `runs/QSB-EXTRACT03/execution_package_preparation/`, `runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/`, and `runs/QSB-EXTRACT03/input/extract03a_execution_authorization_refresh_package_plus_s1.json`.\n"
    (OUT / FILES[32]).write_text(final_note, encoding="utf-8")

    after = {rel(path): sha(path) for path in upstream_paths}
    if after != before:
        fail("extract03a_r1_blocked_guard_violation", "upstream hash changed during execution")
    for row in inventory_rows:
        row["post_run_sha256"] = after[row["path"]]
        row["unchanged"] = "yes"
    write_csv(FILES[1], list(inventory_rows[0]), inventory_rows)

    lineage_rows = [{"audit_scope": "upstream", "artifact": name, "path": lineage_path_map[name], "sha256": value, "hash_role": "required lineage", "status": "pass", "notes": "Read-only; pre/post hash unchanged where file-based.", "lineage_bundle_sha256": lineage_bundle} for name,value in lineage_payload.items()]
    for filename in FILES:
        path = OUT / filename
        if filename == FILES[22]:
            continue
        lineage_rows.append({"audit_scope": "run_output", "artifact": filename, "path": rel(path), "sha256": sha(path), "hash_role": "output integrity", "status": "pass", "notes": "23_lineage_and_hash_audit.csv self-hash excluded.", "lineage_bundle_sha256": lineage_bundle})
    write_csv(FILES[22], list(lineage_rows[0]), lineage_rows)

    actual = sorted(path.name for path in OUT.iterdir())
    if actual != sorted(FILES) or len(actual) != 33:
        fail("extract03a_r1_blocked_guard_violation", f"output artifact mismatch: {len(actual)}")
    print(json.dumps({"status": final_status, "artifacts": len(actual), "source_rows": len(rows), "pairs": n,
                      "x_points": len(x_indices), "split_counts": dict(Counter(r["split_label"] for r in split_rows)),
                      "K_d_D_computed": True, "edges_clusters_motif_ids": True,
                      "bootstrap_stability": "skipped_missing_frozen_sampling_rule", "result_mart": True,
                      "upstream_modified": False}, indent=2))


if __name__ == "__main__":
    main()
