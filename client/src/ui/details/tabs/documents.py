# client/src/ui/details/tabs/documents.py
"""
Вкладка документов панели детальной информации.

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
class DocumentsTab(QWidget):
    """
    Вкладка документов (список связанных документов).

    На данном этапе — только структурный каркас с заглушкой.
    """

    # Локальная константа — текст заглушки для вкладки документов
    _PLACEHOLDER_TEXT: Final[str] = "Список документов будет здесь"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует вкладку документов."""
        log.info("Инициализация DocumentsTab")
        super().__init__(parent)

        log.debug("DocumentsTab: создание структурного каркаса")

        self._setup_ui()

        log.debug("DocumentsTab: структурный каркас создан")
        log.system("DocumentsTab инициализирован")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас вкладки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(self._PLACEHOLDER_TEXT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)

        log.debug("DocumentsTab: UI каркас создан")