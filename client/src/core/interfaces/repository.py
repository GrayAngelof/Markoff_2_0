# client/src/core/interfaces/repository.py
"""
Базовые интерфейсы для репозиториев.

Определяет контракты, которые должны реализовывать
все репозитории в системе.
"""
from typing import Protocol, TypeVar, List, Optional
from typing  import runtime_checkable

# Invariant — используется и как in, и как out
T = TypeVar('T')

# Contravariant — используется только как in (параметры методов)
ID = TypeVar('ID', contravariant=True)


@runtime_checkable
class Repository(Protocol[T, ID]):
    """
    Базовый интерфейс репозитория.
    
    T: тип сущности (invariant — используется и в add, и в get)
    ID: тип идентификатора (contravariant — только в параметрах)
    
    Все репозитории в системе должны реализовывать этот контракт.
    Это обеспечивает единообразие доступа к данным.
    
    Пример:
        class BuildingRepository(Repository[Building, int]):
            def get(self, id: int) -> Optional[Building]:
                return self._graph.get(BUILDING, id)
            
            def get_all(self) -> List[Building]:
                return self._graph.get_all(BUILDING)
            
            def add(self, entity: Building) -> None:
                self._graph.add_or_update(entity)
            
            def remove(self, id: int) -> bool:
                return self._graph.remove(BUILDING, id)
    """
    
    def get(self, id: ID) -> Optional[T]:
        """
        Получить сущность по ID.
        
        Args:
            id: Идентификатор сущности (contravariant)
            
        Returns:
            Optional[T]: Сущность или None (invariant)
        """
        ...
    
    def get_all(self) -> List[T]:
        """
        Получить все сущности данного типа.
        
        Returns:
            List[T]: Список всех сущностей (invariant)
        """
        ...
    
    def add(self, entity: T) -> None:
        """
        Добавить или обновить сущность.
        
        Args:
            entity: Сущность для сохранения (invariant)
        """
        ...
    
    def remove(self, id: ID) -> bool:
        """
        Удалить сущность по ID.
        
        Args:
            id: Идентификатор сущности (contravariant)
            
        Returns:
            bool: True если сущность была удалена
        """
        ...