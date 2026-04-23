# client/src/view_models/__init__.py
"""
View Models — контракты данных между бизнес-логикой и UI.

Все View Models иммутабельны (@dataclass(frozen=True, slots=True)).
Никакой бизнес-логики, только данные.
"""

from .statistics import (
    ComplexStatisticsVM,
    BuildingStatisticsVM,
    FloorStatisticsVM,
    RoomTypeStat,
)
from .sensors import (
    SensorsVM,
    SensorIssue,
)
from .events import (
    EventsVM,
    EventItem,
)
from .lists import (
    BuildingListItem,
    FloorListItem,
    RoomListItem,
)

__all__ = [
    # Statistics
    "ComplexStatisticsVM",
    "BuildingStatisticsVM",
    "FloorStatisticsVM",
    "RoomTypeStat",
    # Sensors
    "SensorsVM",
    "SensorIssue",
    # Events
    "EventsVM",
    "EventItem",
    # Lists
    "BuildingListItem",
    "FloorListItem",
    "RoomListItem",
]