# client/src/projections/__init__.py
"""
Проекции — слой преобразования данных для UI.

Содержит:
- TreeProjection — построение иерархического дерева TreeNode
- TreeNode — узел дерева для отображения
- DetailsProjection — сборка ViewModel для панели деталей
"""

# ===== ИМПОРТЫ =====
from .details_projection import DetailsProjection
from .tree import TreeProjection
from .tree_node import TreeNode


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "DetailsProjection",
    "TreeProjection",
    "TreeNode",
]