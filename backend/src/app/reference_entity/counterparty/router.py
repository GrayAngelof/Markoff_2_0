# backend/src/app/reference_entity/counterparty/router.py
"""
Роутер для работы с контрагентами (reference entity).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.infrastructure.deps import get_db
from src.app.reference_entity.counterparty.service import get_counterparty_by_id
from src.app.reference_entity.counterparty.schemas import CounterpartySchema
from utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/counterparties", tags=["counterparties"])


@router.get("/{counterparty_id}", response_model=CounterpartySchema)
def get_counterparty(
    counterparty_id: int,
    db: Session = Depends(get_db)
) -> CounterpartySchema:
    """
    Получить контрагента по ID.
    
    Args:
        counterparty_id: ID контрагента
    
    Returns:
        CounterpartySchema с полными данными
    
    Raises:
        HTTPException 404: если контрагент не найден
    """
    log.api(f"GET /counterparties/{counterparty_id}")
    
    counterparty = get_counterparty_by_id(db, counterparty_id)
    
    if counterparty is None:
        raise HTTPException(
            status_code=404,
            detail=f"Контрагент с ID={counterparty_id} не найден"
        )
    
    return counterparty