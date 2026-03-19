# client/src/ui/tree/base_tree.py
"""
Базовый класс для дерева объектов.
Предоставляет общую инициализацию пользовательского интерфейса,
заголовок с индикатором загрузки и базовые настройки QTreeView.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel, QProgressBar, QMessageBox
from PySide6.QtCore import Qt, Slot
from typing import Optional

from src.ui.tree_model import TreeModel

from utils.logger import get_logger
log = get_logger(__name__)


class TreeViewBase(QWidget):
    """
    Базовый класс для виджета дерева объектов.
    
    В новой архитектуре модель получает данные через проекцию,
    поэтому методы set_cache и reset_model больше не нужны.
    
    Предоставляет:
    - Инициализацию пользовательского интерфейса
    - Заголовок с индикатором загрузки
    - Модель данных TreeModel
    - Базовые настройки QTreeView
    - Методы для управления индикатором загрузки
    """
    
    # ===== Константы UI =====
    _DEFAULT_TITLE = "Объекты"
    """Заголовок по умолчанию"""
    
    _LOADING_TITLE = "Объекты (загрузка...)"
    """Заголовок во время загрузки"""
    
    _HEADER_STYLESHEET = """
        QLabel {
            background-color: #f0f0f0;
            padding: 8px;
            font-weight: bold;
            font-size: 14px;
            border-bottom: 1px solid #c0c0c0;
        }
    """
    """Стили для заголовка"""
    
    _PROGRESS_BAR_STYLESHEET = """
        QProgressBar {
            border: none;
            background-color: #f0f0f0;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
        }
    """
    """Стили для индикатора загрузки"""
    
    _TREE_VIEW_STYLESHEET = """
        QTreeView {
            background-color: white;
            border: none;
            outline: none;
        }
        QTreeView::item {
            padding: 4px;
            border-bottom: 1px solid #f0f0f0;
        }
        QTreeView::item:selected {
            background-color: #e3f2fd;
            color: black;
        }
        QTreeView::item:hover {
            background-color: #f5f5f5;
        }
    """
    """Стили для дерева"""
    
    # ===== Константы размеров =====
    _PROGRESS_BAR_HEIGHT = 3
    """Высота индикатора загрузки в пикселях"""
    
    _TREE_INDENTATION = 20
    """Отступ для дочерних элементов в пикселях"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует базовый виджет дерева.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Инициализация UI
        self._init_ui()
        
        log.debug("TreeViewBase: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_ui(self) -> None:
        """
        Инициализирует пользовательский интерфейс.
        Создаёт layout, заголовок, модель и представление.
        """
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок с индикатором загрузки
        self._setup_header(layout)
        
        # Создаём модель дерева (проекция будет установлена позже через set_projection)
        self._model = TreeModel()
        
        # Создаём представление
        self._setup_tree_view()
        
        # Добавляем представление в layout
        layout.addWidget(self._tree_view)
        
        log.debug("TreeViewBase: UI инициализирован")
    
    def _setup_header(self, parent_layout: QVBoxLayout) -> None:
        """
        Создаёт заголовок с индикатором загрузки.
        
        Args:
            parent_layout: Родительский layout для добавления заголовка
        """
        # Создаём отдельный виджет для заголовка
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(2)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок
        self._title_label = QLabel(self._DEFAULT_TITLE)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet(self._HEADER_STYLESHEET)
        
        # Индикатор загрузки
        self._loading_bar = QProgressBar()
        self._loading_bar.setMaximum(0)
        self._loading_bar.setMinimum(0)
        self._loading_bar.setTextVisible(False)
        self._loading_bar.setFixedHeight(self._PROGRESS_BAR_HEIGHT)
        self._loading_bar.setStyleSheet(self._PROGRESS_BAR_STYLESHEET)
        self._loading_bar.hide()
        
        header_layout.addWidget(self._title_label)
        header_layout.addWidget(self._loading_bar)
        
        # Добавляем виджет заголовка в родительский layout
        parent_layout.addWidget(header_widget)
    
    def _setup_tree_view(self) -> None:
        """
        Настраивает QTreeView: внешний вид, поведение и модель.
        """
        self._tree_view = QTreeView()
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setAlternatingRowColors(True)
        self._tree_view.setAnimated(True)
        self._tree_view.setIndentation(self._TREE_INDENTATION)
        self._tree_view.setExpandsOnDoubleClick(True)
        
        # Устанавливаем модель
        self._tree_view.setModel(self._model)
        
        # Применяем стили
        self._tree_view.setStyleSheet(self._TREE_VIEW_STYLESHEET)
        
        log.debug("TreeViewBase: QTreeView настроен")
    
    # ===== Геттеры =====
    
    @property
    def model(self) -> TreeModel:
        """
        Возвращает модель данных дерева.
        
        Returns:
            TreeModel: модель данных
        """
        return self._model
    
    @property
    def tree_view(self) -> QTreeView:
        """
        Возвращает виджет дерева.
        
        Returns:
            QTreeView: виджет для отображения дерева
        """
        return self._tree_view
    
    @property
    def title_label(self) -> QLabel:
        """
        Возвращает виджет заголовка.
        
        Returns:
            QLabel: виджет с заголовком
        """
        return self._title_label
    
    @property
    def loading_bar(self) -> QProgressBar:
        """
        Возвращает индикатор загрузки.
        
        Returns:
            QProgressBar: индикатор загрузки
        """
        return self._loading_bar
    
    # ===== Публичные методы =====
    
    def set_projection(self, projection) -> None:
        """
        Устанавливает проекцию для модели.
        
        Args:
            projection: Проекция дерева
        """
        # В новой архитектуре модель создаётся с проекцией в конструкторе
        # Этот метод нужен, если проекция устанавливается после создания модели
        log.debug("TreeViewBase: установка проекции для модели")
        # TODO: реализовать если нужно
    
    @Slot(bool)
    def show_loading(self, show: bool = True) -> None:
        """
        Управляет отображением индикатора загрузки.
        
        Args:
            show: True - показать индикатор, False - скрыть
        """
        if show:
            self._loading_bar.show()
            self._title_label.setText(self._LOADING_TITLE)
            log.debug("TreeViewBase: индикатор загрузки показан")
        else:
            self._loading_bar.hide()
            self._title_label.setText(self._DEFAULT_TITLE)
            log.debug("TreeViewBase: индикатор загрузки скрыт")
        
        # Принудительно обновляем отображение
        self._loading_bar.repaint()
    
    def update_title_count(self, count: int) -> None:
        """
        Обновляет заголовок с указанием количества элементов.
        
        Args:
            count: Количество элементов для отображения
        """
        self._title_label.setText(f"{self._DEFAULT_TITLE} ({count})")
        log.debug(f"TreeViewBase: заголовок обновлён, элементов: {count}")
    
    def _show_error(self, title: str, message: str) -> None:
        """
        Показывает диалоговое окно с ошибкой.
        
        Args:
            title: Заголовок окна
            message: Сообщение об ошибке
        """
        QMessageBox.warning(self, title, message)
        log.warning(f"Показано сообщение об ошибке: {title} - {message}")