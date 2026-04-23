# client/src/core/types/exceptions.py
"""
Базовые исключения ядра.

Иерархия исключений для всех компонентов core.
Все исключения в приложении должны наследоваться от этих базовых классов.

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
- Исключения не содержат логики (логирование — в обработчиках)
- Чёткая иерархия для разных типов ошибок
- Поддержка дополнительных деталей для отладки
"""

# ===== ИМПОРТЫ =====
from typing import Optional


# ===== БАЗОВЫЕ ИСКЛЮЧЕНИЯ =====
class CoreError(Exception):
    """
    Базовое исключение для всех ошибок ядра.

    Позволяет отлавливать все ошибки ядра одним except CoreError.
    """

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


# ===== СПЕЦИАЛЬНЫЕ ИСКЛЮЧЕНИЯ =====
class ConfigurationError(CoreError):
    """Ошибка конфигурации: переменные окружения, настройки, пути."""
    pass


class HierarchyError(CoreError):
    """Ошибка иерархии: недопустимые связи, циклические зависимости."""
    pass


class SerializationError(CoreError):
    """
    Ошибка сериализации/десериализации.

    Пример: key_to_identifier('invalid:key') → неверный формат ключа.
    """
    pass


class ValidationError(CoreError):
    """Ошибка валидации: некорректный ID, пустая строка, неизвестный тип."""
    pass


class NotFoundError(CoreError):
    """Объект не найден: отсутствует в графе, API вернул 404."""
    pass


class DuplicateError(CoreError):
    """Дубликат объекта: попытка добавить уже существующий."""
    pass


class ConnectionError(CoreError):
    """Ошибка соединения: нет доступа к API, таймаут, сетевые проблемы."""
    pass


class ApiError(CoreError):
    """Ошибка API: HTTP ошибки (4xx, 5xx), некорректный ответ."""
    pass