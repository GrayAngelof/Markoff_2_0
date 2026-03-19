# client/src/core/types/exceptions.py
"""
БАЗОВЫЕ ИСКЛЮЧЕНИЯ ЯДРА.

Иерархия исключений для всех компонентов core.
Все исключения в приложении должны наследоваться от этих базовых классов.
"""
from typing import Optional


class CoreError(Exception):
    """
    Базовое исключение для всех ошибок ядра.
    
    Все исключения в core должны наследоваться от этого класса.
    Это позволяет отлавливать все ошибки ядра одним except.
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке
            details: Дополнительные детали (для логирования)
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
        
        from utils.logger import get_logger
        log = get_logger(__name__)
        log.error(f"❌ {self.__class__.__name__}: {message}")
        if details:
            log.debug(f"📋 Детали: {details}")


class ConfigurationError(CoreError):
    """Ошибка конфигурации (неправильные настройки)."""
    pass


class HierarchyError(CoreError):
    """Ошибка в иерархии объектов (неправильные связи)."""
    pass


class SerializationError(CoreError):
    """Ошибка сериализации/десериализации."""
    pass


class ValidationError(CoreError):
    """Ошибка валидации данных."""
    pass


class NotFoundError(CoreError):
    """Объект не найден."""
    pass


class DuplicateError(CoreError):
    """Дубликат объекта."""
    pass