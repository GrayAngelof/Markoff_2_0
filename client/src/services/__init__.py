# client/src/services/__init__.py
"""
Публичное API сервисного слоя.

Экспортирует только фасады:
- ApiClient — HTTP клиент
- DataLoader — оркестратор загрузки
- ConnectionService — мониторинг соединения
- ContextService — построение контекста (имена родителей)
- StatusRegistry — реестр статусов узлов
"""

# ===== ИМПОРТЫ =====
from .api_client import ApiClient
from .connection import ConnectionService
from .context_service import ContextService
from .data_loader import DataLoader
from .status_registry import StatusRegistry


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    "ApiClient",
    "ConnectionService",
    "ContextService",
    "DataLoader",
    "StatusRegistry",
]