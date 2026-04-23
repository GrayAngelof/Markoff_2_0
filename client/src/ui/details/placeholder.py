# client/src/ui/details/placeholder.py
"""
Виджет-заглушка для панели детальной информации.

Показывается, когда не выбран ни один объект.
"""

# ===== ИМПОРТЫ =====
from typing import Final, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class PlaceholderWidget(QWidget):
    """
    Виджет-заглушка, отображаемый при отсутствии выбранного объекта.

    На данном этапе — только текстовая заглушка.
    """

    # Локальная константа — текст заглушки по умолчанию
    _DEFAULT_MESSAGE: Final[str] = "Выберите объект в дереве слева"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует виджет-заглушку."""
        log.info("Инициализация PlaceholderWidget")
        super().__init__(parent)

        log.debug("PlaceholderWidget: создание структурного каркаса")

        self._setup_ui()

        log.debug("PlaceholderWidget: структурный каркас создан")
        log.system("PlaceholderWidget инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    @property
    def message_label(self) -> QLabel:
        """Возвращает виджет текстовой метки."""
        return self._message_label

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас заглушки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._message_label = QLabel(self._DEFAULT_MESSAGE)
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setWordWrap(True)

        layout.addWidget(self._message_label)

        log.debug("PlaceholderWidget: UI каркас создан")