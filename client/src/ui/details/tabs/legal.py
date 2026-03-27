# client/src/ui/details/tabs/legal.py
"""
Вкладка юриков панели детальной информации.
На данном этапе — пустой контейнер.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


class LegalTab(QWidget):
    """
    Вкладка юриков (контрагенты, владельцы, контакты).
    
    На данном этапе:
    - Только структурный каркас
    - Содержит текстовую заглушку
    """
    
    # Сообщение-заглушка
    _PLACEHOLDER_TEXT = "⚖️ Информация о юридических лицах будет здесь"
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует вкладку юриков.
        
        Args:
            parent: Родительский виджет
        """
        log.info("Инициализация LegalTab")
        super().__init__(parent)
        
        log.debug("LegalTab: создание структурного каркаса")
        
        self._setup_ui()
        
        log.debug("LegalTab: структурный каркас создан")
        log.system("LegalTab инициализирован")

    def _setup_ui(self) -> None:
        """Создает структурный каркас вкладки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(self._PLACEHOLDER_TEXT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(label)
        
        log.debug("LegalTab: UI каркас создан")