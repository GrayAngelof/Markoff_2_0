# client/src/ui/common/central_widget.py
"""
Центральный виджет с разделителем 30/70.
Левая панель — TreeView, правая — PlaceholderWidget (заглушка) и DetailsPanel.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QStackedWidget
from PySide6.QtCore import Qt
from typing import Optional

from src.ui.tree.view import TreeView
from src.ui.details import DetailsPanel
from src.ui.details.placeholder import PlaceholderWidget

from utils.logger import get_logger

log = get_logger(__name__)


class CentralWidget:
    """
    Центральный виджет с разделителем.
    
    Левая панель — TreeView
    Правая панель — QStackedWidget с PlaceholderWidget и DetailsPanel
    
    Управление:
    - По умолчанию: показан PlaceholderWidget, DetailsPanel скрыт
    - По событию ShowDetailsPanel: PlaceholderWidget скрывается, DetailsPanel показывается
    
    Методы:
    - get_tree_view() — получить TreeView для установки модели
    - get_details_panel() — получить DetailsPanel для настройки (EventBus)
    - central_widget — получить QWidget для установки в MainWindow
    """
    
    # Индексы в QStackedWidget
    _INDEX_PLACEHOLDER = 0
    _INDEX_DETAILS = 1
    
    def __init__(self) -> None:
        """Инициализирует центральный виджет."""
        log.info("Инициализация CentralWidget")
        
        self._container = QWidget()
        self._stacked: Optional[QStackedWidget] = None
        self._placeholder: Optional[PlaceholderWidget] = None
        self._details_panel: Optional[DetailsPanel] = None
        self._tree_view: Optional[TreeView] = None
        
        self._setup_layout()
        
        log.system("CentralWidget инициализирован")
    
    def _setup_layout(self) -> None:
        """Настраивает layout и разделитель."""
        layout = QHBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель — TreeView
        self._tree_view = TreeView()
        log.success("TreeView создан")
        splitter.addWidget(self._tree_view)
        
        # Правая панель — QStackedWidget (переключение между заглушкой и панелью)
        self._stacked = QStackedWidget()
        
        # Заглушка (видима по умолчанию)
        self._placeholder = PlaceholderWidget()
        self._stacked.addWidget(self._placeholder)  # индекс 0
        log.success("PlaceholderWidget создан и добавлен")
        
        # Панель деталей (скрыта по умолчанию)
        self._details_panel = DetailsPanel()
        self._stacked.addWidget(self._details_panel)  # индекс 1
        self._details_panel.setVisible(False)  # явно скрываем
        log.success("DetailsPanel создан и скрыт")
        
        # Устанавливаем видимым placeholder
        self._stacked.setCurrentIndex(self._INDEX_PLACEHOLDER)
        
        splitter.addWidget(self._stacked)
        splitter.setSizes([300, 700])  # 30% / 70% от 1024
        
        layout.addWidget(splitter)
        
        log.debug("CentralWidget: splitter настроен (TreeView слева, QStackedWidget справа)")
    
    def show_details_panel(self) -> None:
        """
        Переключает правую панель с заглушки на DetailsPanel.
        Вызывается при получении события ShowDetailsPanel.
        """
        if self._stacked is None:
            log.error("CentralWidget: QStackedWidget не инициализирован")
            return
        
        if self._stacked.currentIndex() == self._INDEX_DETAILS:
            log.debug("CentralWidget: DetailsPanel уже видим")
            return
        
        self._stacked.setCurrentIndex(self._INDEX_DETAILS)
        log.info("CentralWidget: показан DetailsPanel, заглушка скрыта")
    
    def get_tree_view(self) -> TreeView:
        """
        Возвращает TreeView для установки модели.
        
        Returns:
            TreeView: Виджет дерева
            
        Raises:
            ValueError: Если TreeView не инициализирован
        """
        if self._tree_view is None:
            raise ValueError("TreeView не инициализирован")
        return self._tree_view
    
    def get_details_panel(self) -> DetailsPanel:
        """
        Возвращает DetailsPanel для настройки (подписка на EventBus и т.д.).
        
        Returns:
            DetailsPanel: Панель детальной информации
            
        Raises:
            ValueError: Если DetailsPanel не инициализирован
        """
        if self._details_panel is None:
            raise ValueError("DetailsPanel не инициализирован")
        return self._details_panel
    
    @property
    def central_widget(self) -> QWidget:
        """
        Возвращает QWidget для установки в MainWindow.
        
        Returns:
            QWidget: Контейнер центрального виджета
        """
        return self._container