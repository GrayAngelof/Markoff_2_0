# client/src/core/serializers.py
"""
ПРЕОБРАЗОВАНИЯ ИДЕНТИФИКАТОРОВ.

Отвечает за все преобразования между различными форматами:
- Строковый ключ ↔ структурированный идентификатор
- Форматирование для отображения
- Парсинг из строк

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
- Чёткое разделение public/private API
- Функции с исключениями для безопасного кода
- *_safe версии для кода, который может обработать None
- Никакой бизнес-логики, только преобразования форматов!

ПРАВИЛА:
- make_node_key() — ВНУТРЕННЯЯ (не экспортировать)
- identifier_to_key() — публичная
- key_to_identifier() — публичная, с исключением
- try_parse_identifier() — публичная, безопасная
"""
from typing import Optional

from .types import NodeType, NodeIdentifier
from .types.exceptions import SerializationError
from .types.nodes import NodeID, NodeKey


# ============================================================
# ВНУТРЕННИЕ ФУНКЦИИ (НЕ ЭКСПОРТИРУЮТСЯ)
# ============================================================

def _make_node_key(node_type: NodeType, node_id: NodeID) -> NodeKey:
    """
    ВНУТРЕННЯЯ функция. Создаёт строковый ключ для индексации.
    Не использовать вне core!
    
    Args:
        node_type: Тип узла
        node_id: Идентификатор узла
        
    Returns:
        NodeKey: Ключ в формате "тип:id"
    """
    return f"{node_type.value}:{node_id}"


def _parse_node_key(key: NodeKey) -> tuple[NodeType, NodeID]:
    """
    ВНУТРЕННЯЯ функция. Разбирает строковый ключ.
    Не использовать вне core!
    
    Args:
        key: Ключ в формате "тип:id"
        
    Returns:
        tuple[NodeType, NodeID]: (тип, id)
        
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


# ============================================================
# ПУБЛИЧНОЕ API (экспортируется)
# ============================================================

# --- Преобразование в ключи ---

def identifier_to_key(identifier: NodeIdentifier) -> NodeKey:
    """
    Преобразует структурированный идентификатор в строковый ключ.
    
    Args:
        identifier: Структурированный идентификатор
        
    Returns:
        NodeKey: Строковый ключ вида "тип:id"
        
    Пример:
        >>> id = NodeIdentifier(NodeType.COMPLEX, 42)
        >>> identifier_to_key(id)
        'complex:42'
    """
    return _make_node_key(identifier.node_type, identifier.node_id)


# --- Преобразование из ключей (с исключением) ---

def key_to_identifier(key: NodeKey) -> NodeIdentifier:
    """
    Преобразует строковый ключ в структурированный идентификатор.
    
    Args:
        key: Ключ в формате "тип:id"
        
    Returns:
        NodeIdentifier: Структурированный идентификатор
        
    Raises:
        SerializationError: Если ключ не может быть распарсен
        
    Пример:
        >>> key_to_identifier('complex:42')
        NodeIdentifier(node_type=<NodeType.COMPLEX: 'complex'>, node_id=42)
    """
    node_type, node_id = _parse_node_key(key)
    return NodeIdentifier(node_type, node_id)


def try_parse_identifier(key: NodeKey) -> Optional[NodeIdentifier]:
    """
    Безопасная версия парсинга — возвращает None при ошибке.
    
    Args:
        key: Ключ в формате "тип:id"
        
    Returns:
        Optional[NodeIdentifier]: Идентификатор или None при ошибке
        
    Пример:
        >>> try_parse_identifier('complex:42')
        NodeIdentifier(...)
        >>> try_parse_identifier('invalid')
        None
    """
    try:
        return key_to_identifier(key)
    except SerializationError:
        return None


# --- Форматирование для отображения ---

def format_display(identifier: NodeIdentifier) -> str:
    """
    Форматирует идентификатор для отображения в логах и UI.
    
    Args:
        identifier: Структурированный идентификатор
        
    Returns:
        str: Отформатированная строка вида "ТИП#ID"
        
    Пример:
        >>> id = NodeIdentifier(NodeType.COMPLEX, 42)
        >>> format_display(id)
        'COMPLEX#42'
    """
    return f"{identifier.node_type.value.upper()}#{identifier.node_id}"


def format_display_from_parts(node_type: NodeType, node_id: NodeID) -> str:
    """
    Форматирует идентификатор из частей для отображения.
    
    Args:
        node_type: Тип узла
        node_id: Идентификатор узла
        
    Returns:
        str: Отформатированная строка вида "ТИП#ID"
    """
    return format_display(NodeIdentifier(node_type, node_id))


def parse_display(display: str) -> NodeIdentifier:
    """
    Разбирает отформатированный идентификатор обратно в структуру.
    
    Args:
        display: Строка вида "ТИП#ID"
        
    Returns:
        NodeIdentifier: Структурированный идентификатор
        
    Raises:
        SerializationError: Если строка не может быть распарсена
        
    Пример:
        >>> parse_display('COMPLEX#42')
        NodeIdentifier(...)
    """
    try:
        type_str, id_str = display.split('#', 1)
        node_type = NodeType(type_str.lower())
        node_id = int(id_str)
        return NodeIdentifier(node_type, node_id)
    except (ValueError, AttributeError) as e:
        raise SerializationError(f"Неверный формат display '{display}': ожидается 'ТИП#ID'") from e


def try_parse_display(display: str) -> Optional[NodeIdentifier]:
    """
    Безопасная версия парсинга display — возвращает None при ошибке.
    
    Args:
        display: Строка вида "ТИП#ID"
        
    Returns:
        Optional[NodeIdentifier]: Идентификатор или None
        
    Пример:
        >>> try_parse_display('COMPLEX#42')
        NodeIdentifier(...)
        >>> try_parse_display('invalid')
        None
    """
    try:
        return parse_display(display)
    except SerializationError:
        return None

