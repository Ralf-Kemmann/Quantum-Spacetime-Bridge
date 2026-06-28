from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import Database
from src.models import Item
from src.repository import DuplicateNameError, ItemNotFoundError, ItemRepository


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "test.db")
        self.db.initialize()
        self.repo = ItemRepository(self.db)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_and_read_item(self) -> None:
        created = self.repo.create(Item(None, "Alpha", "Description", "active"))
        loaded = self.repo.get(created.id or -1)
        self.assertEqual(loaded.name, "Alpha")
        self.assertIsNotNone(loaded.created_at)

    def test_update_item(self) -> None:
        created = self.repo.create(Item(None, "Alpha", "", "active"))
        updated = self.repo.update(Item(created.id, "Beta", "New", "inactive"))
        self.assertEqual(updated.name, "Beta")
        self.assertEqual(updated.status, "inactive")

    def test_delete_item(self) -> None:
        created = self.repo.create(Item(None, "Alpha", "", "active"))
        self.repo.delete(created.id or -1)
        with self.assertRaises(ItemNotFoundError):
            self.repo.get(created.id or -1)

    def test_search_and_status_filter(self) -> None:
        self.repo.create(Item(None, "Alpha", "needle", "active"))
        self.repo.create(Item(None, "Beta", "other", "archived"))
        result = self.repo.search(query="needle", status="active")
        self.assertEqual([item.name for item in result], ["Alpha"])

    def test_duplicate_name(self) -> None:
        self.repo.create(Item(None, "Alpha", "", "active"))
        with self.assertRaises(DuplicateNameError):
            self.repo.create(Item(None, "Alpha", "", "inactive"))

    def test_missing_id(self) -> None:
        with self.assertRaises(ItemNotFoundError):
            self.repo.get(999)


if __name__ == "__main__":
    unittest.main()
