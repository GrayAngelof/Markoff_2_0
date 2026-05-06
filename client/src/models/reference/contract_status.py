# client/src/models/reference/contract_status.py
"""
DTO для статуса договора.
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from .base import ReferenceBaseDTO
from src.core.types.reference_data import ReferenceDataType


@dataclass(frozen=True, kw_only=True)
class ContractStatusDTO(ReferenceBaseDTO):
    """Статус договора (справочник)."""
    
    REFERENCE_TYPE: ClassVar[ReferenceDataType] = ReferenceDataType.CONTRACT_STATUS
    
    is_initial: Optional[bool] = None
    is_terminal: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "ContractStatusDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            code=data["code"],
            name=data["name"],
            description=data.get("description"),
            display_order=data.get("display_order", 0),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
            is_initial=data.get("is_initial"),
            is_terminal=data.get("is_terminal"),
        )