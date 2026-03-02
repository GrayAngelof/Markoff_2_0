# client/src/ui/main_window.py
"""
Главное окно приложения Markoff
Содержит разделение на левую панель (дерево) и правую панель (информация)
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, 
    QSplitter, QToolBar, QStatusBar
)
from PySide6.QtCore import Qt, Slot, QSize  # Добавили QSize
from PySide6.QtGui import QAction

from src.ui.tree_view import TreeView
from src.ui.details_panel import DetailsPanel

class MainWindow(QMainWindow):
    """
    Главное окно приложения
    
    Компоновка:
    - Используем QSplitter для разделения на две части
    - Левая часть: дерево объектов (TreeView)
    - Правая часть: информационная панель (DetailsPanel)
    - Пользователь может изменять размер частей мышью
    
    Панель инструментов:
    - Кнопка "Обновить" для перезагрузки данных
    """
    
    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        
        # Настраиваем окно
        self.setWindowTitle("Markoff - Управление помещениями")
        self.setMinimumSize(900, 600)  # Минимальный размер окна
        
        # Создаём панель инструментов
        self._create_toolbar()
        
        # Создаём строку статуса
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Создаём центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаём горизонтальный layout для центрального виджета
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(2, 2, 2, 2)  # Небольшие отступы от краёв
        layout.setSpacing(0)
        
        # Создаём разделитель (QSplitter)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(5)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #c0c0c0;
            }
            QSplitter::handle:hover {
                background-color: #808080;
            }
        """)
        
        # Создаём левую панель с деревом
        self.tree_view = TreeView()
        
        # Создаём правую панель с информацией
        self.details_panel = DetailsPanel()
        
        # Добавляем виджеты в разделитель
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.details_panel)
        
        # Устанавливаем начальные размеры (30% - дерево, 70% - информация)
        splitter.setSizes([270, 630])  # 30% от 900
        
        # Добавляем разделитель в layout
        layout.addWidget(splitter)
        
        # Подключаем сигналы
        self.tree_view.item_selected.connect(self.details_panel.show_item_details)
        
        print("✅ Главное окно создано")
    
    def _create_toolbar(self):
        """Создаёт панель инструментов с кнопками"""
        toolbar = QToolBar("Панель инструментов")
        toolbar.setMovable(False)  # Запрещаем перемещение
        toolbar.setIconSize(QSize(16, 16))  # Исправлено: используем QSize вместо standardIcon
        self.addToolBar(toolbar)
        
        # Кнопка "Обновить"
        refresh_action = QAction("🔄 Обновить", self)
        refresh_action.setStatusTip("Обновить данные с сервера")
        refresh_action.triggered.connect(self._on_refresh)
        toolbar.addAction(refresh_action)
        
        # Разделитель
        toolbar.addSeparator()
        
        # Информация о статусе
        self.status_action = QAction("✅ Онлайн", self)
        self.status_action.setEnabled(False)
        toolbar.addAction(self.status_action)
    
    def _on_refresh(self):
        """Обработчик кнопки обновления"""
        print("🔄 Обновление по запросу пользователя")
        self.status_bar.showMessage("Обновление данных...")
        self.status_action.setText("🔄 Обновление...")
        
        # Вызываем обновление в дереве
        self.tree_view.refresh()
        
        self.status_bar.showMessage("Данные обновлены", 3000)
        self.status_action.setText("✅ Онлайн")
    
    @Slot(str, int)
    def on_item_selected(self, item_type: str, item_id: int):
        """
        Слот для обработки выбора элемента в дереве
        
        Args:
            item_type: тип элемента ('complex', 'building', etc.)
            item_id: идентификатор элемента
        """
        print(f"🎯 Выбран элемент в главном окне: {item_type} #{item_id}")
        self.status_bar.showMessage(f"Выбран: {item_type} #{item_id}")