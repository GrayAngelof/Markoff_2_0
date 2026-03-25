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

from typing import Final, Optional, cast, Any, Dict
from ...core.types.protocols import HasNodeType
from src.core.types import NodeType
from src.core.hierarchy import get_child_type as _get_child_type
from src.core.hierarchy import get_parent_type as _get_parent_type
from utils.logger import get_logger


# Логгер на уровне модуля
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
# МАППИНГ: имя класса → NodeType
# ============================================
# Нужен для обратной совместимости, когда у сущности нет атрибута NODE_TYPE
# (например, при работе со словарями или старыми данными)

CLASS_NAME_TO_NODETYPE: Final[Dict[str, NodeType]] = {
    "Complex": NodeType.COMPLEX,
    "Building": NodeType.BUILDING,
    "Floor": NodeType.FLOOR,
    "Room": NodeType.ROOM,
    "Counterparty": NodeType.COUNTERPARTY,
    "ResponsiblePerson": NodeType.RESPONSIBLE_PERSON,
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
log.system("Схема графа валидна")


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
    log.debug(f"get_child_type({parent_type.value}) -> {result.value if result else None}")
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
    # log.debug(f"get_parent_type({child_type.value}) -> {result.value if result else None}")
    return result


# ============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С СУЩНОСТЯМИ
# ============================================

def get_node_type(entity: Any) -> Optional[NodeType]:
    """
    Определяет NodeType по классу или атрибуту NODE_TYPE сущности.
    
    Args:
        entity: Сущность (модель или словарь)
        
    Returns:
        Optional[NodeType]: Тип узла или None, если не удалось определить
    """
    # log.debug(f"get_node_type: entity={type(entity).__name__}")
    
    # Сначала проверяем атрибут NODE_TYPE
    if hasattr(entity, 'NODE_TYPE'):
        node_type_value = entity.NODE_TYPE
        # log.debug(f"get_node_type:  NODE_TYPE атрибут: {node_type_value}")
        
        # Если это уже NodeType — возвращаем
        if isinstance(node_type_value, NodeType):
            # log.debug(f"  -> NodeType.{node_type_value.value}")
            return node_type_value
        
        # Если это строка — преобразуем
        if isinstance(node_type_value, str):
            try:
                result = NodeType(node_type_value)
                # log.debug(f"  -> NodeType.{result.value} (из строки)")
                return result
            except ValueError:
                log.warning(f"Неизвестный тип узла из строки: {node_type_value}")
                return None
    
    # Если нет NODE_TYPE, пробуем по имени класса
    class_name = type(entity).__name__
    log.debug(f"  нет NODE_TYPE, пробуем по имени класса: {class_name}")
    result = CLASS_NAME_TO_NODETYPE.get(class_name)
    if result:
        log.debug(f"  -> NodeType.{result.value} (по имени класса)")
    else:
        log.warning(f"Не удалось определить тип для класса {class_name}")
    
    return result


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
    # Получаем node_type в виде строки и NodeType
    if isinstance(entity.NODE_TYPE, str):
        type_str = entity.NODE_TYPE
        try:
            node_type_enum = NodeType(type_str)
        except ValueError:
            log.error(f"Неизвестный тип узла из строки: {type_str}")
            return None
    else:
        node_type_enum = entity.NODE_TYPE
        type_str = node_type_enum.value
    
    # Ищем поле для ID родителя
    field_name = PARENT_ID_FIELD.get(node_type_enum)
    
    if field_name is None:
        log.debug(f"{type_str} корневой (нет родителя)")
        return None
    
    # Проверяем наличие поля
    if not hasattr(entity, field_name):
        log.error(
            f"Архитектурная ошибка: сущность {type_str} "
            f"не имеет поля '{field_name}'"
        )
        raise ValueError(
            f"Архитектурная ошибка: сущность {type_str} "
            f"не имеет поля '{field_name}'"
        )
    
    value = getattr(entity, field_name)
    result = cast(Optional[int], value)
    
    # log.debug(f"get_parent_id: {type_str}#{result if result else 'None'}")
    return result