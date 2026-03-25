# client/src/ui/main_window/menu.py
"""
Главное меню приложения Markoff 2.0.
Только визуальная структура, без событий.
"""

from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction

from utils.logger import get_logger

log = get_logger(__name__)


class MenuBar(QMenuBar):
    """
    Главное меню приложения.
    Только визуальная структура. События будут добавлены позже.
    """
    
    def __init__(self):
        super().__init__()
        
        self._create_file_menu()
        self._create_reference_menu()
        self._create_help_menu()
        
        # DEBUG - отладочная информация о создании визуального компонента
        log.debug("MenuBar создан")
    
    def _create_file_menu(self) -> None:
        """Создает меню 'Файл'."""
        file_menu = self.addMenu("&Файл")
        
        exit_action = QAction("&Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        # TODO: добавить действие при выходе
        file_menu.addAction(exit_action)
        
        log.debug("Меню 'Файл' создано")
    
    def _create_reference_menu(self) -> None:
        """Создает меню 'Справочники'."""
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
        
        log.debug(f"Меню 'Справочники' создано, пунктов: {len(references)}")
    
    def _create_help_menu(self) -> None:
        """Создает меню 'Помощь'."""
        help_menu = self.addMenu("&Помощь")
        
        about_action = QAction("&О программе", self)
        # TODO: добавить действие "О программе"
        help_menu.addAction(about_action)
        
        log.debug("Меню 'Помощь' создано")