# client/src/models/counterparty.py
"""
Модель данных для контрагента (юридического лица).

Чистый DTO — только данные от API, никакой UI-логики.
Соответствует ответам API для контрагентов.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== МОДЕЛИ =====
@dataclass(frozen=True, kw_only=True)
class Counterparty(BaseDTO, DateTimeMixin):
    """Модель контрагента (DTO)."""

    NODE_TYPE = "counterparty"

    short_name: str
    full_name: Optional[str] = None
    type_id: Optional[int] = None
    tax_id: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None
    status_code: str = 'active'
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Counterparty':
        """
        Создаёт объект Counterparty из словаря (ответ API).

        Raises:
            ValueError: Если отсутствует обязательное поле 'id' или 'short_name'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")

        if 'short_name' not in data:
            raise ValueError("Отсутствует обязательное поле 'short_name' в ответе API")

        return cls(
            id=data['id'],
            short_name=data['short_name'],
            full_name=data.get('full_name'),
            type_id=data.get('type_id'),
            tax_id=data.get('tax_id'),
            legal_address=data.get('legal_address'),
            actual_address=data.get('actual_address'),
            bank_details=data.get('bank_details'),
            status_code=data.get('status_code', 'active'),
            notes=data.get('notes'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )