# backend/src/app/reference_data/models/__init__.py
"""
Модели справочников (reference data).
"""

from .building_status import BuildingStatus
from .room_status import RoomStatus
from .contract_status import ContractStatus
from .equipment_status import EquipmentStatus
from .payment_status import PaymentStatus
from .counterparty_type import CounterpartyType
from .placement_status import PlacementStatus

__all__ = [
    "BuildingStatus",
    "RoomStatus",
    "ContractStatus",
    "EquipmentStatus",
    "PaymentStatus",
    "CounterpartyType",
    "PlacementStatus",
]