# client/src/core/bus/weak_callback.py
"""
ПРИВАТНЫЙ МОДУЛЬ: слабые ссылки на callback'и.

Предоставляет класс _WeakCallback, который хранит слабую ссылку
на функцию или метод, позволяя сборщику мусора удалять объекты,
на которые больше нет сильных ссылок.

Использует inspect для безопасного определения типа callback.

ВНУТРЕННИЙ МОДУЛЬ - не для внешнего использования!
"""
import weakref
import inspect
from typing import Callable, Optional, Any
from types import MethodType, FunctionType

from utils.logger import get_logger

# Создаём логгер для этого модуля
log = get_logger(__name__)


class _WeakCallback:
    """
    Слабая ссылка на callback (функцию или метод).
    
    Позволяет:
    - Хранить callback, не препятствуя сборке мусора
    - Определять, жив ли ещё объект/функция
    - Безопасно вызывать callback, если он жив
    
    Использует inspect для корректного определения типа.
    
    ВНУТРЕННИЙ КЛАСС - не для внешнего использования!
    """
    
    def __init__(self, callback: Callable) -> None:
        """
        Создаёт слабую ссылку на callback.
        
        Args:
            callback: Функция или метод для слабого хранения
            
        Логирование:
            - DEBUG: при создании, с определением типа callback
        """
        # Используем inspect для определения типа
        self._is_method = inspect.ismethod(callback)
        self._is_function = inspect.isfunction(callback)
        
        # Сохраняем имя для логирования (БЕЗОПАСНО)
        self._callback_name = self._safe_get_name(callback)
        
        if self._is_method:
            # Для методов храним слабую ссылку на объект и имя метода
            # Используем getattr для безопасности
            obj = getattr(callback, '__self__', None)
            self._obj_ref = weakref.ref(obj) if obj is not None else None
            self._method_name = getattr(callback, '__name__', None)
            self._func_ref = None
            log.debug(f"🔗 Создана слабая ссылка на МЕТОД {self._callback_name}")
            
        elif self._is_function:
            # Для функций храним слабую ссылку на саму функцию
            self._obj_ref = None
            self._method_name = None
            self._func_ref = weakref.ref(callback)
            log.debug(f"🔗 Создана слабая ссылка на ФУНКЦИЮ {self._callback_name}")
            
        else:
            # Неизвестный тип - пробуем как функцию (может быть staticmethod и т.д.)
            self._is_method = False
            self._is_function = True
            self._obj_ref = None
            self._method_name = None
            self._func_ref = weakref.ref(callback)
            log.debug(f"🔗 Создана слабая ссылка на НЕИЗВЕСТНЫЙ тип {self._callback_name}")
    
    def _safe_get_name(self, callback: Callable) -> str:
        """
        Безопасно получает имя callback'а без обращения к несуществующим атрибутам.
        
        Args:
            callback: Callback для получения имени
            
        Returns:
            str: Имя callback'а или "unknown"
        """
        # Пробуем получить __name__ безопасно
        base_name = getattr(callback, '__name__', None)
        if base_name is None:
            base_name = str(callback)
        
        # Если это метод, добавляем имя класса
        if inspect.ismethod(callback):
            # У методов есть __self__ и __class__
            obj = callback.__self__
            class_name = getattr(obj, '__class__', None)
            if class_name is not None:
                class_name = getattr(class_name, '__name__', 'Unknown')
                return f"{class_name}.{base_name}"
        elif inspect.isfunction(callback):
            # Для функций просто возвращаем имя
            return base_name
        
        return str(base_name)
    
    def get(self) -> Optional[Callable]:
        """
        Возвращает живой callback или None, если объект/функция удалены.
        
        Returns:
            Callable если объект жив, иначе None
            
        Логирование:
            - DEBUG: при успешном получении живого callback
            - DEBUG: при обнаружении мёртвого callback
        """
        if self._is_method:
            # Для методов: получаем объект
            if self._obj_ref is None:
                log.debug(f"💀 Ссылка на объект метода {self._callback_name} отсутствует")
                return None
                
            obj = self._obj_ref()
            
            if obj is None:
                log.debug(f"💀 Объект метода {self._callback_name} удалён сборщиком мусора")
                return None
            
            # Получаем метод по имени
            if self._method_name is None:
                log.debug(f"💀 Имя метода {self._callback_name} отсутствует")
                return None
                
            method = getattr(obj, self._method_name, None)
            
            if method is None:
                log.debug(f"💀 Метод {self._method_name} не найден в объекте {obj}")
                return None
            
            # Проверяем, что это действительно вызываемый объект
            if callable(method):
                log.debug(f"✨ Живой метод {self._callback_name}")
                return method
            else:
                log.debug(f"💀 Атрибут {self._method_name} не является вызываемым")
                return None
        
        else:
            # Для функций: получаем функцию
            if self._func_ref is None:
                log.debug(f"💀 Ссылка на функцию {self._callback_name} отсутствует")
                return None
                
            func = self._func_ref()
            
            if func is None:
                log.debug(f"💀 Функция {self._callback_name} удалена сборщиком мусора")
                return None
            
            # Проверяем, что это действительно вызываемый объект
            if callable(func):
                log.debug(f"✨ Живая функция {self._callback_name}")
                return func
            else:
                log.debug(f"💀 Объект {self._callback_name} не является вызываемым")
                return None
    
    def is_alive(self) -> bool:
        """
        Проверяет, жив ли ещё callback.
        
        Returns:
            True если объект/функция ещё существуют
        """
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
    
    def __repr__(self) -> str:
        """Строковое представление для отладки."""
        status = "ЖИВ" if self.is_alive() else "МЁРТВ"
        if self._is_method:
            return f"_WeakCallback(МЕТОД {self._callback_name}, {status})"
        else:
            return f"_WeakCallback(ФУНКЦИЯ {self._callback_name}, {status})"


# Для обратной совместимости и более простого использования
def is_method(callback: Callable) -> bool:
    """
    Безопасно проверяет, является ли callback методом.
    
    Args:
        callback: Проверяемый callback
        
    Returns:
        True если это метод класса
    """
    return inspect.ismethod(callback)


def is_function(callback: Callable) -> bool:
    """
    Безопасно проверяет, является ли callback функцией.
    
    Args:
        callback: Проверяемый callback
        
    Returns:
        True если это функция
    """
    return inspect.isfunction(callback)


def get_callback_name(callback: Callable) -> str:
    """
    Безопасно получает имя callback'а.
    
    Args:
        callback: Callback для получения имени
        
    Returns:
        str: Имя callback'а или "unknown"
    """
    base_name = getattr(callback, '__name__', str(callback))
    
    if inspect.ismethod(callback):
        obj = callback.__self__
        class_name = getattr(obj, '__class__', None)
        if class_name:
            class_name = getattr(class_name, '__name__', 'Unknown')
            return f"{class_name}.{base_name}"
    elif inspect.isfunction(callback):
        return base_name
    
    return str(base_name)