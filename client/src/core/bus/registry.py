# client/src/core/bus/registry.py
"""
Реестр подписок на события.

Внутренний модуль EventBus. Хранит подписки в виде слабых ссылок,
автоматически очищает мёртвые обработчики.

НЕ ДЛЯ ВНЕШНЕГО ИСПОЛЬЗОВАНИЯ!
"""

# ===== ИМПОРТЫ =====
import time
from collections import defaultdict
from typing import Dict, List, Callable, Optional, Any

from utils.logger import get_logger
from .weak_callback import _WeakCallback


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class _SubscriptionRegistry:
    """
    Реестр подписок на события.

    Хранит подписчиков в словаре {тип_события: список слабых ссылок}.
    Автоматически очищает мёртвые подписки при уведомлениях и подсчётах.

    ВНУТРЕННИЙ КЛАСС — не для внешнего использования!
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        """Инициализирует пустой реестр."""
        # Основное хранилище: тип события → список _WeakCallback
        self._subscribers: Dict[str, List[_WeakCallback]] = defaultdict(list)

        # Статистика работы
        self._stats = {
            'total_registrations': 0,
            'total_notifications': 0,
            'total_cleaned': 0,
        }

        log.system("SubscriptionRegistry инициализирован")

    def clear(self) -> int:
        """
        Полностью очищает все подписки.

        Returns:
            int: Количество удалённых подписок
        """
        total = sum(len(subs) for subs in self._subscribers.values())
        self._subscribers.clear()
        log.info(f"Реестр очищен: удалено {total} подписок")
        return total

    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику реестра.

        Returns:
            Dict: Статистика использования
        """
        # Подсчитываем живых подписчиков по типам
        by_type = {}
        total_alive = 0

        for event_type in list(self._subscribers.keys()):
            count = self.get_count(event_type)
            if count > 0:
                by_type[event_type] = count
                total_alive += count

        stats = {
            'by_type': by_type,
            'total': len(self._subscribers),
            'active': total_alive,
            'stats': self._stats.copy(),
        }

        log.debug(f"Статистика: {stats['active']} активных, удалено: {self._stats['total_cleaned']}")
        return stats

    # ---- УПРАВЛЕНИЕ ПОДПИСКАМИ ----
    def register(self, event_type: str, callback: Callable) -> Callable[[], None]:
        """
        Регистрирует подписку на событие.

        Returns:
            Callable: Функция для отписки
        """
        self._stats['total_registrations'] += 1

        weak_ref = _WeakCallback(callback)
        self._subscribers[event_type].append(weak_ref)

        callback_type = "метод" if weak_ref._is_method else "функция"
        log.link(f"Зарегистрирован {callback_type} {weak_ref._callback_name} на {event_type}")
        log.debug(f"Всего подписчиков на {event_type}: {len(self._subscribers[event_type])}")

        def unsubscribe() -> None:
            """Удаляет эту подписку."""
            for i, existing_ref in enumerate(self._subscribers[event_type]):
                if existing_ref is weak_ref:
                    self._subscribers[event_type].pop(i)
                    log.link(f"Удалена подписка на {event_type}")
                    break

        return unsubscribe

    # ---- УВЕДОМЛЕНИЕ ПОДПИСЧИКОВ ----
    def notify(self, event_type: str, event: Dict[str, Any]) -> int:
        """
        Уведомляет всех подписчиков о событии.

        Returns:
            int: Количество очищенных мёртвых подписок
        """
        self._stats['total_notifications'] += 1

        if event_type not in self._subscribers:
            log.debug(f"Нет подписчиков на {event_type}")
            return 0

        subscribers = list(self._subscribers[event_type])
        dead_indices = []

        log.debug(f"Уведомление {len(subscribers)} подписчиков на {event_type}")

        for i, weak_ref in enumerate(subscribers):
            if not weak_ref.is_alive():
                dead_indices.append(i)
                continue

            callback = weak_ref.get()
            if callback is None:
                dead_indices.append(i)
                continue

            try:
                start_time = time.time()
                callback(event)
                duration = (time.time() - start_time) * 1000

                callback_name = getattr(callback, '__name__', str(callback))
                log.debug(f"Обработчик {callback_name} выполнен за {duration:.2f}мс")

            except Exception as e:
                log.error(f"Ошибка в обработчике для {event_type}: {e}")
                import traceback
                traceback.print_exc()

        # Удаляем мёртвые подписки (в обратном порядке, чтобы не сбивать индексы)
        if dead_indices:
            for i in sorted(dead_indices, reverse=True):
                self._subscribers[event_type].pop(i)

            count = len(dead_indices)
            self._stats['total_cleaned'] += count
            log.debug(f"Удалено {count} мёртвых подписок из {event_type}")
            return count

        return 0

    # ---- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ----
    def get_subscribers(self, event_type: str) -> List[_WeakCallback]:
        """
        Возвращает копию списка подписчиков на событие.

        Используется только для отладки.
        """
        return list(self._subscribers.get(event_type, []))

    def get_count(self, event_type: str) -> int:
        """
        Возвращает количество живых подписчиков на событие.

        Автоматически очищает мёртвые подписки при подсчёте.
        """
        if event_type not in self._subscribers:
            return 0

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
            log.debug(f"При подсчёте удалено {count} мёртвых подписок из {event_type}")

        log.debug(f"На {event_type} {alive} живых подписчиков")
        return alive