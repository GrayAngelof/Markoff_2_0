# backend/src/models/__init__.py
"""
Инициализатор пакета моделей
Экспортирует модели из всех схем
"""
from .physical import Complex, Building, Floor, Room, Zone
from .dictionary import (
    CounterpartyStatus,
    CounterpartyType,
    RoleCatalog,
    Counterparty,
    ResponsiblePerson
)

__all__ = [
    # Physical
    "Complex",
    "Building",
    "Floor",
    "Room",
    "Zone",
    
    # Dictionary
    "CounterpartyStatus",
    "CounterpartyType",
    "RoleCatalog",
    "Counterparty",
    "ResponsiblePerson"
]