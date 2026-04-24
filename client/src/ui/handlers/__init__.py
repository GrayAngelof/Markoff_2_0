# client/src/ui/handlers/__init__.py
"""
Обработчики событий UI слоя.

Содержит обработчики, которые подписываются на события EventBus
и обновляют виджеты (TreeView, DetailsPanel).
"""

# ===== ИМПОРТЫ =====
from .details_handler import DetailsUiHandler
from .tree_handler import TreeUiHandler


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "DetailsUiHandler",
    "TreeUiHandler",
]