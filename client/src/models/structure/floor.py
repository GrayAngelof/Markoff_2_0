# client/src/models/structure/floor.py
"""
DTO для этажа (structure layer).

Соответствует бэкенд-схемам:
- FloorTreeResponse → FloorTreeDTO
- FloorDetailResponse → FloorDetailDTO
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from ..base import BaseDTO
from ..mixins import DateTimeMixin
from src.core.types.structure import NodeType


@dataclass(frozen=True, kw_only=True)
class FloorTreeDTO(BaseDTO):
    """Этаж (минимальные данные для дерева)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.FLOOR
    IS_DETAIL: ClassVar[bool] = False

    number: int
    building_id: int
    rooms_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "FloorTreeDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            number=data["number"],
            building_id=data["building_id"],
            rooms_count=data.get("rooms_count", 0),
        )


@dataclass(frozen=True, kw_only=True)
class FloorDetailDTO(BaseDTO, DateTimeMixin):
    """Этаж (полные данные для панели деталей)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.FLOOR
    IS_DETAIL: ClassVar[bool] = True

    number: int
    building_id: int
    rooms_count: int = 0
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    plan_image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FloorDetailDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            number=data["number"],
            building_id=data["building_id"],
            rooms_count=data.get("rooms_count", 0),
            description=data.get("description"),
            physical_type_id=data.get("physical_type_id"),
            status_id=data.get("status_id"),
            plan_image_url=data.get("plan_image_url"),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
        )