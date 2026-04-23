# backend/src/models/physical/building.py
"""
Модель Building для таблицы physical.buildings.

Простая модель без отношений.
"""

# ===== ИМПОРТЫ =====
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


# ===== КЛАССЫ =====
class Building(SQLModel, table=True):
    """Модель корпуса (таблица physical.buildings)."""

    __tablename__ = "buildings"  # type: ignore
    __table_args__ = {"schema": "physical"}

    id: Optional[int] = Field(default=None, primary_key=True)
    complex_id: int = Field(foreign_key="physical.complexes.id", nullable=False)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    floors_count: int = Field(default=0, nullable=False)
    owner_id: Optional[int] = Field(default=None, foreign_key="dictionary.counterparties.id")
    status_id: Optional[int] = Field(default=None, foreign_key="dictionary.building_statuses.id")
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    class Config:
        from_attributes = True