# client/src/ui/main_window/components/central_widget.py
"""
Модуль центрального виджета с разделителем.
Создаёт область для размещения дерева и панели деталей.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QMainWindow
from PySide6.QtCore import Qt
from typing import Optional

from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class CentralWidget:
    """
    Компонент центрального виджета с разделителем.
    
    Предоставляет:
    - Создание центрального виджета
    - Настройку разделителя (QSplitter)
    - Методы для добавления виджетов в разделитель
    """
    
    # ===== Константы =====
    _SPLITTER_HANDLE_WIDTH = 5
    """Ширина разделителя в пикселях"""
    
    _SPLITTER_STYLE = """
        QSplitter::handle {
            background-color: #c0c0c0;
        }
        QSplitter::handle:hover {
            background-color: #808080;
        }
    """
    """Стили для разделителя"""
    
    _DEFAULT_SIZES = [300, 700]
    """Начальные размеры частей разделителя [левая, правая]"""
    
    def __init__(self, parent: QMainWindow) -> None:
        """
        Инициализирует центральный виджет.
        
        Args:
            parent: Родительское окно (MainWindow)
        """
        self._parent = parent
        self._central_widget: Optional[QWidget] = None
        self._splitter: Optional[QSplitter] = None
        
        self._create_central_widget()
        
        log.debug("CentralWidget: инициализирован")
    
    # ===== Приватные методы =====
    
    def _create_central_widget(self) -> None:
        """Создаёт и настраивает центральный виджет."""
        # Создаём центральный виджет
        self._central_widget = QWidget(self._parent)
        self._central_widget.setVisible(True)
        # ИСПРАВЛЕНО: setCentralWidget вызывается у QMainWindow, а не у QWidget
        self._parent.setCentralWidget(self._central_widget)
        
        # Создаём layout
        layout = QHBoxLayout(self._central_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Создаём разделитель
        self._create_splitter()
        if self._splitter:
            layout.addWidget(self._splitter)
        
        log.debug("CentralWidget: центральный виджет создан")
    
    def _create_splitter(self) -> None:
        """Создаёт и настраивает разделитель."""
        # ИСПРАВЛЕНО: используем правильную константу Qt
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(self._SPLITTER_HANDLE_WIDTH)
        self._splitter.setVisible(True)
        self._splitter.setStyleSheet(self._SPLITTER_STYLE)
        
        log.debug("CentralWidget: разделитель создан")
    
    # ===== Геттеры =====
    
    @property
    def central_widget(self) -> QWidget:
        """
        Возвращает центральный виджет.
        
        Returns:
            QWidget: Центральный виджет
        
        Raises:
            ValueError: Если центральный виджет не инициализирован
        """
        if self._central_widget is None:
            raise ValueError("Central widget не инициализирован")
        return self._central_widget
    
    @property
    def splitter(self) -> QSplitter:
        """
        Возвращает разделитель.
        
        Returns:
            QSplitter: Разделитель
        
        Raises:
            ValueError: Если разделитель не инициализирован
        """
        if self._splitter is None:
            raise ValueError("Splitter не инициализирован")
        return self._splitter
    
    # ===== Публичные методы =====
    
    def add_widgets(self, left_widget: QWidget, right_widget: QWidget) -> None:
        """
        Добавляет виджеты в разделитель.
        
        Args:
            left_widget: Левый виджет (дерево)
            right_widget: Правый виджет (панель деталей)
        
        Raises:
            ValueError: Если разделитель не инициализирован
        """
        if self._splitter is None:
            raise ValueError("Невозможно добавить виджеты: разделитель не инициализирован")
        
        self._splitter.addWidget(left_widget)
        self._splitter.addWidget(right_widget)
        self._splitter.setSizes(self._DEFAULT_SIZES)
        
        log.debug(f"CentralWidget: виджеты добавлены в разделитель")
        log.debug(f"  splitter содержит {self._splitter.count()} виджетов")
    
    def is_visible(self) -> bool:
        """
        Проверяет видимость центрального виджета и разделителя.
        
        Returns:
            bool: True если все компоненты видимы
        """
        return (
            self._central_widget is not None and
            self._splitter is not None and
            self._central_widget.isVisible() and
            self._splitter.isVisible()
        )