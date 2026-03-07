# client/src/ui/main_window/components/__init__.py
"""
Компоненты пользовательского интерфейса главного окна.

Предоставляет:
- CentralWidget: центральный виджет с разделителем
- Toolbar: панель инструментов с меню обновления
- StatusBar: строка статуса с индикатором соединения
"""
from src.ui.main_window.components.central_widget import CentralWidget
from src.ui.main_window.components.toolbar import Toolbar
from src.ui.main_window.components.status_bar import StatusBar

__all__ = [
    "CentralWidget",
    "Toolbar",
    "StatusBar"
]