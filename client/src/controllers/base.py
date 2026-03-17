# client/src/controllers/base.py
"""
Базовый класс для всех контроллеров.
Предоставляет общую функциональность подписки и отписки.
"""
from typing import List, Callable

from src.core.event_bus import EventBus
from utils.logger import get_logger


class BaseController:
    """
    Базовый контроллер.
    
    Предоставляет:
    - Единый механизм подписки на события
    - Автоматическую отписку при cleanup
    - Доступ к логгеру с именем контроллера
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Инициализирует базовый контроллер.
        
        Args:
            event_bus: Шина событий
        """
        self._bus = event_bus
        self._logger = get_logger(self.__class__.__name__)
        self._subscriptions: List[Callable] = []
        
        self._logger.debug(f"Контроллер инициализирован")
    
    def _subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Подписывается на событие с сохранением функции отписки.
        
        Args:
            event_type: Тип события
            callback: Функция-обработчик
        """
        unsubscribe = self._bus.subscribe(event_type, callback)
        self._subscriptions.append(unsubscribe)
        self._logger.debug(f"Подписка на {event_type}")
    
    def cleanup(self) -> None:
        """
        Отписывается от всех событий.
        Должен вызываться при уничтожении контроллера.
        """
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()
        self._logger.debug("Контроллер очищен")
        