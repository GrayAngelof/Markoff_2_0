# client/src/data/__init__.py
"""
Публичное API Data слоя.

Экспортирует только фасад графа и репозитории.
Внутренности (graph/*) не доступны напрямую.
"""

from .entity_graph import EntityGraph, EntityGraphStats

__all__ = [
    'EntityGraph',
    'EntityGraphStats',
]