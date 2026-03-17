# client/src/projections/base_projection.py
"""
Базовый класс для всех проекций с поддержкой debounce.
"""
from PySide6.QtCore import QTimer, QObject
from typing import Optional, Any

from utils.logger import get_logger

log = get_logger(__name__)


class BaseProjection(QObject):
    """
    Базовый класс для проекций.
    
    Предоставляет:
    - Debounce механизм для отложенного перестроения
    - Кэширование результатов
    - Подписку на события
    """
    
    def __init__(self, event_bus, debounce_ms=50):
        super().__init__()
        
        self._bus = event_bus
        self._debounce_ms = debounce_ms
        self._cached_result = None
        self._dirty = False
        
        # Таймер для debounce
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._rebuild)
        
        self._subscriptions = []
        
        log.debug(f"{self.__class__.__name__} инициализирован")
    
    def _subscribe(self, event_type, callback):
        """Подписывается на событие с сохранением для отписки."""
        unsubscribe = self._bus.subscribe(event_type, callback)
        self._subscriptions.append(unsubscribe)
    
    def _schedule_rebuild(self):
        """Планирует перестроение с debounce."""
        self._dirty = True
        self._timer.start(self._debounce_ms)
        log.debug(f"Запланировано перестроение {self.__class__.__name__}")
    
    def _rebuild(self):
        """Перестраивает проекцию - должен быть переопределён."""
        raise NotImplementedError
    
    def get(self):
        """Возвращает кэшированный результат."""
        return self._cached_result
    
    def cleanup(self):
        """Отписывается от всех событий."""
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()
        log.debug(f"{self.__class__.__name__} очищен")