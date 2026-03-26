# client/src/ui/app_window.py
"""
Фасад UI слоя.
Собирает главное окно из постоянных компонентов.
"""

from PySide6.QtWidgets import QMainWindow, QWidget

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
    
    Отвечает за:
    - Создание пустого MainWindow
    - Создание постоянных компонентов (MenuBar, Toolbar, StatusBar)
    - Создание CentralWidget
    - Компоновку всех компонентов в окне
    - Предоставление методов для подмены правой панели
    
    НЕ отвечает за:
    - Создание DetailsPanel
    - Решение, когда подменять панели
    """
    
    def __init__(self, bus: EventBus):
        # Создаем пустую оболочку
        self._window = MainWindow()
        
        # Создаем постоянные компоненты
        self._menu = MenuBar()
        log.success("MenuBar создан")

        self._toolbar = Toolbar()
        log.success("Toolbar создан")

        self._status_bar = StatusBar(bus)
        log.success("StatusBar создан")
        
        # Создаем центральную область (TreeView сразу внутри)
        self._central = CentralWidget()
        log.success("CentralWidget создан")

        # Компонуем окно
        self._window.setMenuBar(self._menu)
        self._window.addToolBar(self._toolbar)
        self._window.setStatusBar(self._status_bar)
        self._window.setCentralWidget(self._central.central_widget)
        
        log.success("AppWindow создан")
    
    def get_window(self) -> QMainWindow:
        """Возвращает QMainWindow для отображения."""
        return self._window
    
    def get_tree_view(self):
        """Возвращает TreeView для установки модели."""
        return self._central.get_tree_view()
    
#    def set_right_panel(self, widget: QWidget) -> None:
        """
        Заменяет правую панель.
        Вызывается контроллерами (например, DetailsController).
        
        Args:
            widget: Новый виджет для правой панели
        """
#        self._central.set_right(widget)
#        log.debug("Правая панель заменена по запросу контроллера")