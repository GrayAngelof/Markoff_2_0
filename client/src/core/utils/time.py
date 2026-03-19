# client/src/core/utils/time.py
"""
Утилиты для работы со временем.

Содержит функции для работы с временными метками,
форматирования дат и временных замеров.
"""
from datetime import datetime
from typing import Optional
import time


def current_timestamp() -> str:
    """
    Возвращает текущую временную метку в ISO формате.
    
    Returns:
        str: Текущее время в формате ISO
        
    Пример:
        >>> current_timestamp()
        '2024-01-15T14:30:45.123456'
    """
    return datetime.now().isoformat()


def current_timestamp_ms() -> float:
    """
    Возвращает текущее время в миллисекундах с эпохи.
    
    Returns:
        float: Текущее время в миллисекундах
        
    Пример:
        >>> current_timestamp_ms()
        1705329045123.456
    """
    return time.time() * 1000


def format_timestamp(dt: Optional[datetime]) -> str:
    """
    Форматирует datetime для отображения пользователю.
    
    Args:
        dt: Временная метка или None
        
    Returns:
        str: Отформатированная строка или "—"
        
    Пример:
        >>> format_timestamp(datetime.now())
        '15.01.2024 14:30:45'
        >>> format_timestamp(None)
        '—'
    """
    if dt is None:
        return "—"
    
    return dt.strftime("%d.%m.%Y %H:%M:%S")


def format_timestamp_short(dt: Optional[datetime]) -> str:
    """
    Краткий формат временной метки (без секунд).
    
    Args:
        dt: Временная метка или None
        
    Returns:
        str: Отформатированная строка
        
    Пример:
        >>> format_timestamp_short(datetime.now())
        '15.01.2024 14:30'
    """
    if dt is None:
        return "—"
    
    return dt.strftime("%d.%m.%Y %H:%M")


class Timer:
    """
    Простой таймер для замера времени выполнения.
    
    Пример:
        >>> timer = Timer("Загрузка данных")
        >>> # ... делаем что-то
        >>> timer.stop()  # лог: "⏱ Загрузка данных: 123.45 мс"
    """
    
    def __init__(self, operation_name: str):
        """
        Инициализирует таймер.
        
        Args:
            operation_name: Название операции для логирования
        """
        self.operation_name = operation_name
        self.start_time = time.time()
        
        from utils.logger import get_logger
        self.log = get_logger(__name__)
        self.log.debug(f"⏱ Таймер запущен: {operation_name}")
    
    def stop(self) -> float:
        """
        Останавливает таймер и логирует результат.
        
        Returns:
            float: Время выполнения в миллисекундах
        """
        elapsed_ms = (time.time() - self.start_time) * 1000
        self.log.info(f"⏱ {self.operation_name}: {elapsed_ms:.2f} мс")
        return elapsed_ms
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, *args):
        """Автоматическая остановка при выходе из контекста."""
        self.stop()