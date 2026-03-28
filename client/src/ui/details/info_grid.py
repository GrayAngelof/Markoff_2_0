# client/src/ui/details/info_grid.py
"""
Сетка с полями информации для панели деталей.

На данном этапе — пустой контейнер без полей.
"""

# ===== ИМПОРТЫ =====
from typing import Dict, Optional

from PySide6.QtWidgets import QGridLayout, QWidget

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class InfoGrid(QWidget):
    """
    Сетка для отображения информации в формате "Лейбл: Значение".

    На данном этапе — только структурный каркас без полей.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует сетку информации."""
        log.info("Инициализация InfoGrid")
        super().__init__(parent)

        log.debug("InfoGrid: создание структурного каркаса")

        self._setup_ui()

        log.debug("InfoGrid: структурный каркас создан")
        log.system("InfoGrid инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    @property
    def fields(self) -> Dict[str, QWidget]:
        """Возвращает словарь всех полей значений."""
        return self._value_widgets.copy()

    @property
    def labels(self) -> Dict[str, QWidget]:
        """Возвращает словарь всех лейблов."""
        return self._label_widgets.copy()

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас сетки."""
        self._grid = QGridLayout(self)
        self._grid.setVerticalSpacing(8)
        self._grid.setHorizontalSpacing(20)
        self._grid.setColumnStretch(1, 1)

        # Словари для будущих полей
        self._label_widgets: Dict[str, QWidget] = {}
        self._value_widgets: Dict[str, QWidget] = {}

        log.debug("InfoGrid: UI каркас создан")