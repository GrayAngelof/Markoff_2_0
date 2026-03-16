# client/src/data/entity_types.py (оставляем как есть - это источник правды)
"""
Типы сущностей в графе данных.
Централизованное определение всех возможных типов узлов.
"""
from enum import Enum
from typing import Dict, List, Optional, Type
from src.models import Complex, Building, Floor, Room
from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class NodeType(str, Enum):
    """
    Типы узлов в иерархии объектов.
    """
    COMPLEX = "complex"
    BUILDING = "building"
    FLOOR = "floor"
    ROOM = "room"
    
    def __str__(self) -> str:
        return self.value


# Константы для удобного доступа
COMPLEX = NodeType.COMPLEX
BUILDING = NodeType.BUILDING
FLOOR = NodeType.FLOOR
ROOM = NodeType.ROOM


# Маппинг классов моделей на NodeType
MODEL_TO_NODETYPE: Dict[Type, NodeType] = {
    Complex: COMPLEX,
    Building: BUILDING,
    Floor: FLOOR,
    Room: ROOM,
}

# Маппинг NodeType на классы моделей
NODETYPE_TO_MODEL: Dict[NodeType, Type] = {
    COMPLEX: Complex,
    BUILDING: Building,
    FLOOR: Floor,
    ROOM: Room,
}

log.debug(f"Entity types initialized: {[t.value for t in NodeType]}")