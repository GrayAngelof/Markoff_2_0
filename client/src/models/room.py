# client/src/models/room.py
"""
Модели данных для помещения на стороне клиента.

Чистые DTO — только данные от API, никакой UI-логики.
- RoomTreeDTO: минимальные поля для дерева (RoomTreeResponse)
- RoomDetailDTO: полные данные для панели деталей (RoomDetailResponse)

Правило: DTO = строгий контракт. Обязательные поля берутся через [], а не .get().
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import ClassVar, Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== TREE DTO (минимальные данные для дерева) =====
@dataclass(frozen=True, kw_only=True)
class RoomTreeDTO(BaseDTO):
    """
    DTO для отображения помещения в дереве.
    Соответствует RoomTreeResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "room"
    IS_DETAIL: ClassVar[bool] = False

    number: str
    floor_id: int
    area: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RoomTreeDTO':
        """
        Создаёт RoomTreeDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id', 'number' или 'floor_id'
            ValueError: Если 'area' имеет некорректный тип
        """
        data_id = data["id"]
        number = data["number"]
        floor_id = data["floor_id"]

        area_raw = data.get('area')
        try:
            area = float(area_raw) if area_raw is not None else None
        except (TypeError, ValueError):
            area = None

        return cls(
            id=data_id,
            number=number,
            floor_id=floor_id,
            area=area,
        )


# ===== DETAIL DTO (полные данные для панели) =====
@dataclass(frozen=True, kw_only=True)
class RoomDetailDTO(BaseDTO, DateTimeMixin):
    """
    DTO для отображения детальной информации о помещении.
    Соответствует RoomDetailResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "room"
    IS_DETAIL: ClassVar[bool] = True

    number: str
    floor_id: int
    area: Optional[float] = None
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    max_tenants: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RoomDetailDTO':
        """
        Создаёт RoomDetailDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id', 'number' или 'floor_id'
            ValueError: Если 'area' или 'max_tenants' имеют некорректный тип
        """
        # Строгий контракт — обязательные поля через []
        data_id = data["id"]
        number = data["number"]
        floor_id = data["floor_id"]

        # Опциональные поля через get() с защитой
        area_raw = data.get('area')
        try:
            area = float(area_raw) if area_raw is not None else None
        except (TypeError, ValueError):
            area = None

        max_tenants_raw = data.get('max_tenants')
        try:
            max_tenants = int(max_tenants_raw) if max_tenants_raw is not None else None
        except (TypeError, ValueError):
            max_tenants = None

        return cls(
            id=data_id,
            number=number,
            floor_id=floor_id,
            area=area,
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            status_id=data.get('status_id'),
            max_tenants=max_tenants,
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )