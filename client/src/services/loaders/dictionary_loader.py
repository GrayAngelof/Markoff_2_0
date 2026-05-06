# client/src/services/loaders/dictionary_loader.py
"""
Загрузчик справочных данных (статусы, типы).

Тупой исполнитель — только загружает данные.
Не содержит бизнес-логики, не решает, нужно ли загружать.
"""

# ===== ИМПОРТЫ =====
from typing import List

from src.data import EntityGraph
from src.services.api_client import ApiClient
from src.models import (
    BuildingStatusDTO,
    RoomStatusDTO,
    ContractStatusDTO,
    EquipmentStatusDTO,
    PaymentStatusDTO,
    PlacementStatusDTO,
    CounterpartyTypeDTO,
)
from utils.logger import get_logger


log = get_logger(__name__)


class DictionaryLoader:
    """
    Загрузчик справочных данных.

    Отвечает только за:
    - Вызов ApiClient для получения данных
    - Возврат загруженных данных

    НЕ отвечает за:
    - Проверку кэша (это DataLoader)
    - Бизнес-логику (это контроллеры)
    - Форматирование (это UI)
    - Сохранение в граф (это не его ответственность)
    """

    def __init__(self, api: ApiClient, graph: EntityGraph) -> None:
        """
        Инициализирует загрузчик справочников.

        Args:
            api: API клиент для запросов
            graph: Граф сущностей (пока не используется, но может понадобиться)
        """
        log.system("DictionaryLoader инициализация")
        self._api = api
        self._graph = graph
        log.system("DictionaryLoader инициализирован")

    # ---- СТАТУСЫ ----
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

    def load_contract_statuses(self) -> List[ContractStatusDTO]:
        """Загрузить справочник статусов договоров."""
        log.info("Загрузка статусов договоров...")
        result = self._api.get_contract_statuses()
        log.success(f"Загружено {len(result)} статусов договоров")
        return result

    def load_equipment_statuses(self) -> List[EquipmentStatusDTO]:
        """Загрузить справочник статусов оборудования."""
        log.info("Загрузка статусов оборудования...")
        result = self._api.get_equipment_statuses()
        log.success(f"Загружено {len(result)} статусов оборудования")
        return result

    def load_payment_statuses(self) -> List[PaymentStatusDTO]:
        """Загрузить справочник статусов платежей."""
        log.info("Загрузка статусов платежей...")
        result = self._api.get_payment_statuses()
        log.success(f"Загружено {len(result)} статусов платежей")
        return result

    def load_placement_statuses(self) -> List[PlacementStatusDTO]:
        """Загрузить справочник статусов размещения."""
        log.info("Загрузка статусов размещения...")
        result = self._api.get_placement_statuses()
        log.success(f"Загружено {len(result)} статусов размещения")
        return result

    # ---- ТИПЫ ----
    def load_counterparty_types(self) -> List[CounterpartyTypeDTO]:
        """Загрузить справочник типов контрагентов."""
        log.info("Загрузка типов контрагентов...")
        result = self._api.get_counterparty_types()
        log.success(f"Загружено {len(result)} типов контрагентов")
        return result