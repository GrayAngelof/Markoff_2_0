# client/src/core/types/protocols.py
"""
Протоколы для типизации объектов в системе.

Определяет структурные типы (Protocol) для проверки наличия
необходимых атрибутов у объектов без явного наследования.
"""

# ===== ИМПОРТЫ =====
from typing import Protocol

from .nodes import NodeType


# ===== ПРОТОКОЛЫ =====
class HasNodeType(Protocol):
    """
    Объект, имеющий атрибут NODE_TYPE.

    Используется для статической типизации объектов,
    которые хранят тип узла как атрибут класса.
    """

    NODE_TYPE: NodeType