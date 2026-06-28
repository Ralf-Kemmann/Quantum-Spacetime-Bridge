"""GUI-independent validation logic."""

from __future__ import annotations

from dataclasses import dataclass

from .config import ALLOWED_STATUSES, DESCRIPTION_MAX_LENGTH
from .models import Item


class ValidationError(Exception):
    """Raised when user input violates field-level validation rules."""

    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__("Invalid input")
        self.errors = errors


@dataclass(frozen=True)
class ItemInput:
    name: str
    description: str
    status: str


def validate_item_input(name: str, description: str, status: str) -> ItemInput:
    """Validate raw item input and return normalized values."""
    errors: dict[str, str] = {}
    clean_name = name.strip()
    clean_description = description.strip()
    clean_status = status.strip()

    if not clean_name:
        errors["name"] = "Name ist ein Pflichtfeld."
    elif len(clean_name) > 120:
        errors["name"] = "Name darf maximal 120 Zeichen lang sein."

    if len(clean_description) > DESCRIPTION_MAX_LENGTH:
        errors["description"] = f"Beschreibung darf maximal {DESCRIPTION_MAX_LENGTH} Zeichen lang sein."

    if clean_status not in ALLOWED_STATUSES:
        errors["status"] = "Status muss active, inactive oder archived sein."

    if errors:
        raise ValidationError(errors)
    return ItemInput(name=clean_name, description=clean_description, status=clean_status)


def item_from_input(name: str, description: str, status: str, item_id: int | None = None) -> Item:
    data = validate_item_input(name, description, status)
    return Item(id=item_id, name=data.name, description=data.description, status=data.status)
