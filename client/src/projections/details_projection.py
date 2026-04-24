# client/src/projections/details_projection.py
"""
Projection для сборки DetailsViewModel из DTO.

Преобразует "сырые" DTO из API в готовые ViewModel для UI.
Использует ReferenceStore для маппинга ID → человекочитаемые значения.

Примечание: Все сущности (комплекс, корпус, этаж, помещение) имеют статус.
- Комплекс и корпус используют BuildingStatus
- Этаж и помещение используют RoomStatus

TECHNICAL DEBT:
    - _format_owner: маппить owner_id → название через репозиторий владельцев
    - _format_floor_type: заменить на справочник типов этажей из ReferenceStore
    - _format_room_type: заменить на справочник типов помещений из ReferenceStore
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from src.data import ReferenceStore
from src.models import (
    BuildingDetailDTO,
    ComplexDetailDTO,
    FloorDetailDTO,
    RoomDetailDTO,
)
from src.shared.time import format_timestamp
from src.view_models.details import DetailsViewModel, HeaderViewModel, InfoGridItem
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsProjection:
    """
    Сборщик ViewModel для панели деталей.

    TECHNICAL DEBT:
        - owner_id → название через репозиторий владельцев
        - физические типы этажей и помещений — через ReferenceStore
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, reference_store: ReferenceStore) -> None:
        """Инициализирует проекцию с хранилищем справочников."""
        log.system("DetailsProjection инициализация")
        self._refs = reference_store
        log.system("DetailsProjection инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def build_complex_details(self, dto: ComplexDetailDTO) -> DetailsViewModel:
        """Собирает ViewModel для комплекса."""
        log.debug(f"Сборка ViewModel для комплекса {dto.id}")

        status_dto = self._refs.building_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        header = HeaderViewModel(
            title=dto.name,
            subtitle="КОМПЛЕКС",
            status_name=status_name,
        )

        grid = [
            InfoGridItem("ID", str(dto.id)),
            InfoGridItem("Название", dto.name),
            InfoGridItem("Адрес", dto.address or "—"),
            InfoGridItem("Владелец", self._format_owner(dto.owner_id)),
            InfoGridItem("Количество корпусов", str(dto.buildings_count)),
            InfoGridItem("Статус", status_name or "—"),
            InfoGridItem("Описание", dto.description or "—"),
            InfoGridItem("Создан", format_timestamp(dto.created_at)),
            InfoGridItem("Обновлён", format_timestamp(dto.updated_at)),
        ]

        return DetailsViewModel(header=header, grid=grid)

    def build_building_details(self, dto: BuildingDetailDTO) -> DetailsViewModel:
        """Собирает ViewModel для корпуса."""
        log.debug(f"Сборка ViewModel для корпуса {dto.id}")

        status_dto = self._refs.building_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        header = HeaderViewModel(
            title=dto.name,
            subtitle="КОРПУС",
            status_name=status_name,
        )

        grid = [
            InfoGridItem("ID", str(dto.id)),
            InfoGridItem("Название", dto.name),
            InfoGridItem("Комплекс ID", str(dto.complex_id)),
            InfoGridItem("Адрес", dto.address or "—"),
            InfoGridItem("Владелец", self._format_owner(dto.owner_id)),
            InfoGridItem("Количество этажей", str(dto.floors_count)),
            InfoGridItem("Статус", status_name or "—"),
            InfoGridItem("Описание", dto.description or "—"),
            InfoGridItem("Создан", format_timestamp(dto.created_at)),
            InfoGridItem("Обновлён", format_timestamp(dto.updated_at)),
        ]

        return DetailsViewModel(header=header, grid=grid)

    def build_floor_details(self, dto: FloorDetailDTO) -> DetailsViewModel:
        """Собирает ViewModel для этажа."""
        log.debug(f"Сборка ViewModel для этажа {dto.id}")

        status_dto = self._refs.room_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        header = HeaderViewModel(
            title=f"Этаж {dto.number}",
            subtitle="ЭТАЖ",
            status_name=status_name,
        )

        grid = [
            InfoGridItem("ID", str(dto.id)),
            InfoGridItem("Номер", str(dto.number)),
            InfoGridItem("Корпус ID", str(dto.building_id)),
            InfoGridItem("Количество помещений", str(dto.rooms_count)),
            InfoGridItem("Статус", status_name or "—"),
            InfoGridItem("Описание", dto.description or "—"),
            InfoGridItem("Тип этажа", self._format_floor_type(dto.physical_type_id)),
            InfoGridItem("Создан", format_timestamp(dto.created_at)),
            InfoGridItem("Обновлён", format_timestamp(dto.updated_at)),
        ]

        if dto.plan_image_url:
            grid.append(InfoGridItem("План этажа", dto.plan_image_url))

        return DetailsViewModel(header=header, grid=grid)

    def build_room_details(self, dto: RoomDetailDTO) -> DetailsViewModel:
        """Собирает ViewModel для помещения."""
        log.debug(f"Сборка ViewModel для помещения {dto.id}")

        status_dto = self._refs.room_statuses.get(dto.status_id)
        status_name = status_dto.name if status_dto else None

        header = HeaderViewModel(
            title=f"Помещение {dto.number}",
            subtitle="ПОМЕЩЕНИЕ",
            status_name=status_name,
        )

        grid = [
            InfoGridItem("ID", str(dto.id)),
            InfoGridItem("Номер", dto.number),
            InfoGridItem("Этаж ID", str(dto.floor_id)),
            InfoGridItem("Площадь", self._format_area(dto.area)),
            InfoGridItem("Тип помещения", self._format_room_type(dto.physical_type_id)),
            InfoGridItem("Статус", status_name or "—"),
            InfoGridItem("Макс. арендаторов", str(dto.max_tenants) if dto.max_tenants else "—"),
            InfoGridItem("Описание", dto.description or "—"),
            InfoGridItem("Создан", format_timestamp(dto.created_at)),
            InfoGridItem("Обновлён", format_timestamp(dto.updated_at)),
        ]

        return DetailsViewModel(header=header, grid=grid)

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _format_owner(self, owner_id: Optional[int]) -> str:
        """
        Форматирует ID владельца.

        TODO: маппить owner_id → название через репозиторий владельцев
        """
        if owner_id is None:
            return "—"
        return f"Владелец #{owner_id}"

    def _format_area(self, area: Optional[float]) -> str:
        """Форматирует площадь с единицей измерения."""
        if area is None:
            return "—"
        return f"{area} м²"

    def _format_floor_type(self, type_id: Optional[int]) -> str:
        """
        Форматирует тип этажа.

        TODO: заменить на справочник типов этажей из ReferenceStore
        """
        if type_id is None:
            return "—"
        types = {1: "Наземный", 2: "Подвал", 3: "Технический", 4: "Чердак"}
        return types.get(type_id, f"Тип {type_id}")

    def _format_room_type(self, type_id: Optional[int]) -> str:
        """
        Форматирует тип помещения.

        TODO: заменить на справочник типов помещений из ReferenceStore
        """
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