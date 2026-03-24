# client/src/view_models/__init__.py
"""
View Models — контракты данных между бизнес-логикой и UI.

Все View Models иммутабельны (@dataclass(frozen=True, slots=True)).
Никакой бизнес-логики, только данные.
"""

from src.view_models.statistics import (
    ComplexStatisticsVM,
    BuildingStatisticsVM,
    FloorStatisticsVM,
    RoomTypeStat,
)
from src.view_models.contacts import (
    ContactsVM,
    ContactGroup,
    ContactPerson,
    ContactSummary,
)
from src.view_models.sensors import (
    SensorsVM,
    SensorIssue,
)
from src.view_models.events import (
    EventsVM,
    EventItem,
)
from src.view_models.lists import (
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
    # Contacts
    "ContactsVM",
    "ContactGroup",
    "ContactPerson",
    "ContactSummary",
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