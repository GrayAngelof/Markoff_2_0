# client/src/data/repositories/__init__.py
"""
Публичное API репозиториев.

Экспортирует репозитории для всех типов сущностей.
"""

from .base import BaseRepository
from .complex import ComplexRepository
from .building import BuildingRepository
from .floor import FloorRepository
from .room import RoomRepository
from .counterparty import CounterpartyRepository
from .responsible_person import ResponsiblePersonRepository

__all__ = [
    'BaseRepository',
    'ComplexRepository',
    'BuildingRepository',
    'FloorRepository',
    'RoomRepository',
    'CounterpartyRepository',
    'ResponsiblePersonRepository',
]