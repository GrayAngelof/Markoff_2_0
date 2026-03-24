# client/src/ui/common/central_widget.py
"""
Центральный виджет с разделителем 30/70.
Позволяет подменять левую и правую панели.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QLabel
from PySide6.QtCore import Qt

from utils.logger import get_logger

log = get_logger(__name__)


class CentralWidget:
    """
    Центральный виджет с разделителем.
    
    Создает QSplitter с заглушками и предоставляет методы
    для подмены левой и правой панелей.
    
    Методы:
    - set_left(widget) — заменить левую панель
    - set_right(widget) — заменить правую панель
    - central_widget — получить QWidget для установки в MainWindow
    """
    
    def __init__(self):
        self._container = QWidget()
        self._setup_layout()
        
        log.debug("CentralWidget создан")
    
    def _setup_layout(self) -> None:
        """Настраивает layout и разделитель."""
        layout = QHBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Создаем заглушки
        self._left = self._create_placeholder("🌳 ДЕРЕВО ОБЪЕКТОВ\n\n(будет здесь)")
        self._right = self._create_placeholder(
            "🔍 ВЫБЕРИТЕ ОБЪЕКТ\n\nдля отображения информации"
        )
        
        self._splitter.addWidget(self._left)
        self._splitter.addWidget(self._right)
        self._splitter.setSizes([300, 700])  # 30% / 70% от 1024
        
        layout.addWidget(self._splitter)
    
    def _create_placeholder(self, text: str) -> QWidget:
        """Создает виджет-заглушку."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #999999;
            font-size: 14px;
            padding: 20px;
            border: 1px dashed #cccccc;
            border-radius: 8px;
        """)
        
        layout.addWidget(label)
        return widget
    
    def set_left(self, widget: QWidget) -> None:
        """Заменяет левую панель."""
        # Удаляем старый виджет
        old_widget = self._splitter.widget(0)
        if old_widget:
            old_widget.deleteLater()
        
        # Вставляем новый
        self._splitter.insertWidget(0, widget)
        self._splitter.setSizes([300, 700])
        log.debug("Левая панель заменена")
    
    def set_right(self, widget: QWidget) -> None:
        """Заменяет правую панель."""
        old_widget = self._splitter.widget(1)
        if old_widget:
            old_widget.deleteLater()
        
        self._splitter.insertWidget(1, widget)
        self._splitter.setSizes([300, 700])
        log.debug("Правая панель заменена")
    
    @property
    def central_widget(self) -> QWidget:
        """Возвращает QWidget для установки в MainWindow."""
        return self._container