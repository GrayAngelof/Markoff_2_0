# client/src/controllers/base.py
"""
Базовый контроллер — общая подписка/отписка и обработка ошибок.

Все контроллеры наследуются от этого класса.
"""

from typing import List, Callable, TypeVar, Generic, Optional, Any, cast
from src.core import EventBus
from src.core.types import Event, EventData, NodeIdentifier
from src.core.events import DataError
from utils.logger import get_logger

log = get_logger(__name__)

T = TypeVar('T', bound=EventData)


class BaseController:
    """
    Базовый класс для всех контроллеров.
    
    Предоставляет:
    - Подписку на события с сохранением для отписки
    - Централизованную обработку ошибок
    - Метод cleanup для освобождения ресурсов
    - Хранение wrapper'ов для предотвращения их удаления GC
    """
    
    def __init__(self, bus: EventBus):
        """
        Инициализирует базовый контроллер.
        
        Args:
            bus: Шина событий
        """
        self._bus = bus
        # Храним unsubscribe функции
        self._subscriptions: List[Callable[[], None]] = []
        # Храним wrapper'ы, чтобы они не были удалены GC
        self._wrappers: List[Callable] = []
        # Используем __name__ для правильного пути модуля
        self._logger = get_logger(__name__)
        
        # DEBUG - базовый класс, не конечный компонент
        self._logger.system(f"{self.__class__.__name__} создан")
    
    def _subscribe(
        self,
        event_type: type[T],
        callback: Callable[[Event[T]], None]
    ) -> None:
        """
        Подписывается на событие с сохранением для отписки.
        
        Args:
            event_type: Тип события (класс)
            callback: Функция-обработчик
        """
        callback_name = getattr(callback, '__name__', str(callback))
        
        # LINK категория для подписок (установка связей между компонентами)
        self._logger.link(f"Подписка на {event_type.__name__} -> {callback_name}")
        
        # Создаем wrapper, который будет проверять тип
        def wrapper(event: Event) -> None:
            # Проверяем, что event.data имеет ожидаемый тип
            if isinstance(event.data, event_type):
                # Приводим к правильному типу
                typed_event = cast(Event[T], event)
                callback(typed_event)
            else:
                self._logger.warning(
                    f"Ожидался {event_type.__name__}, получен {type(event.data).__name__}"
                )
        
        # Сохраняем wrapper, чтобы он не был удален GC
        self._wrappers.append(wrapper)
        
        # Подписываемся на событие
        unsubscribe = self._bus.subscribe(event_type, wrapper)
        self._subscriptions.append(unsubscribe)
        
        self._logger.link(f"Подписка на {event_type.__name__} оформлена")
    
    def _emit_error(
        self,
        node: Optional[NodeIdentifier],
        error: Exception,
        extra_context: Optional[dict] = None
    ) -> None:
        """
        Централизованная эмиссия ошибок.
        
        Args:
            node: Идентификатор узла (если есть)
            error: Исключение
            extra_context: Дополнительный контекст
        """
        error_msg = str(error)
        error_type = error.__class__.__name__
        
        self._logger.error(
            f"Ошибка в {self.__class__.__name__}: {error_type} - {error_msg}"
        )
        
        # Собираем контекст
        context = {
            'controller': self.__class__.__name__,
            'error_type': error_type,
        }
        if extra_context:
            context.update(extra_context)
        
        # Добавляем контекст в сообщение ошибки
        full_error = f"{error_msg} [context: {context}]"
        
        self._bus.emit(DataError(
            node_type=node.node_type.value if node else "unknown",
            node_id=node.node_id if node else 0,
            error=full_error
        ))
    
    def cleanup(self) -> None:
        """Отписывается от всех событий и освобождает ресурсы."""
        unsubscribe_count = len(self._subscriptions)
        
        if unsubscribe_count > 0:
            self._logger.link(f"Отписка от {unsubscribe_count} событий")
        
        for unsubscribe in self._subscriptions:
            unsubscribe()
        
        self._subscriptions.clear()
        self._wrappers.clear()
        
        self._logger.debug(f"{self.__class__.__name__} очищен")