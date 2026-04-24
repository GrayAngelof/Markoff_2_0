# client/src/ui/details/panel.py
"""
Главный контейнер правой панели детальной информации.

Содержит шапку, сетку информации и вкладки.
По умолчанию показывает заглушку, при выборе узла переключается на содержимое.

TODO: Реализовать обновление вкладок при получении ViewModel
"""

# ===== ИМПОРТЫ =====
from typing import Dict, Optional

from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.core import EventBus
from src.core.types.nodes import NodeIdentifier
from src.ui.details.details_tabs import DetailsTabs
from src.ui.details.header import HeaderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.placeholder import PlaceholderWidget
from src.view_models.details import DetailsViewModel
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsPanel(QWidget):
    """
    Правая панель детальной информации.

    Получает DetailsViewModel и отображает:
    - Заголовок (HeaderWidget)
    - Сетку информации (InfoGrid)
    - Вкладки (DetailsTabs) — пока заглушки
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует панель детальной информации."""
        log.system("DetailsPanel инициализация")
        super().__init__(parent)

        self._bus: Optional[EventBus] = None
        self._current_node: Optional[NodeIdentifier] = None
        self._current_view_model: Optional[DetailsViewModel] = None

        # Кэш последних ViewModel для быстрого переключения между узлами
        self._view_model_cache: Dict[NodeIdentifier, DetailsViewModel] = {}

        self._setup_ui()
        self._setup_initial_state()

        log.system("DetailsPanel инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def set_event_bus(self, bus: EventBus) -> None:
        """Устанавливает шину событий."""
        self._bus = bus
        log.system("EventBus установлен")

    def update_content(self, vm: DetailsViewModel, node: NodeIdentifier) -> None:
        """
        Обновляет панель на основе ViewModel.

        Args:
            vm: ViewModel с данными для отображения
            node: Идентификатор узла (для кэширования)
        """
        log.debug(f"Обновление панели для {node.node_type.value}#{node.node_id}: {vm.header_title}")

        self._current_node = node
        self._current_view_model = vm

        self._view_model_cache[node] = vm

        self._header.update_content(vm)
        self._info_grid.update_content(vm)
        # TODO: Обновлять вкладки на основе данных из VM
        # self._tabs.update_content(vm)

        self._show_content()

    def get_cached_view_model(self, node: NodeIdentifier) -> Optional[DetailsViewModel]:
        """Возвращает кэшированную ViewModel для узла."""
        return self._view_model_cache.get(node)

    def clear_cache(self) -> None:
        """Очищает кэш ViewModel (например, при полном обновлении)."""
        self._view_model_cache.clear()
        log.debug("Кэш ViewModel очищен")

    @property
    def header(self) -> HeaderWidget:
        """Возвращает виджет шапки."""
        return self._header

    @property
    def placeholder(self) -> Optional[PlaceholderWidget]:
        """Возвращает виджет-заглушку (может быть None после первого показа)."""
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
        content_layout.addWidget(self._info_grid)
        log.success("InfoGrid создан")

        self._tabs = DetailsTabs(self._content_widget)
        content_layout.addWidget(self._tabs)
        log.success("DetailsTabs создан")

        content_layout.addStretch()
        layout.addWidget(self._content_widget, 1)

    def _setup_initial_state(self) -> None:
        """Устанавливает начальное состояние панели (показываем заглушку)."""
        if self._placeholder is not None:
            self._placeholder.setVisible(True)
        self._info_grid.setVisible(False)
        self._tabs.setVisible(False)

    def _show_content(self) -> None:
        """
        Переключает отображение с заглушки на содержимое.

        При первом вызове полностью удаляет PlaceholderWidget из layout.
        """
        # При первом показе — удаляем заглушку навсегда
        if self._placeholder is not None:
            layout = self._content_widget.layout()
            if layout is not None:
                layout.removeWidget(self._placeholder)
            self._placeholder.deleteLater()
            self._placeholder = None
            log.debug("PlaceholderWidget удалён")

        if not self._info_grid.isVisible():
            self._info_grid.setVisible(True)

        if not self._tabs.isVisible():
            self._tabs.setVisible(True)