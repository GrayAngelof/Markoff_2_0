# client/src/core/types/event_structures.py
"""
СТРУКТУРЫ СОБЫТИЙ.

Базовые классы для всех событий в системе.
Обеспечивают типовую безопасность и единый формат.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime


@dataclass
class EventData:
    """
    Базовый класс для всех данных событий.
    
    Все события в системе должны передавать данные,
    наследующиеся от этого класса. Это обеспечивает:
    - Типовую безопасность
    - Единый интерфейс
    - Возможность расширения
    
    Пример:
        @dataclass
        class NodeSelectedEvent(EventData):
            node_type: NodeType
            node_id: int
            context: Optional[Dict] = None
    """
    pass


@dataclass
class Event:
    """
    Конверт события (envelope), которым оборачиваются все данные.
    
    Этот класс используется внутри EventBus для передачи событий.
    Содержит метаданные о событии: тип, источник, время.
    
    Атрибуты:
        type: Тип события (строка из event_constants.py)
        data: Данные события (должны быть наследником EventData)
        source: Источник события (имя компонента, испустившего событие)
        timestamp: Временная метка создания события
    """
    type: str
    data: EventData
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Логируем создание события."""
        from utils.logger import get_logger
        log = get_logger(__name__)
        
        source_str = f" от {self.source}" if self.source else ""
        log.debug(f"📦 Создано событие: {self.type}{source_str}")
    
    @property
    def age_ms(self) -> float:
        """
        Возраст события в миллисекундах (для отладки).
        
        Returns:
            float: Количество миллисекунд с момента создания
        """
        delta = datetime.now() - self.timestamp
        return delta.total_seconds() * 1000