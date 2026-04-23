# client/src/ui/coordinator.py
"""
Координатор глобальных UI-действий.

Подписывается на события, которые требуют прямого управления виджетами:
- ShowDetailsPanel → показать панель деталей
- CollapseAllRequested → свернуть всё дерево
"""

# ===== ИМПОРТЫ =====
from src.core import EventBus
from src.core.events.definitions import CollapseAllRequested, ShowDetailsPanel
from src.ui.app_window import AppWindow
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class UiCoordinator:
    """
    Координатор UI (минимальный).

    Отвечает за:
    - Переключение правой панели (заглушка ↔ DetailsPanel)
    - Сворачивание дерева по запросу
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, app_window: AppWindow) -> None:
        """Инициализирует координатор."""
        log.system("UiCoordinator инициализация")
        self._bus = bus
        self._app_window = app_window
        self._subscriptions = []
        log.system("UiCoordinator инициализирован")

    def start(self) -> None:
        """Подписывается на события."""
        log.info("Запуск UiCoordinator")
        self._subscriptions.append(
            self._bus.subscribe(ShowDetailsPanel, self._on_show_details)
        )
        self._subscriptions.append(
            self._bus.subscribe(CollapseAllRequested, self._on_collapse_all)
        )
        log.success("UiCoordinator запущен")

    def cleanup(self) -> None:
        """Отписывается от событий."""
        log.info("Очистка UiCoordinator")
        for sub in self._subscriptions:
            sub()
        self._subscriptions.clear()
        log.success("UiCoordinator очищен")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_show_details(self, _event: ShowDetailsPanel) -> None:
        """Показывает панель деталей (скрывает заглушку)."""
        self._app_window.show_details_panel()
        log.debug("Панель деталей показана")

    def _on_collapse_all(self, _event: CollapseAllRequested) -> None:
        """Сворачивает все узлы дерева."""
        tree_view = self._app_window.get_tree_view()
        tree_view.collapse_all()
        log.debug("Дерево свёрнуто")