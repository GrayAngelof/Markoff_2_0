# client/src/models/floor.py
"""
Модель данных для этажа на стороне клиента.

Чистый DTO — только данные от API, никакой UI-логики.
Соответствует FloorTreeResponse и FloorDetailResponse из бекенда.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== МОДЕЛИ =====
@dataclass(frozen=True, kw_only=True)
class Floor(BaseDTO, DateTimeMixin):
    """Модель этажа (DTO)."""

    NODE_TYPE = "floor"

    number: int
    building_id: int
    rooms_count: int = 0
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    plan_image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Floor':
        """
        Создаёт объект Floor из словаря (ответ API).

        Raises:
            ValueError: Если отсутствует обязательное поле 'id' или 'building_id'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")

        if 'building_id' not in data:
            raise ValueError("Отсутствует обязательное поле 'building_id' в ответе API")

        return cls(
            id=data['id'],
            number=data['number'],
            building_id=data['building_id'],
            rooms_count=data.get('rooms_count', 0),
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            status_id=data.get('status_id'),
            plan_image_url=data.get('plan_image_url'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )