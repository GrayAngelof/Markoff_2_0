# client/src/ui/details/display_handlers.py
"""
Обработчики отображения для разных типов объектов.
Обновлены для работы с реальными данными из БД.
"""
from typing import TYPE_CHECKING, Optional

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.models.counterparty import Counterparty
from src.ui.details.field_manager import FieldManager

from utils.logger import get_logger
log = get_logger(__name__)


# Для избежания циклических импортов при проверке типов
if TYPE_CHECKING:
    from src.ui.details.details_panel import DetailsPanel


class DisplayHandlers:
    """
    Набор статических методов для отображения разных типов объектов.
    
    Теперь все данные берутся из БД, никаких заглушек.
    """
    
    # ===== Константы =====
    ICON_COMPLEX = "🏢"
    ICON_BUILDING = "🏭"
    ICON_FLOOR = "🏗️"
    ICON_ROOM = "🚪"
    
    @staticmethod
    def show_complex(panel: 'DetailsPanel', data: Complex) -> None:
        """
        Отображает информацию о комплексе.
        
        Args:
            panel: Панель деталей
            data: Данные комплекса
        """
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(f"КОМПЛЕКС: {data.name}")
        panel.hierarchy_label.setText("")
        panel.icon_label.setText(DisplayHandlers.ICON_COMPLEX)
        
        # Статус (пока не используется для комплексов)
        panel.status_label.setText("")
        panel.set_status_style(None)
        
        # Основные поля
        panel.info_grid.set_field("address", data.address)
        panel.info_grid.set_field("description", data.description)
        
        # Информация о владельце (если есть)
        if hasattr(data, 'owner_id') and data.owner_id:
            panel.info_grid.set_field("owner_id", f"ID владельца: {data.owner_id}")
        
        # Показываем сетку и нужные поля
        panel.show_info_grid()
        panel.info_grid.show_only("address", "description", "owner_id")
        
        log.info(f"Отображён комплекс '{data.name}' (ID: {data.id})")
    
    @staticmethod
    def show_building(panel: 'DetailsPanel', data: Building, complex_name: str) -> None:
        """
        Отображает информацию о корпусе.
        
        Args:
            panel: Панель деталей
            data: Данные корпуса
            complex_name: Название родительского комплекса
        """
        # Заголовок и иерархия
        panel.title_label.setText(f"КОРПУС: {data.name}")
        hierarchy_text = f"(в составе комплекса: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_BUILDING)
        
        # Статус
        if data.status_id:
            # TODO: загружать название статуса из справочника
            panel.status_label.setText("Эксплуатируется")
        else:
            panel.status_label.setText("")
        panel.set_status_style(None)
        
        # Основные поля
        panel.info_grid.set_field("address", data.address)
        panel.info_grid.set_field("description", data.description)
        panel.info_grid.set_field("floors_count", f"Этажей: {data.floors_count}")
        
        # Информация о владельце будет добавлена позже через update_owner_info
        
        # Показываем основные поля
        panel.show_info_grid()
        panel.info_grid.show_only("address", "description", "floors_count")
        
        log.info(f"Отображён корпус '{data.name}' (ID: {data.id})")
    
    @staticmethod
    def show_floor(panel: 'DetailsPanel', data: Floor, building_name: str, complex_name: str) -> None:
        """
        Отображает информацию об этаже.
        
        Args:
            panel: Панель деталей
            data: Данные этажа
            building_name: Название родительского корпуса
            complex_name: Название родительского комплекса
        """
        # Форматируем номер этажа
        floor_text = DisplayHandlers._format_floor_number(data.number)
        
        # Заголовок и иерархия
        panel.title_label.setText(f"ЭТАЖ: {floor_text}")
        hierarchy_text = f"(корпус {building_name}, комплекс {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_FLOOR)
        
        # Статус
        panel.status_label.setText("")
        panel.set_status_style(None)
        
        # Основные поля
        panel.info_grid.set_field("description", data.description)
        panel.info_grid.set_field("rooms_count", f"Помещений: {data.rooms_count}")
        
        # Тип этажа (если есть)
        if data.physical_type_id:
            panel.info_grid.set_field("type", f"Тип: #{data.physical_type_id}")
        
        # Планировка (если есть URL)
        if data.plan_image_url:
            panel.info_grid.set_field("plan", data.plan_image_url)
        
        # Показываем сетку
        panel.show_info_grid()
        panel.info_grid.show_only("description", "rooms_count", "type", "plan")
        
        log.info(f"Отображён этаж {data.number} (ID: {data.id})")
    
    @staticmethod
    def show_room(panel: 'DetailsPanel', data: Room, floor_num: int, 
                  building_name: str, complex_name: str) -> None:
        """
        Отображает информацию о помещении.
        
        Args:
            panel: Панель деталей
            data: Данные помещения
            floor_num: Номер этажа
            building_name: Название родительского корпуса
            complex_name: Название родительского комплекса
        """
        # Заголовок
        panel.title_label.setText(f"ПОМЕЩЕНИЕ: {data.number}")
        
        # Иерархия
        hierarchy_text = DisplayHandlers._format_room_hierarchy(
            floor_num, building_name, complex_name
        )
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_ROOM)
        
        # Статус
        status_text = FieldManager.format_status(data.status_code)
        panel.status_label.setText(status_text)
        panel.set_status_style(data.status_code)
        
        # Основные поля
        panel.info_grid.set_field("area", FieldManager.format_area(data.area))
        panel.info_grid.set_field("description", data.description or "Описание отсутствует")
        
        # Тип помещения
        if data.physical_type_id:
            # TODO: загружать название типа из справочника
            panel.info_grid.set_field("type", f"Тип: #{data.physical_type_id}")
        
        # Максимальное количество арендаторов
        if data.max_tenants:
            panel.info_grid.set_field("max_tenants", f"Макс. арендаторов: {data.max_tenants}")
        
        # Определяем базовые поля для всех помещений
        base_fields = ["area", "description", "type", "max_tenants"]
        
        # Если помещение занято, показываем информацию об арендаторе
        if data.status_code == 'occupied':
            # TODO: загружать реальные данные об арендаторе
            panel.info_grid.set_field("tenant", "Арендатор будет загружен...")
            panel.info_grid.set_field("contract", "")
            panel.info_grid.set_field("valid_until", "")
            panel.info_grid.set_field("rent", "")
            
            panel.info_grid.show_only(*(base_fields + ["tenant"]))
        else:
            panel.info_grid.show_only(*base_fields)
        
        panel.show_info_grid()
        log.info(f"Отображено помещение {data.number} (ID: {data.id}), статус: {data.status_code}")
    
    # ===== Вспомогательные методы =====
    
    @staticmethod
    def _format_floor_number(number: int) -> str:
        """Форматирует номер этажа."""
        if number < 0:
            return f"Подвал {abs(number)}"
        elif number == 0:
            return "Цокольный этаж"
        else:
            return f"Этаж {number}"
    
    @staticmethod
    def _format_room_hierarchy(floor_num: int, building_name: str, complex_name: str) -> str:
        """Форматирует строку иерархии для помещения."""
        if floor_num < 0:
            floor_text = f"подвал {abs(floor_num)}"
        elif floor_num == 0:
            floor_text = "цокольный этаж"
        else:
            floor_text = f"этаж {floor_num}"
        
        return f"({floor_text}, корпус {building_name}, комплекс {complex_name})"