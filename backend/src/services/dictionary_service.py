# backend/src/services/dictionary_service.py
"""
Сервисы для работы с dictionary схемой
"""
from sqlmodel import Session, select
from typing import List, Optional

from ..models.dictionary import Counterparty, ResponsiblePerson
from ..schemas.dictionary import CounterpartyDetail, ResponsiblePersonDetail

from utils.logger import get_logger

log = get_logger(__name__)


class DictionaryService:
    """Сервис для работы со справочниками"""
    
    @staticmethod
    def get_counterparties(db: Session, type_id: Optional[int] = None) -> List[Counterparty]:
        """
        Получить список контрагентов
        
        Args:
            db: Сессия БД
            type_id: Фильтр по типу контрагента (опционально)
            
        Returns:
            List[Counterparty]: Список контрагентов
        """
        try:
            query = select(Counterparty)
            if type_id is not None:
                query = query.where(Counterparty.type_id == type_id)
            query = query.order_by(Counterparty.short_name)
            
            result = db.exec(query)
            # Явно преобразуем Sequence в List
            counterparties = list(result.all())
            
            log.debug(f"Загружено {len(counterparties)} контрагентов" + 
                     (f" с type_id={type_id}" if type_id else ""))
            return counterparties
            
        except Exception as e:
            log.error(f"Ошибка в get_counterparties: {e}")
            raise
    
    @staticmethod
    def get_counterparty_detail(db: Session, counterparty_id: int) -> Optional[CounterpartyDetail]:
        """
        Получить детальную информацию о контрагенте
        
        Args:
            db: Сессия БД
            counterparty_id: ID контрагента
            
        Returns:
            Optional[CounterpartyDetail]: Детальная информация или None
        """
        try:
            counterparty = db.get(Counterparty, counterparty_id)
            if not counterparty:
                log.debug(f"Контрагент с ID {counterparty_id} не найден")
                return None
            
            log.debug(f"Загружен контрагент {counterparty_id}: {counterparty.short_name}")
            
            return CounterpartyDetail(
                id=counterparty.id,  # type: ignore
                short_name=counterparty.short_name,
                tax_id=counterparty.tax_id,
                full_name=counterparty.full_name,
                type_id=counterparty.type_id,
                legal_address=counterparty.legal_address,
                actual_address=counterparty.actual_address,
                bank_details=counterparty.bank_details,
                status_code=counterparty.status_code,
                notes=counterparty.notes,
                created_at=counterparty.created_at,
                updated_at=counterparty.updated_at
            )
            
        except Exception as e:
            log.error(f"Ошибка в get_counterparty_detail для ID {counterparty_id}: {e}")
            raise
    
    @staticmethod
    def get_responsible_persons(db: Session, counterparty_id: int) -> List[ResponsiblePerson]:
        """
        Получить список ответственных лиц для контрагента
        
        Args:
            db: Сессия БД
            counterparty_id: ID контрагента
            
        Returns:
            List[ResponsiblePerson]: Список ответственных лиц
        """
        try:
            query = select(ResponsiblePerson).where(
                ResponsiblePerson.counterparty_id == counterparty_id
            ).order_by(ResponsiblePerson.person_name)
            
            result = db.exec(query)
            # Явно преобразуем Sequence в List
            persons = list(result.all())
            
            log.debug(f"Загружено {len(persons)} ответственных лиц для контрагента {counterparty_id}")
            return persons
            
        except Exception as e:
            log.error(f"Ошибка в get_responsible_persons для контрагента {counterparty_id}: {e}")
            raise