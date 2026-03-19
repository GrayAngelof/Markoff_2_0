# client/src/core/utils/comparison.py
"""
Утилиты для сравнения объектов.

Содержит функции для проверки изменений в данных.
Используется в EntityGraph и других компонентах для оптимизации.
"""
from typing import Any


def has_changed(old: Any, new: Any) -> bool:
    """
    Проверяет, изменились ли данные.
    
    Для dataclass'ов использует структурное сравнение,
    для остальных объектов — сравнение словарей.
    
    Args:
        old: Старые данные
        new: Новые данные
        
    Returns:
        bool: True если данные изменились
        
    Пример:
        >>> has_changed(complex1, complex2)
        True  # если данные отличаются
        
    Логирование:
        - debug: результат сравнения
    """
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    # Случаи с None
    if old is None and new is None:
        log.debug("ℹ️ has_changed: оба None → False")
        return False
    
    if old is None or new is None:
        log.debug(f"ℹ️ has_changed: один из объектов None → True")
        return True
    
    # Для dataclass'ов
    if hasattr(old, '__dataclass_fields__') and hasattr(new, '__dataclass_fields__'):
        result = old != new
        log.debug(f"ℹ️ has_changed: dataclass comparison → {result}")
        return result
    
    # Для остальных объектов
    try:
        result = vars(old) != vars(new)
        log.debug(f"ℹ️ has_changed: vars comparison → {result}")
        return result
    except TypeError:
        # Если vars не работает, сравниваем по id
        result = id(old) != id(new)
        log.debug(f"ℹ️ has_changed: id comparison → {result}")
        return result


def is_equal(old: Any, new: Any) -> bool:
    """
    Проверяет, равны ли объекты (обратное от has_changed).
    
    Args:
        old: Старые данные
        new: Новые данные
        
    Returns:
        bool: True если данные равны
    """
    return not has_changed(old, new)