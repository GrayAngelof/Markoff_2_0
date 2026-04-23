# client/src/models/building.py
"""
Модели данных для корпуса на стороне клиента.

Чистые DTO — только данные от API, никакой UI-логики.
- BuildingTreeDTO: минимальные поля для дерева (BuildingTreeResponse)
- BuildingDetailDTO: полные данные для панели деталей (BuildingDetailResponse)

Правило: DTO = строгий контракт. Обязательные поля берутся через [], а не .get().
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import ClassVar, Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== TREE DTO (минимальные данные для дерева) =====
@dataclass(frozen=True, kw_only=True)
class BuildingTreeDTO(BaseDTO):
    """
    DTO для отображения корпуса в дереве.
    Соответствует BuildingTreeResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "building"
    IS_DETAIL: ClassVar[bool] = False

    name: str
    complex_id: int
    floors_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'BuildingTreeDTO':
        """
        Создаёт BuildingTreeDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id', 'name' или 'complex_id'
            ValueError: Если 'floors_count' имеет некорректный тип
        """
        # Строгий контракт — обязательные поля через []
        data_id = data["id"]
        name = data["name"]
        complex_id = data["complex_id"]

        # Опциональные поля через get() с защитой
        floors_count_raw = data.get('floors_count')
        try:
            floors_count = int(floors_count_raw) if floors_count_raw is not None else 0
        except (TypeError, ValueError):
            floors_count = 0

        return cls(
            id=data_id,
            name=name,
            complex_id=complex_id,
            floors_count=floors_count,
        )


# ===== DETAIL DTO (полные данные для панели) =====
@dataclass(frozen=True, kw_only=True)
class BuildingDetailDTO(BaseDTO, DateTimeMixin):
    """
    DTO для отображения детальной информации о корпусе.
    Соответствует BuildingDetailResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "building"
    IS_DETAIL: ClassVar[bool] = True

    name: str
    complex_id: int
    floors_count: int = 0
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    status_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'BuildingDetailDTO':
        """
        Создаёт BuildingDetailDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id', 'name' или 'complex_id'
            ValueError: Если 'floors_count' имеет некорректный тип
        """
        # Строгий контракт — обязательные поля через []
        data_id = data["id"]
        name = data["name"]
        complex_id = data["complex_id"]

        # Опциональные поля через get() с защитой
        floors_count_raw = data.get('floors_count')
        try:
            floors_count = int(floors_count_raw) if floors_count_raw is not None else 0
        except (TypeError, ValueError):
            floors_count = 0

        return cls(
            id=data_id,
            name=name,
            complex_id=complex_id,
            floors_count=floors_count,
            description=data.get('description'),
            address=data.get('address'),
            owner_id=data.get('owner_id'),
            status_id=data.get('status_id'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )