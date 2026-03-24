# client/src/data/graph/store.py
"""
Хранилище сущностей — только хранение объектов по типам и ID.

Это первый компонент Data слоя. EntityStore отвечает только за:
- Хранение объектов в памяти
- Получение по типу и ID
- Удаление
- Временные метки

Никакой логики связей, валидности или навигации!
"""

from threading import RLock
from typing import Dict, Optional, Any, List, TypedDict
from datetime import datetime

from src.core.types import NodeType
from src.shared.validation import validate_positive_int
from utils.logger import get_logger


# ============================================
# КОНСТАНТЫ
# ============================================

log = get_logger(__name__)


# ============================================
# ТИПЫ ДЛЯ СТАТИСТИКИ
# ============================================

class StoreStats(TypedDict):
    """Статистика хранилища."""
    total_entities: int
    by_type: Dict[str, int]


# ============================================
# КЛАСС ENTITY STORE
# ============================================

class EntityStore:
    """
    Потокобезопасное хранилище сущностей.
    
    Только базовые операции: put, get, remove, has.
    Не знает о связях между сущностями.
    
    Пример:
        >>> store = EntityStore()
        >>> store.put(NodeType.COMPLEX, 1, complex_obj)
        >>> obj = store.get(NodeType.COMPLEX, 1)
        >>> store.remove(NodeType.COMPLEX, 1)
    """
    
    def __init__(self):
        """Инициализирует пустое хранилище."""
        self._lock = RLock()
        
        # Основное хранилище: тип узла -> {id: объект}
        self._entities: Dict[NodeType, Dict[int, Any]] = {
            NodeType.COMPLEX: {},
            NodeType.BUILDING: {},
            NodeType.FLOOR: {},
            NodeType.ROOM: {},
            NodeType.COUNTERPARTY: {},
            NodeType.RESPONSIBLE_PERSON: {},
        }
        
        # Временные метки для каждого объекта
        self._timestamps: Dict[NodeType, Dict[int, datetime]] = {
            NodeType.COMPLEX: {},
            NodeType.BUILDING: {},
            NodeType.FLOOR: {},
            NodeType.ROOM: {},
            NodeType.COUNTERPARTY: {},
            NodeType.RESPONSIBLE_PERSON: {},
        }
        
        log.debug("EntityStore инициализирован")
    
    # ============================================
    # ОСНОВНЫЕ ОПЕРАЦИИ
    # ============================================
    
    def put(self, node_type: NodeType, entity_id: int, entity: Any) -> None:
        """
        Сохраняет сущность в хранилище.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            entity: Объект для сохранения
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            self._entities[node_type][entity_id] = entity
            self._timestamps[node_type][entity_id] = datetime.now()
            log.debug(f"PUT {node_type.value}#{entity_id}")
    
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """
        Получает сущность из хранилища.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            Optional[Any]: Сущность или None, если не найдена
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            return self._entities[node_type].get(entity_id)
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """
        Возвращает все сущности указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            List[Any]: Список всех сущностей (может быть пустым)
        """
        with self._lock:
            return list(self._entities[node_type].values())
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """
        Возвращает все ID сущностей указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            List[int]: Список всех ID (может быть пустым)
        """
        with self._lock:
            return list(self._entities[node_type].keys())
    
    def remove(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Удаляет сущность из хранилища.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            bool: True если сущность была удалена
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            if entity_id in self._entities[node_type]:
                del self._entities[node_type][entity_id]
                if entity_id in self._timestamps[node_type]:
                    del self._timestamps[node_type][entity_id]
                log.debug(f"REMOVE {node_type.value}#{entity_id}")
                return True
            return False
    
    def has(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Проверяет наличие сущности в хранилище.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            bool: True если сущность существует
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            return entity_id in self._entities[node_type]
    
    def get_timestamp(self, node_type: NodeType, entity_id: int) -> Optional[datetime]:
        """
        Возвращает время последнего обновления сущности.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            Optional[datetime]: Время обновления или None
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            return self._timestamps[node_type].get(entity_id)
    
    # ============================================
    # УПРАВЛЕНИЕ
    # ============================================
    
    def clear(self) -> None:
        """Полностью очищает хранилище."""
        with self._lock:
            for node_type in self._entities:
                self._entities[node_type].clear()
                self._timestamps[node_type].clear()
            log.debug("EntityStore очищен")
    
    def size(self) -> int:
        """
        Возвращает общее количество сущностей.
        
        Returns:
            int: Сумма всех сущностей всех типов
        """
        with self._lock:
            return sum(len(store) for store in self._entities.values())
    
    def size_by_type(self, node_type: NodeType) -> int:
        """
        Возвращает количество сущностей указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            int: Количество сущностей
        """
        with self._lock:
            return len(self._entities[node_type])
    
    # ============================================
    # СТАТИСТИКА
    # ============================================
    
    def get_stats(self) -> StoreStats:
        """
        Возвращает статистику хранилища.
        
        Returns:
            StoreStats: Статистика с total_entities и by_type
            
        Пример:
            >>> stats = store.get_stats()
            >>> stats['total_entities']
            42
            >>> stats['by_type']['complex']
            5
        """
        with self._lock:
            by_type: Dict[str, int] = {}
            for node_type in self._entities:
                count = len(self._entities[node_type])
                if count > 0:
                    by_type[node_type.value] = count
            
            return StoreStats(
                total_entities=self.size(),
                by_type=by_type
            )