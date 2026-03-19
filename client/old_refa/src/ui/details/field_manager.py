# client/src/ui/details/field_manager.py
"""
Менеджер для форматирования и обработки полей информации.
Все данные загружаются из БД, никаких заглушек.
"""
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson

from utils.logger import get_logger
log = get_logger(__name__)


class FieldManager:
    """
    Управляет форматированием значений полей для отображения.
    
    Все справочники загружаются из БД через API.
    """
    
    # ===== Константы для форматирования (не справочники!) =====
    
    # Карта статусов помещений (коды фиксированы в БД)
    STATUS_MAP: Dict[str, str] = {
        'free': 'СВОБОДНО',
        'occupied': 'ЗАНЯТО',
        'reserved': 'ЗАРЕЗЕРВИРОВАНО',
        'maintenance': 'РЕМОНТ'
    }
    
    # Значения по умолчанию (только для случаев, когда данных нет)
    DEFAULT_UNKNOWN_STATUS = "НЕИЗВЕСТНО"
    DEFAULT_UNKNOWN_TYPE = "Неизвестный тип"
    DEFAULT_AREA_FORMAT = "Площадь: {area} м²"
    DEFAULT_AREA_MISSING = "Площадь не указана"
    DEFAULT_DATE_FORMAT = "%d.%m.%Y %H:%M"
    
    # Категории контактов (фиксированные в БД)
    CONTACT_CATEGORY_MAP: Dict[str, str] = {
        'legal': 'Юридические вопросы',
        'financial': 'Финансовые вопросы',
        'technical': 'Технические вопросы',
        'fire_safety': 'Пожарная безопасность',
        'emergency': 'Аварийные ситуации',
        'general': 'Общие вопросы',
    }
    
    # ===== Методы форматирования =====
    
    @staticmethod
    def format_status(status_code: Optional[str]) -> str:
        """Форматирует код статуса в человекочитаемый текст."""
        if status_code is None:
            return FieldManager.DEFAULT_UNKNOWN_STATUS
        
        formatted = FieldManager.STATUS_MAP.get(
            status_code, 
            status_code.upper() if status_code else FieldManager.DEFAULT_UNKNOWN_STATUS
        )
        
        log.debug(f"FieldManager: статус '{status_code}' -> '{formatted}'")
        return formatted
    
    @staticmethod
    def format_room_type(type_id: Optional[int], type_name: Optional[str] = None) -> str:
        """
        Форматирует тип помещения.
        
        Args:
            type_id: ID типа (для логирования)
            type_name: Название типа из БД
        """
        if type_name:
            return type_name
        
        if type_id:
            return f"Тип #{type_id}"
        
        return FieldManager.DEFAULT_UNKNOWN_TYPE
    
    @staticmethod
    def format_area(area: Optional[float]) -> str:
        """Форматирует значение площади."""
        if area is None:
            return FieldManager.DEFAULT_AREA_MISSING
        
        formatted = FieldManager.DEFAULT_AREA_FORMAT.format(area=area)
        log.debug(f"FieldManager: площадь {area} м²")
        return formatted
    
    @staticmethod
    def format_counterparty(counterparty: Optional[Counterparty]) -> str:
        """
        Форматирует информацию о контрагенте.
        
        Args:
            counterparty: Объект контрагента из БД
        """
        if not counterparty:
            return "Не указан"
        
        if counterparty.tax_id:
            return f"{counterparty.short_name} (ИНН {counterparty.tax_id})"
        return counterparty.short_name
    
    @staticmethod
    def format_counterparty_details(counterparty: Counterparty) -> Dict[str, str]:
        """
        Возвращает словарь с детальной информацией о контрагенте.
        Все данные берутся из БД.
        """
        result = {
            'name': counterparty.short_name,
            'full_name': counterparty.full_name or '',
            'inn': f"ИНН {counterparty.tax_id}" if counterparty.tax_id else 'ИНН не указан',
            'legal_address': counterparty.legal_address or 'Юр. адрес не указан',
            'actual_address': counterparty.actual_address or 'Факт. адрес не указан',
        }
        
        if counterparty.bank_details:
            bank = counterparty.bank_details
            bank_info = []
            if bank.get('bank_name'):
                bank_info.append(f"🏦 {bank['bank_name']}")
            if bank.get('account'):
                bank_info.append(f"💰 р/с: {bank['account']}")
            if bank.get('bik'):
                bank_info.append(f"🔢 БИК: {bank['bik']}")
            if bank.get('correspondent_account'):
                bank_info.append(f"🔄 к/с: {bank['correspondent_account']}")
            if bank.get('ogrn'):
                bank_info.append(f"📋 ОГРН: {bank['ogrn']}")
            if bank.get('okato'):
                bank_info.append(f"📍 ОКАТО: {bank['okato']}")
            
            result['bank_details'] = '\n'.join(bank_info)
        else:
            result['bank_details'] = 'Банковские реквизиты не указаны'
        
        return result
    
    @staticmethod
    def format_responsible_persons(persons: List[ResponsiblePerson]) -> Dict[str, List[str]]:
        """
        Группирует ответственных лиц по категориям контактов.
        
        Args:
            persons: Список ответственных лиц из БД
        """
        result = {}
        
        for person in persons:
            if not person.is_active:
                continue
            
            # Определяем основную категорию из массива categories
            main_category = 'general'
            if person.contact_categories and len(person.contact_categories) > 0:
                main_category = person.contact_categories[0]
            
            category_name = FieldManager.CONTACT_CATEGORY_MAP.get(
                main_category, 'Общие вопросы'
            )
            
            if category_name not in result:
                result[category_name] = []
            
            # Формируем строку с информацией о лице
            info = f"{person.person_name}"
            if person.position:
                info += f", {person.position}"
            
            contacts = []
            if person.phone:
                contacts.append(f"тел: {person.phone}")
            if person.email:
                contacts.append(f"email: {person.email}")
            
            if contacts:
                info += f" ({', '.join(contacts)})"
            
            if person.notes:
                info += f"\n    ⚡ {person.notes}"
            
            result[category_name].append(info)
        
        return result
    
    @staticmethod
    def format_phone(phone: Optional[str]) -> str:
        """Форматирует телефонный номер."""
        if not phone:
            return "—"
        return phone
    
    @staticmethod
    def format_email(email: Optional[str]) -> str:
        """Форматирует email."""
        if not email:
            return "—"
        return email
    
    @staticmethod
    def get_available_statuses() -> Dict[str, str]:
        """
        Возвращает словарь доступных статусов помещений.
        В будущем может загружаться из БД.
        """
        return FieldManager.STATUS_MAP.copy()