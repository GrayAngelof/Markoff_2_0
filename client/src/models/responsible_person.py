# client/src/models/responsible_person.py
"""
Модель данных для ответственного лица (контактного лица контрагента).
Чистый DTO — только данные от API, никакой UI-логики.
"""
from dataclasses import dataclass
from typing import Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


@dataclass(frozen=True, kw_only=True)
class ResponsiblePerson(BaseDTO, DateTimeMixin):
    """
    Модель ответственного лица (DTO).
    
    Соответствует ответам API для ответственных лиц.
    Содержит ТОЛЬКО данные, никаких методов форматирования или UI-логики.
    
    Поля:
        id: уникальный идентификатор (из BaseDTO)
        created_at: дата создания (из DateTimeMixin)
        updated_at: дата обновления (из DateTimeMixin)
        counterparty_id: ID контрагента
        person_name: ФИО
        position: должность
        role_code: код роли (из справочника ролей)
        phone: телефон
        email: email
        contact_categories: категории контактов (строка с разделителями)
        is_public_contact: публичный ли контакт
        is_active: активен ли
        notes: примечания
    """
    
    # Специфичные для ответственного лица поля
    counterparty_id: int
    person_name: str
    position: Optional[str] = None
    role_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_categories: Optional[str] = None  # хранится как строка, например "legal,financial"
    is_public_contact: bool = False
    is_active: bool = True
    notes: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ResponsiblePerson':
        """
        Создаёт объект ResponsiblePerson из словаря (ответ API).
        
        Args:
            data: словарь с данными от API
                Пример: {
                    "id": 1,
                    "counterparty_id": 42,
                    "person_name": "Иванов Иван Иванович",
                    "position": "Генеральный директор",
                    "phone": "+7 (495) 123-45-67",
                    "email": "ivanov@example.com",
                    "contact_categories": "legal,financial",
                    "is_public_contact": True,
                    "is_active": True
                }
            
        Returns:
            ResponsiblePerson: объект ответственного лица
            
        Raises:
            ValueError: если отсутствует обязательное поле
        """
        if 'id' not in data:
            raise ValueError("Отсутствует обязательное поле 'id' в ответе API")
        
        if 'counterparty_id' not in data:
            raise ValueError("Отсутствует обязательное поле 'counterparty_id' в ответе API")
        
        if 'person_name' not in data:
            raise ValueError("Отсутствует обязательное поле 'person_name' в ответе API")
        
        # Обработка contact_categories: API может отдавать как строку или как список
        contact_categories = data.get('contact_categories')
        if isinstance(contact_categories, list):
            # Если пришел список, превращаем в строку
            contact_categories = ','.join(contact_categories) if contact_categories else None
        
        return cls(
            id=data['id'],
            counterparty_id=data['counterparty_id'],
            person_name=data['person_name'],
            position=data.get('position'),
            role_code=data.get('role_code'),
            phone=data.get('phone'),
            email=data.get('email'),
            contact_categories=contact_categories,
            is_public_contact=data.get('is_public_contact', False),
            is_active=data.get('is_active', True),
            notes=data.get('notes'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at'))
        )