# client/src/ui/main_window/main_window.py
"""
Главное окно приложения Markoff.
Объединяет все компоненты и контроллеры для создания полноценного интерфейса
с деревом объектов и панелью детальной информации.
"""
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot, QTimer

from src.ui.tree import TreeView
from src.ui.details import DetailsPanel
from src.ui.main_window.components.central_widget import CentralWidget
from src.ui.main_window.components.toolbar import Toolbar
from src.ui.main_window.components.status_bar import StatusBar
from src.ui.main_window.shortcuts import ShortcutManager
from src.ui.main_window.controllers.refresh_controller import RefreshController
from src.ui.main_window.controllers.data_controller import DataController
from src.ui.main_window.controllers.connection_controller import ConnectionController
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    
    Компоновка:
    - Левая часть: дерево объектов (TreeView)
    - Правая часть: информационная панель (DetailsPanel)
    
    Панель инструментов:
    - Кнопка с меню для выбора типа обновления
    - Индикатор статуса подключения
    - Счётчик загруженных объектов
    
    Горячие клавиши:
    - F5: обновить текущий узел
    - Ctrl+F5: обновить все раскрытые узлы
    - Ctrl+Shift+F5: полная перезагрузка
    """
    
    # ===== Константы =====
    _WINDOW_TITLE = "Markoff - Управление помещениями"
    """Заголовок окна"""
    
    _MINIMUM_WIDTH = 1000
    """Минимальная ширина окна в пикселях"""
    
    _MINIMUM_HEIGHT = 700
    """Минимальная высота окна в пикселях"""
    
    def __init__(self) -> None:
        """Инициализирует главное окно."""
        super().__init__()
        
        # Настройка окна
        self._setup_window()
        
        # Создание компонентов UI
        self._create_components()
        
        # Создание контроллеров
        self._create_controllers()
        
        # Подключение сигналов
        self._connect_signals()
        
        log.success("MainWindow: создано")
    
    # ===== Приватные методы инициализации =====
    
    def _setup_window(self) -> None:
        """Настраивает параметры главного окна."""
        self.setWindowTitle(self._WINDOW_TITLE)
        self.setMinimumSize(self._MINIMUM_WIDTH, self._MINIMUM_HEIGHT)
        log.debug("MainWindow: параметры окна установлены")
    
    def _create_components(self) -> None:
        """Создаёт все компоненты пользовательского интерфейса."""
        # Создаём компоненты
        self._tree_view = TreeView(self)
        self._details_panel = DetailsPanel(self)
        
        # Создаём центральный виджет с разделителем
        self._central = CentralWidget(self)
        self._central.add_widgets(self._tree_view, self._details_panel)
        
        # Создаём панель инструментов
        self._toolbar = Toolbar(self)
        
        # Создаём строку статуса
        self._status_bar = StatusBar(self)
        
        # Создаём менеджер горячих клавиш
        self._shortcuts = ShortcutManager(self)
        
        log.debug("MainWindow: все компоненты созданы")
    
    def _create_controllers(self) -> None:
        """Создаёт все контроллеры для обработки логики."""
        # Контроллер обновления
        self._refresh_controller = RefreshController(
            self._tree_view,
            self._status_bar
        )
        
        # Контроллер данных
        self._data_controller = DataController(
            self._tree_view,
            self._status_bar,
            self._toolbar.counter_action
        )
        
        # Контроллер соединения
        self._connection_controller = ConnectionController(
            self._tree_view,
            self._toolbar,
            self._status_bar
        )
        
        log.debug("MainWindow: все контроллеры созданы")
    
    def _connect_signals(self) -> None:
        """Подключает все сигналы между компонентами."""
        
        # Сигнал выбора элемента в дереве -> панель деталей
        self._tree_view.item_selected.connect(
            self._details_panel.show_item_details
        )
        
        # Сигналы загрузки данных -> контроллер данных
        self._tree_view.data_loading.connect(
            self._data_controller.on_data_loading
        )
        self._tree_view.data_loaded.connect(
            self._data_controller.on_data_loaded
        )
        self._tree_view.data_error.connect(
            self._data_controller.on_data_error
        )
        
        # Сигналы от панели инструментов -> контроллер обновления
        self._toolbar.signals.refresh_current.connect(
            self._refresh_controller.refresh_current
        )
        self._toolbar.signals.refresh_visible.connect(
            self._refresh_controller.refresh_visible
        )
        self._toolbar.signals.full_reset.connect(
            self._refresh_controller.full_reset
        )
        
        # Сигналы от горячих клавиш -> контроллер обновления
        self._shortcuts.signals.refresh_current.connect(
            self._refresh_controller.refresh_current
        )
        self._shortcuts.signals.refresh_visible.connect(
            self._refresh_controller.refresh_visible
        )
        self._shortcuts.signals.full_reset.connect(
            self._refresh_controller.full_reset
        )
        
        log.debug("MainWindow: все сигналы подключены")
    
    # ===== Геттеры =====
    
    @property
    def tree_view(self) -> TreeView:
        """Возвращает виджет дерева."""
        return self._tree_view
    
    @property
    def details_panel(self) -> DetailsPanel:
        """Возвращает панель деталей."""
        return self._details_panel
    
    # ===== Обработчик закрытия =====
    
    def closeEvent(self, event) -> None:
        """
        Обрабатывает закрытие окна.
        Останавливает все контроллеры и очищает ресурсы.
        
        Args:
            event: Событие закрытия
        """
        log.info("Завершение работы...")
        
        # Останавливаем проверку соединения
        if hasattr(self, '_connection_controller'):
            self._connection_controller.stop_checking()
        
        # Очищаем кэш
        if hasattr(self._tree_view, 'cache'):
            self._tree_view.cache.clear()
            log.debug("MainWindow: кэш очищен")
        
        event.accept()
        log.success("Приложение завершено")