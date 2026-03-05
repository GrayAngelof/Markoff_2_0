# client/src/ui/details/details_panel.py
"""
Основной класс панели детальной информации
"""
from PySide6.QtCore import Slot
from typing import Optional, Tuple, Any

from src.ui.details.base_panel import DetailsPanelBase
from src.ui.details.display_handlers import DisplayHandlers
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class DetailsPanel(DetailsPanelBase):
    """
    Панель детальной информации с вкладками
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("✅ DetailsPanel: создана")
    
    def _log_hierarchy(self, item_type: str, hierarchy_text: str):
        """Логирование иерархии для отладки"""
        print(f"📋 DetailsPanel: [{item_type}] иерархия: {hierarchy_text}")
    
    @Slot(str, int, object, dict)
    def show_item_details(self, item_type: str, item_id: int, item_data, context: dict):
        """
        Показать информацию о выбранном объекте с контекстом из родительских узлов
        
        Args:
            item_type: тип элемента
            item_id: идентификатор
            item_data: объект модели
            context: словарь с именами родительских узлов
        """
        self.current_type = item_type
        self.current_id = item_id
        self.current_data = item_data
        
        print(f"\n📋 DetailsPanel: выбран {item_type} #{item_id}")
        print(f"   Контекст: {context}")
        
        # Скрываем заглушку
        self.placeholder.hide()
        
        # Очищаем поля
        self.clear_all_fields()
        
        # Отображаем соответствующий тип с контекстом из узла
        if item_type == 'complex' and isinstance(item_data, Complex):
            DisplayHandlers.show_complex(self, item_data)
            
        elif item_type == 'building' and isinstance(item_data, Building):
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            DisplayHandlers.show_building(self, item_data, complex_name)
            
        elif item_type == 'floor' and isinstance(item_data, Floor):
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            DisplayHandlers.show_floor(self, item_data, building_name, complex_name)
            
        elif item_type == 'room' and isinstance(item_data, Room):
            floor_num = context.get('floor_num', 0)
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            DisplayHandlers.show_room(self, item_data, floor_num, building_name, complex_name)
            
        else:
            self.clear()
        # Отладочный вывод
        visible = []
        for key, widget in self.fields.items():
            if widget.parent().isVisible():
                visible.append(key)
        print(f"📊 После отображения видимы поля: {sorted(visible)}")
    
    def clear(self):
        """Очистить панель (показать заглушку)"""
        self.current_type = None
        self.current_id = None
        self.current_data = None
        
        self.hide_info_grid()
        
        self.title_label.setText("")
        self.hierarchy_label.setText("")
        self.status_label.setText("")
        self.icon_label.setText("🏢")
    
    def get_current_selection(self) -> Tuple[Optional[str], Optional[int], Optional[Any]]:
        """Получить текущий выбранный объект"""
        return self.current_type, self.current_id, self.current_data