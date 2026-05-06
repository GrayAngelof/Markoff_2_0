# client/src/models/reference/__init__.py
"""
DTO для справочников (reference_data layer).
"""

from .building_status import BuildingStatusDTO
from .room_status import RoomStatusDTO
from .contract_status import ContractStatusDTO
from .equipment_status import EquipmentStatusDTO
from .payment_status import PaymentStatusDTO
from .placement_status import PlacementStatusDTO
from .counterparty_type import CounterpartyTypeDTO

__all__ = [
    "BuildingStatusDTO",
    "RoomStatusDTO",
    "ContractStatusDTO",
    "EquipmentStatusDTO",
    "PaymentStatusDTO",
    "PlacementStatusDTO",
    "CounterpartyTypeDTO",
]