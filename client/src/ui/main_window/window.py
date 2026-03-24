"""
Главное окно приложения.
Минимальная версия для тестирования инициализации.
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QLabel
from PySide6.QtCore import Qt

from utils.logger import get_logger

log = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Главное окно приложения Markoff 2.0.
    
    Отвечает за:
    - Настройку окна (размеры, заголовок)
    - Компоновку (30% дерево / 70% детали)
    - Создание базовых виджетов-заглушек
    """
    
    def __init__(self):
        super().__init__()
        
        log.info("Инициализация MainWindow")
        
        # Настройка окна
        self.setWindowTitle("Markoff 2.0")
        self.setMinimumSize(1024, 768)
        self.resize(1024, 768)
        
        # Создаём центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Разделитель 30/70
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель (заглушка дерева)
        left_panel = self._create_left_panel()
        
        # Правая панель (заглушка деталей)
        right_panel = self._create_right_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([int(1024 * 0.3), int(1024 * 0.7)])
        
        layout.addWidget(splitter)
        
        log.success("MainWindow инициализировано")
    
    def _create_left_panel(self) -> QWidget:
        """Создаёт левую панель с заглушкой дерева."""
        panel = QWidget()
        panel.setStyleSheet("background-color: #f5f5f5;")
        
        layout = QHBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("🌳 ДЕРЕВО ОБЪЕКТОВ\n\n(будет здесь)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            color: #999999;
            font-size: 14px;
            padding: 20px;
            border: 1px dashed #cccccc;
            border-radius: 8px;
        """)
        
        layout.addWidget(label)
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Создаёт правую панель с заглушкой деталей."""
        panel = QWidget()
        panel.setStyleSheet("background-color: white;")
        
        layout = QHBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("🔍 ВЫБЕРИТЕ ОБЪЕКТ\n\nдля отображения информации")
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
        return panel