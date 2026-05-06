# backend/src/app/reference_data/schemas/__init__.py
"""
Pydantic схемы для справочников (reference data).
"""

from .base import ReferenceSchema
from .building_status import BuildingStatusSchema
from .room_status import RoomStatusSchema
from .contract_status import ContractStatusSchema
from .equipment_status import EquipmentStatusSchema
from .payment_status import PaymentStatusSchema
from .counterparty_type import CounterpartyTypeSchema
from .placement_status import PlacementStatusSchema

__all__ = [
    "ReferenceSchema",
    "BuildingStatusSchema",
    "RoomStatusSchema",
    "ContractStatusSchema",
    "EquipmentStatusSchema",
    "PaymentStatusSchema",
    "CounterpartyTypeSchema",
    "PlacementStatusSchema",
]