# client/src/services/loading/node_loader.py
"""
NodeLoader — чистая загрузка физической иерархии.

Тупой исполнитель — только вызывает API и возвращает DTO.
НЕ мутирует граф, НЕ знает о EntityGraph.
Вся логика сохранения — в загрузчиках (TreeLoader, PhysicalLoader).
"""

# ===== ИМПОРТЫ =====
from typing import Any, Callable, Dict, List, Optional

from src.core import NodeType
from src.core.types.nodes import NodeID
from src.services.api_client import ApiClient
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class NodeLoader:
    """
    Чистый загрузчик физической иерархии.

    Тупой исполнитель:
    - Конфигурация (какие методы вызывать) передаётся снаружи
    - Не содержит if-elif по типам
    - НЕ мутирует граф — только возвращает DTO
    - Не знает о EntityGraph
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        api: ApiClient,
        child_loaders: Dict[NodeType, Callable[[ApiClient, NodeID], List[Any]]],
        detail_loaders: Dict[NodeType, Callable[[ApiClient, NodeID], Optional[Any]]],
    ) -> None:
        """
        Args:
            api: API клиент
            child_loaders: {child_type: (api, parent_id) -> List[DTO]}
            detail_loaders: {node_type: (api, node_id) -> Optional[DTO]}
        """
        log.system("NodeLoader инициализация (чистый, без мутации графа)")
        self._api = api
        self._child_loaders = child_loaders
        self._detail_loaders = detail_loaders
        log.system(f"NodeLoader инициализирован: child_loaders={len(child_loaders)}, detail_loaders={len(detail_loaders)}")

    # ---- КОНКРЕТНЫЕ ЗАГРУЗЧИКИ (для удобства) ----
    def load_complexes(self) -> List[Any]:
        """Загружает все комплексы. Возвращает список DTO."""
        log.info("Загрузка комплексов")
        data = self._api.get_complexes()
        log.data(f"Загружено {len(data)} комплексов")
        return data

    def load_buildings(self, complex_id: NodeID) -> List[Any]:
        """Загружает корпуса комплекса. Возвращает список DTO."""
        log.info(f"Загрузка корпусов для комплекса {complex_id}")
        data = self._api.get_buildings(complex_id)
        log.data(f"Загружено {len(data)} корпусов для комплекса {complex_id}")
        return data

    def load_floors(self, building_id: NodeID) -> List[Any]:
        """Загружает этажи корпуса. Возвращает список DTO."""
        log.info(f"Загрузка этажей для корпуса {building_id}")
        data = self._api.get_floors(building_id)
        log.data(f"Загружено {len(data)} этажей для корпуса {building_id}")
        return data

    def load_rooms(self, floor_id: NodeID) -> List[Any]:
        """Загружает помещения этажа. Возвращает список DTO."""
        log.info(f"Загрузка помещений для этажа {floor_id}")
        data = self._api.get_rooms(floor_id)
        log.data(f"Загружено {len(data)} помещений для этажа {floor_id}")
        return data

    # ---- УНИВЕРСАЛЬНЫЕ ЗАГРУЗЧИКИ (через DI) ----
    def load_children(
        self,
        parent_type: NodeType,
        parent_id: NodeID,
        child_type: NodeType,
    ) -> List[Any]:
        """
        Универсальная загрузка детей.

        Returns:
            Список загруженных DTO

        Raises:
            KeyError: Если для child_type нет загрузчика
        """
        loader = self._child_loaders.get(child_type)
        if not loader:
            log.error(f"Не найден загрузчик для типа {child_type}")
            raise KeyError(f"No child loader for type: {child_type}")

        log.info(f"Загрузка {child_type.value} для {parent_type.value}#{parent_id}")
        data = loader(self._api, parent_id)
        log.data(f"Загружено {len(data)} {child_type.value} для {parent_type.value}#{parent_id}")
        return data

    def load_details(self, node_type: NodeType, node_id: NodeID) -> Optional[Any]:
        """
        Универсальная загрузка деталей.

        Returns:
            Загруженный DTO или None

        Raises:
            KeyError: Если для node_type нет загрузчика деталей
        """
        loader = self._detail_loaders.get(node_type)
        if not loader:
            log.error(f"Не найден загрузчик деталей для типа {node_type}")
            raise KeyError(f"No detail loader for type: {node_type}")

        log.debug(f"Загрузка деталей для {node_type.value}#{node_id}")
        data = loader(self._api, node_id)

        if data:
            log.debug(f"Детали загружены для {node_type.value}#{node_id}")
        else:
            log.debug(f"Нет деталей для {node_type.value}#{node_id}")

        return data

    # ---- СТАТИСТИКА (заглушка для совместимости) ----
    def get_stats(self) -> dict:
        """Возвращает статистику работы загрузчика (заглушка)."""
        return {
            'api_calls': 0,
            'cache_hits': 0,
            'nodes_loaded': 0,
        }