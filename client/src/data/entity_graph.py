# client/src/data/entity_graph.py
"""
Фасад графа сущностей — единый источник правды для всех данных.

Это центральный компонент Data слоя, который объединяет:
- EntityStore — хранение объектов
- RelationIndex — индексы связей
- ValidityIndex — отслеживание валидности

Все операции с данными в приложении проходят через этот фасад.
Никто не должен обращаться к store, relations, validity напрямую!

Принципы:
    - Единая точка доступа к данным
    - Потокобезопасность через RLock
    - Прозрачное кэширование и инвалидация
    - Автоматическое обновление индексов при добавлении данных

Зависимости:
    - threading — для RLock
    - core.types — NodeType, NodeIdentifier
    - core.hierarchy — get_child_type, get_parent_type
    - shared.validation — validate_positive_int
    - utils.logger — логирование
    - .utils.comparison — has_changed
    - .graph.store — EntityStore
    - .graph.relations — RelationIndex, RelationStats
    - .graph.validity — ValidityIndex, ValidityStats
    - .graph.schema — get_node_type, get_parent_id

Потребители:
    - services (DataLoader) — для сохранения загруженных данных
    - controllers (TreeController) — для навигации и проверки кэша
    - repositories — для доступа к данным
    - projections — для построения структур отображения

ВАЖНО:
    EntityGraph — это фасад. Внутренние компоненты (store, relations, validity)
    не должны быть доступны извне. Все операции идут через методы этого класса.
"""

from threading import RLock
from typing import Optional, Any, List, Dict, Iterable, TypedDict
from datetime import datetime

from core.types import NodeType, NodeIdentifier
from core.hierarchy import get_child_type, get_parent_type
from shared.validation import validate_positive_int
from utils.logger import get_logger

from .utils.comparison import has_changed
from .graph.store import EntityStore
from .graph.relations import RelationIndex, RelationStats
from .graph.validity import ValidityIndex, ValidityStats
from .graph.schema import get_node_type, get_parent_id


# ============================================
# КОНСТАНТЫ
# ============================================

# Единый логгер для модуля
log = get_logger(__name__)

# Сообщения для логирования
_LOG_ADD_OR_UPDATE_NEW = "➕ ADD: {type}#{id} (новый)"
_LOG_ADD_OR_UPDATE_CHANGED = "🔄 UPDATE: {type}#{id} (изменён)"
_LOG_ADD_OR_UPDATE_UNCHANGED = "⏭️ SKIP: {type}#{id} (без изменений)"
_LOG_GET_HIT = "📖 GET HIT: {type}#{id}"
_LOG_GET_MISS = "📖 GET MISS: {type}#{id}"
_LOG_REMOVE = "🗑️ REMOVE: {type}#{id}"
_LOG_REMOVE_CASCADE = "🗑️ REMOVE CASCADE: {type}#{id} + {count} детей"
_LOG_CLEAR = "🧹 EntityGraph полностью очищен"
_LOG_VALIDATE_BULK = "✅ VALIDATE BULK: {type} ×{count}"
_LOG_INVALIDATE_BULK = "❌ INVALIDATE BULK: {type} ×{count}"


# ============================================
# ТИПЫ ДЛЯ СТАТИСТИКИ
# ============================================

class StoreStats(TypedDict):
    """Статистика хранилища."""
    total_entities: int
    by_type: Dict[str, int]


class EntityGraphStats(TypedDict):
    """Полная статистика графа сущностей."""
    store: StoreStats
    relations: RelationStats
    validity: ValidityStats
    total_entities: int
    valid_count: int


# ============================================
# КЛАСС ENTITY GRAPH
# ============================================

class EntityGraph:
    """
    Фасад графа сущностей — единый источник правды для всех данных.
    
    Объединяет хранилище, индексы связей и валидность в единый интерфейс.
    Все операции с данными в приложении проходят через этот класс.
    
    Особенности:
        - Потокобезопасность: все операции под RLock
        - Автоматическое обновление индексов при добавлении
        - Прозрачное кэширование (get проверяет наличие)
        - Управление валидностью (invalidate, is_valid)
        - Навигация по графу (get_children, get_parent, get_ancestors)
        - Bulk-операции для массовой загрузки
        - Проверка консистентности для отладки
    
    Пример:
        >>> graph = EntityGraph()
        >>> complex = Complex(id=1, name="Северный")
        >>> graph.add_or_update(complex)
        >>> 
        >>> # Получение
        >>> cached = graph.get(NodeType.COMPLEX, 1)
        >>> 
        >>> # Навигация
        >>> building = Building(id=101, name="Корпус А", complex_id=1)
        >>> graph.add_or_update(building)
        >>> children = graph.get_children(NodeType.COMPLEX, 1)
        >>> assert children == [101]
        >>> 
        >>> # Инвалидация
        >>> graph.invalidate_branch(NodeType.COMPLEX, 1)
        >>> graph.is_valid(NodeType.COMPLEX, 1)
        False
        >>> 
        >>> # Bulk-операции
        >>> graph.validate_bulk(NodeType.ROOM, [101, 102, 103])
        3
    """
    
    def __init__(self) -> None:
        """Инициализирует пустой граф сущностей."""
        self._lock = RLock()
        
        # Внутренние компоненты (приватные)
        self._store = EntityStore()
        self._relations = RelationIndex()
        self._validity = ValidityIndex()
        
        log.success("EntityGraph инициализирован")
    
    # ============================================
    # ОСНОВНЫЕ ОПЕРАЦИИ
    # ============================================
    
    def add_or_update(self, entity: Any) -> bool:
        """
        Добавляет или обновляет сущность в графе.
        
        Автоматически:
            - Сохраняет объект в хранилище
            - Обновляет индексы связей (родитель-потомок)
            - Помечает сущность как валидную
            
        Args:
            entity: Сущность (должна иметь NODE_TYPE и id)
            
        Returns:
            bool: True если данные изменились, False если без изменений
            
        Raises:
            ValueError: Если сущность не имеет NODE_TYPE или id
            KeyError: Если тип не поддерживается
        """
        with self._lock:
            # Определяем тип и ID
            node_type = get_node_type(entity)
            if node_type is None:
                log.error("❌ add_or_update: сущность не имеет NODE_TYPE")
                raise ValueError("Сущность должна иметь атрибут NODE_TYPE")
            
            entity_id = getattr(entity, 'id', None)
            if entity_id is None:
                log.error(f"❌ add_or_update: сущность {node_type} не имеет id")
                raise ValueError(f"Сущность {node_type} должна иметь атрибут id")
            
            entity_id = validate_positive_int(entity_id, "entity_id")
            
            # Проверяем, есть ли уже такая сущность
            old = self._store.get(node_type, entity_id)
            
            # Проверяем изменения через has_changed
            if old is not None and not has_changed(old, entity):
                log.cache(_LOG_ADD_OR_UPDATE_UNCHANGED.format(
                    type=node_type.value, id=entity_id
                ))
                return False
            
            # Сохраняем в хранилище
            self._store.put(node_type, entity_id, entity)
            
            # Обновляем связи
            parent_id = get_parent_id(entity)
            if parent_id is not None:
                parent_type = get_parent_type(node_type)
                if parent_type is not None:
                    parent_id = validate_positive_int(parent_id, "parent_id")
                    self._relations.link(node_type, entity_id, parent_type, parent_id)
            
            # Помечаем как валидную
            self._validity.mark_valid(node_type, entity_id)
            
            # Логируем
            if old is None:
                log.cache(_LOG_ADD_OR_UPDATE_NEW.format(
                    type=node_type.value, id=entity_id
                ))
            else:
                log.cache(_LOG_ADD_OR_UPDATE_CHANGED.format(
                    type=node_type.value, id=entity_id
                ))
            
            return True
    
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """
        Получает сущность из графа.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            Optional[Any]: Сущность или None, если не найдена
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            entity = self._store.get(node_type, entity_id)
            
            if entity is not None:
                log.cache(_LOG_GET_HIT.format(type=node_type.value, id=entity_id))
            else:
                log.cache(_LOG_GET_MISS.format(type=node_type.value, id=entity_id))
            
            return entity
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """
        Возвращает все сущности указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            List[Any]: Список всех сущностей данного типа
        """
        with self._lock:
            return self._store.get_all(node_type)
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """
        Возвращает все ID сущностей указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            List[int]: Список всех ID данного типа
        """
        with self._lock:
            return self._store.get_all_ids(node_type)
    
    def has_entity(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Проверяет наличие сущности в графе.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            bool: True если сущность существует
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            return self._store.has(node_type, entity_id)
    
    def remove(self, node_type: NodeType, entity_id: int, cascade: bool = False) -> bool:
        """
        Удаляет сущность из графа.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            cascade: Если True, удаляет всех потомков рекурсивно
            
        Returns:
            bool: True если сущность была удалена
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            if not self._store.has(node_type, entity_id):
                return False
            
            removed_children = 0
            
            if cascade:
                # Рекурсивно удаляем всех потомков
                child_ids = self._relations.get_children(node_type, entity_id)
                child_type = get_child_type(node_type)
                
                if child_type:
                    for child_id in child_ids:
                        if self.remove(child_type, child_id, cascade=True):
                            removed_children += 1
                
                if removed_children > 0:
                    log.cache(_LOG_REMOVE_CASCADE.format(
                        type=node_type.value,
                        id=entity_id,
                        count=removed_children
                    ))
            
            # Удаляем все связи, связанные с узлом
            self._relations.remove_node(node_type, entity_id)
            
            # Удаляем из хранилища
            self._store.remove(node_type, entity_id)
            
            # Помечаем как невалидную
            self._validity.mark_invalid(node_type, entity_id)
            
            log.cache(_LOG_REMOVE.format(type=node_type.value, id=entity_id))
            return True
    
    # ============================================
    # BULK-ОПЕРАЦИИ
    # ============================================
    
    def validate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """
        Помечает множество сущностей как валидные.
        
        Args:
            node_type: Тип сущности
            ids: Итератор ID сущностей
            
        Returns:
            int: Количество помеченных сущностей
        """
        with self._lock:
            count = self._validity.mark_valid_bulk(node_type, ids)
            if count > 0:
                log.cache(_LOG_VALIDATE_BULK.format(
                    type=node_type.value,
                    count=count
                ))
            return count
    
    def invalidate_bulk(self, node_type: NodeType, ids: Iterable[int]) -> int:
        """
        Помечает множество сущностей как невалидные.
        
        Args:
            node_type: Тип сущности
            ids: Итератор ID сущностей
            
        Returns:
            int: Количество помеченных сущностей
        """
        with self._lock:
            count = self._validity.mark_invalid_bulk(node_type, ids)
            if count > 0:
                log.cache(_LOG_INVALIDATE_BULK.format(
                    type=node_type.value,
                    count=count
                ))
            return count
    
    # ============================================
    # НАВИГАЦИЯ ПО ГРАФУ
    # ============================================
    
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """
        Возвращает ID всех дочерних элементов родителя.
        
        Args:
            parent_type: Тип родителя
            parent_id: ID родителя
            
        Returns:
            List[int]: Список ID детей (порядок не гарантирован)
        """
        parent_id = validate_positive_int(parent_id, "parent_id")
        
        with self._lock:
            return self._relations.get_children(parent_type, parent_id)
    
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[NodeIdentifier]:
        """
        Возвращает идентификатор родителя дочернего элемента.
        
        Args:
            child_type: Тип дочернего элемента
            child_id: ID дочернего элемента
            
        Returns:
            Optional[NodeIdentifier]: Идентификатор родителя или None
        """
        child_id = validate_positive_int(child_id, "child_id")
        
        with self._lock:
            parent_info = self._relations.get_parent(child_type, child_id)
            if parent_info:
                parent_type, parent_id = parent_info
                return NodeIdentifier(parent_type, parent_id)
            return None
    
    def get_ancestors(self, node_type: NodeType, node_id: int) -> List[NodeIdentifier]:
        """
        Возвращает всех предков узла (родитель, дедушка и т.д.).
        
        Args:
            node_type: Тип узла
            node_id: ID узла
            
        Returns:
            List[NodeIdentifier]: Список предков (от ближайшего к дальнему)
        """
        node_id = validate_positive_int(node_id, "node_id")
        
        with self._lock:
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
    
    # ============================================
    # ВАЛИДНОСТЬ
    # ============================================
    
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Проверяет, валидны ли данные сущности.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            bool: True если данные актуальны
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            return self._validity.is_valid(node_type, entity_id)
    
    def invalidate(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Помечает сущность как невалидную (требует перезагрузки).
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
            
        Returns:
            bool: True если статус изменился
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            return self._validity.mark_invalid(node_type, entity_id)
    
    def invalidate_branch(self, node_type: NodeType, entity_id: int) -> int:
        """
        Рекурсивно инвалидирует всю ветку сущностей.
        
        Args:
            node_type: Тип корневого узла
            entity_id: ID корневого узла
            
        Returns:
            int: Количество инвалидированных сущностей
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            # Передаём get_children как функцию для обхода дерева
            return self._validity.invalidate_branch(
                node_type, entity_id, self._relations.get_children
            )
    
    def validate(self, node_type: NodeType, entity_id: int) -> None:
        """
        Помечает сущность как валидную.
        
        Args:
            node_type: Тип сущности
            entity_id: ID сущности
        """
        entity_id = validate_positive_int(entity_id, "entity_id")
        
        with self._lock:
            self._validity.mark_valid(node_type, entity_id)
    
    # ============================================
    # ВРЕМЕННЫЕ МЕТКИ
    # ============================================
    
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
            return self._store.get_timestamp(node_type, entity_id)
    
    # ============================================
    # УПРАВЛЕНИЕ
    # ============================================
    
    def clear(self) -> None:
        """Полностью очищает граф (все данные, связи, валидность)."""
        with self._lock:
            self._store.clear()
            self._relations.clear()
            self._validity.clear()
            log.cache(_LOG_CLEAR)
    
    def get_stats(self) -> EntityGraphStats:
        """
        Возвращает полную статистику использования графа.
        
        Returns:
            EntityGraphStats: Статистика из всех компонентов
            
        Пример:
            >>> stats = graph.get_stats()
            >>> stats['total_entities']
            42
            >>> stats['valid_count']
            35
        """
        with self._lock:
            # Статистика хранилища
            store_stats: StoreStats = {
                'total_entities': self._store.size(),
                'by_type': {
                    node_type.value: self._store.size_by_type(node_type)
                    for node_type in [
                        NodeType.COMPLEX, NodeType.BUILDING,
                        NodeType.FLOOR, NodeType.ROOM,
                        NodeType.COUNTERPARTY, NodeType.RESPONSIBLE_PERSON
                    ]
                }
            }
            
            # Статистика связей
            relations_stats: RelationStats = self._relations.get_stats()
            
            # Статистика валидности
            validity_stats: ValidityStats = self._validity.get_stats()
            
            return EntityGraphStats(
                store=store_stats,
                relations=relations_stats,
                validity=validity_stats,
                total_entities=store_stats['total_entities'],
                valid_count=validity_stats['total_valid'],
            )
    
    def print_stats(self) -> None:
        """Выводит статистику в консоль (для отладки)."""
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
    
    # ============================================
    # ПРОВЕРКА КОНСИСТЕНТНОСТИ
    # ============================================
    
    def check_consistency(self) -> Dict[str, Any]:
        """
        Проверяет консистентность всех индексов графа.
        
        Выявляет проблемы:
            - Сущности в store, но не валидные
            - Связи, указывающие на несуществующие объекты
            - Висячие объекты без связей
        
        Returns:
            Dict[str, Any]: Результат проверки с возможными проблемами
        """
        with self._lock:
            issues = []
            
            # 1. Проверяем, что у каждого объекта в store есть валидность
            for node_type in [
                NodeType.COMPLEX, NodeType.BUILDING, NodeType.FLOOR, NodeType.ROOM,
                NodeType.COUNTERPARTY, NodeType.RESPONSIBLE_PERSON
            ]:
                for entity_id in self._store.get_all_ids(node_type):
                    if not self._validity.is_valid(node_type, entity_id):
                        issues.append(
                            f"Сущность {node_type.value}#{entity_id} в store, но не валидна"
                        )
            
            # 2. Проверяем, что все связи имеют соответствующие объекты в store
            for parent_type in [NodeType.COMPLEX, NodeType.BUILDING, NodeType.FLOOR, NodeType.COUNTERPARTY]:
                for parent_id in self._store.get_all_ids(parent_type):
                    child_ids = self._relations.get_children(parent_type, parent_id)
                    child_type = get_child_type(parent_type)
                    
                    if child_type:
                        for child_id in child_ids:
                            if not self._store.has(child_type, child_id):
                                issues.append(
                                    f"Связь {parent_type.value}#{parent_id} → "
                                    f"{child_type.value}#{child_id} указывает на несуществующий объект"
                                )
            
            # 3. Проверяем, что у каждого ребенка есть обратная связь с родителем
            for child_type in [NodeType.BUILDING, NodeType.FLOOR, NodeType.ROOM, NodeType.RESPONSIBLE_PERSON]:
                for child_id in self._store.get_all_ids(child_type):
                    parent_info = self._relations.get_parent(child_type, child_id)
                    if not parent_info:
                        issues.append(
                            f"Сущность {child_type.value}#{child_id} имеет родителя по данным, "
                            f"но обратная связь в relations отсутствует"
                        )
            
            # 4. Проверяем, что обратные связи соответствуют прямым
            for parent_type in [NodeType.COMPLEX, NodeType.BUILDING, NodeType.FLOOR, NodeType.COUNTERPARTY]:
                child_type = get_child_type(parent_type)
                if not child_type:
                    continue
                    
                for parent_id in self._store.get_all_ids(parent_type):
                    child_ids = self._relations.get_children(parent_type, parent_id)
                    for child_id in child_ids:
                        actual_parent = self._relations.get_parent(child_type, child_id)
                        if not actual_parent or actual_parent[1] != parent_id:
                            issues.append(
                                f"Несоответствие связей: {parent_type.value}#{parent_id} → "
                                f"{child_type.value}#{child_id} в прямом индексе, "
                                f"но обратный индекс указывает на {actual_parent}"
                            )
            
            return {
                'consistent': len(issues) == 0,
                'issues': issues,
                'issues_count': len(issues)
            }