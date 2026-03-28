# client/src/data/repositories/counterparty.py
"""
Репозиторий для контрагентов.

ТОЛЬКО БАЗОВЫЕ ОПЕРАЦИИ ДОСТУПА:
- get() — получение по ID
- get_all() — все сущности
- get_ids() — все ID
- exists() — проверка существования
- add() — добавление/обновление
- remove() — удаление
- get_person_ids() — навигация по графу (получение ID детей)

Никакой бизнес-логики: фильтрация, поиск по ИНН, статус — только в сервисах!
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.core import NodeType
from src.models import Counterparty
from .base import BaseRepository


# ===== КЛАСС =====
class CounterpartyRepository(BaseRepository[Counterparty]):
    """Репозиторий для работы с контрагентами."""

    def __init__(self, graph) -> None:
        super().__init__(graph, NodeType.COUNTERPARTY)

    # ---- НАВИГАЦИЯ ПО ГРАФУ ----
    def get_person_ids(self, counterparty_id: int) -> List[int]:
        """
        Возвращает ID всех ответственных лиц контрагента.

        Это навигация по графу, а не бизнес-логика.
        Возвращаются ID, а не объекты — ленивая загрузка.
        """
        return self._graph.get_children(NodeType.COUNTERPARTY, counterparty_id)