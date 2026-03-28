# client/src/view_models/sensors.py
"""
View Models для датчиков (вкладка "Пожарка").

Содержат информацию о датчиках: их статусе, активности и проблемах.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ===== VIEW MODELS =====
@dataclass(frozen=True, slots=True)
class SensorIssue:
    """Проблемный датчик."""

    sensor_id: int
    location: str                     # "пом. 203"
    issue: str                        # "не отвечает", "низкий заряд"
    last_check: Optional[datetime] = None


@dataclass(frozen=True, slots=True)
class SensorsVM:
    """
    Датчики для отображения в UI.

    Содержит статистику по датчикам и список проблемных.
    """

    total: int = 0                    # всего датчиков
    active: int = 0                   # активных
    inactive: int = 0                 # неактивных
    maintenance: int = 0              # на обслуживании

    issues: List[SensorIssue] = field(default_factory=list)

    # ID для кликабельности (чтобы запросить список)
    active_ids: List[int] = field(default_factory=list)
    inactive_ids: List[int] = field(default_factory=list)
    maintenance_ids: List[int] = field(default_factory=list)

    @classmethod
    def empty(cls) -> "SensorsVM":
        """Возвращает пустую ViewModel (для fallback)."""
        return cls()