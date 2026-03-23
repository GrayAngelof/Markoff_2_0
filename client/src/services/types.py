# client/src/services/types.py
"""
Типы данных для сервисного слоя.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from models import Building, Counterparty, ResponsiblePerson


@dataclass(frozen=True, slots=True)
class BuildingWithOwnerResult:
    """
    Результат загрузки корпуса с владельцем.
    
    Все поля могут быть None или пустыми, чтобы упростить создание.
    
    Attributes:
        building: Загруженный корпус
        owner: Владелец корпуса (если есть)
        responsible_persons: Список ответственных лиц владельца
    """
    building: Building
    owner: Optional[Counterparty] = None
    responsible_persons: List[ResponsiblePerson] = field(default_factory=list)