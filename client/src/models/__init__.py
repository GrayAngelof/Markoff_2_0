"""
Пакет моделей данных (DTO) для клиентского приложения.

Все модели — иммутабельные dataclasses с полным соответствием API бекенда.
Содержат ТОЛЬКО данные, никакой UI-логики или бизнес-логики.

Разделение на TreeDTO (для дерева) и DetailDTO (для панели деталей).

Использование:
    from src.models import ComplexTreeDTO, ComplexDetailDTO, BuildingTreeDTO
    
    complex_tree = ComplexTreeDTO.from_dict(api_response)
    complex_detail = ComplexDetailDTO.from_dict(api_response)
"""

from .complex import ComplexTreeDTO, ComplexDetailDTO
from .building import BuildingTreeDTO, BuildingDetailDTO
from .floor import FloorTreeDTO, FloorDetailDTO
from .room import RoomTreeDTO, RoomDetailDTO

__all__ = [
    # Complex
    "ComplexTreeDTO",
    "ComplexDetailDTO",
    
    # Building
    "BuildingTreeDTO",
    "BuildingDetailDTO",
    
    # Floor
    "FloorTreeDTO",
    "FloorDetailDTO",
    
    # Room
    "RoomTreeDTO",
    "RoomDetailDTO",
]