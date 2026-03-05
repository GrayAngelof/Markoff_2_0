# client/src/ui/tree/base_tree.py
"""
Базовый класс для дерева объектов
Содержит общую инициализацию и базовые методы
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel, QProgressBar
from PySide6.QtCore import Qt, Slot

from src.ui.tree_model import TreeModel
from src.core.cache import DataCache


class TreeViewBase(QWidget):
    """
    Базовый класс для дерева объектов
    Содержит:
    - Инициализацию UI
    - Заголовок с индикатором загрузки
    - Модель дерева
    - Базовые настройки
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок с индикатором загрузки
        self._setup_header()
        
        # Создаём модель дерева
        self.model = TreeModel()
        
        # Создаём само дерево
        self.tree_view = QTreeView()
        self._setup_tree_view()
        
        layout.addWidget(self.tree_view)
    
    def _setup_header(self):
        """Создание заголовка с индикатором загрузки"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        self.title_label = QLabel("Объекты")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #c0c0c0;
            }
        """)
        
        # Индикатор загрузки
        self.loading_bar = QProgressBar()
        self.loading_bar.setMaximum(0)
        self.loading_bar.setMinimum(0)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        self.loading_bar.hide()
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.loading_bar)
        
        if self.layout():
            self.layout().addLayout(header_layout)
    
    def _setup_tree_view(self):
        """Настройка QTreeView"""
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setExpandsOnDoubleClick(True)
        
        # Устанавливаем модель
        self.tree_view.setModel(self.model)
        
        # Стили
        self.tree_view.setStyleSheet("""
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
        """)
    
    def set_cache(self, cache: DataCache):
        """Установить кэш для модели"""
        self.model.set_cache(cache)
    
    @Slot(bool)
    def show_loading(self, show: bool = True):
        """Показать/скрыть индикатор загрузки"""
        if show:
            self.loading_bar.show()
            self.title_label.setText("Объекты (загрузка...)")
        else:
            self.loading_bar.hide()
            self.title_label.setText("Объекты")
        
        self.loading_bar.repaint()
    
    def _show_error(self, title: str, message: str):
        """Показать сообщение об ошибке"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, title, message)