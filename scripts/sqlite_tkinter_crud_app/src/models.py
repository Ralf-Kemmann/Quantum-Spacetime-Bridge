"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: int | None
    name: str
    description: str
    status: str
    created_at: str | None = None
    updated_at: str | None = None
