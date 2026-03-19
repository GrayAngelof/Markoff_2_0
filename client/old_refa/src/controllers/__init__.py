# client/src/controllers/__init__.py
"""
Контроллеры приложения - связующее звено между UI и сервисами.

Обновлён для поддержки:
- Владельцев корпусов
- Ответственных лиц
- Контактной информации
"""
from src.controllers.base import BaseController
from src.controllers.tree_controller import TreeController
from src.controllers.details_controller import DetailsController
from src.controllers.refresh_controller import RefreshController
from src.controllers.connection_controller import ConnectionController

__all__ = [
    "BaseController",
    "TreeController",
    "DetailsController",
    "RefreshController",
    "ConnectionController",
]