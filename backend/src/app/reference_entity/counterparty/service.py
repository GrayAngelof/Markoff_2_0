# backend/src/app/reference_entity/counterparty/service.py
"""
Сервис для работы с контрагентами (reference entity).
"""

from typing import Optional
from sqlmodel import Session, select
from utils.logger import get_logger
from .models import Counterparty
from .schemas import CounterpartySchema

log = get_logger(__name__)


def get_counterparty_by_id(session: Session, counterparty_id: int) -> Optional[CounterpartySchema]:
    """
    Получить контрагента по ID.
    
    Args:
        session: Сессия БД
        counterparty_id: ID контрагента
    
    Returns:
        CounterpartySchema или None, если не найден
    """
    log.debug(f"get_counterparty_by_id: запрос ID={counterparty_id}")
    
    stmt = select(Counterparty).where(Counterparty.id == counterparty_id)
    result = session.execute(stmt)
    counterparty = result.scalar_one_or_none()
    
    if counterparty is None:
        log.warning(f"Контрагент с ID={counterparty_id} не найден")
        return None
    
    log.info(f"Найден контрагент: ID={counterparty_id}, short_name={counterparty.short_name}")
    return CounterpartySchema.model_validate(counterparty)