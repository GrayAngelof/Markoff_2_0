# client/src/core/types/event_structures.py
"""
Базовые структуры для всех событий в системе.

Обеспечивает типовую безопасность и единый формат событий:
- EventData — факт (то, что произошло)
- Event — конверт с метаданными (время, источник)

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
- События не наследуются (каждый тип уникален)
- Нет Any, нет Optional без причины
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, Optional, TypeVar


# ===== ТИПЫ =====
T = TypeVar('T')


# ===== БАЗОВЫЕ КЛАССЫ =====
@dataclass(frozen=True, slots=True)
class EventData:
    """
    Базовый класс для данных событий.

    Все события в системе должны наследоваться от этого класса.
    Обеспечивает типовую безопасность и единый интерфейс.
    """


@dataclass(frozen=True, slots=True)
class Event(Generic[T]):
    """
    Конверт события (envelope) — транспортный объект.

    Содержит данные события и метаинформацию (источник, время).
    Позволяет добавлять middleware, логирование и трассировку.
    """

    data: T
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def age_ms(self) -> float:
        """Возраст события в миллисекундах (для отладки)."""
        delta = datetime.now() - self.timestamp
        return delta.total_seconds() * 1000

    @property
    def type_name(self) -> str:
        """Имя типа события (для логирования)."""
        return type(self.data).__name__