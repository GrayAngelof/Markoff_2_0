# client/src/data/graph/schema.py
"""
Схема графа — определяет связи между типами сущностей.

Это самый базовый компонент Data слоя. Он описывает:
- Какие типы могут быть родителями для каких
- По какому полю в сущности находится ID родителя
- Как навигировать по иерархии

Никакой бизнес-логики, только декларативные правила.
Все правила берутся из core.hierarchy — священной коровы, которая никогда не меняется.

Зависимости:
    - core.types.NodeType — типы узлов
    - core.types.HasNodeType — протокол для типизации
    - core.hierarchy — правила иерархии

Потребители:
    - graph/relations.py — для построения индексов связей
    - graph/validity.py — для веточной инвалидации
    - entity_graph.py — для извлечения parent_id при add_or_update

ВАЖНО:
Все сущности, реализующие HasNodeType,
обязаны иметь атрибуты, указанные в PARENT_ID_FIELD.
Нарушение — архитектурная ошибка, которая должна быть обнаружена
на этапе разработки и приведет к исключению.
"""

from typing import Final, Optional, cast, Any
from ...core.types.protocols import HasNodeType
from src.core.types import NodeType
from src.core.hierarchy import get_child_type as _get_child_type
from src.core.hierarchy import get_parent_type as _get_parent_type
from utils.logger import get_logger


# Логгер на уровне модуля (один экземпляр для всех функций)
log = get_logger(__name__)


# ============================================
# МАППИНГ: тип сущности → поле с ID родителя
# ============================================
# Это нужно, чтобы при сохранении сущности в граф
# автоматически определить её родителя и обновить индексы.
# None означает, что тип является корневым (не имеет родителя).
#
# ВАЖНО: Все модели, перечисленные здесь, обязаны иметь
# соответствующие поля. Это архитектурное соглашение.
# Final защищает от случайного изменения в рантайме.

PARENT_ID_FIELD: Final[dict[NodeType, Optional[str]]] = {
    # Физическая структура
    NodeType.COMPLEX: None,                      # комплексы — корень дерева
    NodeType.BUILDING: "complex_id",             # корпус → комплекс
    NodeType.FLOOR: "building_id",               # этаж → корпус
    NodeType.ROOM: "floor_id",                   # помещение → этаж
    
    # Контрагенты и контакты
    NodeType.COUNTERPARTY: None,                 # контрагенты — корень
    NodeType.RESPONSIBLE_PERSON: "counterparty_id",  # контакт → контрагент
}


# ============================================
# ВАЛИДАЦИЯ СХЕМЫ (выполняется при импорте)
# ============================================

def _validate_schema() -> None:
    """
    Проверяет, что все типы NodeType имеют маппинг в PARENT_ID_FIELD.
    
    Это критическая проверка, которая обнаруживает ошибки конфигурации
    на этапе импорта модуля, а не в рантайме.
    
    Raises:
        RuntimeError: Если какой-либо тип отсутствует в PARENT_ID_FIELD
    """
    all_types = set(NodeType)
    mapped_types = set(PARENT_ID_FIELD.keys())
    missing = all_types - mapped_types
    
    if missing:
        missing_names = [t.value for t in missing]
        raise RuntimeError(
            f"Схема графа неполна: отсутствуют маппинги для типов: {missing_names}\n"
            f"Добавьте их в PARENT_ID_FIELD в {__file__}"
        )


# Выполняем валидацию при импорте модуля
_validate_schema()


# ============================================
# ОБЕРТКИ НАД core.hierarchy
# ============================================
# Вынесены для единообразия доступа.
# Все компоненты Data слоя используют эти функции,
# а не импортируют core напрямую.
# Это позволяет:
#   1. Единое место для логирования (если понадобится)
#   2. Защиту от случайного изменения core
#   3. Упрощение моков в тестах

def get_child_type(parent_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип дочернего элемента для данного родителя.
    
    Args:
        parent_type: Тип родительского узла
        
    Returns:
        Optional[NodeType]: Тип дочернего узла или None, если у типа нет детей
        
    Пример:
        >>> get_child_type(NodeType.COMPLEX)
        NodeType.BUILDING
        
        >>> get_child_type(NodeType.ROOM)
        None
    """
    result = _get_child_type(parent_type)
    log.debug(f"🔽 get_child_type({parent_type.value}) → {result.value if result else None}")
    return result


def get_parent_type(child_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип родителя для данного дочернего элемента.
    
    Args:
        child_type: Тип дочернего узла
        
    Returns:
        Optional[NodeType]: Тип родительского узла или None, если тип корневой
        
    Пример:
        >>> get_parent_type(NodeType.ROOM)
        NodeType.FLOOR
    """
    result = _get_parent_type(child_type)
    log.debug(f"🔼 get_parent_type({child_type.value}) → {result.value if result else None}")
    return result


# ============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С СУЩНОСТЯМИ
# ============================================

def get_node_type(entity: Any) -> Optional[NodeType]:
    """
    Возвращает тип сущности по атрибуту NODE_TYPE.
    
    Args:
        entity: Сущность (должна иметь атрибут NODE_TYPE)
        
    Returns:
        NodeType: Тип узла или None, если определить не удалось
        
    Пример:
        >>> complex_obj = Complex(id=1, name="Test")
        >>> get_node_type(complex_obj)
        NodeType.COMPLEX
    """
    if not hasattr(entity, 'NODE_TYPE'):
        log.warning(f"Сущность {type(entity).__name__} не имеет атрибута NODE_TYPE")
        return None
    
    node_type_str = entity.NODE_TYPE
    
    try:
        result = NodeType(node_type_str)
        log.debug(f"🏷️ get_node_type({type(entity).__name__}) → {result.value}")
        return result
    except ValueError as e:
        log.error(f"Неизвестный тип узла: {node_type_str} для {type(entity).__name__}")
        return None


def get_parent_id(entity: HasNodeType) -> Optional[int]:
    """
    Извлекает ID родителя из сущности.
    
    Использует PARENT_ID_FIELD для определения имени поля,
    по которому нужно получить значение.
    
    Args:
        entity: Сущность, реализующая протокол HasNodeType
        
    Returns:
        Optional[int]: ID родителя или None
    """
    node_type = entity.NODE_TYPE
    
    # 🔧 ИСПРАВЛЕНИЕ: node_type может быть строкой или NodeType
    if isinstance(node_type, str):
        type_str = node_type
    else:
        type_str = node_type.value
    
    log.debug(f"🔍 get_parent_id: тип={type_str}, сущность={type(entity).__name__}")
    
    field_name = PARENT_ID_FIELD.get(node_type)
    if field_name is None:
        log.debug(f"ℹ️ get_parent_id: тип {type_str} корневой (нет родителя)")
        return None
    
    # Проверка наличия поля — архитектурный контракт
    if not hasattr(entity, field_name):
        log.error(
            f"❌ Архитектурная ошибка: сущность {type_str} "
            f"не имеет поля '{field_name}'"
        )
        raise ValueError(
            f"Архитектурная ошибка: сущность {type_str} "
            f"не имеет поля '{field_name}'"
        )
    
    value = getattr(entity, field_name)
    result = cast(Optional[int], value)
    
    log.debug(f"📎 get_parent_id: {type_str}#{result if result else 'None'}")
    return result