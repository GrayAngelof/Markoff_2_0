# client/src/models/entity/responsible_person.py
"""
DTO для ответственного лица (reference_entity layer).

Соответствует бэкенд-схеме ResponsiblePersonSchema.
"""

from dataclasses import dataclass
from typing import ClassVar, Optional, List
from datetime import date

from .base import EntityBaseDTO
from src.core.types.reference_entity import ReferenceEntityType


@dataclass(frozen=True, kw_only=True)
class ResponsiblePersonDTO(EntityBaseDTO):
    """Ответственное лицо контрагента."""
    
    ENTITY_TYPE: ClassVar[ReferenceEntityType] = ReferenceEntityType.RESPONSIBLE_PERSON
    
    counterparty_id: int
    person_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    role_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_categories: Optional[List[str]] = None
    is_public_contact: bool = False
    is_active: bool = True
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    notes: Optional[str] = None
    
    @staticmethod
    def parse_date(value: Optional[str]) -> Optional[date]:
        """Преобразует строку ISO в date."""
        if value is None:
            return None
        return date.fromisoformat(value)
    
    @classmethod
    def from_dict(cls, data: dict) -> "ResponsiblePersonDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            counterparty_id=data["counterparty_id"],
            person_name=data["person_name"],
            position=data.get("position"),
            department=data.get("department"),
            role_code=data.get("role_code"),
            phone=data.get("phone"),
            email=data.get("email"),
            contact_categories=data.get("contact_categories"),
            is_public_contact=data.get("is_public_contact", False),
            is_active=data.get("is_active", True),
            hire_date=cls.parse_date(data.get("hire_date")),
            termination_date=cls.parse_date(data.get("termination_date")),
            notes=data.get("notes"),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
        )