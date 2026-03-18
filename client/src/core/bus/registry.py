# client/src/core/bus/registry.py
"""
ПРИВАТНЫЙ МОДУЛЬ: реестр подписок на события.

Предоставляет класс _SubscriptionRegistry, который хранит все подписки
и управляет их жизненным циклом. Использует _WeakCallback для слабых ссылок.

ВНУТРЕННИЙ МОДУЛЬ - не для внешнего использования!
"""
from typing import Dict, List, Callable, Optional, Any
from collections import defaultdict
import time

from utils.logger import get_logger
from .weak_callback import _WeakCallback

# Создаём логгер для этого модуля
log = get_logger(__name__)


class _SubscriptionRegistry:
    """
    Реестр подписок на события.
    
    Хранит подписчиков в словаре {тип_события: список слабых ссылок}
    Предоставляет методы для регистрации, уведомления и очистки.
    
    ВНУТРЕННИЙ КЛАСС - не для внешнего использования!
    """
    
    def __init__(self) -> None:
        """Инициализирует пустой реестр подписок."""
        # Основное хранилище: тип события -> список _WeakCallback
        self._subscribers: Dict[str, List[_WeakCallback]] = defaultdict(list)
        
        # Статистика
        self._stats = {
            'total_registrations': 0,
            'total_notifications': 0,
            'total_cleaned': 0
        }
        
        log.success("✅ _SubscriptionRegistry инициализирован")
    
    def register(self, event_type: str, callback: Callable) -> Callable[[], None]:
        """
        Регистрирует подписку на событие.
        
        Args:
            event_type: Тип события
            callback: Функция-обработчик
            
        Returns:
            Callable: Функция для отписки
            
        Логирование:
            - DEBUG: при регистрации с деталями о типе callback
        """
        self._stats['total_registrations'] += 1
        
        # Создаём слабую ссылку
        weak_ref = _WeakCallback(callback)
        
        # Сохраняем в реестр
        self._subscribers[event_type].append(weak_ref)
        
        # Определяем тип для логирования
        callback_type = "метод" if weak_ref._is_method else "функция"
        
        log.debug(f"📝 Зарегистрирован подписчик на {event_type}")
        log.debug(f"   Тип callback: {callback_type}")
        log.debug(f"   Имя: {weak_ref._callback_name}")
        log.debug(f"   Всего подписчиков на {event_type}: {len(self._subscribers[event_type])}")
        
        def unsubscribe() -> None:
            """
            Удаляет эту конкретную подписку.
            """
            for i, existing_ref in enumerate(self._subscribers[event_type]):
                if existing_ref is weak_ref:
                    self._subscribers[event_type].pop(i)
                    log.debug(f"❌ Удалена подписка на {event_type}")
                    break
        
        return unsubscribe
    
    def get_subscribers(self, event_type: str) -> List[_WeakCallback]:
        """
        Возвращает список подписчиков на событие.
        
        Args:
            event_type: Тип события
            
        Returns:
            List[_WeakCallback]: Копия списка подписчиков
        """
        # Возвращаем копию, чтобы внешний код не мог изменить оригинал
        return list(self._subscribers.get(event_type, []))
    
    def notify(self, event_type: str, event: Dict[str, Any]) -> int:
        """
        Уведомляет всех подписчиков о событии.
        
        Args:
            event_type: Тип события
            event: Данные события
            
        Returns:
            int: Количество очищенных мёртвых подписок
            
        Логирование:
            - DEBUG: количество подписчиков, время выполнения
            - ERROR: ошибки в обработчиках
            - DEBUG: обнаружение мёртвых подписок
        """
        self._stats['total_notifications'] += 1
        
        if event_type not in self._subscribers:
            log.debug(f"📢 Нет подписчиков на {event_type}")
            return 0
        
        # Копируем список для безопасной итерации
        subscribers = list(self._subscribers[event_type])
        dead_indices = []
        
        log.debug(f"📢 Уведомление {len(subscribers)} подписчиков на {event_type}")
        
        for i, weak_ref in enumerate(subscribers):
            # ШАГ 1: СНАЧАЛА проверяем, жив ли callback
            if not weak_ref.is_alive():
                dead_indices.append(i)
                log.debug(f"💀 Мёртвая подписка #{i} на {event_type} (обнаружена до вызова)")
                continue
            
            # ШАГ 2: ТОЛЬКО ПОТОМ получаем callback
            callback = weak_ref.get()
            
            # ШАГ 3: Проверяем, что callback действительно жив
            if callback is None:
                # Если get вернул None, значит объект умер между проверками
                dead_indices.append(i)
                log.debug(f"💀 Мёртвая подписка #{i} на {event_type} (умерла между проверками)")
                continue
            
            # ШАГ 4: Вызываем живой callback
            try:
                start_time = time.time()
                callback(event)
                duration = (time.time() - start_time) * 1000  # в мс
                
                callback_name = getattr(callback, '__name__', str(callback))
                log.debug(f"✅ Обработчик {callback_name} выполнен за {duration:.2f}мс")
                
            except Exception as e:
                log.error(f"❌ Ошибка в обработчике для {event_type}: {e}")
                import traceback
                traceback.print_exc()
        
        # ШАГ 5: Удаляем мёртвые подписки (в обратном порядке)
        if dead_indices:
            for i in sorted(dead_indices, reverse=True):
                self._subscribers[event_type].pop(i)
            
            count = len(dead_indices)
            self._stats['total_cleaned'] += count
            log.debug(f"🧹 Удалено {count} мёртвых подписок из {event_type}")
            
            return count
        
        return 0
    
    def get_count(self, event_type: str) -> int:
        """
        Возвращает количество живых подписчиков на событие.
        
        Args:
            event_type: Тип события
            
        Returns:
            int: Количество живых подписчиков
            
        Логирование:
            - DEBUG: при подсчёте с очисткой мёртвых
        """
        if event_type not in self._subscribers:
            return 0
        
        # Очищаем мёртвые и считаем
        alive = 0
        dead_indices = []
        
        for i, weak_ref in enumerate(self._subscribers[event_type]):
            if weak_ref.is_alive():
                alive += 1
            else:
                dead_indices.append(i)
        
        # Удаляем мёртвые
        if dead_indices:
            for i in sorted(dead_indices, reverse=True):
                self._subscribers[event_type].pop(i)
            
            count = len(dead_indices)
            self._stats['total_cleaned'] += count
            log.debug(f"🧹 При подсчёте удалено {count} мёртвых подписок из {event_type}")
        
        log.debug(f"📊 На {event_type} {alive} живых подписчиков")
        return alive
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику реестра.
        
        Returns:
            Dict: Статистика использования
            
        Логирование:
            - DEBUG: детальная статистика
        """
        # Подсчитываем живых подписчиков по типам
        by_type = {}
        total_alive = 0
        
        for event_type in list(self._subscribers.keys()):
            count = self.get_count(event_type)  # заодно чистит мёртвые
            if count > 0:
                by_type[event_type] = count
                total_alive += count
        
        stats = {
            'by_type': by_type,
            'total': len(self._subscribers),
            'active': total_alive,
            'stats': self._stats.copy()
        }
        
        log.debug(f"📊 Статистика реестра: {stats['active']} активных подписок, всего удалено: {self._stats['total_cleaned']}")
        
        return stats
    
    def clear(self) -> int:
        """
        Полностью очищает все подписки.
        
        Returns:
            int: Количество удалённых подписок
            
        Логирование:
            - INFO: при очистке
            - DEBUG: количество удалённых подписок
        """
        total = sum(len(subs) for subs in self._subscribers.values())
        self._subscribers.clear()
        log.info(f"🧹 Реестр очищен: удалено {total} подписок")
        return total