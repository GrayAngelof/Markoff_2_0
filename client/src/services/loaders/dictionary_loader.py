# client/src/services/loaders/dictionary_loader.py
"""
Загрузчик справочных данных (контрагенты, ответственные лица и пр. ).

Тупой исполнитель — только загружает и сохраняет в граф.
Не содержит бизнес-логики, не решает, нужно ли загружать.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional

from src.core.types.nodes import NodeID
from src.data import EntityGraph
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