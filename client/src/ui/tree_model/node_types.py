# client/src/ui/tree_model/node_types.py
"""
Модуль с определением типов узлов дерева.
Содержит перечисление NodeType для идентификации типа каждого узла в иерархии.
"""
from enum import Enum


class NodeType(Enum):
    """
    Типы узлов дерева объектов.
    
    Используется для идентификации типа каждого узла в иерархии:
    - COMPLEX: комплекс зданий (корневой уровень)
    - BUILDING: корпус в составе комплекса
    - FLOOR: этаж в составе корпуса
    - ROOM: помещение на этаже
    """
    COMPLEX = "complex"
    BUILDING = "building"
    FLOOR = "floor"
    ROOM = "room"
    
    def __str__(self) -> str:
        """Возвращает строковое представление типа."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'NodeType':
        """
        Создаёт NodeType из строкового значения.
        
        Args:
            value: Строковое представление типа
            
        Returns:
            NodeType: Соответствующий тип узла
            
        Raises:
            ValueError: Если строка не соответствует ни одному типу
        """
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Неизвестный тип узла: {value}")