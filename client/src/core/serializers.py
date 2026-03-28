# client/src/core/serializers.py
"""
Преобразования идентификаторов между форматами.

Отвечает за:
- Строковый ключ ↔ структурированный идентификатор
- Форматирование для отображения (логи, UI)
- Парсинг из строк

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
- Чёткое разделение public/private API
- *_safe версии для кода, который может обработать None
- Никакой бизнес-логики, только преобразования форматов
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from .types import NodeIdentifier, NodeType
from .types.exceptions import SerializationError
from .types.nodes import NodeID, NodeKey


# ===== ВНУТРЕННИЕ ФУНКЦИИ =====
def _make_node_key(node_type: NodeType, node_id: NodeID) -> NodeKey:
    """Создаёт строковый ключ в формате "тип:id". Внутренняя."""
    return f"{node_type.value}:{node_id}"


def _parse_node_key(key: NodeKey) -> tuple[NodeType, NodeID]:
    """
    Разбирает строковый ключ. Внутренняя.

    Raises:
        SerializationError: Если ключ невалидный
    """
    if not isinstance(key, str):
        raise SerializationError(f"Ожидалась строка, получен {type(key)}")

    try:
        type_str, id_str = key.split(':', 1)
    except ValueError as e:
        raise SerializationError(f"Неверный формат ключа '{key}': ожидается 'тип:id'") from e

    try:
        node_type = NodeType(type_str)
    except ValueError as e:
        raise SerializationError(f"Неизвестный тип узла '{type_str}'") from e

    try:
        node_id = int(id_str)
    except ValueError as e:
        raise SerializationError(f"Некорректный ID '{id_str}'") from e

    return node_type, node_id


# ===== ПУБЛИЧНОЕ API =====
def identifier_to_key(identifier: NodeIdentifier) -> NodeKey:
    """
    Преобразует структурированный идентификатор в строковый ключ.

    Пример:
        >>> identifier_to_key(NodeIdentifier(NodeType.COMPLEX, 42))
        'complex:42'
    """
    return _make_node_key(identifier.node_type, identifier.node_id)


def key_to_identifier(key: NodeKey) -> NodeIdentifier:
    """
    Преобразует строковый ключ в структурированный идентификатор.

    Raises:
        SerializationError: Если ключ не может быть распарсен

    Пример:
        >>> key_to_identifier('complex:42')
        NodeIdentifier(node_type=NodeType.COMPLEX, node_id=42)
    """
    node_type, node_id = _parse_node_key(key)
    return NodeIdentifier(node_type, node_id)


def try_parse_identifier(key: NodeKey) -> Optional[NodeIdentifier]:
    """Безопасная версия key_to_identifier — возвращает None при ошибке."""
    try:
        return key_to_identifier(key)
    except SerializationError:
        return None


def format_display(identifier: NodeIdentifier) -> str:
    """Форматирует идентификатор для отображения: "ТИП#ID"."""
    return f"{identifier.node_type.value.upper()}#{identifier.node_id}"


def format_display_from_parts(node_type: NodeType, node_id: NodeID) -> str:
    """Форматирует идентификатор из частей для отображения."""
    return format_display(NodeIdentifier(node_type, node_id))


def parse_display(display: str) -> NodeIdentifier:
    """
    Разбирает отформатированный идентификатор обратно в структуру.

    Raises:
        SerializationError: Если строка не может быть распарсена

    Пример:
        >>> parse_display('COMPLEX#42')
        NodeIdentifier(node_type=NodeType.COMPLEX, node_id=42)
    """
    try:
        type_str, id_str = display.split('#', 1)
        node_type = NodeType(type_str.lower())
        node_id = int(id_str)
        return NodeIdentifier(node_type, node_id)
    except (ValueError, AttributeError) as e:
        raise SerializationError(f"Неверный формат display '{display}': ожидается 'ТИП#ID'") from e


def try_parse_display(display: str) -> Optional[NodeIdentifier]:
    """Безопасная версия parse_display — возвращает None при ошибке."""
    try:
        return parse_display(display)
    except SerializationError:
        return None