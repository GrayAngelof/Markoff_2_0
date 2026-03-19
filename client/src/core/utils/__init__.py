# client/src/core/utils/__init__.py
"""
Публичное API утилит ядра.

Утилиты находятся ВНУТРИ core/utils, поэтому импорты:
- Из соседних файлов: from .comparison import ...
- БЕЗ импортов из других частей core (чтобы избежать циклических зависимостей)

Утилиты НЕ ДОЛЖНЫ импортировать из core/types, core/hierarchy и т.д.!
Это гарантирует, что utils можно использовать где угодно без риска циклических импортов.
"""
from .comparison import has_changed, is_equal
from .time import (
    current_timestamp, current_timestamp_ms,
    format_timestamp, format_timestamp_short,
    Timer
)
from .validation import (
    is_valid_node_type, is_valid_node_id, is_valid_identifier,
    validate_non_empty, validate_positive_int
)

__all__ = [
    # Сравнение
    'has_changed',
    'is_equal',
    
    # Время
    'current_timestamp',
    'current_timestamp_ms',
    'format_timestamp',
    'format_timestamp_short',
    'Timer',
    
    # Валидация
    'is_valid_node_type',
    'is_valid_node_id',
    'is_valid_identifier',
    'validate_non_empty',
    'validate_positive_int',
]