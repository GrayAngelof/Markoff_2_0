# client/src/ui/details/display_handlers.py
"""
Обработчики отображения для разных типов объектов
"""
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.ui.details.field_manager import FieldManager


class DisplayHandlers:
    """
    Набор методов для отображения разных типов объектов
    """
    
    @staticmethod
    def show_complex(panel, data: Complex):
        """Отображение комплекса"""
        panel.title_label.setText(f"КОМПЛЕКС: {data.name}")
        panel.hierarchy_label.setText("")
        panel.icon_label.setText("🏢")
        
        panel._log_hierarchy("complex", "корневой уровень")
        
        panel.status_label.setText("Активен")
        panel.set_status_style(None)
        
        panel.set_field("address", data.address)
        panel.set_field("owner", FieldManager.format_owner(data.owner_id))
        panel.set_field("description", data.description)
        panel.set_field("plan", "[ ссылка на общий план ]")
        
        panel.show_info_grid()
        panel.show_fields("address", "owner", "description", "plan")
    
    @staticmethod
    def show_building(panel, data: Building, complex_name: str):
        """Отображение корпуса"""
        panel.title_label.setText(f"КОРПУС: {data.name}")
        hierarchy_text = f"(в составе комплекса: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText("🏭")
        
        panel._log_hierarchy("building", hierarchy_text)
        
        panel.status_label.setText("Активен")
        panel.set_status_style(None)
        
        panel.set_field("address", data.address)
        panel.set_field("description", data.description)
        panel.set_field("plan", "[ ссылка на планы корпуса ]")
        
        panel.show_info_grid()
        panel.show_fields("address", "description", "plan")
    
    @staticmethod
    def show_floor(panel, data: Floor, building_name: str, complex_name: str):
        """Отображение этажа"""
        # Номер этажа
        if data.number < 0:
            floor_text = f"Подвал {abs(data.number)}"
        elif data.number == 0:
            floor_text = "Цокольный этаж"
        else:
            floor_text = f"Этаж {data.number}"
        
        panel.title_label.setText(f"ЭТАЖ: {floor_text}")
        hierarchy_text = f"(в составе корпуса: {building_name}, комплекс: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText("🏗️")
        
        panel._log_hierarchy("floor", hierarchy_text)
        
        panel.status_label.setText("Активен")
        panel.set_status_style(None)
        
        panel.set_field("description", data.description)
        panel.set_field("plan", "[ ссылка на план этажа ]")
        panel.set_field("type", "Этаж с офисами")
        
        panel.show_info_grid()
        panel.show_fields("description", "plan", "type")
    
    @staticmethod
    def show_room(panel, data: Room, floor_num: int, building_name: str, complex_name: str):
        """Отображение помещения"""
        panel.title_label.setText(f"ПОМЕЩЕНИЕ: {data.number}")
        
        # Формируем строку иерархии
        if floor_num < 0:
            floor_text = f"подвал {abs(floor_num)}"
        elif floor_num == 0:
            floor_text = "цокольный этаж"
        else:
            floor_text = f"этаж {floor_num}"
        
        hierarchy_text = f"(этаж {floor_num}, корпус {building_name}, комплекс: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText("🚪")
        
        panel._log_hierarchy("room", hierarchy_text)
        
        # Статус
        status_text = FieldManager.format_status(data.status_code)
        panel.status_label.setText(status_text)
        panel.set_status_style(data.status_code)
        
        # Площадь
        panel.set_field("address", FieldManager.format_area(data.area))
        
        # Тип помещения
        panel.set_field("type", FieldManager.format_room_type(data.physical_type_id))
        
        # Описание
        panel.set_field("description", data.description or "Описание отсутствует")
        
        # Планировка (пока нет)
        panel.set_field("plan", None)
        
        panel.show_info_grid()
        
        # Базовые поля для всех помещений
        base_fields = ["address", "type", "description", "plan"]
        
        # Для занятых помещений добавляем поля аренды
        if data.status_code == 'occupied':
            # TODO: брать реальные данные из БД
            panel.set_field("tenant", "Арендатор: ООО \"Ромашка\" (ИНН 7712345678)")
            panel.set_field("contract", "Договор: №А-2024-001 от 01.01.2024")
            panel.set_field("valid_until", "Действует до: 31.12.2025")
            panel.set_field("rent", "Арендная плата: 45 000 ₽/мес")
            
            # Показываем все поля
            panel.show_fields(*(base_fields + ["tenant", "contract", "valid_until", "rent"]))
        else:
            # Для свободных и других статусов
            panel.set_field("tenant", None)
            panel.set_field("contract", None)
            panel.set_field("valid_until", None)
            panel.set_field("rent", None)
            
            # Показываем только базовые поля
            panel.show_fields(*base_fields)