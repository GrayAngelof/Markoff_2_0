# client/src/models/entity/__init__.py
"""
DTO для сущностей (reference_entity layer).
"""

from .counterparty import CounterpartyDTO
from .responsible_person import ResponsiblePersonDTO

__all__ = [
    "CounterpartyDTO",
    "ResponsiblePersonDTO",
]