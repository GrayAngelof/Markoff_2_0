# client/src/projections/tree_projection.py
"""
Проекция дерева объектов.
Строит иерархическую структуру из плоского графа,
используя существующие модели TreeNode из tree_model.
"""
from typing import List, Dict, Any

from src.core.events import SystemEvents
from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM
from src.projections.base_projection import BaseProjection
from src.ui.tree_model.tree_node import TreeNode  # используем существующий TreeNode

from utils.logger import get_logger

log = get_logger(__name__)


class TreeProjection(BaseProjection):
    """
    Проекция дерева объектов.
    
    Строит из плоских данных EntityGraph иерархическую структуру:
    Complex
    └─ Building
        └─ Floor
            └─ Room
    
    Использует существующие модели TreeNode из tree_model.
    """
    
    def __init__(self, event_bus, graph):
        super().__init__(event_bus, debounce_ms=50)
        
        self._graph = graph
        self._node_index: Dict[str, TreeNode] = {}
        
        # Подписываемся на изменения данных
        self._subscribe(SystemEvents.DATA_LOADED, self._on_data_changed)
        
        log.info("TreeProjection инициализирована")
    
    def _on_data_changed(self, event):
        """Данные изменились - планируем перестроение."""
        self._schedule_rebuild()
    
    def _rebuild(self):
        """Перестраивает дерево из графа."""
        log.debug("Перестроение дерева...")
        
        # Получаем все комплексы
        complexes = self._graph.get_all(COMPLEX)
        root_nodes = []
        
        for complex_data in complexes:
            complex_node = self._get_or_create_node(complex_data, NodeType.COMPLEX)
            
            # Добавляем корпуса
            building_ids = self._graph.get_children(COMPLEX, complex_data.id)
            for building_id in building_ids:
                building_data = self._graph.get(BUILDING, building_id)
                if building_data:
                    building_node = self._get_or_create_node(
                        building_data, NodeType.BUILDING, complex_node
                    )
                    
                    # Добавляем этажи
                    floor_ids = self._graph.get_children(BUILDING, building_id)
                    for floor_id in floor_ids:
                        floor_data = self._graph.get(FLOOR, floor_id)
                        if floor_data:
                            floor_node = self._get_or_create_node(
                                floor_data, NodeType.FLOOR, building_node
                            )
                            
                            # Добавляем комнаты
                            room_ids = self._graph.get_children(FLOOR, floor_id)
                            for room_id in room_ids:
                                room_data = self._graph.get(ROOM, room_id)
                                if room_data:
                                    room_node = self._get_or_create_node(
                                        room_data, NodeType.ROOM, floor_node
                                    )
                                    if room_node not in floor_node.children:
                                        floor_node.append_child(room_node)  # <-- ИСПРАВЛЕНО: append_child
                            
                            if floor_node not in building_node.children:
                                building_node.append_child(floor_node)  # <-- ИСПРАВЛЕНО: append_child
                    
                    if building_node not in complex_node.children:
                        complex_node.append_child(building_node)  # <-- ИСПРАВЛЕНО: append_child
            
            root_nodes.append(complex_node)
        
        self._cached_result = root_nodes
        self._dirty = False
        
        log.debug(f"Дерево перестроено: {len(root_nodes)} комплексов")
        self._bus.emit('projection.tree_updated', {'tree': root_nodes})
    
    def _get_or_create_node(self, data, node_type, parent=None):
        """
        Получает существующий узел или создаёт новый.
        
        Args:
            data: Данные узла
            node_type: Тип узла (NodeType)
            parent: Родительский узел (опционально)
        
        Returns:
            TreeNode: Узел дерева
        """
        key = f"{node_type.value}:{data.id}"
        
        if key in self._node_index:
            node = self._node_index[key]
            # Обновляем данные
            node.update_data(data)
            if parent and node.parent != parent:
                # Перемещаем в нового родителя
                if node.parent:
                    node.parent.remove_child(node)
                node._parent = parent  # используем protected доступ для установки
                parent.append_child(node)  # <-- ИСПРАВЛЕНО: append_child
            return node
        
        node = TreeNode(data, node_type, parent)
        if parent:
            parent.append_child(node)  # <-- ИСПРАВЛЕНО: append_child
        self._node_index[key] = node
        return node