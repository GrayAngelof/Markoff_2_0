# client/src/ui/main_window/window.py
"""
Главное окно приложения Markoff 2.0.

Пустая оболочка QMainWindow. Не знает, что внутри.
Центральный виджет, меню, тулбар и статус бар устанавливаются извне (AppWindow).
"""

# ===== ИМПОРТЫ =====
from typing import Final

from PySide6.QtWidgets import QMainWindow

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
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

    # Локальные константы — настройки окна
    _WINDOW_TITLE: Final[str] = "Markoff 2.0"
    _MIN_WIDTH: Final[int] = 1024
    _MIN_HEIGHT: Final[int] = 768
    _DEFAULT_WIDTH: Final[int] = 1024
    _DEFAULT_HEIGHT: Final[int] = 768

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        """Инициализирует главное окно."""
        log.info("Инициализация MainWindow")
        super().__init__()

        self.setWindowTitle(self._WINDOW_TITLE)
        self.setMinimumSize(self._MIN_WIDTH, self._MIN_HEIGHT)
        self.resize(self._DEFAULT_WIDTH, self._DEFAULT_HEIGHT)

        log.system("MainWindow инициализировано")