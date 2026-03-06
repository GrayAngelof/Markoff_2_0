# client/src/ui/details/field_manager.py
"""
Менеджер для форматирования и обработки полей информации.
Предоставляет статические методы для преобразования данных из БД
в человекочитаемый формат для отображения в панели деталей.
"""
from typing import Dict, Any, Optional, Union
from datetime import datetime

from src.utils.logger import get_logger
log = get_logger(__name__)


class FieldManager:
    """
    Управляет форматированием значений полей для отображения.
    
    Содержит методы для форматирования:
    - Статусов объектов
    - Типов помещений
    - Площади
    - Информации о владельце
    - Дат
    
    В будущем может быть расширен для получения данных из справочников БД.
    """
    
    # ===== Константы =====
    
    # Карта типов помещений (временная, потом будет из БД)
    ROOM_TYPE_MAP: Dict[int, str] = {
        1: "Офисное помещение",
        2: "Архив",
        3: "Склад",
        4: "Техническое помещение",
    }
    """Словарь для преобразования ID типа помещения в текстовое описание"""
    
    # Карта статусов
    STATUS_MAP: Dict[str, str] = {
        'free': 'СВОБОДНО',
        'occupied': 'ЗАНЯТО',
        'reserved': 'ЗАРЕЗЕРВИРОВАНО',
        'maintenance': 'РЕМОНТ'
    }
    """Словарь для преобразования кода статуса в текстовое описание"""
    
    # Значения по умолчанию
    DEFAULT_UNKNOWN_STATUS = "НЕИЗВЕСТНО"
    """Текст для неизвестного статуса"""
    
    DEFAULT_UNKNOWN_TYPE = "Неизвестный тип"
    """Текст для неизвестного типа помещения"""
    
    DEFAULT_AREA_FORMAT = "Площадь: {area} м²"
    """Шаблон для форматирования площади"""
    
    DEFAULT_AREA_MISSING = "Площадь не указана"
    """Текст при отсутствии информации о площади"""
    
    DEFAULT_OWNER_FORMAT = "ID владельца: {owner_id}"
    """Шаблон для форматирования информации о владельце"""
    
    DEFAULT_DATE_FORMAT = "%d.%m.%Y %H:%M"
    """Формат для отображения дат"""
    
    # ===== Публичные методы форматирования =====
    
    @staticmethod
    def format_status(status_code: Optional[str]) -> str:
        """
        Форматирует код статуса в человекочитаемый текст.
        
        Args:
            status_code: Код статуса ('free', 'occupied', и т.д.)
            
        Returns:
            str: Текстовое представление статуса
        """
        if status_code is None:
            return FieldManager.DEFAULT_UNKNOWN_STATUS
        
        formatted = FieldManager.STATUS_MAP.get(
            status_code, 
            status_code.upper() if status_code else FieldManager.DEFAULT_UNKNOWN_STATUS
        )
        
        log.debug(f"FieldManager: статус '{status_code}' -> '{formatted}'")
        return formatted
    
    @staticmethod
    def format_room_type(type_id: Optional[int]) -> str:
        """
        Форматирует ID типа помещения в текстовое описание.
        
        Args:
            type_id: ID типа помещения из справочника
            
        Returns:
            str: Название типа помещения
        """
        if type_id is None:
            return FieldManager.DEFAULT_UNKNOWN_TYPE
        
        formatted = FieldManager.ROOM_TYPE_MAP.get(
            type_id, 
            f"{FieldManager.DEFAULT_UNKNOWN_TYPE} (ID: {type_id})"
        )
        
        log.debug(f"FieldManager: тип помещения {type_id} -> '{formatted}'")
        return formatted
    
    @staticmethod
    def format_area(area: Optional[float]) -> str:
        """
        Форматирует значение площади.
        
        Args:
            area: Площадь в квадратных метрах
            
        Returns:
            str: Отформатированная строка с площадью
        """
        if area is None:
            return FieldManager.DEFAULT_AREA_MISSING
        
        formatted = FieldManager.DEFAULT_AREA_FORMAT.format(area=area)
        log.debug(f"FieldManager: площадь {area} м²")
        return formatted
    
    @staticmethod
    def format_owner(owner_id: Optional[int]) -> Optional[str]:
        """
        Форматирует информацию о владельце.
        
        Args:
            owner_id: ID владельца
            
        Returns:
            Optional[str]: Строка с информацией о владельце или None
        """
        if owner_id is None:
            return None
        
        formatted = FieldManager.DEFAULT_OWNER_FORMAT.format(owner_id=owner_id)
        log.debug(f"FieldManager: владелец ID {owner_id}")
        return formatted
    
    @staticmethod
    def format_datetime(dt: Optional[Union[str, datetime]]) -> Optional[str]:
        """
        Форматирует дату и время.
        
        Args:
            dt: Дата и время (строка ISO или объект datetime)
            
        Returns:
            Optional[str]: Отформатированная дата или None
        """
        if dt is None:
            return None
        
        try:
            if isinstance(dt, str):
                # Пробуем распарсить ISO формат
                if 'T' in dt:
                    # Берём только дату и время до минут
                    date_part = dt.split('T')[0]
                    time_part = dt.split('T')[1][:5]
                    formatted = f"{date_part} {time_part}"
                else:
                    formatted = dt
            elif hasattr(dt, 'strftime'):
                formatted = dt.strftime(FieldManager.DEFAULT_DATE_FORMAT)
            else:
                formatted = str(dt)
            
            log.debug(f"FieldManager: дата '{dt}' -> '{formatted}'")
            return formatted
            
        except Exception as error:
            log.error(f"FieldManager: ошибка форматирования даты '{dt}': {error}")
            return str(dt)
    
    @staticmethod
    def format_tenant(tenant_name: Optional[str], inn: Optional[str] = None) -> Optional[str]:
        """
        Форматирует информацию об арендаторе.
        
        Args:
            tenant_name: Название организации-арендатора
            inn: ИНН организации (опционально)
            
        Returns:
            Optional[str]: Отформатированная строка с информацией об арендаторе
        """
        if not tenant_name:
            return None
        
        if inn:
            formatted = f"Арендатор: {tenant_name} (ИНН {inn})"
        else:
            formatted = f"Арендатор: {tenant_name}"
        
        log.debug(f"FieldManager: арендатор '{formatted}'")
        return formatted
    
    @staticmethod
    def format_contract(contract_number: Optional[str], date_from: Optional[str] = None) -> Optional[str]:
        """
        Форматирует информацию о договоре.
        
        Args:
            contract_number: Номер договора
            date_from: Дата начала действия (опционально)
            
        Returns:
            Optional[str]: Отформатированная строка с информацией о договоре
        """
        if not contract_number:
            return None
        
        if date_from:
            formatted = f"Договор: №{contract_number} от {date_from}"
        else:
            formatted = f"Договор: №{contract_number}"
        
        log.debug(f"FieldManager: договор '{formatted}'")
        return formatted
    
    @staticmethod
    def format_valid_until(date_to: Optional[str]) -> Optional[str]:
        """
        Форматирует дату окончания действия договора.
        
        Args:
            date_to: Дата окончания
            
        Returns:
            Optional[str]: Отформатированная строка с датой
        """
        if not date_to:
            return None
        
        formatted = f"Действует до: {date_to}"
        log.debug(f"FieldManager: действует до '{formatted}'")
        return formatted
    
    @staticmethod
    def format_rent(amount: Optional[float], currency: str = "₽", period: str = "мес") -> Optional[str]:
        """
        Форматирует информацию об арендной плате.
        
        Args:
            amount: Сумма арендной платы
            currency: Валюта (по умолчанию ₽)
            period: Период (по умолчанию "мес")
            
        Returns:
            Optional[str]: Отформатированная строка с арендной платой
        """
        if amount is None:
            return None
        
        formatted = f"Арендная плата: {amount:,.0f} {currency}/{period}".replace(",", " ")
        log.debug(f"FieldManager: арендная плата '{formatted}'")
        return formatted
    
    # ===== Вспомогательные методы =====
    
    @staticmethod
    def get_available_room_types() -> Dict[int, str]:
        """
        Возвращает словарь доступных типов помещений.
        
        Returns:
            Dict[int, str]: Словарь {ID: название}
        """
        return FieldManager.ROOM_TYPE_MAP.copy()
    
    @staticmethod
    def get_available_statuses() -> Dict[str, str]:
        """
        Возвращает словарь доступных статусов.
        
        Returns:
            Dict[str, str]: Словарь {код: название}
        """
        return FieldManager.STATUS_MAP.copy()
    
    @staticmethod
    def is_valid_status(status_code: Optional[str]) -> bool:
        """
        Проверяет, является ли статус допустимым.
        
        Args:
            status_code: Код статуса для проверки
            
        Returns:
            bool: True если статус известен
        """
        return status_code in FieldManager.STATUS_MAP