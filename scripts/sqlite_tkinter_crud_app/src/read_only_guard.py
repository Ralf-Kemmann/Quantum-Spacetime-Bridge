"""Runtime guard for read-only SQL statements."""

from __future__ import annotations

import re


class ReadOnlyGuardError(Exception):
    """Raised when a statement is not allowed in the browser."""


WRITE_TOKENS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "REPLACE",
    "CREATE",
    "DROP",
    "ALTER",
    "VACUUM",
    "ATTACH",
    "DETACH",
    "REINDEX",
    "ANALYZE",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "RELEASE",
}

ALLOWED_PRAGMAS = {
    "table_info",
    "index_list",
    "index_info",
    "foreign_key_list",
    "database_list",
    "foreign_keys",
    "query_only",
    "integrity_check",
    "quick_check",
}


def strip_sql_comments(sql: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    text = re.sub(r"--.*?$", " ", text, flags=re.MULTILINE)
    return text.strip()


def assert_read_only_sql(sql: str) -> None:
    """Allow SELECT/WITH and safe introspection PRAGMAs only."""
    normalized = strip_sql_comments(sql)
    if not normalized:
        raise ReadOnlyGuardError("Leere SQL-Anweisung ist nicht erlaubt.")
    statements = [part.strip() for part in normalized.split(";") if part.strip()]
    if len(statements) != 1:
        raise ReadOnlyGuardError("Mehrere SQL-Anweisungen sind nicht erlaubt.")
    statement = statements[0]
    upper = statement.upper()
    first = upper.split(None, 1)[0]
    if any(re.search(rf"\b{token}\b", upper) for token in WRITE_TOKENS):
        raise ReadOnlyGuardError("Schreibende oder schemaändernde SQL-Anweisung wurde blockiert.")
    if first in {"SELECT", "WITH"}:
        return
    if first == "PRAGMA":
        if "=" in statement:
            raise ReadOnlyGuardError("PRAGMA-Zuweisungen sind nicht erlaubt.")
        match = re.match(r"PRAGMA\s+([A-Za-z_][A-Za-z0-9_]*)", statement, flags=re.IGNORECASE)
        pragma_name = match.group(1).casefold() if match else ""
        if pragma_name in ALLOWED_PRAGMAS:
            return
    raise ReadOnlyGuardError("Nur SELECT, WITH und sichere PRAGMA-Introspektion sind erlaubt.")
