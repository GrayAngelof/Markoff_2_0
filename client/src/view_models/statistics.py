# client/src/view_models/statistics.py
"""
View Models для вкладки "Физика".
Содержат статистические данные: количество объектов, площади, занятость.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True, slots=True)
class RoomTypeStat:
    """Статистика по типу помещения."""
    type_name: str          # "Офисное", "Складское", "Торговое"
    count: int              # количество помещений этого типа
    area: float             # общая площадь помещений этого типа


@dataclass(frozen=True, slots=True)
class ComplexStatisticsVM:
    """
    Статистика для комплекса.
    Отображается в правой панели при выборе комплекса.
    """
    total_buildings: int = 0          # всего корпусов
    total_floors: int = 0             # всего этажей
    total_rooms: int = 0              # всего помещений
    free_rooms: int = 0               # свободных помещений
    occupied_rooms: int = 0           # занятых помещений
    reserved_rooms: int = 0           # зарезервированных
    maintenance_rooms: int = 0        # на ремонте
    
    total_area: float = 0.0           # общая площадь всех помещений
    rentable_area: float = 0.0        # сдаваемая площадь
    occupancy_rate: float = 0.0       # процент занятости (0-100)
    
    room_types: List[RoomTypeStat] = field(default_factory=list)
    
    @classmethod
    def empty(cls) -> "ComplexStatisticsVM":
        """Возвращает пустую ViewModel (для fallback)."""
        return cls()


@dataclass(frozen=True, slots=True)
class BuildingStatisticsVM:
    """
    Статистика для корпуса.
    Отображается в правой панели при выборе корпуса.
    """
    total_floors: int = 0             # всего этажей
    total_rooms: int = 0              # всего помещений
    free_rooms: int = 0               # свободных
    occupied_rooms: int = 0           # занятых
    reserved_rooms: int = 0           # зарезервированных
    maintenance_rooms: int = 0        # на ремонте
    total_area: float = 0.0           # общая площадь
    occupancy_rate: float = 0.0       # процент занятости
    
    @classmethod
    def empty(cls) -> "BuildingStatisticsVM":
        """Возвращает пустую ViewModel (для fallback)."""
        return cls()


@dataclass(frozen=True, slots=True)
class FloorStatisticsVM:
    """
    Статистика для этажа.
    Отображается в правой панели при выборе этажа.
    """
    total_rooms: int = 0              # всего помещений
    free_rooms: int = 0               # свободных
    occupied_rooms: int = 0           # занятых
    reserved_rooms: int = 0           # зарезервированных
    maintenance_rooms: int = 0        # на ремонте
    room_types: List[RoomTypeStat] = field(default_factory=list)
    
    @classmethod
    def empty(cls) -> "FloorStatisticsVM":
        """Возвращает пустую ViewModel (для fallback)."""
        return cls()