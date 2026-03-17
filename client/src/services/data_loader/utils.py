# client/src/services/data_loader/utils.py
"""
Вспомогательные функции для DataLoader.
Кэширование, проверки, форматирование.
"""
from typing import Optional, Dict, Any
from src.data.entity_types import NodeType
from src.data.graph.schema import get_child_type, get_parent_type
from src.models import Complex, Building, Floor, Room

from utils.logger import get_logger


log = get_logger(__name__)


class LoaderUtils:
    """
    Утилиты для загрузчика данных.
    
    Отвечает за:
    - Проверку наличия детальных данных
    - Кэширование результатов проверок
    - Вспомогательные функции
    """
    
    def __init__(self) -> None:
        """Инициализирует утилиты."""
        # Кэш для результатов проверки деталей
        self._details_cache: Dict[str, bool] = {}
        
        # Статистика
        self._stats = {
            'detail_checks': 0,
            'detail_cache_hits': 0
        }
        
        log.debug("LoaderUtils инициализирован")
    
    def has_details(self, entity: Any, node_type: NodeType) -> bool:
        """
        Проверяет, загружены ли детальные поля у сущности.
        
        Использует кэш для ускорения повторных проверок.
        """
        if not entity:
            return False
        
        # Формируем ключ кэша
        cache_key = f"{node_type.value}:{entity.id}"
        
        # Проверяем кэш
        if cache_key in self._details_cache:
            self._stats['detail_cache_hits'] += 1
            return self._details_cache[cache_key]
        
        self._stats['detail_checks'] += 1
        
        # Проверяем в зависимости от типа
        result = self._check_details_impl(entity, node_type)
        
        # Сохраняем в кэш
        self._details_cache[cache_key] = result
        
        log.debug(f"has_details({node_type}#{entity.id}) = {result}")
        return result
    
    def _check_details_impl(self, entity: Any, node_type: NodeType) -> bool:
        """Реализация проверки детальных полей."""
        if node_type == NodeType.COMPLEX and isinstance(entity, Complex):
            return entity.description is not None or entity.address is not None
            
        elif node_type == NodeType.BUILDING and isinstance(entity, Building):
            return entity.description is not None or entity.address is not None
            
        elif node_type == NodeType.FLOOR and isinstance(entity, Floor):
            return entity.description is not None
            
        elif node_type == NodeType.ROOM and isinstance(entity, Room):
            return entity.area is not None or entity.status_code is not None
            
        return False
    
    def invalidate_details_cache(self, node_type: NodeType, node_id: int) -> None:
        """Инвалидирует кэш деталей для конкретного узла."""
        cache_key = f"{node_type.value}:{node_id}"
        if cache_key in self._details_cache:
            del self._details_cache[cache_key]
            log.debug(f"Инвалидирован кэш деталей для {cache_key}")
    
    def clear_cache(self) -> None:
        """Полностью очищает кэш."""
        self._details_cache.clear()
        log.debug("Кэш деталей очищен")
    
    # ===== Навигационные утилиты =====
    
    def get_child_type(self, parent_type: NodeType) -> Optional[NodeType]:
        """Возвращает тип дочернего элемента."""
        return get_child_type(parent_type)
    
    def get_parent_type(self, child_type: NodeType) -> Optional[NodeType]:
        """Возвращает тип родителя."""
        return get_parent_type(child_type)
    
    def can_have_children(self, node_type: NodeType) -> bool:
        """Может ли узел иметь детей."""
        return self.get_child_type(node_type) is not None
    
    def is_leaf(self, node_type: NodeType) -> bool:
        """Является ли узел листом."""
        return not self.can_have_children(node_type)
    
    # ===== Форматирование =====
    
    def format_node_id(self, node_type: NodeType, node_id: int) -> str:
        """Форматирует идентификатор узла для логирования."""
        return f"{node_type.value}#{node_id}"
    
    def parse_node_id(self, formatted: str) -> tuple:
        """
        Разбирает отформатированный идентификатор.
        
        Returns:
            tuple: (node_type, node_id)
        """
        try:
            type_str, id_str = formatted.split('#')
            return (NodeType(type_str), int(id_str))
        except:
            log.error(f"Неверный формат идентификатора: {formatted}")
            return (None, None)
    
    # ===== Статистика =====
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику работы утилит."""
        stats = self._stats.copy()
        stats['cache_size'] = len(self._details_cache)
        return stats