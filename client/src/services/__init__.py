# client/src/services/__init__.py
"""
Публичное API сервисного слоя.

Экспортирует только фасады:
- ApiClient — HTTP клиент
- DataLoader — оркестратор загрузки
- ConnectionService — мониторинг соединения
"""

from .api_client import ApiClient
from .data_loader import DataLoader
from .connection import ConnectionService
from .context_service import ContextService

__all__ = [
    'ApiClient',
    'DataLoader',
    'ConnectionService',
    'ContextService',
]