# client/src/models/__init__.py
"""
Пакет моделей данных (DTO) клиентского приложения.

DTO = иммутабельные структуры данных без логики.
Используются как контракт между API → data → projections → UI.

СТРУКТУРА (зеркалирует бэкенд):
- structure/    → физическая иерархия (комплексы, корпуса, этажи, помещения)
- reference/    → справочники (статусы, типы)
- entity/       → бизнес-сущности (контрагенты, ответственные лица)

ВАЖНО:
- Только данные
- Без бизнес-логики
- Без UI-логики
- Без маппинга сложных преобразований
"""

# ===== STRUCTURE DTO (физическая иерархия) =====
from .structure import (
    ComplexTreeDTO,
    ComplexDetailDTO,
    BuildingTreeDTO,
    BuildingDetailDTO,
    FloorTreeDTO,
    FloorDetailDTO,
    RoomTreeDTO,
    RoomDetailDTO,
)

# ===== REFERENCE DTO (справочники) =====
from .reference import (
    BuildingStatusDTO,
    RoomStatusDTO,
    ContractStatusDTO,
    EquipmentStatusDTO,
    PaymentStatusDTO,
    PlacementStatusDTO,
    CounterpartyTypeDTO,
)

# ===== ENTITY DTO (бизнес-сущности) =====
from .entity import (
    CounterpartyDTO,
    ResponsiblePersonDTO,
)

__all__ = [
    # Structure
    "ComplexTreeDTO",
    "ComplexDetailDTO",
    "BuildingTreeDTO",
    "BuildingDetailDTO",
    "FloorTreeDTO",
    "FloorDetailDTO",
    "RoomTreeDTO",
    "RoomDetailDTO",
    # Reference
    "BuildingStatusDTO",
    "RoomStatusDTO",
    "ContractStatusDTO",
    "EquipmentStatusDTO",
    "PaymentStatusDTO",
    "PlacementStatusDTO",
    "CounterpartyTypeDTO",
    # Entity
    "CounterpartyDTO",
    "ResponsiblePersonDTO",
]