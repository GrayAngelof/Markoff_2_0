# client/src/services/data_loader.py
"""
DataLoader — фасад загрузки данных.

Единая точка входа для всех загрузок.
Делегирует специализированным загрузчикам:
- TreeLoader: работа с деревом (комплексы, корпуса, этажи, помещения)
- PhysicalLoader: детальная физика (комплексы, корпуса, этажи, помещения)
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional

from src.core import EventBus, NodeType
from src.core.types.nodes import NodeID
from src.data import EntityGraph
from src.models import (
    ComplexTreeDTO,
    BuildingTreeDTO,
    FloorTreeDTO,
    RoomTreeDTO,
    ComplexDetailDTO,
    BuildingDetailDTO,
    FloorDetailDTO,
    RoomDetailDTO,
)
from src.services.api_client import ApiClient
from src.services.loaders.physical_loader import PhysicalLoader
from src.services.loaders.tree_loader import TreeLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DataLoader:
    """Фасад загрузки данных. Делегирует специализированным загрузчикам."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, api: ApiClient, graph: EntityGraph) -> None:
        log.system("DataLoader фасад инициализация")
        self._tree = TreeLoader(bus, api, graph)
        self._physical = PhysicalLoader(bus, api, graph)
        log.success("DataLoader фасад готов")

    # ---- КОРНЕВЫЕ УЗЛЫ (COMPLEX) ----
    def load_complexes_tree(self) -> List[ComplexTreeDTO]:
        """Загружает все комплексы для дерева."""
        return self._tree.load_complexes_tree()

    # ---- ДЕРЕВО (TREE) - ЛЕНИВАЯ ЗАГРУЗКА ДЕТЕЙ ----
    def load_buildings_tree(self, complex_id: NodeID) -> List[BuildingTreeDTO]:
        """Загружает корпуса для указанного комплекса."""
        return self._tree.load_buildings_tree(complex_id)

    def load_floors_tree(self, building_id: NodeID) -> List[FloorTreeDTO]:
        """Загружает этажи для указанного корпуса."""
        return self._tree.load_floors_tree(building_id)

    def load_rooms_tree(self, floor_id: NodeID) -> List[RoomTreeDTO]:
        """Загружает помещения для указанного этажа."""
        return self._tree.load_rooms_tree(floor_id)

    # ---- ДЕТАЛИ (DETAIL) - ПОЛНЫЕ ДАННЫЕ ----
    def load_complex_detail(self, complex_id: NodeID) -> Optional[ComplexDetailDTO]:
        """Загружает детальную информацию о комплексе."""
        return self._physical.load_complex_detail(complex_id)

    def load_building_detail(self, building_id: NodeID) -> Optional[BuildingDetailDTO]:
        """Загружает детальную информацию о корпусе."""
        return self._physical.load_building_detail(building_id)

    def load_floor_detail(self, floor_id: NodeID) -> Optional[FloorDetailDTO]:
        """Загружает детальную информацию об этаже."""
        return self._physical.load_floor_detail(floor_id)

    def load_room_detail(self, room_id: NodeID) -> Optional[RoomDetailDTO]:
        """Загружает детальную информацию о помещении."""
        return self._physical.load_room_detail(room_id)

    # ---- ОБЩИЕ МЕТОДЫ ----
    def reload_node(self, node_type: NodeType, node_id: NodeID) -> None:
        """Перезагружает указанный узел (инвалидация + загрузка)."""
        self._tree.reload_node(node_type, node_id)

    def clear_cache(self) -> None:
        """Очищает кэш загрузчика дерева."""
        self._tree.clear_cache()