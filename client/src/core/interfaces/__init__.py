# client/src/core/interfaces/__init__.py
"""
Базовые интерфейсы (контракты) ядра.

Содержит только протоколы и абстрактные классы,
которые должны реализовывать другие слои приложения.
"""
from .repository import Repository

__all__ = [
    'Repository',
]