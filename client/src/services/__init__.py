# client/src/services/__init__.py
"""
Публичное API сервисного слоя.

Экспортирует только фасады:
- ApiClient — HTTP клиент
- DataLoader — оркестратор загрузки
- ConnectionService — мониторинг соединения
"""

from src.services.api_client import ApiClient
from src.services.data_loader import DataLoader
from src.services.connection import ConnectionService
from src.services.context_service import ContextService

__all__ = [
    'ApiClient',
    'DataLoader',
    'ConnectionService',
    'ContextService',
]