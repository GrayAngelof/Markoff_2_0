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

from typing import List, Optional, Any, TypeVar

from src.models import (
    Complex, Building, Floor, Room,
    Counterparty, ResponsiblePerson
)


# ===== Тип для generic =====
T = TypeVar('T')


# ===== Физическая структура =====

def to_complex_list(data: List[dict]) -> List[Complex]:
    """
    Преобразует список JSON объектов в список Complex.
    
    Args:
        data: Список словарей от API /physical/
        
    Returns:
        List[Complex]: Список комплексов
        
    Пример:
        >>> data = [{"id": 1, "name": "Северный", "buildings_count": 3}]
        >>> complexes = to_complex_list(data)
        >>> complexes[0].name
        'Северный'
    """
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
    """
    Преобразует JSON объект в Complex (с деталями).
    
    Args:
        data: Словарь от API /physical/complexes/{id}
        
    Returns:
        Optional[Complex]: Комплекс или None, если данных нет
    """
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


# ===== Справочники =====

def to_counterparty(data: Optional[dict]) -> Optional[Counterparty]:
    """Преобразует JSON объект в Counterparty."""
    return Counterparty.from_dict(data) if data else None


def to_responsible_person_list(data: List[dict]) -> List[ResponsiblePerson]:
    """Преобразует список JSON объектов в список ResponsiblePerson."""
    return [ResponsiblePerson.from_dict(item) for item in data]


# ===== Универсальные конвертеры =====

def safe_convert(data: Any, converter, default: Any = None) -> Any:
    """
    Безопасное преобразование с обработкой None.
    
    Args:
        data: Данные для преобразования
        converter: Функция преобразования
        default: Значение по умолчанию при None
        
    Returns:
        Any: Результат преобразования или default
    """
    if data is None:
        return default
    return converter(data)