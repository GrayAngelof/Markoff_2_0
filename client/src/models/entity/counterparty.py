# client/src/models/entity/counterparty.py
"""
DTO для контрагента (reference_entity layer).

Соответствует бэкенд-схеме CounterpartySchema.
"""

from dataclasses import dataclass
from typing import ClassVar, Optional, Dict, Any

from .base import EntityBaseDTO
from src.core.types.reference_entity import ReferenceEntityType


@dataclass(frozen=True, kw_only=True)
class CounterpartyDTO(EntityBaseDTO):
    """Контрагент (юридическое или физическое лицо)."""
    
    ENTITY_TYPE: ClassVar[ReferenceEntityType] = ReferenceEntityType.COUNTERPARTY
    
    short_name: str
    full_name: str
    tax_id: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None
    status_code: Optional[str] = None
    notes: Optional[str] = None
    type_id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "CounterpartyDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            short_name=data["short_name"],
            full_name=data["full_name"],
            tax_id=data.get("tax_id"),
            legal_address=data.get("legal_address"),
            actual_address=data.get("actual_address"),
            bank_details=data.get("bank_details"),
            status_code=data.get("status_code"),
            notes=data.get("notes"),
            type_id=data.get("type_id"),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
        )