# client/src/core/types/nodes.py
"""
Типы узлов иерархии.

Содержит определения:
- NodeType — перечисление типов узлов
- NodeID, NodeKey, ParentInfo — псевдонимы типов
- NodeIdentifier — value object для идентификации узла

Никакой логики, только данные!
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


# ===== ПЕРЕЧИСЛЕНИЯ =====
class NodeType(str, Enum):
    """Типы узлов в иерархии объектов недвижимости."""

    ROOT = "root"
    """Виртуальный корневой узел (для унификации событий)"""

    COMPLEX = "complex"
    """Комплекс зданий (корневой уровень)"""

    BUILDING = "building"
    """Корпус в составе комплекса"""

    FLOOR = "floor"
    """Этаж в составе корпуса (может быть отрицательным для подвалов)"""

    ROOM = "room"
    """Помещение на этаже"""

    def __str__(self) -> str:
        return self.value


# ===== ПСЕВДОНИМЫ ТИПОВ =====
NodeID = int
"""Уникальный числовой идентификатор узла."""

NodeKey = str
"""
Строковый ключ для быстрого доступа к узлу.
Формат: "{тип}:{id}", например "complex:42".
"""

ParentInfo = Tuple[NodeType, NodeID]
"""Информация о родительском узле: (тип, id)."""


# ===== VALUE OBJECTS =====
@dataclass(frozen=True, slots=True)
class NodeIdentifier:
    """
    Структурированный идентификатор узла.

    Используется внутри приложения для типобезопасной передачи идентификаторов.
    Преобразования в строку и обратно — в core.serializers.

    Пример:
        >>> node = NodeIdentifier(NodeType.COMPLEX, 42)
        >>> node.node_type
        NodeType.COMPLEX
        >>> node.node_id
        42
    """

    node_type: NodeType
    node_id: NodeID


# ===== КОНСТАНТЫ =====
# Виртуальный корневой узел для унификации событий ChildrenLoaded
ROOT_NODE = NodeIdentifier(NodeType.ROOT, 0)