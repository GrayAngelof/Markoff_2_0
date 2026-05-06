# backend/src/app/reference_entity/__init__.py
"""
Пакет reference_entity — сущности, загружаемые по ID (lazy loading).
"""

from .counterparty import router as counterparty_router
from .responsible_person import router as responsible_person_router

__all__ = [
    "counterparty_router",
    "responsible_person_router",
]