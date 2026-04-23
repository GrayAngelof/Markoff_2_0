# client/src/projections/__init__.py
"""
Проекции — слой преобразования данных для UI.
"""

from .tree import TreeProjection
from .tree_node import TreeNode

__all__ = [
    "TreeProjection",
    "TreeNode",
]