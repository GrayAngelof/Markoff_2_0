"""
ReferenceStore — фасад для доступа к справочным данным.

Единая точка входа для всех read-only справочников.
Хранит все реестры и управляет их инициализацией.

Используется только в Projections для маппинга ID → DTO.
Не содержит бизнес-логики, только данные.

Пример:
    store = ReferenceStore(
        building_loader=api_client.get_building_statuses,
        room_loader=api_client.get_room_statuses,
        contract_loader=api_client.get_contract_statuses,
        equipment_loader=api_client.get_equipment_statuses,
        payment_loader=api_client.get_payment_statuses,
        placement_loader=api_client.get_placement_statuses,
        counterparty_type_loader=api_client.get_counterparty_types,
    )
    store.warmup()
    
    status = store.building_statuses.get(1)
    name = status.name if status else None
"""

# ===== ИМПОРТЫ =====
from typing import Callable, List

from src.data.reference.building_status_registry import BuildingStatusRegistry
from src.data.reference.room_status_registry import RoomStatusRegistry
from src.data.reference.contract_status_registry import ContractStatusRegistry
from src.data.reference.equipment_status_registry import EquipmentStatusRegistry
from src.data.reference.payment_status_registry import PaymentStatusRegistry
from src.data.reference.placement_status_registry import PlacementStatusRegistry
from src.data.reference.counterparty_type_registry import CounterpartyTypeRegistry

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


class ReferenceStore:
    """Фасад для доступа к справочным данным."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        building_loader: Callable[[], List[BuildingStatusDTO]],
        room_loader: Callable[[], List[RoomStatusDTO]],
        contract_loader: Callable[[], List[ContractStatusDTO]],
        equipment_loader: Callable[[], List[EquipmentStatusDTO]],
        payment_loader: Callable[[], List[PaymentStatusDTO]],
        placement_loader: Callable[[], List[PlacementStatusDTO]],
        counterparty_type_loader: Callable[[], List[CounterpartyTypeDTO]],
    ) -> None:
        """
        Инициализирует фасад (без загрузки данных).

        Args:
            building_loader: Функция для загрузки статусов зданий
            room_loader: Функция для загрузки статусов помещений
            contract_loader: Функция для загрузки статусов договоров
            equipment_loader: Функция для загрузки статусов оборудования
            payment_loader: Функция для загрузки статусов платежей
            placement_loader: Функция для загрузки статусов размещения
            counterparty_type_loader: Функция для загрузки типов контрагентов
        """
        log.system("ReferenceStore инициализация")

        self._building_statuses = BuildingStatusRegistry(building_loader)
        self._room_statuses = RoomStatusRegistry(room_loader)
        self._contract_statuses = ContractStatusRegistry(contract_loader)
        self._equipment_statuses = EquipmentStatusRegistry(equipment_loader)
        self._payment_statuses = PaymentStatusRegistry(payment_loader)
        self._placement_statuses = PlacementStatusRegistry(placement_loader)
        self._counterparty_types = CounterpartyTypeRegistry(counterparty_type_loader)

        log.system("ReferenceStore инициализирован (данные не загружены)")

    def warmup(self) -> None:
        """Загружает все справочники. Вызывается один раз при старте."""
        log.info("Загрузка справочников ReferenceStore...")

        self._building_statuses.warmup()
        self._room_statuses.warmup()
        self._contract_statuses.warmup()
        self._equipment_statuses.warmup()
        self._payment_statuses.warmup()
        self._placement_statuses.warmup()
        self._counterparty_types.warmup()

        log.success("Все справочники загружены")

    def is_ready(self) -> bool:
        """Проверяет, загружены ли все справочники."""
        return (
            self._building_statuses.is_ready()
            and self._room_statuses.is_ready()
            and self._contract_statuses.is_ready()
            and self._equipment_statuses.is_ready()
            and self._payment_statuses.is_ready()
            and self._placement_statuses.is_ready()
            and self._counterparty_types.is_ready()
        )

    # ---- ПУБЛИЧНЫЕ АКСЕССОРЫ (READ-ONLY) ----
    @property
    def building_statuses(self) -> BuildingStatusRegistry:
        """Возвращает реестр статусов зданий."""
        return self._building_statuses

    @property
    def room_statuses(self) -> RoomStatusRegistry:
        """Возвращает реестр статусов помещений."""
        return self._room_statuses

    @property
    def contract_statuses(self) -> ContractStatusRegistry:
        """Возвращает реестр статусов договоров."""
        return self._contract_statuses

    @property
    def equipment_statuses(self) -> EquipmentStatusRegistry:
        """Возвращает реестр статусов оборудования."""
        return self._equipment_statuses

    @property
    def payment_statuses(self) -> PaymentStatusRegistry:
        """Возвращает реестр статусов платежей."""
        return self._payment_statuses

    @property
    def placement_statuses(self) -> PlacementStatusRegistry:
        """Возвращает реестр статусов размещения."""
        return self._placement_statuses

    @property
    def counterparty_types(self) -> CounterpartyTypeRegistry:
        """Возвращает реестр типов контрагентов."""
        return self._counterparty_types