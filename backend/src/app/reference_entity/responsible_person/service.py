# backend/src/app/reference_entity/responsible_person/service.py
"""
Сервис для работы с ответственными лицами.
"""

from typing import List, Optional
from sqlmodel import Session, select
from utils.logger import get_logger
from .models import ResponsiblePerson
from .schemas import ResponsiblePersonSchema

log = get_logger(__name__)


def get_responsible_persons_by_counterparty(
    session: Session, 
    counterparty_id: int
) -> List[ResponsiblePersonSchema]:
    """
    Получить всех ответственных лиц контрагента по ID контрагента.
    
    Args:
        session: Сессия БД
        counterparty_id: ID контрагента
    
    Returns:
        Список ответственных лиц
    """
    log.debug(f"get_responsible_persons_by_counterparty: запрос для counterparty_id={counterparty_id}")
    
    stmt = select(ResponsiblePerson).where(
        ResponsiblePerson.counterparty_id == counterparty_id
    ).order_by(ResponsiblePerson.person_name)
    
    result = session.execute(stmt)
    persons = result.scalars().all()
    
    log.info(f"Найдено {len(persons)} ответственных лиц для контрагента {counterparty_id}")
    return [ResponsiblePersonSchema.model_validate(p) for p in persons]


def get_responsible_person_by_id(
    session: Session, 
    person_id: int
) -> Optional[ResponsiblePersonSchema]:
    """
    Получить ответственное лицо по ID.
    
    Args:
        session: Сессия БД
        person_id: ID ответственного лица
    
    Returns:
        ResponsiblePersonSchema или None, если не найден
    """
    log.debug(f"get_responsible_person_by_id: запрос ID={person_id}")
    
    stmt = select(ResponsiblePerson).where(ResponsiblePerson.id == person_id)
    result = session.execute(stmt)
    person = result.scalar_one_or_none()
    
    if person is None:
        log.warning(f"Ответственное лицо с ID={person_id} не найдено")
        return None
    
    log.info(f"Найдено ответственное лицо: ID={person_id}, name={person.person_name}")
    return ResponsiblePersonSchema.model_validate(person)