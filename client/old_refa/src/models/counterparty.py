# client/src/models/counterparty.py
"""
Модель данных для контрагента (юридического лица).
Соответствует таблице dictionary.counterparties в БД.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class Counterparty:
    """
    Модель контрагента (юридического лица).
    
    Поля:
    - id: уникальный идентификатор
    - short_name: краткое название
    - full_name: полное юридическое название
    - type_id: тип контрагента (ссылка на справочник)
    - tax_id: ИНН
    - legal_address: юридический адрес
    - actual_address: фактический адрес
    - bank_details: банковские реквизиты (JSON)
    - status_code: статус (active, suspended, etc.)
    - notes: примечания
    - created_at: дата создания
    - updated_at: дата обновления
    """
    
    id: int
    short_name: str
    full_name: Optional[str] = None
    type_id: Optional[int] = None
    tax_id: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None
    status_code: str = 'active'
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Counterparty':
        """Создаёт объект Counterparty из словаря (ответ API)"""
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
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Строковое представление для отображения"""
        return self.short_name
    
    def __repr__(self) -> str:
        return f"Counterparty(id={self.id}, name='{self.short_name}', inn={self.tax_id})"