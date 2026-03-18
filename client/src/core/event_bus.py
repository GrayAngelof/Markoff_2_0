# client/src/core/event_bus.py
"""
ФАСАД для работы с шиной событий.

Этот модуль предоставляет публичный интерфейс EventBus,
скрывая все детали реализации в пакете .bus/

EventBus - это центральный диспетчер событий в приложении.
Все компоненты общаются только через него, что обеспечивает
слабую связанность и тестируемость.

Пример использования:
    bus = EventBus(debug=True)
    
    def handler(event):
        print(f"Получено: {event}")
    
    unsubscribe = bus.subscribe('ui.node_selected', handler)
    bus.emit('ui.node_selected', {'node_id': 42})
    unsubscribe()  # Отписка
"""
from typing import Callable, Optional, Dict, Any, Union
import time

from utils.logger import get_logger
from .bus.registry import _SubscriptionRegistry
from .bus.weak_callback import _WeakCallback

# Создаём логгер для этого модуля
log = get_logger(__name__)


class EventBus:
    """
    Единая шина событий для всего приложения.
    
    Этот класс является ФАСАДОМ, который делегирует всю работу
    внутренним компонентам (_SubscriptionRegistry, _WeakCallback).
    
    Публичный интерфейс:
    - subscribe() - подписка на события
    - emit() - испускание событий
    - get_stats() - статистика использования
    - clear() - очистка всех подписок
    
    Внутренние детали полностью скрыты от внешнего мира.
    """
    
    def __init__(self, debug: bool = False) -> None:
        """
        Инициализирует шину событий.
        
        Args:
            debug: Включить детальное логирование (по умолчанию False)
        
        Логирование:
            - SUCCESS: при успешной инициализации
            - INFO: при изменении режима отладки
            - DEBUG: при каждом emit/subscribe если debug=True
        """
        # Внутренний реестр подписок (приватный!)
        self._registry = _SubscriptionRegistry()
        
        # Режим отладки
        self._debug = debug
        
        # Статистика
        self._stats = {
            'total_emits': 0,
            'total_subscribes': 0,
            'total_unsubscribes': 0,
            'dead_callbacks_cleaned': 0
        }
        
        log.success(f"✅ EventBus инициализирован (debug={debug})")
        log.info(f"📊 EventBus stats initialized: {self._stats}")
    
    def subscribe(self, event_type: str, callback: Callable) -> Callable[[], None]:
        """
        Подписывает обработчик на указанный тип события.
        
        Args:
            event_type: Тип события (строка из events.py)
            callback: Функция-обработчик или метод класса
            
        Returns:
            Callable: Функция для отписки
        """
        self._stats['total_subscribes'] += 1
        
        # Используем inspect для безопасного определения типа callback
        import inspect
        is_method = inspect.ismethod(callback)
        is_function = inspect.isfunction(callback)
        
        if is_method:
            callback_type = "метод"
            method_name = getattr(callback, '__name__', 'unknown')
            # Безопасно получаем класс
            obj = getattr(callback, '__self__', None)
            if obj is not None:
                class_name = getattr(obj, '__class__', None)
                if class_name is not None:
                    class_name = getattr(class_name, '__name__', 'Unknown')
                else:
                    class_name = 'Unknown'
            else:
                class_name = 'Unknown'
            log.debug(f"🔍 Подписка: метод {class_name}.{method_name}")
        else:
            callback_type = "функция"
            function_name = getattr(callback, '__name__', str(callback))
            log.debug(f"🔍 Подписка: функция {function_name}")
        
        # Делегируем регистрацию внутреннему компоненту
        unsubscribe = self._registry.register(event_type, callback)
        
        log.info(f"📝 Подписка на '{event_type}' ({callback_type})")
        log.debug(f"📊 Всего подписок после подписки: {self._registry.get_count(event_type)}")
        
        # Оборачиваем функцию отписки для сбора статистики
        def wrapped_unsubscribe() -> None:
            unsubscribe()
            self._stats['total_unsubscribes'] += 1
            log.info(f"❌ Отписка от '{event_type}'")
        
        return wrapped_unsubscribe
    
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None, 
             source: Optional[str] = None) -> None:
        """
        Испускает событие, уведомляя всех подписчиков.
        
        Args:
            event_type: Тип события
            data: Данные события (словарь)
            source: Источник события (для отладки)
            
        Логирование:
            - INFO: каждое испускание события
            - DEBUG: количество подписчиков, время выполнения
            - ERROR: ошибки в обработчиках
            - WARNING: если нет подписчиков (при debug=True)
            
        Пример:
            bus.emit('ui.node_selected', 
                    {'node_type': 'complex', 'node_id': 42},
                    source='tree_view')
        """
        self._stats['total_emits'] += 1
        
        # Формируем событие
        event = {
            'type': event_type,
            'data': data if data is not None else {},
            'source': source,
            'timestamp': time.time()
        }
        
        # Логируем
        source_str = f" от {source}" if source else ""
        log.info(f"📢 EMIT {event_type}{source_str}")
        
        # Получаем подписчиков
        subscribers = self._registry.get_subscribers(event_type)
        count = len(subscribers)
        
        if count == 0:
            log.debug(f"⚠️ Нет подписчиков на {event_type}")
            return
        
        log.debug(f"📋 Оповещение {count} подписчиков...")
        
        # Делегируем уведомление реестру
        dead_count = self._registry.notify(event_type, event)
        
        if dead_count > 0:
            self._stats['dead_callbacks_cleaned'] += dead_count
            log.debug(f"🧹 Очищено {dead_count} мёртвых подписок")
        
        log.debug(f"✅ EMIT {event_type} завершён")
    
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
            
        Логирование:
            - INFO: при запросе статистики
            - DEBUG: детальная статистика
        """
        # Получаем статистику от реестра
        registry_stats = self._registry.get_stats()
        
        stats = {
            **self._stats,
            'subscribers_by_type': registry_stats['by_type'],
            'total_subscriptions': registry_stats['total'],
            'active_subscriptions': registry_stats['active']
        }
        
        log.info(f"📊 Статистика EventBus запрошена")
        log.debug(f"  • Всего испусканий: {stats['total_emits']}")
        log.debug(f"  • Всего подписок: {stats['total_subscribes']}")
        log.debug(f"  • Активных подписок: {stats['active_subscriptions']}")
        log.debug(f"  • Очищено мёртвых: {stats['dead_callbacks_cleaned']}")
        
        return stats
    
    def clear(self) -> None:
        """
        Очищает все подписки.
        
        Используется при завершении приложения или для полного сброса.
        
        Логирование:
            - INFO: при очистке
            - DEBUG: количество удалённых подписок
        """
        count = self._registry.clear()
        log.info(f"🧹 EventBus очищен (удалено {count} подписок)")
        
        # Сбрасываем статистику (кроме total_*)
        self._stats = {
            'total_emits': self._stats['total_emits'],
            'total_subscribes': self._stats['total_subscribes'],
            'total_unsubscribes': self._stats['total_unsubscribes'],
            'dead_callbacks_cleaned': self._stats['dead_callbacks_cleaned']
        }
    
    def set_debug(self, enabled: bool) -> None:
        """
        Включает или выключает режим отладки.
        
        Args:
            enabled: True для включения детального логирования
        """
        self._debug = enabled
        log.info(f"🔧 Режим отладки EventBus: {'включён' if enabled else 'выключен'}")
    
    @property
    def debug(self) -> bool:
        """Возвращает текущий режим отладки."""
        return self._debug

    def get_subscriber_count(self, event_type: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Возвращает количество подписчиков для указанного типа события.
        ТОЛЬКО ДЛЯ ТЕСТОВ И ОТЛАДКИ.
        
        Args:
            event_type: Тип события. Если None, возвращает словарь для всех типов.
        """
        if event_type is not None:
            return self._registry.get_count(event_type)
        
        stats = self._registry.get_stats()
        return stats['by_type']