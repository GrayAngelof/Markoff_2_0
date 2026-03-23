# client/src/core/types/event_structures.py
"""
СТРУКТУРЫ СОБЫТИЙ.

Базовые классы для всех событий в системе.
Обеспечивают типовую безопасность и единый формат.

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
- EventData = факт (то, что произошло)
- Event = транспорт (конверт с метаданными)
- Нет наследования событий (каждый тип уникален)
- Нет Any, нет Optional без причины
"""
from dataclasses import dataclass, field
from typing import Generic, TypeVar, Optional
from datetime import datetime


T = TypeVar('T')


@dataclass(frozen=True, slots=True)
class EventData:
    """
    Базовый класс для всех данных событий (ФАКТ).
    
    Все события в системе должны передавать данные,
    наследующиеся от этого класса. Это обеспечивает:
    - Типовую безопасность
    - Единый интерфейс
    - Возможность расширения
    
    Правила:
        - События не наследуются (каждый тип уникален)
        - Все поля должны быть типизированы
        - Нет Any без крайней необходимости
    
    Пример:
        @dataclass(frozen=True, slots=True)
        class NodeSelected(EventData):
            node: NodeIdentifier
            payload: Optional[Building] = None
    """
    pass


@dataclass(frozen=True, slots=True)
class Event(Generic[T]):
    """
    Конверт события (envelope) — транспортный объект.
    
    Используется внутри EventBus для передачи событий с метаданными.
    
    Атрибуты:
        data: Данные события (наследник EventData)
        source: Источник события (имя компонента, испустившего событие)
        timestamp: Временная метка создания события
    
    Преимущества:
        - Единое место для метаданных
        - Возможность добавлять middleware
        - Легко логировать и трассировать
        - Расширяем без изменения EventData
    """
    data: T
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def age_ms(self) -> float:
        """
        Возраст события в миллисекундах (для отладки).
        
        Returns:
            float: Количество миллисекунд с момента создания
        """
        delta = datetime.now() - self.timestamp
        return delta.total_seconds() * 1000
    
    @property
    def type_name(self) -> str:
        """Имя типа события (для логирования)."""
        return type(self.data).__name__