# client/src/shared/time.py
"""
Утилиты для работы со временем.

Содержит функции для работы с временными метками,
форматирования дат и временных замеров.
"""

# ===== ИМПОРТЫ =====
import time
from datetime import datetime
from typing import Optional

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ФУНКЦИИ =====
def current_timestamp() -> str:
    """Возвращает текущую временную метку в ISO формате."""
    return datetime.now().isoformat()


def current_timestamp_ms() -> float:
    """Возвращает текущее время в миллисекундах с эпохи."""
    return time.time() * 1000


def format_timestamp(dt: Optional[datetime]) -> str:
    """Форматирует datetime для отображения пользователю."""
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M:%S")


def format_timestamp_short(dt: Optional[datetime]) -> str:
    """Краткий формат временной метки (без секунд)."""
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")


# ===== КЛАСС =====
class Timer:
    """
    Простой таймер для замера времени выполнения.

    Использует контекстный менеджер для автоматического логирования.
    """

    def __init__(self, operation_name: str) -> None:
        """Инициализирует таймер."""
        self.operation_name = operation_name
        self.start_time = time.time()
        log.debug(f"Таймер запущен: {operation_name}")

    def stop(self) -> float:
        """
        Останавливает таймер и логирует результат.

        Returns:
            Время выполнения в миллисекундах
        """
        elapsed_ms = (time.time() - self.start_time) * 1000
        log.performance(f"{self.operation_name}: {elapsed_ms:.2f} мс")
        return elapsed_ms

    def __enter__(self) -> 'Timer':
        """Поддержка контекстного менеджера."""
        return self

    def __exit__(self, *args) -> None:
        """Автоматическая остановка при выходе из контекста."""
        self.stop()