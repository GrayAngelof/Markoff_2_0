# client/src/models/counterparty.py
"""
Модель данных для контрагента (юридического лица).
Чистый DTO — только данные от API, никакой UI-логики.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .base import BaseDTO
from .mixins import DateTimeMixin


@dataclass(frozen=True, kw_only=True)
class Counterparty(BaseDTO, DateTimeMixin):
    """
    Модель контрагента (юридического лица) — DTO.
    
    Соответствует ответам API для контрагентов.
    Содержит ТОЛЬКО данные, никаких методов форматирования или UI-логики.
    
    Поля:
        id: уникальный идентификатор (из BaseDTO)
        created_at: дата создания (из DateTimeMixin)
        updated_at: дата обновления (из DateTimeMixin)
        short_name: краткое название (для отображения)
        full_name: полное юридическое название
        type_id: тип контрагента (ссылка на справочник)
        tax_id: ИНН
        legal_address: юридический адрес
        actual_address: фактический адрес
        bank_details: банковские реквизиты (JSON-объект)
        status_code: статус ('active', 'suspended', 'blocked')
        notes: примечания
    """
    
    # Специфичные для контрагента поля
    short_name: str
    full_name: Optional[str] = None
    type_id: Optional[int] = None
    tax_id: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None
    status_code: str = 'active'
    notes: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Counterparty':
        """
        Создаёт объект Counterparty из словаря (ответ API).
        
        Args:
            data: словарь с данными от API
                Пример: {
                    "id": 42,
                    "short_name": "ООО Ромашка",
                    "full_name": "ООО Ромашка",
                    "tax_id": "1234567890",
                    "status_code": "active"
                }
            
        Returns:
            Counterparty: объект контрагента
            
        Raises:
            ValueError: если отсутствует обязательное поле 'id' или 'short_name'
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")
        
        if 'short_name' not in data:
            raise ValueError("Отсутствует обязательное поле 'short_name' в ответе API")
        
        return cls(
            id=data['id'],
            short_name=data['short_name'],
            full_name=data.get('full_name'),
            type_id=data.get('type_id'),
            tax_id=data.get('tax_id'),
            legal_address=data.get('legal_address'),
            actual_address=data.get('actual_address'),
            bank_details=data.get('bank_details'),
            status_code=data.get('status_code', 'active'),
            notes=data.get('notes'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at'))
        )