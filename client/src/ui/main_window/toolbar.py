# client/src/ui/main_window/toolbar.py
"""
Панель инструментов приложения Markoff 2.0.

Только визуальные кнопки, без событий.
События будут добавлены позже через подключение к EventBus.
"""

# ===== ИМПОРТЫ =====
from typing import Final

from PySide6.QtWidgets import QPushButton, QToolBar

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class Toolbar(QToolBar):
    """
    Панель инструментов приложения.

    Только визуальные кнопки. События будут добавлены позже.
    """

    # Локальные константы — тексты кнопок
    _BTN_REFRESH: Final[str] = "Обновить"
    _BTN_MODE_READ_ONLY: Final[str] = "Read Only"
    _BTN_MODE_EDIT: Final[str] = "Edit Mode"

    # Локальные константы — символы для кнопок
    _SYMBOL_REFRESH: Final[str] = "🔄"
    _SYMBOL_LOCK: Final[str] = "🔒"
    _SYMBOL_UNLOCK: Final[str] = "✏️"

    # Локальные константы — подсказки
    _TOOLTIP_REFRESH: Final[str] = "Обновить текущий узел (F5)"
    _TOOLTIP_MODE: Final[str] = "Переключить режим редактирования"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        """Инициализирует панель инструментов."""
        log.info("Инициализация Toolbar")
        super().__init__("Панель инструментов")

        self._create_refresh_button()
        self._create_mode_button()

        log.system("Toolbar инициализирован")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _create_refresh_button(self) -> None:
        """Создаёт кнопку обновления."""
        self._refresh_btn = QPushButton(f"{self._SYMBOL_REFRESH} {self._BTN_REFRESH}")
        self._refresh_btn.setToolTip(self._TOOLTIP_REFRESH)
        # TODO: добавить действие для обновления
        self.addWidget(self._refresh_btn)
        self.addSeparator()

        log.info("Кнопка обновления добавлена")

    def _create_mode_button(self) -> None:
        """Создаёт кнопку переключения режима."""
        self._mode_btn = QPushButton(f"{self._SYMBOL_LOCK} {self._BTN_MODE_READ_ONLY}")
        self._mode_btn.setToolTip(self._TOOLTIP_MODE)
        self._mode_btn.setCheckable(True)
        # TODO: добавить действие для переключения режима
        self.addWidget(self._mode_btn)

        log.info("Кнопка переключения режима добавлена")