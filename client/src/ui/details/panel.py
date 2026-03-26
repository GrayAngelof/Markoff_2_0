# client/src/ui/details/panel.py
"""
Главный контейнер правой панели детальной информации.
На данном этапе — только структурный скелет без логики.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from typing import Optional

from src.ui.details.header import HeaderWidget
from src.ui.details.placeholder import PlaceholderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.details_tabs import DetailsTabs

from utils.logger import get_logger

log = get_logger(__name__)


class DetailsPanel(QWidget):
    """
    Правая панель детальной информации.
    
    На данном этапе:
    - Создает структурный каркас
    - Не содержит логики загрузки данных
    - Не подписывается на события
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует панель детальной информации.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        log.debug("DetailsPanel: создание структурного каркаса")
        
        self._setup_ui()
        
        log.debug("DetailsPanel: структурный каркас создан")

        log.system("DetailsPanel инициализирован")
    
    def _setup_ui(self) -> None:
        """Создает структурный каркас панели."""
        # Основной вертикальный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Шапка панели
        self._header = HeaderWidget(self)
        layout.addWidget(self._header)
        
        # Контейнер для основного контента
        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Заглушка (показывается по умолчанию)
        self._placeholder = PlaceholderWidget(self._content_widget)
        content_layout.addWidget(self._placeholder)
        
        # Сетка информации (скрыта по умолчанию)
        self._info_grid = InfoGrid(self._content_widget)
        self._info_grid.setVisible(False)
        content_layout.addWidget(self._info_grid)
        
        # Вкладки
        self._tabs = DetailsTabs(self._content_widget)
        content_layout.addWidget(self._tabs)
        
        # Растяжка в конце
        content_layout.addStretch()
        
        layout.addWidget(self._content_widget, 1)  # Растягивается
        
        log.debug("DetailsPanel: UI каркас создан")
    
    # ===== Геттеры (для будущего использования) =====
    
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