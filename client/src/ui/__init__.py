# client/src/ui/__init__.py
"""
Инициализатор пакета UI.
Экспортирует все основные компоненты интерфейса.
"""

# Импортируем из новых пакетов
from src.ui.tree import TreeView
from src.ui.details import DetailsPanel
from src.ui.main_window import MainWindow
from src.ui.refresh_menu import RefreshMenu

__all__ = [
    "TreeView",
    "DetailsPanel", 
    "MainWindow",
    "RefreshMenu"
]