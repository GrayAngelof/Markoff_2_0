# client/src/ui/main_window/toolbar.py
"""
Панель инструментов приложения Markoff 2.0.
Только визуальные кнопки, без событий.
"""

from PySide6.QtWidgets import QToolBar, QPushButton

from utils.logger import get_logger

log = get_logger(__name__)


class Toolbar(QToolBar):
    """
    Панель инструментов приложения.
    Только визуальные кнопки. События будут добавлены позже.
    """
    
    def __init__(self):
        super().__init__("Панель инструментов")
        
        self._create_refresh_button()
        self._create_mode_button()
        
        log.debug("Toolbar создан (только визуал)")
    
    def _create_refresh_button(self) -> None:
        """Создает кнопку обновления."""
        self._refresh_btn = QPushButton("🔄 Обновить")
        self._refresh_btn.setToolTip("Обновить текущий узел (F5)")
        # TODO: добавить действие для обновления
        self.addWidget(self._refresh_btn)
        self.addSeparator()
    
    def _create_mode_button(self) -> None:
        """Создает кнопку переключения режима."""
        self._mode_btn = QPushButton("🔒 Read Only")
        self._mode_btn.setToolTip("Переключить режим редактирования")
        self._mode_btn.setCheckable(True)
        # TODO: добавить действие для переключения режима
        self.addWidget(self._mode_btn)