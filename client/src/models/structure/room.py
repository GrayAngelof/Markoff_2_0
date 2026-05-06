# client/src/models/structure/room.py
"""
DTO для помещения (structure layer).

Соответствует бэкенд-схемам:
- RoomTreeResponse → RoomTreeDTO
- RoomDetailResponse → RoomDetailDTO
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from ..base import BaseDTO
from ..mixins import DateTimeMixin
from src.core.types.structure import NodeType


@dataclass(frozen=True, kw_only=True)
class RoomTreeDTO(BaseDTO):
    """Помещение (минимальные данные для дерева)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.ROOM
    IS_DETAIL: ClassVar[bool] = False

    number: str
    floor_id: int
    area: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "RoomTreeDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            number=data["number"],
            floor_id=data["floor_id"],
            area=data.get("area"),
        )


@dataclass(frozen=True, kw_only=True)
class RoomDetailDTO(BaseDTO, DateTimeMixin):
    """Помещение (полные данные для панели деталей)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.ROOM
    IS_DETAIL: ClassVar[bool] = True

    number: str
    floor_id: int
    area: Optional[float] = None
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    max_tenants: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "RoomDetailDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            number=data["number"],
            floor_id=data["floor_id"],
            area=data.get("area"),
            description=data.get("description"),
            physical_type_id=data.get("physical_type_id"),
            status_id=data.get("status_id"),
            max_tenants=data.get("max_tenants"),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
        )