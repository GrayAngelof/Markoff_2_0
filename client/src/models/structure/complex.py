# client/src/models/structure/complex.py
"""
DTO для комплекса (structure layer).

Соответствует бэкенд-схемам:
- ComplexTreeResponse → ComplexTreeDTO
- ComplexDetailResponse → ComplexDetailDTO
"""

from dataclasses import dataclass
from typing import ClassVar, Optional

from ..base import BaseDTO
from ..mixins import DateTimeMixin
from src.core.types.structure import NodeType


@dataclass(frozen=True, kw_only=True)
class ComplexTreeDTO(BaseDTO):
    """Комплекс (минимальные данные для дерева)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.COMPLEX
    IS_DETAIL: ClassVar[bool] = False

    name: str
    buildings_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "ComplexTreeDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            name=data["name"],
            buildings_count=data.get("buildings_count", 0),
        )


@dataclass(frozen=True, kw_only=True)
class ComplexDetailDTO(BaseDTO, DateTimeMixin):
    """Комплекс (полные данные для панели деталей)."""

    NODE_TYPE: ClassVar[NodeType] = NodeType.COMPLEX
    IS_DETAIL: ClassVar[bool] = True

    name: str
    buildings_count: int = 0
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    status_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ComplexDetailDTO":
        """Создаёт DTO из словаря (ответ API)."""
        return cls(
            id=data["id"],
            name=data["name"],
            buildings_count=data.get("buildings_count", 0),
            description=data.get("description"),
            address=data.get("address"),
            owner_id=data.get("owner_id"),
            status_id=data.get("status_id"),
            created_at=cls.parse_datetime(data.get("created_at")),
            updated_at=cls.parse_datetime(data.get("updated_at")),
        )