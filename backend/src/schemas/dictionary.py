# backend/src/schemas/dictionary.py
"""
Pydantic схемы для словарей и справочников
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


# ===== Counterparty (контрагент) =====

class CounterpartyBase(BaseModel):
    """Базовая информация о контрагенте"""
    id: int
    short_name: str
    tax_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class CounterpartyDetail(CounterpartyBase):
    """Детальная информация о контрагенте"""
    full_name: Optional[str] = None
    type_id: Optional[int] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    bank_details: Optional[dict] = None
    status_code: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CounterpartyWithOwner(CounterpartyBase):
    """Контрагент с информацией о владельце (для вложенных ответов)"""
    full_name: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    bank_details: Optional[dict] = None


# ===== Responsible Person (ответственное лицо) =====

class ResponsiblePersonBase(BaseModel):
    """Базовая информация об ответственном лице"""
    id: int
    person_name: str
    position: Optional[str] = None
    role_code: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ResponsiblePersonDetail(ResponsiblePersonBase):
    """Детальная информация об ответственном лице"""
    counterparty_id: int
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_categories: Optional[List[str]] = None
    is_public_contact: bool
    is_active: bool
    notes: Optional[str] = None
    hire_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime