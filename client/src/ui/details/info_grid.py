# client/src/ui/details/info_grid.py
"""
Сетка с полями информации для панели деталей.
На данном этапе — пустой контейнер без полей.
"""

from PySide6.QtWidgets import QWidget, QGridLayout
from typing import Optional, Dict

from utils.logger import get_logger

log = get_logger(__name__)


class InfoGrid(QWidget):
    """
    Сетка для отображения информации в формате "Лейбл: Значение".
    
    На данном этапе:
    - Только структурный каркас
    - Не содержит полей
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует сетку информации.
        
        Args:
            parent: Родительский виджет
        """
        log.info("Инициализация InfoGrid")
        super().__init__(parent)
        
        log.debug("InfoGrid: создание структурного каркаса")
        
        self._setup_ui()
        
        log.debug("InfoGrid: структурный каркас создан")
        log.system("InfoGrid инициализирован")

    def _setup_ui(self) -> None:
        """Создает структурный каркас сетки."""
        # Сетка (пока пустая)
        self._grid = QGridLayout(self)
        self._grid.setVerticalSpacing(8)
        self._grid.setHorizontalSpacing(20)
        self._grid.setColumnStretch(1, 1)
        
        # Словари для будущих полей
        self._label_widgets: Dict[str, QWidget] = {}
        self._value_widgets: Dict[str, QWidget] = {}
        
        log.debug("InfoGrid: UI каркас создан")
    
    # ===== Геттеры (для будущего использования) =====
    
    @property
    def fields(self) -> Dict[str, QWidget]:
        """Возвращает словарь всех полей значений."""
        return self._value_widgets.copy()
    
    @property
    def labels(self) -> Dict[str, QWidget]:
        """Возвращает словарь всех лейблов."""
        return self._label_widgets.copy()