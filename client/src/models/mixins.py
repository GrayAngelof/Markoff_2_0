# client/src/models/mixins.py
"""
Миксины для DTO моделей.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from utils.logger import get_logger


log = get_logger(__name__)


@dataclass(frozen=True)
class DateTimeMixin:
    """
    Миксин для работы с датами создания и обновления.
    
    Добавляет в модель поля created_at и updated_at,
    а также утилиты для их парсинга из API.
    """
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @staticmethod
    def parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """
        Парсит ISO дату из строки с логированием ошибок.
        
        Использует встроенный datetime.fromisoformat,
        который понимает ISO 8601 форматы.
        """
        if not value:
            return None
        
        try:
            # Нормализуем Z в +00:00 и парсим
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError) as e:
            log.warning(f"Не удалось распарсить дату '{value}': {e}")
            return None