# client/src/services/api/converters.py
"""
Преобразование JSON ответов API в модели данных.

Каждая функция:
- Принимает словарь (или список словарей) от API
- Возвращает модель (или список моделей)
- Не содержит логики, только вызов from_dict

Конвертеры отделены от HTTP логики, что позволяет:
- Легко тестировать преобразование
- Менять формат API без изменения HTTP клиента
- Переиспользовать конвертеры в разных местах

Разделение на Tree и Detail DTO:
- TreeDTO для минимальных ответов (дерево)
- DetailDTO для полных ответов (панель деталей)
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, TypeVar

from src.models import (
    ComplexTreeDTO,
    ComplexDetailDTO,
    BuildingTreeDTO,
    BuildingDetailDTO,
    FloorTreeDTO,
    FloorDetailDTO,
    RoomTreeDTO,
    RoomDetailDTO,
    BuildingStatusDTO,
    RoomStatusDTO,
)


# ===== ТИПЫ =====
T = TypeVar('T')


# ===== ДЕРЕВО (TREE) =====
def to_complex_tree_list(data: List[dict]) -> List[ComplexTreeDTO]:
    """Преобразует список JSON объектов в список ComplexTreeDTO."""
    return [ComplexTreeDTO.from_dict(item) for item in data]


def to_building_tree_list(data: List[dict]) -> List[BuildingTreeDTO]:
    """Преобразует список JSON объектов в список BuildingTreeDTO."""
    return [BuildingTreeDTO.from_dict(item) for item in data]


def to_floor_tree_list(data: List[dict]) -> List[FloorTreeDTO]:
    """Преобразует список JSON объектов в список FloorTreeDTO."""
    return [FloorTreeDTO.from_dict(item) for item in data]


def to_room_tree_list(data: List[dict]) -> List[RoomTreeDTO]:
    """Преобразует список JSON объектов в список RoomTreeDTO."""
    return [RoomTreeDTO.from_dict(item) for item in data]


# ===== ДЕТАЛИ (DETAIL) =====
def to_complex_detail(data: Optional[dict]) -> Optional[ComplexDetailDTO]:
    """Преобразует JSON объект в ComplexDetailDTO."""
    return ComplexDetailDTO.from_dict(data) if data else None


def to_building_detail(data: Optional[dict]) -> Optional[BuildingDetailDTO]:
    """Преобразует JSON объект в BuildingDetailDTO."""
    return BuildingDetailDTO.from_dict(data) if data else None


def to_floor_detail(data: Optional[dict]) -> Optional[FloorDetailDTO]:
    """Преобразует JSON объект в FloorDetailDTO."""
    return FloorDetailDTO.from_dict(data) if data else None


def to_room_detail(data: Optional[dict]) -> Optional[RoomDetailDTO]:
    """Преобразует JSON объект в RoomDetailDTO."""
    return RoomDetailDTO.from_dict(data) if data else None

# ===== СПРАВОЧНИКИ (DICTIONARY) =====
def to_building_status_list(data: List[dict]) -> List[BuildingStatusDTO]:
    """Преобразует список JSON объектов в список BuildingStatusDTO."""
    return [BuildingStatusDTO.from_dict(item) for item in data]


def to_room_status_list(data: List[dict]) -> List[RoomStatusDTO]:
    """Преобразует список JSON объектов в список RoomStatusDTO."""
    return [RoomStatusDTO.from_dict(item) for item in data]

# ===== УНИВЕРСАЛЬНЫЙ КОНВЕРТЕР =====
def convert_optional(data: Optional[dict], converter, default=None):
    """
    Безопасное преобразование с обработкой None.

    Args:
        data: Данные для преобразования
        converter: Функция преобразования
        default: Значение по умолчанию при None
    """
    if data is None:
        return default
    return converter(data)