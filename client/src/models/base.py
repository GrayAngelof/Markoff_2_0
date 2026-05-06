# client/src/models/base.py
from dataclasses import dataclass
from typing import ClassVar, Tuple
from src.core.types.structure import NodeType, NodeIdentifier


@dataclass(frozen=True, kw_only=True)
class BaseDTO:
    """Базовый DTO с минимальным набором полей."""
    
    id: int
    
    # Метаданные класса — теперь используем NodeType
    NODE_TYPE: ClassVar[NodeType] = NodeType.ROOT
    IS_DETAIL: ClassVar[bool] = False
    
    def key(self) -> Tuple[NodeType, int]:
        """Уникальный ключ для хранения в EntityGraph."""
        return (self.NODE_TYPE, self.id)
    
    def to_identifier(self) -> NodeIdentifier:
        """Преобразует DTO в NodeIdentifier."""
        return NodeIdentifier(self.NODE_TYPE, self.id)