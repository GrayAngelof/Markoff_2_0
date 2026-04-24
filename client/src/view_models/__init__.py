# client/src/view_models/__init__.py
"""
View Models — контракты данных между бизнес-логикой и UI.

Все View Models иммутабельны (@dataclass(frozen=True, slots=True)).
Никакой бизнес-логики, только данные.
"""

# ===== ИМПОРТЫ =====
from .details import DetailsViewModel, HeaderViewModel, InfoGridItem
from .lists import BuildingListItem, FloorListItem, RoomListItem
from .statistics import BuildingStatisticsVM, ComplexStatisticsVM, FloorStatisticsVM, RoomTypeStat


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Статистика
    "BuildingStatisticsVM",
    "ComplexStatisticsVM",
    "FloorStatisticsVM",
    "RoomTypeStat",
    # Списки
    "BuildingListItem",
    "FloorListItem",
    "RoomListItem",
    # Детали
    "DetailsViewModel",
    "HeaderViewModel",
    "InfoGridItem",
]