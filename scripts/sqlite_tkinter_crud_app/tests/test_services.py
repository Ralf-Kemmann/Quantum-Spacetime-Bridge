from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import Database
from src.repository import ItemNotFoundError, ItemRepository
from src.services import ItemService, ValidationError


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        db = Database(Path(self.tmp.name) / "test.db")
        db.initialize()
        self.service = ItemService(ItemRepository(db))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_update_delete_via_service(self) -> None:
        item = self.service.create_item("Alpha", "Text", "active")
        updated = self.service.update_item(item.id or -1, "Beta", "", "inactive")
        self.assertEqual(updated.name, "Beta")
        self.service.delete_item(updated.id or -1)
        with self.assertRaises(ItemNotFoundError):
            self.service.get_item(updated.id or -1)

    def test_invalid_input_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create_item("", "", "active")

    def test_list_items(self) -> None:
        self.service.create_item("Alpha", "needle", "active")
        self.service.create_item("Beta", "", "archived")
        items = self.service.list_items(query="needle", status="active")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "Alpha")


if __name__ == "__main__":
    unittest.main()
