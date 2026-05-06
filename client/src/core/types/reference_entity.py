# client/src/core/types/reference_entity.py
"""
Типы для сущностей (reference_entity layer).

Содержит определения:
- ReferenceEntityType — перечисление типов сущностей

Никакой логики, только данные!
"""

from enum import Enum


class ReferenceEntityType(str, Enum):
    """Типы сущностей (загружаемые по ID)."""
    
    COUNTERPARTY = "counterparty"
    RESPONSIBLE_PERSON = "responsible_person"
    
    def __str__(self) -> str:
        return self.value