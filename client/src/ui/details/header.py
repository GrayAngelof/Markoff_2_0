# client/src/ui/details/header.py
"""
Шапка панели детальной информации.
На данном этапе — пустой контейнер без логики.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


class HeaderWidget(QWidget):
    """
    Шапка панели детальной информации.
    
    На данном этапе:
    - Только структурный каркас
    - Содержит пустые метки-заглушки
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Инициализирует шапку.
        
        Args:
            parent: Родительский виджет
        """
        log.info("Инициализация HeaderWidget")
        super().__init__(parent)
        
        log.debug("HeaderWidget: создание структурного каркаса")
        
        self._setup_ui()
        
        log.debug("HeaderWidget: структурный каркас создан")
        log.system("HeaderWidget инициализирован")

    def _setup_ui(self) -> None:
        """Создает структурный каркас шапки."""
        # Основной вертикальный layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Верхняя строка: иконка и заголовок
        self._top_row = QWidget()
        top_layout = QVBoxLayout(self._top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Иконка (пока пустая)
        self._icon_label = QLabel("")
        top_layout.addWidget(self._icon_label)
        
        # Заголовок (пока пустой)
        self._title_label = QLabel("")
        self._title_label.setWordWrap(True)
        top_layout.addWidget(self._title_label)
        
        # Статус (пока пустой)
        self._status_label = QLabel("")
        top_layout.addWidget(self._status_label)
        
        layout.addWidget(self._top_row)
        
        # Нижняя строка: иерархия (пока пустая)
        self._hierarchy_label = QLabel("")
        self._hierarchy_label.setWordWrap(True)
        layout.addWidget(self._hierarchy_label)
        
        log.debug("HeaderWidget: UI каркас создан")
    
    # ===== Геттеры (для будущего использования) =====
    
    @property
    def icon_label(self) -> QLabel:
        """Возвращает виджет иконки."""
        return self._icon_label
    
    @property
    def title_label(self) -> QLabel:
        """Возвращает виджет заголовка."""
        return self._title_label
    
    @property
    def status_label(self) -> QLabel:
        """Возвращает виджет статуса."""
        return self._status_label
    
    @property
    def hierarchy_label(self) -> QLabel:
        """Возвращает виджет иерархии."""
        return self._hierarchy_label