# client/src/ui/main_window/menu.py
"""
Главное меню приложения Markoff 2.0.

Только визуальная структура, без событий.
События будут добавлены позже через подключение к EventBus.
"""

# ===== ИМПОРТЫ =====
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMenuBar

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class MenuBar(QMenuBar):
    """
    Главное меню приложения.

    Только визуальная структура. События будут добавлены позже.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        """Инициализирует главное меню."""
        log.info("Инициализация MenuBar")
        super().__init__()

        self._create_file_menu()
        self._create_reference_menu()
        self._create_help_menu()

        log.system("MenuBar инициализирован")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _create_file_menu(self) -> None:
        """Создаёт меню 'Файл'."""
        file_menu = self.addMenu("&Файл")

        exit_action = QAction("&Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        # TODO: добавить действие при выходе
        file_menu.addAction(exit_action)

        log.info("Меню 'Файл' добавлено")

    def _create_reference_menu(self) -> None:
        """Создаёт меню 'Справочники'."""
        ref_menu = self.addMenu("&Справочники")

        references = [
            "Типы помещений",
            "Статусы помещений",
            "Типы контрагентов",
            "Роли ответственных лиц",
            "Категории контактов",
        ]

        for ref_name in references:
            action = QAction(ref_name, self)
            # TODO: добавить действия для справочников
            ref_menu.addAction(action)

        log.info(f"Меню 'Справочники' добавлено, пунктов: {len(references)}")

    def _create_help_menu(self) -> None:
        """Создаёт меню 'Помощь'."""
        help_menu = self.addMenu("&Помощь")

        about_action = QAction("&О программе", self)
        # TODO: добавить действие "О программе"
        help_menu.addAction(about_action)

        log.info("Меню 'Помощь' добавлено")