# client/src/shared/validation.py
"""
Утилиты для валидации данных.

Содержит функции для проверки корректности данных
перед их использованием в системе.
"""
from typing import Any, Optional

from ..core import NodeType, NodeIdentifier
from ..core.types.exceptions import ValidationError
from utils.logger import get_logger

log = get_logger(__name__)


def is_valid_node_type(type_str: str) -> bool:
    """
    Проверяет, является ли строка валидным типом узла.
    
    Args:
        type_str: Проверяемая строка
        
    Returns:
        bool: True если строка соответствует одному из типов
        
    Пример:
        >>> is_valid_node_type('complex')
        True
        >>> is_valid_node_type('invalid')
        False
    """
    return type_str in NodeType._value2member_map_


def is_valid_node_id(node_id: Any) -> bool:
    """
    Проверяет, является ли значение валидным ID узла.
    
    Args:
        node_id: Проверяемое значение
        
    Returns:
        bool: True если это положительное целое число
    """
    return isinstance(node_id, int) and node_id > 0


def is_valid_identifier(identifier: Any) -> bool:
    """
    Проверяет, является ли объект валидным NodeIdentifier.
    
    Args:
        identifier: Проверяемый объект
        
    Returns:
        bool: True если это NodeIdentifier с корректными полями
    """
    if not isinstance(identifier, NodeIdentifier):
        return False
    
    return (isinstance(identifier.node_type, NodeType) and
            is_valid_node_id(identifier.node_id))


def validate_non_empty(value: Optional[str], name: str = "Значение") -> str:
    """
    Проверяет, что строка не пустая.
    
    Args:
        value: Проверяемая строка
        name: Имя поля для сообщения об ошибке
        
    Returns:
        str: Исходная строка
        
    Raises:
        ValidationError: Если строка пустая или None
    """
    if value is None:
        log.warning(f"Валидация {name}: значение None")
        raise ValidationError(f"{name} не может быть None")
    
    if not value.strip():
        log.warning(f"Валидация {name}: пустая строка")
        raise ValidationError(f"{name} не может быть пустым")
    
    # log.debug(f"Валидация {name}: '{value[:50]}...'")
    return value


def validate_positive_int(value: Any, name: str = "ID") -> int:
    """
    Проверяет, что значение является положительным целым числом.
    
    Args:
        value: Проверяемое значение
        name: Имя поля для сообщения об ошибке
        
    Returns:
        int: Исходное значение
        
    Raises:
        ValidationError: Если значение не является положительным целым
    """
    if not isinstance(value, int):
        log.warning(f"Валидация {name}: {value} (тип {type(value).__name__})")
        raise ValidationError(f"{name} должен быть целым числом")
    
    if value <= 0:
        log.warning(f"Валидация {name}: {value} (не положительное)")
        raise ValidationError(f"{name} должен быть положительным")
    
    # log.debug(f"validate_positive_int: Валидация {name}: {value}")
    return value


def validate_node_id(node_id: Any) -> int:
    """
    Проверяет, что значение является валидным ID узла.
    
    Args:
        node_id: Проверяемое значение
        
    Returns:
        int: ID узла
        
    Raises:
        ValidationError: Если значение не является валидным ID
    """
    return validate_positive_int(node_id, "ID узла")


def validate_node_type(node_type: Any) -> NodeType:
    """
    Проверяет, что значение является валидным типом узла.
    
    Args:
        node_type: Проверяемое значение
        
    Returns:
        NodeType: Тип узла
        
    Raises:
        ValidationError: Если значение не является валидным типом
    """
    if isinstance(node_type, NodeType):
        log.debug(f"Валидация типа узла: {node_type}")
        return node_type
    
    if isinstance(node_type, str):
        try:
            result = NodeType(node_type)
            log.debug(f"Валидация типа узла: '{node_type}' -> {result}")
            return result
        except ValueError:
            log.warning(f"Валидация типа узла: неизвестный тип '{node_type}'")
            raise ValidationError(f"Неизвестный тип узла: '{node_type}'")
    
    log.warning(f"Валидация типа узла: {node_type} (тип {type(node_type).__name__})")
    raise ValidationError(f"Тип узла должен быть NodeType или str")