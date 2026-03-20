# Базовый класс для всех репозиториев
# Зависимости: core, data.entity_graph, typing, abc

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from core import Repository as CoreRepository, NodeType, NodeIdentifier
from data.entity_graph import EntityGraph

T = TypeVar('T')

class BaseRepository(Generic[T], CoreRepository[T, int], ABC):
    """Базовый репозиторий для всех типов сущностей"""
    
    def __init__(self, graph: EntityGraph, node_type: NodeType):
        self._graph = graph
        self._node_type = node_type
    
    def get(self, id: int) -> Optional[T]:
        """Получает сущность по ID."""
        return self._graph.get(self._node_type, id)
    
    def get_all(self) -> List[T]:
        """Получает все сущности типа."""
        return self._graph.get_all(self._node_type)
    
    def add(self, entity: T) -> None:
        """Добавляет или обновляет сущность."""
        self._graph.add_or_update(entity)
    
    def remove(self, id: int) -> bool:
        """Удаляет сущность."""
        return self._graph.remove(self._node_type, id)
    
    def exists(self, id: int) -> bool:
        """Проверяет существование."""
        return self._graph.get(self._node_type, id) is not None
    
    def is_valid(self, id: int) -> bool:
        """Проверяет валидность."""
        return self._graph.is_valid(self._node_type, id)
    
    def invalidate(self, id: int) -> bool:
        """Помечает как невалидное."""
        return self._graph.invalidate(self._node_type, id)