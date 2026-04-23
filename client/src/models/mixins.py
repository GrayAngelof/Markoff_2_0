# client/src/models/mixins.py
"""
Миксины для DTO моделей.

Предоставляют общую функциональность для всех моделей:
- Работа с датами (парсинг из API)
- Другие общие возможности
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== МИКСИНЫ =====
@dataclass(frozen=True)
class DateTimeMixin:
    """
    Миксин для работы с датами создания и обновления.

    Добавляет поля created_at и updated_at,
    а также утилиту для парсинга ISO дат из API.
    """

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @staticmethod
    def parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """
        Парсит ISO дату из строки.

        Нормализует 'Z' (UTC) в '+00:00' для корректной работы fromisoformat.
        Логирует ошибки парсинга как warning.
        """
        if not value:
            return None

        try:
            # Нормализуем Z (UTC) в формат, понятный fromisoformat
            normalized = value.replace('Z', '+00:00')
            return datetime.fromisoformat(normalized)
        except (ValueError, TypeError) as e:
            log.warning(f"Не удалось распарсить дату '{value}': {e}")
            return None