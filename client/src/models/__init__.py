# client/src/models/__init__.py
"""
Пакет моделей данных (DTO) клиентского приложения.

DTO = иммутабельные структуры данных без логики.
Используются как контракт между API → data → projections → UI.

ВАЖНО:
- Только данные
- Без бизнес-логики
- Без UI-логики
- Без маппинга сложных преобразований

Текущее состояние:
DTO пока сгруппированы в единый пакет.
В будущем планируется разделение на:
    - entities/   (бизнес-сущности)
    - reference/  (справочники)
"""

# ===== ENTITY DTO (основные бизнес-сущности) =====
from .complex import ComplexTreeDTO, ComplexDetailDTO
from .building import BuildingTreeDTO, BuildingDetailDTO
from .floor import FloorTreeDTO, FloorDetailDTO
from .room import RoomTreeDTO, RoomDetailDTO

# ===== REFERENCE DTO (справочники) =====
from .status import BuildingStatusDTO, RoomStatusDTO

# ===== TODO: будущие справочники =====
# TODO: SensorTypeDTO
# TODO: RoomTypeDTO
# TODO: FloorTypeDTO
# TODO: PositionDTO (если появится)

# TODO: РАЗДЕЛИТЬ ПАКЕТЫ НА:
# models/entities/
# models/reference/

__all__ = [
    # Complex
    "ComplexTreeDTO",
    "ComplexDetailDTO",

    # Building
    "BuildingTreeDTO",
    "BuildingDetailDTO",

    # Floor
    "FloorTreeDTO",
    "FloorDetailDTO",

    # Room
    "RoomTreeDTO",
    "RoomDetailDTO",

    # Reference (status)
    "BuildingStatusDTO",
    "RoomStatusDTO",
]