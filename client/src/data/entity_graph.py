# client/src/data/entity_graph.py
"""
Граф сущностей - математически чистый объект.
Все операции определяются схемой, никакого хардкода.
"""
from threading import RLock
from typing import Optional, Any, List, Dict, TypeVar, Generic
from datetime import datetime

from src.data.entity_types import NodeType
from src.data.graph.schema import GraphSchema, get_parent_id, get_node_type
from src.data.graph.entity_store import EntityStore
from src.data.graph.relation_index import RelationIndex, ParentInfo
from src.data.graph.validity_index import ValidityIndex
from utils.logger import get_logger


T = TypeVar('T')
log = get_logger(__name__)


class EntityGraph:
    """
    Граф сущностей - чистая математическая структура.
    
    Все операции определяются схемой (GraphSchema).
    Нет ни одного упоминания конкретных типов (COMPLEX, BUILDING...)
    в логике - только в схеме.
    
    Граф гарантирует:
    - Консистентность индексов
    - O(1) доступ к любым данным
    - Возможность обхода в любом направлении
    """
    
    def __init__(self) -> None:
        """Инициализирует граф сущностей."""
        self._lock = RLock()
        
        # Компоненты
        self._store = EntityStore()
        self._relations = RelationIndex()
        self._validity = ValidityIndex()
        
        log.success("EntityGraph инициализирован (schema-driven)")
    
    # ===== Основные операции =====
    
    def add_or_update(self, entity: Any) -> bool:
        """
        Добавляет или обновляет сущность.
        """
        with self._lock:
            log.debug(f"add_or_update: {type(entity).__name__}")
            
            # Валидация по схеме
            if not GraphSchema.validate_entity(entity):
                log.error("Сущность не прошла валидацию схемы")
                return False
            
            node_type = get_node_type(entity)
            entity_id = entity.id
            
            # Проверка что тип определён (для Pylance)
            if node_type is None:
                log.error("Не удалось определить тип сущности")
                return False
            
            # Проверка изменений
            old = self._store.get(node_type, entity_id)
            if old and not self._has_changed(old, entity):
                log.debug(f"{node_type}#{entity_id} не изменилась")
                # ДАЖЕ ЕСЛИ НЕ ИЗМЕНИЛАСЬ, ОНА ДОЛЖНА БЫТЬ ВАЛИДНОЙ!
                # Проверим, может быть дело в этом
                self._validity.mark_valid(node_type, entity_id)
                log.debug(f"Помечена как валидная (без изменений): {node_type}#{entity_id}")
                return False
            
            # Обновление связей (если есть родитель)
            parent_id = get_parent_id(entity)
            if parent_id is not None:
                parent_type = GraphSchema.get_parent_type(node_type)
                if parent_type is not None:
                    self._relations.link(node_type, entity_id, parent_type, parent_id)
            
            # Сохранение
            self._store.put(node_type, entity_id, entity)
            
            # ЯВНО ПОМЕЧАЕМ КАК ВАЛИДНУЮ
            self._validity.mark_valid(node_type, entity_id)
            log.debug(f"Помечена как валидная: {node_type}#{entity_id}")
            
            log.info(f"Добавлена/обновлена: {node_type}#{entity_id}")
            return True
    
    def _has_changed(self, old: Any, new: Any) -> bool:
        """Проверяет изменения через сравнение датаклассов."""
        if hasattr(old, '__dataclass_fields__'):
            return old != new
        return vars(old) != vars(new)
    
    # ===== Навигация по графу =====
    
    def get_children(self, node_type: NodeType, node_id: int, 
                    ordered: bool = True) -> List[int]:
        """
        Возвращает ID всех непосредственных детей.
        
        Args:
            ordered: если True - возвращает в порядке вставки,
                    если False - быстрее, но без порядка
        """
        return self._relations.get_children(node_type, node_id, ordered)
    
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[ParentInfo]:
        """Возвращает родителя."""
        # child_type уже не Optional, так как параметр функции
        return self._relations.get_parent(child_type, child_id)
    
    def get_ancestors(self, node_type: NodeType, node_id: int) -> List[ParentInfo]:
        """
        Возвращает всех предков (родитель, дедушка и т.д.).
        Полезно для построения контекста.
        """
        ancestors = []
        current_type = node_type
        current_id = node_id
        
        while True:
            parent = self._relations.get_parent(current_type, current_id)
            if not parent:
                break
            ancestors.append(parent)
            current_type, current_id = parent
        
        return ancestors
    
    def get_descendants(self, node_type: NodeType, node_id: int, 
                        max_depth: int = -1) -> Dict[NodeType, List[int]]:
        """
        Возвращает всех потомков, сгруппированных по типу.
        Рекурсивный обход графа.
        """
        # Инициализируем результат для всех типов из схемы
        result = {nt: [] for nt in GraphSchema.HIERARCHY_ORDER}
        
        def traverse(ctype: NodeType, cid: int, depth: int):
            if max_depth != -1 and depth >= max_depth:
                return
            
            children = self._relations.get_children(ctype, cid)
            child_type = GraphSchema.get_child_type(ctype)
            
            if child_type is not None:  # Проверка для Pylance
                result[child_type].extend(children)
                for child_id in children:
                    traverse(child_type, child_id, depth + 1)
        
        traverse(node_type, node_id, 0)
        return result
    
    # ===== Доступ к данным =====
    
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """Получает сущность по типу и ID."""
        # node_type уже не Optional, так как параметр функции
        return self._store.get(node_type, entity_id)
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """Получает все сущности типа."""
        # node_type уже не Optional, так как параметр функции
        return self._store.get_all(node_type)
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """Получает все ID типа."""
        # node_type уже не Optional, так как параметр функции
        return self._store.get_all_ids(node_type)
    
    def get_many(self, node_type: NodeType, entity_ids: List[int]) -> List[Any]:
        """Получает несколько сущностей по списку ID."""
        # node_type уже не Optional, так как параметр функции
        return [
            self._store.get(node_type, eid) 
            for eid in entity_ids 
            if self._store.has(node_type, eid)
        ]
    
    def has_entity(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет наличие сущности."""
        # node_type уже не Optional, так как параметр функции
        return self._store.has(node_type, entity_id)
    
    # ===== Валидность =====
    
    def is_valid(self, node_type: NodeType, entity_id: int) -> bool:
        """Проверяет, валидны ли данные."""
        with self._lock:
            # Сущность должна существовать в хранилище
            if not self._store.has(node_type, entity_id):
                log.debug(f"is_valid: {node_type}#{entity_id} не существует в store")
                return False
            
            # Проверяем статус валидности
            valid = self._validity.is_valid(node_type, entity_id)
            log.debug(f"is_valid: {node_type}#{entity_id} = {valid}")
            return valid
    
    def invalidate(self, node_type: NodeType, entity_id: int) -> bool:
        """Помечает сущность как устаревшую."""
        with self._lock:
            log.debug(f"invalidate: {node_type}#{entity_id}")
            result = self._validity.mark_invalid(node_type, entity_id)
            log.debug(f"Результат инвалидации: {result}")
            return result
    
    def invalidate_branch(self, node_type: NodeType, entity_id: int) -> int:
        """Рекурсивно инвалидирует ветку."""
        # node_type уже не Optional, так как параметр функции
        return self._validity.invalidate_branch(
            node_type, entity_id, self.get_children
        )
    
    def validate(self, node_type: NodeType, entity_id: int) -> None:
        """
        Помечает сущность как валидную.
        Если сущности не существует в хранилище - ничего не делает.
        """
        with self._lock:
            # Проверяем, что сущность существует в хранилище
            if not self._store.has(node_type, entity_id):
                log.warning(f"Попытка валидации несуществующей сущности: {node_type}#{entity_id}")
                return
            
            self._validity.mark_valid(node_type, entity_id)
    
    # ===== Удаление =====
    
    def remove(self, node_type: NodeType, entity_id: int, cascade: bool = False) -> bool:
        """
        Удаляет сущность из графа.
        
        Args:
            cascade: если True, удаляет всех потомков рекурсивно
                    если False, удаление разрешено только если нет детей
        
        Returns:
            True если удаление выполнено, False если сущность не существует
            или есть дети при cascade=False
        """
        with self._lock:
            if not self._store.has(node_type, entity_id):
                log.debug(f"remove: {node_type}#{entity_id} не существует")
                return False
            
            # Проверяем наличие детей, если не каскадное удаление
            children = self._relations.get_children(node_type, entity_id, ordered=False)
            
            if not cascade:
                if children:
                    log.warning(f"Нельзя удалить {node_type}#{entity_id}: есть дети {children} (cascade=False)")
                    return False
            else:
                # При каскадном удалении - рекурсивно удаляем всех детей ТОЖЕ С КАСКАДОМ
                child_type = GraphSchema.get_child_type(node_type)
                if child_type:
                    for child_id in children:
                        # ВАЖНО: удаляем детей ТОЖЕ С cascade=True
                        self.remove(child_type, child_id, cascade=True)
            
            # Удаляем связи
            self._relations.remove_node(node_type, entity_id)
            
            # Удаляем из хранилища
            self._store.remove(node_type, entity_id)
            
            # Помечаем как невалидную
            self._validity.mark_invalid(node_type, entity_id)
            
            log.info(f"Удалена: {node_type}#{entity_id} (cascade={cascade})")
            return True
    
    def clear(self) -> None:
        """Полностью очищает граф."""
        with self._lock:
            self._store.clear()
            self._relations.clear()
            self._validity.clear()
            log.info("EntityGraph полностью очищен")
    
    # ===== Поиск и запросы =====
    
    def find_by_parent(self, parent_type: NodeType, parent_id: int, 
                       child_type: NodeType) -> List[Any]:
        """
        Находит всех детей определённого типа для родителя.
        """
        child_ids = self.get_children(parent_type, parent_id)
        return self.get_many(child_type, child_ids)
    
    def get_tree(self, root_type: Optional[NodeType] = None, 
                 root_id: Optional[int] = None) -> Dict:
        """
        Строит дерево для отладки.
        """
        if root_type is None:
            # Берём корневые типы (COMPLEX)
            root_type = GraphSchema.HIERARCHY_ORDER[0]
            roots = self.get_all_ids(root_type)
            return {f"{root_type}#{rid}": self.get_tree(root_type, rid) for rid in roots}
        
        if root_id is None:
            return {}
        
        result = {
            'data': str(self.get(root_type, root_id)),  # преобразуем в строку для вывода
            'children': {}
        }
        
        child_type = GraphSchema.get_child_type(root_type)
        if child_type is not None:
            child_ids = self.get_children(root_type, root_id)
            result['children'] = {
                f"{child_type}#{cid}": self.get_tree(child_type, cid)
                for cid in child_ids
            }
        
        return result
    
    # ===== Статистика и отладка =====
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования графа."""
        with self._lock:
            stats = {
                'total_entities': self._store.size(),
                'by_type': {
                    nt.value: len(self._store.get_all(nt))
                    for nt in GraphSchema.HIERARCHY_ORDER
                },
                'relations': len(self._relations.get_all_relations()['parents']),
                'valid_count': sum(
                    len(self._validity._valid[nt]) 
                    for nt in GraphSchema.HIERARCHY_ORDER
                ),
            }
            return stats
    
    def check_consistency(self) -> Dict[str, Any]:
        """
        Проверяет консистентность всех индексов.
        Теперь тоже универсальное - работает для любой схемы.
        """
        issues = []
        
        for child_type in self._relations._parents:
            for child_id, (parent_type, parent_id) in self._relations._parents[child_type].items():
                # Проверяем существование родителя
                if not self._store.has(parent_type, parent_id):
                    issues.append(f"Родитель {parent_type}#{parent_id} не существует для {child_type}#{child_id}")
                
                # Проверяем обратную связь
                if child_id not in self._relations.get_children(parent_type, parent_id):
                    issues.append(f"Ребёнок {child_type}#{child_id} не найден в children[{parent_type}][{parent_id}]")
        
        log.debug(f"Consistency check: {len(issues)} issues")
        return {
            'consistent': len(issues) == 0,
            'issues': issues
        }