# client/src/data/utils/__init__.py
"""
Утилиты Data слоя.

Экспортирует вспомогательные функции.
"""

from .comparison import has_changed, is_equal

__all__ = [
    'has_changed',
    'is_equal',
]