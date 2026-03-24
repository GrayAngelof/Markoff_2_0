# client/src/view_models/lists.py
"""
View Models для списков (корпуса, этажи, помещения).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class BuildingListItem:
    """Элемент списка корпусов."""
    id: int
    name: str
    floors_count: int


@dataclass(frozen=True, slots=True)
class FloorListItem:
    """Элемент списка этажей."""
    id: int
    number: int
    rooms_count: int


@dataclass(frozen=True, slots=True)
class RoomListItem:
    """Элемент списка помещений."""
    id: int
    number: str
    area: Optional[float] = None
    status_code: Optional[str] = None