# client/src/ui/app_window.py
"""
Фасад UI слоя.

Собирает главное окно из постоянных компонентов.
Принципы работы:
1. AppWindow создаёт ВСЕ UI компоненты (не принимает их извне)
2. Компоненты создаются в порядке: оболочка → постоянные → центральная область
3. Геттеры позволяют контроллерам устанавливать модели и подписывать компоненты
4. Подписки на события обрабатываются здесь же, делегируя управление CentralWidget
"""

# ===== ИМПОРТЫ =====
from PySide6.QtWidgets import QMainWindow

from src.core import EventBus
from src.core.events.definitions import RefreshRequested, ShowDetailsPanel
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
    - Создание пустого MainWindow
    - Создание постоянных компонентов (MenuBar, Toolbar, StatusBar)
    - Создание CentralWidget (TreeView и DetailsPanel внутри)
    - Компоновку всех компонентов в окне
    - Подписку на глобальные UI-события (ShowDetailsPanel, RefreshRequested)
    - Предоставление геттеров для контроллеров

    НЕ отвечает за:
    - Создание моделей данных (TreeModel)
    - Бизнес-логику (передаётся контроллерам)
    - Решение, когда показывать DetailsPanel (только делегирует CentralWidget)
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus) -> None:
        """Инициализирует фасад UI слоя."""
        log.info("Инициализация AppWindow")

        self._bus = bus
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

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

        # Подписка на события
        self._bus.subscribe(ShowDetailsPanel, self._on_show_details_panel)
        log.link("AppWindow подписан на ShowDetailsPanel")

        # Подключение сигналов UI к EventBus
        self._toolbar.refresh_triggered.connect(self._on_refresh_triggered)
        log.link("Toolbar.refresh_triggered подключён")

        # Компоновка
        self._window.setMenuBar(self._menu)
        self._window.addToolBar(self._toolbar)
        self._window.setStatusBar(self._status_bar)
        self._window.setCentralWidget(self._central.central_widget)

        log.system("AppWindow инициализирован")

    # ---- ПУБЛИЧНОЕ API (ГЕТТЕРЫ ДЛЯ КОНТРОЛЛЕРОВ) ----
    def get_tree_view(self):
        """Возвращает TreeView для установки модели."""
        return self._central.get_tree_view()

    def get_details_panel(self):
        """Возвращает DetailsPanel для дополнительной настройки."""
        return self._central.get_details_panel()

    def get_window(self) -> QMainWindow:
        """Возвращает QMainWindow для отображения."""
        return self._window

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_show_details_panel(self, event_data: ShowDetailsPanel) -> None:
        """
        Обрабатывает событие показа панели деталей.

        Делегирует переключение видимости CentralWidget.
        """
        log.debug("AppWindow: получено ShowDetailsPanel, переключаем панель")
        self._central.show_details_panel()

    def _on_refresh_triggered(self, mode: str) -> None:
        """
        Обрабатывает клик по кнопке обновления.

        Преобразует UI-сигнал в событие EventBus.

        Args:
            mode: Режим обновления ('current', 'visible', 'full')
        """
        log.info(f"Запрос обновления: режим {mode}")
        self._bus.emit(RefreshRequested(mode=mode))