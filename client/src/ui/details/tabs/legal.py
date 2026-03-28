# client/src/ui/details/tabs/legal.py
"""
Вкладка юридических лиц панели детальной информации.

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
class LegalTab(QWidget):
    """
    Вкладка юридических лиц (контрагенты, владельцы, контакты).

    На данном этапе — только структурный каркас с заглушкой.
    """

    # Локальная константа — текст заглушки для вкладки юридических лиц
    _PLACEHOLDER_TEXT: Final[str] = "Информация о юридических лицах будет здесь"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует вкладку юридических лиц."""
        log.info("Инициализация LegalTab")
        super().__init__(parent)

        log.debug("LegalTab: создание структурного каркаса")

        self._setup_ui()

        log.debug("LegalTab: структурный каркас создан")
        log.system("LegalTab инициализирован")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас вкладки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(self._PLACEHOLDER_TEXT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        log.debug("LegalTab: UI каркас создан")