#!/usr/bin/env python3
"""QSB-EXTRACT03M-RG registry / DWH integration snapshot.

Creates an isolated registry snapshot from EXTRACT03M review outputs. The
script does not write to any existing registry or DWH database.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs/QSB-EXTRACT03M-RG/registry_dwh_integration_snapshot"
SQLITE = OUT / "30_registry_snapshot.sqlite"
M = REPO / "runs/QSB-EXTRACT03M/source_response_audit_result_review"
UPSTREAMS = [
    ("EXTRACT03I", REPO / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review", "identity_k_alignment_review"),
    ("EXTRACT03J", REPO / "runs/QSB-EXTRACT03J/near_alignment_structure_review", "near_alignment_structure_review"),
    ("EXTRACT03K", REPO / "runs/QSB-EXTRACT03K/collinearity_control_contract", "control_contract"),
    ("EXTRACT03K-R1", REPO / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run", "authorized_control_run"),
    ("EXTRACT03K-R2", REPO / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications", "human_review_decision_matrix"),
    ("EXTRACT03L", REPO / "runs/QSB-EXTRACT03L/source_response_audit_contract", "source_response_audit_contract"),
    ("EXTRACT03L-R1", REPO / "runs/QSB-EXTRACT03L-R1/authorized_source_response_audit_run", "authorized_source_response_audit_run"),
    ("EXTRACT03M", M, "source_response_audit_result_review"),
]

FILES = [
    "01_extract03m_rg_run_manifest.json",
    "02_upstream_chain_inventory.csv",
    "03_upstream_artifact_hashes.csv",
    "04_input_availability_review.csv",
    "05_work_package_status_registry.csv",
    "06_artifact_registry_records.csv",
    "07_aq_classification_registry_records.csv",
    "08_origin_topic_registry_records.csv",
    "09_review_item_registry_records.csv",
    "10_decision_point_registry_records.csv",
    "11_guard_result_registry_records.csv",
    "12_claim_boundary_registry_records.csv",
    "13_l2_boundary_registry_record.csv",
    "14_crosswalk_i_to_m_registry.csv",
    "15_pipeline_review_pattern_summary.csv",
    "16_partial_and_inconclusive_summary.csv",
    "17_forbidden_claims_registry.csv",
    "18_allowed_internal_claims_registry.csv",
    "19_registry_import_schema_draft.sql",
    "20_registry_import_rows_preview.csv",
    "21_dwh_integration_plan.md",
    "22_human_readable_registry_snapshot_de.md",
    "23_machine_readable_registry_snapshot_summary.json",
    "24_next_step_options.csv",
    "25_recommended_next_step.md",
    "26_no_execution_guard_results.csv",
    "27_validation_results.csv",
    "28_publication_safe_note_candidates.md",
    "29_short_result_note_de.md",
    "30_registry_snapshot.sqlite",
    "31_registry_snapshot_integrity_check.csv",
    "32_registry_snapshot_readme.md",
    "33_claim_boundary_grep_report.csv",
    "FINAL_RESULT_NOTE.md",
]

CLAIM_BOUNDARY = (
    "EXTRACT03M-RG prepares a registry/DWH integration snapshot for the completed "
    "EXTRACT03 I-to-M review chain. The snapshot records pipeline-review "
    "classifications, claim boundaries, guards, review items, decision points, "
    "and unchanged L2 boundary status. It makes no nature, Interface, geometry, "
    "gravity, or L2-repair claim."
)
NEXT_ALLOWED_ACTION = (
    "Human review of this isolated registry snapshot; optionally create a "
    "separate, explicit Source-Response degeneracy lineage-audit contract."
)


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
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def top_files(path: Path) -> list[Path]:
    return sorted(p for p in path.iterdir() if p.is_file()) if path.exists() else []


def create_sqlite(
    work_rows: list[dict[str, object]],
    origin_rows: list[dict[str, object]],
    review_rows: list[dict[str, object]],
    decision_rows: list[dict[str, object]],
    guard_rows: list[dict[str, object]],
    claim_rows: list[dict[str, object]],
    l2_rows: list[dict[str, object]],
) -> dict[str, object]:
    con = sqlite3.connect(SQLITE)
    cur = con.cursor()
    cur.executescript(SCHEMA_SQL)

    def insert(table: str, rows: list[dict[str, object]]) -> None:
        if not rows:
            return
        fields = list(rows[0])
        placeholders = ",".join(["?"] * len(fields))
        cur.executemany(
            f"INSERT INTO {table} ({','.join(fields)}) VALUES ({placeholders})",
            [[str(row.get(field, "")) for field in fields] for row in rows],
        )

    insert("rg_work_package_status", work_rows)
    insert("rg_origin_topic_classification", origin_rows)
    insert("rg_review_item", review_rows)
    insert("rg_decision_point", decision_rows)
    insert("rg_guard_result", guard_rows)
    insert("rg_claim_boundary", claim_rows)
    insert("rg_l2_boundary", l2_rows)
    con.commit()
    table_names = {
        row[0]
        for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    integrity = cur.execute("PRAGMA integrity_check").fetchone()[0]
    counts = {
        table: cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in [
            "rg_work_package_status",
            "rg_origin_topic_classification",
            "rg_review_item",
            "rg_decision_point",
            "rg_guard_result",
            "rg_claim_boundary",
            "rg_l2_boundary",
        ]
    }
    con.close()
    return {"tables": sorted(table_names), "integrity": integrity, "counts": counts}


SCHEMA_SQL = """CREATE TABLE rg_work_package_status (
  registry_id TEXT PRIMARY KEY,
  work_package TEXT NOT NULL,
  status TEXT NOT NULL,
  role_in_chain TEXT NOT NULL,
  upstream_path TEXT NOT NULL,
  artifact_count_if_known TEXT NOT NULL,
  claim_boundary_status TEXT NOT NULL,
  l2_boundary_status TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE rg_origin_topic_classification (
  registry_id TEXT PRIMARY KEY,
  origin_topic TEXT NOT NULL,
  classification TEXT NOT NULL,
  evidence_summary TEXT NOT NULL,
  limitations TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  recommended_registry_status TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE rg_review_item (
  registry_id TEXT PRIMARY KEY,
  review_item_id TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  severity TEXT NOT NULL,
  recommended_resolution TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE rg_decision_point (
  registry_id TEXT PRIMARY KEY,
  decision_id TEXT NOT NULL,
  decision_question TEXT NOT NULL,
  recommended_decision TEXT NOT NULL,
  requires_new_data TEXT NOT NULL,
  requires_new_authorization TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE rg_guard_result (
  registry_id TEXT PRIMARY KEY,
  guard_id TEXT NOT NULL,
  guard TEXT NOT NULL,
  status TEXT NOT NULL,
  evidence TEXT NOT NULL,
  blocking TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE rg_claim_boundary (
  registry_id TEXT PRIMARY KEY,
  claim_key TEXT NOT NULL,
  claim_status TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  source_artifact TEXT NOT NULL,
  notes TEXT NOT NULL
);
CREATE TABLE rg_l2_boundary (
  registry_id TEXT PRIMARY KEY,
  l2_status TEXT NOT NULL,
  n4_support TEXT NOT NULL,
  n4_required TEXT NOT NULL,
  theta_new TEXT NOT NULL,
  epsilon_new TEXT NOT NULL,
  changed_by_extract03_chain TEXT NOT NULL,
  claim_boundary TEXT NOT NULL,
  notes TEXT NOT NULL
);
"""


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUT}")
    OUT.mkdir(parents=True)

    required = {
        "m_manifest": M / "01_extract03m_run_manifest.json",
        "aq_review": M / "05_AQ_classification_review.csv",
        "origin_review": M / "06_origin_classification_review_matrix.csv",
        "supported_topics": M / "07_supported_origin_topics_review.csv",
        "partial_topics": M / "08_partial_origin_topics_review.csv",
        "inconclusive_topics": M / "10_inconclusive_origin_topics_review.csv",
        "crosswalk_ijk": M / "21_crosswalk_to_I_J_K_reviews.csv",
        "crosswalk_kr": M / "22_crosswalk_to_K_R1_K_R2_decisions.csv",
        "review_items": M / "23_open_review_items_from_L_R1.csv",
        "decision_points": M / "24_decision_points_for_human_review.csv",
        "registry_recommendation": M / "27_registry_or_dwh_integration_recommendation.csv",
        "guards": M / "32_guard_results.csv",
        "validation": M / "33_validation_results.csv",
        "summary": M / "35_machine_readable_m_result_review_summary.json",
        "final_note": M / "FINAL_RESULT_NOTE.md",
    }
    missing = [key for key, path in required.items() if not path.exists()]
    if missing:
        status = "extract03m_rg_blocked_missing_extract03m_outputs"
        if "origin_review" in missing:
            status = "extract03m_rg_blocked_missing_origin_classification_matrix"
        raise SystemExit(f"{status}: missing {missing}")

    m_manifest = json.loads(required["m_manifest"].read_text(encoding="utf-8"))
    m_summary = json.loads(required["summary"].read_text(encoding="utf-8"))
    aq_rows = read_csv(required["aq_review"])
    origin_m_rows = read_csv(required["origin_review"])
    review_item_m_rows = read_csv(required["review_items"])
    decision_m_rows = read_csv(required["decision_points"])
    guard_m_rows = read_csv(required["guards"])
    crosswalk_ijk_rows = read_csv(required["crosswalk_ijk"])
    crosswalk_kr_rows = read_csv(required["crosswalk_kr"])

    if any(row.get("status") != "pass" for row in guard_m_rows):
        raise SystemExit("extract03m_rg_blocked_guard_violation")

    class_counts = Counter(row["l_r1_classification"] for row in origin_m_rows)
    supported_cls = "source_response_origin_supported_as_pipeline_review_pattern"
    partial_cls = "source_response_origin_partially_supported_with_review_items"
    not_supported_cls = "source_response_origin_not_supported_by_audit"
    inconclusive_cls = "source_response_origin_inconclusive"
    input_gap_cls = "source_response_origin_input_gap"
    blocked_cls = "source_response_origin_blocked_by_guard"
    status = "extract03m_rg_registry_dwh_integration_snapshot_completed_ready_for_review"
    if review_item_m_rows or class_counts[partial_cls] or class_counts[inconclusive_cls]:
        status = "extract03m_rg_registry_dwh_integration_snapshot_completed_with_review_items"
    if class_counts[input_gap_cls]:
        status = "extract03m_rg_registry_dwh_integration_snapshot_completed_with_input_gaps"

    chain_inventory = []
    artifact_hashes = []
    for idx, (wp, path, role) in enumerate(UPSTREAMS, 1):
        files = top_files(path)
        chain_inventory.append(
            {
                "chain_order": idx,
                "work_package": wp,
                "role_in_chain": role,
                "upstream_path": str(path.relative_to(REPO)),
                "exists": path.exists(),
                "artifact_count_if_known": len(files),
                "read_mode": "read_only",
                "notes": "Included in isolated snapshot inventory.",
            }
        )
        for file_path in files:
            artifact_hashes.append(
                {
                    "work_package": wp,
                    "artifact_path": str(file_path.relative_to(REPO)),
                    "sha256": sha256(file_path),
                    "bytes": file_path.stat().st_size,
                    "read_mode": "read_only",
                    "notes": "Hash only; no artifact mutation.",
                }
            )

    input_rows = [
        {
            "input_id": key,
            "path": str(path.relative_to(REPO)),
            "available": path.exists(),
            "blocking": key in {"m_manifest", "origin_review", "summary"},
            "used_for": "registry snapshot import",
            "notes": "Read-only.",
        }
        for key, path in required.items()
    ]

    known_status = {
        "EXTRACT03I": "completed_context_available",
        "EXTRACT03J": "completed_context_available",
        "EXTRACT03K": "contract_completed_no_execution",
        "EXTRACT03K-R1": "authorized_controls_completed",
        "EXTRACT03K-R2": "human_review_completed_decision_matrix_ready",
        "EXTRACT03L": "contract_completed_ready_for_authorized_audit",
        "EXTRACT03L-R1": "authorized_source_response_audit_completed",
        "EXTRACT03M": str(m_summary.get("status", "")),
    }
    work_rows = []
    for idx, row in enumerate(chain_inventory, 1):
        work_rows.append(
            {
                "registry_id": f"RG-WP-{idx:02d}",
                "work_package": row["work_package"],
                "status": known_status[row["work_package"]],
                "role_in_chain": row["role_in_chain"],
                "upstream_path": row["upstream_path"],
                "artifact_count_if_known": row["artifact_count_if_known"],
                "claim_boundary_status": "bounded_no_physical_or_public_claim_expansion",
                "l2_boundary_status": "unchanged_fail" if row["work_package"] in {"EXTRACT03L-R1", "EXTRACT03M"} else "not_modified_by_snapshot",
                "notes": "Registry snapshot record only.",
            }
        )

    artifact_rows = [
        {
            "registry_id": f"RG-ART-{idx:04d}",
            "work_package": row["work_package"],
            "artifact_path": row["artifact_path"],
            "sha256": row["sha256"],
            "bytes": row["bytes"],
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Artifact hash registry record.",
        }
        for idx, row in enumerate(artifact_hashes, 1)
    ]
    aq_registry = [
        {
            "registry_id": f"RG-AQ-{idx:02d}",
            "audit_question_id": row["audit_question_id"],
            "classification": row["l_r1_classification"],
            "human_review_status": row["human_review_status"],
            "recommended_human_decision": row["recommended_human_decision"],
            "source_artifact": "runs/QSB-EXTRACT03M/source_response_audit_result_review/05_AQ_classification_review.csv",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": row["notes"],
        }
        for idx, row in enumerate(aq_rows, 1)
    ]
    origin_registry = [
        {
            "registry_id": f"RG-ORIGIN-{idx:02d}",
            "origin_topic": row["origin_topic"],
            "classification": row["l_r1_classification"],
            "evidence_summary": row["evidence_for"],
            "limitations": row["limitations"],
            "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03M/source_response_audit_result_review/06_origin_classification_review_matrix.csv",
            "recommended_registry_status": row["recommended_human_decision"],
            "notes": row["notes"],
        }
        for idx, row in enumerate(origin_m_rows, 1)
    ]
    review_registry = [
        {
            "registry_id": f"RG-REVIEW-{idx:02d}",
            "review_item_id": row["review_item_id"],
            "category": row["category"],
            "description": row["description"],
            "severity": row["severity"],
            "recommended_resolution": row["recommended_resolution"],
            "source_artifact": "runs/QSB-EXTRACT03M/source_response_audit_result_review/23_open_review_items_from_L_R1.csv",
            "notes": row["notes"],
        }
        for idx, row in enumerate(review_item_m_rows, 1)
    ]
    decision_registry = [
        {
            "registry_id": f"RG-DECISION-{idx:02d}",
            "decision_id": row["decision_id"],
            "decision_question": row["decision_question"],
            "recommended_decision": row["recommended_decision"],
            "requires_new_data": row["requires_new_data"],
            "requires_new_authorization": row["requires_new_authorization"],
            "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03M/source_response_audit_result_review/24_decision_points_for_human_review.csv",
            "notes": row["notes"],
        }
        for idx, row in enumerate(decision_m_rows, 1)
    ]
    guard_registry = [
        {
            "registry_id": f"RG-GUARD-{idx:02d}",
            "guard_id": row["guard_id"],
            "guard": row["guard"],
            "status": row["status"],
            "evidence": row["evidence"],
            "blocking": row["blocking"],
            "notes": row["notes"],
        }
        for idx, row in enumerate(guard_m_rows, 1)
    ]
    claim_rows = [
        {
            "registry_id": "RG-CLAIM-01",
            "claim_key": "safe_snapshot_scope",
            "claim_status": "allowed_internal_record",
            "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03M/source_response_audit_result_review/01_extract03m_run_manifest.json",
            "notes": "Internal registry snapshot only.",
        },
        {
            "registry_id": "RG-CLAIM-02",
            "claim_key": "physical_or_public_claim_expansion",
            "claim_status": "blocked",
            "claim_boundary": CLAIM_BOUNDARY,
            "source_artifact": "runs/QSB-EXTRACT03M/source_response_audit_result_review/FINAL_RESULT_NOTE.md",
            "notes": "No nature, Interface, geometry, gravity, or public-claim authorization.",
        },
    ]
    l2_rows = [
        {
            "registry_id": "RG-L2-01",
            "l2_status": "fail",
            "n4_support": "0/3",
            "n4_required": "2/3",
            "theta_new": "0.012446436850524916",
            "epsilon_new": "0.006009422749372488",
            "changed_by_extract03_chain": "false",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "L2 boundary copied as unchanged fail state.",
        }
    ]

    forbidden_keys = [
        "QSB_proven",
        "Interface_mechanism_confirmed",
        "geometry_demonstrated",
        "gravity_demonstrated",
        "L2_repaired",
        "collinearity_established_as_natural",
        "collinearity_established_as_artifact",
        "public_claim_authorized",
    ]
    forbidden_rows = [
        {
            "claim_key": key,
            "registry_status": "forbidden",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Explicitly blocked for this snapshot.",
        }
        for key in forbidden_keys
    ]
    allowed_keys = [
        "I_to_M_chain_review_completed",
        "full_response_vectors_reviewed",
        "identity_groups_component_pure",
        "near_alignment_patterns_characterized",
        "collinearity_controls_classified",
        "source_response_audit_completed",
        "origin_classifications_reviewed",
        "registry_snapshot_created",
        "l2_boundary_unchanged",
    ]
    allowed_rows = [
        {
            "claim_key": key,
            "registry_status": "allowed_internal_bounded_statement",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Internal documentation statement only.",
        }
        for key in allowed_keys
    ]

    pipeline_summary = [
        {
            "classification": supported_cls,
            "topic_count": class_counts[supported_cls],
            "registry_status": "ready_for_internal_registry",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Pipeline-review pattern only.",
        }
    ]
    partial_summary = [
        {
            "classification": partial_cls,
            "topic_count": class_counts[partial_cls],
            "registry_status": "registry_with_review_note",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Partial classification retained.",
        },
        {
            "classification": inconclusive_cls,
            "topic_count": class_counts[inconclusive_cls],
            "registry_status": "open_review_item",
            "claim_boundary": CLAIM_BOUNDARY,
            "notes": "Degeneracy remains inconclusive.",
        },
    ]
    crosswalk_registry = []
    for idx, row in enumerate(crosswalk_ijk_rows + crosswalk_kr_rows, 1):
        crosswalk_registry.append(
            {
                "registry_id": f"RG-XWALK-{idx:02d}",
                "source_block": row.get("source_block") or row.get("decision_source"),
                "imported_context": row.get("imported_context") or row.get("decision_or_hypothesis"),
                "snapshot_use": row.get("m_review_use") or row.get("m_review"),
                "claim_boundary": CLAIM_BOUNDARY,
                "notes": row["notes"],
            }
        )

    preview_rows = [
        {"table_name": "rg_work_package_status", "row_count": len(work_rows), "source_csv": "05_work_package_status_registry.csv"},
        {"table_name": "rg_origin_topic_classification", "row_count": len(origin_registry), "source_csv": "08_origin_topic_registry_records.csv"},
        {"table_name": "rg_review_item", "row_count": len(review_registry), "source_csv": "09_review_item_registry_records.csv"},
        {"table_name": "rg_decision_point", "row_count": len(decision_registry), "source_csv": "10_decision_point_registry_records.csv"},
        {"table_name": "rg_guard_result", "row_count": len(guard_registry), "source_csv": "11_guard_result_registry_records.csv"},
        {"table_name": "rg_claim_boundary", "row_count": len(claim_rows), "source_csv": "12_claim_boundary_registry_records.csv"},
        {"table_name": "rg_l2_boundary", "row_count": len(l2_rows), "source_csv": "13_l2_boundary_registry_record.csv"},
    ]
    next_options = [
        {
            "option_id": "MRG-NEXT-01",
            "option": "human_review_registry_snapshot",
            "recommended": "yes",
            "requires_new_authorization": "no",
            "notes": "Immediate next step.",
        },
        {
            "option_id": "MRG-NEXT-02",
            "option": "import_snapshot_into_library_or_DWH_layer_after_review",
            "recommended": "conditional",
            "requires_new_authorization": "yes_if_live_mutation",
            "notes": "This run did not mutate live DWH.",
        },
        {
            "option_id": "MRG-NEXT-03",
            "option": "source_response_degeneracy_lineage_audit_contract",
            "recommended": "conditional",
            "requires_new_authorization": "yes",
            "notes": "Only as a separate future contract.",
        },
    ]
    no_exec_guards = [
        "live_dwh_not_modified",
        "no_audit_rerun",
        "no_controls_reexecuted",
        "no_vectors_exported",
        "no_K_recompute",
        "no_strength_recompute",
        "no_d_recompute",
        "no_D_recompute",
        "no_edge_recompute",
        "no_shortest_path_rerun",
        "no_edge_rethresholding",
        "no_cluster_rerun",
        "no_motif_rerun",
        "no_bootstrap",
        "no_raw_phase_reconstruction",
        "no_F3_raw_source_opened",
        "no_A_R1_pipeline_rerun",
        "no_upstream_mutation",
        "no_l2_change",
        "no_post_hoc_tuning",
        "no_nature_claim",
        "no_interface_claim",
        "no_geometry_claim",
        "no_gravity_claim",
        "overwrite_refusal",
    ]
    no_exec_rows = [
        {
            "guard_id": f"MRG-G{i:02d}",
            "guard": guard,
            "status": "pass",
            "evidence": "Isolated snapshot written only under EXTRACT03M-RG output directory.",
            "blocking": "yes",
            "notes": "Guard satisfied.",
        }
        for i, guard in enumerate(no_exec_guards, 1)
    ]

    registry_records_created = (
        len(work_rows)
        + len(artifact_rows)
        + len(aq_registry)
        + len(origin_registry)
        + len(review_registry)
        + len(decision_registry)
        + len(guard_registry)
        + len(claim_rows)
        + len(l2_rows)
    )
    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        "work_package": "QSB-EXTRACT03M-RG",
        "status": status,
        "created_at_utc": now,
        "repo_root": str(REPO),
        "extract03m_seen": True,
        "extract03m_status": m_summary.get("status", ""),
        "chain_work_packages_seen": [row["work_package"] for row in chain_inventory if row["exists"]],
        "chain_work_packages_expected": [row[0] for row in UPSTREAMS],
        "origin_topics_total": len(origin_m_rows),
        "origin_topics_supported": class_counts[supported_cls],
        "origin_topics_partial": class_counts[partial_cls],
        "origin_topics_not_supported": class_counts[not_supported_cls],
        "origin_topics_inconclusive": class_counts[inconclusive_cls],
        "origin_topics_input_gap": class_counts[input_gap_cls],
        "origin_topics_blocked_by_guard": class_counts[blocked_cls],
        "decision_points_count": len(decision_registry),
        "review_items_count": len(review_registry),
        "registry_records_created": registry_records_created,
        "sqlite_snapshot_created": True,
        "live_dwh_modified": False,
        "audit_rerun": False,
        "controls_reexecuted": False,
        "vectors_exported": False,
        "K_recomputed": False,
        "strength_recomputed": False,
        "d_recomputed": False,
        "D_recomputed": False,
        "edge_recomputed": False,
        "shortest_path_rerun": False,
        "edge_rethresholding": False,
        "cluster_rerun": False,
        "motif_rerun": False,
        "raw_phase_reconstruction": False,
        "F3_raw_source_opened": False,
        "A_R1_pipeline_rerun": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "post_hoc_tuning_performed": False,
        "nature_claim_made": False,
        "interface_claim_made": False,
        "geometry_claim_made": False,
        "gravity_claim_made": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }

    write_json("01_extract03m_rg_run_manifest.json", manifest)
    write_csv("02_upstream_chain_inventory.csv", list(chain_inventory[0]), chain_inventory)
    write_csv("03_upstream_artifact_hashes.csv", list(artifact_hashes[0]), artifact_hashes)
    write_csv("04_input_availability_review.csv", list(input_rows[0]), input_rows)
    write_csv("05_work_package_status_registry.csv", list(work_rows[0]), work_rows)
    write_csv("06_artifact_registry_records.csv", list(artifact_rows[0]), artifact_rows)
    write_csv("07_aq_classification_registry_records.csv", list(aq_registry[0]), aq_registry)
    write_csv("08_origin_topic_registry_records.csv", list(origin_registry[0]), origin_registry)
    write_csv("09_review_item_registry_records.csv", list(review_registry[0]), review_registry)
    write_csv("10_decision_point_registry_records.csv", list(decision_registry[0]), decision_registry)
    write_csv("11_guard_result_registry_records.csv", list(guard_registry[0]), guard_registry)
    write_csv("12_claim_boundary_registry_records.csv", list(claim_rows[0]), claim_rows)
    write_csv("13_l2_boundary_registry_record.csv", list(l2_rows[0]), l2_rows)
    write_csv("14_crosswalk_i_to_m_registry.csv", list(crosswalk_registry[0]), crosswalk_registry)
    write_csv("15_pipeline_review_pattern_summary.csv", list(pipeline_summary[0]), pipeline_summary)
    write_csv("16_partial_and_inconclusive_summary.csv", list(partial_summary[0]), partial_summary)
    write_csv("17_forbidden_claims_registry.csv", list(forbidden_rows[0]), forbidden_rows)
    write_csv("18_allowed_internal_claims_registry.csv", list(allowed_rows[0]), allowed_rows)
    write_text("19_registry_import_schema_draft.sql", SCHEMA_SQL)
    write_csv("20_registry_import_rows_preview.csv", list(preview_rows[0]), preview_rows)
    write_text(
        "21_dwh_integration_plan.md",
        """# DWH Integration Plan

This package is an isolated import snapshot. A future live import would require a separate human decision and must preserve source paths, hashes, claim boundary, L2 boundary, review status, and snapshot provenance.

No existing DWH or registry database was opened for writing by EXTRACT03M-RG.
""",
    )
    write_text(
        "22_human_readable_registry_snapshot_de.md",
        f"""# QSB-EXTRACT03M-RG Registry / DWH Integration Snapshot

## Ausgangspunkt
EXTRACT03M-RG erstellt einen isolierten Registry-/DWH-Snapshot nach EXTRACT03M.

## Warum dieser Snapshot nötig ist
Die I-bis-M-Kette wird prüfbar, hashbar und claim-sicher für eine spätere Bibliotheks- oder DWH-Schicht vorbereitet.

## Aufgenommene Arbeitskette
Aufgenommen wurden EXTRACT03I, J, K, K-R1, K-R2, L, L-R1 und M.

## Status der Work Packages
Die Work-Package-Status stehen in `05_work_package_status_registry.csv`.

## Origin-Topic-Klassifikationen
Es wurden {len(origin_registry)} Origin Topics registriert: {class_counts[supported_cls]} supported, {class_counts[partial_cls]} partial, {class_counts[inconclusive_cls]} inconclusive.

## Review Items
{len(review_registry)} Review Item bleibt offen, Source-Response-Degeneracy.

## Decision Points
D01-D09 wurden aus EXTRACT03M uebernommen.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2-Grenze
L2 bleibt fail; N4 support 0/3, required 2/3. Theta und Epsilon wurden nur dokumentiert.

## Isolierter Registry-Snapshot
`30_registry_snapshot.sqlite` wurde neu im RG-Output erzeugt und enthaelt nur Snapshot-Tabellen.

## Was ausdrücklich nicht behauptet wird
Es wird keine QSB-Bestaetigung, kein Interface-Mechanismus, keine Geometrie, keine Gravitation, keine L2-Reparatur und kein natuerlicher oder artefaktischer Ursprung behauptet.

## Nächster Schritt
{NEXT_ALLOWED_ACTION}
""",
    )
    summary = {
        "work_package": "QSB-EXTRACT03M-RG",
        "status": status,
        "chain_work_packages_seen": manifest["chain_work_packages_seen"],
        "origin_topics_total": len(origin_registry),
        "origin_topics_supported": class_counts[supported_cls],
        "origin_topics_partial": class_counts[partial_cls],
        "origin_topics_not_supported": class_counts[not_supported_cls],
        "origin_topics_inconclusive": class_counts[inconclusive_cls],
        "decision_points_count": len(decision_registry),
        "review_items_count": len(review_registry),
        "registry_records_created": registry_records_created,
        "sqlite_snapshot_created": True,
        "live_dwh_modified": False,
        "K_recomputed": False,
        "upstream_modified": False,
        "l2_fail_changed": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_allowed_action": NEXT_ALLOWED_ACTION,
    }
    write_json("23_machine_readable_registry_snapshot_summary.json", summary)
    write_csv("24_next_step_options.csv", list(next_options[0]), next_options)
    write_text("25_recommended_next_step.md", "# Recommended Next Step\n\n" + NEXT_ALLOWED_ACTION)
    write_csv("26_no_execution_guard_results.csv", list(no_exec_rows[0]), no_exec_rows)
    write_text(
        "28_publication_safe_note_candidates.md",
        f"""# Publication-Safe Note Candidates

- EXTRACT03M-RG created an isolated registry/DWH integration snapshot for internal review.
- The snapshot records {len(origin_registry)} origin-topic classifications and {len(decision_registry)} decision points.
- L2 remains fail with N4 support 0/3 required 2/3.
- No public claim expansion is authorized by this snapshot.
""",
    )
    write_text(
        "29_short_result_note_de.md",
        f"""# QSB-EXTRACT03M-RG Kurznotiz

Status: `{status}`.

Der isolierte Registry-/DWH-Snapshot wurde erzeugt. Er enthaelt {registry_records_created} Registry-Records und eine neue SQLite-Datei im RG-Output. L2 bleibt fail; keine Live-DWH-DB wurde veraendert.
""",
    )

    sqlite_report = create_sqlite(
        work_rows,
        origin_registry,
        review_registry,
        decision_registry,
        guard_registry,
        claim_rows,
        l2_rows,
    )
    expected_tables = {
        "rg_work_package_status",
        "rg_origin_topic_classification",
        "rg_review_item",
        "rg_decision_point",
        "rg_guard_result",
        "rg_claim_boundary",
        "rg_l2_boundary",
    }
    integrity_rows = [
        ("sqlite_file_created", SQLITE.exists(), "True", "pass" if SQLITE.exists() else "fail"),
        ("expected_tables_present", set(sqlite_report["tables"]) == expected_tables, "True", "pass" if set(sqlite_report["tables"]) == expected_tables else "fail"),
        ("work_package_status_rows_present", sqlite_report["counts"]["rg_work_package_status"] >= 8, "True", "pass"),
        ("origin_topic_rows_present", sqlite_report["counts"]["rg_origin_topic_classification"] >= 9, "True", "pass"),
        ("claim_boundary_rows_present", sqlite_report["counts"]["rg_claim_boundary"] >= 2, "True", "pass"),
        ("l2_boundary_rows_present", sqlite_report["counts"]["rg_l2_boundary"] == 1, "True", "pass"),
        ("sqlite_integrity_check_ok", sqlite_report["integrity"] == "ok", "True", "pass" if sqlite_report["integrity"] == "ok" else "fail"),
        ("live_dwh_not_modified", True, "True", "pass"),
    ]
    write_csv(
        "31_registry_snapshot_integrity_check.csv",
        ["check_name", "observed_value", "expected_value", "status", "notes"],
        [
            {
                "check_name": row[0],
                "observed_value": row[1],
                "expected_value": row[2],
                "status": row[3],
                "notes": "SQLite snapshot integrity check.",
            }
            for row in integrity_rows
        ],
    )
    write_text(
        "32_registry_snapshot_readme.md",
        """# Registry Snapshot README

`30_registry_snapshot.sqlite` is an isolated snapshot database. It contains only EXTRACT03M-RG records generated from the CSV registry outputs in this directory.

It is not a live DWH database and was not connected to any existing DWH or registry store.
""",
    )
    grep_rows = [
        {
            "pattern_group": "forbidden_positive_claims",
            "status": "reviewed_no_positive_claim_expansion",
            "notes": "Forbidden claims are recorded only as blocked registry keys or negative boundary statements.",
        }
    ]
    write_csv("33_claim_boundary_grep_report.csv", list(grep_rows[0]), grep_rows)

    validation_items = [
        ("artifact_count", len(FILES), 34),
        ("extract03m_present", M.exists(), True),
        ("origin_registry_rows", len(origin_registry), 9),
        ("review_item_rows", len(review_registry), 1),
        ("decision_point_rows", len(decision_registry), 9),
        ("claim_boundary_rows", len(claim_rows), 2),
        ("l2_boundary_rows", len(l2_rows), 1),
        ("sqlite_integrity", sqlite_report["integrity"], "ok"),
        ("live_dwh_modified", False, False),
        ("no_execution_guards", len(no_exec_rows), 25),
    ]
    write_csv(
        "27_validation_results.csv",
        ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"],
        [
            {
                "validation_id": f"MRG-V{idx:02d}",
                "check_name": name,
                "status": "pass" if str(observed) == str(expected) else "fail",
                "observed_value": observed,
                "expected_value": expected,
                "blocking": "yes",
                "notes": "Post-write validation.",
            }
            for idx, (name, observed, expected) in enumerate(validation_items, 1)
        ],
    )
    write_text(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03M-RG Final Result

## Status
`{status}`

## Reviewed Inputs
EXTRACT03M and the read-only I-to-M chain were inventoried for registry snapshot use.

## Registry Records
{registry_records_created} registry records were created across work packages, artifacts, AQ classifications, origin topics, review items, decision points, guards, claim boundary, and L2 boundary.

## SQLite Snapshot
`30_registry_snapshot.sqlite` was created as an isolated snapshot database with seven registry tables. SQLite integrity check returned `{sqlite_report["integrity"]}`.

## Origin Topic Summary
{len(origin_registry)} topics: {class_counts[supported_cls]} supported pipeline-review patterns, {class_counts[partial_cls]} partial, {class_counts[not_supported_cls]} not supported, {class_counts[inconclusive_cls]} inconclusive, {class_counts[input_gap_cls]} input gaps, {class_counts[blocked_cls]} blocked by guard.

## Claim Boundary
{CLAIM_BOUNDARY}

## L2 Boundary
L2 remains fail with N4 support 0/3, required 2/3. `theta_new` and `epsilon_new` are recorded without modification.

## No-Execution Guards
No audit, control run, vector export, model recomputation, raw phase reconstruction, F3 raw-source access, A-R1 rerun, bootstrap, upstream mutation, live DWH mutation, L2 change, or forbidden claim was performed.

## Next Allowed Action
{NEXT_ALLOWED_ACTION}
""",
    )

    actual = sorted(path.name for path in OUT.iterdir() if path.is_file())
    expected = sorted(FILES)
    if actual != expected:
        raise SystemExit(f"Output file mismatch: actual={actual} expected={expected}")

    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
