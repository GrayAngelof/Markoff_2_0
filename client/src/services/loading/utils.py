# client/src/services/loading/utils.py
"""
Вспомогательные функции для загрузчиков.

Содержит утилиты, которые не относятся к конкретным типам загрузки:
- Проверка полноты данных (есть ли детальные поля)
- Кэширование результатов проверок
- Форматирование идентификаторов для логирования
"""

# ===== ИМПОРТЫ =====
from typing import Any, Optional

from src.core import NodeType
from src.models import Building, Complex, Floor, Room
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class LoaderUtils:
    """Утилиты для загрузчиков данных."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        """Инициализирует утилиты."""
        self._detail_cache: dict[str, bool] = {}
        self._stats = {
            'detail_checks': 0,
            'detail_cache_hits': 0,
        }
        log.system("LoaderUtils инициализирован")

    def clear_cache(self) -> None:
        """Полностью очищает кэш деталей."""
        cache_size = len(self._detail_cache)
        self._detail_cache.clear()
        log.cache(f"Кэш LoaderUtils очищен (удалено {cache_size} записей)")

    # ---- ПРОВЕРКА ПОЛНОТЫ ДАННЫХ ----
    def has_details(self, entity: Any, node_type: NodeType) -> bool:
        """
        Проверяет, загружены ли детальные поля у сущности.

        Логика полноты:
        - Complex: есть description или address
        - Building: есть description или address
        - Floor: есть description
        - Room: есть area или status_code
        """
        if not entity:
            return False

        cache_key = f"{node_type.value}:{entity.id}"

        if cache_key in self._detail_cache:
            self._stats['detail_cache_hits'] += 1
            return self._detail_cache[cache_key]

        self._stats['detail_checks'] += 1

        result = self._check_details_impl(entity, node_type)
        self._detail_cache[cache_key] = result

        if result:
            log.debug(f"Обнаружены детальные данные: {self.format_node_id(node_type, entity.id)}")

        return result

    def invalidate_detail_cache(self, node_type: NodeType, node_id: int) -> None:
        """Инвалидирует кэш деталей для конкретного узла."""
        cache_key = f"{node_type.value}:{node_id}"
        if cache_key in self._detail_cache:
            del self._detail_cache[cache_key]
            log.cache(f"Кэш деталей инвалидирован: {cache_key}")

    # ---- СТАТИСТИКА ----
    def get_stats(self) -> dict:
        """Возвращает статистику использования утилит."""
        stats = {
            'detail_checks': self._stats['detail_checks'],
            'detail_cache_hits': self._stats['detail_cache_hits'],
            'cache_size': len(self._detail_cache),
        }

        if stats['detail_checks'] > 0:
            hit_rate = (stats['detail_cache_hits'] / stats['detail_checks'] * 100)
            log.performance(
                f"LoaderUtils статистика: {stats['detail_checks']} проверок, "
                f"{stats['detail_cache_hits']} попаданий в кэш ({hit_rate:.1f}%)"
            )

        return stats

    # ---- ФОРМАТИРОВАНИЕ ДЛЯ ЛОГИРОВАНИЯ ----
    @staticmethod
    def format_node_id(node_type: NodeType, node_id: int) -> str:
        """Форматирует идентификатор узла для логирования."""
        return f"{node_type.value}#{node_id}"

    @staticmethod
    def format_node(node_type: NodeType, node_id: int, name: Optional[str] = None) -> str:
        """Форматирует узел с именем для логирования."""
        if name:
            return f"{node_type.value}#{node_id} ({name})"
        return f"{node_type.value}#{node_id}"

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _check_details_impl(self, entity: Any, node_type: NodeType) -> bool:
        """Реализация проверки детальных полей."""
        if node_type == NodeType.COMPLEX and isinstance(entity, Complex):
            return entity.description is not None or entity.address is not None

        if node_type == NodeType.BUILDING and isinstance(entity, Building):
            return entity.description is not None or entity.address is not None

        if node_type == NodeType.FLOOR and isinstance(entity, Floor):
            return entity.description is not None

        if node_type == NodeType.ROOM and isinstance(entity, Room):
            return entity.area is not None or entity.status_code is not None

        return False