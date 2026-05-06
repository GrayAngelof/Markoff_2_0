# backend/src/app/reference_data/schemas/payment_status.py
"""
Pydantic схема для PaymentStatus (справочник статусов платежей).
"""

from pydantic import ConfigDict
from .base import ReferenceSchema


class PaymentStatusSchema(ReferenceSchema):
    """Статус платежа (полный ответ API)."""
    
    is_initial: bool | None = None
    is_success: bool | None = None

    model_config = ConfigDict(from_attributes=True)