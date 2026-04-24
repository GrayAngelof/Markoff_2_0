# client/src/ui/details/header.py
"""
Шапка панели детальной информации.

Отображает:
- Тип узла + название (например, "КОМПЛЕКС: Фабрика Веретено")
- Статус узла (например, "Активен", если есть)
- Дополнительные динамические поля

TODO: Добавить иконку в зависимости от типа узла
TODO: Добавить цветовую индикацию статуса
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.view_models.details import DetailsViewModel
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class HeaderWidget(QWidget):
    """
    Шапка панели детальной информации.

    Динамическая сетка: строки добавляются через _add_row(),
    очищаются через _clear().
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализирует шапку."""
        log.system("HeaderWidget инициализация")
        super().__init__(parent)

        self._layout: Optional[QVBoxLayout] = None
        self._setup_ui()

        log.system("HeaderWidget инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def update_content(self, vm: DetailsViewModel) -> None:
        """Обновляет содержимое шапки на основе ViewModel."""
        log.debug(f"Обновление: {vm.header_title}")

        self._clear()

        title_text = f"{vm.header_subtitle}: {vm.header_title}"
        self._add_row(title_text, is_title=True)

        if vm.header_status_name:
            self._add_row(vm.header_status_name, is_status=True)

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _setup_ui(self) -> None:
        """Создаёт структурный каркас шапки."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 8, 10, 8)
        self._layout.setSpacing(5)

    def _add_row(self, text: str, is_title: bool = False, is_status: bool = False) -> None:
        """Добавляет строку в шапку."""
        if self._layout is None:
            log.error("Layout не инициализирован")
            return

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.PlainText)

        if is_title:
            font = label.font()
            font.setPointSize(14)
            font.setBold(True)
            label.setFont(font)
        elif is_status:
            font = label.font()
            font.setPointSize(12)
            label.setFont(font)
            # TODO: Добавить цвет статуса в зависимости от типа
            # label.setStyleSheet("color: green;")
        else:
            font = label.font()
            font.setPointSize(11)
            label.setFont(font)

        self._layout.addWidget(label)

    def _clear(self) -> None:
        """Очищает все строки из шапки."""
        if self._layout is None:
            return

        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()