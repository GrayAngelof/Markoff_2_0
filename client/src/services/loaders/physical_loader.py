# client/src/services/loaders/physical_loader.py
"""
PhysicalLoader — загрузка детальной информации о физических объектах.

Загружает детальные данные для комплексов, корпусов, этажей и помещений.
Использует кэш графа для проверки наличия полных данных.
Каждый тип объекта — свой явный метод.
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from src.core import EventBus, NodeType
from src.core.events.definitions import DataLoadedKind
from src.core.types.nodes import NodeID
from src.data import EntityGraph
from src.services.api_client import ApiClient
from src.services.loaders.base import BaseLoader
from src.services.loaders.node_loader import NodeLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class PhysicalLoader(BaseLoader):
    """Загрузчик детальной информации о физических объектах."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, api: ApiClient, graph: EntityGraph) -> None:
        log.system("PhysicalLoader инициализация")
        super().__init__(bus)
        self._graph = graph
        self._node_loader = NodeLoader(api)
        log.system("PhysicalLoader инициализирован")

    # ---- ДЕТАЛИ КОМПЛЕКСА ----
    def load_complex_detail(self, complex_id: NodeID):
        """
        Загружает детальную информацию о комплексе.

        Args:
            complex_id: ID комплекса

        Returns:
            Optional[ComplexDetailDTO] — детали комплекса или None
        """
        node_display = f"{NodeType.COMPLEX.value}#{complex_id}"

        cached = self._graph.get_if_full(NodeType.COMPLEX, complex_id)
        if cached:
            log.cache(f"Полные детали для {node_display} найдены в кэше")
            return cached

        log.api(f"Загрузка деталей комплекса {node_display} через API")
        result = self._node_loader.load_complex_detail(complex_id)

        if result:
            self._graph.add_or_update(result)

        self._with_events(
            node_type=NodeType.COMPLEX,
            node_id=complex_id,
            fn=lambda: result,
            kind=DataLoadedKind.DETAILS,
        )
        return result

    # ---- ДЕТАЛИ КОРПУСА ----
    def load_building_detail(self, building_id: NodeID):
        """
        Загружает детальную информацию о корпусе.

        Args:
            building_id: ID корпуса

        Returns:
            Optional[BuildingDetailDTO] — детали корпуса или None
        """
        node_display = f"{NodeType.BUILDING.value}#{building_id}"

        cached = self._graph.get_if_full(NodeType.BUILDING, building_id)
        if cached:
            log.cache(f"Полные детали для {node_display} найдены в кэше")
            return cached

        log.api(f"Загрузка деталей корпуса {node_display} через API")
        result = self._node_loader.load_building_detail(building_id)

        if result:
            self._graph.add_or_update(result)

        self._with_events(
            node_type=NodeType.BUILDING,
            node_id=building_id,
            fn=lambda: result,
            kind=DataLoadedKind.DETAILS,
        )
        return result

    # ---- ДЕТАЛИ ЭТАЖА ----
    def load_floor_detail(self, floor_id: NodeID):
        """
        Загружает детальную информацию об этаже.

        Args:
            floor_id: ID этажа

        Returns:
            Optional[FloorDetailDTO] — детали этажа или None
        """
        node_display = f"{NodeType.FLOOR.value}#{floor_id}"

        cached = self._graph.get_if_full(NodeType.FLOOR, floor_id)
        if cached:
            log.cache(f"Полные детали для {node_display} найдены в кэше")
            return cached

        log.api(f"Загрузка деталей этажа {node_display} через API")
        result = self._node_loader.load_floor_detail(floor_id)

        if result:
            self._graph.add_or_update(result)

        self._with_events(
            node_type=NodeType.FLOOR,
            node_id=floor_id,
            fn=lambda: result,
            kind=DataLoadedKind.DETAILS,
        )
        return result

    # ---- ДЕТАЛИ ПОМЕЩЕНИЯ ----
    def load_room_detail(self, room_id: NodeID):
        """
        Загружает детальную информацию о помещении.

        Args:
            room_id: ID помещения

        Returns:
            Optional[RoomDetailDTO] — детали помещения или None
        """
        node_display = f"{NodeType.ROOM.value}#{room_id}"

        cached = self._graph.get_if_full(NodeType.ROOM, room_id)
        if cached:
            log.cache(f"Полные детали для {node_display} найдены в кэше")
            return cached

        log.api(f"Загрузка деталей помещения {node_display} через API")
        result = self._node_loader.load_room_detail(room_id)

        if result:
            self._graph.add_or_update(result)

        self._with_events(
            node_type=NodeType.ROOM,
            node_id=room_id,
            fn=lambda: result,
            kind=DataLoadedKind.DETAILS,
        )
        return result