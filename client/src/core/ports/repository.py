# client/src/core/ports/repository.py
"""
Базовые интерфейсы для репозиториев.

Определяет контракты (Protocol) для всех репозиториев в системе.
Единообразие доступа к данным через стандартные CRUD-операции.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, Protocol, TypeVar, runtime_checkable


# ===== ТИПЫ =====
# T — invariant: используется и как in, и как out (параметры методов и возврат)
T = TypeVar('T')

# ID — contravariant: используется только как in (параметры методов)
ID = TypeVar('ID', contravariant=True)


# ===== ИНТЕРФЕЙСЫ =====
@runtime_checkable
class Repository(Protocol[T, ID]):
    """
    Базовый интерфейс репозитория.

    Все репозитории в системе должны реализовывать этот контракт.
    Обеспечивает единообразие CRUD-операций над сущностями.

    TypeVar'ы:
        T — тип сущности (invariant)
        ID — тип идентификатора (contravariant)
    """

    def get(self, id: ID) -> Optional[T]:
        """
        Возвращает сущность по ID.

        Returns:
            None если сущность не найдена
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