# client/src/ui/app_window.py
"""
Фасад UI слоя.

Собирает главное окно из постоянных компонентов.
"""

# ===== ИМПОРТЫ =====
from PySide6.QtWidgets import QMainWindow

from src.core import EventBus
from src.core.events.definitions import RefreshRequested
from src.ui.common.central_widget import CentralWidget
from src.ui.main_window.menu import MenuBar
from src.ui.main_window.status_bar import StatusBar
from src.ui.main_window.toolbar import Toolbar
from src.ui.main_window.window import MainWindow
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class AppWindow:
    """
    Фасад UI слоя — единственный композиционный корень.

    Отвечает за:
    - Создание всех UI компонентов
    - Предоставление геттеров для виджетов
    - Предоставление методов для управления UI (show_details_panel)

    НЕ отвечает за:
    - Подписку на события (это делают UiHandler / UiCoordinator)
    - Бизнес-логику
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus) -> None:
        """Инициализирует фасад UI слоя."""
        log.system("AppWindow инициализация")

        self._bus = bus

        self._window = MainWindow()
        log.success("MainWindow создан")

        self._menu = MenuBar()
        log.success("MenuBar создан")

        self._toolbar = Toolbar()
        log.success("Toolbar создан")

        self._status_bar = StatusBar(bus)
        log.success("StatusBar создан")

        self._central = CentralWidget()
        log.success("CentralWidget создан")

        # Настройка TreeView
        tree_view = self._central.get_tree_view()
        tree_view.set_event_bus(bus)
        log.success("TreeView настроен (EventBus передан)")

        # Настройка DetailsPanel
        self._details_panel = self._central.get_details_panel()
        self._details_panel.set_event_bus(bus)
        log.success("DetailsPanel настроен (EventBus передан)")

        # Подключение сигналов UI к EventBus (только преобразование сигналов в события)
        self._toolbar.refresh_triggered.connect(self._on_refresh_triggered)
        log.link("Toolbar.refresh_triggered подключён")

        # Компоновка
        self._window.setMenuBar(self._menu)
        self._window.addToolBar(self._toolbar)
        self._window.setStatusBar(self._status_bar)
        self._window.setCentralWidget(self._central.central_widget)

        log.system("AppWindow инициализирован")

    # ---- ПУБЛИЧНОЕ API (ГЕТТЕРЫ ДЛЯ КОНТРОЛЛЕРОВ И COORDINATOR) ----
    def get_tree_view(self):
        """Возвращает TreeView для установки модели."""
        return self._central.get_tree_view()

    def get_details_panel(self):
        """Возвращает DetailsPanel для дополнительной настройки."""
        return self._central.get_details_panel()

    def get_window(self) -> QMainWindow:
        """Возвращает QMainWindow для отображения."""
        return self._window

    def show_details_panel(self) -> None:
        """Переключает правую панель с заглушки на DetailsPanel."""
        self._central.show_details_panel()
        log.debug("DetailsPanel показан через AppWindow")

    # ---- ОБРАБОТЧИКИ СИГНАЛОВ (преобразование в события) ----
    def _on_refresh_triggered(self, mode: str) -> None:
        """
        Обрабатывает клик по кнопке обновления.

        Преобразует UI-сигнал в событие EventBus.
        """
        log.info(f"Запрос обновления: режим {mode}")
        self._bus.emit(RefreshRequested(mode=mode))