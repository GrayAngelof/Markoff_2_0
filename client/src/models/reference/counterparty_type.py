# client/src/models/reference/counterparty_type.py
"""
DTO для типа контрагента.
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from .base import ReferenceBaseDTO
from src.core.types.reference_data import ReferenceDataType


@dataclass(frozen=True, kw_only=True)
class CounterpartyTypeDTO(ReferenceBaseDTO):
    """Тип контрагента (справочник)."""
    
    REFERENCE_TYPE: ClassVar[ReferenceDataType] = ReferenceDataType.COUNTERPARTY_TYPE
    
    is_active: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "CounterpartyTypeDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            code=data["code"],
            name=data["name"],
            description=data.get("description"),
            display_order=data.get("display_order", 0),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
            is_active=data.get("is_active"),
        )