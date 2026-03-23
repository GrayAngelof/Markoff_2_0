# client/src/data/entity_graph.py
"""
Фасад графа сущностей — координатор store, relations, validity.

Только координация: не содержит логики хранения, связей или валидности.
"""

from threading import RLock
from typing import Optional, Any, List, Iterable, Dict, TypedDict
from datetime import datetime

from core import EventBus
from core.types import NodeType, NodeIdentifier
from core.types.nodes import NodeID 
from core.hierarchy import get_child_type, get_parent_type
from shared.validation import validate_positive_int
from utils.logger import get_logger

from .graph.store import EntityStore, StoreStats
from .graph.relations import RelationIndex, RelationStats
from .graph.validity import ValidityIndex, ValidityStats
from .graph.schema import get_node_type, get_parent_id
from .graph.consistency import ConsistencyChecker
from .graph.decorators import validate_ids

# Импорт из shared (правильный путь)
from shared.comparison import has_changed

log = get_logger(__name__)


class EntityGraphStats(TypedDict):
    """Полная статистика графа сущностей."""
    store: StoreStats
    relations: RelationStats
    validity: ValidityStats
    total_entities: int
    valid_count: int


class EntityGraph:
    """
    Фасад графа сущностей — координатор store, relations, validity.
    
    Только координация: не содержит логики хранения, связей или валидности.
    """
    
    def __init__(self, event_bus: EventBus) -> None:
        """
        Инициализирует пустой граф сущностей.
        
        Args:
            event_bus: Шина событий для уведомлений об инвалидации
        """
        self._bus = event_bus
        self._lock = RLock()
        
        self._store = EntityStore()
        self._relations = RelationIndex()
        self._validity = ValidityIndex(event_bus)
        
        self._consistency = ConsistencyChecker(
            self._store, self._relations, self._validity
        )
        
        log.success("EntityGraph инициализирован")
    
    # ============================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================
    
    def _with_lock(self, func):
        """Выполняет функцию под блокировкой."""
        with self._lock:
            return func()
    
    # ============================================
    # CRUD (координация)
    # ============================================
    
    @validate_ids('entity_id')
    def add_or_update(self, entity: Any) -> bool:
        """
        Добавляет или обновляет сущность в графе.
        
        Args:
            entity: Сущность (должна иметь NODE_TYPE и id)
            
        Returns:
            bool: True если данные изменились, False если без изменений
        """
        def _add():
            node_type = get_node_type(entity)
            if node_type is None:
                raise ValueError("Сущность должна иметь атрибут NODE_TYPE")
            
            entity_id = entity.id
            if entity_id is None:
                raise ValueError(f"Сущность {node_type} должна иметь атрибут id")
            
            old = self._store.get(node_type, entity_id)
            
            if old is not None and not has_changed(old, entity):
                return False
            
            self._store.put(node_type, entity_id, entity)
            
            parent_id = get_parent_id(entity)
            if parent_id is not None:
                parent_type = get_parent_type(node_type)
                if parent_type:
                    self._relations.link(
                        node_type, entity_id, parent_type, parent_id
                    )
            
            self._validity.mark_valid(node_type, entity_id)
            return True
        
        return self._with_lock(_add)
    
    @validate_ids('entity_id')
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """Получает сущность."""
        return self._with_lock(lambda: self._store.get(node_type, entity_id))
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """Возвращает все сущности типа."""
        return self._with_lock(lambda: self._store.get_all(node_type))
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """Возвращает все ID сущностей типа."""
        return self._with_lock(lambda: self._store.get_all_ids(node_type))
    
    def has_entity(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет наличие сущности."""
        return self._with_lock(lambda: self._store.has(node_type, entity_id))
    
    @validate_ids('entity_id')
    def remove(self, node_type: NodeType, entity_id: int, cascade: bool = False) -> bool:
        """Удаляет сущность."""
        def _remove():
            if not self._store.has(node_type, entity_id):
                return False
            
            if cascade:
                child_ids = self._relations.get_children(node_type, entity_id)
                child_type = get_child_type(node_type)
                if child_type:
                    for child_id in child_ids:
                        self.remove(child_type, child_id, cascade=True)
            
            self._relations.remove_node(node_type, entity_id)
            self._store.remove(node_type, entity_id)
            self._validity.mark_invalid(node_type, entity_id)
            return True
        
        return self._with_lock(_remove)
    
    # ============================================
    # BULK-ОПЕРАЦИИ
    # ============================================
    
    def validate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """Помечает множество сущностей как валидные."""
        return self._with_lock(
            lambda: self._validity.mark_valid_bulk(node_type, ids)
        )
    
    def invalidate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """Помечает множество сущностей как невалидные."""
        return self._with_lock(
            lambda: self._validity.mark_invalid_bulk(node_type, ids)
        )
    
    # ============================================
    # НАВИГАЦИЯ ПО ГРАФУ
    # ============================================
    
    @validate_ids('parent_id')
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """Возвращает ID всех детей."""
        return self._with_lock(
            lambda: self._relations.get_children(parent_type, parent_id)
        )
    
    @validate_ids('child_id')
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[NodeIdentifier]:
        """Возвращает родителя."""
        def _get():
            parent_info = self._relations.get_parent(child_type, child_id)
            if parent_info:
                parent_type, parent_id = parent_info
                return NodeIdentifier(parent_type, parent_id)
            return None
        
        return self._with_lock(_get)
    
    @validate_ids('node_id')
    def get_ancestors(self, node_type: NodeType, node_id: int) -> List[NodeIdentifier]:
        """Возвращает всех предков."""
        def _get():
            ancestors = []
            current_type = node_type
            current_id = node_id
            
            while True:
                parent_info = self._relations.get_parent(current_type, current_id)
                if not parent_info:
                    break
                parent_type, parent_id = parent_info
                ancestors.append(NodeIdentifier(parent_type, parent_id))
                current_type, current_id = parent_type, parent_id
            
            return ancestors
        
        return self._with_lock(_get)
    
    # ============================================
    # ВАЛИДНОСТЬ
    # ============================================
    
    @validate_ids('entity_id')
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет валидность."""
        return self._with_lock(
            lambda: self._validity.is_valid(node_type, entity_id)
        )
    
    @validate_ids('entity_id')
    def invalidate(self, node_type: NodeType, entity_id: int) -> bool:
        """Инвалидирует сущность."""
        return self._with_lock(
            lambda: self._validity.mark_invalid(node_type, entity_id)
        )
    
    @validate_ids('entity_id')
    def invalidate_branch(self, node_type: NodeType, entity_id: int) -> int:
        """Инвалидирует ветку."""
        return self._with_lock(
            lambda: self._validity.invalidate_branch(
                node_type, entity_id, self._relations.get_children
            )
        )
    
    @validate_ids('entity_id')
    def validate(self, node_type: NodeType, entity_id: int) -> None:
        """Помечает сущность как валидную."""
        return self._with_lock(
            lambda: self._validity.mark_valid(node_type, entity_id)
        )
    
    # ============================================
    # ВРЕМЕННЫЕ МЕТКИ
    # ============================================
    
    @validate_ids('entity_id')
    def get_timestamp(self, node_type: NodeType, entity_id: int) -> Optional[datetime]:
        """Возвращает время последнего обновления."""
        return self._with_lock(
            lambda: self._store.get_timestamp(node_type, entity_id)
        )
    
    # ============================================
    # СТАТИСТИКА И ДИАГНОСТИКА
    # ============================================
    
    def get_stats(self) -> EntityGraphStats:
        """Возвращает статистику."""
        def _get():
            store_stats = self._store.get_stats()
            relations_stats = self._relations.get_stats()
            validity_stats = self._validity.get_stats()
            
            return EntityGraphStats(
                store=store_stats,
                relations=relations_stats,
                validity=validity_stats,
                total_entities=store_stats['total_entities'],
                valid_count=validity_stats['total_valid'],
            )
        
        return self._with_lock(_get)
    
    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()
        
        log.info("\n" + "=" * 50)
        log.info("📊 EntityGraph Statistics")
        log.info("=" * 50)
        
        log.info("\n📦 Store:")
        log.info(f"  • Всего сущностей: {stats['store']['total_entities']}")
        for type_name, count in stats['store']['by_type'].items():
            log.info(f"  • {type_name}: {count}")
        
        log.info("\n🔗 Relations:")
        log.info(f"  • Parent entries: {stats['relations']['parent_entries']}")
        log.info(f"  • Child entries: {stats['relations']['child_entries']}")
        
        log.info("\n✅ Validity:")
        validity_stats = stats['validity']
        log.info(f"  • Всего валидных: {validity_stats['total_valid']}")
        for type_name, count in validity_stats['by_type'].items():
            if count > 0:
                log.info(f"  • {type_name}: {count}")
        
        log.info("=" * 50 + "\n")
    
    def check_consistency(self) -> Dict[str, Any]:
        """Проверяет консистентность графа."""
        return self._consistency.check()
    
    def clear(self) -> None:
        """Полная очистка."""
        def _clear():
            self._store.clear()
            self._relations.clear()
            self._validity.clear()
        
        self._with_lock(_clear)

    def get_if_full(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """
        Возвращает сущность только если она есть И полная.
        
        Логика полноты определяется в _has_full_details().
        """
        entity = self.get(node_type, node_id)
        if entity and self.is_valid(node_type, node_id):
            if self._has_full_details(entity, node_type):
                return entity
        return None
    
    def get_cached_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType
    ) -> List[Any]:
        """
        Возвращает детей только если ВСЕ они есть в кэше.
        
        Если хоть одного ребёнка нет — возвращает [] (неполные данные).
        """
        child_ids = self.get_children(parent_type, parent_id)
        if not child_ids:
            return []
        
        result = []
        for child_id in child_ids:
            child = self.get(child_type, child_id)
            if child is None:
                return []  # неполные данные
            result.append(child)
        
        return result
    
    def _has_full_details(self, entity: Any, node_type: NodeType) -> bool:
        """Внутренняя логика полноты данных."""
        if node_type == NodeType.COMPLEX:
            return entity.description is not None or entity.address is not None
        if node_type == NodeType.BUILDING:
            return entity.description is not None or entity.address is not None
        if node_type == NodeType.FLOOR:
            return entity.description is not None
        if node_type == NodeType.ROOM:
            return entity.area is not None or entity.status_code is not None
        return False