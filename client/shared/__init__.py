"""
Утилиты общего назначения.

Наиболее часто используемые функции доступны напрямую:
    from utils import Timer, has_changed

Для специфических функций используйте подмодули:
    from utils.validation import validate_node_id
    from utils.time import format_timestamp
"""

from .time import Timer


__all__ = [
    "Timer",        # часто используется
]