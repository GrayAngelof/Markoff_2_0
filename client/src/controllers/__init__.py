# client/src/controllers/__init__.py
"""
Публичное API контроллеров.

Контроллеры — управляющий слой, который:
- Подписывается на события от UI
- Координирует работу сервисов (DataLoader, ReferenceStore)
- Управляет состоянием приложения (выбранный узел, раскрытые узлы)
- Эмитит события для UI (ChildrenLoaded, NodeDetailsLoaded)

ЕДИНСТВЕННЫЙ способ импорта контроллеров:
    from src.controllers import TreeController, DetailsController

ПРИМЕЧАНИЕ:
    BaseController — внутренняя деталь реализации, не экспортируется.
    Для создания собственных контроллеров наследуйтесь от BaseController
    напрямую из src.controllers.base, но это требуется только при расширении
    ядра приложения.
"""

# ===== ИМПОРТЫ =====
from .tree_controller import TreeController
from .details_controller import DetailsController
from .refresh_controller import RefreshController
from .connection_controller import ConnectionController


# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Управление деревом (раскрытие узлов, загрузка детей)
    "TreeController",
    
    # Управление панелью деталей (загрузка и отображение данных узла)
    "DetailsController",
    
    # Управление обновлением данных (F5, Ctrl+F5, полное обновление)
    "RefreshController",
    
    # Управление статусом соединения с сервером
    "ConnectionController",
]