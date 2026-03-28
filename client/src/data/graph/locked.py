# client/src/data/graph/locked.py
"""
Базовый класс для потокобезопасных компонентов.

Предоставляет RLock для синхронизации доступа к общим данным.
Все компоненты графа, работающие с разделяемыми индексами,
должны наследоваться от этого класса.
"""

# ===== ИМПОРТЫ =====
from threading import RLock
from typing import Any, Callable, TypeVar


# ===== ТИПЫ =====
T = TypeVar('T')


# ===== КЛАСС =====
class LockedComponent:
    """Базовый класс для компонентов с RLock."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        self._lock = RLock()

    # ---- ЗАЩИЩЁННЫЕ МЕТОДЫ ----
    def _synchronized(self, func: Callable[..., T]) -> T:
        """
        Выполняет функцию под блокировкой.

        Используется для атомарного выполнения операций,
        требующих синхронизации доступа к разделяемым данным.

        Example:
            def get_value(self) -> str:
                return self._synchronized(lambda: self._data)
        """
        with self._lock:
            return func()