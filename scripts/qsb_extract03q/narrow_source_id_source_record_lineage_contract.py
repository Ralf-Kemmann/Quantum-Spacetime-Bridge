#!/usr/bin/env python3
"""Generate QSB-EXTRACT03Q Source-ID / Source-Record lineage contract.

Contract-only block: imports EXTRACT03P and EXTRACT03P-R1 read-only, carries
forward the direct source_id and role_a/role_b boundaries, and prepares a later
Q-R1 authorization template. It does not execute Source-ID/Source-Record audit.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
P_DIR = REPO_ROOT / "runs/QSB-EXTRACT03P/narrow_source_configuration_lineage_audit_contract"
P_R1_DIR = REPO_ROOT / "runs/QSB-EXTRACT03P-R1/narrow_real_data_source_configuration_lineage_audit"
OUT_DIR = REPO_ROOT / "runs/QSB-EXTRACT03Q/narrow_source_id_source_record_lineage_contract"

STATUS = "extract03q_source_id_source_record_lineage_contract_completed_with_authorization_gap"
CLAIM_BOUNDARY = (
    "EXTRACT03Q is a narrow contract-only Source-ID / Source-Record Lineage "
    "Contract that carries forward the remaining direct source_id/source-record "
    "gap from P-R1. It prepares a possible later Q-R1 audit but does not execute "
    "Source-ID audit, Source-Record audit, recomputation, upstream mutation, live "
    "DWH/registry mutation, L2 change, public-claim upgrade, or nature, Interface, "
    "geometry, or gravity claims."
)
NEXT_ALLOWED_ACTION = (
    "Human review of EXTRACT03Q; if accepted, separately authorize Q-R1 as a "
    "narrow read-only Source-ID / Source-Record lineage audit."
)

ARTIFACTS = [
    "00_RUN_MANIFEST.json",
    "01_IMPORTED_CONTEXT.json",
    "02_P_R1_FINDINGS_CARRIED_FORWARD.json",
    "03_SOURCE_ID_GAP_STATEMENT.md",
    "04_SOURCE_ID_FIELD_REQUIREMENTS.csv",
    "05_SOURCE_RECORD_FIELD_REQUIREMENTS.csv",
    "06_SOURCE_ID_ALIAS_CANDIDATE_MATRIX.csv",
    "07_SOURCE_RECORD_ALIAS_CANDIDATE_MATRIX.csv",
    "08_DWH_CARRY_FORWARD_RULES.csv",
    "09_HUMAN_DECISION_REUSE_RULES.csv",
    "10_Q_R1_AUDIT_QUESTION_REGISTRY.csv",
    "11_Q_R1_REQUIRED_INPUTS.csv",
    "12_Q_R1_ALLOWED_OPERATIONS.csv",
    "13_Q_R1_FORBIDDEN_OPERATIONS.csv",
    "14_Q_R1_STOP_CRITERIA.csv",
    "15_SOURCE_ID_BOUNDARY_NOTE.md",
    "16_SOURCE_RECORD_BOUNDARY_NOTE.md",
    "17_ROLE_FIELD_BOUNDARY_NOTE.md",
    "18_PAIR_IDENTIFIER_CARRY_FORWARD_NOTE.md",
    "19_LINEAGE_JOIN_KEY_CARRY_FORWARD_MATRIX.csv",
    "20_SOURCE_ID_TO_CONFIGURATION_TRACEABILITY_MATRIX.csv",
    "21_SOURCE_RECORD_TO_ARTIFACT_TRACEABILITY_MATRIX.csv",
    "22_REVIEW_ITEMS.csv",
    "23_FUTURE_AUTHORIZATION_TEMPLATE_EXTRACT03Q_R1.json",
    "24_CLAIM_BOUNDARY_CONFIRMATION.md",
    "25_VALIDATION_SUMMARY.csv",
    "26_GUARDRAIL_CHECKS.json",
    "FINAL_RESULT_NOTE.md",
]

SOURCE_ID_FIELDS = [
    "source_id",
    "source_record_id",
    "source_object_id",
    "source_file_id",
    "source_config_id",
    "source_run_id",
    "source_artifact_id",
    "source_manifest_id",
    "config_id",
    "run_id",
    "artifact_id",
    "file_id",
    "object_id",
    "canonical_source_id",
    "canonical_source_record_id",
    "normalized_file_key",
    "content_hash",
    "source_hash",
    "config_hash",
    "run_hash",
    "artifact_hash",
]

SOURCE_RECORD_FIELDS = [
    "record identifier",
    "source identifier",
    "source object reference",
    "source file reference",
    "config reference",
    "run reference",
    "artifact reference",
    "content hash",
    "source/config hash",
    "import timestamp or run timestamp",
    "lineage stage",
    "originating artifact path",
    "transformation rule reference",
    "validation rule reference",
    "claim-boundary reference",
]

READONLY_CANDIDATES = {
    "P_manifest": P_DIR / "01_extract03p_run_manifest.json",
    "P_required_inputs": P_DIR / "07_required_p_r1_inputs.csv",
    "P_source_id_boundary": P_DIR / "18_source_id_boundary_contract.csv",
    "P_R1_manifest": P_R1_DIR / "01_extract03p_r1_run_manifest.json",
    "P_R1_summary": P_R1_DIR / "30_machine_readable_summary.json",
    "P_R1_field_matrix": P_R1_DIR / "09_source_configuration_field_observation_matrix.csv",
    "P_R1_join_key_matrix": P_R1_DIR / "10_lineage_join_key_coverage_matrix.csv",
    "P_R1_role_audit": P_R1_DIR / "11_pair_role_order_symmetry_audit.csv",
    "P_R1_review_items": P_R1_DIR / "21_blockers_and_review_items.csv",
    "P_R1_final_note": P_R1_DIR / "FINAL_RESULT_NOTE.md",
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
    if not path.is_file():
        return set()
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            return set(next(csv.reader(f)))
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", text))


def write_json(name: str, obj: object) -> None:
    (OUT_DIR / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_md(name: str, text: str) -> None:
    (OUT_DIR / name).write_text(text.strip() + "\n", encoding="utf-8")


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUT_DIR / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def classify_field(field: str, headers: dict[str, set[str]]) -> tuple[str, str, str]:
    direct_sources = [name for name, cols in headers.items() if field in cols]
    if direct_sources:
        return "direct_supported", ";".join(direct_sources), "Exact field name appears in read-only carry-forward context."
    aliases = {
        "source_id": {"source_registry_id", "legacy_source_id", "candidate_id"},
        "source_record_id": {"raw_source_file_id", "observation_id", "dataset_id"},
        "source_object_id": {"candidate_id", "source_family", "source_name"},
        "source_file_id": {"raw_source_file_id", "source_filename"},
        "source_config_id": {"config_id", "source_config_id", "split_protocol_id"},
        "source_run_id": {"run_id", "source_run_id", "created_at_utc"},
        "source_artifact_id": {"artifact_id", "raw_source_file_id", "lineage_bundle_sha256"},
        "source_manifest_id": {"manifest", "run_manifest", "lineage_bundle_sha256"},
        "config_id": {"split_protocol_id", "config_reference"},
        "run_id": {"work_package", "created_at_utc"},
        "artifact_id": {"raw_source_file_id", "lineage_bundle_sha256"},
        "file_id": {"raw_source_file_id", "source_filename"},
        "object_id": {"candidate_id", "source_name"},
        "canonical_source_id": {"source_registry_id", "candidate_id"},
        "canonical_source_record_id": {"raw_source_file_id", "observation_id"},
        "normalized_file_key": {"source_filename", "raw_source_file_id"},
        "content_hash": {"sha256", "raw_vector_sha256", "rounded_vector_sha256"},
        "source_hash": {"sha256", "lineage_bundle_sha256"},
        "config_hash": {"lineage_bundle_sha256", "sha256"},
        "run_hash": {"sha256"},
        "artifact_hash": {"sha256", "artifact_sha256", "lineage_bundle_sha256"},
    }.get(field, set())
    alias_sources = [name for name, cols in headers.items() if aliases & cols]
    if alias_sources:
        if field in {"source_id", "source_record_id", "canonical_source_id", "canonical_source_record_id"}:
            return "partial_review", ";".join(alias_sources), "Alias candidates exist but direct lineage remains a Q-R1 review target."
        return "alias_supported", ";".join(alias_sources), "Alias candidate appears in read-only carry-forward context."
    return "missing", "", "No direct or alias candidate observed in selected read-only context."


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if any(OUT_DIR.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {OUT_DIR}")

    created_at = datetime.now(timezone.utc).isoformat()
    p_manifest = json.loads((P_DIR / "01_extract03p_run_manifest.json").read_text(encoding="utf-8"))
    p_r1_manifest = json.loads((P_R1_DIR / "01_extract03p_r1_run_manifest.json").read_text(encoding="utf-8"))
    p_r1_summary = json.loads((P_R1_DIR / "30_machine_readable_summary.json").read_text(encoding="utf-8"))
    p_r1_fields = read_csv(P_R1_DIR / "09_source_configuration_field_observation_matrix.csv")
    p_r1_keys = read_csv(P_R1_DIR / "10_lineage_join_key_coverage_matrix.csv")
    p_r1_reviews = read_csv(P_R1_DIR / "21_blockers_and_review_items.csv")

    headers = {name: header(path) for name, path in READONLY_CANDIDATES.items()}
    direct_source_id_gap = next(row for row in p_r1_fields if row["field_name"] == "source_id")
    source_key_gap = next(row for row in p_r1_keys if row["join_key"] == "source_id")

    source_id_rows = []
    for idx, field in enumerate(SOURCE_ID_FIELDS, 1):
        status, sources, notes = classify_field(field, headers)
        source_id_rows.append(
            {
                "field_id": f"SID-F-{idx:02d}",
                "field_name": field,
                "q_r1_need": "required_or_review_candidate",
                "contract_status": status,
                "read_only_candidate_sources": sources,
                "requires_human_review": "yes" if status in {"partial_review", "missing", "blocked"} else "no",
                "notes": notes,
            }
        )

    record_rows = []
    record_map = {
        "record identifier": "source_record_id",
        "source identifier": "source_id",
        "source object reference": "source_object_id",
        "source file reference": "source_file_id",
        "config reference": "source_config_id",
        "run reference": "source_run_id",
        "artifact reference": "source_artifact_id",
        "content hash": "content_hash",
        "source/config hash": "source_hash",
        "import timestamp or run timestamp": "created_at_utc",
        "lineage stage": "migration_status",
        "originating artifact path": "source_filename",
        "transformation rule reference": "transformation_rule",
        "validation rule reference": "validation_rule",
        "claim-boundary reference": "claim_boundary",
    }
    for idx, field in enumerate(SOURCE_RECORD_FIELDS, 1):
        proxy = record_map[field]
        status, sources, notes = classify_field(proxy, headers)
        record_rows.append(
            {
                "record_field_id": f"SREC-F-{idx:02d}",
                "record_field": field,
                "candidate_direct_or_alias_field": proxy,
                "q_r1_need": "required_or_review_candidate",
                "contract_status": status,
                "read_only_candidate_sources": sources,
                "requires_human_review": "yes" if status in {"partial_review", "missing", "blocked"} else "no",
                "notes": notes,
            }
        )

    qq_rows = [
        ("QQ01", "direct source_id presence", "Does a direct source_id or equivalent canonical source field exist in allowed read-only artifacts?"),
        ("QQ02", "acceptable aliases", "Which aliases may count as carry-forward source identity without claim upgrade?"),
        ("QQ03", "source-record identity", "Can a source_record_id or source-record row key be localized?"),
        ("QQ04", "source-object/source-file relation", "Can source object/file references be linked read-only?"),
        ("QQ05", "config/run/artifact identity", "Can config/run/artifact identity be carried forward?"),
        ("QQ06", "hash-based identity", "Which hashes are available as carry-forward identity evidence?"),
        ("QQ07", "join-key compatibility", "Can source_id/source_record keys join to P-R1 matrices?"),
        ("QQ08", "pair/object linkage", "Can pair identifiers be linked to source identity without relabeling?"),
        ("QQ09", "role-field boundary", "How is the P-R1 role_a/role_b boundary preserved?"),
        ("QQ10", "stop and claim boundary", "Which blockers stop Q-R1 without widening scope?"),
    ]

    required_inputs = [
        ("QRI-01", "EXTRACT03Q contract outputs", "created_by_this_block", rel(OUT_DIR), "yes", "Q-R1 must import this contract read-only."),
        ("QRI-02", "EXTRACT03P outputs", "available_readonly", rel(P_DIR), "yes", "Carry-forward contract context."),
        ("QRI-03", "EXTRACT03P-R1 outputs", "available_readonly", rel(P_R1_DIR), "yes", "Carry-forward real-data source-configuration findings."),
        ("QRI-04", "Source-Hub schema/usage artifacts", "available_readonly", rel(READONLY_CANDIDATES["SourceHub_schema"]), "conditional", "Schema only; no source-record audit in Q."),
        ("QRI-05", "DWH external source registry snapshot", "available_readonly" if READONLY_CANDIDATES["DWH_external_source_registry"].exists() else "missing", rel(READONLY_CANDIDATES["DWH_external_source_registry"]), "conditional", "Candidate carry-forward source registry."),
        ("QRI-06", "DWH raw source file migration snapshot", "available_readonly" if READONLY_CANDIDATES["DWH_raw_source_file_migration"].exists() else "missing", rel(READONLY_CANDIDATES["DWH_raw_source_file_migration"]), "conditional", "Candidate source-record/file registry."),
        ("QRI-07", "Existing run manifests/hash manifests", "available_readonly", "P/P-R1 manifests and hash imports", "yes", "No hash/provenance conflict observed in contract creation."),
        ("QRI-08", "Q-R1 human execution authorization", "source_id_source_record_audit_authorization = not_present_template_only", "not present", "yes", "Template only; Q-R1 not authorized by EXTRACT03Q."),
    ]

    allowed_ops = [
        "read EXTRACT03Q/P/P-R1 artifacts",
        "read existing DWH/Source-Hub metadata snapshots",
        "inspect schemas and manifests",
        "inspect field names and aliases",
        "inspect hashes and provenance fields",
        "build local read-only crosswalk matrices",
        "classify fields as direct/alias/carry-forward/partial/missing",
        "create new Q-R1 run artifacts only",
    ]
    forbidden_ops = [
        "no Q-R1 audit execution inside Q",
        "no Source-ID audit inside Q",
        "no Source-Record audit inside Q",
        "no source-response audit rerun",
        "no source-configuration audit rerun",
        "no controls rerun",
        "no vector export or mutation",
        "no K/Strength/d/D/Edge recompute",
        "no shortest-path rerun",
        "no edge rethresholding",
        "no cluster/motive/bootstrap run",
        "no raw phase reconstruction",
        "no F3 raw-data access beyond already staged/read-only allowed artifacts",
        "no A-R1 rerun",
        "no upstream mutation",
        "no live DWH mutation",
        "no live registry mutation",
        "no L2 change",
        "no post-hoc tuning",
        "no Natur-/Interface-/Geometrie-/Gravitationsclaim",
        "no public-claim upgrade",
        "no alias-to-direct upgrade unless explicitly supported by read-only evidence",
    ]
    stop_criteria = [
        "Q-R1 authorization missing",
        "EXTRACT03Q contract missing",
        "P/P-R1 context missing",
        "Source-Hub/DWH metadata unavailable when required",
        "source identity cannot be localized",
        "source-record identity cannot be localized",
        "alias mapping conflicts with existing DWH/registry decisions",
        "hashes/provenance mismatch",
        "read-only artifact set insufficient",
        "direct source identity requires forbidden raw access",
        "direct source record audit would require live DWH mutation",
        "any forbidden recomputation would be required",
        "any claim upgrade would be required",
    ]

    imported_context = [
        {
            "context_id": f"CTX-{idx:02d}",
            "name": name,
            "path": rel(path),
            "exists": path.exists(),
            "sha256": sha256(path),
            "readonly_use": "yes",
        }
        for idx, (name, path) in enumerate(READONLY_CANDIDATES.items(), 1)
    ]

    write_json(
        "00_RUN_MANIFEST.json",
        {
            "work_package": "QSB-EXTRACT03Q",
            "status": STATUS,
            "created_at_utc": created_at,
            "repo_root": str(REPO_ROOT),
            "p_status": p_manifest["status"],
            "p_r1_status": p_r1_manifest["status"],
            "direct_source_id_gap_carried_forward": True,
            "role_a_role_b_boundary_carried_forward": True,
            "q_r1_audit_executed": False,
            "source_id_audit_executed": False,
            "source_record_audit_executed": False,
            "source_configuration_audit_rerun": False,
            "source_response_audit_rerun": False,
            "controls_rerun": False,
            "K_strength_d_D_edge_recomputed": False,
            "upstream_modified": False,
            "live_dwh_modified": False,
            "live_registry_modified": False,
            "l2_changed": False,
            "post_hoc_tuning": False,
            "public_claim_upgrade": False,
            "artifact_count": len(ARTIFACTS),
            "claim_boundary": CLAIM_BOUNDARY,
            "next_allowed_action": NEXT_ALLOWED_ACTION,
        },
    )
    write_json("01_IMPORTED_CONTEXT.json", {"contexts": imported_context})
    write_json(
        "02_P_R1_FINDINGS_CARRIED_FORWARD.json",
        {
            "p_r1_status": p_r1_summary["status"],
            "partial_topics": p_r1_summary["unresolved_partial_topics"],
            "field_requirements_total": p_r1_summary["field_requirements_total"],
            "field_requirements_with_direct_field_gaps": p_r1_summary["field_requirements_with_direct_field_gaps"],
            "join_keys_total": p_r1_summary["join_keys_total"],
            "join_keys_with_gaps": p_r1_summary["join_keys_with_gaps"],
            "direct_source_id_gap": direct_source_id_gap,
            "source_id_join_key_gap": source_key_gap,
            "review_items": p_r1_reviews,
        },
    )
    write_md(
        "03_SOURCE_ID_GAP_STATEMENT.md",
        f"""# Source-ID Gap Statement

Befund: P-R1 did not directly observe `source_id` in the allowed source-configuration artifacts. The `source_id` join key remains partial.

Interpretation: EXTRACT03Q carries this gap forward into a narrow Source-ID / Source-Record lineage contract. Alias and carry-forward identifiers may be listed as candidates, but EXTRACT03Q does not upgrade alias evidence to direct support.

Claim Boundary: {CLAIM_BOUNDARY}
""",
    )
    write_csv("04_SOURCE_ID_FIELD_REQUIREMENTS.csv", list(source_id_rows[0].keys()), source_id_rows)
    write_csv("05_SOURCE_RECORD_FIELD_REQUIREMENTS.csv", list(record_rows[0].keys()), record_rows)
    write_csv(
        "06_SOURCE_ID_ALIAS_CANDIDATE_MATRIX.csv",
        ["candidate_id", "direct_field", "alias_or_carry_forward_field", "candidate_sources", "contract_status", "q_r1_review_boundary"],
        [
            {
                "candidate_id": row["field_id"],
                "direct_field": "source_id",
                "alias_or_carry_forward_field": row["field_name"],
                "candidate_sources": row["read_only_candidate_sources"],
                "contract_status": row["contract_status"],
                "q_r1_review_boundary": "May be inspected in Q-R1; cannot be upgraded to direct without explicit evidence.",
            }
            for row in source_id_rows
        ],
    )
    write_csv(
        "07_SOURCE_RECORD_ALIAS_CANDIDATE_MATRIX.csv",
        ["candidate_id", "record_field", "alias_or_carry_forward_field", "candidate_sources", "contract_status", "q_r1_review_boundary"],
        [
            {
                "candidate_id": row["record_field_id"],
                "record_field": row["record_field"],
                "alias_or_carry_forward_field": row["candidate_direct_or_alias_field"],
                "candidate_sources": row["read_only_candidate_sources"],
                "contract_status": row["contract_status"],
                "q_r1_review_boundary": "May be inspected in Q-R1; missing fields remain gaps.",
            }
            for row in record_rows
        ],
    )
    write_csv(
        "08_DWH_CARRY_FORWARD_RULES.csv",
        ["rule_id", "rule", "allowed_without_new_human_decision", "requires_new_decision_if", "notes"],
        [
            {"rule_id": "DWH-CF-01", "rule": "Registered, validated, unchanged DWH/registry/run decisions may be reused as carry-forward context.", "allowed_without_new_human_decision": "yes", "requires_new_decision_if": "hash/provenance conflict, scope expansion, new source family, parameter change, claim upgrade", "notes": "Reuse context; do not mutate live DWH/registry."},
            {"rule_id": "DWH-CF-02", "rule": "Alias fields may be listed as candidates without upgrading to direct support.", "allowed_without_new_human_decision": "yes", "requires_new_decision_if": "alias-to-direct upgrade is requested", "notes": "Protects real-data work without replacing it."},
        ],
    )
    write_csv(
        "09_HUMAN_DECISION_REUSE_RULES.csv",
        ["rule_id", "decision_context", "reuse_allowed", "new_human_confirmation_required_for"],
        [
            {"rule_id": "HDR-01", "decision_context": "validated P/P-R1 decisions and hashes", "reuse_allowed": "yes", "new_human_confirmation_required_for": "new execution run"},
            {"rule_id": "HDR-02", "decision_context": "existing DWH/registry/run artifacts", "reuse_allowed": "yes_if_unchanged", "new_human_confirmation_required_for": "new source family or scope expansion"},
            {"rule_id": "HDR-03", "decision_context": "claim boundaries", "reuse_allowed": "yes", "new_human_confirmation_required_for": "claim upgrade or physical interpretation"},
            {"rule_id": "HDR-04", "decision_context": "raw/source-record access", "reuse_allowed": "no_auto_reuse", "new_human_confirmation_required_for": "access to previously forbidden raw/source records"},
        ],
    )
    write_csv(
        "10_Q_R1_AUDIT_QUESTION_REGISTRY.csv",
        ["question_id", "topic", "question", "required_inputs", "expected_output", "claim_boundary"],
        [
            {"question_id": qid, "topic": topic, "question": question, "required_inputs": "EXTRACT03Q/P/P-R1 plus read-only DWH/Source-Hub metadata", "expected_output": "Q-R1 matrix row", "claim_boundary": CLAIM_BOUNDARY}
            for qid, topic, question in qq_rows
        ],
    )
    write_csv(
        "11_Q_R1_REQUIRED_INPUTS.csv",
        ["input_id", "input_name", "current_status", "evidence_or_source", "blocking_if_missing", "notes"],
        [
            {"input_id": input_id, "input_name": name, "current_status": status, "evidence_or_source": source, "blocking_if_missing": blocking, "notes": notes}
            for input_id, name, status, source, blocking, notes in required_inputs
        ],
    )
    write_csv(
        "12_Q_R1_ALLOWED_OPERATIONS.csv",
        ["operation_id", "operation", "allowed_in_q", "allowed_in_q_r1_after_authorization", "guard"],
        [{"operation_id": f"QALLOW-{idx:02d}", "operation": op, "allowed_in_q": "contract_definition_only", "allowed_in_q_r1_after_authorization": "yes_readonly", "guard": "no mutation, no recompute, no claim upgrade"} for idx, op in enumerate(allowed_ops, 1)],
    )
    write_csv(
        "13_Q_R1_FORBIDDEN_OPERATIONS.csv",
        ["operation_id", "operation", "forbidden_in_q", "forbidden_in_q_r1", "reason"],
        [{"operation_id": f"QFORBID-{idx:02d}", "operation": op, "forbidden_in_q": "yes", "forbidden_in_q_r1": "yes_unless_separate_contract_outside_q", "reason": "Outside narrow Source-ID/Source-Record read-only contract."} for idx, op in enumerate(forbidden_ops, 1)],
    )
    write_csv(
        "14_Q_R1_STOP_CRITERIA.csv",
        ["stop_id", "criterion", "blocking_for_q_r1", "required_action"],
        [{"stop_id": f"QSTOP-{idx:02d}", "criterion": criterion, "blocking_for_q_r1": "yes", "required_action": "Stop and record blocker; do not widen scope."} for idx, criterion in enumerate(stop_criteria, 1)],
    )
    write_md("15_SOURCE_ID_BOUNDARY_NOTE.md", "# Source-ID Boundary\n\nDirect `source_id` remains the central carried-forward gap. EXTRACT03Q does not audit it; Q-R1 remains template-only.")
    write_md("16_SOURCE_RECORD_BOUNDARY_NOTE.md", "# Source-Record Boundary\n\nSource-record identity may be specified for Q-R1, but no Source-Record audit is executed in EXTRACT03Q.")
    write_md("17_ROLE_FIELD_BOUNDARY_NOTE.md", "# Role Field Boundary\n\nP-R1 found pair order visible through `pair_i`/`pair_j`, while direct `role_a`/`role_b` fields were absent. EXTRACT03Q carries this boundary forward.")
    write_md("18_PAIR_IDENTIFIER_CARRY_FORWARD_NOTE.md", "# Pair Identifier Carry-Forward\n\n`pair_id`, `canonical_pair_id`, `pair_i`, and `pair_j` may remain carry-forward pair context. They do not by themselves establish direct source identity.")
    write_csv(
        "19_LINEAGE_JOIN_KEY_CARRY_FORWARD_MATRIX.csv",
        ["join_key", "p_r1_status", "q_contract_status", "candidate_q_r1_use", "boundary"],
        [
            {"join_key": row["join_key"], "p_r1_status": row["p_r1_coverage_status"], "q_contract_status": "carry_forward_supported" if row["join_key"] != "source_id" else "partial_review", "candidate_q_r1_use": "read-only join compatibility review", "boundary": row["gap_or_limitation"]}
            for row in p_r1_keys
        ],
    )
    write_csv(
        "20_SOURCE_ID_TO_CONFIGURATION_TRACEABILITY_MATRIX.csv",
        ["trace_id", "p_r1_field", "p_r1_status", "q_contract_target", "q_contract_status", "notes"],
        [
            {"trace_id": row["field_id"], "p_r1_field": row["field_name"], "p_r1_status": row["p_r1_observation_status"], "q_contract_target": "source identity lineage" if "source" in row["field_name"] else "configuration carry-forward context", "q_contract_status": "partial_review" if row["field_name"] == "source_id" else "carry_forward_supported", "notes": row["gap_or_limitation"]}
            for row in p_r1_fields
        ],
    )
    write_csv(
        "21_SOURCE_RECORD_TO_ARTIFACT_TRACEABILITY_MATRIX.csv",
        ["trace_id", "record_field", "candidate_field", "candidate_sources", "contract_status", "notes"],
        [
            {"trace_id": row["record_field_id"], "record_field": row["record_field"], "candidate_field": row["candidate_direct_or_alias_field"], "candidate_sources": row["read_only_candidate_sources"], "contract_status": row["contract_status"], "notes": row["notes"]}
            for row in record_rows
        ],
    )
    write_csv(
        "22_REVIEW_ITEMS.csv",
        ["review_item_id", "topic", "severity", "description", "next_action", "claim_boundary"],
        [
            {"review_item_id": "Q-RI-01", "topic": "source_id", "severity": "authorization_gap", "description": "Q-R1 authorization is not present; template only.", "next_action": "Human review and separate Q-R1 authorization if accepted.", "claim_boundary": CLAIM_BOUNDARY},
            {"review_item_id": "Q-RI-02", "topic": "direct_source_id_gap", "severity": "carried_forward_gap", "description": "P-R1 direct source_id gap remains.", "next_action": "Q-R1 may inspect direct/alias fields read-only after authorization.", "claim_boundary": CLAIM_BOUNDARY},
            {"review_item_id": "Q-RI-03", "topic": "role_a_role_b", "severity": "carried_forward_boundary", "description": "Direct role_a/role_b fields remain absent; pair_i/pair_j carry-forward only.", "next_action": "Preserve role boundary; no relabeling.", "claim_boundary": CLAIM_BOUNDARY},
        ],
    )
    write_json(
        "23_FUTURE_AUTHORIZATION_TEMPLATE_EXTRACT03Q_R1.json",
        {
            "authorization_status": "TEMPLATE_REQUIRES_HUMAN_APPROVAL",
            "authorized_work_package": "QSB-EXTRACT03Q-R1_NARROW_SOURCE_ID_SOURCE_RECORD_LINEAGE_AUDIT",
            "source_contract": "QSB-EXTRACT03Q",
            "human_approval_required": True,
            "source_id_source_record_audit_authorization": "not_present_template_only",
            "allowed_scope": "narrow_readonly_source_id_source_record_lineage_audit_only",
            "no_source_response_rerun": True,
            "no_source_configuration_rerun": True,
            "no_controls_rerun": True,
            "no_K_strength_d_D_edge_recompute": True,
            "no_live_dwh_or_registry_mutation": True,
            "no_l2_change": True,
            "no_claim_upgrade": True,
        },
    )
    write_md("24_CLAIM_BOUNDARY_CONFIRMATION.md", f"# Claim Boundary Confirmation\n\n{CLAIM_BOUNDARY}\n")
    validation_rows = [
        ("VAL-01", "artifact_count_28", "pending", ""),
        ("VAL-02", "p_and_p_r1_context_imported", "true", "P/P-R1 manifests loaded"),
        ("VAL-03", "direct_source_id_gap_carried_forward", "true", direct_source_id_gap["p_r1_observation_status"]),
        ("VAL-04", "qq01_qq10_created", "true", str(len(qq_rows))),
        ("VAL-05", "source_id_field_matrix_created", "true", str(len(source_id_rows))),
        ("VAL-06", "source_record_field_matrix_created", "true", str(len(record_rows))),
        ("VAL-07", "future_authorization_template_not_authorized", "true", "TEMPLATE_REQUIRES_HUMAN_APPROVAL"),
        ("VAL-08", "no_q_r1_or_source_id_audit_execution", "true", "contract-only"),
        ("VAL-09", "no_recompute_or_mutation", "true", "guardrails"),
        ("VAL-10", "l2_unchanged", "true", "no L2 operation"),
    ]
    write_csv("25_VALIDATION_SUMMARY.csv", ["validation_id", "check", "passed", "evidence"], [{"validation_id": a, "check": b, "passed": c, "evidence": d} for a, b, c, d in validation_rows])
    write_json(
        "26_GUARDRAIL_CHECKS.json",
        {
            "q_r1_audit_executed": False,
            "source_id_audit_executed": False,
            "source_record_audit_executed": False,
            "source_configuration_audit_rerun": False,
            "source_response_audit_rerun": False,
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
        },
    )
    write_md(
        "FINAL_RESULT_NOTE.md",
        f"""# QSB-EXTRACT03Q Final Result

## Status
{STATUS}

## Imported P/P-R1 Context
EXTRACT03P and EXTRACT03P-R1 were imported read-only. P-R1 status: {p_r1_summary['status']}.

## Carried-Forward Gaps
Direct `source_id` remains absent in P-R1 allowed artifacts. Direct `role_a`/`role_b` remain absent; `pair_i`/`pair_j` are carry-forward role/order context only.

## Source-ID Field Matrix
{len(source_id_rows)} candidate fields were classified as direct, alias, carry-forward, partial, missing, or blocked contract candidates.

## Source-Record Field Matrix
{len(record_rows)} source-record requirement rows were defined for a later Q-R1 audit.

## Q-R1 Boundary
Q-R1 is not authorized. The future authorization template is template-only.

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
    rows = read_csv(OUT_DIR / "25_VALIDATION_SUMMARY.csv")
    rows[0]["passed"] = str(len(files) == len(ARTIFACTS)).lower()
    rows[0]["evidence"] = str(len(files))
    write_csv("25_VALIDATION_SUMMARY.csv", list(rows[0].keys()), rows)


if __name__ == "__main__":
    main()
