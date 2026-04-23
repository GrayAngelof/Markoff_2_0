# client/src/models/floor.py
"""
Модели данных для этажа на стороне клиента.

Чистые DTO — только данные от API, никакой UI-логики.
- FloorTreeDTO: минимальные поля для дерева (FloorTreeResponse)
- FloorDetailDTO: полные данные для панели деталей (FloorDetailResponse)

Правило: DTO = строгий контракт. Обязательные поля берутся через [], а не .get().
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import ClassVar, Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== TREE DTO (минимальные данные для дерева) =====
@dataclass(frozen=True, kw_only=True)
class FloorTreeDTO(BaseDTO):
    """
    DTO для отображения этажа в дереве.
    Соответствует FloorTreeResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "floor"
    IS_DETAIL: ClassVar[bool] = False

    number: int
    building_id: int
    rooms_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'FloorTreeDTO':
        """
        Создаёт FloorTreeDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id', 'number' или 'building_id'
            ValueError: Если 'rooms_count' имеет некорректный тип
        """
        # Строгий контракт — обязательные поля через []
        data_id = data["id"]
        number = data["number"]
        building_id = data["building_id"]

        # Опциональные поля через get() с защитой
        rooms_count_raw = data.get('rooms_count')
        try:
            rooms_count = int(rooms_count_raw) if rooms_count_raw is not None else 0
        except (TypeError, ValueError):
            rooms_count = 0

        return cls(
            id=data_id,
            number=number,
            building_id=building_id,
            rooms_count=rooms_count,
        )


# ===== DETAIL DTO (полные данные для панели) =====
@dataclass(frozen=True, kw_only=True)
class FloorDetailDTO(BaseDTO, DateTimeMixin):
    """
    DTO для отображения детальной информации об этаже.
    Соответствует FloorDetailResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "floor"
    IS_DETAIL: ClassVar[bool] = True

    number: int
    building_id: int
    rooms_count: int = 0
    description: Optional[str] = None
    physical_type_id: Optional[int] = None
    status_id: Optional[int] = None
    plan_image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'FloorDetailDTO':
        """
        Создаёт FloorDetailDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id', 'number' или 'building_id'
            ValueError: Если 'rooms_count' имеет некорректный тип
        """
        # Строгий контракт — обязательные поля через []
        data_id = data["id"]
        number = data["number"]
        building_id = data["building_id"]

        # Опциональные поля через get() с защитой
        rooms_count_raw = data.get('rooms_count')
        try:
            rooms_count = int(rooms_count_raw) if rooms_count_raw is not None else 0
        except (TypeError, ValueError):
            rooms_count = 0

        return cls(
            id=data_id,
            number=number,
            building_id=building_id,
            rooms_count=rooms_count,
            description=data.get('description'),
            physical_type_id=data.get('physical_type_id'),
            status_id=data.get('status_id'),
            plan_image_url=data.get('plan_image_url'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )