# client/src/shared/comparison.py
"""
Утилиты для сравнения объектов.

Содержит функции для проверки изменений в данных.
Используется для определения необходимости обновления кэша.
"""

# ===== ИМПОРТЫ =====
from typing import Any

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ФУНКЦИИ =====
def has_changed(old: Any, new: Any) -> bool:
    """
    Проверяет, изменились ли данные.

    Использует структурное сравнение для dataclass'ов,
    сравнение словарей для обычных объектов,
    сравнение id как fallback.
    """
    if old is None and new is None:
        log.debug("has_changed: оба None → False")
        return False

    if old is None or new is None:
        log.debug("has_changed: один из объектов None → True")
        return True

    # Для dataclass'ов
    if hasattr(old, '__dataclass_fields__') and hasattr(new, '__dataclass_fields__'):
        result = old != new
        log.debug(f"has_changed: dataclass comparison → {result}")
        return result

    # Для остальных объектов
    try:
        result = vars(old) != vars(new)
        log.debug(f"has_changed: vars comparison → {result}")
        return result
    except TypeError:
        result = id(old) != id(new)
        log.debug(f"has_changed: id comparison → {result}")
        return result


def is_equal(old: Any, new: Any) -> bool:
    """Проверяет, равны ли объекты (обратное от has_changed)."""
    return not has_changed(old, new)