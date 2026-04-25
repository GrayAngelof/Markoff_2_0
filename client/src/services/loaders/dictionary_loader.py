# client/src/services/loaders/dictionary_loader.py
"""
Загрузчик справочных данных (контрагенты, ответственные лица и пр. ).

Тупой исполнитель — только загружает и сохраняет в граф.
Не содержит бизнес-логики, не решает, нужно ли загружать.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional

from src.data import EntityGraph
from src.services.api_client import ApiClient
from src.models import BuildingStatusDTO, RoomStatusDTO
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
        log.system("DictionaryLoader инициализация")
        self._api = api
        self._graph = graph
        log.system("DictionaryLoader инициализирован")

    # ---- ЗАГРУЗКА ДАННЫХ ----
    def load_building_statuses(self) -> List[BuildingStatusDTO]:
        """Загрузить справочник статусов зданий."""
        log.info("Загрузка статусов зданий...")
        result = self._api.get_building_statuses()
        log.success(f"Загружено {len(result)} статусов зданий")
        return result
    
    def load_room_statuses(self) -> List[RoomStatusDTO]:
        """Загрузить справочник статусов помещений."""
        log.info("Загрузка статусов помещений...")
        result = self._api.get_room_statuses()
        log.success(f"Загружено {len(result)} статусов помещений")
        return result