# client/src/services/loaders/tree_loader.py
"""
TreeLoader — загрузка данных для дерева (ленивая загрузка детей).

Использует LoadStateIndex для отслеживания состояния загрузки детей.
"""

# ===== ИМПОРТЫ =====
from typing import Any, List

from src.core import EventBus, NodeType
from src.core.events.definitions import DataLoadedKind
from src.core.types.nodes import NodeID
from src.data import EntityGraph
from src.models import Complex
from src.services.api_client import ApiClient
from src.services.loaders.base import BaseLoader
from src.services.loading.node_loader import NodeLoader
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

        child_loaders = {
            NodeType.BUILDING: lambda a, pid: a.get_buildings(pid),
            NodeType.FLOOR: lambda a, pid: a.get_floors(pid),
            NodeType.ROOM: lambda a, pid: a.get_rooms(pid),
        }
        self._node_loader = NodeLoader(api, child_loaders, detail_loaders={})
        log.system("TreeLoader инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def load_complexes(self) -> List[Complex]:
        """Загружает все комплексы (корневые узлы)."""
        cached = self._graph.get_all(NodeType.COMPLEX)
        if cached:
            log.cache(f"Найдено {len(cached)} комплексов в кэше")
            return cached

        log.api("Загрузка комплексов через API")
        result = self._node_loader.load_complexes()

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

    def load_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType,
    ) -> List[Any]:
        """
        Загружает дочерние элементы для указанного родителя.

        Использует LoadStateIndex для предотвращения повторных загрузок.
        """
        node_display = f"{parent_type.value}#{parent_id}"

        # Проверяем, не загружены ли уже дети
        if self._graph.is_children_loaded(parent_type, parent_id):
            log.cache(f"Дети уже загружены для {node_display}")
            return self._graph.get_cached_children(parent_type, parent_id, child_type)

        # Проверяем, не идёт ли уже загрузка
        if not self._graph.mark_children_loading(parent_type, parent_id):
            log.debug(f"Пропуск — уже загружается {node_display}")
            return []

        try:
            log.api(f"Загрузка детей {child_type.value} для {node_display} через API")
            result = self._node_loader.load_children(parent_type, parent_id, child_type)

            # Сохраняем в граф
            for item in result:
                self._graph.add_or_update(item)

            # Фиксируем успех
            self._graph.mark_children_loaded(parent_type, parent_id)

            # Эмитим событие
            self._with_events(
                node_type=parent_type,
                node_id=parent_id,
                fn=lambda: result,
                kind=DataLoadedKind.CHILDREN,
            )
            return result

        except Exception:
            self._graph.mark_children_load_failed(parent_type, parent_id)
            raise

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