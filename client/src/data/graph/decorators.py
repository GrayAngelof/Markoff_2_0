# data/utils/decorators.py
"""
Декораторы для Data слоя.
"""

import inspect
from functools import wraps
from typing import Callable, TypeVar
from src.shared.validation import validate_positive_int

T = TypeVar('T')


def validate_ids(*id_names: str):
    """
    Декоратор для валидации ID в методах.
    
    Пример:
        @validate_ids('entity_id', 'parent_id')
        def some_method(self, entity_id: int, parent_id: int):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Получаем параметры
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            
            # Валидируем каждый ID
            for name in id_names:
                if name in bound_args.arguments:
                    value = bound_args.arguments[name]
                    if value is not None:
                        bound_args.arguments[name] = validate_positive_int(value, name)
            
            return func(self, *bound_args.args, **bound_args.kwargs)
        return wrapper
    return decorator