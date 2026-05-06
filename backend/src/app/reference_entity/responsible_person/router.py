# backend/src/app/reference_entity/responsible_person/router.py
"""
Роутер для работы с ответственными лицами.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.infrastructure.deps import get_db
from src.app.reference_entity.responsible_person.service import (
    get_responsible_persons_by_counterparty,
    get_responsible_person_by_id,
)
from src.app.reference_entity.responsible_person.schemas import ResponsiblePersonSchema
from utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/responsible-persons", tags=["responsible-persons"])


@router.get("/by-counterparty/{counterparty_id}", response_model=List[ResponsiblePersonSchema])
def get_responsible_persons_by_counterparty_endpoint(
    counterparty_id: int,
    db: Session = Depends(get_db)
) -> List[ResponsiblePersonSchema]:
    """
    Получить всех ответственных лиц контрагента.
    
    Args:
        counterparty_id: ID контрагента
    
    Returns:
        Список ответственных лиц
    """
    log.api(f"GET /responsible-persons/by-counterparty/{counterparty_id}")
    return get_responsible_persons_by_counterparty(db, counterparty_id)


@router.get("/{person_id}", response_model=ResponsiblePersonSchema)
def get_responsible_person(
    person_id: int,
    db: Session = Depends(get_db)
) -> ResponsiblePersonSchema:
    """
    Получить ответственное лицо по ID.
    
    Args:
        person_id: ID ответственного лица
    
    Returns:
        ResponsiblePersonSchema
    
    Raises:
        HTTPException 404: если не найдено
    """
    log.api(f"GET /responsible-persons/{person_id}")
    
    person = get_responsible_person_by_id(db, person_id)
    
    if person is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ответственное лицо с ID={person_id} не найдено"
        )
    
    return person