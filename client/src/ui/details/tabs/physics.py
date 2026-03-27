# client/src/ui/details/tabs/physics.py
"""
Вкладка физики панели детальной информации.
На данном этапе — пустой контейнер.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


class PhysicsTab(QWidget):
    """
    Вкладка физики (статистика, метрики).
    
    На данном этапе:
    - Только структурный каркас
    - Содержит текстовую заглушку
    """
    
    # Сообщение-заглушка
    _PLACEHOLDER_TEXT = "📊 Статистика будет здесь"
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует вкладку физики.
        
        Args:
            parent: Родительский виджет
        """
        log.info("Инициализация PhysicsTab")
        super().__init__(parent)
        
        log.debug("PhysicsTab: создание структурного каркаса")
        
        self._setup_ui()
        
        log.debug("PhysicsTab: структурный каркас создан")
        log.system("PhysicsTab инициализирован")

    def _setup_ui(self) -> None:
        """Создает структурный каркас вкладки."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(self._PLACEHOLDER_TEXT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(label)
        
        log.debug("PhysicsTab: UI каркас создан")