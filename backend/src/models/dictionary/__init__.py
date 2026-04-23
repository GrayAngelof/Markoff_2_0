# backend/src/models/dictionary/__init__.py
"""
Инициализатор пакета моделей схемы dictionary
"""
from .counterparty_status import CounterpartyStatus
from .counterparty_type import CounterpartyType
from .role_catalog import RoleCatalog
from .counterparty import Counterparty
from .responsible_person import ResponsiblePerson

__all__ = [
    "CounterpartyStatus",
    "CounterpartyType", 
    "RoleCatalog",
    "Counterparty",
    "ResponsiblePerson"
]