# client/src/core/bus/weak_callback.py
"""
Слабые ссылки на callback'и.

Внутренний модуль EventBus. Позволяет хранить callback'и, не препятствуя
сборке мусора объектов, на которые они ссылаются.

НЕ ДЛЯ ВНЕШНЕГО ИСПОЛЬЗОВАНИЯ!
"""

# ===== ИМПОРТЫ =====
import inspect
import weakref
from typing import Callable, Optional

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class _WeakCallback:
    """
    Слабая ссылка на callback (функцию или метод).

    Позволяет:
    - Хранить callback без препятствования сборке мусора
    - Проверять, жив ли callback
    - Безопасно вызывать callback, если он жив

    ВНУТРЕННИЙ КЛАСС — не для внешнего использования!
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, callback: Callable) -> None:
        """Создаёт слабую ссылку на callback."""
        self._is_method = inspect.ismethod(callback)
        self._callback_name = self._get_name(callback)

        if self._is_method:
            # Метод: храним слабую ссылку на объект и имя метода
            obj = getattr(callback, '__self__', None)
            self._obj_ref = weakref.ref(obj) if obj is not None else None
            self._method_name = getattr(callback, '__name__', None)
            self._func_ref = None
        else:
            # Функция или другой callable: храним слабую ссылку на сам объект
            self._obj_ref = None
            self._method_name = None
            self._func_ref = weakref.ref(callback)

        log.debug(f"Создана слабая ссылка на {self._callback_name}")

    # ---- ПУБЛИЧНОЕ API ----
    def get(self) -> Optional[Callable]:
        """
        Возвращает живой callback или None, если объект удалён.

        Вызов этого метода не должен препятствовать сборке мусора.
        """
        if self._is_method:
            if self._obj_ref is None:
                return None

            obj = self._obj_ref()
            if obj is None or self._method_name is None:
                return None

            method = getattr(obj, self._method_name, None)
            return method if callable(method) else None

        # Для функций и других callable
        if self._func_ref is None:
            return None

        func = self._func_ref()
        return func if callable(func) else None

    def is_alive(self) -> bool:
        """Проверяет, жив ли ещё callback."""
        if self._is_method:
            if self._obj_ref is None:
                return False
            obj = self._obj_ref()
            return obj is not None
        else:
            if self._func_ref is None:
                return False
            func = self._func_ref()
            return func is not None

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _get_name(self, callback: Callable) -> str:
        """Безопасно получает имя callback'а для логирования."""
        base_name = getattr(callback, '__name__', str(callback))

        if inspect.ismethod(callback):
            obj = callback.__self__
            class_name = getattr(obj, '__class__', None)
            if class_name is not None:
                class_name = getattr(class_name, '__name__', 'Unknown')
                return f"{class_name}.{base_name}"

        return str(base_name)

    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        status = "жив" if self.is_alive() else "мёртв"
        kind = "метод" if self._is_method else "функция"
        return f"_WeakCallback({kind} {self._callback_name}, {status})"