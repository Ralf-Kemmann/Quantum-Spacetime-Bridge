"""Business logic layer for items."""

from __future__ import annotations

from .models import Item
from .repository import DuplicateNameError, ItemNotFoundError, ItemRepository
from .validators import ValidationError, item_from_input


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository

    def create_item(self, name: str, description: str, status: str) -> Item:
        return self.repository.create(item_from_input(name, description, status))

    def update_item(self, item_id: int, name: str, description: str, status: str) -> Item:
        return self.repository.update(item_from_input(name, description, status, item_id=item_id))

    def delete_item(self, item_id: int) -> None:
        self.repository.delete(item_id)

    def get_item(self, item_id: int) -> Item:
        return self.repository.get(item_id)

    def list_items(self, query: str = "", status: str = "", sort_by: str = "name", descending: bool = False) -> list[Item]:
        return self.repository.search(query=query, status=status, sort_by=sort_by, descending=descending)


__all__ = ["DuplicateNameError", "ItemNotFoundError", "ItemService", "ValidationError"]
