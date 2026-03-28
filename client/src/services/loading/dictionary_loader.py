# client/src/services/loading/dictionary_loader.py
"""
Загрузчик справочных данных (контрагенты, ответственные лица).

Тупой исполнитель — только загружает и сохраняет в граф.
Не содержит бизнес-логики, не решает, нужно ли загружать.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional

from src.core.types.nodes import NodeID
from src.data import EntityGraph
from src.models import Counterparty, ResponsiblePerson
from src.services.api_client import ApiClient
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
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

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, api: ApiClient, graph: EntityGraph) -> None:
        """Инициализирует загрузчик справочников."""
        self._api = api
        self._graph = graph
        log.system("DictionaryLoader инициализирован")

    # ---- ЗАГРУЗКА ДАННЫХ ----
    def load_counterparty(self, counterparty_id: NodeID) -> Optional[Counterparty]:
        """
        Загружает контрагента по ID.

        Returns:
            None если контрагент не найден
        """
        log.api(f"Загрузка контрагента {counterparty_id}")

        data = self._api.get_counterparty(counterparty_id)
        if data:
            self._graph.add_or_update(data)
            log.data(f"Контрагент {counterparty_id} загружен и сохранён")
        else:
            log.warning(f"Контрагент {counterparty_id} не найден")

        return data

    def load_responsible_persons(self, counterparty_id: NodeID) -> List[ResponsiblePerson]:
        """
        Загружает список ответственных лиц для контрагента.

        Returns:
            Список ответственных лиц (может быть пустым)
        """
        log.api(f"Загрузка ответственных лиц для контрагента {counterparty_id}")

        data = self._api.get_responsible_persons(counterparty_id)

        for person in data:
            self._graph.add_or_update(person)

        if data:
            log.data(f"Загружено {len(data)} ответственных лиц для контрагента {counterparty_id}")
        else:
            log.debug(f"Нет ответственных лиц для контрагента {counterparty_id}")

        return data