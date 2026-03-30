# client/src/controllers/base.py
"""
Базовый контроллер — общая подписка/отписка и обработка ошибок.

Все контроллеры наследуются от этого класса.
Предоставляет:
- Подписку на события с автоматической отпиской
- Централизованную обработку ошибок
- Метод cleanup для освобождения ресурсов
"""

# ===== ИМПОРТЫ =====
from typing import Callable, List, Optional, TypeVar, cast

from src.core import EventBus
from src.core.events.definitions import DataError
from src.core.types import Event, EventData, NodeIdentifier
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

T = TypeVar('T', bound=EventData)


# ===== КЛАСС =====
class BaseController:
    """Базовый класс для всех контроллеров."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus) -> None:
        """Инициализирует базовый контроллер."""
        self._logger = get_logger(self.__class__.__name__)
        self._bus = bus

        # Функции отписки
        self._subscriptions: List[Callable[[], None]] = []

        # Хранилище wrapper'ов (предотвращает удаление GC)
        self._wrappers: List[Callable] = []

    def cleanup(self) -> None:
        """Отписывается от всех событий и освобождает ресурсы."""
        controller_name = self.__class__.__name__
        unsubscribe_count = len(self._subscriptions)

        if unsubscribe_count > 0:
            self._logger.link(f"[{controller_name}] Отписка от {unsubscribe_count} событий")

        for unsubscribe in self._subscriptions:
            unsubscribe()

        self._subscriptions.clear()
        self._wrappers.clear()

        self._logger.data(f"[{controller_name}] Очищен")

    # ---- ЗАЩИЩЁННЫЕ МЕТОДЫ ----
    def _subscribe(
        self,
        event_type: type[T],
        callback: Callable[[Event[T]], None]
    ) -> None:
        """
        Подписывается на событие с сохранением для отписки.

        Создаёт wrapper для проверки типа и сохраняет unsubscribe функцию.
        """
        controller_name = self.__class__.__name__
        callback_name = getattr(callback, '__name__', str(callback))

        self._logger.link(f"[{controller_name}] Подписка на {event_type.__name__} -> {callback_name}")

        def wrapper(event: Event) -> None:
            if isinstance(event.data, event_type):
                typed_event = cast(Event[T], event)
                callback(typed_event)
            else:
                self._logger.warning(
                    f"[{controller_name}] Ожидался {event_type.__name__}, "
                    f"получен {type(event.data).__name__}"
                )

        self._wrappers.append(wrapper)
        unsubscribe = self._bus.subscribe(event_type, wrapper)
        self._subscriptions.append(unsubscribe)

        self._logger.link(f"[{controller_name}] Подписка на {event_type.__name__} оформлена")

    def _emit_error(
        self,
        node: Optional[NodeIdentifier],
        error: Exception,
        extra_context: Optional[dict] = None
    ) -> None:
        """
        Централизованная эмиссия ошибок.

        Собирает контекст (контроллер, тип ошибки) и отправляет DataError.
        """
        error_msg = str(error)
        error_type = error.__class__.__name__
        controller_name = self.__class__.__name__

        self._logger.error(f"[{controller_name}] Ошибка: {error_type} - {error_msg}")

        context = {
            'controller': controller_name,
            'error_type': error_type,
        }
        if extra_context:
            context.update(extra_context)

        full_error = f"{error_msg} [context: {context}]"

        self._bus.emit(DataError(
            node_type=node.node_type.value if node else "unknown",
            node_id=node.node_id if node else 0,
            error=full_error,
        ))