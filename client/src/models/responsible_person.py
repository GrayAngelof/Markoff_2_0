# client/src/models/responsible_person.py
"""
Модель данных для ответственного лица (контактного лица контрагента).

Чистый DTO — только данные от API, никакой UI-логики.
Соответствует ответам API для ответственных лиц.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== МОДЕЛИ =====
@dataclass(frozen=True, kw_only=True)
class ResponsiblePerson(BaseDTO, DateTimeMixin):
    """Модель ответственного лица (DTO)."""

    NODE_TYPE = "responsible_person"

    counterparty_id: int
    person_name: str
    position: Optional[str] = None
    role_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_categories: Optional[str] = None  # строка, например "legal,financial"
    is_public_contact: bool = False
    is_active: bool = True
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ResponsiblePerson':
        """
        Создаёт объект ResponsiblePerson из словаря (ответ API).

        Raises:
            ValueError: Если отсутствует обязательное поле 'id', 'counterparty_id' или 'person_name'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")

        if 'counterparty_id' not in data:
            raise ValueError("Отсутствует обязательное поле 'counterparty_id' в ответе API")

        if 'person_name' not in data:
            raise ValueError("Отсутствует обязательное поле 'person_name' в ответе API")

        # API может отдавать contact_categories как строку или как список
        contact_categories = data.get('contact_categories')
        if isinstance(contact_categories, list):
            contact_categories = ','.join(contact_categories) if contact_categories else None

        return cls(
            id=data['id'],
            counterparty_id=data['counterparty_id'],
            person_name=data['person_name'],
            position=data.get('position'),
            role_code=data.get('role_code'),
            phone=data.get('phone'),
            email=data.get('email'),
            contact_categories=contact_categories,
            is_public_contact=data.get('is_public_contact', False),
            is_active=data.get('is_active', True),
            notes=data.get('notes'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )