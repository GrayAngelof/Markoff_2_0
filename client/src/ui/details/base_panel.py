# client/src/ui/details/base_panel.py
"""
Базовый класс для панели детальной информации
Содержит общую инициализацию и базовые компоненты
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from src.ui.details.header_widget import HeaderWidget
from src.ui.details.placeholder import PlaceholderWidget
from src.ui.details.info_grid import InfoGrid
from src.ui.details.tabs import DetailsTabs


class DetailsPanelBase(QWidget):
    """
    Базовый класс для панели детальной информации
    Содержит:
    - Шапку (HeaderWidget)
    - Заглушку (PlaceholderWidget)
    - Сетку информации (InfoGrid)
    - Вкладки (DetailsTabs)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Шапка
        self.header = HeaderWidget()
        layout.addWidget(self.header)
        
        # Контейнер для контента
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        
        # Заглушка
        self.placeholder = PlaceholderWidget()
        self.content_layout.addWidget(self.placeholder)
        
        # Сетка информации (изначально скрыта)
        self.info_grid = InfoGrid()
        self.info_grid.hide()
        self.content_layout.addWidget(self.info_grid)
        
        # Вкладки
        self.tabs = DetailsTabs()
        self.content_layout.addWidget(self.tabs)
        
        layout.addWidget(self.content_widget)
        layout.addStretch()
        
        # Состояние
        self.current_type = None
        self.current_id = None
        self.current_data = None
    
    # ===== Прокси-методы для доступа к компонентам =====
    
    @property
    def title_label(self):
        return self.header.title_label
    
    @property
    def hierarchy_label(self):
        return self.header.hierarchy_label
    
    @property
    def status_label(self):
        return self.header.status_label
    
    @property
    def icon_label(self):
        return self.header.icon_label
    
    @property
    def fields(self):
        return self.info_grid.fields
    
    def show_info_grid(self):
        """Показать сетку информации и скрыть заглушку"""
        self.placeholder.hide()
        self.info_grid.show()
    
    def hide_info_grid(self):
        """Скрыть сетку информации и показать заглушку"""
        self.placeholder.show()
        self.info_grid.hide()
    
    def clear_all_fields(self):
        """Очистить все поля"""
        self.info_grid.clear_all()
    
    def set_field(self, key: str, value):
        """Установить значение поля"""
        self.info_grid.set_field(key, value)
    
    def set_status_style(self, status: str):
        """Установить стиль статуса"""
        self.header.set_status_style(status)
    
    def show_fields(self, *keys):
        """Показать только указанные поля"""
        self.info_grid.show_only(*keys)