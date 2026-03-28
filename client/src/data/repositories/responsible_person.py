# client/src/data/repositories/responsible_person.py
"""
Репозиторий для ответственных лиц.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_by_counterparty() — навигация по графу (получение ID детей)

Никакой бизнес-логики: фильтрация, сортировка, агрегация — только в сервисах!
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.core import NodeType
from src.models import ResponsiblePerson
from .base import BaseRepository


# ===== КЛАСС =====
class ResponsiblePersonRepository(BaseRepository[ResponsiblePerson]):
    """Репозиторий для работы с ответственными лицами."""

    def __init__(self, graph) -> None:
        super().__init__(graph, NodeType.RESPONSIBLE_PERSON)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_by_counterparty(self, counterparty_id: int) -> List[int]:
        """
        Возвращает ID всех ответственных лиц контрагента.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.COUNTERPARTY, counterparty_id)