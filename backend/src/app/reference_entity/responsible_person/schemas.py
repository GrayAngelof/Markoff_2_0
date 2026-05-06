# backend/src/app/reference_entity/responsible_person/schemas.py
"""
Pydantic схемы для ResponsiblePerson.
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ResponsiblePersonSchema(BaseModel):
    """Ответственное лицо (полный ответ API)."""
    
    id: int
    counterparty_id: int
    person_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    role_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contact_categories: Optional[List[str]] = None
    is_public_contact: bool
    is_active: bool
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)