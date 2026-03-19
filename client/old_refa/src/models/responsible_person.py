# client/src/models/responsible_person.py
"""
Модель данных для ответственного лица (контактного лица контрагента).
Соответствует таблице dictionary.responsible_persons в БД.
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ResponsiblePerson:
    """
    Модель ответственного лица.
    
    Поля:
    - id: уникальный идентификатор
    - counterparty_id: ID контрагента
    - person_name: ФИО
    - position: должность
    - role_code: код роли (из role_catalog)
    - phone: телефон
    - email: email
    - contact_categories: категории контактов (legal, financial, etc.)
    - is_public_contact: публичный ли контакт
    - is_active: активен ли
    - notes: примечания
    """
    
    id: int
    counterparty_id: int
    person_name: str
    position: Optional[str] = None
    role_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_categories: Optional[str] = None
    is_public_contact: bool = False
    is_active: bool = True
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ResponsiblePerson':
        """Создаёт объект ResponsiblePerson из словаря (ответ API)"""
        return cls(
            id=data['id'],
            counterparty_id=data['counterparty_id'],
            person_name=data['person_name'],
            position=data.get('position'),
            role_code=data.get('role_code'),
            phone=data.get('phone'),
            email=data.get('email'),
            contact_categories=data.get('contact_categories', []),
            is_public_contact=data.get('is_public_contact', False),
            is_active=data.get('is_active', True),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        return f"{self.person_name} ({self.position})"
    
    def get_contact_info(self) -> str:
        """Возвращает строку с контактной информацией"""
        parts = []
        if self.phone:
            parts.append(f"тел: {self.phone}")
        if self.email:
            parts.append(f"email: {self.email}")
        return ", ".join(parts) if parts else "нет контактов"