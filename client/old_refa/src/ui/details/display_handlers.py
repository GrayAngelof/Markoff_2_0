# client/src/ui/details/display_handlers.py
"""
Обработчики отображения для разных типов объектов.
Использует DisplayConfig для определения полей.
"""
from typing import TYPE_CHECKING, Dict, Any

from src.ui.details.display_config import DisplayConfig
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room

from utils.logger import get_logger

if TYPE_CHECKING:
    from src.ui.details.details_panel import DetailsPanel

log = get_logger(__name__)


class DisplayHandlers:
    """
    Набор статических методов для отображения разных типов объектов.
    Делегирует получение полей в DisplayConfig.
    """
    
    # ===== Константы =====
    ICON_COMPLEX = "🏢"
    ICON_BUILDING = "🏭"
    ICON_FLOOR = "🏗️"
    ICON_ROOM = "🚪"
    
    @classmethod
    def _populate_fields(cls, panel: 'DetailsPanel', fields, data: Any) -> None:
        """
        Заполняет панель полями из конфигурации
        
        Args:
            panel: Панель деталей
            fields: Список FieldDefinition
            data: Данные объекта
        """
        fields_to_show = []
        
        for field_def in fields:
            # Проверяем условие показа поля
            if not field_def.condition(data):
                log.debug(f"Поле '{field_def.label}' скрыто по условию")
                continue
            
            # Получаем значение
            try:
                value = field_def.getter(data)
            except Exception as e:
                log.error(f"Ошибка получения значения для поля '{field_def.label}': {e}")
                value = "Ошибка данных"
            
            # Устанавливаем поле
            panel.info_grid.set_field(field_def.label, value)
            fields_to_show.append(field_def.label)
            log.debug(f"Установлено поле '{field_def.label}': {value}")
        
        # Показываем только добавленные поля
        if fields_to_show:
            panel.info_grid.show_only(*fields_to_show)
            log.debug(f"Показано {len(fields_to_show)} полей: {fields_to_show}")
    
    @classmethod
    def show_complex(cls, panel: 'DetailsPanel', data: Complex) -> None:
        """
        Отображает информацию о комплексе.
        """
        log.info(f"show_complex: id={data.id}, name={data.name}")
        log.debug(f"show_complex: data.address={data.address}, data.description={data.description}")
        log.debug(f"show_complex: data.owner_id={data.owner_id}")
        
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(DisplayConfig.get_title('complex', data))
        panel.hierarchy_label.setText(DisplayConfig.get_hierarchy('complex', data, {}))
        panel.icon_label.setText(cls.ICON_COMPLEX)
        
        # Статус
        status_text = DisplayConfig.get_status('complex', data)
        panel.status_label.setText(status_text)
        panel.set_status_style(None)  # Для комплексов статус не используем
        
        # Получаем поля из конфигурации и заполняем
        fields = DisplayConfig.get_complex_fields()
        cls._populate_fields(panel, fields, data)
        
        # Показываем сетку
        panel.show_info_grid()
        
        log.info(f"Отображён комплекс '{data.name}' (ID: {data.id})")
    
    @classmethod
    def show_building(cls, panel: 'DetailsPanel', data: Building, complex_name: str) -> None:
        """
        Отображает информацию о корпусе.
        
        Args:
            panel: Панель деталей
            data: Данные корпуса
            complex_name: Название родительского комплекса
        """
        log.info(f"show_building: id={data.id}, name={data.name}")
        log.debug(f"show_building: data.address={data.address}, data.description={data.description}")
        log.debug(f"show_building: data.owner_id={data.owner_id}")
        
        # Контекст для иерархии
        context = {'complex_name': complex_name}
        
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(DisplayConfig.get_title('building', data))
        panel.hierarchy_label.setText(DisplayConfig.get_hierarchy('building', data, context))
        panel.icon_label.setText(cls.ICON_BUILDING)
        
        # Статус
        status_text = DisplayConfig.get_status('building', data)
        panel.status_label.setText(status_text)
        panel.set_status_style(None)
        
        # Получаем поля из конфигурации и заполняем
        fields = DisplayConfig.get_building_fields()
        cls._populate_fields(panel, fields, data)
        
        # Показываем сетку
        panel.show_info_grid()
        
        log.info(f"Отображён корпус '{data.name}' (ID: {data.id})")
    
    @classmethod
    def show_floor(cls, panel: 'DetailsPanel', data: Floor, building_name: str, complex_name: str) -> None:
        """
        Отображает информацию об этаже.
        
        Args:
            panel: Панель деталей
            data: Данные этажа
            building_name: Название родительского корпуса
            complex_name: Название родительского комплекса
        """
        log.info(f"show_floor: id={data.id}, number={data.number}")
        log.debug(f"show_floor: data.description={data.description}")
        log.debug(f"show_floor: data.plan_image_url={data.plan_image_url}")
        
        # Контекст для иерархии
        context = {
            'building_name': building_name,
            'complex_name': complex_name
        }
        
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(DisplayConfig.get_title('floor', data))
        panel.hierarchy_label.setText(DisplayConfig.get_hierarchy('floor', data, context))
        panel.icon_label.setText(cls.ICON_FLOOR)
        
        # Статус
        status_text = DisplayConfig.get_status('floor', data)
        panel.status_label.setText(status_text)
        panel.set_status_style(None)
        
        # Получаем поля из конфигурации и заполняем
        fields = DisplayConfig.get_floor_fields()
        cls._populate_fields(panel, fields, data)
        
        # Показываем сетку
        panel.show_info_grid()
        
        log.info(f"Отображён этаж {data.number} (ID: {data.id})")
    
    @classmethod
    def show_room(cls, panel: 'DetailsPanel', data: Room, floor_num: int, 
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
        log.info(f"show_room: id={data.id}, number={data.number}, status={data.status_code}")
        log.debug(f"show_room: data.area={data.area}, data.description={data.description}")
        log.debug(f"show_room: data.physical_type_id={data.physical_type_id}")
        
        # Контекст для иерархии
        context = {
            'floor_num': str(floor_num),
            'building_name': building_name,
            'complex_name': complex_name
        }
        
        # Устанавливаем заголовок и иерархию
        panel.title_label.setText(DisplayConfig.get_title('room', data))
        panel.hierarchy_label.setText(DisplayConfig.get_hierarchy('room', data, context))
        panel.icon_label.setText(cls.ICON_ROOM)
        
        # Статус
        status_text = DisplayConfig.get_status('room', data)
        panel.status_label.setText(status_text)
        panel.set_status_style(data.status_code)
        
        # Получаем поля из конфигурации в зависимости от статуса
        fields = DisplayConfig.get_room_fields(data.status_code)
        cls._populate_fields(panel, fields, data)
        
        # Показываем сетку
        panel.show_info_grid()
        
        log.info(f"Отображено помещение {data.number} (ID: {data.id})")