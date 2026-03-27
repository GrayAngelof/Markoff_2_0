# client/src/core/event_bus.py
"""
ФАСАД для работы с шиной событий (type-based).

EventBus — центральный диспетчер событий в приложении.
Все компоненты общаются только через него, что обеспечивает
слабую связанность и тестируемость.

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
- События — классы, наследующие EventData (типобезопасность)
- Подписка по типу события, а не по строке
- Event envelope с метаданными (источник, время)
- Слабые ссылки для предотвращения утечек памяти

Пример использования:
    bus = EventBus()
    
    def handler(event: Event[NodeSelected]) -> None:
        print(f"Выбран узел: {event.data.node.display}")
    
    unsubscribe = bus.subscribe(NodeSelected, handler)
    bus.emit(NodeSelected(node=NodeIdentifier(NodeType.COMPLEX, 42)))
    unsubscribe()  # Отписка
"""
import weakref
import inspect
from typing import Dict, List, Type, Callable, Optional, Any, Union, Protocol, cast
from datetime import datetime

from utils.logger import get_logger
from .types.event_structures import EventData, Event

log = get_logger(__name__)


class EventHandler(Protocol):
    """Протокол для обработчиков событий (строгая типизация callback)."""
    def __call__(self, event: Event[Any]) -> None:
        """
        Обрабатывает событие.
        
        Args:
            event: Конверт события с данными и метаданными
        """
        ...


# Тип для хранения в кэше (универсальный)
_CallbackType = Union[Callable, weakref.ReferenceType]


class EventBus:
    """
    Единая шина событий для всего приложения (type-based).
    
    Принципы работы:
    1. Подписка по типу события (класс, наследующий EventData)
    2. Использование слабых ссылок для предотвращения утечек
    3. Автоматическая очистка мёртвых подписок
    4. Типобезопасность через Protocol
    """
    
    def __init__(self, debug: bool = False) -> None:
        """
        Инициализирует шину событий.
        
        Args:
            debug: Включить детальное логирование
        """
        log.info("Инициализация EventBus")
        # Реестр подписок: тип события -> список слабых ссылок на callback'и
        self._subscribers: Dict[Type[EventData], List[weakref.ref]] = {}
        
        # Хранилище для восстановления callback'ов
        self._callbacks: Dict[int, _CallbackType] = {}
        self._next_id = 0
        
        # Режим отладки
        self._debug = debug
        
        # Статистика
        self._stats = {
            'total_emits': 0,
            'total_subscribes': 0,
            'total_unsubscribes': 0,
            'dead_callbacks_cleaned': 0
        }
        
        log.system("EventBus инициализирован")
        if debug:
            log.debug("Режим отладки включен")
    
    def _get_callback_info(self, callback: Callable) -> tuple[str, str]:
        """
        Возвращает информацию о callback для логирования.
        
        Returns:
            tuple: (тип_ссылки, описание_обработчика)
        """
        if inspect.ismethod(callback):
            obj = callback.__self__
            class_name = obj.__class__.__name__ if obj else "Unknown"
            handler_desc = f"{class_name}.{callback.__name__}"
            ref_type = "слабая (метод)"
        else:
            handler_desc = getattr(callback, '__name__', str(callback))
            ref_type = "слабая (функция)"
        
        return ref_type, handler_desc
    
    def subscribe(self, event_type: Type[EventData], callback: EventHandler) -> Callable[[], None]:
        """
        Подписывает обработчик на указанный тип события.
        
        Args:
            event_type: Класс события (наследник EventData)
            callback: Функция-обработчик или метод
            
        Returns:
            Callable: Функция для отписки
        """
        self._stats['total_subscribes'] += 1
        callback_id = self._next_id
        self._next_id += 1
        
        # Получаем информацию о callback для логирования
        ref_type, handler_desc = self._get_callback_info(callback)
        
        # Определяем тип callback и создаём слабую ссылку
        if inspect.ismethod(callback):
            ref = weakref.WeakMethod(callback)
        else:
            ref = weakref.ref(callback)
        
        self._callbacks[callback_id] = ref
        
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(ref)
        
        # Логируем подписку с информацией о типе ссылки
        log.link(f"Подписка {handler_desc} на {event_type.__name__} [{ref_type}]")
        
        def unsubscribe() -> None:
            """Функция отписки."""
            if ref in self._subscribers.get(event_type, []):
                self._subscribers[event_type].remove(ref)
            self._callbacks.pop(callback_id, None)
            self._stats['total_unsubscribes'] += 1
            log.link(f"Отписка {handler_desc} от {event_type.__name__}")
        
        return unsubscribe
    
    def _cleanup_dead(self) -> int:
        """
        Удаляет мёртвые ссылки из реестра подписок.

        Returns:
            int: Количество удалённых подписок
        """
        dead_count = 0

        for event_type, callbacks in list(self._subscribers.items()):
            alive = []
            for ref in callbacks:
                callback = ref()
                if callback is not None:
                    alive.append(ref)
                else:
                    dead_count += 1

            if alive:
                self._subscribers[event_type] = alive
            else:
                del self._subscribers[event_type]

        if dead_count > 0:
            log.debug(f"Очищено {dead_count} мёртвых подписок")

        return dead_count

    def emit(self, event_data: EventData, source: Optional[str] = None) -> None:
        """
        Испускает событие, уведомляя всех подписчиков.
        
        Args:
            event_data: Данные события (наследник EventData)
            source: Источник события (для отладки)
        """
        if event_data is None:
            raise ValueError("Event data cannot be None")
        
        self._stats['total_emits'] += 1
        
        # Создаём конверт события
        envelope = Event(
            data=event_data,
            source=source,
            timestamp=datetime.now()
        )
        
        event_type = type(event_data)
        
        # Очищаем мёртвые ссылки
        dead_count = self._cleanup_dead()
        if dead_count > 0:
            self._stats['dead_callbacks_cleaned'] += dead_count
        
        # Получаем подписчиков
        subscribers = self._subscribers.get(event_type, [])
        
        if not subscribers:
            if self._debug:
                log.debug(f"Нет подписчиков на {event_type.__name__}")
            return
        
        # Логирование испускания события
        source_str = f" от {source}" if source else ""
        log.info(f"Испускание {event_type.__name__}{source_str}")
        
        if self._debug:
            log.debug(f"Оповещение {len(subscribers)} подписчиков")
        
        # Уведомляем всех подписчиков
        for ref in subscribers:
            callback = ref()
            if callback is None:
                continue
            
            try:
                handler = cast(EventHandler, callback)
                handler(envelope)
            except Exception as e:
                log.error(f"Ошибка в обработчике {event_type.__name__}: {e}")
                import traceback
                traceback.print_exc()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику использования шины.
        
        Returns:
            Dict с ключами:
            - total_emits: всего испущено событий
            - total_subscribes: всего подписок
            - total_unsubscribes: всего отписок
            - dead_callbacks_cleaned: очищено мёртвых ссылок
            - subscribers_by_type: количество подписчиков по типам
        """
        subscribers_by_type = {
            event_type.__name__: len(callbacks)
            for event_type, callbacks in self._subscribers.items()
        }
        
        active_subscriptions = sum(len(callbacks) for callbacks in self._subscribers.values())
        
        stats = {
            **self._stats,
            'subscribers_by_type': subscribers_by_type,
            'total_subscriptions': len(self._subscribers),
            'active_subscriptions': active_subscriptions
        }
        
        log.info("Статистика EventBus запрошена")
        if self._debug:
            log.debug(f"Всего испусканий: {stats['total_emits']}")
            log.debug(f"Всего подписок: {stats['total_subscribes']}")
            log.debug(f"Активных подписок: {stats['active_subscriptions']}")
            log.debug(f"Очищено мёртвых: {stats['dead_callbacks_cleaned']}")
        
        return stats
    
    def clear(self) -> None:
        """
        Очищает все подписки.
        
        Используется при завершении приложения или для полного сброса.
        """
        count = sum(len(callbacks) for callbacks in self._subscribers.values())
        self._subscribers.clear()
        self._callbacks.clear()
        self._next_id = 0
        
        # Сбрасываем статистику (сохраняем total_* для истории)
        self._stats = {
            'total_emits': self._stats['total_emits'],
            'total_subscribes': self._stats['total_subscribes'],
            'total_unsubscribes': self._stats['total_unsubscribes'],
            'dead_callbacks_cleaned': self._stats['dead_callbacks_cleaned']
        }
        
        log.system(f"EventBus очищен (удалено {count} подписок)")
    
    def set_debug(self, enabled: bool) -> None:
        """
        Включает или выключает режим отладки.
        
        Args:
            enabled: True для включения детального логирования
        """
        self._debug = enabled
        log.info(f"Режим отладки EventBus: {'включён' if enabled else 'выключен'}")
    
    @property
    def debug(self) -> bool:
        """Возвращает текущий режим отладки."""
        return self._debug
    
    def get_subscriber_count(self, event_type: Optional[Type[EventData]] = None) -> Union[int, Dict[str, int]]:
        """
        Возвращает количество подписчиков для указанного типа события.
        ТОЛЬКО ДЛЯ ТЕСТОВ И ОТЛАДКИ.
        
        Args:
            event_type: Класс события. Если None, возвращает словарь для всех типов.
        """
        if event_type is not None:
            return len(self._subscribers.get(event_type, []))
        
        return {
            event_type.__name__: len(callbacks)
            for event_type, callbacks in self._subscribers.items()
        }