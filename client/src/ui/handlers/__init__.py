# client/src/ui/handlers/__init__.py
"""
Обработчики событий UI слоя.

Подписываются на события EventBus и обновляют виджеты.
"""

# ===== ИМПОРТЫ =====
from .details_handler import DetailsUiHandler
from .tree_handler import TreeUiHandler


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Обработчик событий панели деталей
    "DetailsUiHandler",
    # Обработчик событий дерева объектов 
    "TreeUiHandler",
]