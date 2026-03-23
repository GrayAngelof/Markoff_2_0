"""
Утилиты общего назначения.

Наиболее часто используемые функции доступны напрямую:
    from utils import Timer, has_changed

Для специфических функций используйте подмодули:
    from utils.validation import validate_node_id
    from utils.time import format_timestamp
"""

from .time import Timer
from .comparison import has_changed, is_equal
from .validation import validate_node_id
__all__ = []