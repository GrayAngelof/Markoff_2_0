# client/src/models/complex.py
"""
Модель данных для комплекса на стороне клиента.

Чистый DTO — только данные от API, никакой UI-логики.
Соответствует ComplexTreeResponse и ComplexDetailResponse из бекенда.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== МОДЕЛИ =====
@dataclass(frozen=True, kw_only=True)
class Complex(BaseDTO, DateTimeMixin):
    """Модель комплекса (DTO)."""

    NODE_TYPE = "complex"

    name: str
    buildings_count: int = 0
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Complex':
        """
        Создаёт объект Complex из словаря (ответ API).

        Raises:
            ValueError: Если отсутствует обязательное поле 'id'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")

        return cls(
            id=data['id'],
            name=data['name'],
            buildings_count=data.get('buildings_count', 0),
            description=data.get('description'),
            address=data.get('address'),
            owner_id=data.get('owner_id'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )