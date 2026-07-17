#!/usr/bin/env python3
"""Validate an executed SQLite literature metadata import."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


CLAIM_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"


def scalar(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> int:
    return int(conn.execute(sql, params).fetchone()[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"FAIL: DB path does not exist: {db_path}")
        return 1

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    failures: list[str] = []
    try:
        checks = [
            ("source_count", scalar(conn, "SELECT COUNT(*) FROM qsb_literature_source"), 23),
            ("tag_count_min", scalar(conn, "SELECT COUNT(*) FROM qsb_literature_mechanism_tag"), 50),
            ("claim_boundary_count", scalar(conn, "SELECT COUNT(*) FROM qsb_literature_claim_boundary"), 23),
            ("internal_evidence_nonzero", scalar(conn, "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE internal_evidence_flag <> 0"), 0),
            ("mechanism_claim_nonzero", scalar(conn, "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE mechanism_claim_support <> 0"), 0),
            ("physical_claim_nonzero", scalar(conn, "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE physical_claim_support <> 0"), 0),
            ("wrong_claim_boundary", scalar(conn, "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE claim_boundary <> ?", (CLAIM_BOUNDARY,)), 0),
        ]
        for name, actual, expected in checks:
            if actual != expected:
                failures.append(f"{name}: expected {expected}, observed {actual}")
        missing_tags = scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM qsb_literature_source s
            WHERE NOT EXISTS (
              SELECT 1 FROM qsb_literature_mechanism_tag t
              WHERE t.literature_id = s.literature_id
            )
            """,
        )
        if missing_tags != 0:
            failures.append(f"sources_without_tags: expected 0, observed {missing_tags}")
    finally:
        conn.close()

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: executed literature metadata import validates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
