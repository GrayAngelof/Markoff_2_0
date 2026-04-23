# backend/src/routers/dictionary.py
"""
Роутер для работы со словарями
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional

from ..core.deps import get_db
from ..services.dictionary_service import DictionaryService
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
        # Используем класс напрямую
        counterparties = DictionaryService.get_counterparties(db, type_id)
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
        counterparty = DictionaryService.get_counterparty_detail(db, counterparty_id)
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
        persons = DictionaryService.get_responsible_persons(db, counterparty_id)
        log.info(f"Загружено {len(persons)} ответственных лиц для контрагента {counterparty_id}")
        return persons
        
    except Exception as e:
        log.error(f"Ошибка загрузки ответственных лиц: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))