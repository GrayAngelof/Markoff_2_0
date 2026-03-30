# client/src/core/event_bus.py
"""
Фасад шины событий (type-based).

EventBus — центральный диспетчер событий в приложении.
Обеспечивает слабую связанность компонентов и тестируемость.

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
- События — классы, наследующие EventData (типобезопасность)
- Подписка по типу события, а не по строке
- Слабые ссылки для предотвращения утечек памяти
"""

# ===== ИМПОРТЫ =====
from typing import Callable, Optional, Type, TypeVar

from utils.logger import get_logger
from .bus.registry import _SubscriptionRegistry
from .types.event_structures import EventData


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ТИПЫ =====
T = TypeVar('T', bound=EventData)

# Обработчик принимает конкретный тип события
EventHandler = Callable[[T], None]


# ===== КЛАСС =====
class EventBus:
    """
    Единая шина событий для всего приложения.

    Подписка по типу события (класс, наследующий EventData).
    Использует слабые ссылки для предотвращения утечек памяти.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, debug: bool = False) -> None:
        """Инициализирует шину событий."""
        self._registry = _SubscriptionRegistry()
        self._debug = debug

        log.system("EventBus инициализирован")
        if debug:
            log.debug("Режим отладки включён")

    def clear(self) -> None:
        """Очищает все подписки. Используется при завершении приложения."""
        cleared = self._registry.clear()
        log.system(f"EventBus очищен (удалено {cleared} подписок)")

    # ---- ПУБЛИЧНОЕ API ----
    def subscribe(
        self, 
        event_type: Type[T], 
        callback: EventHandler[T],
    ) -> Callable[[], None]:
        """
        Подписывает обработчик на указанный тип события.

        Args:
            event_type: Тип события (класс-наследник EventData)
            callback: Функция-обработчик, принимающая event_type

        Returns:
            Функция для отписки
        """
        return self._registry.register(event_type, callback)

    def emit(self, event_data: EventData, source: Optional[str] = None) -> None:
        """
        Испускает событие, уведомляя всех подписчиков.

        Args:
            event_data: Данные события (наследник EventData)
            source: Источник события (для отладки)
        """
        if event_data is None:
            raise ValueError("Event data cannot be None")

        event_type = type(event_data)
        source_str = f" от {source}" if source else ""

        log.info(f"Испускание {event_type.__name__}{source_str}")

        self._registry.notify(event_type, event_data)

    def set_debug(self, enabled: bool) -> None:
        """Включает или выключает режим отладки."""
        self._debug = enabled
        log.info(f"Режим отладки EventBus: {'включён' if enabled else 'выключен'}")

    @property
    def debug(self) -> bool:
        """Возвращает текущий режим отладки."""
        return self._debug