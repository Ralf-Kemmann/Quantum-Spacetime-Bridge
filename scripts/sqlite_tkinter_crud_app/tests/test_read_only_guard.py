from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.read_only_guard import ReadOnlyGuardError, assert_read_only_sql


class ReadOnlyGuardTests(unittest.TestCase):
    def test_select_and_with_allowed(self) -> None:
        assert_read_only_sql("SELECT * FROM meta_object")
        assert_read_only_sql("WITH x AS (SELECT 1) SELECT * FROM x")

    def test_safe_pragma_allowed(self) -> None:
        assert_read_only_sql('PRAGMA table_info("meta_object")')

    def test_write_statements_rejected(self) -> None:
        for sql in [
            "INSERT INTO x VALUES (1)",
            "UPDATE x SET a=1",
            "DELETE FROM x",
            "CREATE TABLE x(id)",
            "DROP TABLE x",
            "PRAGMA query_only = OFF",
        ]:
            with self.subTest(sql=sql):
                with self.assertRaises(ReadOnlyGuardError):
                    assert_read_only_sql(sql)

    def test_multiple_statements_rejected(self) -> None:
        with self.assertRaises(ReadOnlyGuardError):
            assert_read_only_sql("SELECT 1; SELECT 2")


if __name__ == "__main__":
    unittest.main()
