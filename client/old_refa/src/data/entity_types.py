# client/src/data/entity_types.py
"""
Типы сущностей в графе данных.
Централизованное определение всех возможных типов узлов.
"""
from enum import Enum
from typing import Dict, List, Optional, Type
from src.models import Complex, Building, Floor, Room
from src.models.counterparty import Counterparty
from src.models.responsible_person import ResponsiblePerson
from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class NodeType(str, Enum):
    """
    Типы узлов в иерархии объектов.
    
    Расширено для поддержки:
    - Контрагентов (юридические лица)
    - Ответственных лиц (контакты)
    """
    # Физическая структура
    COMPLEX = "complex"
    BUILDING = "building"
    FLOOR = "floor"
    ROOM = "room"
    
    # Контрагенты и контакты
    COUNTERPARTY = "counterparty"
    RESPONSIBLE_PERSON = "responsible_person"
    
    def __str__(self) -> str:
        return self.value


# Константы для удобного доступа
COMPLEX = NodeType.COMPLEX
BUILDING = NodeType.BUILDING
FLOOR = NodeType.FLOOR
ROOM = NodeType.ROOM
COUNTERPARTY = NodeType.COUNTERPARTY
RESPONSIBLE_PERSON = NodeType.RESPONSIBLE_PERSON


# Маппинг классов моделей на NodeType
MODEL_TO_NODETYPE: Dict[Type, NodeType] = {
    Complex: COMPLEX,
    Building: BUILDING,
    Floor: FLOOR,
    Room: ROOM,
    Counterparty: COUNTERPARTY,
    ResponsiblePerson: RESPONSIBLE_PERSON,
}

# Маппинг NodeType на классы моделей
NODETYPE_TO_MODEL: Dict[NodeType, Type] = {
    COMPLEX: Complex,
    BUILDING: Building,
    FLOOR: Floor,
    ROOM: Room,
    COUNTERPARTY: Counterparty,
    RESPONSIBLE_PERSON: ResponsiblePerson,
}

# Маппинг названий классов (строк) на NodeType (для schema.py)
CLASS_NAME_TO_NODETYPE: Dict[str, NodeType] = {
    'Complex': COMPLEX,
    'Building': BUILDING,
    'Floor': FLOOR,
    'Room': ROOM,
    'Counterparty': COUNTERPARTY,
    'ResponsiblePerson': RESPONSIBLE_PERSON,
}

log.debug(f"Entity types initialized: {[t.value for t in NodeType]}")