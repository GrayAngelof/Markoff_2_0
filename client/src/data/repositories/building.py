# client/src/data/repositories/building.py
"""
Репозиторий для корпусов.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_floor_ids() — навигация по графу (получение ID детей)
- get_by_complex() — навигация по графу (получение ID корпусов комплекса)

Никакой бизнес-логики: фильтрация по владельцу — только в сервисах!
Работает с TreeDTO и DetailDTO.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, Union, cast

from src.core.types import NodeType
from .base import BaseRepository
from src.models import BuildingDetailDTO, BuildingTreeDTO


# ===== ТИПЫ =====
# Репозиторий может хранить как Tree, так и Detail DTO
BuildingDTO = Union[BuildingTreeDTO, BuildingDetailDTO]


# ===== КЛАСС =====
class BuildingRepository(BaseRepository[BuildingDTO]):
    """Репозиторий для работы с корпусами."""

    def __init__(self, graph) -> None:
        super().__init__(graph, NodeType.BUILDING)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_floor_ids(self, building_id: int) -> List[int]:
        """
        Возвращает ID всех этажей корпуса.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.BUILDING, building_id)

    def get_by_complex(self, complex_id: int) -> List[int]:
        """
        Возвращает ID всех корпусов комплекса.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.COMPLEX, complex_id)

    # ---- УДОБНЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С TREE/DETAIL ----
    def get_tree(self, building_id: int) -> Optional[BuildingTreeDTO]:
        """
        Возвращает TreeDTO корпуса (минимальные данные).

        Returns:
            BuildingTreeDTO или None, если не найден
        """
        entity = self.get(building_id)
        if entity and not entity.IS_DETAIL:
            return cast(BuildingTreeDTO, entity)
        return None

    def get_detail(self, building_id: int) -> Optional[BuildingDetailDTO]:
        """
        Возвращает DetailDTO корпуса (полные данные).

        Returns:
            BuildingDetailDTO или None, если не найден или есть только TreeDTO
        """
        entity = self.get(building_id)
        if entity and entity.IS_DETAIL:
            return cast(BuildingDetailDTO, entity)
        return None

    def has_detail(self, building_id: int) -> bool:
        """Проверяет, загружены ли полные данные корпуса."""
        entity = self.get(building_id)
        return entity is not None and entity.IS_DETAIL