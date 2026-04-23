# client/src/models/status.py
"""
DTO для справочников статусов.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BuildingStatusDTO:
    """Статус здания (справочник)."""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "BuildingStatusDTO":
        """Создаёт DTO из словаря API."""
        return cls(
            id=data["id"],
            code=data["code"],
            name=data["name"],
            description=data.get("description"),
        )


@dataclass(frozen=True)
class RoomStatusDTO:
    """Статус помещения (справочник)."""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "RoomStatusDTO":
        """Создаёт DTO из словаря API."""
        return cls(
            id=data["id"],
            code=data["code"],
            name=data["name"],
            description=data.get("description"),
        )