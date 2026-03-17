# client/src/data/graph/relation_index.py
"""
Индекс связей между сущностями.
Теперь полностью управляется схемой, без хардкода типов.
"""
from threading import RLock
from typing import Dict, Set, List, Optional, Tuple,Any
from collections import defaultdict

from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM, COUNTERPARTY, RESPONSIBLE_PERSON
from src.data.graph.schema import get_child_type, get_parent_type
from utils.logger import get_logger

log = get_logger(__name__)


ParentInfo = Tuple[NodeType, int]  # (parent_type, parent_id)


class RelationIndex:
    """
    Индекс связей между сущностями.
    
    Полностью универсальный - работает с любыми типами из схемы.
    Не содержит упоминаний конкретных типов (COMPLEX, BUILDING и т.д.)
    """
    
    def __init__(self):
        self._lock = RLock()
        
        # Прямые индексы: parent_type -> {parent_id: set(child_ids)}
        # Используем defaultdict, чтобы не проверять наличие ключей
        self._children: Dict[NodeType, Dict[int, Set[int]]] = {
            COMPLEX: {},
            BUILDING: {},
            FLOOR: {},
            COUNTERPARTY: {},  # <-- ДОБАВЛЕНО для контрагентов (их дети - ответственные лица)
        }
        
        # Обратные индексы: child_type -> {child_id: (parent_type, parent_id)}
        self._parents: Dict[NodeType, Dict[int, ParentInfo]] = {
            BUILDING: {},
            FLOOR: {},
            ROOM: {},
            RESPONSIBLE_PERSON: {},  # <-- ДОБАВЛЕНО для ответственных лиц
        }
        
        log.debug(f"RelationIndex инициализирован для типов: children={list(self._children.keys())}, parents={list(self._parents.keys())}")
    
    def link(self, child_type: NodeType, child_id: int, 
             parent_type: NodeType, parent_id: int) -> None:
        """
        Устанавливает связь родитель-потомок.
        Автоматически удаляет старую связь, если она была.
        """
        with self._lock:
            # Проверяем, что такая связь допустима по схеме
            expected_parent = get_parent_type(child_type)
            if expected_parent and expected_parent != parent_type:
                log.error(f"Недопустимая связь: {child_type} -> {parent_type} (ожидался {expected_parent})")
                return
            
            # Удаляем старую связь, если была
            old_parent = self._parents.get(child_type, {}).get(child_id)
            if old_parent:
                old_parent_type, old_parent_id = old_parent
                if old_parent_type in self._children and old_parent_id in self._children[old_parent_type]:
                    self._children[old_parent_type][old_parent_id].discard(child_id)
                    log.debug(f"Удалена старая связь: {child_type}#{child_id} из {old_parent_type}#{old_parent_id}")
            
            # Добавляем в нового родителя
            if parent_type not in self._children:
                self._children[parent_type] = {}
            
            if parent_id not in self._children[parent_type]:
                self._children[parent_type][parent_id] = set()
            
            self._children[parent_type][parent_id].add(child_id)
            
            # Обновляем обратный индекс
            if child_type not in self._parents:
                self._parents[child_type] = {}
            
            self._parents[child_type][child_id] = (parent_type, parent_id)
            
            log.debug(f"Установлена связь: {child_type}#{child_id} -> {parent_type}#{parent_id}")
    
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
            if parent_type in self._children and parent_id in self._children[parent_type]:
                self._children[parent_type][parent_id].discard(child_id)
            
            # Удаляем обратный индекс
            del self._parents[child_type][child_id]
            
            log.debug(f"Удалена связь: {child_type}#{child_id}")
            return True
    
    def get_children(self, parent_type: NodeType, parent_id: int) -> List[int]:
        """Возвращает ID всех дочерних элементов."""
        with self._lock:
            if parent_type not in self._children:
                return []
            return list(self._children[parent_type].get(parent_id, set()))
    
    def get_parent(self, child_type: NodeType, child_id: int) -> Optional[ParentInfo]:
        """Возвращает информацию о родителе."""
        with self._lock:
            if child_type not in self._parents:
                return None
            return self._parents[child_type].get(child_id)
    
    def has_children(self, parent_type: NodeType, parent_id: int) -> bool:
        """Проверяет, есть ли у родителя дети."""
        with self._lock:
            if parent_type not in self._children:
                return False
            return bool(self._children[parent_type].get(parent_id))
    
    def remove_node(self, node_type: NodeType, node_id: int) -> None:
        """Удаляет все связи, связанные с узлом."""
        with self._lock:
            # Если узел может быть родителем, удаляем всех его детей из обратных индексов
            if node_type in self._children:
                child_ids = self.get_children(node_type, node_id)
                child_type = get_child_type(node_type)
                
                if child_type and child_type in self._parents:
                    for child_id in child_ids:
                        if child_id in self._parents[child_type]:
                            del self._parents[child_type][child_id]
                
                # Удаляем из прямого индекса
                if node_id in self._children[node_type]:
                    del self._children[node_type][node_id]
            
            # Если узел может быть потомком, удаляем из обратного индекса
            if node_type in self._parents and node_id in self._parents[node_type]:
                del self._parents[node_type][node_id]
    
    def get_all_relations(self) -> Dict[str, Any]:
        """Возвращает все связи для отладки."""
        with self._lock:
            return {
                'children': {
                    f"{ptype.value}#{pid}": list(children)
                    for ptype, pdata in self._children.items()
                    for pid, children in pdata.items()
                },
                'parents': {
                    f"{ctype.value}#{cid}": f"{ptype.value}#{pid}"
                    for ctype, cdata in self._parents.items()
                    for cid, (ptype, pid) in cdata.items()
                }
            }
    
    def clear(self) -> None:
        """Полностью очищает все индексы."""
        with self._lock:
            self._children.clear()
            self._parents.clear()
            log.debug("RelationIndex очищен")