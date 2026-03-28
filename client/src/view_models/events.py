# client/src/view_models/events.py
"""
View Models для событий (вкладка "Пожарка").

Содержат информацию о событиях: сработках датчиков, техническом обслуживании,
ошибках и других происшествиях.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ===== VIEW MODELS =====
@dataclass(frozen=True, slots=True)
class EventItem:
    """Отдельное событие."""

    timestamp: datetime
    type: str          # "Сработка", "ТО", "Ошибка"
    location: str      # "Корпус А, 3 этаж"
    description: str
    is_critical: bool = False


@dataclass(frozen=True, slots=True)
class EventsVM:
    """
    События для отображения в UI.

    Содержит список недавних событий и общую информацию.
    """

    total: int = 0                    # всего событий
    recent_events: List[EventItem] = field(default_factory=list)
    all_events_link: bool = True      # показывать ссылку "все события"

    @classmethod
    def empty(cls) -> "EventsVM":
        """Возвращает пустую ViewModel (для fallback)."""
        return cls()