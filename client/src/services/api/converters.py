# client/src/services/converters.py
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
"""

# ===== ИМПОРТЫ =====
from typing import Any, List, Optional, TypeVar

from src.models import (
    Building,
    Complex,
    Counterparty,
    Floor,
    ResponsiblePerson,
    Room,
)


# ===== ТИПЫ =====
T = TypeVar('T')


# ===== ФИЗИЧЕСКАЯ СТРУКТУРА =====
def to_complex_list(data: List[dict]) -> List[Complex]:
    """Преобразует список JSON объектов в список Complex."""
    return [Complex.from_dict(item) for item in data]


def to_building_list(data: List[dict]) -> List[Building]:
    """Преобразует список JSON объектов в список Building."""
    return [Building.from_dict(item) for item in data]


def to_floor_list(data: List[dict]) -> List[Floor]:
    """Преобразует список JSON объектов в список Floor."""
    return [Floor.from_dict(item) for item in data]


def to_room_list(data: List[dict]) -> List[Room]:
    """Преобразует список JSON объектов в список Room."""
    return [Room.from_dict(item) for item in data]


def to_complex(data: Optional[dict]) -> Optional[Complex]:
    """Преобразует JSON объект в Complex (с деталями)."""
    return Complex.from_dict(data) if data else None


def to_building(data: Optional[dict]) -> Optional[Building]:
    """Преобразует JSON объект в Building (с деталями)."""
    return Building.from_dict(data) if data else None


def to_floor(data: Optional[dict]) -> Optional[Floor]:
    """Преобразует JSON объект в Floor (с деталями)."""
    return Floor.from_dict(data) if data else None


def to_room(data: Optional[dict]) -> Optional[Room]:
    """Преобразует JSON объект в Room (с деталями)."""
    return Room.from_dict(data) if data else None


# ===== СПРАВОЧНИКИ =====
def to_counterparty(data: Optional[dict]) -> Optional[Counterparty]:
    """Преобразует JSON объект в Counterparty."""
    return Counterparty.from_dict(data) if data else None


def to_responsible_person_list(data: List[dict]) -> List[ResponsiblePerson]:
    """Преобразует список JSON объектов в список ResponsiblePerson."""
    return [ResponsiblePerson.from_dict(item) for item in data]

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