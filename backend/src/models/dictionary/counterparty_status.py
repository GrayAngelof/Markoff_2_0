# backend/src/models/dictionary/counterparty_status.py
"""
Модель CounterpartyStatus для таблицы dictionary.counterparty_statuses
Представляет статус контрагента (активен, приостановлен, должник и т.д.)
"""
from __future__ import annotations  # <-- ДОБАВЛЕНО

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .counterparty import Counterparty

class CounterpartyStatus(SQLModel, table=True):
    """
    Модель статуса контрагента (таблица dictionary.counterparty_statuses)
    
    Связи:
    - has_many: Counterparty (один ко многим)
    """
    
    __tablename__ = "counterparty_statuses"  # type: ignore
    __table_args__ = {"schema": "dictionary"}
    
    # Первичный ключ
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Код статуса (active, suspended, debtor, contract_terminated, archived)
    code: str = Field(nullable=False, unique=True)
    
    # Название для отображения
    name: str = Field(nullable=False)
    
    # Описание
    description: Optional[str] = Field(default=None)
    
    # Можно ли установить при создании
    is_initial: bool = Field(default=False)
    
    # Порядок отображения
    display_order: int = Field(default=0)
    
    # Метаданные
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    
    # Relationships
    counterparties: List["Counterparty"] = Relationship(back_populates="status")
    
    class Config:
        from_attributes = True