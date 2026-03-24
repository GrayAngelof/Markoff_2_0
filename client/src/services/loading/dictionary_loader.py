# client/src/services/loading/dictionary_loader.py
"""
Загрузчик справочных данных (контрагенты, ответственные лица).

Тупой исполнитель — только загружает и сохраняет в граф.
Не содержит бизнес-логики, не решает, нужно ли загружать.
"""

from typing import List, Optional

from src.core.types.nodes import NodeID 
from src.models import Counterparty, ResponsiblePerson
from src.services.api_client import ApiClient
from src.data import EntityGraph
from utils.logger import get_logger

log = get_logger(__name__)


class DictionaryLoader:
    """
    Загрузчик справочных данных.
    
    Отвечает только за:
    - Вызов ApiClient для получения данных
    - Сохранение данных в EntityGraph
    - Возврат загруженных данных
    
    НЕ отвечает за:
    - Проверку кэша (это DataLoader)
    - Бизнес-логику (это контроллеры)
    - Форматирование (это UI)
    """
    
    def __init__(self, api: ApiClient, graph: EntityGraph):
        """
        Инициализирует загрузчик справочников.
        
        Args:
            api: HTTP клиент
            graph: Граф сущностей для сохранения
        """
        self._api = api
        self._graph = graph
        log.debug("DictionaryLoader initialized")
    
    def load_counterparty(self, counterparty_id: NodeID) -> Optional[Counterparty]:
        """
        Загружает контрагента по ID.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            Optional[Counterparty]: Контрагент или None, если не найден
        """
        log.info(f"Loading counterparty {counterparty_id}")
        
        data = self._api.get_counterparty(counterparty_id)
        if data:
            self._graph.add_or_update(data)
            log.success(f"Counterparty {counterparty_id} loaded and saved to graph")
        else:
            log.warning(f"Counterparty {counterparty_id} not found")
        
        return data
    
    def load_responsible_persons(self, counterparty_id: NodeID) -> List[ResponsiblePerson]:
        """
        Загружает список ответственных лиц для контрагента.
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            List[ResponsiblePerson]: Список ответственных лиц (может быть пустым)
        """
        log.info(f"Loading responsible persons for counterparty {counterparty_id}")
        
        data = self._api.get_responsible_persons(counterparty_id)
        
        for person in data:
            self._graph.add_or_update(person)
        
        if data:
            log.success(f"Loaded {len(data)} responsible persons for counterparty {counterparty_id}")
        else:
            log.debug(f"No responsible persons for counterparty {counterparty_id}")
        
        return data