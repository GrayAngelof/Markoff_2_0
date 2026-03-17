# client/src/controllers/__init__.py
"""
Контроллеры приложения - связующее звено между UI и сервисами.

Каждый контроллер:
- Подписывается на определённые события
- Содержит логику "что делать"
- Не содержит UI-кода (только вызовы сервисов и эмит событий)
"""
from src.controllers.tree_controller import TreeController
from src.controllers.details_controller import DetailsController
from src.controllers.refresh_controller import RefreshController
from src.controllers.connection_controller import ConnectionController

__all__ = [
    "TreeController",
    "DetailsController",
    "RefreshController",
    "ConnectionController",
]