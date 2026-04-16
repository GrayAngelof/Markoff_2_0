# client/src/services/data_loader.py
"""
DataLoader — фасад загрузки данных.

Единая точка входа для всех загрузок.
Делегирует специализированным загрузчикам:
- TreeLoader: работа с деревом (комплексы, дети)
- PhysicalLoader: детальная физика
- BusinessLoader: бизнес-данные (заглушка)
- SafetyLoader: пожарная безопасность (заглушка)
"""

# ===== ИМПОРТЫ =====
from typing import Any, List, Optional

from src.core import EventBus, NodeType
from src.core.types.nodes import NodeID
from src.data import EntityGraph
from src.models import Complex
from src.services.api_client import ApiClient
from src.services.loaders.business_loader import BusinessLoader
from src.services.loaders.physical_loader import PhysicalLoader
from src.services.loaders.safety_loader import SafetyLoader
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
        self._business = BusinessLoader(bus)
        self._safety = SafetyLoader(bus)
        log.success("DataLoader фасад готов")

    # ---- МЕТОДЫ ДЛЯ ДЕРЕВА (ленивая загрузка) ----
    def load_complexes(self) -> List[Complex]:
        """Загружает все комплексы."""
        return self._tree.load_complexes()

    def load_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType,
    ) -> List[Any]:
        """Загружает дочерние элементы для указанного родителя."""
        return self._tree.load_children(parent_type, parent_id, child_type)

    def reload_node(self, node_type: NodeType, node_id: NodeID) -> None:
        """Перезагружает указанный узел (инвалидация + загрузка)."""
        self._tree.reload_node(node_type, node_id)

    def clear_cache(self) -> None:
        """Очищает кэш загрузчика дерева."""
        self._tree.clear_cache()

    # ---- МЕТОДЫ ДЛЯ ДЕТАЛЬНОЙ ФИЗИКИ ----
    def load_details(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """Загружает детальную информацию об объекте."""
        return self._physical.load_details(node_type, node_id)

    # ---- МЕТОДЫ ДЛЯ БИЗНЕСА (заглушки) ----
    def load_counterparty(self, counterparty_id: int) -> Optional[Any]:
        """Загружает контрагента по ID."""
        return self._business.load_counterparty(counterparty_id)

    def load_responsible_persons(self, counterparty_id: int) -> List[Any]:
        """Загружает ответственных лиц контрагента."""
        return self._business.load_responsible_persons(counterparty_id)

    # ---- МЕТОДЫ ДЛЯ ПОЖАРНОЙ БЕЗОПАСНОСТИ (заглушки) ----
    def load_sensors_by_room(self, room_id: int) -> List[Any]:
        """Загружает датчики по ID помещения."""
        return self._safety.load_sensors_by_room(room_id)

    def load_events_by_building(self, building_id: int) -> List[Any]:
        """Загружает события по ID здания."""
        return self._safety.load_events_by_building(building_id)