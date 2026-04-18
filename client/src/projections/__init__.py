# client/src/projections/__init__.py
"""
Проекции — слой преобразования данных для UI.
"""

from src.projections.tree import TreeProjection
from src.projections.tree_node import TreeNode

__all__ = [
    "TreeProjection",
    "TreeNode",
]