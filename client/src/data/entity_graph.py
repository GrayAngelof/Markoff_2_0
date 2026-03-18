# client/src/data/entity_graph.py
"""
Граф сущностей - фасад для работы с данными.
Объединяет хранилище, индексы связей и валидность.
"""
from threading import RLock
from typing import Optional, Any, List, Dict, Tuple
from datetime import datetime

from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM, COUNTERPARTY, RESPONSIBLE_PERSON
# ИСПРАВЛЕНО: импортируем функции, а не класс GraphSchema
from src.data.graph.schema import (
    get_node_type, get_parent_id, get_child_type,
    NODETYPE_TO_MODEL, MODEL_TO_NODETYPE
)
from src.data.graph.entity_store import EntityStore
from src.data.graph.relation_index import RelationIndex, ParentInfo
from src.data.graph.validity_index import ValidityIndex
from src.models import Complex, Building, Floor, Room
from utils.logger import get_logger


log = get_logger(__name__)


class EntityGraph:
    """
    Граф сущностей - фасад для работы с данными.
    
    Объединяет:
    - EntityStore: хранение объектов
    - RelationIndex: индексы связей
    - ValidityIndex: валидность данных
    
    Предоставляет единый интерфейс для всех операций.
    """
    
    def __init__(self) -> None:
        """Инициализирует граф сущностей."""
        self._lock = RLock()
        
        # Внутренние компоненты
        self._store = EntityStore()
        self._relations = RelationIndex()
        self._validity = ValidityIndex()
        
        log.success("EntityGraph инициализирован")
    
    # ===== Основные операции =====
    
    def add_or_update(self, entity: Any) -> bool:
        """
        Добавляет или обновляет сущность.
        Автоматически обновляет все индексы.
        
        Returns:
            bool: True если данные изменились
        """
        with self._lock:
            log.debug(f"add_or_update: {type(entity).__name__}")
            log.info(f"📊 ENTITY_GRAPH: add_or_update {type(entity).__name__} id={entity.id if hasattr(entity, 'id') else 'unknown'}")

            # Определяем тип и ID
            node_type = get_node_type(entity)
            if not node_type:
                log.error("Не удалось определить тип сущности")
                return False
            
            entity_id = entity.id
            if entity_id is None:
                log.error("Сущность не имеет ID")
                return False
            
            # Проверяем изменения
            old = self._store.get(node_type, entity_id)
            if old and not self._has_changed(old, entity):
                log.debug(f"Сущность {node_type.value}#{entity_id} не изменилась")
                return False
            
            # Сохраняем в хранилище
            self._store.put(node_type, entity_id, entity)
            
            # Обновляем связи (если есть родитель)
            parent_id = get_parent_id(entity)
            if parent_id is not None:
                parent_type = {
                    BUILDING: COMPLEX,
                    FLOOR: BUILDING,
                    ROOM: FLOOR,
                    RESPONSIBLE_PERSON: COUNTERPARTY,
                }.get(node_type)
                
                if parent_type:
                    self._relations.link(node_type, entity_id, parent_type, parent_id)
            
            # Помечаем как валидную
            self._validity.mark_valid(node_type, entity_id)
            
            log.info(f"Добавлена/обновлена сущность: {node_type.value}#{entity_id}")
            return True
    
    def _has_changed(self, old: Any, new: Any) -> bool:
        """
        Проверяет, изменились ли данные.
        Использует сравнение датаклассов, а не ручное сравнение полей.
        """
        # Если модели - dataclasses, можно сравнить напрямую
        if hasattr(old, '__dataclass_fields__') and hasattr(new, '__dataclass_fields__'):
            return old != new
        
        # Запасной вариант - сравнение словарей
        return vars(old) != vars(new)
    
    # ===== Методы доступа =====
    
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """Получает сущность по типу и ID."""
        return self._store.get(node_type, entity_id)
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """Получает все сущности указанного типа."""
        return self._store.get_all(node_type)
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """Получает все ID сущностей указанного типа."""
        return self._store.get_all_ids(node_type)
    
    def has_entity(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет наличие сущности."""
        return self._store.has(node_type, entity_id)
    
    # ===== Методы навигации по графу =====
    
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """Получает ID всех дочерних элементов."""
        return self._relations.get_children(parent_type, parent_id)
    
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[ParentInfo]:
        """Получает информацию о родителе."""
        return self._relations.get_parent(child_type, child_id)
    
    def get_ancestors(self, node_type: NodeType, node_id: int) -> List[ParentInfo]:
        """
        Возвращает всех предков (родитель, дедушка и т.д.).
        Полезно для построения контекста.
        """
        ancestors = []
        current_type, current_id = node_type, node_id
        
        while True:
            parent = self._relations.get_parent(current_type, current_id)
            if not parent:
                break
            ancestors.append(parent)
            current_type, current_id = parent
        
        return ancestors
    
    # ===== Методы валидности =====
    
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет, валидны ли данные."""
        return self._validity.is_valid(node_type, entity_id)
    
    def invalidate(self, node_type: NodeType, entity_id: int) -> bool:
        """Помечает сущность как устаревшую."""
        return self._validity.mark_invalid(node_type, entity_id)
    
    def invalidate_branch(self, node_type: NodeType, entity_id: int) -> int:
        """
        Рекурсивно инвалидирует всю ветку.
        Возвращает количество инвалидированных сущностей.
        """
        return self._validity.invalidate_branch(
            node_type, entity_id, self.get_children
        )
    
    def validate(self, node_type: NodeType, entity_id: int) -> None:
        """Помечает сущность как валидную."""
        self._validity.mark_valid(node_type, entity_id)
    
    # ===== Методы удаления =====
    
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
        with self._lock:
            if not self._store.has(node_type, entity_id):
                log.debug(f"REMOVE: {node_type.value}#{entity_id} не найдена")
                return False
            
            if cascade:
                # Рекурсивно удаляем всех потомков
                child_ids = self.get_children(node_type, entity_id)
                child_type = get_child_type(node_type)
                
                if child_type:
                    for child_id in child_ids:
                        self.remove(child_type, child_id, cascade=True)
            
            # Удаляем все связи
            self._relations.remove_node(node_type, entity_id)
            
            # Удаляем из хранилища
            self._store.remove(node_type, entity_id)
            
            # Удаляем из индекса валидности
            self._validity.mark_invalid(node_type, entity_id)
            
            log.info(f"Удалена сущность: {node_type.value}#{entity_id} (cascade={cascade})")
            return True
    
    def clear(self) -> None:
        """Полностью очищает граф."""
        with self._lock:
            self._store.clear()
            self._relations.clear()
            self._validity.clear()
            log.info("EntityGraph полностью очищен")
    
    # ===== Методы для статистики и отладки =====
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования графа."""
        with self._lock:
            relations = self._relations.get_all_relations()
            
            stats = {
                'total_entities': self._store.size(),
                'by_type': {
                    node_type.value: len(self._store.get_all(node_type))
                    for node_type in [
                        COMPLEX, BUILDING, FLOOR, ROOM,
                        COUNTERPARTY, RESPONSIBLE_PERSON
                    ]
                },
                'valid_count': sum(
                    len(self._validity._valid[nt]) 
                    for nt in self._validity._valid
                ),
                'children_indices': len(relations['children']),
                'parent_indices': len(relations['parents']),
            }
            return stats
    
    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()
        
        log.info("\n=== Entity Graph Statistics ===")
        log.info(f"📦 Всего сущностей: {stats['total_entities']}")
        for node_type, count in stats['by_type'].items():
            log.info(f"  • {node_type}: {count}")
        log.info(f"✅ Валидных: {stats['valid_count']}")
        log.info(f"🔗 Индексов детей: {stats['children_indices']}")
        log.info(f"🔗 Индексов родителей: {stats['parent_indices']}")
        log.info("=" * 30)
    
    def get_timestamp(self, node_type: NodeType, entity_id: int) -> Optional[datetime]:
        """
        Возвращает временную метку последнего обновления сущности.
        
        Args:
            node_type: Тип узла
            entity_id: ID сущности
            
        Returns:
            Optional[datetime]: Время последнего обновления или None
        """
        return self._store.get_timestamp(node_type, entity_id)
    
    def check_consistency(self) -> Dict[str, Any]:
        """
        Проверяет консистентность всех индексов.
        """
        issues = []
        
        # Получаем все отношения через публичный метод
        relations = self._relations.get_all_relations()
        
        # Проверка обратных индексов через parents
        for parent_key, parent_info in relations['parents'].items():
            # parent_key = "building#101", parent_info = "complex#1"
            try:
                child_type_str, child_id_str = parent_key.split('#')
                parent_type_str, parent_id_str = parent_info.split('#')
                
                child_id = int(child_id_str)
                parent_id = int(parent_id_str)
                
                child_type = NodeType(child_type_str)
                parent_type = NodeType(parent_type_str)
                
                # Проверяем, что родитель существует
                if not self._store.has(parent_type, parent_id):
                    issues.append(f"Родитель {parent_type.value}#{parent_id} не существует для {child_type.value}#{child_id}")
                
                # Проверяем, что ребёнок есть в children у родителя
                children = self.get_children(parent_type, parent_id)
                if child_id not in children:
                    issues.append(f"Ребёнок {child_type.value}#{child_id} не найден в children[{parent_type.value}][{parent_id}]")
                    
            except Exception as e:
                issues.append(f"Ошибка парсинга отношения: {parent_key} -> {parent_info}: {e}")
        
        # Проверка прямых индексов через children
        for parent_key, child_list in relations['children'].items():
            try:
                parent_type_str, parent_id_str = parent_key.split('#')
                parent_id = int(parent_id_str)
                parent_type = NodeType(parent_type_str)
                
                # Проверяем, что родитель существует
                if not self._store.has(parent_type, parent_id):
                    issues.append(f"Родитель {parent_type.value}#{parent_id} не существует")
                
                # Для каждого ребёнка проверяем обратную связь
                child_type = get_child_type(parent_type)
                if child_type:
                    for child_id in child_list:
                        parent_info = self.get_parent(child_type, child_id)
                        if not parent_info:
                            issues.append(f"Нет обратной связи для {child_type.value}#{child_id}")
                        elif parent_info[1] != parent_id:
                            issues.append(f"Несоответствие родителей: {child_type.value}#{child_id} указывает на {parent_info[1]}, но должен на {parent_id}")
                            
            except Exception as e:
                issues.append(f"Ошибка парсинга отношения: {parent_key} -> {child_list}: {e}")
        
        log.debug(f"Проверка консистентности: найдено {len(issues)} проблем")
        return {
            'consistent': len(issues) == 0,
            'issues': issues
        }