from __future__ import annotations

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.validators import ValidationError, validate_item_input


class ValidatorTests(unittest.TestCase):
    def test_valid_input_is_trimmed(self) -> None:
        data = validate_item_input("  Name  ", "  Text  ", "active")
        self.assertEqual(data.name, "Name")
        self.assertEqual(data.description, "Text")

    def test_name_required(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            validate_item_input(" ", "", "active")
        self.assertIn("name", ctx.exception.errors)

    def test_name_max_length(self) -> None:
        with self.assertRaises(ValidationError):
            validate_item_input("x" * 121, "", "active")

    def test_status_must_be_allowed(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            validate_item_input("Name", "", "unknown")
        self.assertIn("status", ctx.exception.errors)


if __name__ == "__main__":
    unittest.main()
