# client/src/services/types.py
"""
Типы данных для сервисного слоя.

Содержит общие типы и структуры данных,
используемые несколькими сервисами.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from typing import List, Optional

from src.models import Building, Counterparty, ResponsiblePerson


# ===== ТИПЫ =====
@dataclass(frozen=True, slots=True)
class BuildingWithOwnerResult:
    """
    Результат загрузки корпуса с владельцем.

    Attributes:
        building: Загруженный корпус
        owner: Владелец корпуса (если есть)
        responsible_persons: Список ответственных лиц владельца
    """
    building: Building
    owner: Optional[Counterparty] = None
    responsible_persons: List[ResponsiblePerson] = field(default_factory=list)