# backend/src/models/dictionary/counterparty.py
"""
Модель Counterparty для таблицы dictionary.counterparties
Представляет контрагента (юридическое лицо)
"""
from __future__ import annotations  # <-- ДОБАВЛЕНО

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import JSON

if TYPE_CHECKING:
    from .counterparty_status import CounterpartyStatus
    from .counterparty_type import CounterpartyType
    from .responsible_person import ResponsiblePerson
    from ..physical.complex import Complex
    from ..physical.building import Building

class Counterparty(SQLModel, table=True):
    """
    Модель контрагента (таблица dictionary.counterparties)
    
    Связи:
    - belongs_to: CounterpartyStatus (по status_code)
    - belongs_to: CounterpartyType (по type_id)
    - has_many: ResponsiblePerson (один ко многим)
    - has_many: Complex (как владелец)
    - has_many: Building (как владелец)
    """
    
    __tablename__ = "counterparties"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Тип контрагента (ссылка на counterparty_types)
    type_id: Optional[int] = Field(default=None, foreign_key="dictionary.counterparty_types.id")
    
    # Основные поля
    short_name: str = Field(nullable=False)
    full_name: Optional[str] = Field(default=None)
    tax_id: Optional[str] = Field(default=None)  # ИНН
    
    # Адреса
    legal_address: Optional[str] = Field(default=None)
    actual_address: Optional[str] = Field(default=None)
    
    # Банковские реквизиты (JSON)
    bank_details: Optional[dict] = Field(default=None, sa_type=JSON)
    
    # Статус (ссылка на counterparty_statuses)
    status_code: str = Field(default="active", foreign_key="dictionary.counterparty_statuses.code")
    
    # Метаданные
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    status: Optional["CounterpartyStatus"] = Relationship(back_populates="counterparties")
    type: Optional["CounterpartyType"] = Relationship(back_populates="counterparties")
    responsible_persons: List["ResponsiblePerson"] = Relationship(back_populates="counterparty")
    complexes: List["Complex"] = Relationship(back_populates="owner")
    buildings: List["Building"] = Relationship(back_populates="owner")
    
    class Config:
        from_attributes = True