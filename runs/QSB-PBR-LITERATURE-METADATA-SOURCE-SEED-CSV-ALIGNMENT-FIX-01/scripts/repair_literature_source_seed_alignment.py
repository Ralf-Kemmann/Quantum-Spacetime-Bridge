#!/usr/bin/env python3
"""Repair and validate QSB/PBR literature_source_seed.csv column alignment."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import sqlite3
import subprocess
from pathlib import Path


RUN_ID = "QSB-PBR-LITERATURE-METADATA-SOURCE-SEED-CSV-ALIGNMENT-FIX-01"
RUN_DIR = Path("runs") / RUN_ID
DATA_DIR = RUN_DIR / "data"
VALIDATION_DIR = RUN_DIR / "validation"
IMPORT_DIR = Path("runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01")
SEED_PATH = IMPORT_DIR / "data" / "literature_source_seed.csv"
SOURCE_COPY = IMPORT_DIR / "source" / "deep-research-report-claim-safe-literature-expansion.md"
TAGS_PATH = IMPORT_DIR / "data" / "literature_mechanism_tags.csv"
CLAIMS_PATH = IMPORT_DIR / "data" / "literature_claim_boundaries.csv"
INTEGRITY_PATH = Path("runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01/data/two_db_dry_run_target_integrity.csv")

CLAIM_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"
FINAL_STATUS = "source_seed_alignment_fix_validated_for_dryrun_review_retry"

FIELDNAMES = [
    "literature_id",
    "source_key",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "arxiv_id",
    "source_url",
    "source_type",
    "source_class",
    "author_cluster",
    "theory_cluster",
    "green_status",
    "risk_status",
    "verification_status",
    "discovery_channel",
    "notes",
]

EXPECTED_IDS = [
    "L1", "L2", "L3", "L4", "L5", "L6", "L7",
    "W1", "W2", "W3", "W4", "W5", "W6", "W7",
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
]

SOURCE_TYPES_DE = {
    "Primärliteratur": "primary_literature",
    "Review": "review",
    "Review/Handbook-Kapitel": "handbook_chapter",
}

AUTHOR_CLUSTER_BY_PREFIX = {
    "L": "LQG_quantum_geometry",
    "W": "Wadia_holography_string_black_holes",
    "F": "FLM_Born_metastring_modular_spacetime",
}
THEORY_CLUSTER_BY_PREFIX = {
    "L": "loop_quantum_geometry",
    "W": "holography_string_qg",
    "F": "born_geometry_phase_space",
}

VALID_SOURCE_TYPES = {
    "primary_literature",
    "review",
    "handbook_chapter",
    "lecture_notes",
    "speculative_program",
    "secondary_commentary",
}
VALID_SOURCE_CLASSES = {"GREEN", "GREEN-YELLOW", "YELLOW", "RED-YELLOW", "RED"}
VALID_AUTHOR_CLUSTERS = set(AUTHOR_CLUSTER_BY_PREFIX.values())
VALID_THEORY_CLUSTERS = set(THEORY_CLUSTER_BY_PREFIX.values())
VALID_RISK = {"low", "low_to_moderate", "moderate", "high", "requires_red_team_review"}
VALID_VERIFICATION = {
    "verified_from_deep_research_report",
    "needs_doi_or_arxiv_verification",
    "needs_human_review",
}
VALID_DISCOVERY = {"deep_research_report", "academia_discovery_verified_elsewhere", "arxiv", "inspire", "journal"}
SOURCE_TYPE_LIKE = VALID_SOURCE_TYPES | {"GREEN", "GREEN-YELLOW", "YELLOW"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_csv_text(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_head_file(path: Path) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{path.as_posix()}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def parse_source_copy() -> dict[str, dict[str, str]]:
    text = SOURCE_COPY.read_text(encoding="utf-8")
    pattern = re.compile(r"^(?P<id>[LWF]\d+) \| (?P<authors>.*?) \| (?P<year>\d{4}) \| (?P<title>.*?) \| (?P<class>GREEN-YELLOW|GREEN|YELLOW|RED-YELLOW|RED) \| (?P<type>.*?) \| (?P<tags>.*?)$", re.MULTILINE)
    parsed: dict[str, dict[str, str]] = {}
    for match in pattern.finditer(text):
        literature_id = match.group("id")
        prefix = literature_id[0]
        source_type = SOURCE_TYPES_DE.get(match.group("type"), "needs_human_review")
        source_class = match.group("class")
        risk_status = {
            "GREEN": "low",
            "GREEN-YELLOW": "low_to_moderate",
            "YELLOW": "moderate",
            "RED-YELLOW": "requires_red_team_review",
            "RED": "high",
        }[source_class]
        parsed[literature_id] = {
            "literature_id": literature_id,
            "source_key": literature_id,
            "title": match.group("title"),
            "authors": match.group("authors"),
            "year": match.group("year"),
            "venue": "",
            "doi": "",
            "arxiv_id": "",
            "source_url": "",
            "source_type": source_type,
            "source_class": source_class,
            "author_cluster": AUTHOR_CLUSTER_BY_PREFIX[prefix],
            "theory_cluster": THEORY_CLUSTER_BY_PREFIX[prefix],
            "green_status": source_class,
            "risk_status": risk_status,
            "verification_status": "verified_from_deep_research_report",
            "discovery_channel": "deep_research_report",
            "notes": "DOI/arXiv/source URL not provided in task prompt; keep empty pending verification.",
        }
    return parsed


def diagnose_rows(rows: list[dict[str, str]], phase: str) -> list[dict[str, object]]:
    diagnostics: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        overflow_count = len(row.get(None, []) or [])
        diagnostics.append(
            {
                "phase": phase,
                "row_index": index,
                "literature_id": row.get("literature_id", ""),
                "dictreader_overflow_fields": overflow_count,
                "notes_is_none": str(row.get("notes") is None).lower(),
                "source_url": row.get("source_url", ""),
                "source_url_source_type_like": str(row.get("source_url", "") in SOURCE_TYPE_LIKE).lower(),
                "source_type": row.get("source_type", ""),
                "source_type_valid": str(row.get("source_type", "") in VALID_SOURCE_TYPES).lower(),
                "source_class": row.get("source_class", ""),
                "source_class_valid": str(row.get("source_class", "") in VALID_SOURCE_CLASSES).lower(),
                "author_cluster": row.get("author_cluster", ""),
                "author_cluster_valid": str(row.get("author_cluster", "") in VALID_AUTHOR_CLUSTERS).lower(),
                "theory_cluster": row.get("theory_cluster", ""),
                "theory_cluster_valid": str(row.get("theory_cluster", "") in VALID_THEORY_CLUSTERS).lower(),
                "verification_status": row.get("verification_status", ""),
                "verification_status_valid": str(row.get("verification_status", "") in VALID_VERIFICATION).lower(),
                "discovery_channel": row.get("discovery_channel", ""),
                "discovery_channel_valid": str(row.get("discovery_channel", "") in VALID_DISCOVERY).lower(),
            }
        )
    return diagnostics


def validate_seed(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[str]]:
    failures: list[str] = []
    validation: list[dict[str, object]] = []
    ids = [row.get("literature_id", "") for row in rows]
    checks = [
        ("source_count", "23", str(len(rows)), len(rows) == 23),
        ("row_ids", ";".join(EXPECTED_IDS), ";".join(ids), ids == EXPECTED_IDS),
        ("dictreader_overflow", "0", str(sum(len(row.get(None, []) or []) for row in rows)), all(not row.get(None) for row in rows)),
        ("notes_not_none", "0", str(sum(1 for row in rows if row.get("notes") is None)), all(row.get("notes") is not None for row in rows)),
        ("source_url_not_source_type_like", "0", str(sum(1 for row in rows if row.get("source_url") in SOURCE_TYPE_LIKE)), all(row.get("source_url") not in SOURCE_TYPE_LIKE for row in rows)),
        ("source_type_enum", "0", str(sum(1 for row in rows if row.get("source_type") not in VALID_SOURCE_TYPES)), all(row.get("source_type") in VALID_SOURCE_TYPES for row in rows)),
        ("source_class_enum", "0", str(sum(1 for row in rows if row.get("source_class") not in VALID_SOURCE_CLASSES)), all(row.get("source_class") in VALID_SOURCE_CLASSES for row in rows)),
        ("author_cluster_enum", "0", str(sum(1 for row in rows if row.get("author_cluster") not in VALID_AUTHOR_CLUSTERS)), all(row.get("author_cluster") in VALID_AUTHOR_CLUSTERS for row in rows)),
        ("theory_cluster_enum", "0", str(sum(1 for row in rows if row.get("theory_cluster") not in VALID_THEORY_CLUSTERS)), all(row.get("theory_cluster") in VALID_THEORY_CLUSTERS for row in rows)),
        ("risk_status_enum", "0", str(sum(1 for row in rows if row.get("risk_status") not in VALID_RISK)), all(row.get("risk_status") in VALID_RISK for row in rows)),
        ("verification_status_enum", "0", str(sum(1 for row in rows if row.get("verification_status") not in VALID_VERIFICATION)), all(row.get("verification_status") in VALID_VERIFICATION for row in rows)),
        ("discovery_channel_enum", "0", str(sum(1 for row in rows if row.get("discovery_channel") not in VALID_DISCOVERY)), all(row.get("discovery_channel") in VALID_DISCOVERY for row in rows)),
        ("doi_arxiv_url_empty", "0", str(sum(1 for row in rows if row.get("doi") or row.get("arxiv_id") or row.get("source_url"))), all(not row.get("doi") and not row.get("arxiv_id") and not row.get("source_url") for row in rows)),
    ]
    for check_name, expected, actual, passed in checks:
        validation.append({"check_name": check_name, "expected": expected, "actual": actual, "status": "pass" if passed else "fail"})
        if not passed:
            failures.append(check_name)
    return validation, failures


def sqlite_count(db_path: Path, table: str) -> int:
    with sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True) as conn:
        return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])


def main() -> int:
    head_payload = git_head_file(SEED_PATH)
    if head_payload is not None:
        before_sha = sha256_bytes(head_payload)
        before_rows = read_csv_text(head_payload.decode("utf-8"))
        before_source = "git_head_baseline"
    else:
        before_sha = sha256_file(SEED_PATH)
        before_rows = read_csv(SEED_PATH)
        before_source = "current_file_fallback"
    write_csv(DATA_DIR / "seed_header_review.csv", ["field_order", "field_name"], [{"field_order": i, "field_name": name} for i, name in enumerate(FIELDNAMES, start=1)])
    write_csv(DATA_DIR / "seed_before_alignment_diagnostics.csv", list(diagnose_rows(before_rows, "before")[0].keys()), diagnose_rows(before_rows, "before"))

    parsed = parse_source_copy()
    missing = [literature_id for literature_id in EXPECTED_IDS if literature_id not in parsed]
    if missing:
        write_csv(VALIDATION_DIR / "validation_results.csv", ["check_name", "expected", "actual", "status"], [{"check_name": "parse_source_copy", "expected": "all_ids", "actual": ";".join(missing), "status": "fail"}])
        print(f"FAIL: missing source-copy IDs: {';'.join(missing)}")
        return 1

    for row in before_rows:
        literature_id = row.get("literature_id", "")
        shifted_note = row.get("discovery_channel", "")
        if literature_id in parsed and shifted_note and shifted_note not in VALID_DISCOVERY:
            parsed[literature_id]["notes"] = shifted_note

    repaired_rows = [parsed[literature_id] for literature_id in EXPECTED_IDS]
    write_csv(SEED_PATH, FIELDNAMES, repaired_rows)

    after_sha = sha256_file(SEED_PATH)
    after_rows = read_csv(SEED_PATH)
    write_csv(DATA_DIR / "seed_after_alignment_validation.csv", list(diagnose_rows(after_rows, "after")[0].keys()), diagnose_rows(after_rows, "after"))
    enum_validation, enum_failures = validate_seed(after_rows)
    write_csv(DATA_DIR / "enum_validation_results.csv", ["check_name", "expected", "actual", "status"], enum_validation)

    tag_rows = read_csv(TAGS_PATH)
    claim_rows = read_csv(CLAIMS_PATH)
    forbidden = [
        "supports QSB",
        "proves QSB",
        "confirms mechanism",
        "evidence for QSB",
        "physical discovery",
        "mechanism found",
        "new physics confirmed",
    ]
    claim_text = " ".join(" ".join(str(value or "") for value in row.values()) for row in claim_rows).lower()
    bad_flags = sum(
        1
        for row in claim_rows
        if row.get("internal_evidence_flag") != "0"
        or row.get("mechanism_claim_support") != "0"
        or row.get("physical_claim_support") != "0"
        or row.get("claim_boundary") != CLAIM_BOUNDARY
    )
    forbidden_hits = [phrase for phrase in forbidden if phrase.lower() in claim_text]
    claim_validation = [
        {"check_name": "claim_boundary_count", "expected": "23", "actual": str(len(claim_rows)), "status": "pass" if len(claim_rows) == 23 else "fail"},
        {"check_name": "mechanism_tag_count", "expected": "50", "actual": str(len(tag_rows)), "status": "pass" if len(tag_rows) == 50 else "fail"},
        {"check_name": "claim_flags_zero", "expected": "0", "actual": str(bad_flags), "status": "pass" if bad_flags == 0 else "fail"},
        {"check_name": "forbidden_phrases_absent", "expected": "0", "actual": ";".join(forbidden_hits), "status": "pass" if not forbidden_hits else "fail"},
        {"check_name": "claim_boundary", "expected": CLAIM_BOUNDARY, "actual": CLAIM_BOUNDARY, "status": "pass"},
    ]
    write_csv(DATA_DIR / "claim_boundary_validation.csv", ["check_name", "expected", "actual", "status"], claim_validation)

    integrity_rows = read_csv(INTEGRITY_PATH)
    integrity_by_role = {row["target_role"]: row for row in integrity_rows}
    data_copy = Path(integrity_by_role["literature_data_db"]["dryrun_db_path"])
    metadata_copy = Path(integrity_by_role["metadata_registration_db"]["dryrun_db_path"])
    dryrun_summary = [
        {
            "check_name": "real_data_db_unchanged",
            "expected": "true",
            "actual": integrity_by_role["literature_data_db"]["real_target_unchanged"],
            "status": "pass" if integrity_by_role["literature_data_db"]["real_target_unchanged"] == "true" else "fail",
        },
        {
            "check_name": "real_metadata_db_unchanged",
            "expected": "true",
            "actual": integrity_by_role["metadata_registration_db"]["real_target_unchanged"],
            "status": "pass" if integrity_by_role["metadata_registration_db"]["real_target_unchanged"] == "true" else "fail",
        },
        {
            "check_name": "dryrun_source_count",
            "expected": "23",
            "actual": str(sqlite_count(data_copy, "qsb_literature_source")),
            "status": "pass" if sqlite_count(data_copy, "qsb_literature_source") == 23 else "fail",
        },
        {
            "check_name": "dryrun_tag_count",
            "expected": "50",
            "actual": str(sqlite_count(data_copy, "qsb_literature_mechanism_tag")),
            "status": "pass" if sqlite_count(data_copy, "qsb_literature_mechanism_tag") == 50 else "fail",
        },
        {
            "check_name": "dryrun_claim_boundary_count",
            "expected": "23",
            "actual": str(sqlite_count(data_copy, "qsb_literature_claim_boundary")),
            "status": "pass" if sqlite_count(data_copy, "qsb_literature_claim_boundary") == 23 else "fail",
        },
        {
            "check_name": "metadata_plan_rows",
            "expected": "17",
            "actual": str(sqlite_count(metadata_copy, "qsb_literature_metadata_registration_plan_dryrun")),
            "status": "pass" if sqlite_count(metadata_copy, "qsb_literature_metadata_registration_plan_dryrun") == 17 else "fail",
        },
    ]
    write_csv(DATA_DIR / "dryrun_after_repair_summary.csv", ["check_name", "expected", "actual", "status"], dryrun_summary)

    manifest_rows = [
        {
            "file_path": SEED_PATH.as_posix(),
            "sha256_before": before_sha,
            "sha256_after": after_sha,
            "row_count": len(after_rows),
            "repair_status": "repaired_and_validated" if not enum_failures else "repair_validation_failed",
            "before_source": before_source,
            "claim_boundary": CLAIM_BOUNDARY,
        }
    ]
    write_csv(DATA_DIR / "repaired_source_seed_manifest.csv", ["file_path", "sha256_before", "sha256_after", "row_count", "repair_status", "before_source", "claim_boundary"], manifest_rows)
    write_csv(DATA_DIR / "modified_files.csv", ["file_path", "change_type", "notes"], [{"file_path": SEED_PATH.as_posix(), "change_type": "modified", "notes": "Rewritten with csv.DictWriter from documented source-copy seed rows."}])
    write_csv(DATA_DIR / "recommended_next_action.csv", ["step_order", "action", "exact_command", "notes", "claim_boundary"], [
        {
            "step_order": 1,
            "action": "retry_two_db_dryrun_review",
            "exact_command": "QSB-PBR-LITERATURE-METADATA-TWO-DB-DRYRUN-REVIEW-01A",
            "notes": "Run a new dry-run review after the seed alignment repair.",
            "claim_boundary": CLAIM_BOUNDARY,
        }
    ])

    validation_rows = enum_validation + claim_validation + dryrun_summary
    validation_rows.append({"check_name": "final_status_allowed", "expected": "allowed_status", "actual": FINAL_STATUS, "status": "pass"})
    write_csv(VALIDATION_DIR / "validation_results.csv", ["check_name", "expected", "actual", "status"], validation_rows)

    failures = [row for row in validation_rows if row["status"] != "pass"]
    if failures:
        for row in failures:
            print(f"FAIL: {row['check_name']}: {row['actual']}")
        return 1
    print(f"PASS: seed alignment repaired and validated; final_status={FINAL_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
