# client/src/data/utils/decorators.py
"""
Декораторы для Data слоя.

Обеспечивают единообразную валидацию и логирование
для методов работы с данными.
"""

# ===== ИМПОРТЫ =====
import inspect
from functools import wraps
from typing import Callable, TypeVar

from src.shared.validation import validate_positive_int
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ТИПЫ =====
T = TypeVar('T')


# ===== ДЕКОРАТОРЫ =====
def validate_ids(*id_names: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Декоратор для валидации ID в методах.

    Проверяет, что указанные параметры являются положительными целыми числами.
    Если параметр None — пропускает (некоторые методы допускают отсутствие ID).

    Args:
        *id_names: Имена параметров, которые нужно валидировать

    Example:
        @validate_ids('entity_id', 'parent_id')
        def some_method(self, entity_id: int, parent_id: int) -> None:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            # Получаем все параметры функции
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            # Валидируем каждый указанный ID
            for name in id_names:
                if name in bound_args.arguments:
                    value = bound_args.arguments[name]
                    if value is not None:
                        try:
                            bound_args.arguments[name] = validate_positive_int(value, name)
                        except ValueError as e:
                            log.error(f"Ошибка валидации {name}: {e}")
                            raise

            return func(self, *bound_args.args, **bound_args.kwargs)
        return wrapper
    return decorator