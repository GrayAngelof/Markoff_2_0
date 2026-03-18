# client/src/ui/details/display_config.py
"""
Конфигурация отображения для разных типов узлов.
Определяет, какие поля показывать и откуда их брать.
"""
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room
from src.models.counterparty import Counterparty

from utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class FieldDefinition:
    """Определение поля для отображения"""
    label: str  # Что показывать в интерфейсе
    getter: Callable[[Any], str]  # Как получить значение
    condition: Callable[[Any], bool] = lambda x: True  # Когда показывать


class DisplayConfig:
    """
    Конфигурация отображения для разных типов узлов.
    Содержит правила, какие поля показывать и откуда их брать.
    """
    
    # ===== Заглушки для отсутствующих данных =====
    _PLACEHOLDER = "—"
    _TENANT_PLACEHOLDER = "Информация об арендаторе"
    _CONTRACT_PLACEHOLDER = "Информация о договоре"
    _RENT_PLACEHOLDER = "Информация об арендной плате"
    
    # ===== Форматтеры для разных типов данных =====
    
    @staticmethod
    def _format_owner(owner: Any) -> str:
        """Форматирует информацию о владельце"""
        if not owner:
            return DisplayConfig._PLACEHOLDER
        if isinstance(owner, Counterparty):
            return f"{owner.short_name} (ИНН {owner.tax_id})"
        return str(owner)
    
    @staticmethod
    def _format_datetime(dt: Optional[datetime]) -> str:
        """Форматирует дату и время"""
        if not dt:
            return DisplayConfig._PLACEHOLDER
        if isinstance(dt, str):
            return dt[:16].replace('T', ' ')
        return dt.strftime("%d.%m.%Y %H:%M")
    
    @staticmethod
    def _format_area(area: Optional[float]) -> str:
        """Форматирует площадь"""
        if area is None:
            return DisplayConfig._PLACEHOLDER
        return f"{area} м²"
    
    @staticmethod
    def _format_status(status: Optional[str]) -> str:
        """Форматирует статус помещения"""
        status_map = {
            'free': 'СВОБОДНО',
            'occupied': 'ЗАНЯТО',
            'reserved': 'ЗАРЕЗЕРВИРОВАНО',
            'maintenance': 'РЕМОНТ'
        }
        if not status:
            return DisplayConfig._PLACEHOLDER
        return status_map.get(status, status.upper())
    
    @staticmethod
    def _format_room_type(type_id: Optional[int]) -> str:
        """Форматирует тип помещения"""
        type_map = {
            1: "Офисное помещение",
            2: "Складское помещение",
            3: "Торговое помещение",
            4: "Производственное помещение",
        }
        if not type_id:
            return DisplayConfig._PLACEHOLDER
        return type_map.get(type_id, f"Тип {type_id}")
    
    @staticmethod
    def _format_floor_number(number: int) -> str:
        """Форматирует номер этажа"""
        if number < 0:
            return f"Подвал {abs(number)}"
        elif number == 0:
            return "Цокольный этаж"
        else:
            return f"Этаж {number}"
    
    # ===== Определения полей для каждого типа =====
    
    # Поля для КОМПЛЕКСА
    COMPLEX_FIELDS: List[FieldDefinition] = [
        FieldDefinition(
            label="Адрес",
            getter=lambda c: c.address if c.address else DisplayConfig._PLACEHOLDER
        ),
        FieldDefinition(
            label="Владелец",
            getter=lambda c: DisplayConfig._format_owner(getattr(c, 'owner', None)),
            condition=lambda c: hasattr(c, 'owner_id') and c.owner_id is not None
        ),
        FieldDefinition(
            label="Описание",
            getter=lambda c: c.description if c.description else DisplayConfig._PLACEHOLDER
        ),
        FieldDefinition(
            label="Создан",
            getter=lambda c: DisplayConfig._format_datetime(c.created_at)
        ),
        FieldDefinition(
            label="Обновлён",
            getter=lambda c: DisplayConfig._format_datetime(c.updated_at)
        ),
    ]
    
    # Поля для КОРПУСА
    BUILDING_FIELDS: List[FieldDefinition] = [
        FieldDefinition(
            label="Адрес",
            getter=lambda b: b.address if b.address else DisplayConfig._PLACEHOLDER
        ),
        FieldDefinition(
            label="Описание",
            getter=lambda b: b.description if b.description else DisplayConfig._PLACEHOLDER
        ),
        FieldDefinition(
            label="Создан",
            getter=lambda b: DisplayConfig._format_datetime(b.created_at)
        ),
        FieldDefinition(
            label="Обновлён",
            getter=lambda b: DisplayConfig._format_datetime(b.updated_at)
        ),
    ]
    
    # Поля для ЭТАЖА
    FLOOR_FIELDS: List[FieldDefinition] = [
        FieldDefinition(
            label="Описание",
            getter=lambda f: f.description if f.description else DisplayConfig._PLACEHOLDER
        ),
        FieldDefinition(
            label="Планировка",
            getter=lambda f: f.plan_image_url if f.plan_image_url else DisplayConfig._PLACEHOLDER
        ),
        FieldDefinition(
            label="Создан",
            getter=lambda f: DisplayConfig._format_datetime(f.created_at)
        ),
        FieldDefinition(
            label="Обновлён",
            getter=lambda f: DisplayConfig._format_datetime(f.updated_at)
        ),
    ]
    
    # Поля для СВОБОДНОГО ПОМЕЩЕНИЯ
    FREE_ROOM_FIELDS: List[FieldDefinition] = [
        FieldDefinition(
            label="Площадь",
            getter=lambda r: DisplayConfig._format_area(r.area)
        ),
        FieldDefinition(
            label="Тип",
            getter=lambda r: DisplayConfig._format_room_type(r.physical_type_id)
        ),
        FieldDefinition(
            label="Описание",
            getter=lambda r: r.description if r.description else DisplayConfig._PLACEHOLDER
        ),
        FieldDefinition(
            label="Создан",
            getter=lambda r: DisplayConfig._format_datetime(r.created_at)
        ),
        FieldDefinition(
            label="Обновлён",
            getter=lambda r: DisplayConfig._format_datetime(r.updated_at)
        ),
    ]
    
    # Поля для ЗАНЯТОГО ПОМЕЩЕНИЯ (дополнительные к базовым)
    OCCUPIED_ROOM_EXTRA_FIELDS: List[FieldDefinition] = [
        FieldDefinition(
            label="Арендатор",
            getter=lambda r: DisplayConfig._TENANT_PLACEHOLDER  # Заглушка
        ),
        FieldDefinition(
            label="Договор",
            getter=lambda r: DisplayConfig._CONTRACT_PLACEHOLDER  # Заглушка
        ),
        FieldDefinition(
            label="Действует до",
            getter=lambda r: DisplayConfig._PLACEHOLDER  # Заглушка
        ),
        FieldDefinition(
            label="Арендная плата",
            getter=lambda r: DisplayConfig._RENT_PLACEHOLDER  # Заглушка
        ),
    ]
    
    # ===== Методы для получения полей =====
    
    @classmethod
    def get_complex_fields(cls) -> List[FieldDefinition]:
        """Возвращает поля для комплекса"""
        log.debug(f"DisplayConfig: получено {len(cls.COMPLEX_FIELDS)} полей для комплекса")
        return cls.COMPLEX_FIELDS.copy()
    
    @classmethod
    def get_building_fields(cls) -> List[FieldDefinition]:
        """Возвращает поля для корпуса"""
        log.debug(f"DisplayConfig: получено {len(cls.BUILDING_FIELDS)} полей для корпуса")
        return cls.BUILDING_FIELDS.copy()
    
    @classmethod
    def get_floor_fields(cls) -> List[FieldDefinition]:
        """Возвращает поля для этажа"""
        log.debug(f"DisplayConfig: получено {len(cls.FLOOR_FIELDS)} полей для этажа")
        return cls.FLOOR_FIELDS.copy()
    
    @classmethod
    def get_room_fields(cls, status_code: Optional[str]) -> List[FieldDefinition]:
        """
        Возвращает поля для помещения в зависимости от статуса
        
        Args:
            status_code: Код статуса помещения ('free', 'occupied', ...)
        """
        base_fields = cls.FREE_ROOM_FIELDS.copy()
        
        if status_code == 'occupied':
            fields = base_fields + cls.OCCUPIED_ROOM_EXTRA_FIELDS
            log.debug(f"DisplayConfig: получено {len(fields)} полей для ЗАНЯТОГО помещения")
        else:
            fields = base_fields
            log.debug(f"DisplayConfig: получено {len(fields)} полей для СВОБОДНОГО помещения")
        
        return fields
    
    @classmethod
    def get_title(cls, node_type: str, data: Any) -> str:
        """
        Возвращает заголовок для панели деталей
        
        Args:
            node_type: Тип узла
            data: Данные узла
        """
        if node_type == 'complex':
            return f"КОМПЛЕКС: {data.name}"
        elif node_type == 'building':
            return f"КОРПУС: {data.name}"
        elif node_type == 'floor':
            floor_text = cls._format_floor_number(data.number)
            return f"ЭТАЖ: {floor_text}"
        elif node_type == 'room':
            return f"ПОМЕЩЕНИЕ: {data.number}"
        else:
            log.warning(f"DisplayConfig: неизвестный тип узла '{node_type}'")
            return "НЕИЗВЕСТНЫЙ ОБЪЕКТ"
    
    @classmethod
    def get_status(cls, node_type: str, data: Any) -> str:
        """
        Возвращает статус для отображения
        
        Args:
            node_type: Тип узла
            data: Данные узла
        """
        if node_type == 'room':
            return cls._format_status(data.status_code)
        elif node_type in ['complex', 'building', 'floor']:
            return "Активен"  # Заглушка для статуса
        else:
            return ""
    
    @classmethod
    def get_hierarchy(cls, node_type: str, data: Any, context: Dict) -> str:
        """
        Возвращает строку иерархии для отображения
        
        Args:
            node_type: Тип узла
            data: Данные узла
            context: Контекст с именами родителей
        """
        if node_type == 'complex':
            return ""
        elif node_type == 'building':
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            return f"(в составе комплекса: {complex_name})"
        elif node_type == 'floor':
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            return f"(корпус {building_name}, комплекс {complex_name})"
        elif node_type == 'room':
            floor_num = context.get('floor_num', '?')
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            
            try:
                floor_int = int(floor_num) if floor_num != '?' else None
                if floor_int == 0:
                    floor_text = "цокольный этаж"
                elif floor_int and floor_int < 0:
                    floor_text = f"подвал {abs(floor_int)}"
                else:
                    floor_text = f"этаж {floor_num}"
            except (ValueError, TypeError):
                floor_text = f"этаж {floor_num}"
            
            return f"({floor_text}, корпус {building_name}, комплекс {complex_name})"
        else:
            return ""