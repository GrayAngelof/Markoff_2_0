# client/src/models/__init__.py
"""
Модели данных для клиента.
Экспортирует все модели для удобного импорта.

Обновлён для поддержки:
- Контрагентов (Counterparty)
- Ответственных лиц (ResponsiblePerson)
"""
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson

__all__ = [
    "Complex",
    "Building",
    "Floor",
    "Room",
    "Counterparty",
    "ResponsiblePerson",
]