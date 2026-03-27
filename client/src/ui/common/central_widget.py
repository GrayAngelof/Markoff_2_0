# client/src/ui/common/central_widget.py
"""
Центральный виджет с разделителем 30/70.
Левая панель — TreeView, правая — DetailsPanel.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt

from src.ui.tree.view import TreeView
from src.ui.details import DetailsPanel

from utils.logger import get_logger

log = get_logger(__name__)


class CentralWidget:
    """
    Центральный виджет с разделителем.
    
    Левая панель — TreeView
    Правая панель — DetailsPanel
    
    Методы:
    - get_tree_view() — получить TreeView для установки модели
    - central_widget — получить QWidget для установки в MainWindow
    """
    
    def __init__(self) -> None:
        log.info("Инициализация CentralWidget")
        """Инициализирует центральный виджет."""
        self._container = QWidget()
        self._setup_layout()
        
        log.system("CentralWidget инициализирован")
    
    def _setup_layout(self) -> None:
        """Настраивает layout и разделитель."""
        layout = QHBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель — TreeView
        self._tree_view = TreeView()
        log.success("TreeView создан")

        # Правая панель — DetailsPanel
        self._details_panel = DetailsPanel()
        log.success("DetailsPanel создан")

        self._splitter.addWidget(self._tree_view)
        self._splitter.addWidget(self._details_panel)
        self._splitter.setSizes([300, 700])  # 30% / 70% от 1024
        
        layout.addWidget(self._splitter)
        
        log.debug("CentralWidget: splitter настроен (TreeView слева, DetailsPanel справа)")
    
    def get_tree_view(self) -> TreeView:
        """
        Возвращает TreeView для установки модели.
        
        Returns:
            TreeView: Виджет дерева
        """
        return self._tree_view
    
    @property
    def central_widget(self) -> QWidget:
        """
        Возвращает QWidget для установки в MainWindow.
        
        Returns:
            QWidget: Контейнер центрального виджета
        """
        return self._container