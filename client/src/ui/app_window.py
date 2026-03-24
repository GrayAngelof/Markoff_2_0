# client/src/ui/app_window.py
"""
Фасад UI слоя.
Собирает главное окно из постоянных компонентов.
"""

from PySide6.QtWidgets import QMainWindow

from src.core.event_bus import EventBus

from src.ui.main_window.window import MainWindow
from src.ui.main_window.menu import MenuBar
from src.ui.main_window.toolbar import Toolbar
from src.ui.main_window.status_bar import StatusBar
from src.ui.common.central_widget import CentralWidget

from utils.logger import get_logger

log = get_logger(__name__)


class AppWindow:
    """
    Фасад UI слоя.
    Собирает главное окно из компонентов.
    """
    
    def __init__(self, bus: EventBus):
        # Создаем пустую оболочку
        self._window = MainWindow()
        
        # Создаем постоянные компоненты (только визуал)
        self._menu = MenuBar()
        self._toolbar = Toolbar()
        self._status_bar = StatusBar(bus)
        
        # Создаем центральную область с заглушками
        self._central = CentralWidget()
        
        # Компонуем окно
        self._window.setMenuBar(self._menu)
        self._window.addToolBar(self._toolbar)
        self._window.setStatusBar(self._status_bar)
        self._window.setCentralWidget(self._central.central_widget)
        
        log.success("AppWindow создан (только визуал)")
    
    def get_window(self) -> QMainWindow:
        """Возвращает QMainWindow для отображения."""
        return self._window