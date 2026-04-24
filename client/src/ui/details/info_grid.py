# client/src/ui/details/info_grid.py
"""
Сетка с полями информации для панели деталей.

Отображает данные в формате "Лейбл: Значение" в виде сетки из двух колонок.
Поддерживает динамическое добавление/очистку строк.

TODO: Добавить поддержку ссылок (URL план этажа) — кликабельные значения
TODO: Добавить поддержку многострочных значений (сейчас QLabel с WordWrap)
TODO: Добавить форматирование специальных типов (площадь, даты, ID владельца)
"""

# ===== ИМПОРТЫ =====
from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from src.view_models.details import DetailsViewModel
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class InfoGrid(QWidget):
    """
    Сетка для отображения информации в формате "Лейбл: Значение".

    Динамически создаёт строки на основе vm.grid_items.
    Каждая строка содержит:
    - Лейбл (жирный шрифт, выровнен вправо)
    - Значение (обычный шрифт, выровнен влево)
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует сетку информации."""
        log.system("InfoGrid инициализация")
        super().__init__(parent)

        self._setup_ui()
        self._clear_grid()

        log.system("InfoGrid инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def update_content(self, vm: DetailsViewModel) -> None:
        """Обновляет сетку на основе ViewModel."""
        log.debug(f"Обновление: {len(vm.grid)} записей")

        self._clear_grid()

        for row, item in enumerate(vm.grid):
            self._add_row(row, item.label, item.value)

    def clear(self) -> None:
        """Очищает сетку (удаляет все строки)."""
        self._clear_grid()
        log.debug("Сетка очищена")

    @property
    def row_count(self) -> int:
        """Возвращает количество строк в сетке."""
        return len(self._label_widgets)

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас сетки."""
        self._grid = QGridLayout(self)
        self._grid.setVerticalSpacing(8)
        self._grid.setHorizontalSpacing(20)
        self._grid.setColumnStretch(1, 1)

        self._label_widgets: Dict[int, QLabel] = {}
        self._value_widgets: Dict[int, QLabel] = {}

        self._label_style = """
            QLabel {
                font-weight: bold;
                color: #555;
            }
        """

        self._value_style = """
            QLabel {
                color: #333;
            }
        """

    def _clear_grid(self) -> None:
        """Удаляет все строки из сетки."""
        for label in self._label_widgets.values():
            self._grid.removeWidget(label)
            label.deleteLater()

        for value in self._value_widgets.values():
            self._grid.removeWidget(value)
            value.deleteLater()

        self._label_widgets.clear()
        self._value_widgets.clear()

    def _add_row(self, row: int, label: str, value: str) -> None:
        """Добавляет одну строку в сетку."""
        label_widget = QLabel(label)
        label_widget.setStyleSheet(self._label_style)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label_widget.setWordWrap(True)

        value_widget = QLabel(value)
        value_widget.setStyleSheet(self._value_style)
        value_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value_widget.setWordWrap(True)

        self._grid.addWidget(label_widget, row, 0)
        self._grid.addWidget(value_widget, row, 1)

        self._label_widgets[row] = label_widget
        self._value_widgets[row] = value_widget