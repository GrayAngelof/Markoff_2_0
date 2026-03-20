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

from typing import Final, Optional, cast

from core.types import NodeType, HasNodeType
from core.hierarchy import get_child_type as _get_child_type
from core.hierarchy import get_parent_type as _get_parent_type
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

def get_node_type(entity: HasNodeType) -> NodeType:
    """
    Возвращает тип сущности.
    
    Args:
        entity: Сущность, реализующая протокол HasNodeType
        
    Returns:
        NodeType: Тип узла
        
    Пример:
        >>> get_node_type(complex_obj)
        NodeType.COMPLEX
    """
    result = entity.NODE_TYPE
    log.debug(f"🏷️ get_node_type({type(entity).__name__}) → {result.value}")
    return result


def get_parent_id(entity: HasNodeType) -> Optional[int]:
    """
    Извлекает ID родителя из сущности.
    
    Использует PARENT_ID_FIELD для определения имени поля,
    по которому нужно получить значение.
    
    Args:
        entity: Сущность, реализующая протокол HasNodeType
        
    Returns:
        Optional[int]: ID родителя или None, если:
            - у сущности нет родителя (корневой тип)
            - поле с родителем отсутствует
            - значение поля равно None
            
    Raises:
        ValueError: Если сущность не имеет поля, указанного в PARENT_ID_FIELD.
                     Это архитектурная ошибка — нарушение контракта.
        
    Пример:
        >>> building = Building(complex_id=42)
        >>> get_parent_id(building)
        42
        
        >>> complex = Complex(name="Северный")
        >>> get_parent_id(complex)
        None
    """
    node_type = entity.NODE_TYPE
    log.debug(f"🔍 get_parent_id: тип={node_type.value}, сущность={type(entity).__name__}")
    
    field_name = PARENT_ID_FIELD.get(node_type)
    if field_name is None:
        log.debug(f"ℹ️ get_parent_id: тип {node_type.value} корневой (нет родителя)")
        return None
    
    # Проверка наличия поля — архитектурный контракт
    if not hasattr(entity, field_name):
        log.error(
            f"❌ Архитектурная ошибка: сущность {node_type.value} "
            f"не имеет поля '{field_name}'"
        )
        raise ValueError(
            f"Архитектурная ошибка: сущность {node_type.value} "
            f"не имеет поля '{field_name}'. "
            f"Проверьте PARENT_ID_FIELD в {__file__} "
            f"и модель {type(entity).__name__}."
        )
    
    value = getattr(entity, field_name)
    # Приводим к int с помощью cast для строгой типизации
    result = cast(Optional[int], value)
    
    log.debug(f"📎 get_parent_id: {node_type.value}#{result if result else 'None'}")
    return result