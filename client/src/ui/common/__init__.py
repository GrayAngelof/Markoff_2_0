# client/src/ui/common/__init__.py
"""
Общие компоненты UI, используемые несколькими модулями.
"""

# ===== ИМПОРТЫ  =====
from .central_widget import CentralWidget


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Центральный виджет с разделением на дерево и панель деталей
    "CentralWidget", 
]