# client/src/services/loaders/physical_loader.py
"""
PhysicalLoader — загрузка детальной информации о физических объектах.

Загружает детальные данные для комплексов, корпусов, этажей и помещений.
Использует кэш графа для проверки наличия полных данных.
"""

# ===== ИМПОРТЫ =====
from typing import Any, Optional

from src.core import EventBus, NodeType
from src.core.events.definitions import DataLoadedKind
from src.core.types.nodes import NodeID
from src.data import EntityGraph
from src.services.api_client import ApiClient
from src.services.loaders.base import BaseLoader
from src.services.loading.node_loader import NodeLoader
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

        detail_loaders = {
            NodeType.COMPLEX: lambda a, nid: a.get_complex_detail(nid),
            NodeType.BUILDING: lambda a, nid: a.get_building_detail(nid),
            NodeType.FLOOR: lambda a, nid: a.get_floor_detail(nid),
            NodeType.ROOM: lambda a, nid: a.get_room_detail(nid),
        }
        self._node_loader = NodeLoader(api, child_loaders={}, detail_loaders=detail_loaders)
        log.system("PhysicalLoader инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def load_details(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """
        Загружает детальную информацию об объекте.

        Сначала проверяет кэш через get_if_full().
        Если полных данных нет — загружает через API и сохраняет в граф.
        """
        node_display = f"{node_type.value}#{node_id}"

        cached = self._graph.get_if_full(node_type, node_id)
        if cached:
            log.cache(f"Полные детали для {node_display} найдены в кэше")
            return cached

        log.api(f"Загрузка деталей для {node_display} через API")
        result = self._node_loader.load_details(node_type, node_id)

        # Сохраняем в граф (только если данные загружены)
        if result:
            self._graph.add_or_update(result)

        # Эмитим событие
        self._with_events(
            node_type=node_type,
            node_id=node_id,
            fn=lambda: result,
            kind=DataLoadedKind.DETAILS,
        )
        return result