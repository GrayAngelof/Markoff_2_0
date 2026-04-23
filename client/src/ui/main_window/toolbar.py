# client/src/ui/main_window/toolbar.py
"""
Панель инструментов приложения Markoff 2.0.

Содержит сплит-кнопку обновления с выпадающим меню (3 режима).
"""

# ===== ИМПОРТЫ =====
from typing import Final

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu, QToolButton, QToolBar

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class Toolbar(QToolBar):
    """
    Панель инструментов приложения.

    Сигналы:
        refresh_triggered(str) — выбран режим обновления ('current', 'visible', 'full')
    """

    refresh_triggered = Signal(str)

    # Локальные константы — тексты кнопок
    _BTN_REFRESH: Final[str] = "Обновить"
    _BTN_MODE_READ_ONLY: Final[str] = "Read Only"
    _BTN_MODE_EDIT: Final[str] = "Edit Mode"

    # Локальные константы — символы для кнопок
    _SYMBOL_REFRESH: Final[str] = "🔄"
    _SYMBOL_LOCK: Final[str] = "🔒"
    _SYMBOL_UNLOCK: Final[str] = "✏️"

    # Локальные константы — подсказки
    _TOOLTIP_REFRESH: Final[str] = "Обновить (нажмите для выбора режима)"
    _TOOLTIP_MODE: Final[str] = "Переключить режим редактирования"

    # Режимы обновления
    _REFRESH_CURRENT: Final[str] = "current"
    _REFRESH_VISIBLE: Final[str] = "visible"
    _REFRESH_FULL: Final[str] = "full"

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
        """Создаёт сплит-кнопку обновления с выпадающим меню."""
        # Создаём кнопку
        self._refresh_btn = QToolButton()
        self._refresh_btn.setText(f"{self._SYMBOL_REFRESH} {self._BTN_REFRESH}")
        self._refresh_btn.setToolTip(self._TOOLTIP_REFRESH)

        # Создаём меню
        menu = QMenu(self)

        # Пункт 1: Обновить выбранный узел
        action_current = menu.addAction("Обновить выбранный узел")
        action_current.triggered.connect(
            lambda: self.refresh_triggered.emit(self._REFRESH_CURRENT)
        )

        # Пункт 2: Обновить все раскрытые узлы
        action_visible = menu.addAction("Обновить все раскрытые узлы")
        action_visible.triggered.connect(
            lambda: self.refresh_triggered.emit(self._REFRESH_VISIBLE)
        )

        menu.addSeparator()

        # Пункт 3: Полное обновление (очистить кэш + свернуть всё)
        action_full = menu.addAction("Полное обновление")
        action_full.triggered.connect(
            lambda: self.refresh_triggered.emit(self._REFRESH_FULL)
        )

        # Прикрепляем меню к кнопке в режиме MenuButtonPopup
        # В этом режиме:
        # - Нажатие на стрелку → показывает меню
        # - Нажатие на основную часть кнопки → выполняет действие по умолчанию
        self._refresh_btn.setMenu(menu)
        self._refresh_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

        # Действие по умолчанию при клике на основную часть — обновить текущий узел
        self._refresh_btn.clicked.connect(
            lambda: self.refresh_triggered.emit(self._REFRESH_CURRENT)
        )

        self.addWidget(self._refresh_btn)
        self.addSeparator()

        log.info("Сплит-кнопка обновления добавлена (3 режима)")

    def _create_mode_button(self) -> None:
        """Создаёт кнопку переключения режима."""
        self._mode_btn = QToolButton()
        self._mode_btn.setText(f"{self._SYMBOL_LOCK} {self._BTN_MODE_READ_ONLY}")
        self._mode_btn.setToolTip(self._TOOLTIP_MODE)
        self._mode_btn.setCheckable(True)
        # TODO: добавить действие для переключения режима
        self.addWidget(self._mode_btn)

        log.info("Кнопка переключения режима добавлена")