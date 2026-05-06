# backend/src/app/reference_entity/counterparty/schemas.py
"""
Pydantic схемы для Counterparty (контрагент).
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class CounterpartySchema(BaseModel):
    """Контрагент (полный ответ API)."""
    
    id: int
    short_name: str
    full_name: str
    tax_id: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None
    status_code: Optional[str] = None
    notes: Optional[str] = None
    type_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)