# client/src/data/reference/placement_status_registry.py
"""
Реестр статусов размещения.

Хранит read-only справочник статусов размещения.
Загружается один раз при старте приложения.
"""

from typing import Callable, List

from .base import BaseRegistry
from src.models import PlacementStatusDTO
from utils.logger import get_logger


log = get_logger(__name__)


class PlacementStatusRegistry(BaseRegistry[PlacementStatusDTO]):
    """Реестр статусов размещения (read-only)."""

    def __init__(self, loader: Callable[[], List[PlacementStatusDTO]]) -> None:
        log.system("PlacementStatusRegistry инициализация")
        super().__init__(loader)
        log.system("PlacementStatusRegistry инициализирован")

    def _log_result(self, count: int) -> None:
        log.success(f"Статусы размещения: {count} записей")