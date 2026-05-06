# client/src/core/types/reference_data.py
"""
Типы для справочников (reference_data layer).

Содержит определения:
- ReferenceDataType — перечисление типов справочников

Никакой логики, только данные!
"""

from enum import Enum


class ReferenceDataType(str, Enum):
    """Типы справочных данных."""
    
    # Статусы
    BUILDING_STATUS = "building_status"
    ROOM_STATUS = "room_status"
    CONTRACT_STATUS = "contract_status"
    EQUIPMENT_STATUS = "equipment_status"
    PAYMENT_STATUS = "payment_status"
    PLACEMENT_STATUS = "placement_status"
    
    # Типы
    COUNTERPARTY_TYPE = "counterparty_type"
    
    def __str__(self) -> str:
        return self.value