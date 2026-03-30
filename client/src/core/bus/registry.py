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
from typing import Callable, Dict, List, Type

from utils.logger import get_logger
from .weak_callback import _WeakCallback
from ..types.event_structures import Event, EventData


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
        self._subscribers: Dict[Type[EventData], List[_WeakCallback]] = defaultdict(list)

        log.system("SubscriptionRegistry инициализирован")

    def clear(self) -> int:
        """
        Полностью очищает все подписки.

        Returns:
            Количество удалённых подписок
        """
        total = sum(len(subs) for subs in self._subscribers.values())
        self._subscribers.clear()
        log.info(f"Реестр очищен: удалено {total} подписок")
        return total

    # ---- УПРАВЛЕНИЕ ПОДПИСКАМИ ----
    def register(
        self,
        event_type: Type[EventData],
        callback: Callable[[Event[EventData]], None],
    ) -> Callable[[], None]:
        """
        Регистрирует подписку на событие.

        Returns:
            Функция для отписки
        """
        weak_ref = _WeakCallback(callback)
        self._subscribers[event_type].append(weak_ref)

        callback_type = "метод" if weak_ref._is_method else "функция"
        log.link(f"Зарегистрирован {callback_type} {weak_ref._callback_name} на {event_type.__name__}")
        log.debug(f"Всего подписчиков на {event_type.__name__}: {len(self._subscribers[event_type])}")

        def unsubscribe() -> None:
            """Удаляет эту подписку."""
            for i, existing_ref in enumerate(self._subscribers[event_type]):
                if existing_ref is weak_ref:
                    self._subscribers[event_type].pop(i)
                    log.link(f"Удалена подписка на {event_type.__name__}")
                    break

        return unsubscribe

    # ---- УВЕДОМЛЕНИЕ ПОДПИСЧИКОВ ----
    def notify(self, event_type: Type[EventData], event: Event[EventData]) -> int:
        """
        Уведомляет всех подписчиков о событии.

        Returns:
            Количество очищенных мёртвых подписок
        """
        if event_type not in self._subscribers:
            log.debug(f"Нет подписчиков на {event_type.__name__}")
            return 0

        subscribers = list(self._subscribers[event_type])
        dead_indices = []

        log.debug(f"Уведомление {len(subscribers)} подписчиков на {event_type.__name__}")

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
                log.error(f"Ошибка в обработчике для {event_type.__name__}: {e}")
                import traceback
                traceback.print_exc()

        if dead_indices:
            return self._cleanup(event_type, dead_indices)

        return 0

    # ---- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ----
    def _cleanup(self, event_type: Type[EventData], dead_indices: List[int]) -> int:
        """
        Удаляет мёртвые подписки по индексам.

        Returns:
            Количество удалённых подписок
        """
        for i in sorted(dead_indices, reverse=True):
            self._subscribers[event_type].pop(i)

        count = len(dead_indices)
        log.debug(f"Удалено {count} мёртвых подписок из {event_type.__name__}")
        return count

    def get_count(self, event_type: Type[EventData]) -> int:
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

        if dead_indices:
            self._cleanup(event_type, dead_indices)

        log.debug(f"На {event_type.__name__} {alive} живых подписчиков")
        return alive