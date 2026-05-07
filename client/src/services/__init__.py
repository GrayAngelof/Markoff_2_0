# client/src/services/__init__.py
"""
Публичное API сервисного слоя.

Сервисы — слой бизнес-логики и координации:
- ApiClient — HTTP клиент для взаимодействия с бэкендом
- DataLoader — оркестратор загрузки данных (дерево, детали, справочники)
- ConnectionService — мониторинг состояния соединения с сервером
- ContextService — построение контекста (имена родителей для UI)

ЕДИНСТВЕННЫЙ способ импорта сервисов:
    from src.services import ApiClient, DataLoader, ConnectionService

ПРИМЕЧАНИЕ:
    Внутренние загрузчики (loaders/*) и API детали (api/*) — приватные пакеты.
    Используйте только фасады из этого модуля.
"""

# ===== ИМПОРТЫ) =====
from .api_client import ApiClient
from .connection import ConnectionService
from .data_loader import DataLoader


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # HTTP клиент для запросов к бэкенду
    "ApiClient",
    
    # Мониторинг состояния соединения
    "ConnectionService",
    
    # Оркестратор загрузки данных
    "DataLoader",
]