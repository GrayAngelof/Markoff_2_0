# client/src/core/event_bus.py
"""
Центральная шина событий приложения.
Обеспечивает слабосвязанную коммуникацию между компонентами через подписку и испускание событий.

Критически важные моменты архитектуры:
1. Использует weakref.WeakMethod для методов, чтобы не удерживать объекты в памяти
2. Для обычных функций использует weakref.ref
3. Копирует список подписчиков при emit для безопасной модификации во время итерации
4. Уважает глобальные настройки логирования
"""
import weakref
import time
from typing import Dict, List, Callable, Optional, Any, Union
from collections import defaultdict
from utils.logger import get_logger, Logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class EventBus:
    """
    Единая шина событий для всего приложения.
    
    Принцип работы со слабыми ссылками:
    - Для методов: weakref.WeakMethod(callback) - хранит слабую ссылку на объект и имя метода
    - Для функций: weakref.ref(callback) - хранит слабую ссылку на функцию
    
    При emit:
    1. Пытаемся получить callable через ref()
    2. Если вернулся None - объект/функция удалены, убираем подписку
    3. Если вернулся callable - вызываем его
    """
    
    def __init__(self) -> None:
        """Инициализирует шину событий."""
        # Словарь подписчиков: event_type -> список слабых ссылок
        self._subscribers: Dict[str, List] = defaultdict(list)
        
        log.info("EventBus инициализирован")
    
    # ===== Публичные методы =====
    
    def subscribe(self, event_type: str, callback: Callable) -> Callable[[], None]:
        """
        Подписывает обработчик на указанный тип события.
        
        Args:
            event_type: Тип события
            callback: Функция-обработчик или метод
            
        Returns:
            Callable: Функция для отписки
        """
        # Определяем тип callback и создаём соответствующую слабую ссылку
        if hasattr(callback, '__self__') and hasattr(callback, '__func__'):
            # Это метод класса - используем WeakMethod
            ref = weakref.WeakMethod(callback)
            ref_type = "метод"
        else:
            # Это обычная функция или статический метод - используем weakref.ref
            ref = weakref.ref(callback)
            ref_type = "функция"
        
        # Сохраняем подписку
        self._subscribers[event_type].append(ref)
        
        # Логируем при INFO и выше
        method_name = getattr(callback, '__name__', str(callback))
        log.info(f"Подписка ({ref_type}) на '{event_type}': {method_name}")
        
        # Возвращаем функцию для отписки
        def unsubscribe() -> None:
            """Удаляет подписку."""
            # Ищем и удаляем эту конкретную подписку
            for i, existing_ref in enumerate(self._subscribers[event_type]):
                if existing_ref is ref:
                    self._subscribers[event_type].pop(i)
                    log.info(f"Отписка от '{event_type}': {method_name}")
                    break
        
        return unsubscribe
    
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
        """
        Испускает событие, уведомляя всех подписчиков.
    
        Args:
            event_type: Тип события
            data: Данные события (словарь) или None
            source: Источник события или None
    
        Важные моменты:
        1. Копируем список подписчиков перед итерацией
        2. При вызове ref() может вернуть None - значит объект/функция удалены
        3. Все ошибки в обработчиках логируются через log.error
        """
        # Формируем событие с защитой от None
        event = {
            'type': event_type,
            'data': data if data is not None else {},
            'source': source,
            'timestamp': time.time()
        }
    
        # Логируем emit при INFO и выше
        source_str = f" от {source}" if source else ""
        log.info(f"EMIT {event_type}{source_str}")
    
        # Получаем список подписчиков для этого типа
        subscribers = self._subscribers.get(event_type, [])
        if not subscribers:
            return
    
        # КРИТИЧЕСКИ ВАЖНО: копируем список, чтобы можно было менять оригинал
        # во время итерации (например, при отписке внутри обработчика)
        subscribers_copy = list(subscribers)
    
        # Собираем индексы мёртвых подписок для удаления
        dead_indices = []
    
        for i, ref in enumerate(subscribers_copy):
            # Пытаемся получить callable
            callback = ref()
    
            # Если callable умер (ref() вернул None) - помечаем для удаления
            if callback is None:
                # Находим индекс в оригинальном списке
                for j, original_ref in enumerate(subscribers):
                    if original_ref is ref:
                        dead_indices.append(j)
                continue
    
            # Вызываем живой callable
            try:
                callback(event)
            except Exception as e:
                log.error(f"Ошибка в обработчике для {event_type}: {e}")
                import traceback
                traceback.print_exc()
    
        # Удаляем мёртвые подписки (в обратном порядке) - ТОЛЬКО ОДИН РАЗ
        if dead_indices:
            # Сортируем в обратном порядке, чтобы удаление с конца не влияло на индексы в начале
            for i in sorted(dead_indices, reverse=True):
                # Проверяем, что индекс всё ещё существует (на случай, если список изменился)
                if i < len(self._subscribers[event_type]):
                    self._subscribers[event_type].pop(i)
    
            if Logger.is_debug_enabled():
                log.debug(f"Удалено {len(dead_indices)} мёртвых подписок из {event_type}")
    
    def get_subscriber_count(self, event_type: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """
        Возвращает количество живых подписчиков (для отладки).
        
        Args:
            event_type: Тип события. Если None, возвращает словарь для всех типов.
        
        Returns:
            Union[int, Dict[str, int]]: 
                - Если указан event_type: количество подписчиков для этого типа
                - Если event_type = None: словарь {тип_события: количество}
        """
        if event_type is not None:
            return self._cleanup_and_count(event_type)
        
        result = {}
        # Используем копию ключей, чтобы избежать изменения словаря во время итерации
        for et in list(self._subscribers.keys()):
            count = self._cleanup_and_count(et)
            if count > 0 or et in self._subscribers:
                result[et] = count
        
        return result
    
    def _cleanup_and_count(self, event_type: str) -> int:
        """Очищает мёртвые ссылки и возвращает количество живых."""
        if event_type not in self._subscribers:
            return 0
        
        dead_indices = []
        for i, ref in enumerate(self._subscribers[event_type]):
            if ref() is None:
                dead_indices.append(i)
        
        if dead_indices:
            for i in reversed(dead_indices):
                self._subscribers[event_type].pop(i)
            
            if Logger.is_debug_enabled():
                log.debug(f"Очистка {event_type}: удалено {len(dead_indices)} мёртвых ссылок")
        
        return len(self._subscribers[event_type])
    
    def clear(self) -> None:
        """Очищает все подписки."""
        self._subscribers.clear()
        log.info("EventBus: все подписки очищены")

    def set_debug(self, enabled: bool = True) -> None:
        """
        Включает или выключает debug-режим.
        
        Args:
            enabled: True для включения debug-логирования
        """
        self._debug = enabled
        log.debug(f"EventBus debug режим: {'включен' if enabled else 'выключен'}")