# client/src/shared/validation.py
"""
Утилиты для валидации данных.

Содержит функции для проверки корректности данных
перед их использованием в системе.
"""

# ===== ИМПОРТЫ =====
from typing import Any, Optional

from src.core import NodeIdentifier, NodeType
from src.core.types.exceptions import ValidationError
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ФУНКЦИИ ПРОВЕРКИ (без исключений) =====
def is_valid_node_type(type_str: str) -> bool:
    """Проверяет, является ли строка валидным типом узла."""
    return type_str in NodeType._value2member_map_


def is_valid_node_id(node_id: Any) -> bool:
    """Проверяет, является ли значение валидным ID узла."""
    return isinstance(node_id, int) and node_id > 0


def is_valid_identifier(identifier: Any) -> bool:
    """Проверяет, является ли объект валидным NodeIdentifier."""
    if not isinstance(identifier, NodeIdentifier):
        return False
    return (isinstance(identifier.node_type, NodeType) and
            is_valid_node_id(identifier.node_id))


# ===== ФУНКЦИИ ВАЛИДАЦИИ (с исключениями) =====
def validate_non_empty(value: Optional[str], name: str = "Значение") -> str:
    """
    Проверяет, что строка не пустая.

    Raises:
        ValidationError: Если строка пустая или None
    """
    if value is None:
        log.warning(f"Валидация {name}: значение None")
        raise ValidationError(f"{name} не может быть None")

    if not value.strip():
        log.warning(f"Валидация {name}: пустая строка")
        raise ValidationError(f"{name} не может быть пустым")

    return value


def validate_positive_int(value: Any, name: str = "ID") -> int:
    """
    Проверяет, что значение является положительным целым числом.

    Raises:
        ValidationError: Если значение не является положительным целым
    """
    if not isinstance(value, int):
        log.warning(f"Валидация {name}: {value} (тип {type(value).__name__})")
        raise ValidationError(f"{name} должен быть целым числом")

    if value <= 0:
        log.warning(f"Валидация {name}: {value} (не положительное)")
        raise ValidationError(f"{name} должен быть положительным")

    return value


def validate_node_id(node_id: Any) -> int:
    """Проверяет, что значение является валидным ID узла."""
    return validate_positive_int(node_id, "ID узла")


def validate_node_type(node_type: Any) -> NodeType:
    """
    Проверяет, что значение является валидным типом узла.

    Raises:
        ValidationError: Если значение не является валидным типом
    """
    if isinstance(node_type, NodeType):
        return node_type

    if isinstance(node_type, str):
        try:
            return NodeType(node_type)
        except ValueError:
            log.warning(f"Валидация типа узла: неизвестный тип '{node_type}'")
            raise ValidationError(f"Неизвестный тип узла: '{node_type}'")

    log.warning(f"Валидация типа узла: {node_type} (тип {type(node_type).__name__})")
    raise ValidationError(f"Тип узла должен быть NodeType или str")