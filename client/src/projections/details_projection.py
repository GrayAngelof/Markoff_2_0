# client/src/projections/details_projection.py
"""
Projection для сборки данных панели деталей.

Преобразует "сырые" DTO из API в структурированный контракт (IDetailsViewModel).
Использует ReferenceStore для маппинга ID → человекочитаемые значения.

Возвращает объект, реализующий протокол IDetailsViewModel из core.
UI-слой сам решает, как преобразовать его в конкретные ViewModel.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.core.types.protocols import IDetailsViewModel
from src.data import ReferenceStore
from src.models import (
    BuildingDetailDTO,
    ComplexDetailDTO,
    FloorDetailDTO,
    RoomDetailDTO,
)
from src.shared.time import format_timestamp
from utils.logger import get_logger


log = get_logger(__name__)


@dataclass(frozen=True)
class _DetailsViewModelImpl(IDetailsViewModel):
    """
    Внутренняя реализация IDetailsViewModel.
    Используется только внутри проекции, не экспортируется.
    """
    _header_title: str
    _header_subtitle: str
    _header_status_name: Optional[str]
    _grid_items: List[Tuple[str, str]]

    @property
    def header_title(self) -> str:
        return self._header_title

    @property
    def header_subtitle(self) -> str:
        return self._header_subtitle

    @property
    def header_status_name(self) -> Optional[str]:
        return self._header_status_name

    @property
    def grid_items(self) -> List[Tuple[str, str]]:
        return self._grid_items


class DetailsProjection:
    def __init__(self, reference_store: ReferenceStore) -> None:
        log.system("DetailsProjection инициализация")
        self._refs = reference_store
        log.system("DetailsProjection инициализирован")

    def build_complex_details(self, dto: ComplexDetailDTO) -> IDetailsViewModel:
        log.debug(f"Сборка данных для комплекса {dto.id}")
        status_dto = self._refs.building_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        grid: List[Tuple[str, str]] = [
            ("ID", str(dto.id)),
            ("Название", dto.name),
            ("Адрес", dto.address or "—"),
            ("Владелец", self._format_owner(dto.owner_id)),
            ("Количество корпусов", str(dto.buildings_count)),
            ("Статус", status_name or "—"),
            ("Описание", dto.description or "—"),
            ("Создан", format_timestamp(dto.created_at)),
            ("Обновлён", format_timestamp(dto.updated_at)),
        ]

        return _DetailsViewModelImpl(
            _header_title=dto.name,
            _header_subtitle="КОМПЛЕКС",
            _header_status_name=status_name,
            _grid_items=grid,
        )

    def build_building_details(self, dto: BuildingDetailDTO) -> IDetailsViewModel:
        log.debug(f"Сборка данных для корпуса {dto.id}")
        status_dto = self._refs.building_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        grid: List[Tuple[str, str]] = [
            ("ID", str(dto.id)),
            ("Название", dto.name),
            ("Комплекс ID", str(dto.complex_id)),
            ("Адрес", dto.address or "—"),
            ("Владелец", self._format_owner(dto.owner_id)),
            ("Количество этажей", str(dto.floors_count)),
            ("Статус", status_name or "—"),
            ("Описание", dto.description or "—"),
            ("Создан", format_timestamp(dto.created_at)),
            ("Обновлён", format_timestamp(dto.updated_at)),
        ]

        return _DetailsViewModelImpl(
            _header_title=dto.name,
            _header_subtitle="КОРПУС",
            _header_status_name=status_name,
            _grid_items=grid,
        )

    def build_floor_details(self, dto: FloorDetailDTO) -> IDetailsViewModel:
        log.debug(f"Сборка данных для этажа {dto.id}")
        status_dto = self._refs.room_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        grid: List[Tuple[str, str]] = [
            ("ID", str(dto.id)),
            ("Номер", str(dto.number)),
            ("Корпус ID", str(dto.building_id)),
            ("Количество помещений", str(dto.rooms_count)),
            ("Статус", status_name or "—"),
            ("Описание", dto.description or "—"),
            ("Тип этажа", self._format_floor_type(dto.physical_type_id)),
            ("Создан", format_timestamp(dto.created_at)),
            ("Обновлён", format_timestamp(dto.updated_at)),
        ]
        if dto.plan_image_url:
            grid.append(("План этажа", dto.plan_image_url))

        return _DetailsViewModelImpl(
            _header_title=f"Этаж {dto.number}",
            _header_subtitle="ЭТАЖ",
            _header_status_name=status_name,
            _grid_items=grid,
        )

    def build_room_details(self, dto: RoomDetailDTO) -> IDetailsViewModel:
        log.debug(f"Сборка данных для помещения {dto.id}")
        status_dto = self._refs.room_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        grid: List[Tuple[str, str]] = [
            ("ID", str(dto.id)),
            ("Номер", dto.number),
            ("Этаж ID", str(dto.floor_id)),
            ("Площадь", self._format_area(dto.area)),
            ("Тип помещения", self._format_room_type(dto.physical_type_id)),
            ("Статус", status_name or "—"),
            ("Макс. арендаторов", str(dto.max_tenants) if dto.max_tenants else "—"),
            ("Описание", dto.description or "—"),
            ("Создан", format_timestamp(dto.created_at)),
            ("Обновлён", format_timestamp(dto.updated_at)),
        ]

        return _DetailsViewModelImpl(
            _header_title=f"Помещение {dto.number}",
            _header_subtitle="ПОМЕЩЕНИЕ",
            _header_status_name=status_name,
            _grid_items=grid,
        )

    # ---- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ----
    @staticmethod
    def _format_owner(owner_id: Optional[int]) -> str:
        return "—" if owner_id is None else f"Владелец #{owner_id}"

    @staticmethod
    def _format_area(area: Optional[float]) -> str:
        return "—" if area is None else f"{area} м²"

    @staticmethod
    def _format_floor_type(type_id: Optional[int]) -> str:
        if type_id is None:
            return "—"
        types = {1: "Наземный", 2: "Подвал", 3: "Технический", 4: "Чердак"}
        return types.get(type_id, f"Тип {type_id}")

    @staticmethod
    def _format_room_type(type_id: Optional[int]) -> str:
        if type_id is None:
            return "—"
        types = {
            1: "Офисное",
            2: "Складское",
            3: "Торговое",
            4: "Производственное",
            5: "Техническое",
            6: "Коридор",
        }
        return types.get(type_id, f"Тип {type_id}")