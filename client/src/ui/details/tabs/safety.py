# client/src/ui/details/tabs/safety.py
"""
Вкладка пожарной безопасности панели детальной информации.

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
class SafetyTab(QWidget):
    """
    Вкладка пожарной безопасности (датчики, события).

    На данном этапе — только структурный каркас с заглушкой.
    """

    # Локальная константа — текст заглушки для вкладки пожарной безопасности
    _PLACEHOLDER_TEXT: Final[str] = "Данные пожарной безопасности будут здесь"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует вкладку пожарной безопасности."""
        log.info("Инициализация SafetyTab")
        super().__init__(parent)

        log.debug("SafetyTab: создание структурного каркаса")

        self._setup_ui()

        log.debug("SafetyTab: структурный каркас создан")
        log.system("SafetyTab инициализирован")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас вкладки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(self._PLACEHOLDER_TEXT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        log.debug("SafetyTab: UI каркас создан")