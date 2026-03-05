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
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Явно делаем себя видимым
        self.setVisible(True)
        
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Шапка (всегда видима)
        self.header = HeaderWidget()
        self.header.setVisible(True)
        layout.addWidget(self.header)
        
        # Контейнер для контента
        self.content_widget = QWidget()
        self.content_widget.setVisible(True)
        
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        
        # Заглушка (видима по умолчанию)
        self.placeholder = PlaceholderWidget()
        self.placeholder.setVisible(True)
        self.content_layout.addWidget(self.placeholder)
        
        # Сетка информации (скрыта по умолчанию)
        self.info_grid = InfoGrid()
        self.info_grid.setVisible(False)
        self.content_layout.addWidget(self.info_grid)
        
        # Вкладки (всегда видимы)
        self.tabs = DetailsTabs()
        self.tabs.setVisible(True)
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
        print("🔧 base_panel.show_info_grid: показываем info_grid")
        
        # Убеждаемся, что вся цепочка видима
        self.setVisible(True)
        self.content_widget.setVisible(True)
        self.info_grid.setVisible(True)
        
        # Скрываем заглушку
        self.placeholder.setVisible(False)
        
        # Проверка видимости
        print(f"🔧 base_panel видим: {self.isVisible()}")
        print(f"🔧 content_widget видим: {self.content_widget.isVisible()}")
        print(f"🔧 info_grid видим: {self.info_grid.isVisible()}")
    
    def hide_info_grid(self):
        """Скрыть сетку информации и показать заглушку"""
        self.placeholder.setVisible(True)
        self.info_grid.setVisible(False)
    
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