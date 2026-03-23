# client/src/services/__init__.py
"""
Публичное API сервисного слоя.

Экспортирует только фасады:
- ApiClient — HTTP клиент
- DataLoader — оркестратор загрузки
- ConnectionService — мониторинг соединения
"""

from services.api_client import ApiClient
from services.data_loader import DataLoader
from services.connection import ConnectionService
from services.context_service import ContextService

__all__ = [
    'ApiClient',
    'DataLoader',
    'ConnectionService',
    'ContextService',
]