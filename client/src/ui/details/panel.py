# client/src/ui/details/panel.py
"""
Главный контейнер правой панели детальной информации.

Содержит шапку, заглушку, сетку информации и вкладки.
По умолчанию показывает заглушку, при выборе узла переключается на содержимое.
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.core import EventBus
from src.ui.details.details_tabs import DetailsTabs
from src.ui.details.header import HeaderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.placeholder import PlaceholderWidget
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsPanel(QWidget):
    """
    Правая панель детальной информации.

    На данном этапе — только структурный каркас.
    По умолчанию показывает заглушку, при выборе узла будет показывать содержимое.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует панель детальной информации."""
        log.info("Инициализация DetailsPanel")
        super().__init__(parent)

        self._bus: Optional[EventBus] = None

        self._setup_ui()
        self._setup_default_state()

        log.system("DetailsPanel инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def set_event_bus(self, bus: EventBus) -> None:
        """Устанавливает шину событий и подписывается на события."""
        self._bus = bus
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

    @property
    def header(self) -> HeaderWidget:
        """Возвращает виджет шапки."""
        return self._header

    @property
    def placeholder(self) -> PlaceholderWidget:
        """Возвращает виджет-заглушку."""
        return self._placeholder

    @property
    def info_grid(self) -> InfoGrid:
        """Возвращает сетку информации."""
        return self._info_grid

    @property
    def tabs(self) -> DetailsTabs:
        """Возвращает виджет вкладок."""
        return self._tabs

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас панели."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._header = HeaderWidget(self)
        layout.addWidget(self._header)
        log.success("HeaderWidget создан")

        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        self._placeholder = PlaceholderWidget(self._content_widget)
        content_layout.addWidget(self._placeholder)
        log.success("PlaceholderWidget создан")

        self._info_grid = InfoGrid(self._content_widget)
        self._info_grid.setVisible(False)
        content_layout.addWidget(self._info_grid)
        log.success("InfoGrid создан")

        self._tabs = DetailsTabs(self._content_widget)
        content_layout.addWidget(self._tabs)
        log.success("DetailsTabs создан")

        content_layout.addStretch()
        layout.addWidget(self._content_widget, 1)

    def _setup_default_state(self) -> None:
        """Устанавливает начальное состояние панели."""
        self._placeholder.setVisible(True)
        self._info_grid.setVisible(False)