# client/src/ui/details/panel.py
"""
Главный контейнер правой панели детальной информации.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from typing import Optional

from src.ui.details.header import HeaderWidget
from src.ui.details.placeholder import PlaceholderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.details_tabs import DetailsTabs
from src.core import EventBus
from src.core.events import ShowDetailsPanel

from utils.logger import get_logger

log = get_logger(__name__)


class DetailsPanel(QWidget):
    """
    Правая панель детальной информации.
    
    На данном этапе:
    - Показывает заглушку по умолчанию
    - Подписывается на ShowPlaceholder
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует панель детальной информации.
        
        Args:
            parent: Родительский виджет
        """
        log.info("Инициализация DetailsPanel")
        super().__init__(parent)
        
        self._bus: Optional[EventBus] = None
        
        self._setup_ui()
        self._setup_default_state()
        
        log.system("DetailsPanel инициализирован")

    def set_event_bus(self, bus: EventBus) -> None:
        """
        Устанавливает шину событий и подписывается на события.
        
        Args:
            bus: Шина событий
        """
        self._bus = bus
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")
    
    def _setup_ui(self) -> None:
        """Создает структурный каркас панели."""
        # Основной вертикальный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Шапка панели
        self._header = HeaderWidget(self)
        layout.addWidget(self._header)
        log.success("HeaderWidget создан")

        # Контейнер для основного контента
        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Заглушка (показывается по умолчанию)
        self._placeholder = PlaceholderWidget(self._content_widget)
        content_layout.addWidget(self._placeholder)
        log.success("PlaceholderWidget создан")

        # Сетка информации (скрыта по умолчанию)
        self._info_grid = InfoGrid(self._content_widget)
        self._info_grid.setVisible(False)
        content_layout.addWidget(self._info_grid)
        log.success("InfoGrid создан")

        # Вкладки
        self._tabs = DetailsTabs(self._content_widget)
        content_layout.addWidget(self._tabs)
        log.success("DetailsTabs создан")

        # Растяжка в конце
        content_layout.addStretch()

        layout.addWidget(self._content_widget, 1)
    
    def _setup_default_state(self) -> None:
        """Устанавливает начальное состояние панели."""
        # По умолчанию показываем заглушку, скрываем сетку
        self._placeholder.setVisible(True)
        self._info_grid.setVisible(False)
    
    # ===== Геттеры =====
    
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