# client/src/models/complex.py
"""
Модели данных для комплекса на стороне клиента.

Чистые DTO — только данные от API, никакой UI-логики.
- ComplexTreeDTO: минимальные поля для дерева (ComplexTreeResponse)
- ComplexDetailDTO: полные данные для панели деталей (ComplexDetailResponse)

Правило: DTO = строгий контракт. Обязательные поля берутся через [], а не .get().
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from typing import ClassVar, Optional

from .base import BaseDTO
from .mixins import DateTimeMixin


# ===== TREE DTO (минимальные данные для дерева) =====
@dataclass(frozen=True, kw_only=True)
class ComplexTreeDTO(BaseDTO):
    """
    DTO для отображения комплекса в дереве.
    Соответствует ComplexTreeResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "complex"
    IS_DETAIL: ClassVar[bool] = False

    name: str
    buildings_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'ComplexTreeDTO':
        """
        Создаёт ComplexTreeDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id' или 'name'
            ValueError: Если 'buildings_count' имеет некорректный тип
        """
        # Строгий контракт — обязательные поля через []
        data_id = data["id"]
        name = data["name"]

        # Опциональные поля через get() с защитой
        buildings_count_raw = data.get('buildings_count')
        try:
            buildings_count = int(buildings_count_raw) if buildings_count_raw is not None else 0
        except (TypeError, ValueError):
            buildings_count = 0

        return cls(
            id=data_id,
            name=name,
            buildings_count=buildings_count,
        )


# ===== DETAIL DTO (полные данные для панели) =====
@dataclass(frozen=True, kw_only=True)
class ComplexDetailDTO(BaseDTO, DateTimeMixin):
    """
    DTO для отображения детальной информации о комплексе.
    Соответствует ComplexDetailResponse из бекенда.
    """

    NODE_TYPE: ClassVar[str] = "complex"
    IS_DETAIL: ClassVar[bool] = True

    name: str
    buildings_count: int = 0
    description: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    status_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ComplexDetailDTO':
        """
        Создаёт ComplexDetailDTO из словаря (ответ API).

        Raises:
            KeyError: Если отсутствует обязательное поле 'id' или 'name'
            ValueError: Если 'buildings_count' имеет некорректный тип
        """
        # Строгий контракт — обязательные поля через []
        data_id = data["id"]
        name = data["name"]

        # Опциональные поля через get() с защитой
        buildings_count_raw = data.get('buildings_count')
        try:
            buildings_count = int(buildings_count_raw) if buildings_count_raw is not None else 0
        except (TypeError, ValueError):
            buildings_count = 0

        return cls(
            id=data_id,
            name=name,
            buildings_count=buildings_count,
            description=data.get('description'),
            address=data.get('address'),
            owner_id=data.get('owner_id'),
            status_id=data.get('status_id'),
            created_at=cls.parse_datetime(data.get('created_at')),
            updated_at=cls.parse_datetime(data.get('updated_at')),
        )