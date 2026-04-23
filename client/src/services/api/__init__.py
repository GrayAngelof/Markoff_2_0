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
from .http_client import HttpClient
from .endpoints import Endpoints
from .converters import (
    # Tree конвертеры (списки для дерева)
    to_complex_tree_list,
    to_building_tree_list,
    to_floor_tree_list,
    to_room_tree_list,
    # Detail конвертеры (одиночные объекты для панели)
    to_complex_detail,
    to_building_detail,
    to_floor_detail,
    to_room_detail,
    # Утилита
    convert_optional,
)
from src.services.api.errors import (
    ApiError,
    ConnectionError,
    TimeoutError,
    NotFoundError,
    ClientError,
    ServerError,
)

# НЕТ __all__! Это приватный пакет, не нужно экспортировать имена.
# Если очень нужно — используем __all__ = [] (пустой список),
# чтобы явно указать, что ничего не экспортируется.

__all__: list[str] = []