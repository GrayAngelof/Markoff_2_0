# client/src/models/room.py
"""
Модель данных для помещения на стороне клиента.

Чистый DTO — только данные от API, никакой UI-логики.
Соответствует RoomTreeResponse и RoomDetailResponse из бекенда.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== МОДЕЛИ =====
@dataclass(frozen=True, kw_only=True)
class Room(BaseDTO, DateTimeMixin):
    """Модель помещения (DTO)."""

    NODE_TYPE = "room"

    number: str
    floor_id: int
    area: Optional[float] = None
    status_code: Optional[str] = None
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    max_tenants: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        """
        Создаёт объект Room из словаря (ответ API).

        Raises:
            ValueError: Если отсутствует обязательное поле 'id' или 'floor_id'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")

        if 'floor_id' not in data:
            raise ValueError("Отсутствует обязательное поле 'floor_id' в ответе API")

        return cls(
            id=data['id'],
            number=data['number'],
            floor_id=data['floor_id'],
            area=data.get('area'),
            status_code=data.get('status_code'),
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            max_tenants=data.get('max_tenants'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )