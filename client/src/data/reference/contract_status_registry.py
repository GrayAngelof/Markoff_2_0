# client/src/data/reference/contract_status_registry.py
"""
Реестр статусов договоров.

Хранит read-only справочник статусов договоров.
Загружается один раз при старте приложения.
"""

from typing import Callable, List

from .base import BaseRegistry
from src.models import ContractStatusDTO
from utils.logger import get_logger


log = get_logger(__name__)


class ContractStatusRegistry(BaseRegistry[ContractStatusDTO]):
    """Реестр статусов договоров (read-only)."""

    def __init__(self, loader: Callable[[], List[ContractStatusDTO]]) -> None:
        log.system("ContractStatusRegistry инициализация")
        super().__init__(loader)
        log.system("ContractStatusRegistry инициализирован")

    def _log_result(self, count: int) -> None:
        log.success(f"Статусы договоров: {count} записей")