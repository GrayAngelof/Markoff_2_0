# client/src/data/graph/schema.py
"""
Схема графа — определяет связи между типами сущностей.

Это самый базовый компонент Data слоя. Он описывает:
- Какие типы могут быть родителями для каких
- По какому полю в сущности находится ID родителя
- Как навигировать по иерархии

Никакой бизнес-логики, только декларативные правила.
Все правила берутся из core.hierarchy — священной коровы, которая никогда не меняется.

ВАЖНО:
Все сущности, реализующие HasNodeType,
обязаны иметь атрибуты, указанные в PARENT_ID_FIELD.
Нарушение — архитектурная ошибка.
"""

# ===== ИМПОРТЫ =====
from typing import Any, Dict, Final, Optional, cast

from src.core.rules.hierarchy import get_child_type as _get_child_type
from src.core.rules.hierarchy import get_parent_type as _get_parent_type
from src.core.types import NodeType
from src.core.types.protocols import HasNodeType
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

# Маппинг: тип сущности → поле с ID родителя
# None означает, что тип является корневым (не имеет родителя)
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

# Маппинг: имя класса → NodeType (для обратной совместимости)
CLASS_NAME_TO_NODETYPE: Final[Dict[str, NodeType]] = {
    "Complex": NodeType.COMPLEX,
    "Building": NodeType.BUILDING,
    "Floor": NodeType.FLOOR,
    "Room": NodeType.ROOM,
    "Counterparty": NodeType.COUNTERPARTY,
    "ResponsiblePerson": NodeType.RESPONSIBLE_PERSON,
}


# ===== ВНУТРЕННИЕ ФУНКЦИИ =====
def _validate_schema() -> None:
    """
    Проверяет, что все типы NodeType имеют маппинг в PARENT_ID_FIELD.

    Вызывается при импорте модуля.
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


_validate_schema()
log.info(f"Схема графа валидна: {len(PARENT_ID_FIELD)} типов")


# ===== ОБЁРТКИ НАД core.hierarchy =====
def get_child_type(parent_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип дочернего элемента для данного родителя.

    Returns:
        None если у типа нет детей
    """
    result = _get_child_type(parent_type)
    log.debug(f"get_child_type({parent_type.value}) -> {result.value if result else None}")
    return result


def get_parent_type(child_type: NodeType) -> Optional[NodeType]:
    """
    Возвращает тип родителя для данного дочернего элемента.

    Returns:
        None если тип корневой
    """
    result = _get_parent_type(child_type)
    log.debug(f"get_parent_type({child_type.value}) -> {result.value if result else None}")
    return result


# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С СУЩНОСТЯМИ =====
def get_node_type(entity: Any) -> Optional[NodeType]:
    """
    Определяет NodeType по классу или атрибуту NODE_TYPE сущности.

    Returns:
        None если не удалось определить тип
    """
    # Сначала проверяем атрибут NODE_TYPE
    if hasattr(entity, 'NODE_TYPE'):
        node_type_value = entity.NODE_TYPE

        if isinstance(node_type_value, NodeType):
            return node_type_value

        if isinstance(node_type_value, str):
            try:
                return NodeType(node_type_value)
            except ValueError:
                log.warning(f"Неизвестный тип узла из строки: {node_type_value}")
                return None

    # Если нет NODE_TYPE, пробуем по имени класса
    class_name = type(entity).__name__
    result = CLASS_NAME_TO_NODETYPE.get(class_name)
    if result is None:
        log.warning(f"Не удалось определить тип для класса {class_name}")

    return result


def get_parent_id(entity: HasNodeType) -> Optional[int]:
    """
    Извлекает ID родителя из сущности.

    Использует PARENT_ID_FIELD для определения имени поля.

    Raises:
        ValueError: Если у сущности отсутствует обязательное поле
    """
    # Определяем NodeType
    if isinstance(entity.NODE_TYPE, str):
        type_str = entity.NODE_TYPE
        try:
            node_type_enum = NodeType(type_str)
        except ValueError:
            log.error(f"Неизвестный тип узла из строки: {type_str}")
            return None
    else:
        node_type_enum = entity.NODE_TYPE

    # Ищем поле для ID родителя
    field_name = PARENT_ID_FIELD.get(node_type_enum)

    if field_name is None:
        log.debug(f"{node_type_enum.value} корневой (нет родителя)")
        return None

    # Проверяем наличие поля
    if not hasattr(entity, field_name):
        log.error(
            f"Архитектурная ошибка: сущность {node_type_enum.value} "
            f"не имеет поля '{field_name}'"
        )
        raise ValueError(
            f"Архитектурная ошибка: сущность {node_type_enum.value} "
            f"не имеет поля '{field_name}'"
        )

    return cast(Optional[int], getattr(entity, field_name))