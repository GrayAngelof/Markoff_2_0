# client/src/ui/details/display_handlers.py
"""
Обработчики отображения для разных типов объектов.
Предоставляют методы для заполнения панели детальной информации
данными из моделей Complex, Building, Floor, Room.
"""
from typing import TYPE_CHECKING

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.ui.details.field_manager import FieldManager

from src.utils.logger import get_logger
log = get_logger(__name__)


# Для избежания циклических импортов при проверке типов
if TYPE_CHECKING:
    from src.ui.details.base_panel import DetailsPanelBase


class DisplayHandlers:
    """
    Набор статических методов для отображения разных типов объектов.
    
    Каждый метод отвечает за заполнение панели данными соответствующего типа:
    - show_complex: отображение комплекса
    - show_building: отображение корпуса
    - show_floor: отображение этажа
    - show_room: отображение помещения
    
    Методы учитывают контекст иерархии и статус объекта.
    """
    
    # ===== Константы =====
    
    # Тексты для статусов по умолчанию
    _DEFAULT_STATUS = "Активен"
    """Текст статуса по умолчанию для комплексов, корпусов и этажей"""
    
    # Иконки для разных типов объектов
    ICON_COMPLEX = "🏢"
    ICON_BUILDING = "🏭"
    ICON_FLOOR = "🏗️"
    ICON_ROOM = "🚪"
    
    # Тексты для ссылок на планировки
    _PLAN_COMPLEX = "[ ссылка на общий план ]"
    _PLAN_BUILDING = "[ ссылка на планы корпуса ]"
    _PLAN_FLOOR = "[ ссылка на план этажа ]"
    
    # Текст для типа этажа по умолчанию
    _DEFAULT_FLOOR_TYPE = "Этаж с офисами"
    
    # Текст для отсутствующего описания
    _DESCRIPTION_MISSING = "Описание отсутствует"
    
    # ===== Приватные вспомогательные методы =====
    
    @staticmethod
    def _log_hierarchy(panel: 'DetailsPanelBase', item_type: str, hierarchy_text: str) -> None:
        """
        Логирует информацию об иерархии для отладки.
        
        Args:
            panel: Панель деталей
            item_type: Тип объекта
            hierarchy_text: Текст иерархии
        """
        if hasattr(panel, '_log_hierarchy'):
            panel._log_hierarchy(item_type, hierarchy_text)
    
    @staticmethod
    def _format_floor_number(number: int) -> str:
        """
        Форматирует номер этажа с учётом подвала и цоколя.
        
        Args:
            number: Номер этажа
            
        Returns:
            str: Отформатированное название этажа
        """
        if number < 0:
            return f"Подвал {abs(number)}"
        elif number == 0:
            return "Цокольный этаж"
        else:
            return f"Этаж {number}"
    
    @staticmethod
    def _format_room_hierarchy(floor_num: int, building_name: str, complex_name: str) -> str:
        """
        Форматирует строку иерархии для помещения.
        
        Args:
            floor_num: Номер этажа
            building_name: Название корпуса
            complex_name: Название комплекса
            
        Returns:
            str: Отформатированная строка иерархии
        """
        if floor_num < 0:
            floor_text = f"подвал {abs(floor_num)}"
        elif floor_num == 0:
            floor_text = "цокольный этаж"
        else:
            floor_text = f"этаж {floor_num}"
        
        return f"(этаж {floor_num}, корпус {building_name}, комплекс: {complex_name})"
    
    # ===== Публичные методы отображения =====
    
    @staticmethod
    def show_complex(panel: 'DetailsPanelBase', data: Complex) -> None:
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
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "complex", "корневой уровень")
        
        # Устанавливаем статус
        panel.status_label.setText(DisplayHandlers._DEFAULT_STATUS)
        panel.set_status_style(None)
        
        # Устанавливаем поля
        panel.set_field("address", data.address)
        panel.set_field("owner", FieldManager.format_owner(data.owner_id))
        panel.set_field("description", data.description)
        panel.set_field("plan", DisplayHandlers._PLAN_COMPLEX)
        
        # Очищаем лишние поля
        panel.set_field("tenant", None)
        panel.set_field("type", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        
        # Показываем сетку и нужные поля
        panel.show_info_grid()
        panel.show_fields("address", "owner", "description", "plan")
        
        log.info(f"Отображён комплекс '{data.name}' (ID: {data.id})")
    
    @staticmethod
    def show_building(panel: 'DetailsPanelBase', data: Building, complex_name: str) -> None:
        """
        Отображает информацию о корпусе.
        
        Args:
            panel: Панель деталей
            data: Данные корпуса
            complex_name: Название родительского комплекса
        """
        # Формируем заголовок и иерархию
        panel.title_label.setText(f"КОРПУС: {data.name}")
        hierarchy_text = f"(в составе комплекса: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_BUILDING)
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "building", hierarchy_text)
        
        # Устанавливаем статус
        panel.status_label.setText(DisplayHandlers._DEFAULT_STATUS)
        panel.set_status_style(None)
        
        # Устанавливаем поля
        panel.set_field("address", data.address)
        panel.set_field("description", data.description)
        panel.set_field("plan", DisplayHandlers._PLAN_BUILDING)
        
        # Очищаем лишние поля
        panel.set_field("owner", None)
        panel.set_field("tenant", None)
        panel.set_field("type", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        
        # Показываем сетку и нужные поля
        panel.show_info_grid()
        panel.show_fields("address", "description", "plan")
        
        log.info(f"Отображён корпус '{data.name}' (ID: {data.id})")
    
    @staticmethod
    def show_floor(panel: 'DetailsPanelBase', data: Floor, building_name: str, complex_name: str) -> None:
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
        
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(f"ЭТАЖ: {floor_text}")
        hierarchy_text = f"(в составе корпуса: {building_name}, комплекс: {complex_name})"
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_FLOOR)
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "floor", hierarchy_text)
        
        # Устанавливаем статус
        panel.status_label.setText(DisplayHandlers._DEFAULT_STATUS)
        panel.set_status_style(None)
        
        # Устанавливаем поля
        panel.set_field("description", data.description)
        panel.set_field("plan", DisplayHandlers._PLAN_FLOOR)
        panel.set_field("type", DisplayHandlers._DEFAULT_FLOOR_TYPE)
        
        # Очищаем лишние поля
        panel.set_field("address", None)
        panel.set_field("owner", None)
        panel.set_field("tenant", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        
        # Показываем сетку и нужные поля
        panel.show_info_grid()
        panel.show_fields("description", "plan", "type")
        
        log.info(f"Отображён этаж {data.number} (ID: {data.id})")
    
    @staticmethod
    def show_room(panel: 'DetailsPanelBase', data: Room, floor_num: int, 
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
        # Устанавливаем заголовок
        panel.title_label.setText(f"ПОМЕЩЕНИЕ: {data.number}")
        
        # Формируем и устанавливаем иерархию
        hierarchy_text = DisplayHandlers._format_room_hierarchy(
            floor_num, building_name, complex_name
        )
        panel.hierarchy_label.setText(hierarchy_text)
        panel.icon_label.setText(DisplayHandlers.ICON_ROOM)
        
        # Логируем
        DisplayHandlers._log_hierarchy(panel, "room", hierarchy_text)
        
        # Устанавливаем статус
        status_text = FieldManager.format_status(data.status_code)
        panel.status_label.setText(status_text)
        panel.set_status_style(data.status_code)
        
        # Устанавливаем основные поля
        panel.set_field("address", FieldManager.format_area(data.area))
        panel.set_field("type", FieldManager.format_room_type(data.physical_type_id))
        panel.set_field("description", data.description or DisplayHandlers._DESCRIPTION_MISSING)
        panel.set_field("plan", None)  # Планировка пока не поддерживается
        
        # Определяем базовые поля для всех помещений
        base_fields = ["address", "type", "description", "plan"]
        
        # Обработка в зависимости от статуса
        if data.status_code == 'occupied':
            # Для занятых помещений добавляем поля аренды
            DisplayHandlers._set_occupied_room_fields(panel, data)
            
            # Показываем все поля
            panel.show_fields(*(base_fields + ["tenant", "contract", "valid_until", "rent"]))
            
            log.info(f"Отображено занятое помещение {data.number} (ID: {data.id})")
        else:
            # Для свободных и других статусов
            DisplayHandlers._clear_rental_fields(panel)
            
            # Показываем только базовые поля
            panel.show_fields(*base_fields)
            
            log.info(f"Отображено помещение {data.number} (ID: {data.id}), статус: {data.status_code}")
    
    # ===== Приватные методы для работы с помещениями =====
    
    @staticmethod
    def _set_occupied_room_fields(panel: 'DetailsPanelBase', data: Room) -> None:
        """
        Устанавливает поля для занятого помещения.
        
        Args:
            panel: Панель деталей
            data: Данные помещения
        """
        # TODO: брать реальные данные из БД
        panel.set_field("tenant", "Арендатор: ООО \"Ромашка\" (ИНН 7712345678)")
        panel.set_field("contract", "Договор: №А-2024-001 от 01.01.2024")
        panel.set_field("valid_until", "Действует до: 31.12.2025")
        panel.set_field("rent", "Арендная плата: 45 000 ₽/мес")
        
        # Очищаем поле владельца (не нужно для аренды)
        panel.set_field("owner", None)
    
    @staticmethod
    def _clear_rental_fields(panel: 'DetailsPanelBase') -> None:
        """
        Очищает поля аренды для свободного помещения.
        
        Args:
            panel: Панель деталей
        """
        panel.set_field("tenant", None)
        panel.set_field("contract", None)
        panel.set_field("valid_until", None)
        panel.set_field("rent", None)
        panel.set_field("owner", None)