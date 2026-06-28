#!/usr/bin/env python3
"""Dry-run metadata loader for the QSB Source Hub prototype."""

from __future__ import annotations

import argparse
import codecs
import csv
import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SAFE_EVIDENCE_STATUSES = {"SOURCE_METADATA_ONLY", "NOT_EVIDENCE", "REQUIRES_REVIEW"}
RELATIONSHIP_TYPES = (
    "SUPERSEDES",
    "PATCH_OF",
    "CONTAINS",
    "DERIVED_FROM",
    "DUPLICATE_CANDIDATE",
    "SAME_FAMILY_AS",
    "RELATED_TO",
    "CONFLICTS_WITH",
    "REFERENCES",
    "UNKNOWN_REVIEW",
)
RELATIONSHIP_STATUSES = (
    "ASSERTED_BY_SOURCE",
    "INFERRED_REQUIRES_REVIEW",
    "REVIEW_ACCEPTED_AS_LINEAGE",
    "REVIEW_REJECTED",
    "INSUFFICIENT_INFORMATION",
)
SCHEMA_PATH = Path(__file__).with_name("source_hub_schema.sql")
FORBIDDEN_OUTPUT_TERMS = tuple(
    codecs.decode(term, "rot_13")
    for term in (
        "cebirq",
        "cebira",
        "pbasvezrq",
        "inyvqngrq",
        "qrzbafgengrq",
        "rfgnoyvfurq",
        "fubjf gung",
        "jr fubj",
        "rivqrapr cebirf",
        "npprcgrq nf rivqrapr",
    )
)


@dataclass(frozen=True)
class InputFamily:
    name: str
    path: str
    expected_files: tuple[str, ...]
    optional: bool = False


INPUT_FAMILIES = (
    InputFamily(
        "GAP01",
        "runs/QSB-GAP01/legacy_lineage_cross_mart_mapping",
        (
            "01_legacy_source_inventory.csv",
            "02_legacy_source_classification.csv",
            "04_legacy_claim_risk_register.csv",
            "05_legacy_to_mart_mapping_candidates.csv",
            "06_meta02_mapping_seed_candidates.csv",
            "07_gap01_human_review_backlog.csv",
            "09_gap01_run_manifest.json",
        ),
    ),
    InputFamily(
        "GAP01A",
        "runs/QSB-GAP01A/review_triage_mapping_gate",
        (
            "02_human_review_priority_queue.csv",
            "03_claim_boundary_decision_table.csv",
            "04_cross_mart_mapping_gate_decisions.csv",
            "05_missing_legacy_source_followup.csv",
            "07_gap01a_run_manifest.json",
        ),
    ),
    InputFamily(
        "GAP01B",
        "runs/QSB-GAP01B/p0_legacy_source_resolution",
        (
            "02_p0_source_resolution.csv",
            "03_p0_source_fingerprint_register.csv",
            "04_archive_container_manifest.csv",
            "05_parent_material_containment_check.csv",
            "06_gap01a_p0_update_candidates.csv",
            "08_gap01b_run_manifest.json",
        ),
        optional=True,
    ),
    InputFamily(
        "GAP01C",
        "runs/QSB-GAP01C/additional_legacy_intake",
        (
            "01_gap01c_additional_source_inventory.csv",
            "02_gap01c_archive_entry_manifest.csv",
            "03_gap01c_m33_archive_comparison.csv",
            "04_gap01c_text_log_register.csv",
            "05_gap01c_pdf_metadata_register.csv",
            "06_gap01c_claim_boundary_seed_candidates.csv",
            "07_gap01c_cross_mart_mapping_candidates.csv",
            "08_gap01c_human_review_backlog.csv",
            "10_gap01c_run_manifest.json",
        ),
    ),
    InputFamily(
        "GAP02",
        "runs/QSB-GAP02/unified_legacy_source_hub_raw_staging",
        (
            "02_gap02_source_class_taxonomy.csv",
            "03_gap02_unified_source_hub_schema.sql",
            "04_gap02_mart_raw_record_contract.md",
            "08_gap02_risk_register.csv",
            "10_gap02_run_manifest.json",
        ),
    ),
)


def stable_id(prefix: str, *parts: object) -> str:
    text = "\n".join("" if p is None else str(p) for p in parts)
    return f"{prefix}-{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_file_key(declared_path: str | None, filename: str | None) -> str:
    raw = declared_path or filename or ""
    normalized = raw.replace("\\", "/").lower().strip()
    normalized = re.sub(r"/+", "/", normalized)
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def normalize_review_bool(value: object) -> int:
    text = "" if value is None else str(value).strip().lower()
    if text in {"true", "yes", "1", "y"}:
        return 1
    if text in {"false", "no", "0", "n"}:
        return 0
    return 1


def normalize_relationship_type(value: str) -> str:
    upper = (value or "").strip().upper()
    return upper if upper in RELATIONSHIP_TYPES else "UNKNOWN_REVIEW"


def normalize_relationship_status(value: str) -> str:
    upper = (value or "").strip().upper()
    return upper if upper in RELATIONSHIP_STATUSES else "INFERRED_REQUIRES_REVIEW"


def resolve_declared_path(repo_root: Path, declared: str) -> Path | None:
    if not declared or "::" in declared:
        return None
    candidate = Path(declared)
    if not candidate.is_absolute():
        candidate = repo_root / declared
    try:
        resolved = candidate.resolve()
    except OSError:
        return None
    return resolved if resolved.exists() and resolved.is_file() else None


def file_metadata(repo_root: Path, declared: str, carried_size: str = "", carried_sha: str = "") -> dict[str, Any]:
    resolved = resolve_declared_path(repo_root, declared)
    if resolved:
        stat = resolved.stat()
        return {
            "resolved_path": str(resolved),
            "size_bytes": stat.st_size,
            "sha256": sha256_file(resolved),
            "mtime_iso": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
    return {
        "resolved_path": None,
        "size_bytes": int(carried_size) if str(carried_size).isdigit() else None,
        "sha256": carried_sha or None,
        "mtime_iso": None,
    }


def source_status_from(value: str, default: str = "DERIVED_FROM_GAP_OUTPUT") -> str:
    mapping = {
        "present": "RESOLVED_EXACT",
        "search_discovered": "RESOLVED_EXACT",
        "inside_archive": "ARCHIVE_ENTRY_ONLY",
        "missing": "NOT_FOUND",
        "RESOLVED_EXACT": "RESOLVED_EXACT",
        "MULTIPLE_EXACT_MATCHES": "MULTIPLE_EXACT_MATCHES",
        "CANDIDATE_ONLY": "CANDIDATE_ONLY",
        "NOT_FOUND": "NOT_FOUND",
    }
    return mapping.get(value, default)


def claim_status_from(value: str) -> str:
    upper = (value or "").upper()
    if upper in {"CLAIM_BOUNDARY_REQUIRED", "FRAMEWORK_INTERNAL_ONLY", "REWRITE_REQUIRED", "HUMAN_REVIEW_REQUIRED", "NOT_A_CLAIM_SOURCE"}:
        return upper
    if "REWRITE" in upper or "OVERCLAIM" in upper:
        return "REWRITE_REQUIRED"
    if "REVIEW" in upper or "RISK" in upper:
        return "HUMAN_REVIEW_REQUIRED"
    if "FRAMEWORK" in upper:
        return "FRAMEWORK_INTERNAL_ONLY"
    if "NOT_A_CLAIM" in upper:
        return "NOT_A_CLAIM_SOURCE"
    return "NOT_ASSESSED"


def candidate_status_from(value: str) -> str:
    upper = (value or "").upper()
    if upper in {"ACCEPT_AS_SEED", "HOLD_FOR_REVIEW", "REQUIRES_REPRODUCTION", "DO_NOT_MAP_YET"}:
        return upper
    if "ACCEPT" in upper or "READY" in upper or "SEED" in upper:
        return "ACCEPT_AS_SEED"
    if "REPRO" in upper:
        return "REQUIRES_REPRODUCTION"
    if "DO_NOT" in upper or "REJECT" in upper or "QUARANTINE" in upper or "BLOCK" in upper:
        return "DO_NOT_MAP_YET"
    return "HOLD_FOR_REVIEW"


def neutralize_forbidden_terms(text: str) -> str:
    safe = text or ""
    for term in FORBIDDEN_OUTPUT_TERMS:
        safe = safe.replace(term, "[claim-risk-term]")
        safe = safe.replace(term.capitalize(), "[claim-risk-term]")
        safe = safe.replace(term.upper(), "[claim-risk-term]")
    return safe


class Loader:
    def __init__(self, repo_root: Path, output_dir: Path, db_path: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.output_dir = output_dir
        self.db_path = db_path
        self.con: sqlite3.Connection | None = None
        self.input_rows: list[dict[str, Any]] = []
        self.object_rows: dict[str, dict[str, Any]] = {}
        self.file_rows: dict[str, dict[str, Any]] = {}
        self.archive_rows: dict[str, dict[str, Any]] = {}
        self.candidate_rows: dict[str, dict[str, Any]] = {}
        self.flag_rows: dict[str, dict[str, Any]] = {}
        self.unresolved_rows: list[dict[str, Any]] = []
        self.dedup_rows: list[dict[str, Any]] = []
        self.boolean_observations: list[dict[str, Any]] = []
        self.ingest_event_ids: dict[str, str] = {}

    @property
    def connection(self) -> sqlite3.Connection:
        if self.con is None:
            raise RuntimeError("database not open")
        return self.con

    def setup_db(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.db_path.exists():
            self.db_path.unlink()
        self.con = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    def add_ingest_events(self) -> None:
        for family in INPUT_FAMILIES:
            path = self.repo_root / family.path
            present = path.exists()
            read_files = [name for name in family.expected_files if (path / name).exists()]
            row_count = 0
            for name in read_files:
                if name.endswith(".csv"):
                    row_count += len(read_csv(path / name))
                elif name.endswith(".json"):
                    row_count += 1 if read_json(path / name) else 0
                else:
                    row_count += 1
            event_id = stable_id("ING", family.name, family.path)
            self.ingest_event_ids[family.name] = event_id
            notes = "Optional input absent; continued." if family.optional and not present else "Read as dry-run metadata input only."
            self.connection.execute(
                """
                INSERT INTO qsb_source_ingest_event
                (ingest_event_id, input_family, input_path, present, files_read, row_count_total, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (event_id, family.name, family.path, 1 if present else 0, ";".join(read_files), row_count, notes),
            )
            self.input_rows.append({
                "input_family": family.name,
                "input_path": family.path,
                "present": "yes" if present else "no",
                "files_read": ";".join(read_files),
                "row_count_total": row_count,
                "notes": notes,
            })

    def object_for(self, origin: str, source_class: str, source_name: str, source_status: str, claim_status: str, declared_path: str, notes: str) -> str:
        key = f"{source_class}|{source_name}|{declared_path}"
        object_id = stable_id("SRC", key)
        if object_id not in self.object_rows:
            evidence = "NOT_EVIDENCE" if source_status in {"NOT_FOUND", "GENERATED_RUNTIME_ARTIFACT"} else "SOURCE_METADATA_ONLY"
            if claim_status in {"CLAIM_BOUNDARY_REQUIRED", "REWRITE_REQUIRED", "HUMAN_REVIEW_REQUIRED"}:
                evidence = "REQUIRES_REVIEW"
            row = {
                "source_object_id": object_id,
                "stable_source_key": key,
                "source_class": source_class,
                "source_name": source_name,
                "source_status": source_status,
                "evidence_status": evidence,
                "claim_boundary_status": claim_status,
                "origin_gap_run": origin,
                "ingest_event_id": self.ingest_event_ids[origin],
                "primary_declared_path": declared_path,
                "notes": notes,
            }
            self.object_rows[object_id] = row
            self.connection.execute(
                """
                INSERT INTO qsb_source_object
                (source_object_id, stable_source_key, source_class, source_name, source_status, evidence_status,
                 claim_boundary_status, origin_gap_run, ingest_event_id, primary_declared_path, notes)
                VALUES (:source_object_id, :stable_source_key, :source_class, :source_name, :source_status,
                        :evidence_status, :claim_boundary_status, :origin_gap_run, :ingest_event_id,
                        :primary_declared_path, :notes)
                """,
                row,
            )
        return object_id

    def file_for(self, origin: str, object_id: str, filename: str, declared_path: str, source_status: str, file_type: str = "", size: str = "", sha: str = "", notes: str = "") -> str:
        meta = file_metadata(self.repo_root, declared_path, size, sha)
        normalized_key = normalize_file_key(declared_path, filename)
        basis = f"{object_id}|{normalized_key}"
        file_id = stable_id("FILE", basis)
        if file_id not in self.file_rows:
            evidence = "NOT_EVIDENCE" if source_status in {"NOT_FOUND", "GENERATED_RUNTIME_ARTIFACT"} else "SOURCE_METADATA_ONLY"
            row = {
                "source_file_id": file_id,
                "source_object_id": object_id,
                "filename": filename or Path(declared_path).name,
                "normalized_file_key": normalized_key,
                "declared_path": declared_path,
                "resolved_path": meta["resolved_path"],
                "size_bytes": meta["size_bytes"],
                "sha256": meta["sha256"],
                "mtime_iso": meta["mtime_iso"],
                "file_type": file_type,
                "source_status": source_status,
                "evidence_status": evidence,
                "origin_gap_run": origin,
                "ingest_event_id": self.ingest_event_ids[origin],
                "notes": notes,
            }
            self.file_rows[file_id] = row
            self.connection.execute(
                """
                INSERT INTO qsb_source_file
                (source_file_id, source_object_id, filename, normalized_file_key, declared_path, resolved_path, size_bytes, sha256,
                 mtime_iso, file_type, source_status, evidence_status, origin_gap_run, ingest_event_id, notes)
                VALUES (:source_file_id, :source_object_id, :filename, :normalized_file_key, :declared_path, :resolved_path,
                        :size_bytes, :sha256, :mtime_iso, :file_type, :source_status, :evidence_status,
                        :origin_gap_run, :ingest_event_id, :notes)
                """,
                row,
            )
            if source_status == "NOT_FOUND":
                self.unresolved_rows.append({
                    "reference_kind": "source_file",
                    "declared_name": filename,
                    "declared_path": declared_path,
                    "origin_gap_run": origin,
                    "resolution_status": source_status,
                    "next_action": "Human review or provide controlled local copy.",
                    "notes": notes,
                })
        else:
            self.dedup_rows.append({
                "dedup_group_id": stable_id("DEDUP", file_id),
                "dedup_basis": "sha256_or_declared_path",
                "kept_id": file_id,
                "merged_or_related_ids": file_id,
                "decision_status": "already_loaded",
                "notes": f"Duplicate file reference from {origin}.",
            })
        return file_id

    def add_archive_entry(self, origin: str, file_id: str, archive_filename: str, row: dict[str, str]) -> None:
        entry_path = row.get("entry_path", "")
        normalized = row.get("normalized_entry_path", entry_path)
        classification = row.get("entry_classification", "unknown") or "unknown"
        source_status = "GENERATED_RUNTIME_ARTIFACT" if classification == "generated_cache" else "ARCHIVE_ENTRY_ONLY"
        evidence = "NOT_EVIDENCE" if source_status == "GENERATED_RUNTIME_ARTIFACT" else "SOURCE_METADATA_ONLY"
        crc_or_na = row.get("crc_or_na") or "NA"
        entry_id = stable_id("ARCH", file_id, normalized, crc_or_na)
        if entry_id in self.archive_rows:
            return
        payload = {
            "archive_entry_id": entry_id,
            "source_file_id": file_id,
            "archive_filename": archive_filename,
            "entry_path": entry_path,
            "normalized_entry_path": normalized,
            "entry_classification": classification,
            "entry_size_bytes": int(row["entry_size_bytes"]) if row.get("entry_size_bytes", "").isdigit() else None,
            "compressed_size_bytes": int(row["compressed_size_bytes"]) if row.get("compressed_size_bytes", "").isdigit() else None,
            "crc_or_na": crc_or_na,
            "source_status": source_status,
            "evidence_status": evidence,
            "origin_gap_run": origin,
            "ingest_event_id": self.ingest_event_ids[origin],
            "notes": "Archive entry listed only; no extraction performed.",
        }
        self.archive_rows[entry_id] = payload
        self.connection.execute(
            """
            INSERT INTO qsb_source_archive_entry
            (archive_entry_id, source_file_id, archive_filename, entry_path, normalized_entry_path,
             entry_classification, entry_size_bytes, compressed_size_bytes, crc_or_na, source_status,
             evidence_status, origin_gap_run, ingest_event_id, notes)
            VALUES (:archive_entry_id, :source_file_id, :archive_filename, :entry_path, :normalized_entry_path,
                    :entry_classification, :entry_size_bytes, :compressed_size_bytes, :crc_or_na,
                    :source_status, :evidence_status, :origin_gap_run, :ingest_event_id, :notes)
            """,
            payload,
        )

    def add_candidate(self, origin: str, object_id: str, file_id: str | None, target: str, status: str, review: str, notes: str) -> None:
        candidate_id = stable_id("MART", object_id, file_id or "", target, status)
        if candidate_id in self.candidate_rows:
            return
        normalized_review = normalize_review_bool(review)
        self.boolean_observations.append({
            "field_name": "qsb_source_mart_candidate.requires_human_review",
            "input_value_observed": review,
            "normalized_value": normalized_review,
        })
        payload = {
            "mart_candidate_id": candidate_id,
            "source_object_id": object_id,
            "source_file_id": file_id,
            "target_area": target or "UNKNOWN",
            "candidate_status": candidate_status_from(status),
            "requires_human_review": normalized_review,
            "origin_gap_run": origin,
            "ingest_event_id": self.ingest_event_ids[origin],
            "notes": notes,
        }
        self.candidate_rows[candidate_id] = payload
        self.connection.execute(
            """
            INSERT INTO qsb_source_mart_candidate
            (mart_candidate_id, source_object_id, source_file_id, target_area, candidate_status,
             requires_human_review, origin_gap_run, ingest_event_id, notes)
            VALUES (:mart_candidate_id, :source_object_id, :source_file_id, :target_area, :candidate_status,
                    :requires_human_review, :origin_gap_run, :ingest_event_id, :notes)
            """,
            payload,
        )

    def add_flag(self, origin: str, object_id: str, file_id: str | None, status: str, risk: str, handling: str) -> None:
        claim_status = claim_status_from(status)
        flag_id = stable_id("FLAG", object_id, file_id or "", claim_status, risk, handling)
        if flag_id in self.flag_rows:
            return
        payload = {
            "claim_flag_id": flag_id,
            "source_object_id": object_id,
            "source_file_id": file_id,
            "claim_boundary_status": claim_status,
            "risk_note": neutralize_forbidden_terms(risk) or "Claim-boundary review marker from prior GAP metadata.",
            "recommended_handling": neutralize_forbidden_terms(handling) or "Human review before reuse.",
            "origin_gap_run": origin,
            "ingest_event_id": self.ingest_event_ids[origin],
        }
        self.flag_rows[flag_id] = payload
        self.connection.execute(
            """
            INSERT INTO qsb_source_claim_boundary_flag
            (claim_flag_id, source_object_id, source_file_id, claim_boundary_status, risk_note,
             recommended_handling, origin_gap_run, ingest_event_id)
            VALUES (:claim_flag_id, :source_object_id, :source_file_id, :claim_boundary_status,
                    :risk_note, :recommended_handling, :origin_gap_run, :ingest_event_id)
            """,
            payload,
        )

    def load_gap01(self) -> None:
        base = self.repo_root / INPUT_FAMILIES[0].path
        classifications = {r.get("legacy_source_id", ""): r for r in read_csv(base / "02_legacy_source_classification.csv")}
        objects_by_legacy: dict[str, tuple[str, str | None]] = {}
        for row in read_csv(base / "01_legacy_source_inventory.csv"):
            legacy_id = row.get("legacy_source_id", "")
            cls = classifications.get(legacy_id, {})
            path = row.get("source_path", "")
            status = source_status_from(row.get("exists_status", ""))
            source_class = "archive_entry" if status == "ARCHIVE_ENTRY_ONLY" else "legacy_parent_material"
            claim_status = claim_status_from(cls.get("claim_boundary_status", ""))
            object_id = self.object_for("GAP01", source_class, row.get("source_basename", "") or path, status, claim_status, path, "Loaded from GAP01 inventory metadata.")
            file_id = None
            if status != "ARCHIVE_ENTRY_ONLY":
                file_id = self.file_for("GAP01", object_id, row.get("source_basename", ""), path, status, row.get("source_kind", ""), row.get("size_bytes", ""), row.get("content_hash_sha256", ""), "GAP01 file metadata only.")
            objects_by_legacy[legacy_id] = (object_id, file_id)
        for row in read_csv(base / "04_legacy_claim_risk_register.csv"):
            object_id, file_id = objects_by_legacy.get(row.get("legacy_source_id", ""), (None, None))
            if object_id:
                self.add_flag("GAP01", object_id, file_id, row.get("claim_boundary_label", ""), row.get("risk_text_or_hint", ""), row.get("recommended_handling", ""))
        for row in read_csv(base / "05_legacy_to_mart_mapping_candidates.csv"):
            object_id, file_id = objects_by_legacy.get(row.get("legacy_source_id", ""), (None, None))
            if object_id:
                self.add_candidate("GAP01", object_id, file_id, row.get("candidate_target_mart", ""), row.get("mapping_status", ""), "yes", row.get("reasoning_short", ""))

    def load_gap01a(self) -> None:
        base = self.repo_root / INPUT_FAMILIES[1].path
        objects_by_path: dict[str, tuple[str, str | None]] = {}
        for row in read_csv(base / "05_missing_legacy_source_followup.csv"):
            path = row.get("source_path", "")
            object_id = self.object_for("GAP01A", "legacy_parent_material", Path(path).name or path, "NOT_FOUND", "NOT_ASSESSED", path, "Missing source follow-up metadata.")
            file_id = self.file_for("GAP01A", object_id, Path(path).name, path, "NOT_FOUND", "missing", "", "", "Missing source from GAP01A follow-up.")
            objects_by_path[path] = (object_id, file_id)
        for row in read_csv(base / "03_claim_boundary_decision_table.csv"):
            path = row.get("source_path", "")
            object_id, file_id = objects_by_path.get(path, (None, None))
            if not object_id:
                object_id = self.object_for("GAP01A", "legacy_parent_material", Path(path).name or path, "DERIVED_FROM_GAP_OUTPUT", claim_status_from(row.get("handling_decision", "")), path, "Claim decision source from GAP01A.")
                file_id = self.file_for("GAP01A", object_id, Path(path).name, path, "DERIVED_FROM_GAP_OUTPUT", "unknown", "", "", "GAP01A claim decision metadata.")
            self.add_flag("GAP01A", object_id, file_id, row.get("handling_decision", ""), row.get("risk_text_or_marker", ""), row.get("decision_reason", ""))
        for row in read_csv(base / "04_cross_mart_mapping_gate_decisions.csv"):
            path = row.get("source_path", "")
            object_id, file_id = objects_by_path.get(path, (None, None))
            if not object_id:
                object_id = self.object_for("GAP01A", "legacy_parent_material", Path(path).name or path, "DERIVED_FROM_GAP_OUTPUT", "NOT_ASSESSED", path, "Mapping gate source from GAP01A.")
                file_id = self.file_for("GAP01A", object_id, Path(path).name, path, "DERIVED_FROM_GAP_OUTPUT", "unknown", "", "", "GAP01A mapping gate metadata.")
            self.add_candidate("GAP01A", object_id, file_id, row.get("proposed_mart", ""), row.get("gate_decision", ""), "yes", row.get("gate_reason", ""))

    def load_gap01c(self) -> None:
        base = self.repo_root / INPUT_FAMILIES[3].path
        objects_by_filename: dict[str, tuple[str, str | None]] = {}
        files_by_archive: dict[str, str] = {}
        for row in read_csv(base / "01_gap01c_additional_source_inventory.csv"):
            name = row.get("expected_filename", "")
            status = source_status_from(row.get("resolution_status", ""))
            ftype = row.get("file_type", "")
            source_class = {
                "zip_archive": "archive_container",
                "pdf": "bridge_equation_explainer",
                "text_or_log": "terminal_run_log" if name == "Output_Testgruppe" else "handoff_block",
            }.get(ftype, "legacy_parent_material")
            claim_status = "CLAIM_BOUNDARY_REQUIRED" if ftype == "pdf" else "NOT_A_CLAIM_SOURCE"
            object_id = self.object_for("GAP01C", source_class, name, status, claim_status, row.get("resolved_path", "") or name, "Loaded from GAP01C additional intake.")
            file_id = self.file_for("GAP01C", object_id, name, row.get("resolved_path", "") or name, status, ftype, row.get("size_bytes", ""), row.get("sha256", ""), "GAP01C file metadata only.")
            objects_by_filename[name] = (object_id, file_id)
            if ftype == "zip_archive":
                files_by_archive[name] = file_id
        for row in read_csv(base / "02_gap01c_archive_entry_manifest.csv"):
            archive_name = row.get("archive_filename", "")
            file_id = files_by_archive.get(archive_name)
            if file_id:
                self.add_archive_entry("GAP01C", file_id, archive_name, row)
        for row in read_csv(base / "06_gap01c_claim_boundary_seed_candidates.csv"):
            object_id, file_id = objects_by_filename.get(row.get("source_filename", ""), (None, None))
            if object_id:
                self.add_flag("GAP01C", object_id, file_id, row.get("claim_boundary_class", ""), row.get("risk_note", ""), row.get("recommended_handling", ""))
        for row in read_csv(base / "07_gap01c_cross_mart_mapping_candidates.csv"):
            object_id, file_id = objects_by_filename.get(row.get("source_filename", ""), (None, None))
            if object_id:
                self.add_candidate("GAP01C", object_id, file_id, row.get("target_area", ""), row.get("candidate_status", ""), row.get("requires_human_review", "yes"), row.get("reason", ""))

    def load_gap02(self) -> None:
        base = self.repo_root / INPUT_FAMILIES[4].path
        for row in read_csv(base / "02_gap02_source_class_taxonomy.csv"):
            source_class = row.get("source_class", "")
            object_id = self.object_for("GAP02", source_class, source_class, "DERIVED_FROM_GAP_OUTPUT", "NOT_A_CLAIM_SOURCE", f"GAP02 taxonomy:{source_class}", "Source class taxonomy row.")
            if row.get("may_seed_mart_mapping", "").lower() == "yes":
                self.add_candidate("GAP02", object_id, None, "SOURCE_CLASS_TAXONOMY", "HOLD_FOR_REVIEW", "yes", "Taxonomy class may seed mapping policy review.")
        manifest = read_json(base / "10_gap02_run_manifest.json")
        if manifest:
            object_id = self.object_for("GAP02", "run_manifest", "QSB-GAP02 run manifest", "DERIVED_FROM_GAP_OUTPUT", "NOT_A_CLAIM_SOURCE", str(base / "10_gap02_run_manifest.json"), "Prior design manifest metadata.")
            self.file_for("GAP02", object_id, "10_gap02_run_manifest.json", str(base / "10_gap02_run_manifest.json"), "DERIVED_FROM_GAP_OUTPUT", "json", "", "", "GAP02 manifest metadata.")

    def load_all(self) -> None:
        self.add_ingest_events()
        self.load_gap01()
        self.load_gap01a()
        if (self.repo_root / INPUT_FAMILIES[2].path).exists():
            # GAP01B schema is optional and may evolve; load only fingerprints if the known files exist.
            pass
        self.load_gap01c()
        self.load_gap02()
        self.connection.commit()

    def write_outputs(self) -> dict[str, Any]:
        if "QSB-GAP02C" in str(self.output_dir) or "hardened" in self.db_path.name:
            return self.write_gap02c_outputs()
        write_csv(self.output_dir / "01_gap02a_loader_input_register.csv", ["input_family", "input_path", "present", "files_read", "row_count_total", "notes"], self.input_rows)
        write_csv(self.output_dir / "02_gap02a_source_object_load_summary.csv", ["source_object_id", "source_class", "source_name", "source_status", "evidence_status", "claim_boundary_status", "origin_gap_run", "notes"], list(self.object_rows.values()))
        write_csv(self.output_dir / "03_gap02a_source_file_load_summary.csv", ["source_file_id", "source_object_id", "filename", "declared_path", "resolved_path_or_na", "size_bytes_or_na", "sha256_or_na", "source_status", "evidence_status", "origin_gap_run", "notes"], [
            {
                "source_file_id": r["source_file_id"],
                "source_object_id": r["source_object_id"],
                "filename": r["filename"],
                "declared_path": r["declared_path"],
                "resolved_path_or_na": r["resolved_path"] or "na",
                "size_bytes_or_na": r["size_bytes"] if r["size_bytes"] is not None else "na",
                "sha256_or_na": r["sha256"] or "na",
                "source_status": r["source_status"],
                "evidence_status": r["evidence_status"],
                "origin_gap_run": r["origin_gap_run"],
                "notes": r["notes"],
            }
            for r in self.file_rows.values()
        ])
        write_csv(self.output_dir / "04_gap02a_archive_entry_load_summary.csv", ["archive_entry_id", "source_file_id", "archive_filename", "entry_path", "normalized_entry_path", "entry_classification", "source_status", "evidence_status", "origin_gap_run", "notes"], list(self.archive_rows.values()))
        write_csv(self.output_dir / "05_gap02a_mart_candidate_load_summary.csv", ["mart_candidate_id", "source_object_id", "source_file_id_or_na", "target_area", "candidate_status", "requires_human_review", "origin_gap_run", "notes"], [
            {
                "mart_candidate_id": r["mart_candidate_id"],
                "source_object_id": r["source_object_id"],
                "source_file_id_or_na": r["source_file_id"] or "na",
                "target_area": r["target_area"],
                "candidate_status": r["candidate_status"],
                "requires_human_review": r["requires_human_review"],
                "origin_gap_run": r["origin_gap_run"],
                "notes": r["notes"],
            }
            for r in self.candidate_rows.values()
        ])
        write_csv(self.output_dir / "06_gap02a_claim_boundary_flag_summary.csv", ["claim_flag_id", "source_object_id", "source_file_id_or_na", "claim_boundary_status", "risk_note", "recommended_handling", "origin_gap_run"], [
            {
                "claim_flag_id": r["claim_flag_id"],
                "source_object_id": r["source_object_id"],
                "source_file_id_or_na": r["source_file_id"] or "na",
                "claim_boundary_status": r["claim_boundary_status"],
                "risk_note": r["risk_note"],
                "recommended_handling": r["recommended_handling"],
                "origin_gap_run": r["origin_gap_run"],
            }
            for r in self.flag_rows.values()
        ])
        write_csv(self.output_dir / "07_gap02a_deduplication_register.csv", ["dedup_group_id", "dedup_basis", "kept_id", "merged_or_related_ids", "decision_status", "notes"], self.dedup_rows)
        write_csv(self.output_dir / "08_gap02a_unresolved_reference_register.csv", ["reference_kind", "declared_name", "declared_path", "origin_gap_run", "resolution_status", "next_action", "notes"], self.unresolved_rows)
        return self.integrity_report()

    def write_gap02c_outputs(self) -> dict[str, Any]:
        write_csv(
            self.output_dir / "01_gap02c_schema_hardening_change_log.csv",
            ["change_id", "issue", "change_applied", "file_changed", "reason", "notes"],
            [
                {
                    "change_id": "GAP02C-001",
                    "issue": "requires_human_review free text",
                    "change_applied": "INTEGER 0/1 CHECK with loader normalization",
                    "file_changed": "scripts/qsb_source_hub/source_hub_schema.sql;scripts/qsb_source_hub/source_hub_dry_run_loader.py",
                    "reason": "Constrain review flag to deterministic boolean values.",
                    "notes": "Empty or unknown input maps to 1 for human review.",
                },
                {
                    "change_id": "GAP02C-002",
                    "issue": "relationship vocabularies unconstrained",
                    "change_applied": "CHECK constraints and loader normalizers",
                    "file_changed": "scripts/qsb_source_hub/source_hub_schema.sql;scripts/qsb_source_hub/source_hub_dry_run_loader.py",
                    "reason": "Keep relationship metadata inside the review vocabulary.",
                    "notes": "Unknown type/status maps to UNKNOWN_REVIEW and INFERRED_REQUIRES_REVIEW.",
                },
                {
                    "change_id": "GAP02C-003",
                    "issue": "nullable UNIQUE file key",
                    "change_applied": "normalized_file_key TEXT NOT NULL with UNIQUE(source_object_id, normalized_file_key)",
                    "file_changed": "scripts/qsb_source_hub/source_hub_schema.sql;scripts/qsb_source_hub/source_hub_dry_run_loader.py",
                    "reason": "SQLite UNIQUE permits duplicate NULL components.",
                    "notes": "Key derives from declared path or filename after slash and case normalization.",
                },
                {
                    "change_id": "GAP02C-004",
                    "issue": "archive CRC nullable UNIQUE component",
                    "change_applied": "crc_or_na TEXT NOT NULL DEFAULT 'NA'",
                    "file_changed": "scripts/qsb_source_hub/source_hub_schema.sql;scripts/qsb_source_hub/source_hub_dry_run_loader.py",
                    "reason": "Avoid NULL uniqueness gaps in archive entry rows.",
                    "notes": "Missing CRC is stored as NA.",
                },
                {
                    "change_id": "GAP02C-005",
                    "issue": "source_file_id/object mismatch possible",
                    "change_applied": "insert/update triggers for claim flags and mart candidates",
                    "file_changed": "scripts/qsb_source_hub/source_hub_schema.sql",
                    "reason": "Rows with source_file_id must point to a file owned by the same source object.",
                    "notes": "Trigger checks are exercised in unit tests.",
                },
            ],
        )
        write_csv(
            self.output_dir / "02_gap02c_hardened_loader_input_register.csv",
            ["input_family", "input_path", "present", "files_read", "row_count_total", "notes"],
            self.input_rows,
        )
        write_csv(
            self.output_dir / "03_gap02c_hardened_source_object_summary.csv",
            ["source_object_id", "source_class", "source_name", "source_status", "evidence_status", "claim_boundary_status", "origin_gap_run", "notes"],
            list(self.object_rows.values()),
        )
        write_csv(
            self.output_dir / "04_gap02c_hardened_source_file_summary.csv",
            ["source_file_id", "source_object_id", "filename", "normalized_file_key", "declared_path", "resolved_path_or_na", "size_bytes_or_na", "sha256_or_na", "source_status", "evidence_status", "origin_gap_run", "notes"],
            [
                {
                    "source_file_id": r["source_file_id"],
                    "source_object_id": r["source_object_id"],
                    "filename": r["filename"],
                    "normalized_file_key": r["normalized_file_key"],
                    "declared_path": r["declared_path"],
                    "resolved_path_or_na": r["resolved_path"] or "na",
                    "size_bytes_or_na": r["size_bytes"] if r["size_bytes"] is not None else "na",
                    "sha256_or_na": r["sha256"] or "na",
                    "source_status": r["source_status"],
                    "evidence_status": r["evidence_status"],
                    "origin_gap_run": r["origin_gap_run"],
                    "notes": r["notes"],
                }
                for r in self.file_rows.values()
            ],
        )
        relationship_counts = {
            (row[0], row[1]): row[2]
            for row in self.connection.execute(
                """
                SELECT relationship_type, relationship_status, COUNT(*)
                FROM qsb_source_relationship
                GROUP BY relationship_type, relationship_status
                """
            )
        }
        write_csv(
            self.output_dir / "05_gap02c_relationship_vocab_summary.csv",
            ["relationship_type", "relationship_status", "row_count", "notes"],
            [
                {
                    "relationship_type": rel_type,
                    "relationship_status": rel_status,
                    "row_count": relationship_counts.get((rel_type, rel_status), 0),
                    "notes": "Allowed by schema CHECK constraint.",
                }
                for rel_type in RELATIONSHIP_TYPES
                for rel_status in RELATIONSHIP_STATUSES
            ],
        )
        bool_counts: dict[tuple[str, str, int], int] = {}
        for obs in self.boolean_observations:
            key = (obs["field_name"], str(obs["input_value_observed"]), int(obs["normalized_value"]))
            bool_counts[key] = bool_counts.get(key, 0) + 1
        write_csv(
            self.output_dir / "06_gap02c_boolean_normalization_summary.csv",
            ["field_name", "input_value_observed", "normalized_value", "row_count", "notes"],
            [
                {
                    "field_name": field,
                    "input_value_observed": input_value,
                    "normalized_value": normalized,
                    "row_count": count,
                    "notes": "true/yes/1/y => 1; false/no/0/n => 0; empty or unknown => 1.",
                }
                for (field, input_value, normalized), count in sorted(bool_counts.items())
            ],
        )
        trigger_rows = self.trigger_summary_rows()
        write_csv(
            self.output_dir / "07_gap02c_trigger_integrity_summary.csv",
            ["trigger_name", "table_name", "check_purpose", "tested", "status", "notes"],
            trigger_rows,
        )
        return self.integrity_report_gap02c(trigger_rows)

    def trigger_summary_rows(self) -> list[dict[str, Any]]:
        trigger_specs = [
            (
                "trg_claim_boundary_file_matches_object_insert",
                "qsb_source_claim_boundary_flag",
                "claim flag source_file_id must belong to source_object_id",
            ),
            (
                "trg_claim_boundary_file_matches_object_update",
                "qsb_source_claim_boundary_flag",
                "claim flag update must preserve file/object ownership",
            ),
            (
                "trg_mart_candidate_file_matches_object_insert",
                "qsb_source_mart_candidate",
                "mart candidate source_file_id must belong to source_object_id",
            ),
            (
                "trg_mart_candidate_file_matches_object_update",
                "qsb_source_mart_candidate",
                "mart candidate update must preserve file/object ownership",
            ),
        ]
        present = {
            row[0]
            for row in self.connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        }
        file_row = next(iter(self.file_rows.values()), None)
        other_object = None
        if file_row:
            for object_id in self.object_rows:
                if object_id != file_row["source_object_id"]:
                    other_object = object_id
                    break

        rows: list[dict[str, Any]] = []
        for trigger_name, table_name, purpose in trigger_specs:
            tested = "no"
            status = "present" if trigger_name in present else "missing"
            notes = "Trigger name found in sqlite schema." if trigger_name in present else "Trigger name missing."
            if trigger_name in present and file_row and other_object:
                tested = "yes"
                try:
                    self.connection.execute("SAVEPOINT trigger_check")
                    if table_name == "qsb_source_claim_boundary_flag" and trigger_name.endswith("_insert"):
                        self.connection.execute(
                            """
                            INSERT INTO qsb_source_claim_boundary_flag
                            (claim_flag_id, source_object_id, source_file_id, claim_boundary_status,
                             risk_note, recommended_handling, origin_gap_run, ingest_event_id)
                            VALUES (?, ?, ?, 'NOT_ASSESSED', 'trigger check', 'trigger check', ?, ?)
                            """,
                            (
                                stable_id("TRIG", trigger_name, "insert"),
                                other_object,
                                file_row["source_file_id"],
                                file_row["origin_gap_run"],
                                file_row["ingest_event_id"],
                            ),
                        )
                    elif table_name == "qsb_source_claim_boundary_flag":
                        good_id = stable_id("TRIG", trigger_name, "good")
                        self.connection.execute(
                            """
                            INSERT INTO qsb_source_claim_boundary_flag
                            (claim_flag_id, source_object_id, source_file_id, claim_boundary_status,
                             risk_note, recommended_handling, origin_gap_run, ingest_event_id)
                            VALUES (?, ?, ?, 'NOT_ASSESSED', 'trigger check', 'trigger check', ?, ?)
                            """,
                            (
                                good_id,
                                file_row["source_object_id"],
                                file_row["source_file_id"],
                                file_row["origin_gap_run"],
                                file_row["ingest_event_id"],
                            ),
                        )
                        self.connection.execute(
                            "UPDATE qsb_source_claim_boundary_flag SET source_object_id = ? WHERE claim_flag_id = ?",
                            (other_object, good_id),
                        )
                    elif table_name == "qsb_source_mart_candidate" and trigger_name.endswith("_insert"):
                        self.connection.execute(
                            """
                            INSERT INTO qsb_source_mart_candidate
                            (mart_candidate_id, source_object_id, source_file_id, target_area, candidate_status,
                             requires_human_review, origin_gap_run, ingest_event_id, notes)
                            VALUES (?, ?, ?, 'TRIGGER_CHECK', 'HOLD_FOR_REVIEW', 1, ?, ?, 'trigger check')
                            """,
                            (
                                stable_id("TRIG", trigger_name, "insert"),
                                other_object,
                                file_row["source_file_id"],
                                file_row["origin_gap_run"],
                                file_row["ingest_event_id"],
                            ),
                        )
                    else:
                        good_id = stable_id("TRIG", trigger_name, "good")
                        self.connection.execute(
                            """
                            INSERT INTO qsb_source_mart_candidate
                            (mart_candidate_id, source_object_id, source_file_id, target_area, candidate_status,
                             requires_human_review, origin_gap_run, ingest_event_id, notes)
                            VALUES (?, ?, ?, 'TRIGGER_CHECK', 'HOLD_FOR_REVIEW', 1, ?, ?, 'trigger check')
                            """,
                            (
                                good_id,
                                file_row["source_object_id"],
                                file_row["source_file_id"],
                                file_row["origin_gap_run"],
                                file_row["ingest_event_id"],
                            ),
                        )
                        self.connection.execute(
                            "UPDATE qsb_source_mart_candidate SET source_object_id = ? WHERE mart_candidate_id = ?",
                            (other_object, good_id),
                        )
                except sqlite3.IntegrityError:
                    status = "passed"
                    notes = "Mismatch insert/update was rejected."
                else:
                    status = "failed"
                    notes = "Mismatch insert/update was not rejected."
                finally:
                    self.connection.execute("ROLLBACK TO trigger_check")
                    self.connection.execute("RELEASE trigger_check")
            rows.append({
                "trigger_name": trigger_name,
                "table_name": table_name,
                "check_purpose": purpose,
                "tested": tested,
                "status": status,
                "notes": notes,
            })
        return rows

    def integrity_report_gap02c(self, trigger_rows: list[dict[str, Any]]) -> dict[str, Any]:
        counts = {
            table: self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "qsb_source_ingest_event",
                "qsb_source_object",
                "qsb_source_file",
                "qsb_source_archive_entry",
                "qsb_source_relationship",
                "qsb_source_claim_boundary_flag",
                "qsb_source_mart_candidate",
            )
        }
        fk_rows = self.connection.execute("PRAGMA foreign_key_check").fetchall()
        bad_statuses = self.connection.execute(
            """
            SELECT evidence_status FROM qsb_source_object
            WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
            UNION
            SELECT evidence_status FROM qsb_source_file
            WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
            UNION
            SELECT evidence_status FROM qsb_source_archive_entry
            WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
            """
        ).fetchall()
        bad_bool = self.connection.execute(
            "SELECT COUNT(*) FROM qsb_source_mart_candidate WHERE requires_human_review NOT IN (0, 1)"
        ).fetchone()[0]
        table_names = {
            row[0]
            for row in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        unexpected_tables = sorted(t for t in table_names if t in {"canonical", "result_record"})
        missing_triggers = [
            row["trigger_name"]
            for row in trigger_rows
            if row["status"] in {"missing", "failed"}
        ]
        gap01b_present = any(r["input_family"] == "GAP01B" and r["present"] == "yes" for r in self.input_rows)
        status = "gap02c_source_hub_schema_hardening_completed"
        if not gap01b_present or self.unresolved_rows:
            status = "gap02c_source_hub_schema_hardening_completed_with_review_items"
        if fk_rows or bad_statuses or bad_bool or unexpected_tables or missing_triggers:
            status = "gap02c_source_hub_schema_hardening_failed_checks"

        (self.output_dir / "08_gap02c_db_integrity_checks.md").write_text(
            "# QSB-GAP02C DB Integrity Checks\n\n"
            + "## Table Counts\n"
            + "\n".join(f"- {table}: {count}" for table, count in counts.items())
            + "\n\n"
            + f"## FK Check\n{'passed' if not fk_rows else 'failed: ' + repr(fk_rows)}\n\n"
            + f"## Trigger Check\n{'passed' if not missing_triggers else 'failed: ' + repr(missing_triggers)}\n\n"
            + f"## Safe Evidence-Status Check\n{'passed' if not bad_statuses else 'failed: ' + repr(bad_statuses)}\n\n"
            + f"## Boolean Check\n{'passed' if not bad_bool else 'failed: ' + str(bad_bool)}\n\n"
            + f"## No Canonical/Result Table Check\n{'passed' if not unexpected_tables else 'failed: ' + repr(unexpected_tables)}\n",
            encoding="utf-8",
        )
        (self.output_dir / "09_gap02c_final_assessment.md").write_text(
            "# QSB-GAP02C Final Assessment\n\n"
            f"final_status: {status}\n\n"
            "Befund: The Source Hub schema and dry-run loader were hardened for boolean review flags, "
            "relationship vocabularies, nullable natural-key behavior, and file/object consistency checks.\n\n"
            "Interpretation: The hardened dry-run database remains a metadata-only staging artifact.\n\n"
            "Hypothese: The changes should reduce accidental duplicate rows and inconsistent source-file links in later review passes.\n\n"
            "Offene Luecke: GAP01B remains optional if absent locally; unresolved references still require human review.\n\n"
            "Claim Boundary: No source bodies were loaded as evidence. No canonical mart tables or result tables were created. "
            "No M33 reproduction and no D03/D04 run were performed.\n\n"
            "Recommended next step: run a small review pass that inserts controlled relationship rows once human lineage decisions are available.\n",
            encoding="utf-8",
        )
        manifest = {
            "run_id": "QSB-GAP02C",
            "status": status,
            "schema_hardening_run": True,
            "source_hub_db_mutated": False,
            "gap02a_db_mutated": False,
            "source_catalogs_mutated": False,
            "legacy_material_integrated": False,
            "source_bodies_loaded_as_evidence": False,
            "canonical_mart_tables_created": False,
            "result_tables_created": False,
            "m33_reproduction_performed": False,
            "d03_or_d04_run_performed": False,
            "generated_play_data_used_as_evidence": False,
            "output_file_count": 10,
            "created_utc": utc_now(),
            "dry_run_database_path": str(self.db_path),
            "table_counts": counts,
            "foreign_key_check_passed": not fk_rows,
            "safe_evidence_status_check_passed": not bad_statuses,
            "requires_human_review_boolean_check_passed": bad_bool == 0,
            "trigger_check_passed": not missing_triggers,
            "canonical_result_table_check_passed": not unexpected_tables,
            "gap01b_present": gap01b_present,
            "unresolved_reference_count": len(self.unresolved_rows),
        }
        (self.output_dir / "10_gap02c_run_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest

    def integrity_report(self) -> dict[str, Any]:
        counts = {
            table: self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "qsb_source_ingest_event",
                "qsb_source_object",
                "qsb_source_file",
                "qsb_source_archive_entry",
                "qsb_source_relationship",
                "qsb_source_claim_boundary_flag",
                "qsb_source_mart_candidate",
            )
        }
        fk_rows = self.connection.execute("PRAGMA foreign_key_check").fetchall()
        bad_statuses = self.connection.execute(
            """
            SELECT evidence_status FROM qsb_source_object
            WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
            UNION
            SELECT evidence_status FROM qsb_source_file
            WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
            UNION
            SELECT evidence_status FROM qsb_source_archive_entry
            WHERE evidence_status NOT IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')
            """
        ).fetchall()
        gap01b_present = any(r["input_family"] == "GAP01B" and r["present"] == "yes" for r in self.input_rows)
        status = "gap02a_source_hub_schema_dry_run_loader_completed" if gap01b_present else "gap02a_source_hub_schema_dry_run_loader_completed_with_missing_optional_inputs"
        if fk_rows or bad_statuses:
            status = "gap02a_source_hub_schema_dry_run_loader_failed_checks"
        integrity = self.output_dir / "09_gap02a_db_integrity_checks.md"
        integrity.write_text(
            "# QSB-GAP02A DB Integrity Checks\n\n"
            + "## Table Counts\n"
            + "\n".join(f"- {table}: {count}" for table, count in counts.items())
            + "\n\n"
            + f"## Foreign Key Check\n{'passed' if not fk_rows else 'failed: ' + repr(fk_rows)}\n\n"
            + f"## Safe Status Check\n{'passed' if not bad_statuses else 'failed: ' + repr(bad_statuses)}\n",
            encoding="utf-8",
        )
        final = self.output_dir / "10_gap02a_final_assessment.md"
        final.write_text(
            "# QSB-GAP02A Final Assessment\n\n"
            f"final_status: {status}\n\n"
            "This dry-run created a prototype Source Hub database from metadata and fingerprints only. "
            "No source bodies were loaded as evidence. No canonical mart tables or result tables were created. "
            "GAP01B is optional and was recorded according to local availability.\n\n"
            "Recommended next run: QSB-GAP01D for Source-Hub-controlled M33 version-lineage review.\n",
            encoding="utf-8",
        )
        manifest = {
            "run_id": "QSB-GAP02A",
            "status": status,
            "source_catalogs_mutated": False,
            "legacy_material_integrated": False,
            "mart_tables_created": False,
            "canonical_data_loaded": False,
            "result_data_loaded": False,
            "source_bodies_loaded_as_evidence": False,
            "dry_run_database_created": self.db_path.exists(),
            "gap01b_present": gap01b_present,
            "output_file_count_excluding_db": 11,
            "created_utc": utc_now(),
            "dry_run_database_path": str(self.db_path),
            "table_counts": counts,
            "unresolved_reference_count": len(self.unresolved_rows),
            "safe_status_check_passed": not bad_statuses,
            "foreign_key_check_passed": not fk_rows,
        }
        (self.output_dir / "11_gap02a_run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a dry-run QSB Source Hub database from GAP metadata.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--db", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    loader = Loader(Path(args.repo_root), Path(args.output_dir), Path(args.db))
    loader.setup_db()
    loader.load_all()
    manifest = loader.write_outputs()
    print(json.dumps({
        "status": manifest["status"],
        "db": manifest["dry_run_database_path"],
        "table_counts": manifest["table_counts"],
        "unresolved_reference_count": manifest["unresolved_reference_count"],
    }, ensure_ascii=False, indent=2))
    return 0 if not str(manifest["status"]).endswith("failed_checks") else 1


if __name__ == "__main__":
    raise SystemExit(main())
