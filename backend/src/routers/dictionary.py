# backend/src/routers/dictionary.py
"""
Роутер для работы со словарями
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional

from ..core.deps import get_db
from ..models.dictionary import Counterparty, ResponsiblePerson
from ..schemas.dictionary import CounterpartyDetail, ResponsiblePersonDetail

from utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/dictionary", tags=["dictionary"])


# ===== Counterparty endpoints =====

@router.get("/counterparties", response_model=List[CounterpartyDetail])
async def read_counterparties(
    type_id: Optional[int] = Query(None, description="Filter by counterparty type"),
    db: Session = Depends(get_db)
):
    """Получить список контрагентов"""
    try:
        query = select(Counterparty)
        if type_id:
            query = query.where(Counterparty.type_id == type_id)
        query = query.order_by(Counterparty.short_name)
        
        result = db.exec(query)
        counterparties = result.all()
        
        log.info(f"Загружено {len(counterparties)} контрагентов")
        return counterparties
        
    except Exception as e:
        log.error(f"Ошибка загрузки контрагентов: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/counterparties/{counterparty_id}", response_model=CounterpartyDetail)
async def read_counterparty(
    counterparty_id: int,
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о контрагенте"""
    try:
        counterparty = db.get(Counterparty, counterparty_id)
        if not counterparty:
            raise HTTPException(status_code=404, detail="Counterparty not found")
        
        log.info(f"Загружен контрагент {counterparty_id}")
        return counterparty
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Ошибка загрузки контрагента {counterparty_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/counterparties/{counterparty_id}/persons", response_model=List[ResponsiblePersonDetail])
async def read_responsible_persons(
    counterparty_id: int,
    db: Session = Depends(get_db)
):
    """Получить список ответственных лиц для контрагента"""
    try:
        query = select(ResponsiblePerson).where(
            ResponsiblePerson.counterparty_id == counterparty_id
        ).order_by(ResponsiblePerson.person_name)
        
        result = db.exec(query)
        persons = result.all()
        
        log.info(f"Загружено {len(persons)} ответственных лиц для контрагента {counterparty_id}")
        return persons
        
    except Exception as e:
        log.error(f"Ошибка загрузки ответственных лиц: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))