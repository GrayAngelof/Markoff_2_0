# client/src/data/entity_graph.py
"""
Фасад графа сущностей — координатор store, relations, validity.

Только координация: не содержит логики хранения, связей или валидности.
"""

from threading import RLock
from typing import Optional, Any, List, Iterable, Dict, TypedDict
from datetime import datetime

from src.core import EventBus
from src.core.types import NodeType, NodeIdentifier
from src.core.types.nodes import NodeID 
from src.core.hierarchy import get_child_type, get_parent_type
from src.shared.validation import validate_positive_int
from utils.logger import get_logger

from .graph.store import EntityStore, StoreStats
from .graph.relations import RelationIndex, RelationStats
from .graph.validity import ValidityIndex, ValidityStats
from .graph.schema import get_node_type, get_parent_id
from .graph.consistency import ConsistencyChecker
from .graph.decorators import validate_ids

# Импорт из shared
from src.shared.comparison import has_changed

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
        
        log.success("✅ EntityGraph инициализирован")
    
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
    
    #@validate_ids('entity_id')
    def add_or_update(self, entity: Any) -> bool:
        """
        Добавляет или обновляет сущность в графе.
        
        Args:
            entity: Сущность (должна иметь NODE_TYPE и id)
            
        Returns:
            bool: True если данные изменились, False если без изменений
        """
        log.debug(f"🔧 add_or_update вызван для {type(entity).__name__}#{getattr(entity, 'id', '?')}")
        
        def _add():
            # Получаем тип сущности
            node_type = get_node_type(entity)
            if node_type is None:
                log.error(f"❌ Не удалось определить тип сущности {type(entity).__name__}")
                raise ValueError(f"Сущность {type(entity).__name__} должна иметь NODE_TYPE")
            
            entity_id = entity.id
            if entity_id is None:
                log.error(f"❌ Сущность {node_type.value} не имеет id")
                raise ValueError(f"Сущность {node_type.value} должна иметь атрибут id")
            
            log.debug(f"📝 Обработка {node_type.value}#{entity_id}")
            
            # Проверяем существующую
            old = self._store.get(node_type, entity_id)
            
            if old is not None and not has_changed(old, entity):
                log.cache(f"💾 {node_type.value}#{entity_id} без изменений, пропускаем")
                return False
            
            # Сохраняем в хранилище
            self._store.put(node_type, entity_id, entity)
            log.cache(f"💾 PUT {node_type.value}#{entity_id} в хранилище")
            
            # Обновляем связи
            parent_id = get_parent_id(entity)
            if parent_id is not None:
                parent_type = get_parent_type(node_type)
                if parent_type:
                    log.debug(f"🔗 LINK: {node_type.value}#{entity_id} → {parent_type.value}#{parent_id}")
                    self._relations.link(
                        node_type, entity_id, parent_type, parent_id
                    )
            else:
                log.debug(f"🌳 {node_type.value}#{entity_id} корневой узел (нет родителя)")
            
            # Помечаем как валидный
            self._validity.mark_valid(node_type, entity_id)
            log.success(f"✅ {node_type.value}#{entity_id} добавлен/обновлён в графе")
            return True
        
        return self._with_lock(_add)
    
    # ============================================
    # ОСТАЛЬНЫЕ МЕТОДЫ
    # ============================================
    
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """Получает сущность."""
        log.debug(f"🔍 GET {node_type.value}#{entity_id}")
        return self._with_lock(lambda: self._store.get(node_type, entity_id))
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """Возвращает все сущности типа."""
        result = self._with_lock(lambda: self._store.get_all(node_type))
        log.debug(f"📋 GET_ALL {node_type.value} → {len(result)} записей")
        return result
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """Возвращает все ID сущностей типа."""
        result = self._with_lock(lambda: self._store.get_all_ids(node_type))
        log.debug(f"🔢 GET_ALL_IDS {node_type.value} → {len(result)} ID")
        return result
    
    def has_entity(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет наличие сущности."""
        result = self._with_lock(lambda: self._store.has(node_type, entity_id))
        log.debug(f"❓ HAS {node_type.value}#{entity_id} → {result}")
        return result
    
    def remove(self, node_type: NodeType, entity_id: int, cascade: bool = False) -> bool:
        """Удаляет сущность."""
        log.info(f"🗑️ REMOVE {node_type.value}#{entity_id} (cascade={cascade})")
        
        def _remove():
            if not self._store.has(node_type, entity_id):
                log.warning(f"⚠️ {node_type.value}#{entity_id} не найден для удаления")
                return False
            
            if cascade:
                child_ids = self._relations.get_children(node_type, entity_id)
                child_type = get_child_type(node_type)
                if child_type:
                    log.debug(f"📦 Каскадное удаление {len(child_ids)} детей {child_type.value}")
                    for child_id in child_ids:
                        self.remove(child_type, child_id, cascade=True)
            
            self._relations.remove_node(node_type, entity_id)
            self._store.remove(node_type, entity_id)
            self._validity.mark_invalid(node_type, entity_id)
            log.success(f"✅ {node_type.value}#{entity_id} удалён")
            return True
        
        return self._with_lock(_remove)
    
    # ============================================
    # BULK-ОПЕРАЦИИ
    # ============================================
    
    def validate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """Помечает множество сущностей как валидные."""
        ids_list = list(ids)
        log.info(f"✅ VALIDATE_BULK {node_type.value} ×{len(ids_list)}")
        return self._with_lock(
            lambda: self._validity.mark_valid_bulk(node_type, ids_list)
        )
    
    def invalidate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """Помечает множество сущностей как невалидные."""
        ids_list = list(ids)
        log.info(f"❌ INVALIDATE_BULK {node_type.value} ×{len(ids_list)}")
        return self._with_lock(
            lambda: self._validity.mark_invalid_bulk(node_type, ids_list)
        )
    
    # ============================================
    # НАВИГАЦИЯ ПО ГРАФУ
    # ============================================
    
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """Возвращает ID всех детей."""
        result = self._with_lock(
            lambda: self._relations.get_children(parent_type, parent_id)
        )
        log.debug(f"👶 CHILDREN {parent_type.value}#{parent_id} → {len(result)} детей")
        return result
    
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[NodeIdentifier]:
        """Возвращает родителя."""
        def _get():
            parent_info = self._relations.get_parent(child_type, child_id)
            if parent_info:
                parent_type, parent_id = parent_info
                return NodeIdentifier(parent_type, parent_id)
            return None
        
        result = self._with_lock(_get)
        if result:
            log.debug(f"👪 PARENT {child_type.value}#{child_id} → {result.node_type.value}#{result.node_id}")
        else:
            log.debug(f"👪 PARENT {child_type.value}#{child_id} → None")
        return result
    
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
        
        result = self._with_lock(_get)
        if result:
            log.debug(f"🌳 ANCESTORS {node_type.value}#{node_id} → {len(result)} уровней")
        return result
    
    # ============================================
    # ВАЛИДНОСТЬ
    # ============================================
    
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет валидность."""
        result = self._with_lock(
            lambda: self._validity.is_valid(node_type, entity_id)
        )
        log.debug(f"✓ IS_VALID {node_type.value}#{entity_id} → {result}")
        return result
    
    def invalidate(self, node_type: NodeType, entity_id: int) -> bool:
        """Инвалидирует сущность."""
        log.info(f"❌ INVALIDATE {node_type.value}#{entity_id}")
        return self._with_lock(
            lambda: self._validity.mark_invalid(node_type, entity_id)
        )
    
    def invalidate_branch(self, node_type: NodeType, entity_id: int) -> int:
        """Инвалидирует ветку."""
        log.info(f"🌿 INVALIDATE_BRANCH {node_type.value}#{entity_id}")
        return self._with_lock(
            lambda: self._validity.invalidate_branch(
                node_type, entity_id, self._relations.get_children
            )
        )
    
    def validate(self, node_type: NodeType, entity_id: int) -> None:
        """Помечает сущность как валидную."""
        log.info(f"✅ VALIDATE {node_type.value}#{entity_id}")
        return self._with_lock(
            lambda: self._validity.mark_valid(node_type, entity_id)
        )
    
    # ============================================
    # ВРЕМЕННЫЕ МЕТКИ
    # ============================================
    
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
        log.info("🔍 Проверка консистентности графа...")
        return self._consistency.check()
    
    def clear(self) -> None:
        """Полная очистка."""
        log.info("🧹 Очистка EntityGraph")
        def _clear():
            self._store.clear()
            self._relations.clear()
            self._validity.clear()
        
        self._with_lock(_clear)
        log.success("✅ EntityGraph очищен")
    
    # ============================================
    # СПЕЦИАЛЬНЫЕ МЕТОДЫ ДЛЯ ЗАГРУЗЧИКА
    # ============================================
    
    def get_if_full(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """
        Возвращает сущность только если она есть И полная.
        
        Логика полноты определяется в _has_full_details().
        """
        log.debug(f"🔍 get_if_full {node_type.value}#{node_id}")
        entity = self.get(node_type, node_id)
        if entity and self.is_valid(node_type, node_id):
            if self._has_full_details(entity, node_type):
                log.cache(f"💾 get_if_full {node_type.value}#{node_id} → полные данные")
                return entity
            else:
                log.cache(f"💾 get_if_full {node_type.value}#{node_id} → данные неполные")
        else:
            log.cache(f"💾 get_if_full {node_type.value}#{node_id} → нет данных")
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
        log.debug(f"👶 get_cached_children {parent_type.value}#{parent_id} → {child_type.value}")
        
        child_ids = self.get_children(parent_type, parent_id)
        if not child_ids:
            log.cache(f"💾 Нет детей у {parent_type.value}#{parent_id}")
            return []
        
        result = []
        for child_id in child_ids:
            child = self.get(child_type, child_id)
            if child is None:
                log.cache(f"💾 Неполный кэш: отсутствует {child_type.value}#{child_id}")
                return []  # неполные данные
            result.append(child)
        
        log.cache(f"💾 Все {len(result)} детей {child_type.value} в кэше")
        return result
    
    def _has_full_details(self, entity: Any, node_type: NodeType) -> bool:
        """Внутренняя логика полноты данных."""
        if node_type == NodeType.COMPLEX:
            has = entity.description is not None or entity.address is not None
            log.debug(f"🔍 _has_full_details complex#{entity.id} → {has}")
            return has
        if node_type == NodeType.BUILDING:
            has = entity.description is not None or entity.address is not None
            log.debug(f"🔍 _has_full_details building#{entity.id} → {has}")
            return has
        if node_type == NodeType.FLOOR:
            has = entity.description is not None
            log.debug(f"🔍 _has_full_details floor#{entity.id} → {has}")
            return has
        if node_type == NodeType.ROOM:
            has = entity.area is not None or entity.status_code is not None
            log.debug(f"🔍 _has_full_details room#{entity.id} → {has}")
            return has
        log.debug(f"🔍 _has_full_details {node_type.value}#{entity.id} → False (тип не поддерживается)")
        return False