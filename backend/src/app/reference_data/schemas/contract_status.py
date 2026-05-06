# backend/src/app/reference_data/schemas/contract_status.py
"""
Pydantic схема для ContractStatus (справочник статусов договоров).
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ContractStatusSchema(BaseModel):
    """Статус договора (полный ответ API)."""
    
    id: int
    code: str
    name: str
    description: str | None = None
    display_order: int
    created_at: datetime
    updated_at: datetime
    is_initial: bool | None = None
    is_terminal: bool | None = None

    model_config = ConfigDict(from_attributes=True)