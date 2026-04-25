# client/src/services/loaders/tree_loader.py
"""
TreeLoader — загрузка данных для дерева (ленивая загрузка детей).

Использует LoadStateIndex для отслеживания состояния загрузки детей.
Каждый уровень иерархии — свой явный метод.
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.core.event_bus import EventBus
from src.core.events.definitions import DataLoadedKind
from src.core.types.nodes import NodeID, NodeType
from src.data import EntityGraph
from src.models import (
    ComplexTreeDTO,
    BuildingTreeDTO,
    FloorTreeDTO,
    RoomTreeDTO,
)
from src.services.api_client import ApiClient
from .base import BaseLoader
from .node_loader import NodeLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class TreeLoader(BaseLoader):
    """Загрузчик данных для дерева (ленивая загрузка детей)."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, api: ApiClient, graph: EntityGraph) -> None:
        log.system("TreeLoader инициализация")
        super().__init__(bus)
        self._graph = graph
        self._node_loader = NodeLoader(api)
        log.system("TreeLoader инициализирован")

    # ---- КОРНЕВЫЕ УЗЛЫ (COMPLEX) ----
    def load_complexes_tree(self) -> List[ComplexTreeDTO]:
        """Загружает все комплексы (корневые узлы)."""
        cached = self._graph.get_all(NodeType.COMPLEX)
        if cached:
            log.cache(f"Найдено {len(cached)} комплексов в кэше")
            return cached

        log.api("Загрузка комплексов для дерева через API")
        result = self._node_loader.load_complexes_tree()

        # Сохраняем в граф
        for item in result:
            self._graph.add_or_update(item)

        # Эмитим событие
        self._with_events(
            node_type=NodeType.COMPLEX,
            node_id=0,
            fn=lambda: result,
            kind=DataLoadedKind.CHILDREN,
        )
        return result

    # ---- КОРПУСА (BUILDING) ----
    def load_buildings_tree(self, complex_id: NodeID) -> List[BuildingTreeDTO]:
        """
        Загружает корпуса для указанного комплекса.

        Args:
            complex_id: ID комплекса

        Returns:
            List[BuildingTreeDTO] — список корпусов
        """
        node_display = f"{NodeType.COMPLEX.value}#{complex_id}"

        # Проверяем, не загружены ли уже дети
        if self._graph.is_children_loaded(NodeType.COMPLEX, complex_id):
            log.cache(f"Корпуса уже загружены для {node_display}")
            return self._graph.get_cached_children(NodeType.COMPLEX, complex_id, NodeType.BUILDING)

        # Проверяем, не идёт ли уже загрузка
        if not self._graph.mark_children_loading(NodeType.COMPLEX, complex_id):
            log.debug(f"Пропуск — уже загружаются корпуса для {node_display}")
            return []

        try:
            log.api(f"Загрузка корпусов для {node_display} через API")
            result = self._node_loader.load_buildings_tree(complex_id)

            # Сохраняем в граф
            for item in result:
                self._graph.add_or_update(item)

            # Фиксируем успех
            self._graph.mark_children_loaded(NodeType.COMPLEX, complex_id)

            # Эмитим событие
            self._with_events(
                node_type=NodeType.COMPLEX,
                node_id=complex_id,
                fn=lambda: result,
                kind=DataLoadedKind.CHILDREN,
            )
            return result

        except Exception:
            self._graph.mark_children_load_failed(NodeType.COMPLEX, complex_id)
            raise

    # ---- ЭТАЖИ (FLOOR) ----
    def load_floors_tree(self, building_id: NodeID) -> List[FloorTreeDTO]:
        """
        Загружает этажи для указанного корпуса.

        Args:
            building_id: ID корпуса

        Returns:
            List[FloorTreeDTO] — список этажей
        """
        node_display = f"{NodeType.BUILDING.value}#{building_id}"

        # Проверяем, не загружены ли уже дети
        if self._graph.is_children_loaded(NodeType.BUILDING, building_id):
            log.cache(f"Этажи уже загружены для {node_display}")
            return self._graph.get_cached_children(NodeType.BUILDING, building_id, NodeType.FLOOR)

        # Проверяем, не идёт ли уже загрузка
        if not self._graph.mark_children_loading(NodeType.BUILDING, building_id):
            log.debug(f"Пропуск — уже загружаются этажи для {node_display}")
            return []

        try:
            log.api(f"Загрузка этажей для {node_display} через API")
            result = self._node_loader.load_floors_tree(building_id)

            # Сохраняем в граф
            for item in result:
                self._graph.add_or_update(item)

            # Фиксируем успех
            self._graph.mark_children_loaded(NodeType.BUILDING, building_id)

            # Эмитим событие
            self._with_events(
                node_type=NodeType.BUILDING,
                node_id=building_id,
                fn=lambda: result,
                kind=DataLoadedKind.CHILDREN,
            )
            return result

        except Exception:
            self._graph.mark_children_load_failed(NodeType.BUILDING, building_id)
            raise

    # ---- ПОМЕЩЕНИЯ (ROOM) ----
    def load_rooms_tree(self, floor_id: NodeID) -> List[RoomTreeDTO]:
        """
        Загружает помещения для указанного этажа.

        Args:
            floor_id: ID этажа

        Returns:
            List[RoomTreeDTO] — список помещений
        """
        node_display = f"{NodeType.FLOOR.value}#{floor_id}"

        # Проверяем, не загружены ли уже дети
        if self._graph.is_children_loaded(NodeType.FLOOR, floor_id):
            log.cache(f"Помещения уже загружены для {node_display}")
            return self._graph.get_cached_children(NodeType.FLOOR, floor_id, NodeType.ROOM)

        # Проверяем, не идёт ли уже загрузка
        if not self._graph.mark_children_loading(NodeType.FLOOR, floor_id):
            log.debug(f"Пропуск — уже загружаются помещения для {node_display}")
            return []

        try:
            log.api(f"Загрузка помещений для {node_display} через API")
            result = self._node_loader.load_rooms_tree(floor_id)

            # Сохраняем в граф
            for item in result:
                self._graph.add_or_update(item)

            # Фиксируем успех
            self._graph.mark_children_loaded(NodeType.FLOOR, floor_id)

            # Эмитим событие
            self._with_events(
                node_type=NodeType.FLOOR,
                node_id=floor_id,
                fn=lambda: result,
                kind=DataLoadedKind.CHILDREN,
            )
            return result

        except Exception:
            self._graph.mark_children_load_failed(NodeType.FLOOR, floor_id)
            raise

    # ---- ОБЩИЕ МЕТОДЫ ----
    def reload_node(self, node_type: NodeType, node_id: NodeID) -> None:
        """
        Перезагружает узел (инвалидация + сброс состояния детей).

        Используется при ручном обновлении данных.
        """
        node_display = f"{node_type.value}#{node_id}"
        self._graph.invalidate(node_type, node_id)
        self._graph.reset_children_state(node_type, node_id)
        log.cache(f"Узел {node_display} инвалидирован и состояние детей сброшено")

    def clear_cache(self) -> None:
        """Очищает весь кэш графа."""
        self._graph.clear()
        log.cache("Кэш графа очищен")