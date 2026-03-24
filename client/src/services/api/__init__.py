# client/src/services/api/__init__.py
"""
Приватный пакет API слоя.

ВНИМАНИЕ: Это ПРИВАТНЫЙ пакет. Никто не должен импортировать из него напрямую.

Все публичные методы доступны через ApiClient (services.api_client).
Внутренние модули импортируются только для удобства внутри services,
но не экспортируются наружу.

Правильное использование:
    from src.services import ApiClient  # ✅

Неправильное использование:
    from src.services.api import HttpClient  # ❌
    from src.services.api.errors import ApiError  # ❌
"""

# Импортируем для удобства внутри services (не для экспорта!)
from src.services.api.http_client import HttpClient
from src.services.api.endpoints import Endpoints
from src.services.api.converters import (
    to_complex_list, to_building_list, to_floor_list, to_room_list,
    to_complex, to_building, to_floor, to_room,
    to_counterparty, to_responsible_person_list,
)
from src.services.api.errors import (
    ApiError, ConnectionError, TimeoutError,
    NotFoundError, ClientError, ServerError,
)

# НЕТ __all__! Это приватный пакет, не нужно экспортировать имена.
# Если очень нужно — используем __all__ = [] (пустой список),
# чтобы явно указать, что ничего не экспортируется.

__all__: list[str] = []