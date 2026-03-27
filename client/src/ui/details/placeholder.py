# client/src/ui/details/placeholder.py
"""
Виджет-заглушка для панели детальной информации.
Показывается, когда не выбран ни один объект.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


class PlaceholderWidget(QWidget):
    """
    Виджет-заглушка, отображаемый при отсутствии выбранного объекта.
    
    На данном этапе:
    - Только структурный каркас
    - Содержит текстовую заглушку
    """
    
    # Сообщение по умолчанию
    _DEFAULT_MESSAGE = "Выберите объект в дереве слева"
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует виджет-заглушку.
        
        Args:
            parent: Родительский виджет
        """
        log.info("Инициализация PlaceholderWidget")
        super().__init__(parent)
        
        log.debug("PlaceholderWidget: создание структурного каркаса")
        
        self._setup_ui()
        
        log.debug("PlaceholderWidget: структурный каркас создан")
        log.system("PlaceholderWidget инициализирован")

    def _setup_ui(self) -> None:
        """Создает структурный каркас заглушки."""
        # Основной layout с центрированием
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Текстовая метка
        self._message_label = QLabel(self._DEFAULT_MESSAGE)
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setWordWrap(True)
        
        layout.addWidget(self._message_label)
        
        log.debug("PlaceholderWidget: UI каркас создан")
    
    # ===== Геттеры (для будущего использования) =====
    
    @property
    def message_label(self) -> QLabel:
        """Возвращает виджет текстовой метки."""
        return self._message_label