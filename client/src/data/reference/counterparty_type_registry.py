# client/src/data/reference/counterparty_type_registry.py
"""
Реестр типов контрагентов.

Хранит read-only справочник типов контрагентов.
Загружается один раз при старте приложения.
"""

from typing import Callable, List

from .base import BaseRegistry
from src.models import CounterpartyTypeDTO
from utils.logger import get_logger


log = get_logger(__name__)


class CounterpartyTypeRegistry(BaseRegistry[CounterpartyTypeDTO]):
    """Реестр типов контрагентов (read-only)."""

    def __init__(self, loader: Callable[[], List[CounterpartyTypeDTO]]) -> None:
        log.system("CounterpartyTypeRegistry инициализация")
        super().__init__(loader)
        log.system("CounterpartyTypeRegistry инициализирован")

    def _log_result(self, count: int) -> None:
        log.success(f"Типы контрагентов: {count} записей")