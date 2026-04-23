# client/src/models/base.py
"""
Базовый класс для всех DTO моделей.

Обеспечивает единую структуру данных для всех сущностей.
frozen=True гарантирует иммутабельность для безопасного кэширования.
NODE_TYPE и IS_DETAIL — ClassVar, так как это метаданные класса,
а не состояние экземпляра.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import ClassVar, Tuple


# ===== БАЗОВЫЕ КЛАССЫ =====
@dataclass(frozen=True, kw_only=True)
class BaseDTO:
    """
    Базовый DTO с минимальным набором полей.

    Все модели должны наследовать этот класс.
    Дополнительные возможности добавляются через миксины.
    """

    id: int

    # Метаданные класса (не попадают в __init__, не участвуют в eq/hash)
    NODE_TYPE: ClassVar[str] = "unknown"
    IS_DETAIL: ClassVar[bool] = False

    def key(self) -> Tuple[str, int]:
        """
        Уникальный ключ для хранения в EntityGraph.

        Returns:
            Кортеж (тип_узла, id)
        """
        return (self.NODE_TYPE, self.id)

    def __eq__(self, other: object) -> bool:
        """
        Сравнение объектов по ключу (тип + id).

        Это гарантирует, что ComplexTreeDTO(id=1) != BuildingTreeDTO(id=1).
        """
        if not isinstance(other, BaseDTO):
            return NotImplemented
        return self.key() == other.key()

    def __hash__(self) -> int:
        """Хеш от ключа для использования в множествах и словарях."""
        return hash(self.key())

    def __repr__(self) -> str:
        """Возвращает строковое представление для отладки."""
        detail_flag = "[DETAIL]" if self.IS_DETAIL else "[TREE]"
        return f"{self.__class__.__name__}{detail_flag}(key={self.key()})"