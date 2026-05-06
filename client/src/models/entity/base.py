# client/src/models/entity/base.py
"""
Базовый DTO для всех сущностей (reference_entity).
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from ..mixins import DateTimeMixin
from src.core.types.reference_entity import ReferenceEntityType


@dataclass(frozen=True, kw_only=True)
class EntityBaseDTO(DateTimeMixin):
    """Базовый DTO для сущностей."""
    
    id: int
    
    # Метаданные класса — должны быть переопределены в наследниках
    ENTITY_TYPE: ClassVar[ReferenceEntityType]
    
    @classmethod
    def from_dict(cls, data: dict) -> "EntityBaseDTO":
        """Базовый метод — должен быть переопределён."""
        raise NotImplementedError