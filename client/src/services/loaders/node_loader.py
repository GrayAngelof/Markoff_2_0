# client/src/services/loaders/node_loader.py

"""
NodeLoader — чистая загрузка физической иерархии.

Тупой исполнитель — только вызывает API и возвращает DTO.
НЕ мутирует граф, НЕ знает о EntityGraph.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, TYPE_CHECKING

from src.core.types.nodes import NodeID
from src.services.api_client import ApiClient
from utils.logger import get_logger

if TYPE_CHECKING:
    from src.models import (
        ComplexTreeDTO,
        ComplexDetailDTO,
        BuildingTreeDTO,
        BuildingDetailDTO,
        FloorTreeDTO,
        FloorDetailDTO,
        RoomTreeDTO,
        RoomDetailDTO,
    )


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class NodeLoader:
    """
    Чистый загрузчик физической иерархии.

    Каждый метод — прямой вызов API с конкретным типом возврата.
    """

    def __init__(self, api: ApiClient) -> None:
        log.system("NodeLoader инициализация (чистый, без мутации графа)")
        self._api = api
        log.system("NodeLoader инициализирован")

    # ---- ДЕРЕВО (TREE) - МИНИМАЛЬНЫЕ ДАННЫЕ ----
    def load_complexes_tree(self) -> List['ComplexTreeDTO']:
        from src.models import ComplexTreeDTO
        log.info("Загрузка комплексов для дерева")
        data = self._api.get_complexes_tree()
        log.data(f"Загружено {len(data)} комплексов")
        return data

    def load_buildings_tree(self, complex_id: NodeID) -> List['BuildingTreeDTO']:
        from src.models import BuildingTreeDTO
        log.info(f"Загрузка корпусов для дерева (комплекс {complex_id})")
        data = self._api.get_buildings_tree(complex_id)
        log.data(f"Загружено {len(data)} корпусов для комплекса {complex_id}")
        return data

    def load_floors_tree(self, building_id: NodeID) -> List['FloorTreeDTO']:
        from src.models import FloorTreeDTO
        log.info(f"Загрузка этажей для дерева (корпус {building_id})")
        data = self._api.get_floors_tree(building_id)
        log.data(f"Загружено {len(data)} этажей для корпуса {building_id}")
        return data

    def load_rooms_tree(self, floor_id: NodeID) -> List['RoomTreeDTO']:
        from src.models import RoomTreeDTO
        log.info(f"Загрузка помещений для дерева (этаж {floor_id})")
        data = self._api.get_rooms_tree(floor_id)
        log.data(f"Загружено {len(data)} помещений для этажа {floor_id}")
        return data

    # ---- ДЕТАЛИ (DETAIL) - ПОЛНЫЕ ДАННЫЕ ----
    def load_complex_detail(self, complex_id: NodeID) -> Optional['ComplexDetailDTO']:
        from src.models import ComplexDetailDTO
        log.debug(f"Загрузка деталей комплекса {complex_id}")
        data = self._api.get_complex_detail(complex_id)
        if data:
            log.debug(f"Детали загружены для комплекса {complex_id}")
        else:
            log.debug(f"Нет деталей для комплекса {complex_id}")
        return data

    def load_building_detail(self, building_id: NodeID) -> Optional['BuildingDetailDTO']:
        from src.models import BuildingDetailDTO
        log.debug(f"Загрузка деталей корпуса {building_id}")
        data = self._api.get_building_detail(building_id)
        if data:
            log.debug(f"Детали загружены для корпуса {building_id}")
        else:
            log.debug(f"Нет деталей для корпуса {building_id}")
        return data

    def load_floor_detail(self, floor_id: NodeID) -> Optional['FloorDetailDTO']:
        from src.models import FloorDetailDTO
        log.debug(f"Загрузка деталей этажа {floor_id}")
        data = self._api.get_floor_detail(floor_id)
        if data:
            log.debug(f"Детали загружены для этажа {floor_id}")
        else:
            log.debug(f"Нет деталей для этажа {floor_id}")
        return data

    def load_room_detail(self, room_id: NodeID) -> Optional['RoomDetailDTO']:
        from src.models import RoomDetailDTO
        log.debug(f"Загрузка деталей помещения {room_id}")
        data = self._api.get_room_detail(room_id)
        if data:
            log.debug(f"Детали загружены для помещения {room_id}")
        else:
            log.debug(f"Нет деталей для помещения {room_id}")
        return data