# client/src/core/__init__.py
"""
Ядро клиентского приложения.
Предоставляет основные сервисы для работы с данными:
- API клиент для взаимодействия с бекендом
- Система кэширования данных
"""
from src.core.api_client import ApiClient
from src.core.cache import DataCache

__all__ = [
    "ApiClient",
    "DataCache"
]