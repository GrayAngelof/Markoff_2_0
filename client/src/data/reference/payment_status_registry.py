# client/src/data/reference/payment_status_registry.py
"""
Реестр статусов платежей.

Хранит read-only справочник статусов платежей.
Загружается один раз при старте приложения.
"""

from typing import Callable, List

from .base import BaseRegistry
from src.models import PaymentStatusDTO
from utils.logger import get_logger


log = get_logger(__name__)


class PaymentStatusRegistry(BaseRegistry[PaymentStatusDTO]):
    """Реестр статусов платежей (read-only)."""

    def __init__(self, loader: Callable[[], List[PaymentStatusDTO]]) -> None:
        log.system("PaymentStatusRegistry инициализация")
        super().__init__(loader)
        log.system("PaymentStatusRegistry инициализирован")

    def _log_result(self, count: int) -> None:
        log.success(f"Статусы платежей: {count} записей")