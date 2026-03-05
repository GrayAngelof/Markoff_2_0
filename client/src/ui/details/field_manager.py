# client/src/ui/details/field_manager.py
"""
Менеджер для работы с полями информации
"""
from typing import Dict, Any, Optional


class FieldManager:
    """
    Управляет значениями полей и их отображением
    """
    
    # Карта типов помещений (временная, потом будет из БД)
    ROOM_TYPE_MAP = {
        1: "Офисное помещение",
        2: "Архив",
        3: "Склад",
        4: "Техническое помещение",
    }
    
    # Карта статусов
    STATUS_MAP = {
        'free': 'СВОБОДНО',
        'occupied': 'ЗАНЯТО',
        'reserved': 'ЗАРЕЗЕРВИРОВАНО',
        'maintenance': 'РЕМОНТ'
    }
    
    @staticmethod
    def format_status(status_code: Optional[str]) -> str:
        """Форматирование статуса"""
        return FieldManager.STATUS_MAP.get(status_code, status_code or "НЕИЗВЕСТНО")
    
    @staticmethod
    def format_room_type(type_id: Optional[int]) -> str:
        """Форматирование типа помещения"""
        return FieldManager.ROOM_TYPE_MAP.get(type_id, "Неизвестный тип")
    
    @staticmethod
    def format_area(area: Optional[float]) -> str:
        """Форматирование площади"""
        if area:
            return f"Площадь: {area} м²"
        return "Площадь не указана"
    
    @staticmethod
    def format_owner(owner_id: Optional[int]) -> Optional[str]:
        """Форматирование владельца"""
        if owner_id:
            return f"ID владельца: {owner_id}"
        return None