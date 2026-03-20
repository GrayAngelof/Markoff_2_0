# client/src/core/types/protocols.py
"""
Протоколы для типизации объектов, имеющих NODE_TYPE.
"""

from typing import Protocol
from .nodes import NodeType


class HasNodeType(Protocol):
    """Объект, имеющий атрибут NODE_TYPE с типом узла."""
    NODE_TYPE: NodeType