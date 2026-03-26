# client/src/ui/main_window/window.py
"""
Главное окно приложения Markoff 2.0.
Пустая оболочка QMainWindow. Не знает, что внутри.
"""

from PySide6.QtWidgets import QMainWindow

from utils.logger import get_logger

log = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Пустая оболочка главного окна.
    
    Отвечает только за:
    - Настройку заголовка
    - Настройку размеров
    - Предоставление места для UI фасада
    
    НЕ знает:
    - Какие компоненты будут добавлены
    - Как устроено меню, тулбар, статус бар
    - Что находится в центральной области
    """
    
    def __init__(self):
        super().__init__()
        
        # Базовые настройки окна
        self.setWindowTitle("Markoff 2.0")
        self.setMinimumSize(1024, 768)
        self.resize(1024, 768)
        
        log.system("Главное окно инициализировано")