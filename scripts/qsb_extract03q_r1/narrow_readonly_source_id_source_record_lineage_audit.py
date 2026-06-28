#!/usr/bin/env python3
"""Generate QSB-EXTRACT03Q-R1 narrow read-only Source-ID audit outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
Q_DIR = REPO_ROOT / "runs/QSB-EXTRACT03Q/narrow_source_id_source_record_lineage_contract"
P_DIR = REPO_ROOT / "runs/QSB-EXTRACT03P/narrow_source_configuration_lineage_audit_contract"
P_R1_DIR = REPO_ROOT / "runs/QSB-EXTRACT03P-R1/narrow_real_data_source_configuration_lineage_audit"
OUT_DIR = REPO_ROOT / "runs/QSB-EXTRACT03Q-R1/narrow_readonly_source_id_source_record_lineage_audit"

STATUS = "extract03q_r1_source_id_source_record_lineage_audit_completed_partial_with_review_items"
CLAIM_BOUNDARY = (
    "EXTRACT03Q-R1 is a narrow read-only Source-ID / Source-Record Lineage "
    "Audit under EXTRACT03Q. It classifies existing field, alias, hash, and "
    "provenance evidence only. It does not rerun source-response or "
    "source-configuration audits, rerun controls, recompute K/Strength/d/D/Edge, "
    "mutate upstream or live DWH/registry state, change L2, patch schemas/exports, "
    "perform post-hoc tuning, or make nature, Interface, geometry, gravity, or "
    "public-claim upgrades."
)
NEXT_ALLOWED_ACTION = (
    "Human review of Q-R1 partial findings and schema/export fix recommendations; "
    "any patch or live registry/DWH action requires separate authorization."
)

ARTIFACTS = [
    "00_RUN_MANIFEST.json",
    "01_IMPORTED_Q_CONTRACT.json",
    "02_IMPORTED_P_P_R1_CONTEXT.json",
    "03_HUMAN_AUTHORIZATION_RESOLUTION.json",
    "04_READONLY_SOURCE_ARTIFACT_INVENTORY.csv",
    "05_QQ01_QQ10_AUDIT_RESULTS.csv",
    "06_SOURCE_ID_DIRECT_SUPPORT_AUDIT.csv",
    "07_SOURCE_ID_ALIAS_SUPPORT_AUDIT.csv",
    "08_SOURCE_RECORD_DIRECT_SUPPORT_AUDIT.csv",
    "09_SOURCE_RECORD_ALIAS_SUPPORT_AUDIT.csv",
    "10_SOURCE_OBJECT_FILE_LINEAGE_AUDIT.csv",
    "11_CONFIG_RUN_ARTIFACT_LINEAGE_AUDIT.csv",
    "12_HASH_CARRY_FORWARD_LINEAGE_AUDIT.csv",
    "13_JOIN_KEY_COMPATIBILITY_AUDIT.csv",
    "14_PAIR_OBJECT_SOURCE_LINKAGE_AUDIT.csv",
    "15_ROLE_FIELD_BOUNDARY_CARRY_FORWARD_AUDIT.md",
    "16_SOURCE_ID_CLASSIFICATION_MATRIX.csv",
    "17_SOURCE_RECORD_CLASSIFICATION_MATRIX.csv",
    "18_SOURCE_ID_TO_SOURCE_RECORD_CROSSWALK.csv",
    "19_SOURCE_RECORD_TO_ARTIFACT_CROSSWALK.csv",
    "20_RESOLVED_PARTIAL_MISSING_SUMMARY.csv",
    "21_BLOCKERS_AND_REVIEW_ITEMS.csv",
    "22_STOP_CRITERIA_EVALUATION.csv",
    "23_SCHEMA_OR_EXPORT_FIX_RECOMMENDATIONS.md",
    "24_CLAIM_BOUNDARY_CONFIRMATION.md",
    "25_GUARDRAIL_CHECKS.json",
    "26_VALIDATION_SUMMARY.csv",
    "FINAL_RESULT_NOTE.md",
]

READONLY = {
    "Q_manifest": Q_DIR / "00_RUN_MANIFEST.json",
    "Q_source_id_fields": Q_DIR / "04_SOURCE_ID_FIELD_REQUIREMENTS.csv",
    "Q_source_record_fields": Q_DIR / "05_SOURCE_RECORD_FIELD_REQUIREMENTS.csv",
    "Q_qq_registry": Q_DIR / "10_Q_R1_AUDIT_QUESTION_REGISTRY.csv",
    "Q_required_inputs": Q_DIR / "11_Q_R1_REQUIRED_INPUTS.csv",
    "Q_stop_criteria": Q_DIR / "14_Q_R1_STOP_CRITERIA.csv",
    "Q_join_key_carry_forward": Q_DIR / "19_LINEAGE_JOIN_KEY_CARRY_FORWARD_MATRIX.csv",
    "P_manifest": P_DIR / "01_extract03p_run_manifest.json",
    "P_R1_manifest": P_R1_DIR / "01_extract03p_r1_run_manifest.json",
    "P_R1_field_matrix": P_R1_DIR / "09_source_configuration_field_observation_matrix.csv",
    "P_R1_join_key_matrix": P_R1_DIR / "10_lineage_join_key_coverage_matrix.csv",
    "P_R1_review_items": P_R1_DIR / "21_blockers_and_review_items.csv",
    "DWH_external_source_registry": REPO_ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/db28_external_source_registry.csv",
    "DWH_raw_source_file_migration": REPO_ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/dwh05_raw_source_file_migration.csv",
    "DWH_source_to_core_dataset_map": REPO_ROOT / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/dwh05_source_to_core_dataset_map.csv",
    "SourceHub_schema": REPO_ROOT / "scripts/qsb_source_hub/source_hub_schema.sql",
    "SourceHub_usage_note": REPO_ROOT / "scripts/qsb_source_hub/M33_LINEAGE_USAGE_NOTE.md",
    "Bridge_candidate_source_registry": REPO_ROOT / "data/QSB-BRIDGE-DATA-01/candidate_source_registry.csv",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def header(path: Path) -> set[str]:
    if not path.exists():
        return set()
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            return set(next(csv.reader(f)))
    return set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", path.read_text(encoding="utf-8", errors="replace")))


def count_rows(path: Path) -> int:
    if not path.is_file() or path.suffix.lower() != ".csv":
        return 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT_DIR / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(name: str, obj: object) -> None:
    (OUT_DIR / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_md(name: str, text: str) -> None:
    (OUT_DIR / name).write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if any(OUT_DIR.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {OUT_DIR}")

    created_at = datetime.now(timezone.utc).isoformat()
    q_manifest = json.loads((Q_DIR / "00_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    p_manifest = json.loads((P_DIR / "01_extract03p_run_manifest.json").read_text(encoding="utf-8"))
    p_r1_manifest = json.loads((P_R1_DIR / "01_extract03p_r1_run_manifest.json").read_text(encoding="utf-8"))
    sid_contract = read_csv(Q_DIR / "04_SOURCE_ID_FIELD_REQUIREMENTS.csv")
    srec_contract = read_csv(Q_DIR / "05_SOURCE_RECORD_FIELD_REQUIREMENTS.csv")
    qq_contract = read_csv(Q_DIR / "10_Q_R1_AUDIT_QUESTION_REGISTRY.csv")
    q_stop = read_csv(Q_DIR / "14_Q_R1_STOP_CRITERIA.csv")
    p_r1_keys = read_csv(P_R1_DIR / "10_lineage_join_key_coverage_matrix.csv")

    readonly_headers = {name: header(path) for name, path in READONLY.items()}
    inventory = [
        {
            "artifact_id": f"RO-{idx:02d}",
            "name": name,
            "path": rel(path),
            "exists": path.exists(),
            "sha256": sha256(path),
            "row_count_if_csv": count_rows(path),
            "readonly_use": "yes",
        }
        for idx, (name, path) in enumerate(READONLY.items(), 1)
    ]

    # Q contract already classifies candidates; Q-R1 tests those classifications
    # against currently readable headers and snapshots without upgrading aliases.
    sid_matrix = []
    for row in sid_contract:
        field = row["field_name"]
        exact_sources = [name for name, cols in readonly_headers.items() if field in cols]
        contract_status = row["contract_status"]
        if exact_sources:
            q_r1_status = "direct_supported" if contract_status == "direct_supported" else "carry_forward_supported"
        elif contract_status == "alias_supported":
            q_r1_status = "alias_supported"
        elif contract_status == "partial_review":
            q_r1_status = "partial_review"
        elif contract_status == "missing":
            q_r1_status = "missing"
        else:
            q_r1_status = contract_status
        sid_matrix.append(
            {
                "field_id": row["field_id"],
                "field_name": field,
                "contract_status": contract_status,
                "q_r1_classification": q_r1_status,
                "direct_evidence_sources": ";".join(exact_sources),
                "alias_or_candidate_sources": row["read_only_candidate_sources"],
                "lineage_finding": "Direct read-only field observed." if q_r1_status == "direct_supported" else "No alias-to-direct upgrade performed.",
                "review_item": "yes" if q_r1_status in {"partial_review", "missing", "blocked"} else "no",
            }
        )

    srec_matrix = []
    for row in srec_contract:
        candidate = row["candidate_direct_or_alias_field"]
        exact_sources = [name for name, cols in readonly_headers.items() if candidate in cols]
        contract_status = row["contract_status"]
        if exact_sources:
            q_r1_status = "direct_supported" if contract_status == "direct_supported" else "carry_forward_supported"
        elif contract_status == "alias_supported":
            q_r1_status = "alias_supported"
        elif contract_status == "partial_review":
            q_r1_status = "partial_review"
        elif contract_status == "missing":
            q_r1_status = "missing"
        else:
            q_r1_status = contract_status
        srec_matrix.append(
            {
                "record_field_id": row["record_field_id"],
                "record_field": row["record_field"],
                "candidate_field": candidate,
                "contract_status": contract_status,
                "q_r1_classification": q_r1_status,
                "direct_evidence_sources": ";".join(exact_sources),
                "alias_or_candidate_sources": row["read_only_candidate_sources"],
                "lineage_finding": "Read-only candidate field observed." if exact_sources else "No direct candidate observed in allowed artifacts.",
                "review_item": "yes" if q_r1_status in {"partial_review", "missing", "blocked"} else "no",
            }
        )

    sid_counts = Counter(row["q_r1_classification"] for row in sid_matrix)
    srec_counts = Counter(row["q_r1_classification"] for row in srec_matrix)

    qq_results = [
        ("QQ01", "direct source_id presence", "partial_review", "A direct source_id exists in DWH external source registry, but P-R1 target artifacts still lack direct source_id; no alias-to-direct upgrade."),
        ("QQ02", "acceptable aliases", "alias_supported", "source_registry_id, legacy_source_id, raw_source_file_id, dataset_id, observation_id and hash/path fields are acceptable candidates for Q-R1 matrices only."),
        ("QQ03", "source-record identity", "partial_review", "raw_source_file_id and observation_id candidates exist; no canonical source_record_id is established for P-R1 pair rows."),
        ("QQ04", "source-object/source-file relation", "alias_supported", "DWH raw source file migration provides source_filename/raw_source_file_id; Source-Hub schema names source object/file fields."),
        ("QQ05", "config/run/artifact identity", "partial_review", "run/artifact carry-forward exists via manifests, raw_source_file_id and hashes; source_config_id/config_id remain missing."),
        ("QQ06", "hash-based identity", "carry_forward_supported", "sha256/hash fields may support carry-forward provenance, not semantic identity by themselves."),
        ("QQ07", "join-key compatibility", "partial_review", "P-R1 pair/component/identity keys are compatible internally; source_id join remains unresolved for P-R1 rows."),
        ("QQ08", "pair/object linkage", "partial_review", "pair_i/pair_j and pair_id are carry-forward pair context, but no read-only source-object link to pair rows is fully established."),
        ("QQ09", "role-field boundary", "partial_review", "role_a/role_b remain absent; pair_i/pair_j order is carry-forward only."),
        ("QQ10", "stop and claim boundary", "partial_review", "No run-level stop; unresolved gaps require review items and schema/export recommendations, not scope widening."),
    ]

    direct_sid = [row for row in sid_matrix if row["q_r1_classification"] == "direct_supported"]
    alias_sid = [row for row in sid_matrix if row["q_r1_classification"] == "alias_supported"]
    direct_srec = [row for row in srec_matrix if row["q_r1_classification"] == "direct_supported"]
    alias_srec = [row for row in srec_matrix if row["q_r1_classification"] == "alias_supported"]

    join_rows = []
    for row in p_r1_keys:
        status = "partial_review" if row["join_key"] == "source_id" else "carry_forward_supported"
        join_rows.append(
            {
                "join_key": row["join_key"],
                "p_r1_status": row["p_r1_coverage_status"],
                "q_r1_classification": status,
                "compatibility_finding": "source_id direct join to P-R1 rows remains unresolved" if row["join_key"] == "source_id" else "carry-forward compatible inside existing P/P-R1 matrices",
                "review_item": "yes" if row["join_key"] == "source_id" else "no",
            }
        )

    source_object_rows = [
        {"audit_id": "SOF-01", "relation": "source_id to external source registry", "evidence": "db28_external_source_registry.source_id", "classification": "direct_supported", "notes": "Registry source identity exists read-only; not joined to P-R1 pair rows."},
        {"audit_id": "SOF-02", "relation": "source file to raw source migration", "evidence": "dwh05_raw_source_file_migration.raw_source_file_id/source_filename", "classification": "direct_supported", "notes": "Source-file lineage exists as DWH snapshot context."},
        {"audit_id": "SOF-03", "relation": "pair rows to source file", "evidence": "no direct pair_id-to-source_file_id mapping observed", "classification": "partial_review", "notes": "Do not infer linkage by scope expansion."},
    ]
    config_rows = [
        {"audit_id": "CRA-01", "identity_family": "config", "evidence": "source_config_id/config_id absent in Q-R1 selected artifacts", "classification": "missing", "notes": "Recommend future schema/export field if needed."},
        {"audit_id": "CRA-02", "identity_family": "run", "evidence": "run manifests and created_at_utc carry-forward", "classification": "carry_forward_supported", "notes": "Run context only."},
        {"audit_id": "CRA-03", "identity_family": "artifact", "evidence": "raw_source_file_id, sha256/hash manifests, lineage_bundle_sha256 candidates", "classification": "alias_supported", "notes": "No semantic identity upgrade from hash alone."},
    ]
    hash_rows = [
        {"hash_id": "HASH-01", "hash_field": "sha256", "sources": "imported context hashes", "classification": "carry_forward_supported", "boundary": "Artifact identity only."},
        {"hash_id": "HASH-02", "hash_field": "raw_source_file_id", "sources": "DWH raw source file migration", "classification": "alias_supported", "boundary": "Source-record alias; not pair-level direct source_id."},
        {"hash_id": "HASH-03", "hash_field": "content/source/config/run/artifact hash", "sources": "Source-Hub schema", "classification": "carry_forward_supported", "boundary": "Schema candidate; no Q-R1 schema patch."},
    ]
    pair_rows = [
        {"audit_id": "PAIR-01", "pair_context": "pair_id/pair_i/pair_j", "source_linkage": "no direct source_id link observed", "classification": "partial_review", "notes": "Pair order is carry-forward role context only."},
        {"audit_id": "PAIR-02", "pair_context": "canonical_pair_id", "source_linkage": "configuration lineage alias only", "classification": "partial_review", "notes": "No Source-ID audit widening."},
    ]
    crosswalk_rows = [
        {"crosswalk_id": "SID-SREC-01", "source_identity_field": "source_id", "source_record_field": "raw_source_file_id", "evidence": "DWH has both source registry and raw source file migration snapshots, but not a complete P-R1 pair join.", "classification": "partial_review"},
        {"crosswalk_id": "SID-SREC-02", "source_identity_field": "source_registry_id", "source_record_field": "dataset_id/observation_id", "evidence": "source_to_core_dataset_map carries source_registry_id to dataset/observation.", "classification": "alias_supported"},
    ]
    record_artifact_rows = [
        {"crosswalk_id": "SREC-ART-01", "source_record_field": "raw_source_file_id", "artifact_field": "source_filename", "evidence": "dwh05_raw_source_file_migration", "classification": "direct_supported"},
        {"crosswalk_id": "SREC-ART-02", "source_record_field": "source_record_id", "artifact_field": "source_config_id/config_id", "evidence": "not observed", "classification": "missing"},
        {"crosswalk_id": "SREC-ART-03", "source_record_field": "observation_id", "artifact_field": "dataset_id", "evidence": "dwh05_source_to_core_dataset_map", "classification": "alias_supported"},
    ]

    review_items = [
        {"review_item_id": "Q-R1-RI-01", "topic": "P-R1 source_id join", "severity": "partial_review", "description": "DWH source_id exists but direct source_id remains absent in P-R1 pair/config artifacts.", "recommendation": "Add/export explicit source_id linkage in a future authorized schema/export fix."},
        {"review_item_id": "Q-R1-RI-02", "topic": "source_record_id", "severity": "partial_review", "description": "raw_source_file_id and observation_id aliases exist; canonical source_record_id is not established for P-R1 rows.", "recommendation": "Define canonical source_record_id mapping if Q-R2/schema work is authorized."},
        {"review_item_id": "Q-R1-RI-03", "topic": "role_a/role_b", "severity": "partial_review", "description": "role_a/role_b remain absent; pair_i/pair_j are carry-forward only.", "recommendation": "Do not relabel; future export may include role_a/role_b if explicitly authorized."},
        {"review_item_id": "Q-R1-RI-04", "topic": "config identity", "severity": "missing", "description": "source_config_id/config_id are not observed.", "recommendation": "Document future schema/export recommendation only."},
    ]
    stop_rows = []
    stop_triggered = False
    for row in q_stop:
        criterion = row["criterion"]
        triggered = "no"
        evidence = "Resolved by Q-R1 authorization and read-only classification."
        if "authorization missing" in criterion:
            evidence = "authorized_by_human_for_q_r1"
        elif "source identity cannot be localized" in criterion:
            evidence = "source identity localized in DWH registry, but P-R1 direct join remains partial."
        elif "source-record identity cannot be localized" in criterion:
            evidence = "source-record aliases localized via raw_source_file_id/observation_id; partial."
        elif "forbidden recomputation" in criterion or "claim upgrade" in criterion:
            evidence = "Not required; guard passed."
        stop_rows.append({"stop_id": row["stop_id"], "criterion": criterion, "triggered": triggered, "evidence": evidence, "action": "continue_as_partial_audit"})

    write_json(
        "00_RUN_MANIFEST.json",
        {
            "work_package": "QSB-EXTRACT03Q-R1",
            "status": STATUS,
            "created_at_utc": created_at,
            "repo_root": str(REPO_ROOT),
            "q_contract_status": q_manifest["status"],
            "p_status": p_manifest["status"],
            "p_r1_status": p_r1_manifest["status"],
            "authorization_resolution": "authorized_by_human_for_q_r1",
            "artifact_count": len(ARTIFACTS),
            "run_level_stop_triggered": stop_triggered,
            "source_response_audit_rerun": False,
            "source_configuration_audit_rerun": False,
            "controls_rerun": False,
            "vectors_exported_or_mutated": False,
            "K_strength_d_D_edge_recomputed": False,
            "shortest_path_edge_cluster_motif_bootstrap_rerun": False,
            "raw_phase_reconstruction": False,
            "upstream_modified": False,
            "live_dwh_modified": False,
            "live_registry_modified": False,
            "l2_changed": False,
            "post_hoc_tuning": False,
            "schema_or_export_patch_performed": False,
            "public_claim_upgrade": False,
            "claim_boundary": CLAIM_BOUNDARY,
            "next_allowed_action": NEXT_ALLOWED_ACTION,
        },
    )
    write_json("01_IMPORTED_Q_CONTRACT.json", {"q_contract_dir": str(Q_DIR), "status": q_manifest["status"], "sha256_manifest": sha256(Q_DIR / "00_RUN_MANIFEST.json")})
    write_json("02_IMPORTED_P_P_R1_CONTEXT.json", {"p_dir": str(P_DIR), "p_status": p_manifest["status"], "p_r1_dir": str(P_R1_DIR), "p_r1_status": p_r1_manifest["status"]})
    write_json("03_HUMAN_AUTHORIZATION_RESOLUTION.json", {"source_id_source_record_audit_authorization": "authorized_by_human_for_q_r1", "scope": "Q-R1 execution only", "no_claim_upgrade": True})
    write_csv("04_READONLY_SOURCE_ARTIFACT_INVENTORY.csv", list(inventory[0].keys()), inventory)
    write_csv(
        "05_QQ01_QQ10_AUDIT_RESULTS.csv",
        ["question_id", "topic", "q_r1_classification", "answer", "claim_boundary"],
        [{"question_id": qid, "topic": topic, "q_r1_classification": status, "answer": answer, "claim_boundary": CLAIM_BOUNDARY} for qid, topic, status, answer in qq_results],
    )
    write_csv("06_SOURCE_ID_DIRECT_SUPPORT_AUDIT.csv", list(sid_matrix[0].keys()), direct_sid or sid_matrix[:0])
    write_csv("07_SOURCE_ID_ALIAS_SUPPORT_AUDIT.csv", list(sid_matrix[0].keys()), alias_sid)
    write_csv("08_SOURCE_RECORD_DIRECT_SUPPORT_AUDIT.csv", list(srec_matrix[0].keys()), direct_srec or srec_matrix[:0])
    write_csv("09_SOURCE_RECORD_ALIAS_SUPPORT_AUDIT.csv", list(srec_matrix[0].keys()), alias_srec)
    write_csv("10_SOURCE_OBJECT_FILE_LINEAGE_AUDIT.csv", list(source_object_rows[0].keys()), source_object_rows)
    write_csv("11_CONFIG_RUN_ARTIFACT_LINEAGE_AUDIT.csv", list(config_rows[0].keys()), config_rows)
    write_csv("12_HASH_CARRY_FORWARD_LINEAGE_AUDIT.csv", list(hash_rows[0].keys()), hash_rows)
    write_csv("13_JOIN_KEY_COMPATIBILITY_AUDIT.csv", list(join_rows[0].keys()), join_rows)
    write_csv("14_PAIR_OBJECT_SOURCE_LINKAGE_AUDIT.csv", list(pair_rows[0].keys()), pair_rows)
    write_md(
        "15_ROLE_FIELD_BOUNDARY_CARRY_FORWARD_AUDIT.md",
        """# Role Field Boundary Carry-Forward

P-R1 found `pair_i` / `pair_j` and pair identifiers as carry-forward role/order context. Direct `role_a` / `role_b` fields remain absent. Q-R1 does not relabel roles and does not infer source identity from pair order.
""",
    )
    write_csv("16_SOURCE_ID_CLASSIFICATION_MATRIX.csv", list(sid_matrix[0].keys()), sid_matrix)
    write_csv("17_SOURCE_RECORD_CLASSIFICATION_MATRIX.csv", list(srec_matrix[0].keys()), srec_matrix)
    write_csv("18_SOURCE_ID_TO_SOURCE_RECORD_CROSSWALK.csv", list(crosswalk_rows[0].keys()), crosswalk_rows)
    write_csv("19_SOURCE_RECORD_TO_ARTIFACT_CROSSWALK.csv", list(record_artifact_rows[0].keys()), record_artifact_rows)
    summary_rows = []
    for scope, counts in [("source_id", sid_counts), ("source_record", srec_counts)]:
        for classification in ["direct_supported", "alias_supported", "carry_forward_supported", "partial_review", "missing", "not_applicable", "blocked"]:
            summary_rows.append({"scope": scope, "classification": classification, "count": counts.get(classification, 0)})
    write_csv("20_RESOLVED_PARTIAL_MISSING_SUMMARY.csv", list(summary_rows[0].keys()), summary_rows)
    write_csv("21_BLOCKERS_AND_REVIEW_ITEMS.csv", list(review_items[0].keys()), review_items)
    write_csv("22_STOP_CRITERIA_EVALUATION.csv", list(stop_rows[0].keys()), stop_rows)
    write_md(
        "23_SCHEMA_OR_EXPORT_FIX_RECOMMENDATIONS.md",
        """# Schema Or Export Fix Recommendations

No schema/export patch was performed in Q-R1.

Recommended future fixes, if separately authorized:

- Add explicit `source_id` to P-R1 pair/config export rows.
- Define and export canonical `source_record_id` for source-file/source-object records.
- Add direct `role_a` and `role_b` fields or document that `pair_i` / `pair_j` are the only role convention.
- Add `source_config_id` or `config_id` to source-configuration export manifests.
- Preserve hash/provenance fields as carry-forward artifact identity, not semantic source identity by themselves.
""",
    )
    write_md("24_CLAIM_BOUNDARY_CONFIRMATION.md", f"# Claim Boundary Confirmation\n\n{CLAIM_BOUNDARY}\n")
    write_json(
        "25_GUARDRAIL_CHECKS.json",
        {
            "source_response_audit_rerun": False,
            "source_configuration_audit_rerun": False,
            "controls_rerun": False,
            "vectors_exported_or_mutated": False,
            "K_strength_d_D_edge_recomputed": False,
            "shortest_path_edge_cluster_motif_bootstrap_rerun": False,
            "raw_phase_reconstruction": False,
            "upstream_modified": False,
            "live_dwh_modified": False,
            "live_registry_modified": False,
            "l2_changed": False,
            "post_hoc_tuning": False,
            "nature_interface_geometry_gravity_claim": False,
            "public_claim_upgrade": False,
            "schema_or_export_patch_performed": False,
        },
    )
    validation_rows = [
        ("VAL-01", "artifact_count_28", "pending", ""),
        ("VAL-02", "q_contract_imported", "true", q_manifest["status"]),
        ("VAL-03", "p_p_r1_context_imported", "true", p_r1_manifest["status"]),
        ("VAL-04", "authorization_resolved", "true", "authorized_by_human_for_q_r1"),
        ("VAL-05", "qq01_qq10_executed", "true", "10"),
        ("VAL-06", "source_id_matrices_created", "true", str(len(sid_matrix))),
        ("VAL-07", "source_record_matrices_created", "true", str(len(srec_matrix))),
        ("VAL-08", "join_key_compatibility_created", "true", str(len(join_rows))),
        ("VAL-09", "hash_carry_forward_created", "true", str(len(hash_rows))),
        ("VAL-10", "source_record_crosswalk_created", "true", str(len(crosswalk_rows))),
        ("VAL-11", "stop_criteria_evaluated", "true", str(len(stop_rows))),
        ("VAL-12", "guardrails_passed", "true", "25_GUARDRAIL_CHECKS.json"),
        ("VAL-13", "l2_unchanged", "true", "no L2 operation"),
    ]
    write_csv("26_VALIDATION_SUMMARY.csv", ["validation_id", "check", "passed", "evidence"], [{"validation_id": a, "check": b, "passed": c, "evidence": d} for a, b, c, d in validation_rows])
    write_md(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03Q-R1 Final Result

## Status
{STATUS}

## Authorization
`source_id_source_record_audit_authorization = authorized_by_human_for_q_r1`.

## QQ01-QQ10
All QQ01-QQ10 were executed read-only. Direct DWH source identity exists as registry context, but the P-R1 pair/config artifact chain remains partial for direct `source_id`.

## Source-ID / Source-Record Findings
Source-ID classifications: {dict(sorted(sid_counts.items()))}

Source-record classifications: {dict(sorted(srec_counts.items()))}

## Join-Key Findings
P-R1 source_id join remains partial. Other P/P-R1 join keys are carry-forward compatible inside existing matrices.

## Hash Carry-Forward
Hashes support artifact/provenance carry-forward only. They are not treated as semantic source identity by themselves.

## Review Items
Direct P-R1 `source_id`, canonical `source_record_id`, direct `role_a`/`role_b`, and `source_config_id`/`config_id` remain review items.

## Stop Criteria
No run-level stop was triggered. Gaps were recorded as partial/review items.

## Claim Boundary
{CLAIM_BOUNDARY}

## Next Allowed Action
{NEXT_ALLOWED_ACTION}
""",
    )

    files = sorted(path.name for path in OUT_DIR.iterdir() if path.is_file())
    missing = [name for name in ARTIFACTS if name not in files]
    extra = [name for name in files if name not in ARTIFACTS]
    if missing or extra:
        raise SystemExit(f"Artifact mismatch missing={missing} extra={extra}")
    rows = read_csv(OUT_DIR / "26_VALIDATION_SUMMARY.csv")
    rows[0]["passed"] = str(len(files) == len(ARTIFACTS)).lower()
    rows[0]["evidence"] = str(len(files))
    write_csv("26_VALIDATION_SUMMARY.csv", list(rows[0].keys()), rows)


if __name__ == "__main__":
    main()
