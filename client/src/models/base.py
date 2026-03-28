# client/src/models/base.py
"""
Базовый класс для всех DTO моделей.

Обеспечивает единую структуру данных для всех сущностей.
frozen=True гарантирует иммутабельность для безопасного кэширования.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass


# ===== БАЗОВЫЕ КЛАССЫ =====
@dataclass(frozen=True, kw_only=True)
class BaseDTO:
    """
    Базовый DTO с минимальным набором полей.

    Все модели должны наследовать этот класс.
    Дополнительные возможности добавляются через миксины.
    """

    id: int

    def __post_init__(self) -> None:
        """Валидирует ID после создания."""
        if self.id <= 0:
            raise ValueError(f"ID должен быть положительным числом, получено: {self.id}")

    def __repr__(self) -> str:
        """Возвращает строковое представление для отладки."""
        return f"{self.__class__.__name__}(id={self.id})"