# client/src/ui/tree/__init__.py
"""
Модуль дерева объектов.

Содержит модель и представление для иерархического дерева.
"""

# ===== ИМПОРТЫ =====
from .model import TreeModel
from .view import TreeView


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Модель данных для QTreeView
    "TreeModel",
    # Виджет дерева с эмиссией событий через EventBus
    "TreeView",
]