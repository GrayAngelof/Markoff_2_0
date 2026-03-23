# data/graph/locked.py
"""
Базовый класс для потокобезопасных компонентов.
"""

from threading import RLock
from typing import Callable, TypeVar, Any

T = TypeVar('T')


class LockedComponent:
    """Базовый класс для компонентов с RLock."""
    
    def __init__(self):
        self._lock = RLock()
    
    def _synchronized(self, func: Callable[..., T]) -> T:
        """Выполняет функцию под блокировкой."""
        with self._lock:
            return func()