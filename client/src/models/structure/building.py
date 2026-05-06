# client/src/models/structure/building.py
"""
DTO для корпуса (structure layer).

Соответствует бэкенд-схемам:
- BuildingTreeResponse → BuildingTreeDTO
- BuildingDetailResponse → BuildingDetailDTO
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from ..base import BaseDTO
from ..mixins import DateTimeMixin
from src.core.types.structure import NodeType


@dataclass(frozen=True, kw_only=True)
class BuildingTreeDTO(BaseDTO):
    """Корпус (минимальные данные для дерева)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.BUILDING
    IS_DETAIL: ClassVar[bool] = False

    name: str
    complex_id: int
    floors_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "BuildingTreeDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            name=data["name"],
            complex_id=data["complex_id"],
            floors_count=data.get("floors_count", 0),
        )


@dataclass(frozen=True, kw_only=True)
class BuildingDetailDTO(BaseDTO, DateTimeMixin):
    """Корпус (полные данные для панели деталей)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.BUILDING
    IS_DETAIL: ClassVar[bool] = True

    name: str
    complex_id: int
    floors_count: int = 0
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    status_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "BuildingDetailDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            name=data["name"],
            complex_id=data["complex_id"],
            floors_count=data.get("floors_count", 0),
            description=data.get("description"),
            address=data.get("address"),
            owner_id=data.get("owner_id"),
            status_id=data.get("status_id"),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
        )