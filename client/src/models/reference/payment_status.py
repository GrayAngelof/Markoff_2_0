# client/src/models/reference/payment_status.py
"""
DTO для статуса платежа.
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from .base import ReferenceBaseDTO
from src.core.types.reference_data import ReferenceDataType


@dataclass(frozen=True, kw_only=True)
class PaymentStatusDTO(ReferenceBaseDTO):
    """Статус платежа (справочник)."""
    
    REFERENCE_TYPE: ClassVar[ReferenceDataType] = ReferenceDataType.PAYMENT_STATUS
    
    is_initial: Optional[bool] = None
    is_success: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "PaymentStatusDTO":
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
            is_success=data.get("is_success"),
        )