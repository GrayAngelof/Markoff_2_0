# client/src/core/ports/repository.py
"""
Базовые интерфейсы для репозиториев.

Определяет контракты (Protocol) для всех репозиториев в системе.
Единообразие доступа к данным через стандартные CRUD-операции.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, Protocol, TypeVar, runtime_checkable

# ===== ТИПЫ =====
T = TypeVar('T')
ID = TypeVar('ID', contravariant=True)


# ===== ИНТЕРФЕЙСЫ =====
class Repository(Protocol[T, ID]):
    """
    Базовый интерфейс репозитория.

    Все репозитории в системе должны реализовывать этот контракт.
    Обеспечивает единообразие CRUD-операций над сущностями.
    """

    def get(self, id: ID) -> T:
        """
        Возвращает сущность по ID.

        Raises:
            NotFoundError: Если сущность не найдена
        """
        ...

    def get_all(self) -> List[T]:
        """Возвращает список всех сущностей данного типа."""
        ...

    def add(self, entity: T) -> None:
        """
        Добавляет или обновляет сущность.

        Если сущность с таким ID уже существует — обновляет.
        """
        ...

    def remove(self, id: ID) -> bool:
        """
        Удаляет сущность по ID.

        Returns:
            True если сущность была удалена, False если не найдена
        """
        ...