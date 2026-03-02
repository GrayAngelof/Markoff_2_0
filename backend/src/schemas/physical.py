# backend/src/schemas/physical.py
"""
Pydantic схемы для ответов API
Содержат только те поля, которые нужны для отображения в дереве
"""
from pydantic import BaseModel
from typing import List, Optional

# ===== Схемы для комплексов =====
class ComplexTreeResponse(BaseModel):
    """
    Ответ для отображения комплекса в дереве
    Только поля, нужные для UI
    """
    id: int
    name: str
    buildings_count: int  # Для отображения количества корпусов

    class Config:
        from_attributes = True

# ===== Схемы для корпусов =====
class BuildingTreeResponse(BaseModel):
    """
    Ответ для отображения корпуса в дереве
    """
    id: int
    name: str
    complex_id: int
    floors_count: int  # Для отображения количества этажей

    class Config:
        from_attributes = True

# ===== Схемы для этажей =====
class FloorTreeResponse(BaseModel):
    """
    Ответ для отображения этажа в дереве
    """
    id: int
    number: int
    building_id: int
    rooms_count: int  # Для отображения количества помещений

    class Config:
        from_attributes = True

# ===== Схемы для помещений =====
class RoomTreeResponse(BaseModel):
    """
    Ответ для отображения помещения в дереве
    """
    id: int
    number: str
    floor_id: int
    # Дополнительные поля, которые могут понадобиться в дереве
    area: Optional[float] = None
    status_code: Optional[str] = None

    class Config:
        from_attributes = True