# client/src/data/repositories/complex.py
"""
Репозиторий для комплексов.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_building_ids() — навигация по графу (получение ID детей)

Никакой бизнес-логики: фильтрация по владельцу, поиск по имени — только в сервисах!
Работает с TreeDTO и DetailDTO.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, Union, cast

from src.core.types import NodeType
from src.models import ComplexTreeDTO, ComplexDetailDTO
from .base import BaseRepository


# ===== ТИПЫ =====
# Репозиторий может хранить как Tree, так и Detail DTO
ComplexDTO = Union[ComplexTreeDTO, ComplexDetailDTO]


# ===== КЛАСС =====
class ComplexRepository(BaseRepository[ComplexDTO]):
    """Репозиторий для работы с комплексами."""

    def __init__(self, graph) -> None:
        super().__init__(graph, NodeType.COMPLEX)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_building_ids(self, complex_id: int) -> List[int]:
        """
        Возвращает ID всех корпусов комплекса.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.COMPLEX, complex_id)

    # ---- УДОБНЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С TREE/DETAIL ----
    def get_tree(self, complex_id: int) -> Optional[ComplexTreeDTO]:
        """
        Возвращает TreeDTO комплекса (минимальные данные).

        Returns:
            ComplexTreeDTO или None, если не найден
        """
        entity = self.get(complex_id)
        if entity and not entity.IS_DETAIL:
            return cast(ComplexTreeDTO, entity)
        return None

    def get_detail(self, complex_id: int) -> Optional[ComplexDetailDTO]:
        """
        Возвращает DetailDTO комплекса (полные данные).

        Returns:
            ComplexDetailDTO или None, если не найден или есть только TreeDTO
        """
        entity = self.get(complex_id)
        if entity and entity.IS_DETAIL:
            return cast(ComplexDetailDTO, entity)
        return None

    def has_detail(self, complex_id: int) -> bool:
        """Проверяет, загружены ли полные данные комплекса."""
        entity = self.get(complex_id)
        return entity is not None and entity.IS_DETAIL