# client/src/services/loading/utils.py
"""
Вспомогательные функции для загрузчиков.

Содержит утилиты, которые не относятся к конкретным типам загрузки.
"""

from typing import Any, Optional

from src.core import NodeType
from src.models import Complex, Building, Floor, Room

from utils.logger import get_logger

log = get_logger(__name__)


class LoaderUtils:
    """
    Утилиты для загрузчиков данных.
    
    Отвечает за:
    - Проверку полноты данных (есть ли детальные поля)
    - Кэширование результатов проверок (опционально)
    - Форматирование идентификаторов для логирования
    """
    
    def __init__(self):
        """Инициализирует утилиты."""
        self._detail_cache: dict[str, bool] = {}
        self._stats = {
            'detail_checks': 0,
            'detail_cache_hits': 0,
        }
        log.system("LoaderUtils инициализирован")
    
    def has_details(self, entity: Any, node_type: NodeType) -> bool:
        """
        Проверяет, загружены ли детальные поля у сущности.
        
        Логика полноты:
        - Complex: есть description или address
        - Building: есть description или address
        - Floor: есть description
        - Room: есть area или status_code
        
        Args:
            entity: Сущность для проверки
            node_type: Тип сущности
            
        Returns:
            bool: True если детальные поля загружены
        """
        if not entity:
            return False
        
        # Формируем ключ кэша
        cache_key = f"{node_type.value}:{entity.id}"
        
        # Проверяем кэш
        if cache_key in self._detail_cache:
            self._stats['detail_cache_hits'] += 1
            return self._detail_cache[cache_key]
        
        self._stats['detail_checks'] += 1
        
        # Проверяем в зависимости от типа
        result = self._check_details_impl(entity, node_type)
        
        # Сохраняем в кэш
        self._detail_cache[cache_key] = result
        
        # Логируем только важные случаи
        if result:
            # Обнаружены детальные данные - это событие, достойное DEBUG
            log.debug(f"Обнаружены детальные данные: {self.format_node_id(node_type, entity.id)}")
        
        return result
    
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
    
    def invalidate_detail_cache(self, node_type: NodeType, node_id: int) -> None:
        """Инвалидирует кэш деталей для конкретного узла."""
        cache_key = f"{node_type.value}:{node_id}"
        if cache_key in self._detail_cache:
            del self._detail_cache[cache_key]
            log.cache(f"Кэш деталей инвалидирован: {cache_key}")
    
    def clear_cache(self) -> None:
        """Полностью очищает кэш деталей."""
        cache_size = len(self._detail_cache)
        self._detail_cache.clear()
        log.cache(f"Кэш LoaderUtils очищен (удалено {cache_size} записей)")
    
    def get_stats(self) -> dict:
        """Возвращает статистику использования утилит."""
        stats = {
            'detail_checks': self._stats['detail_checks'],
            'detail_cache_hits': self._stats['detail_cache_hits'],
            'cache_size': len(self._detail_cache),
        }
        
        # Статистика - это performance метрика
        if stats['detail_checks'] > 0:
            hit_rate = (stats['detail_cache_hits'] / stats['detail_checks'] * 100) if stats['detail_checks'] > 0 else 0
            log.performance(f"LoaderUtils статистика: {stats['detail_checks']} проверок, "
                          f"{stats['detail_cache_hits']} попаданий в кэш ({hit_rate:.1f}%)")
        
        return stats
    
    # ===== Форматирование для логирования =====
    
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