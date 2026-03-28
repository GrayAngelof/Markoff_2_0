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
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.core import NodeType
from src.models import Complex
from .base import BaseRepository


# ===== КЛАСС =====
class ComplexRepository(BaseRepository[Complex]):
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