# client/src/ui/details/tabs/safety.py
"""
Вкладка пожарной безопасности панели детальной информации.
На данном этапе — пустой контейнер.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


class SafetyTab(QWidget):
    """
    Вкладка пожарной безопасности (датчики, события).
    
    На данном этапе:
    - Только структурный каркас
    - Содержит текстовую заглушку
    """
    
    # Сообщение-заглушка
    _PLACEHOLDER_TEXT = "🔥 Данные пожарной безопасности будут здесь"
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует вкладку пожарной безопасности.
        
        Args:
            parent: Родительский виджет
        """
        log.info("Инициализация SafetyTab")
        super().__init__(parent)
        
        log.debug("SafetyTab: создание структурного каркаса")
        
        self._setup_ui()
        
        log.debug("SafetyTab: структурный каркас создан")
        log.system("SafetyTab инициализирован")

    def _setup_ui(self) -> None:
        """Создает структурный каркас вкладки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(self._PLACEHOLDER_TEXT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(label)
        
        log.debug("SafetyTab: UI каркас создан")