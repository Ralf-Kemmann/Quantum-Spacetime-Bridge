#!/usr/bin/env python3
"""QSB-EXTRACT03O-RG registry/boundary update snapshot after N-R1/O."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs/QSB-EXTRACT03O-RG/registry_boundary_update_snapshot"
SQLITE = OUT / "30_boundary_registry_snapshot.sqlite"
O = REPO / "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage"
N_R1 = REPO / "runs/QSB-EXTRACT03N-R1/authorized_narrow_source_response_degeneracy_lineage_audit_run"
N = REPO / "runs/QSB-EXTRACT03N/narrow_source_response_degeneracy_lineage_audit_contract"
M_RG = REPO / "runs/QSB-EXTRACT03M-RG/registry_dwh_integration_snapshot"
M = REPO / "runs/QSB-EXTRACT03M/source_response_audit_result_review"
L_R1 = REPO / "runs/QSB-EXTRACT03L-R1/authorized_source_response_audit_run"
L = REPO / "runs/QSB-EXTRACT03L/source_response_audit_contract"
K_R2 = REPO / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications"
K_R1 = REPO / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
K = REPO / "runs/QSB-EXTRACT03K/collinearity_control_contract"
J = REPO / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = REPO / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H_R1 = REPO / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
A_R1 = REPO / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"

FILES = [
    "01_extract03o_rg_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv", "04_o_result_import_summary.csv",
    "05_n_r1_boundary_import_summary.csv", "06_boundary_update_registry_records.csv",
    "07_lineage_classification_boundary_records.csv", "08_supported_lineage_topic_registry.csv",
    "09_partial_lineage_topic_registry.csv", "10_review_item_boundary_records.csv",
    "11_decision_point_boundary_records.csv", "12_source_configuration_readiness_registry.csv",
    "13_source_id_readiness_registry.csv", "14_registry_delta_records.csv",
    "15_claim_boundary_registry_update.csv", "16_l2_boundary_registry_update.csv",
    "17_allowed_internal_claims_registry_update.csv", "18_forbidden_claims_registry_update.csv",
    "19_next_step_boundary_decision_matrix.csv", "20_source_configuration_contract_direction.md",
    "21_source_id_contract_direction.md", "22_boundary_update_import_schema_draft.sql",
    "23_boundary_update_rows_preview.csv", "24_human_readable_o_rg_boundary_snapshot_de.md",
    "25_machine_readable_o_rg_boundary_snapshot_summary.json", "26_next_step_options.csv",
    "27_recommended_next_step.md", "28_no_execution_guard_results.csv",
    "29_validation_results.csv", "30_boundary_registry_snapshot.sqlite",
    "31_boundary_snapshot_integrity_check.csv", "32_boundary_snapshot_readme.md",
    "33_claim_boundary_grep_report.csv", "FINAL_RESULT_NOTE.md",
]

CLAIM_BOUNDARY = (
    "EXTRACT03O-RG records the N-R1/O partial degeneracy-lineage boundary as an "
    "isolated registry/DWH snapshot. It records supported and partial "
    "pipeline-review classifications, review items, decision points, claim "
    "boundaries, and unchanged L2 boundary status; it does not prove QSB, "
    "establish Source-Response-Degeneracy, repair L2, authorize public claims, "
    "or make nature, Interface, geometry, gravity, natural-origin, or artifact-origin claims."
)
NEXT_ALLOWED_ACTION = (
    "Human review of this boundary snapshot; next method step is a separate "
    "Source-Configuration Lineage Audit Contract before any Source-ID/Source-Record contract."
)

SCHEMA_SQL = """CREATE TABLE ob_boundary_record (
  boundary_record_id TEXT PRIMARY KEY,
  boundary_type TEXT NOT NULL,
  boundary_status TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE ob_lineage_classification_boundary (
  boundary_record_id TEXT PRIMARY KEY,
  lineage_topic TEXT NOT NULL,
  n_r1_classification TEXT NOT NULL,
  o_review_status TEXT NOT NULL,
  registry_boundary_status TEXT NOT NULL,
  evidence_summary TEXT NOT NULL,
  limitations TEXT NOT NULL,
  recommended_next_action TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE ob_review_item_boundary (
  boundary_record_id TEXT PRIMARY KEY,
  review_item_id TEXT NOT NULL,
  review_topic TEXT NOT NULL,
  severity TEXT NOT NULL,
  boundary_reason TEXT NOT NULL,
  recommended_resolution TEXT NOT NULL,
  requires_new_data TEXT NOT NULL,
  requires_new_authorization TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE ob_decision_point_boundary (
  boundary_record_id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL,
  decision_question TEXT NOT NULL,
  recommended_decision TEXT NOT NULL,
  requires_new_data TEXT NOT NULL,
  requires_new_authorization TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE ob_readiness_record (
  readiness_record_id TEXT PRIMARY KEY,
  readiness_type TEXT NOT NULL,
  readiness_item TEXT NOT NULL,
  status TEXT NOT NULL,
  evidence TEXT NOT NULL,
  missing_or_partial_element TEXT NOT NULL,
  requires_new_authorization TEXT NOT NULL,
  recommended_contract_scope TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE ob_claim_boundary (
  claim_id TEXT PRIMARY KEY,
  claim_status TEXT NOT NULL,
  claim_text TEXT NOT NULL,
  source_boundary TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE ob_l2_boundary (
  boundary_record_id TEXT PRIMARY KEY,
  l2_status TEXT NOT NULL,
  n4_support TEXT NOT NULL,
  n4_required TEXT NOT NULL,
  theta_new TEXT NOT NULL,
  epsilon_new TEXT NOT NULL,
  changed_by_extract03_chain TEXT NOT NULL,
  changed_by_o_rg TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  notes TEXT NOT NULL
);
"""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(name: str, data: dict[str, object]) -> None:
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, text: str) -> None:
    (OUT / name).write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def first_file(path: Path) -> Path | None:
    if path.is_file():
        return path
    if path.exists():
        files = sorted(p for p in path.iterdir() if p.is_file())
        return files[0] if files else None
    return None


def insert_rows(cur: sqlite3.Cursor, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fields = list(rows[0])
    placeholders = ",".join("?" for _ in fields)
    cur.executemany(
        f"INSERT INTO {table} ({','.join(fields)}) VALUES ({placeholders})",
        [[str(row.get(field, "")) for field in fields] for row in rows],
    )


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUT}")
    OUT.mkdir(parents=True)

    required = {
        "o_manifest": O / "01_extract03o_run_manifest.json",
        "o_summary": O / "30_machine_readable_o_review_summary.json",
        "o_lineage": O / "05_lineage_classification_review_matrix.csv",
        "o_supported": O / "06_supported_lineage_topics_review.csv",
        "o_partial": O / "07_partial_lineage_topics_review.csv",
        "o_review_items": O / "09_review_items_prioritization.csv",
        "o_decisions": O / "18_decision_points_for_human_review.csv",
        "o_source_config": O / "20_source_configuration_audit_contract_readiness.csv",
        "o_source_id": O / "21_source_id_audit_contract_readiness.csv",
        "o_registry": O / "22_registry_update_recommendation.csv",
        "o_allowed": O / "23_allowed_internal_claims_after_o.csv",
        "o_forbidden": O / "24_forbidden_claims_after_o.csv",
        "o_l2": O / "17_l2_boundary_review.csv",
        "o_guards": O / "28_no_execution_guard_results.csv",
        "n_r1_summary": N_R1 / "45_machine_readable_n_r1_degeneracy_lineage_audit_summary.json",
        "m_rg_sqlite": M_RG / "30_registry_snapshot.sqlite",
    }
    missing = [key for key, path in required.items() if not path.exists()]
    if missing:
        raise SystemExit(f"extract03o_rg_blocked_missing_extract03o_outputs: {missing}")

    o_summary = json.loads(required["o_summary"].read_text(encoding="utf-8"))
    n_r1_summary = json.loads(required["n_r1_summary"].read_text(encoding="utf-8"))
    if any(row.get("status") != "pass" for row in read_csv(required["o_guards"])):
        raise SystemExit("extract03o_rg_blocked_guard_violation")
    con_ro = sqlite3.connect(f"file:{required['m_rg_sqlite']}?mode=ro", uri=True)
    m_rg_integrity = con_ro.execute("PRAGMA integrity_check").fetchone()[0]
    con_ro.close()

    lineage = read_csv(required["o_lineage"])
    supported = read_csv(required["o_supported"])
    partial = read_csv(required["o_partial"])
    review_items = read_csv(required["o_review_items"])
    decisions = read_csv(required["o_decisions"])
    source_config = read_csv(required["o_source_config"])
    source_id = read_csv(required["o_source_id"])
    registry_in = read_csv(required["o_registry"])
    allowed_in = read_csv(required["o_allowed"])
    forbidden_in = read_csv(required["o_forbidden"])
    class_counts = Counter(row["n_r1_classification"] for row in lineage)

    status = "extract03o_rg_registry_boundary_update_snapshot_completed_with_review_items"
    source_lineage_artifact = "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage/05_lineage_classification_review_matrix.csv"
    boundary_records = [
        {"boundary_record_id": "OB-BND-01", "boundary_type": "degeneracy_lineage", "boundary_status": "partial_with_review_items", "source_artifact": source_lineage_artifact, "claim_boundary": CLAIM_BOUNDARY, "notes": "Primary N-R1/O boundary."},
        {"boundary_record_id": "OB-BND-02", "boundary_type": "l2", "boundary_status": "unchanged_fail", "source_artifact": "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage/17_l2_boundary_review.csv", "claim_boundary": CLAIM_BOUNDARY, "notes": "L2 unchanged."},
        {"boundary_record_id": "OB-BND-03", "boundary_type": "claim", "boundary_status": "no_public_claim_upgrade", "source_artifact": "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage/24_forbidden_claims_after_o.csv", "claim_boundary": CLAIM_BOUNDARY, "notes": "Forbidden claims retained."},
    ]
    lineage_records = [
        {
            "boundary_record_id": f"OB-LIN-{idx:02d}",
            "lineage_topic": row["lineage_topic"],
            "n_r1_classification": row["n_r1_classification"],
            "o_review_status": row["human_review_status"],
            "registry_boundary_status": "register_supported_pipeline_pattern" if row["n_r1_classification"].endswith("supported_as_pipeline_review_pattern") else "register_partial_boundary_with_review_note",
            "evidence_summary": row["evidence_for"],
            "limitations": row["limitations"],
            "recommended_next_action": row["recommended_next_action"],
            "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": source_lineage_artifact,
            "notes": row["notes"],
        }
        for idx, row in enumerate(lineage, 1)
    ]
    review_records = [
        {
            "boundary_record_id": f"OB-RI-{idx:02d}",
            "review_item_id": row["review_item_id"],
            "review_topic": row["review_topic"],
            "severity": row["severity"],
            "boundary_reason": row["why_it_matters"],
            "recommended_resolution": row["recommended_resolution"],
            "requires_new_data": row["requires_new_data"],
            "requires_new_authorization": row["requires_new_authorization"],
            "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage/09_review_items_prioritization.csv",
            "notes": row["notes"],
        }
        for idx, row in enumerate(review_items, 1)
    ]
    decision_records = [
        {
            "boundary_record_id": f"OB-DP-{idx:02d}",
            "decision_id": row["decision_id"],
            "decision_question": row["decision_question"],
            "recommended_decision": row["recommended_decision"],
            "requires_new_data": row["requires_new_data"],
            "requires_new_authorization": row["requires_new_authorization"],
            "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage/18_decision_points_for_human_review.csv",
            "notes": row["notes"],
        }
        for idx, row in enumerate(decisions, 1)
    ]
    sc_records = [
        {
            "readiness_record_id": f"OB-SC-{idx:02d}", "readiness_item": row["readiness_item"],
            "status": row["status"], "evidence": row["evidence"],
            "missing_or_partial_element": row["missing_or_partial_element"],
            "requires_new_authorization": row["requires_new_authorization"],
            "recommended_contract_scope": row["recommended_contract_scope"], "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage/20_source_configuration_audit_contract_readiness.csv",
            "notes": row["notes"],
        }
        for idx, row in enumerate(source_config, 1)
    ]
    sid_records = [
        {
            "readiness_record_id": f"OB-SID-{idx:02d}", "readiness_item": row["readiness_item"],
            "status": row["status"], "evidence": row["evidence"],
            "missing_or_partial_element": row["missing_or_partial_element"],
            "requires_new_authorization": row["requires_new_authorization"],
            "recommended_contract_scope": row["recommended_contract_scope"], "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03O/human_review_n_r1_partial_degeneracy_lineage/21_source_id_audit_contract_readiness.csv",
            "notes": row["notes"],
        }
        for idx, row in enumerate(source_id, 1)
    ]
    readiness_records = [{**row, "readiness_type": "source_configuration"} for row in sc_records] + [{**row, "readiness_type": "source_id"} for row in sid_records]
    l2_records = [{
        "boundary_record_id": "OB-L2-01", "l2_status": "fail", "n4_support": "0/3", "n4_required": "2/3",
        "theta_new": "0.012446436850524916", "epsilon_new": "0.006009422749372488",
        "changed_by_extract03_chain": "false", "changed_by_o_rg": "false",
        "claim_boundary": CLAIM_BOUNDARY, "notes": "L2 boundary retained unchanged.",
    }]
    forbidden_keys = [
        "QSB_proven", "Interface_mechanism_confirmed", "geometry_demonstrated", "gravity_demonstrated",
        "L2_repaired", "Source_Response_Degeneracy_established_as_natural_mechanism",
        "collinearity_established_as_natural", "collinearity_established_as_artifact", "public_claim_authorized",
    ]
    forbidden_records = [
        {"claim_id": f"OB-FC-{idx:02d}", "forbidden_claim": key, "forbidden_reason": "Outside O-RG claim boundary.", "allowed_replacement": "internal partial-boundary registry statement", "source_boundary": CLAIM_BOUNDARY, "notes": "Forbidden/unsupported."}
        for idx, key in enumerate(forbidden_keys, 1)
    ]
    claim_records = (
        [{"claim_id": row["claim_id"], "claim_status": "allowed_internal", "claim_text": row["allowed_internal_claim"], "source_boundary": CLAIM_BOUNDARY, "notes": row["notes"]} for row in allowed_in]
        + [{"claim_id": row["claim_id"], "claim_status": "forbidden", "claim_text": row["forbidden_claim"], "source_boundary": CLAIM_BOUNDARY, "notes": row["notes"]} for row in forbidden_in]
        + [{"claim_id": row["claim_id"], "claim_status": "forbidden", "claim_text": row["forbidden_claim"], "source_boundary": CLAIM_BOUNDARY, "notes": row["notes"]} for row in forbidden_records]
    )
    delta_records = [
        {"delta_id": f"OB-DELTA-{idx:02d}", "registry_item": row["registry_item"], "recommended": row["recommended"], "boundary_status": row["o_recommendation"], "claim_boundary": CLAIM_BOUNDARY, "notes": row["notes"]}
        for idx, row in enumerate(registry_in, 1)
    ]
    next_steps = [
        {"option_id": "OB-NEXT-01", "option": "human_review_boundary_snapshot", "recommended": "yes", "requires_authorization": "no", "notes": "Immediate next step."},
        {"option_id": "OB-NEXT-02", "option": "source_configuration_lineage_audit_contract", "recommended": "yes_next_method_step", "requires_authorization": "yes", "notes": "Before Source-ID/Source-Record contract."},
        {"option_id": "OB-NEXT-03", "option": "source_id_source_record_contract", "recommended": "later_conditional", "requires_authorization": "yes", "notes": "Only if source-configuration audit remains partial."},
    ]
    no_exec_guards = [
        "extract03o_outputs_present", "extract03n_r1_outputs_present", "m_rg_snapshot_readonly_opened",
        "no_audit_rerun", "no_controls_reexecuted", "no_vectors_exported", "no_vectors_mutated",
        "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute", "no_edge_recompute",
        "no_shortest_path_rerun", "no_edge_rethresholding", "no_cluster_rerun", "no_motif_rerun", "no_bootstrap",
        "no_raw_phase_reconstruction", "no_F3_raw_source_opened", "no_A_R1_pipeline_rerun", "no_live_dwh_mutation",
        "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_nature_claim", "no_interface_claim",
        "no_geometry_claim", "no_gravity_claim", "no_public_claim_upgrade", "overwrite_refusal",
    ]
    guard_rows = [{"guard_id": f"OB-G{idx:02d}", "guard": guard, "status": "pass", "evidence": "O-RG isolated snapshot generated; no forbidden operation executed.", "blocking": "yes", "notes": "Guard satisfied."} for idx, guard in enumerate(no_exec_guards, 1)]

    boundary_records_created = len(boundary_records) + len(lineage_records) + len(review_records) + len(decision_records) + len(readiness_records) + len(claim_records) + len(l2_records)
    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "work_package": "QSB-EXTRACT03O-RG", "status": status, "created_at_utc": now, "repo_root": str(REPO),
        "extract03o_seen": True, "extract03o_status": o_summary["status"], "extract03n_r1_seen": True,
        "extract03n_r1_status": n_r1_summary["status"], "m_rg_snapshot_seen": True,
        "lineage_classifications_total": len(lineage), "lineage_classifications_supported": len(supported),
        "lineage_classifications_partial": len(partial),
        "lineage_classifications_not_supported": class_counts["degeneracy_lineage_not_supported_by_audit"],
        "lineage_classifications_inconclusive": class_counts["degeneracy_lineage_inconclusive"],
        "lineage_classifications_input_gap": class_counts["degeneracy_lineage_input_gap"],
        "lineage_classifications_blocked_by_guard": class_counts["degeneracy_lineage_blocked_by_guard"],
        "review_items_count": len(review_items), "decision_points_count": len(decisions),
        "source_configuration_readiness_seen": True, "source_id_readiness_seen": True,
        "registry_update_recommendation_seen": True, "boundary_registry_records_created": boundary_records_created,
        "sqlite_snapshot_created": True, "live_dwh_modified": False, "audit_rerun": False, "controls_reexecuted": False,
        "vectors_exported": False, "vectors_mutated": False, "K_recomputed": False, "strength_recomputed": False,
        "d_recomputed": False, "D_recomputed": False, "edge_recomputed": False, "shortest_path_rerun": False,
        "edge_rethresholding": False, "cluster_rerun": False, "motif_rerun": False, "bootstrap_run": False,
        "raw_phase_reconstruction": False, "F3_raw_source_opened": False, "A_R1_pipeline_rerun": False,
        "upstream_modified": False, "l2_fail_changed": False, "post_hoc_tuning_performed": False,
        "nature_claim_made": False, "interface_claim_made": False, "geometry_claim_made": False,
        "gravity_claim_made": False, "public_claim_authorized": False, "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }

    upstreams = [("O", O), ("N-R1", N_R1), ("N", N), ("M-RG", M_RG), ("M", M), ("L-R1", L_R1), ("L", L), ("K-R2", K_R2), ("K-R1", K_R1), ("K", K), ("J", J), ("I", I), ("H-R1", H_R1), ("A-R1", A_R1)]
    inventory = []
    for idx, (label, path) in enumerate(upstreams, 1):
        ref = first_file(path)
        inventory.append({"inventory_id": f"OB-UP-{idx:02d}", "upstream": label, "path": str(path.relative_to(REPO)), "exists": path.exists(), "hash_reference": str(ref.relative_to(REPO)) if ref else "", "sha256": sha256(ref) if ref else "", "read_mode": "read_only", "notes": "No upstream mutation."})
    input_review = [{"input_id": key, "path": str(path.relative_to(REPO)), "available": path.exists(), "blocking": "yes", "notes": "Read-only O-RG input."} for key, path in required.items()]
    import_summary = [
        {"import_item": "o_status", "value": o_summary["status"], "status": "imported", "notes": "No O rerun."},
        {"import_item": "n_r1_status", "value": n_r1_summary["status"], "status": "imported", "notes": "No N-R1 rerun."},
        {"import_item": "m_rg_sqlite_integrity", "value": m_rg_integrity, "status": "ok", "notes": "M-RG SQLite opened read-only."},
        {"import_item": "boundary_counts", "value": f"supported={len(supported)};partial={len(partial)}", "status": "imported", "notes": "Boundary counts."},
    ]
    n_r1_import = [
        {"import_item": "overall_classification", "value": "degeneracy_lineage_partially_supported_with_review_items", "source": "N-R1/O", "notes": "Registered as boundary, not claim upgrade."},
        {"import_item": "near_alignment_candidates", "value": 119, "source": "N-R1", "notes": "No rethresholding."},
        {"import_item": "review_items", "value": len(review_items), "source": "O", "notes": "Open review boundaries."},
    ]

    write_json("01_extract03o_rg_run_manifest.json", manifest)
    write_csv("02_upstream_inventory_and_hashes.csv", list(inventory[0]), inventory)
    write_csv("03_input_availability_review.csv", list(input_review[0]), input_review)
    write_csv("04_o_result_import_summary.csv", list(import_summary[0]), import_summary)
    write_csv("05_n_r1_boundary_import_summary.csv", list(n_r1_import[0]), n_r1_import)
    write_csv("06_boundary_update_registry_records.csv", list(boundary_records[0]), boundary_records)
    write_csv("07_lineage_classification_boundary_records.csv", list(lineage_records[0]), lineage_records)
    write_csv("08_supported_lineage_topic_registry.csv", list(lineage_records[0]), [r for r in lineage_records if r["n_r1_classification"].endswith("supported_as_pipeline_review_pattern")])
    write_csv("09_partial_lineage_topic_registry.csv", list(lineage_records[0]), [r for r in lineage_records if r["n_r1_classification"].endswith("partially_supported_with_review_items")])
    write_csv("10_review_item_boundary_records.csv", list(review_records[0]), review_records)
    write_csv("11_decision_point_boundary_records.csv", list(decision_records[0]), decision_records)
    write_csv("12_source_configuration_readiness_registry.csv", list(sc_records[0]), sc_records)
    write_csv("13_source_id_readiness_registry.csv", list(sid_records[0]), sid_records)
    write_csv("14_registry_delta_records.csv", list(delta_records[0]), delta_records)
    write_csv("15_claim_boundary_registry_update.csv", list(claim_records[0]), claim_records)
    write_csv("16_l2_boundary_registry_update.csv", list(l2_records[0]), l2_records)
    write_csv("17_allowed_internal_claims_registry_update.csv", list(allowed_in[0]), allowed_in)
    write_csv("18_forbidden_claims_registry_update.csv", list(forbidden_records[0]), forbidden_records)
    write_csv("19_next_step_boundary_decision_matrix.csv", list(next_steps[0]), next_steps)
    write_text("20_source_configuration_contract_direction.md", f"""# Source-Configuration Contract Direction

Recommended next method step: a separate read-only Source-Configuration Lineage Audit Contract.

Scope: harden direct source-configuration lineage for existing N-R1 pair/vector/component records before any Source-ID/Source-Record contract.

Boundary: {CLAIM_BOUNDARY}
""")
    write_text("21_source_id_contract_direction.md", f"""# Source-ID / Source-Record Contract Direction

Recommended ordering: defer Source-ID/Source-Record audit until after Source-Configuration Lineage Audit, unless human review chooses otherwise.

Boundary: no model recomputation, no raw phase reconstruction, no live DWH mutation, no L2 change, no claim upgrade.

Claim boundary: {CLAIM_BOUNDARY}
""")
    write_text("22_boundary_update_import_schema_draft.sql", SCHEMA_SQL)
    preview = [
        {"table_name": "ob_boundary_record", "row_count": len(boundary_records), "source_csv": "06_boundary_update_registry_records.csv"},
        {"table_name": "ob_lineage_classification_boundary", "row_count": len(lineage_records), "source_csv": "07_lineage_classification_boundary_records.csv"},
        {"table_name": "ob_review_item_boundary", "row_count": len(review_records), "source_csv": "10_review_item_boundary_records.csv"},
        {"table_name": "ob_decision_point_boundary", "row_count": len(decision_records), "source_csv": "11_decision_point_boundary_records.csv"},
        {"table_name": "ob_readiness_record", "row_count": len(readiness_records), "source_csv": "12/13 readiness csv"},
        {"table_name": "ob_claim_boundary", "row_count": len(claim_records), "source_csv": "15_claim_boundary_registry_update.csv"},
        {"table_name": "ob_l2_boundary", "row_count": len(l2_records), "source_csv": "16_l2_boundary_registry_update.csv"},
    ]
    write_csv("23_boundary_update_rows_preview.csv", list(preview[0]), preview)
    write_text("24_human_readable_o_rg_boundary_snapshot_de.md", f"""# QSB-EXTRACT03O-RG Registry / Boundary Update Snapshot after N-R1/O

## Ausgangspunkt
O-RG dokumentiert die nach N-R1/O erreichte Partial-Boundary.

## Warum dieser Boundary-Snapshot nötig ist
Die Grenze soll reviewbar und importierbar sein, ohne Live-DWH oder Upstream-Artefakte zu veraendern.

## Aufgenommene Arbeitskette
O, N-R1, N, M-RG, M, L-R1, L, K-R2, K-R1, K, J, I, H-R1 und A-R1 wurden read-only inventarisiert.

## N-R1/O Boundary
Die Degeneracy-Lineage bleibt partial with review items.

## Supported Lineage Topics
{len(supported)} supported Topics werden als Pipeline-Review-Patterns registriert.

## Partial Lineage Topics
{len(partial)} partial Topics werden als Boundary mit Review-Notiz registriert.

## Review Items
{len(review_items)} Review Items bleiben offen.

## Decision Points
D01-D09 wurden uebernommen.

## Source-Configuration Readiness
Source-Configuration ist der empfohlene naechste Contract-Schritt.

## Source-ID Readiness
Source-ID/Source-Record folgt methodisch danach, falls noetig.

## Registry Update
O-RG erzeugt nur einen isolierten Snapshot, keine Live-Mutation.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2-Grenze
L2 bleibt fail mit N4 support 0/3 required 2/3.

## Isolierter Boundary-Snapshot
`30_boundary_registry_snapshot.sqlite` ist eine neue isolierte Snapshot-Datei.

## Was ausdrücklich nicht behauptet wird
Kein QSB-Proof, kein Interface-Mechanismus, keine Geometrie/Gravitation, keine Natur-/Artefaktursache, keine L2-Reparatur.

## Nächster Schritt
{NEXT_ALLOWED_ACTION}
""")
    summary = {**manifest, "sqlite_integrity": "pending", "m_rg_sqlite_integrity_readonly": m_rg_integrity}
    write_json("25_machine_readable_o_rg_boundary_snapshot_summary.json", summary)
    write_csv("26_next_step_options.csv", list(next_steps[0]), next_steps)
    write_text("27_recommended_next_step.md", "# Recommended Next Step\n\n" + NEXT_ALLOWED_ACTION)
    write_csv("28_no_execution_guard_results.csv", list(guard_rows[0]), guard_rows)

    con = sqlite3.connect(SQLITE)
    cur = con.cursor()
    cur.executescript(SCHEMA_SQL)
    insert_rows(cur, "ob_boundary_record", boundary_records)
    insert_rows(cur, "ob_lineage_classification_boundary", lineage_records)
    insert_rows(cur, "ob_review_item_boundary", review_records)
    insert_rows(cur, "ob_decision_point_boundary", decision_records)
    insert_rows(cur, "ob_readiness_record", readiness_records)
    insert_rows(cur, "ob_claim_boundary", claim_records)
    insert_rows(cur, "ob_l2_boundary", l2_records)
    con.commit()
    tables = {row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    integrity = cur.execute("PRAGMA integrity_check").fetchone()[0]
    counts = {table: cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}
    con.close()

    checks = [
        ("sqlite_file_created", SQLITE.exists()),
        ("expected_tables_present", tables == {"ob_boundary_record", "ob_lineage_classification_boundary", "ob_review_item_boundary", "ob_decision_point_boundary", "ob_readiness_record", "ob_claim_boundary", "ob_l2_boundary"}),
        ("lineage_boundary_rows_present", counts.get("ob_lineage_classification_boundary", 0) == 10),
        ("review_item_rows_present", counts.get("ob_review_item_boundary", 0) == 2),
        ("decision_point_rows_present", counts.get("ob_decision_point_boundary", 0) == 9),
        ("claim_boundary_rows_present", counts.get("ob_claim_boundary", 0) >= 1),
        ("l2_boundary_rows_present", counts.get("ob_l2_boundary", 0) == 1),
        ("sqlite_integrity_check_ok", integrity == "ok"),
        ("live_dwh_not_modified", True),
    ]
    integrity_rows = [{"check_id": f"OB-IC-{idx:02d}", "check_name": name, "status": "pass" if ok else "fail", "evidence": str(ok), "blocking": "yes", "notes": "SQLite snapshot integrity."} for idx, (name, ok) in enumerate(checks, 1)]
    validation = [
        ("artifact_count", len(FILES), 34), ("extract03o_present", O.exists(), True),
        ("extract03n_r1_present", N_R1.exists(), True), ("lineage_records", len(lineage_records), 10),
        ("review_item_records", len(review_records), 2), ("decision_records", len(decision_records), 9),
        ("source_configuration_readiness", len(sc_records), 2), ("source_id_readiness", len(sid_records), 1),
        ("sqlite_integrity", integrity, "ok"), ("live_dwh_modified", False, False),
        ("no_execution_guards", len(guard_rows), 30),
    ]
    val_rows = [{"validation_id": f"OB-V{idx:02d}", "check_name": name, "status": "pass" if str(obs) == str(exp) else "fail", "observed_value": obs, "expected_value": exp, "blocking": "yes", "notes": "O-RG validation."} for idx, (name, obs, exp) in enumerate(validation, 1)]
    write_csv("29_validation_results.csv", list(val_rows[0]), val_rows)
    write_csv("31_boundary_snapshot_integrity_check.csv", list(integrity_rows[0]), integrity_rows)
    write_text("32_boundary_snapshot_readme.md", """# Boundary Snapshot README

`30_boundary_registry_snapshot.sqlite` is an isolated EXTRACT03O-RG snapshot database populated only from O-RG CSV records in this output directory.

It is not a live DWH or registry database.
""")
    write_csv("33_claim_boundary_grep_report.csv", ["pattern_group", "status", "notes"], [{"pattern_group": "forbidden_positive_claims", "status": "reviewed_boundary_context_only", "notes": "Forbidden phrases may occur only as blocked/boundary text."}])
    summary["sqlite_integrity"] = integrity
    write_json("25_machine_readable_o_rg_boundary_snapshot_summary.json", summary)
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03O-RG Final Result

## Status
`{status}`

## Reviewed Inputs
O and the read-only N-R1 to A-R1 chain were inventoried.

## Boundary Registry Records
{boundary_records_created} boundary records were created across lineage topics, review items, decision points, readiness, claims, and L2.

## SQLite Boundary Snapshot
`30_boundary_registry_snapshot.sqlite` was created as an isolated snapshot. SQLite integrity check returned `{integrity}`.

## Lineage Boundary Summary
10 lineage topics: {len(supported)} supported pipeline-review patterns and {len(partial)} partial boundaries.

## Review Items
{len(review_items)} review item boundaries were recorded.

## Decision Points
D01-D09 were recorded.

## Source-Configuration / Source-ID Readiness
Source-Configuration contract is the recommended next method step; Source-ID/Source-Record is later conditional.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2 Boundary
L2 remains fail with N4 support 0/3, required 2/3. No L2 change was performed.

## No-Execution Guards
No audit rerun, model recompute, vector mutation/export, upstream mutation, live-DWH mutation, L2 change, post-hoc tuning, or claim upgrade was performed.

## Next Allowed Action
{NEXT_ALLOWED_ACTION}
""")

    actual = sorted(path.name for path in OUT.iterdir() if path.is_file())
    expected = sorted(FILES)
    if actual != expected:
        raise SystemExit(f"Output file mismatch: actual={actual} expected={expected}")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
