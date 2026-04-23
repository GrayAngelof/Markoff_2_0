# backend/src/schemas/dictionary.py
"""
Pydantic схемы для словарей и справочников
"""

from pydantic import BaseModel
from typing import Optional


class BuildingStatusResponse(BaseModel):
    """Статус здания (ответ API)"""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    
    model_config = {"from_attributes": True}


class RoomStatusResponse(BaseModel):
    """Статус помещения (ответ API)"""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    
    model_config = {"from_attributes": True}