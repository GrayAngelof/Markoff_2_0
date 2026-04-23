# backend/src/models/dictionary/building_status.py
"""
Модель для таблицы building_statuses (схема dictionary)
"""

from sqlmodel import SQLModel, Field
from typing import Optional


class BuildingStatus(SQLModel, table=True):
    """Статус здания (справочник)"""
    
    __tablename__ = "building_statuses" # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=50, unique=True, nullable=False)
    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = None