# client/src/models/reference/base.py
"""
Базовый DTO для всех справочников.
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from ..mixins import DateTimeMixin
from src.core.types.reference_data import ReferenceDataType


@dataclass(frozen=True, kw_only=True)
class ReferenceBaseDTO(DateTimeMixin):
    """Базовый DTO для справочников."""
    
    id: int
    code: str
    name: str
    description: Optional[str] = None
    display_order: int = 0
    
    # Метаданные класса — должны быть переопределены в наследниках
    REFERENCE_TYPE: ClassVar[ReferenceDataType]
    
    @classmethod
    def from_dict(cls, data: dict) -> "ReferenceBaseDTO":
        """Базовый метод — должен быть переопределён."""
        raise NotImplementedError