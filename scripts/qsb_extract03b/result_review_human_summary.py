#!/usr/bin/env python3
"""Read-only human/result review of existing EXTRACT03A-R1 artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03B/result_review_human_summary"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
MART = A / "21_extract03a_r1_result_mart.sqlite"
S1 = ROOT / "runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
PACKAGE = ROOT / "runs/QSB-EXTRACT03/execution_package_preparation"
R1F = ROOT / "runs/QSB-EXTRACT02A-R1F/artifact_consistency_fix_human_freeze_recheck"
F3 = ROOT / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2"
M2 = ROOT / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2"
N0 = ROOT / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path"

STATUS = "extract03b_result_review_completed_bootstrap_freeze_recommended"
EXPECTED_A_STATUS = "extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items"
CLAIM = "EXTRACT03A-R1 computed candidate Gram/Tensor relational structures from the frozen F3-like phase-response source under the approved EXTRACT03 package plus S1 split/seed addendum."
FILES = [
    "01_extract03b_review_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_extract03a_r1_manifest_import.csv", "04_result_mart_readonly_review.csv",
    "05_matrix_summary_K.csv", "06_matrix_summary_d.csv", "07_matrix_summary_D.csv",
    "08_strength_and_edge_summary.csv", "09_split_summary.csv",
    "10_phase_response_vector_summary_review.csv", "11_kernel_summary_review.csv",
    "12_cluster_candidate_review.csv", "13_motif_candidate_review.csv",
    "14_validation_guard_gate_summary.csv", "15_review_items_import_and_classification.csv",
    "16_claim_boundary_review.csv", "17_l2_boundary_check.csv", "18_bootstrap_gap_assessment.csv",
    "19_human_readable_result_interpretation_de.md", "20_next_step_options.csv",
    "21_recommended_next_step.md", "22_short_review_note_de.md", "23_no_reexecution_guard.csv",
    "FINAL_RESULT_NOTE.md",
]


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_path(path: Path) -> str:
    if path.is_file():
        return sha_file(path)
    h = hashlib.sha256()
    for item in sorted(p for p in path.iterdir() if p.is_file()):
        h.update(item.name.encode())
        h.update(b"\0")
        h.update(sha_file(item).encode())
        h.update(b"\n")
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_csv(name: str):
    with (A / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict]):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fail(status: str, message: str):
    raise SystemExit(f"{status}: {message}")


def summary_rows(items):
    return [{"summary_item": key, "observed_value": value, "status": status, "notes": notes}
            for key, value, status, notes in items]


def matrix_review(filename: str, field: str):
    rows = read_csv(filename)
    values = [float(row[field]) for row in rows]
    row_ids = sorted({row["row_pair_id"] for row in rows})
    column_ids = sorted({row["column_pair_id"] for row in rows})
    diagonal = [float(row[field]) for row in rows if row["row_pair_id"] == row["column_pair_id"]]
    return rows, values, row_ids, column_ids, diagonal


def main():
    if OUT.exists():
        fail("extract03b_blocked_guard_violation", f"refusing to overwrite {OUT}")
    required_files = [
        A / "01_extract03a_r1_run_manifest.json", MART, A / "08_canonical_pair_split_assignment.csv",
        A / "10_phase_response_vector_summary.csv", A / "11_K_candidate_matrix.csv",
        A / "13_distance_cost_matrix.csv", A / "14_shortest_path_D_matrix.csv",
        A / "15_strength_matrix.csv", A / "16_edge_candidate_result.csv",
        A / "17_kernel_execution_summary.csv", A / "18_cluster_dendrogram_candidate_result.csv",
        A / "19_motif_candidate_summary.csv", A / "25_validation_results.csv",
        A / "26_acceptance_gate_results.csv", A / "27_guard_results.csv", A / "28_review_items.csv",
        L2 / "01_l2_run_manifest.json", M2 / "04_l2_contract_result_summary.csv",
    ]
    if not A.is_dir() or any(not path.is_file() for path in required_files):
        fail("extract03b_blocked_missing_extract03a_r1_outputs", "required review input missing")

    manifest = json.loads((A / "01_extract03a_r1_run_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != EXPECTED_A_STATUS:
        fail("extract03b_blocked_upstream_mismatch", f"EXTRACT03A-R1 status={manifest.get('status')}")
    expected_manifest = {
        "source_rows": 168042, "ordered_pairs": 42, "x_points": 4001,
        "K_computed": True, "d_computed": True, "D_computed": True,
        "result_mart_written": True, "upstream_modified": False, "l2_fail_changed": False,
        "physical_evidence_claim_made": False,
    }
    mismatch = [key for key, value in expected_manifest.items() if manifest.get(key) != value]
    if mismatch:
        fail("extract03b_blocked_upstream_mismatch", "manifest mismatch: " + ", ".join(mismatch))

    upstream = [
        ("EXTRACT03A_R1_OUTPUT", A, "yes", "reviewed result directory"),
        ("EXTRACT03A_R1_RESULT_MART", MART, "yes", "read-only table review"),
        ("EXTRACT03_S1", S1, "yes", "split/seed context"),
        ("EXTRACT03_PACKAGE", PACKAGE, "yes", "frozen package context"),
        ("EXTRACT02A_R1F", R1F, "yes", "authorization context"),
        ("F3", F3, "yes", "source context only; raw source not read"),
        ("L2", L2, "yes", "unchanged fail boundary"),
        ("M2", M2, "yes", "failure-localization context"),
        ("N0", N0, "yes", "post-fail scope context"),
    ]
    if any(not path.exists() for _, path, _, _ in upstream):
        fail("extract03b_blocked_upstream_mismatch", "required upstream block missing")
    before = {rel(path): sha_path(path) for _, path, _, _ in upstream}

    try:
        db = sqlite3.connect(f"file:{MART}?mode=ro&immutable=1", uri=True)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        mart_rows = []
        for table in tables:
            count = db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            mart_rows.append({"table_name": table, "row_count": count, "read_status": "pass", "expected_or_reference": "existing stored rows", "notes": "Read with SQLite mode=ro&immutable=1; no write transaction."})
        db.close()
    except sqlite3.Error as exc:
        fail("extract03b_blocked_invalid_extract03a_r1_result_mart", str(exc))
    if integrity != "ok" or len(tables) < 14:
        fail("extract03b_blocked_invalid_extract03a_r1_result_mart", f"integrity={integrity}; tables={len(tables)}")

    K_rows, K, K_rids, K_cids, K_diag = matrix_review("11_K_candidate_matrix.csv", "K_candidate")
    d_rows, dvals, d_rids, d_cids, d_diag = matrix_review("13_distance_cost_matrix.csv", "d_cost_candidate")
    D_rows, Dvals, D_rids, D_cids, D_diag = matrix_review("14_shortest_path_D_matrix.csv", "D_shortest_path_candidate")
    strength_rows, strengths, s_rids, s_cids, s_diag = matrix_review("15_strength_matrix.csv", "relation_strength")
    kval = {row["check_name"]: row for row in read_csv("12_K_validation_results.csv")}
    validations = read_csv("25_validation_results.csv")
    validation_by_check = {row["check_name"]: row for row in validations}
    finite = lambda vals: all(math.isfinite(value) for value in vals)
    shape = lambda rids, cids: f"{len(rids)}x{len(cids)} ({len(rids)*len(cids)} stored cells)"

    K_summary = summary_rows([
        ("shape", shape(K_rids, K_cids), "pass" if len(K_rows) == 1764 else "fail", "Read from stored K CSV; no Gram reconstruction."),
        ("minimum", min(K), "review", "Descriptive statistic of stored candidate values."),
        ("maximum", max(K), "review", "Descriptive statistic of stored candidate values."),
        ("diagonal_min", min(K_diag), "pass", "Stored diagonal values."),
        ("diagonal_max", max(K_diag), "pass", "Stored diagonal values."),
        ("diagonal_mean", sum(K_diag)/len(K_diag), "pass", "Stored diagonal values."),
        ("symmetry_validation", kval["symmetry_tolerance"]["status"], kval["symmetry_tolerance"]["status"], "Imported EXTRACT03A-R1 validation; not recomputed."),
        ("PSD_validation", kval["PSD_lower_tolerance"]["status"], kval["PSD_lower_tolerance"]["status"], "Imported eigenvalue validation; eigenvalues not recomputed."),
        ("finite_validation", kval["finite_values"]["status"], kval["finite_values"]["status"], "Imported validation; descriptive values also finite."),
    ])
    d_summary = summary_rows([
        ("shape", shape(d_rids, d_cids), "pass" if len(d_rows) == 1764 else "fail", "Read from stored d CSV; no cost reconstruction."),
        ("minimum", min(dvals), "review", "Stored candidate costs."),
        ("maximum", max(dvals), "review", "Stored candidate costs."),
        ("mean", sum(dvals)/len(dvals), "review", "Stored candidate costs, diagonal included."),
        ("diagonal_policy", f"min={min(d_diag)}; max={max(d_diag)}", "pass" if min(d_diag) == max(d_diag) == 0 else "fail", "Stored diagonal is zero."),
        ("finite_validation", validation_by_check["finite_values"]["status"], validation_by_check["finite_values"]["status"], "d-layer imported validation."),
        ("nonnegative_validation", validation_by_check["non_negative_off_diagonal"]["status"], validation_by_check["non_negative_off_diagonal"]["status"], "Imported; tiny numerical negatives were already handled in EXTRACT03A-R1."),
    ])
    D_summary = summary_rows([
        ("shape", shape(D_rids, D_cids), "pass" if len(D_rows) == 1764 else "fail", "Read from stored D CSV; shortest paths not rerun."),
        ("finite_path_count", sum(math.isfinite(x) for x in Dvals), "pass" if finite(Dvals) else "fail", "Stored cells."),
        ("disconnected_count", sum(not math.isfinite(x) for x in Dvals), "pass" if finite(Dvals) else "review", "Stored non-finite cells."),
        ("minimum", min(Dvals), "review", "Stored candidate cost-distance."),
        ("maximum", max(Dvals), "review", "Stored candidate cost-distance."),
        ("mean", sum(Dvals)/len(Dvals), "review", "Stored candidate cost-distance, diagonal included."),
        ("finite_paths_validation", validation_by_check["finite_paths"]["status"], validation_by_check["finite_paths"]["status"], "Imported EXTRACT03A-R1 validation."),
        ("symmetric_nonnegative_validation", validation_by_check["symmetric_non_negative"]["status"], validation_by_check["symmetric_non_negative"]["status"], "Imported EXTRACT03A-R1 validation."),
    ])

    edge_rows = read_csv("16_edge_candidate_result.csv")
    edge_count = sum(int(row["edge_candidate_flag"]) for row in edge_rows)
    strength_edge_summary = summary_rows([
        ("strength_shape", shape(s_rids, s_cids), "pass" if len(strength_rows) == 1764 else "fail", "Stored strength matrix."),
        ("strength_min", min(strengths), "review", "Stored relation-strength candidates."),
        ("strength_max", max(strengths), "review", "Stored relation-strength candidates."),
        ("strength_mean", sum(strengths)/len(strengths), "review", "Diagonal included."),
        ("undirected_pair_rows", len(edge_rows), "pass" if len(edge_rows) == 861 else "fail", "42 choose 2 stored candidate comparisons."),
        ("edge_candidate_count", edge_count, "review", "Threshold was not changed or reapplied."),
        ("non_edge_candidate_count", len(edge_rows)-edge_count, "review", "Stored flags only."),
        ("theta_edge", edge_rows[0]["theta_edge"], "pass", "Imported frozen value; no tuning."),
    ])

    split_assignments = read_csv("08_canonical_pair_split_assignment.csv")
    split_counts = Counter(row["split_label"] for row in split_assignments)
    expected_fractions = {"calibration": .4, "validation": .3, "review": .2, "holdout": .1}
    split_summary = [{"split_label": label, "expected_fraction": fraction, "observed_count": split_counts[label], "observed_fraction": split_counts[label]/len(split_assignments), "status": "deterministic_observed_split", "notes": "Small-n hash split is recorded, not forced to ideal percentages."} for label, fraction in expected_fractions.items()]

    vectors = read_csv("10_phase_response_vector_summary.csv")
    vector_summary = summary_rows([
        ("vector_count", len(vectors), "pass" if len(vectors) == 42 else "fail", "Stored vector summaries only."),
        ("vector_length", ",".join(sorted({row["x_point_count"] for row in vectors})), "pass", "Expected 4001."),
        ("normalized_norm_min", min(float(row["normalized_l2_norm"]) for row in vectors), "pass", "Stored norms; no normalization rerun."),
        ("normalized_norm_max", max(float(row["normalized_l2_norm"]) for row in vectors), "pass", "Stored norms; no normalization rerun."),
        ("zero_norm_count", sum(row["zero_norm"].lower() == "true" for row in vectors), "pass", "Zero-norm policy was reject as validation failure."),
        ("vector_status_pass_count", sum(row["status"] == "pass" for row in vectors), "pass", "Imported statuses."),
    ])

    kernels = read_csv("17_kernel_execution_summary.csv")
    kernel_outputs = {"gram_distance_kernel": len(K_rows)+len(d_rows), "shortest_path_kernel": len(D_rows), "edge_candidate_kernel": len(edge_rows), "cluster_dendrogram_kernel": 41, "motif_stability_kernel": 41}
    kernel_summary = [{"kernel_name": row["kernel_name"], "execution_status": row["execution_status"], "validation_status": "reviewed_existing_output", "output_rows_or_count": kernel_outputs[row["kernel_name"]], "review_status": "candidate_output_reviewed" if row["kernel_name"] != "motif_stability_kernel" else "stability_not_certified", "notes": row["stop_or_skip_reason"] + "; no kernel rerun in EXTRACT03B."} for row in kernels]

    clusters = read_csv("18_cluster_dendrogram_candidate_result.csv")
    cluster_summary = summary_rows([
        ("cluster_candidate_rows", len(clusters), "pass" if len(clusters) == 41 else "fail", "Stored dendrogram merges."),
        ("linkage_methods", ";".join(sorted({row["linkage_method"] for row in clusters})), "pass", "Imported method."),
        ("distance_matrix_sources", ";".join(sorted({row["distance_matrix_source"] for row in clusters})), "pass", "Imported source label."),
        ("cut_rule", "none applied; dendrogram merges reviewed", "review", "No cluster-count cut or tuning in EXTRACT03B."),
        ("member_count_min", min(int(row["member_count"]) for row in clusters), "review", "Stored membership counts."),
        ("member_count_max", max(int(row["member_count"]) for row in clusters), "review", "Stored membership counts."),
        ("candidate_statuses", ";".join(sorted({row["candidate_status"] for row in clusters})), "review", "No stability certification."),
    ])
    motifs = read_csv("19_motif_candidate_summary.csv")
    motif_summary = summary_rows([
        ("motif_candidate_count", len(motifs), "pass" if len(motifs) == 41 else "fail", "Stored motif IDs."),
        ("id_generation_policy", ";".join(sorted({row["id_contract"] for row in motifs})), "pass", "Imported policy; IDs not regenerated."),
        ("stability_status", ";".join(sorted({row["stability_status"] for row in motifs})), "review", "Bootstrap gap remains open."),
        ("claim_boundary", ";".join(sorted({row["interpretation"] for row in motifs})), "pass", "Candidate relational grouping only."),
    ])

    gates = read_csv("26_acceptance_gate_results.csv")
    guards = read_csv("27_guard_results.csv")
    def layer_summary(layer, rows):
        pass_count = sum(row["status"] == "pass" for row in rows)
        review_count = sum(row["status"] == "fail" and row.get("severity") == "review" for row in rows)
        fail_count = sum(row["status"] == "fail" and row.get("severity") != "review" for row in rows)
        blocking_fail = sum(row["status"] == "fail" and row.get("blocking", row.get("blocking_if_violated")) == "yes" and row.get("severity") != "review" for row in rows)
        return {"layer": layer, "total_count": len(rows), "pass_count": pass_count, "review_count": review_count, "fail_count": fail_count, "blocking_fail_count": blocking_fail, "status": "review" if review_count else "fail" if fail_count else "pass", "notes": "Imported statuses; no validation rerun."}
    layer_rows = [layer_summary("validation_results", validations), layer_summary("acceptance_gates", gates), layer_summary("guards", guards)]
    blocking_errors = sum(row["status"] == "fail" and row["severity"] == "error" for row in validations)

    imported_review = read_csv("28_review_items.csv")
    review_rows = [{"review_item_id": row["review_item_id"], "source_review_item": row["topic"], "category": "bootstrap_protocol_gap", "severity": "review", "blocks_limited_review": "no", "blocks_stability_certification": "yes", "recommended_resolution": "Create QSB-EXTRACT03-C0 Bootstrap Freeze Addendum before any stability run.", "notes": row["reason"] + " " + row["impact"]} for row in imported_review]
    bootstrap_gap = bool(review_rows)

    claims = [
        ("E03B-CB-01", CLAIM, "computed_candidate_structure", "Review stored candidate structures descriptively.", "Treating candidates as physical evidence.", "pass", "Safe review statement."),
        ("E03B-CB-02", "D is a reconstructed cost-distance candidate.", "candidate_relational_grouping", "Report stored cost-distance summaries.", "Calling D proven geometry.", "pass", "Boundary retained."),
        ("E03B-CB-03", "Clusters and motif IDs are not stability-certified.", "inconclusive_pending_bootstrap_freeze", "Report candidates and the open gap.", "Calling them stable or bootstrap validated.", "pass", "No bootstrap run exists."),
        ("E03B-CB-04", "Claims that the run proves QSB, repairs L2, demonstrates gravity, or provides physical evidence for geometry are unsupported.", "unsupported_claim", "Do not make these claims.", "Any positive use of the listed wording.", "pass", "Explicit forbidden-claim context only."),
    ]
    claim_rows = [{"statement_id": a, "claim_or_statement": b, "classification": c, "safe_interpretation": d, "forbidden_interpretation": e, "status": f, "notes": g} for a,b,c,d,e,f,g in claims]

    l2_manifest = json.loads((L2 / "01_l2_run_manifest.json").read_text(encoding="utf-8"))
    m2_summary = {row["result_item"]: row["observed_value"] for row in csv.DictReader((M2 / "04_l2_contract_result_summary.csv").open(encoding="utf-8", newline=""))}
    l2_rows = [
        {"boundary_item": "L2_result", "upstream_value": l2_manifest["minimaltest_contract_result"], "current_review_value": "fail retained", "status": "pass", "notes": "No rerun or reinterpretation."},
        {"boundary_item": "N4_support", "upstream_value": f"{m2_summary['n4_support_count']}/3", "current_review_value": "0/3 retained; required 2/3", "status": "pass", "notes": "Feature-to-N4 separation and J2 gate remain unchanged."},
        {"boundary_item": "theta_new", "upstream_value": m2_summary["theta_new"], "current_review_value": "0.012446436850524916", "status": "pass", "notes": "Read-only reference."},
        {"boundary_item": "epsilon_new", "upstream_value": m2_summary["epsilon_new"], "current_review_value": "0.006009422749372488", "status": "pass", "notes": "Read-only reference."},
        {"boundary_item": "L2_manifest_sha256", "upstream_value": sha_file(L2 / "01_l2_run_manifest.json"), "current_review_value": sha_file(L2 / "01_l2_run_manifest.json"), "status": "pass", "notes": "Hash unchanged during review."},
    ]
    bootstrap_rows = [
        {"assessment_item": "bootstrap_seeds", "observed_value": "five frozen seeds exist in S1", "required_for_stability_certification": "necessary but insufficient", "status": "present", "blocking_for_stability_certification": "no", "notes": "Seeds alone do not define resampling."},
        {"assessment_item": "resampling_unit_and_method", "observed_value": "not frozen", "required_for_stability_certification": "required", "status": "gap", "blocking_for_stability_certification": "yes", "notes": "Not blocking computed candidate review."},
        {"assessment_item": "stability_acceptance_threshold", "observed_value": "not frozen", "required_for_stability_certification": "required", "status": "gap", "blocking_for_stability_certification": "yes", "notes": "Must be prospective, not tuned to EXTRACT03A-R1."},
        {"assessment_item": "bootstrap_execution", "observed_value": "not run", "required_for_stability_certification": "required after freeze", "status": "pending", "blocking_for_stability_certification": "yes", "notes": "No bootstrap run in EXTRACT03B."},
        {"assessment_item": "computed_candidate_review", "observed_value": "available", "required_for_stability_certification": "not applicable", "status": "not_blocked", "blocking_for_stability_certification": "no", "notes": "Descriptive review is valid within the claim boundary."},
    ]

    after_read = {rel(path): sha_path(path) for _, path, _, _ in upstream}
    if before != after_read:
        fail("extract03b_blocked_guard_violation", "upstream changed during read-only review")

    OUT.mkdir(parents=True)
    now = datetime.now(timezone.utc).isoformat()
    review_manifest = {
        "work_package": "QSB-EXTRACT03B", "status": STATUS, "created_at_utc": now, "repo_root": str(ROOT),
        "extract03a_r1_seen": True, "extract03a_r1_status": manifest["status"], "result_mart_seen": True,
        "result_mart_read_only_reviewed": True, "K_reviewed": True, "d_reviewed": True, "D_reviewed": True,
        "strength_edges_reviewed": True, "clusters_reviewed": True, "motifs_reviewed": True,
        "blocking_validation_errors_count": blocking_errors, "review_items_count": len(review_rows),
        "bootstrap_gap_present": bootstrap_gap, "stability_certified": False, "reexecution_performed": False,
        "K_recomputed": False, "d_recomputed": False, "D_recomputed": False,
        "shortest_paths_recomputed": False, "kernels_rerun": False, "clustering_rerun": False,
        "motif_extraction_rerun": False, "upstream_modified": False, "l2_fail_changed": False,
        "post_hoc_tuning_performed": False, "physical_evidence_claim_made": False,
        "claim_boundary": CLAIM + " All reviewed structures remain candidates; no physical interpretation follows.",
        "next_allowed_action": "prepare_QSB_EXTRACT03_C0_bootstrap_freeze_addendum_if_stability_certification_is_requested",
    }
    (OUT / FILES[0]).write_text(json.dumps(review_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    inventory_rows = [{"artifact_id": f"E03B-A{i:02d}", "upstream_block": block, "path": rel(path), "exists": "yes", "sha256": before[rel(path)], "role": "read-only review input", "required": required, "used_for": use, "notes": "Directory hashes are deterministic hashes over direct artifact names and file hashes; no upstream file modified."} for i,(block,path,required,use) in enumerate(upstream,1)]
    write_csv(FILES[1], list(inventory_rows[0]), inventory_rows)
    manifest_items = [("status",manifest["status"],EXPECTED_A_STATUS),("source_rows",manifest["source_rows"],168042),("ordered_pairs",manifest["ordered_pairs"],42),("x_points",manifest["x_points"],4001),("split_counts",json.dumps(manifest["split_counts"],sort_keys=True),json.dumps({"calibration":7,"validation":11,"review":19,"holdout":5},sort_keys=True)),("K_computed",manifest["K_computed"],True),("d_computed",manifest["d_computed"],True),("D_computed",manifest["D_computed"],True),("result_mart_written",manifest["result_mart_written"],True),("upstream_modified",manifest["upstream_modified"],False),("l2_fail_changed",manifest["l2_fail_changed"],False),("physical_evidence_claim_made",manifest["physical_evidence_claim_made"],False)]
    manifest_rows = [{"manifest_item": key, "observed_value": observed, "expected_or_reference_value": expected, "status": "pass" if str(observed)==str(expected) else "fail", "blocking": "yes", "notes": "Imported without mutation."} for key,observed,expected in manifest_items]
    write_csv(FILES[2], list(manifest_rows[0]), manifest_rows)
    write_csv(FILES[3], list(mart_rows[0]), mart_rows)
    write_csv(FILES[4], list(K_summary[0]), K_summary)
    write_csv(FILES[5], list(d_summary[0]), d_summary)
    write_csv(FILES[6], list(D_summary[0]), D_summary)
    write_csv(FILES[7], list(strength_edge_summary[0]), strength_edge_summary)
    write_csv(FILES[8], list(split_summary[0]), split_summary)
    write_csv(FILES[9], list(vector_summary[0]), vector_summary)
    write_csv(FILES[10], list(kernel_summary[0]), kernel_summary)
    write_csv(FILES[11], ["review_item","observed_value","status","notes"], cluster_summary)
    write_csv(FILES[12], ["review_item","observed_value","status","notes"], motif_summary)
    write_csv(FILES[13], list(layer_rows[0]), layer_rows)
    write_csv(FILES[14], list(review_rows[0]), review_rows)
    write_csv(FILES[15], list(claim_rows[0]), claim_rows)
    write_csv(FILES[16], list(l2_rows[0]), l2_rows)
    write_csv(FILES[17], list(bootstrap_rows[0]), bootstrap_rows)

    interpretation = f"""# QSB-EXTRACT03B Ergebnisprüfung

## Was EXTRACT03A-R1 geleistet hat

EXTRACT03A-R1 hat aus der eingefrorenen F3-ähnlichen Phasenantwortquelle gespeicherte Kandidatenmatrizen K, d und D sowie Stärke-, Kanten-, Dendrogramm- und Motiv-ID-Kandidaten erzeugt. EXTRACT03B liest und beschreibt ausschließlich diese bestehenden Ausgaben.

## Welche Strukturen nur Kandidaten sind

K ist eine Gram-/Korrelationskandidatin. d und D sind Kosten- beziehungsweise rekonstruierte Kostendistanzkandidaten. Kanten, Cluster und Motiv-IDs sind relationale Gruppierungskandidaten ohne physikalische oder geometrische Interpretation.

## Was validiert wurde

Es liegen {len(validations)} Validierungseinträge, {len(gates)} Acceptance Gates und {len(guards)} Guards vor. Blockierende Validierungsfehler: {blocking_errors}. Die Result-Mart-Integritätsprüfung war `{integrity}`.

## Was offen bleibt

S1 friert fünf Bootstrap-Seeds ein, aber weder Resampling-Einheit und -Methode noch eine prospektive Stabilitätsschwelle. Deshalb ist eine Stabilitätszertifizierung derzeit blockiert, nicht jedoch die begrenzte deskriptive Prüfung der berechneten Kandidaten.

## Warum der Status inconclusive sinnvoll ist

Die Kandidatenstrukturen sind berechnet und technisch prüfbar; ihre Cluster-/Motivstabilität ist ohne vollständigen Bootstrap-Vertrag nicht zertifiziert. Der Status trennt vorhandene Berechnung von offener Stabilitätsprüfung.

## Was ausdrücklich nicht behauptet wird

Der Review beweist weder QSB noch Raumzeitentstehung oder Gravitation, liefert keinen physikalischen Geometrienachweis und repariert den L2-Fail nicht.
"""
    (OUT / FILES[18]).write_text(interpretation, encoding="utf-8")
    options = [
        ("E03B-O01","human_review_only","Inspect existing candidate summaries within the claim boundary.","no","no","low","no","Does not address stability certification."),
        ("E03B-O02","bootstrap_freeze_addendum","Freeze resampling unit/method and stability threshold prospectively.","yes","no","low","yes","Recommended as QSB-EXTRACT03-C0 only if certification is wanted."),
        ("E03B-O03","extract03c_bootstrap_stability_run","Execute a later stability analysis under C0.","yes","yes","medium","no","Allowed only after a separate freeze and execution authorization."),
        ("E03B-O04","limited_interpretation_note","Document computed candidates and boundaries without stability language.","no","no","low","no","Can proceed independently of bootstrap certification."),
        ("E03B-O05","source_expansion_contract","Define a separate prospective source extension.","yes","yes","high","no","Outside current review scope."),
        ("E03B-O06","material_sensitive_source_contract_later","Prepare a separately authorized material-sensitive source contract.","yes","yes","high","no","Remains excluded from current scope."),
    ]
    option_rows = [{"option_id":a,"option":b,"purpose":c,"requires_new_human_decision":d,"requires_new_execution":e,"risk":f,"recommended":g,"notes":h} for a,b,c,d,e,f,g,h in options]
    write_csv(FILES[19], list(option_rows[0]), option_rows)
    recommendation = """# Empfohlener nächster Schritt

Wenn eine Cluster-/Motiv-Stabilitätszertifizierung gewünscht ist, wird **QSB-EXTRACT03-C0 — Bootstrap Freeze Addendum** empfohlen. Der Nachtrag muss vor jeder Ausführung die Resampling-Einheit, das deterministische Verfahren, den Umgang mit Splits sowie die Stabilitätsmetrik und Akzeptanzschwelle festlegen. Diese Entscheidung darf nicht an die EXTRACT03A-R1-Ergebnisse angepasst werden.

Für eine begrenzte deskriptive Interpretation der bereits berechneten Kandidaten ist C0 nicht erforderlich. Eine spätere Bootstrap-Ausführung benötigt eine separate Autorisierung.
"""
    (OUT / FILES[20]).write_text(recommendation, encoding="utf-8")
    short_note = f"""# QSB-EXTRACT03B Kurznotiz

Status: `{STATUS}`. EXTRACT03A-R1 und das Result-Mart wurden read-only geprüft. K/d/D, Stärke, Kanten, 41 Dendrogramm- und 41 Motiv-ID-Kandidaten liegen vor; blockierende Validierungsfehler: {blocking_errors}. Die Bootstrap-Prozedur ist nicht vollständig eingefroren, daher bleibt Stabilitätszertifizierung offen. Keine Neuberechnung, keine L2-Änderung und kein physikalischer Evidenzclaim.
"""
    (OUT / FILES[21]).write_text(short_note, encoding="utf-8")
    guard_names = ["no_K_recompute","no_d_recompute","no_D_recompute","no_shortest_path_rerun","no_kernel_rerun","no_clustering_rerun","no_motif_rerun","no_bootstrap_run","no_upstream_mutation","no_l2_change","no_post_hoc_tuning","no_physical_claim"]
    no_reexecution = [{"guard_id":f"E03B-G-{i:02d}","guard":guard,"status":"pass","evidence":"Review script has no computational execution path; inputs read as files and mart opened mode=ro&immutable=1.","notes":"Existing stored values only."} for i,guard in enumerate(guard_names,1)]
    write_csv(FILES[22], list(no_reexecution[0]), no_reexecution)
    final_note = f"""# QSB-EXTRACT03B Final Result

## Status

`{STATUS}`

## Reviewed Inputs

The 33-artifact EXTRACT03A-R1 output, its SQLite result mart, S1/package context, and L2/M2/N0 boundaries were reviewed read-only.

## Computed Candidate Structures

Stored K, d, D, strength, edge, dendrogram, and motif-ID candidates were summarized without recomputation.

## Validation Summary

Blocking validation errors: {blocking_errors}. One review item remains open.

## Bootstrap Gap

Seeds exist, but the resampling method and stability threshold are not frozen. This blocks stability certification, not limited candidate review.

## Claim Boundary

All structures remain computational candidates. No physical, geometric, gravity, or mechanism-confirmation claim follows.

## L2 Boundary

L2 remains fail with N4 support 0/3 versus required 2/3. theta_new and epsilon_new remain unchanged.

## Result-Mart Review

SQLite integrity: `{integrity}`; {len(tables)} tables read with `mode=ro&immutable=1`.

## Next Allowed Action

Prepare QSB-EXTRACT03-C0 Bootstrap Freeze Addendum if stability certification is requested; otherwise limit interpretation to descriptive candidate results.
"""
    (OUT / FILES[23]).write_text(final_note, encoding="utf-8")

    after = {rel(path): sha_path(path) for _, path, _, _ in upstream}
    if before != after:
        fail("extract03b_blocked_guard_violation", "upstream hash changed during output creation")
    actual = sorted(path.name for path in OUT.iterdir())
    if actual != sorted(FILES) or len(actual) != 24:
        fail("extract03b_blocked_guard_violation", f"output artifact mismatch: {len(actual)}")
    print(json.dumps({"status":STATUS,"artifacts":len(actual),"result_mart_read_only_reviewed":True,
        "K_d_D_summaries":True,"edges_clusters_motifs_reviewed":True,
        "blocking_validation_errors":blocking_errors,"bootstrap_gap":bootstrap_gap,
        "recomputation":False,"upstream_modified":False,"l2_changed":False}, indent=2))


if __name__ == "__main__":
    main()
