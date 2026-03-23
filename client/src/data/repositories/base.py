# client/src/data/repositories/base.py
"""
Базовый класс для всех репозиториев.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — возвращает T или кидает NotFoundError
- get_all() — возвращает List[T] (может быть пустым)
- get_ids() — возвращает List[int] (все ID типа)
- exists() — проверяет существование (без исключений)
- add() — добавляет или обновляет
- remove() — удаляет или кидает NotFoundError
- is_valid() — проверяет валидность
- invalidate() — помечает как невалидный

ВАЖНО:
- get() НЕ возвращает Optional[T]! Только T или исключение.
- remove() НЕ возвращает bool! Только None или исключение.
- Для проверки существования используйте exists().

Следуем контракту core.Repository:
- get() кидает NotFoundError
- remove() кидает NotFoundError
- exists() возвращает bool
"""
from abc import ABC
from typing import Generic, TypeVar, List
from core import NodeType, NotFoundError
from core.interfaces import Repository as CoreRepository
from data.entity_graph import EntityGraph

T = TypeVar('T')


class BaseRepository(Generic[T], CoreRepository[T, int], ABC):
    """
    Базовый репозиторий для всех типов сущностей.
    
    Реализует контракт core.Repository.
    """
    
    def __init__(self, graph: EntityGraph, node_type: NodeType):
        self._graph = graph
        self._node_type = node_type
    
    def get(self, id: int) -> T:
        """
        Возвращает сущность по ID.
        
        Args:
            id: ID сущности
            
        Returns:
            T: Сущность
            
        Raises:
            NotFoundError: Если сущность не найдена
        """
        entity = self._graph.get(self._node_type, id)
        if entity is None:
            raise NotFoundError(
                f"{self._node_type.value} #{id} not found",
                details={"node_type": self._node_type.value, "node_id": id}
            )
        return entity
    
    def get_all(self) -> List[T]:
        """
        Возвращает все сущности типа.
        
        Returns:
            List[T]: Список сущностей (может быть пустым)
        """
        return self._graph.get_all(self._node_type)
    
    def get_ids(self) -> List[int]:
        """
        Возвращает все ID сущностей типа.
        
        Returns:
            List[int]: Список ID (может быть пустым)
        """
        return self._graph.get_all_ids(self._node_type)
    
    def add(self, entity: T) -> None:
        """
        Добавляет или обновляет сущность.
        
        Args:
            entity: Сущность для сохранения
        """
        self._graph.add_or_update(entity)
    
    def remove(self, id: int) -> bool:
        """
        Удаляет сущность по ID.
        
        Args:
            id: ID сущности
            
        Returns:
            bool: True если сущность была удалена, False если не найдена
            
        Note:
            Следуем контракту core.Repository: возвращаем bool, не кидаем исключение.
            Для проверки существования используйте exists() перед удалением.
        """
        return self._graph.remove(self._node_type, id)
    
    def exists(self, id: int) -> bool:
        """
        Проверяет существование сущности (без исключений).
        
        Args:
            id: ID сущности
            
        Returns:
            bool: True если сущность существует
        """
        return self._graph.get(self._node_type, id) is not None
    
    def is_valid(self, id: int) -> bool:
        """
        Проверяет, валидны ли данные сущности.
        
        Args:
            id: ID сущности
            
        Returns:
            bool: True если данные валидны
        """
        return self._graph.is_valid(self._node_type, id)
    
    def invalidate(self, id: int) -> bool:
        """
        Помечает сущность как невалидную (требует перезагрузки).
        
        Args:
            id: ID сущности
            
        Returns:
            bool: True если статус изменился
        """
        return self._graph.invalidate(self._node_type, id)