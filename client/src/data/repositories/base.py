# client/src/data/repositories/base.py
"""
Базовый класс для всех репозиториев.

Реализует контракт core.Repository:
- get() — возвращает T или кидает NotFoundError
- get_all() — возвращает List[T] (может быть пустым)
- get_ids() — возвращает List[int] (все ID типа)
- exists() — проверяет существование (без исключений)
- add() — добавляет или обновляет
- remove() — удаляет, возвращает bool (True если был удалён)
- is_valid() — проверяет валидность
- invalidate() — помечает как невалидный

ВАЖНО:
- get() НЕ возвращает Optional[T]! Только T или исключение.
- Для проверки существования используйте exists().
"""

# ===== ИМПОРТЫ =====
from abc import ABC
from typing import Generic, List, TypeVar

from src.core import NodeType, NotFoundError
from src.core.interfaces import Repository as CoreRepository
from src.data.entity_graph import EntityGraph


# ===== ТИПЫ =====
T = TypeVar('T')


# ===== КЛАСС =====
class BaseRepository(Generic[T], CoreRepository[T, int], ABC):
    """
    Базовый репозиторий для всех типов сущностей.

    Реализует контракт core.Repository.
    Все специфичные репозитории наследуются от этого класса.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, graph: EntityGraph, node_type: NodeType) -> None:
        self._graph = graph
        self._node_type = node_type

    # ---- CRUD ОПЕРАЦИИ ----
    def get(self, id: int) -> T:
        """
        Возвращает сущность по ID.

        Raises:
            NotFoundError: Если сущность не найдена
        """
        entity = self._graph.get(self._node_type, id)
        if entity is None:
            raise NotFoundError(
                f"{self._node_type.value} #{id} not found",
                details={"node_type": self._node_type.value, "node_id": id},
            )
        return entity

    def get_all(self) -> List[T]:
        """Возвращает все сущности данного типа."""
        return self._graph.get_all(self._node_type)

    def get_ids(self) -> List[int]:
        """Возвращает все ID сущностей данного типа."""
        return self._graph.get_all_ids(self._node_type)

    def add(self, entity: T) -> None:
        """Добавляет или обновляет сущность."""
        self._graph.add_or_update(entity)

    def remove(self, id: int) -> bool:
        """
        Удаляет сущность по ID.

        Returns:
            True если сущность была удалена, False если не найдена
        """
        return self._graph.remove(self._node_type, id)

    # ---- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ----
    def exists(self, id: int) -> bool:
        """Проверяет существование сущности (без исключений)."""
        return self._graph.get(self._node_type, id) is not None

    def is_valid(self, id: int) -> bool:
        """Проверяет, валидны ли данные сущности."""
        return self._graph.is_valid(self._node_type, id)

    def invalidate(self, id: int) -> bool:
        """
        Помечает сущность как невалидную (требует перезагрузки).

        Returns:
            True если статус изменился
        """
        return self._graph.invalidate(self._node_type, id)