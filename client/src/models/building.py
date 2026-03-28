# client/src/models/building.py
"""
Модель данных для корпуса на стороне клиента.

Чистый DTO — только данные от API, никакой UI-логики.
Соответствует BuildingTreeResponse и BuildingDetailResponse из бекенда.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== МОДЕЛИ =====
@dataclass(frozen=True, kw_only=True)
class Building(BaseDTO, DateTimeMixin):
    """Модель корпуса (DTO)."""

    NODE_TYPE = "building"

    name: str
    complex_id: int
    floors_count: int = 0
    description: Optional[str] = None
    address: Optional[str] = None
    status_id: Optional[int] = None
    owner_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Building':
        """
        Создаёт объект Building из словаря (ответ API).

        Raises:
            ValueError: Если отсутствует обязательное поле 'id' или 'complex_id'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")

        if 'complex_id' not in data:
            raise ValueError("Отсутствует обязательное поле 'complex_id' в ответе API")

        return cls(
            id=data['id'],
            name=data['name'],
            complex_id=data['complex_id'],
            floors_count=data.get('floors_count', 0),
            description=data.get('description'),
            address=data.get('address'),
            status_id=data.get('status_id'),
            owner_id=data.get('owner_id'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )