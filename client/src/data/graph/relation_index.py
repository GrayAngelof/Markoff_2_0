"""
Индекс связей между сущностями.
Хранит два представления для оптимальной работы:
- Set для быстрых проверок наличия (link, unlink, has_children)
- Sorted List для UI (get_children с ordered=True)
"""
from threading import RLock
from typing import Dict, Set, List, Optional, Tuple, Any
from bisect import insort
from collections import defaultdict

from src.data.entity_types import NodeType
from src.data.graph.schema import GraphSchema, get_child_type, get_parent_type
from utils.logger import get_logger

log = get_logger(__name__)


ParentInfo = Tuple[NodeType, int]  # (parent_type, parent_id)


class RelationIndex:
    """
    Индекс связей между сущностями.
    
    Хранит два представления для каждой связи:
    - Set: для быстрых проверок наличия и уникальности
    - Sorted List: для UI (всегда отсортирован по возрастанию ID)
    
    При удалении/добавлении синхронизирует оба представления.
    Для UI гарантируется отсортированный порядок.
    """
    
    def __init__(self):
        self._lock = RLock()
        
        # Set представление - для быстрых проверок
        self._children_set: Dict[NodeType, Dict[int, Set[int]]] = {}
        
        # Sorted List представление - для UI (всегда отсортирован)
        self._children_sorted: Dict[NodeType, Dict[int, List[int]]] = {}
        
        # Обратные индексы (единые, так как родитель всегда один)
        self._parents: Dict[NodeType, Dict[int, ParentInfo]] = {}
        
        # Инициализируем для всех типов из схемы
        for node_type in GraphSchema.HIERARCHY_ORDER:
            if GraphSchema.can_have_children(node_type):
                self._children_set[node_type] = {}
                self._children_sorted[node_type] = {}
            
            if not GraphSchema.is_root(node_type):
                self._parents[node_type] = {}
        
        log.debug(f"RelationIndex инициализирован для типов: {list(self._parents.keys())}")
    
    def link(self, child_type: NodeType, child_id: int, 
             parent_type: NodeType, parent_id: int) -> None:
        """
        Устанавливает связь родитель-потомок.
        Автоматически удаляет старую связь, если она была.
        Обновляет оба представления (set и sorted list).
        """
        with self._lock:
            # Проверяем, что такая связь допустима по схеме
            expected_parent = get_parent_type(child_type)
            if expected_parent != parent_type:
                log.error(f"Недопустимая связь: {child_type} -> {parent_type} (ожидался {expected_parent})")
                return
            
            # Удаляем старую связь, если была
            old_parent = self._parents.get(child_type, {}).get(child_id)
            if old_parent:
                old_parent_type, old_parent_id = old_parent
                self._remove_from_parent(old_parent_type, old_parent_id, child_id)
            
            # Добавляем в нового родителя
            self._add_to_parent(parent_type, parent_id, child_type, child_id)
            
            log.debug(f"Установлена связь: {child_type}#{child_id} -> {parent_type}#{parent_id}")
    
    def _add_to_parent(self, parent_type: NodeType, parent_id: int, 
                       child_type: NodeType, child_id: int) -> None:
        """Внутренний метод добавления ребёнка к родителю."""
        # Инициализация структур если нужно
        if parent_type not in self._children_set:
            self._children_set[parent_type] = {}
            self._children_sorted[parent_type] = {}
        
        if parent_id not in self._children_set[parent_type]:
            self._children_set[parent_type][parent_id] = set()
            self._children_sorted[parent_type][parent_id] = []
        
        # Добавляем в set (для быстрой проверки)
        self._children_set[parent_type][parent_id].add(child_id)
        
        # Добавляем в sorted list с сохранением сортировки
        if child_id not in self._children_sorted[parent_type][parent_id]:
            # Используем bisect.insort для вставки с сохранением порядка
            from bisect import insort
            insort(self._children_sorted[parent_type][parent_id], child_id)
        
        # Обновляем обратный индекс
        if child_type not in self._parents:
            self._parents[child_type] = {}
        
        self._parents[child_type][child_id] = (parent_type, parent_id)
    
    def _remove_from_parent(self, parent_type: NodeType, parent_id: int, child_id: int) -> None:
        """Внутренний метод удаления ребёнка из родителя."""
        # Удаляем из set
        if parent_type in self._children_set and parent_id in self._children_set[parent_type]:
            self._children_set[parent_type][parent_id].discard(child_id)
        
        # Удаляем из sorted list
        if parent_type in self._children_sorted and parent_id in self._children_sorted[parent_type]:
            try:
                self._children_sorted[parent_type][parent_id].remove(child_id)
            except ValueError:
                pass  # Если элемента нет в списке - игнорируем
    
    def unlink(self, child_type: NodeType, child_id: int) -> bool:
        """Удаляет связь для потомка."""
        with self._lock:
            if child_type not in self._parents:
                return False
            
            parent_info = self._parents[child_type].get(child_id)
            if not parent_info:
                return False
            
            parent_type, parent_id = parent_info
            
            # Удаляем из родителя
            self._remove_from_parent(parent_type, parent_id, child_id)
            
            # Удаляем обратный индекс
            del self._parents[child_type][child_id]
            
            log.debug(f"Удалена связь: {child_type}#{child_id}")
            return True
    
    def get_children(self, parent_type: NodeType, parent_id: int, 
                    ordered: bool = True) -> List[int]:
        """
        Возвращает ID всех дочерних элементов.
        
        Args:
            ordered: если True - возвращает отсортированный список (для UI)
                    если False - возвращает set как list (быстрее, для внутренних операций)
        """
        with self._lock:
            if ordered:
                # Для UI - возвращаем отсортированный список
                if parent_type not in self._children_sorted:
                    return []
                # Возвращаем копию, чтобы предотвратить случайные изменения
                return list(self._children_sorted[parent_type].get(parent_id, []))
            else:
                # Для внутренних операций - быстрый вариант (может быть неотсортированным)
                if parent_type not in self._children_set:
                    return []
                return list(self._children_set[parent_type].get(parent_id, set()))
    
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[ParentInfo]:
        """Возвращает информацию о родителе."""
        with self._lock:
            if child_type not in self._parents:
                return None
            return self._parents[child_type].get(child_id)
    
    def has_children(self, parent_type: NodeType, parent_id: int) -> bool:
        """Проверяет, есть ли у родителя дети (использует set для скорости)."""
        with self._lock:
            if parent_type not in self._children_set:
                return False
            return bool(self._children_set[parent_type].get(parent_id))
    
    def remove_node(self, node_type: NodeType, node_id: int) -> None:
        """Удаляет все связи, связанные с узлом."""
        with self._lock:
            # Если узел может быть родителем, удаляем всех его детей из обратных индексов
            if node_type in self._children_set:
                child_ids = self.get_children(node_type, node_id, ordered=False)
                child_type = get_child_type(node_type)
                
                if child_type and child_type in self._parents:
                    for child_id in child_ids:
                        if child_id in self._parents[child_type]:
                            del self._parents[child_type][child_id]
                
                # Удаляем из обоих представлений
                if node_id in self._children_set[node_type]:
                    del self._children_set[node_type][node_id]
                if node_id in self._children_sorted[node_type]:
                    del self._children_sorted[node_type][node_id]
            
            # Если узел может быть потомком, удаляем из обратного индекса
            if node_type in self._parents and node_id in self._parents[node_type]:
                # Перед удалением узла как потомка, убираем его из родителя
                parent_type, parent_id = self._parents[node_type][node_id]
                self._remove_from_parent(parent_type, parent_id, node_id)
                del self._parents[node_type][node_id]
    
    def get_all_relations(self) -> Dict[str, Any]:
        """Возвращает все связи для отладки."""
        with self._lock:
            return {
                'children_set': {
                    f"{ptype}#{pid}": list(children)
                    for ptype, pdata in self._children_set.items()
                    for pid, children in pdata.items()
                },
                'children_sorted': {
                    f"{ptype}#{pid}": children
                    for ptype, pdata in self._children_sorted.items()
                    for pid, children in pdata.items()
                },
                'parents': {
                    f"{ctype}#{cid}": f"{ptype}#{pid}"
                    for ctype, cdata in self._parents.items()
                    for cid, (ptype, pid) in cdata.items()
                }
            }
    
    def clear(self) -> None:
        """Полностью очищает все индексы."""
        with self._lock:
            self._children_set.clear()
            self._children_sorted.clear()
            self._parents.clear()
            log.debug("RelationIndex очищен")