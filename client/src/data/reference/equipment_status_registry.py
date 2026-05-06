# client/src/data/reference/equipment_status_registry.py
"""
Реестр статусов оборудования.

Хранит read-only справочник статусов оборудования.
Загружается один раз при старте приложения.
"""

from typing import Callable, List

from .base import BaseRegistry
from src.models import EquipmentStatusDTO
from utils.logger import get_logger


log = get_logger(__name__)


class EquipmentStatusRegistry(BaseRegistry[EquipmentStatusDTO]):
    """Реестр статусов оборудования (read-only)."""

    def __init__(self, loader: Callable[[], List[EquipmentStatusDTO]]) -> None:
        log.system("EquipmentStatusRegistry инициализация")
        super().__init__(loader)
        log.system("EquipmentStatusRegistry инициализирован")

    def _log_result(self, count: int) -> None:
        log.success(f"Статусы оборудования: {count} записей")