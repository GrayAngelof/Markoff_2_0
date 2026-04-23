# client/src/ui/details/tabs/physics.py
"""
Вкладка физических параметров панели детальной информации.

На данном этапе — пустой контейнер с заглушкой.
"""

# ===== ИМПОРТЫ =====
from typing import Final, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class PhysicsTab(QWidget):
    """
    Вкладка физических параметров (статистика, метрики).

    На данном этапе — только структурный каркас с заглушкой.
    """

    # Локальная константа — текст заглушки для вкладки физических параметров
    _PLACEHOLDER_TEXT: Final[str] = "Статистика будет здесь"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует вкладку физических параметров."""
        log.info("Инициализация PhysicsTab")
        super().__init__(parent)

        log.debug("PhysicsTab: создание структурного каркаса")

        self._setup_ui()

        log.debug("PhysicsTab: структурный каркас создан")
        log.system("PhysicsTab инициализирован")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас вкладки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(self._PLACEHOLDER_TEXT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        log.debug("PhysicsTab: UI каркас создан")