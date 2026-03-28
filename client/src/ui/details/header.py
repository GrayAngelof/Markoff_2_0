# client/src/ui/details/header.py
"""
Шапка панели детальной информации.

На данном этапе — пустой контейнер без логики.
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class HeaderWidget(QWidget):
    """
    Шапка панели детальной информации.

    На данном этапе — только структурный каркас с пустыми метками-заглушками.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует шапку."""
        log.info("Инициализация HeaderWidget")
        super().__init__(parent)

        log.debug("HeaderWidget: создание структурного каркаса")

        self._setup_ui()

        log.debug("HeaderWidget: структурный каркас создан")
        log.system("HeaderWidget инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    @property
    def icon_label(self) -> QLabel:
        """Возвращает виджет иконки."""
        return self._icon_label

    @property
    def title_label(self) -> QLabel:
        """Возвращает виджет заголовка."""
        return self._title_label

    @property
    def status_label(self) -> QLabel:
        """Возвращает виджет статуса."""
        return self._status_label

    @property
    def hierarchy_label(self) -> QLabel:
        """Возвращает виджет иерархии."""
        return self._hierarchy_label

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас шапки."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Верхняя строка: иконка и заголовок
        self._top_row = QWidget()
        top_layout = QVBoxLayout(self._top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self._icon_label = QLabel("")
        top_layout.addWidget(self._icon_label)

        self._title_label = QLabel("")
        self._title_label.setWordWrap(True)
        top_layout.addWidget(self._title_label)

        self._status_label = QLabel("")
        top_layout.addWidget(self._status_label)

        layout.addWidget(self._top_row)

        # Нижняя строка: иерархия
        self._hierarchy_label = QLabel("")
        self._hierarchy_label.setWordWrap(True)
        layout.addWidget(self._hierarchy_label)

        log.debug("HeaderWidget: UI каркас создан")