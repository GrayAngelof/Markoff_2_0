# client/src/ui/common/central_widget.py
"""
Центральный виджет с разделителем 30/70.
Левая панель — TreeView (создается сразу), правая — заглушка.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QLabel
from PySide6.QtCore import Qt

from src.ui.tree.view import TreeView

from utils.logger import get_logger

log = get_logger(__name__)


class CentralWidget:
    """
    Центральный виджет с разделителем.
    
    Левая панель — TreeView (создается сразу)
    Правая панель — заглушка (будет заменена позже)
    
    Методы:
    - set_right(widget) — заменить правую панель
    - get_tree_view() — получить TreeView для установки модели
    - central_widget — получить QWidget для установки в MainWindow
    """
    
    def __init__(self):
        log.system("CentralWidget инициализирован")
        
        self._container = QWidget()
        self._setup_layout()
    
    def _setup_layout(self) -> None:
        """Настраивает layout и разделитель."""
        layout = QHBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель — сразу TreeView
        self._tree_view = TreeView()
        self._tree_view.setStyleSheet("""
            QTreeView {
                background-color: #f5f5f5;
                alternate-background-color: #e8e8e8;
                border: none;
                outline: none;
            }
            QTreeView::item {
                padding: 4px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTreeView::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QTreeView::item:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # Правая панель — заглушка с инструкцией
        self._right = self._create_placeholder(
            "ВЫБЕРИТЕ ОБЪЕКТ\n\nдля отображения информации"
        )
        
        self._splitter.addWidget(self._tree_view)
        self._splitter.addWidget(self._right)
        self._splitter.setSizes([300, 700])  # 30% / 70% от 1024
        
        layout.addWidget(self._splitter)
        
        log.debug(f"Splitter настроен: левая панель TreeView, правая заглушка")
    
    def _create_placeholder(self, text: str) -> QWidget:
        """Создает виджет-заглушку."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #999999;
            font-size: 16px;
            font-weight: bold;
            padding: 40px;
            border: 2px dashed #cccccc;
            border-radius: 12px;
            background-color: #fafafa;
        """)
        
        layout.addWidget(label)
        
        log.debug(f"Создана заглушка: {text[:30]}...")
        return widget
    
    def set_right(self, widget: QWidget) -> None:
        """Заменяет правую панель."""
        old_widget = self._splitter.widget(1)
        if old_widget:
            old_widget.deleteLater()
        
        self._splitter.insertWidget(1, widget)
        self._splitter.setSizes([300, 700])
        
        log.info("Правая панель заменена")
        log.debug(f"Новый виджет: {widget.__class__.__name__}")
    
    def get_tree_view(self) -> TreeView:
        """Возвращает TreeView для установки модели."""
        return self._tree_view
    
    @property
    def central_widget(self) -> QWidget:
        """Возвращает QWidget для установки в MainWindow."""
        return self._container