# client/src/core/serializers.py
"""
ПРЕОБРАЗОВАНИЯ ИДЕНТИФИКАТОРОВ.

Отвечает за все преобразования между различными форматами:
- Строковый ключ ↔ структурированный идентификатор
- Форматирование для отображения
- Парсинг из строк

Никакой бизнес-логики, только преобразования форматов!
"""
from typing import Optional

from .types import NodeType, NodeID, NodeKey, NodeIdentifier
from .types.exceptions import SerializationError

# ===== Сериализация в строковые ключи =====

def make_node_key(node_type: NodeType, node_id: NodeID) -> NodeKey:
    """
    Создаёт строковый ключ для индексации.
    
    Args:
        node_type: Тип узла
        node_id: Идентификатор узла
        
    Returns:
        NodeKey: Ключ в формате "тип:id"
        
    Пример:
        >>> make_node_key(NodeType.COMPLEX, 42)
        'complex:42'
        
    Логирование:
        - debug: созданный ключ
    """
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    key = f"{node_type.value}:{node_id}"
    log.debug(f"🔑 make_node_key: {key}")
    return key


def identifier_to_key(identifier: NodeIdentifier) -> NodeKey:
    """
    Преобразует структурированный идентификатор в строковый ключ.
    
    Args:
        identifier: Структурированный идентификатор
        
    Returns:
        NodeKey: Строковый ключ
        
    Пример:
        >>> id = NodeIdentifier(NodeType.COMPLEX, 42)
        >>> identifier_to_key(id)
        'complex:42'
    """
    return make_node_key(identifier.node_type, identifier.node_id)


# ===== Десериализация из строковых ключей =====

def parse_node_key(key: NodeKey) -> Optional[NodeIdentifier]:
    """
    Разбирает строковый ключ в структурированный идентификатор.
    
    Args:
        key: Ключ в формате "тип:id"
        
    Returns:
        Optional[NodeIdentifier]: Структурированный идентификатор или None
        
    Пример:
        >>> parse_node_key('complex:42')
        NodeIdentifier(node_type=<NodeType.COMPLEX: 'complex'>, node_id=42)
        >>> parse_node_key('invalid')
        None
        
    Логирование:
        - debug: успешный разбор
        - warning: ошибки формата
    """
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    if not isinstance(key, str):
        log.warning(f"⚠️ parse_node_key: ожидалась строка, получен {type(key)}")
        return None
    
    try:
        type_str, id_str = key.split(':', 1)
        
        # Преобразуем строку в NodeType
        try:
            node_type = NodeType(type_str)
        except ValueError:
            log.warning(f"⚠️ parse_node_key: неизвестный тип '{type_str}'")
            return None
        
        # Преобразуем строку в int
        try:
            node_id = int(id_str)
        except ValueError:
            log.warning(f"⚠️ parse_node_key: некорректный ID '{id_str}'")
            return None
        
        identifier = NodeIdentifier(node_type, node_id)
        log.debug(f"🔍 parse_node_key: {key} → {identifier}")
        return identifier
        
    except ValueError as e:
        log.warning(f"⚠️ parse_node_key: неверный формат '{key}': {e}")
        return None


def key_to_identifier(key: NodeKey) -> Optional[NodeIdentifier]:
    """
    Псевдоним для parse_node_key (для симметрии).
    """
    return parse_node_key(key)


def safe_parse_node_key(key: NodeKey) -> NodeIdentifier:
    """
    Безопасный парсинг с исключением при ошибке.
    
    Args:
        key: Ключ в формате "тип:id"
        
    Returns:
        NodeIdentifier: Структурированный идентификатор
        
    Raises:
        SerializationError: Если ключ не может быть распарсен
        
    Пример:
        >>> safe_parse_node_key('complex:42')
        NodeIdentifier(...)
        >>> safe_parse_node_key('invalid')
        SerializationError: Не удалось распарсить ключ 'invalid'
    """
    result = parse_node_key(key)
    if result is None:
        raise SerializationError(f"Не удалось распарсить ключ '{key}'")
    return result


# ===== Форматирование для отображения =====

def format_display_id(identifier: NodeIdentifier) -> str:
    """
    Форматирует идентификатор для отображения в логах и UI.
    
    Args:
        identifier: Структурированный идентификатор
        
    Returns:
        str: Отформатированная строка вида "ТИП#ID"
        
    Пример:
        >>> id = NodeIdentifier(NodeType.COMPLEX, 42)
        >>> format_display_id(id)
        'COMPLEX#42'
        
    Логирование:
        - debug: отформатированная строка
    """
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    formatted = f"{identifier.node_type.value.upper()}#{identifier.node_id}"
    log.debug(f"🔤 format_display_id: {formatted}")
    return formatted


def format_display_from_parts(node_type: NodeType, node_id: NodeID) -> str:
    """
    Форматирует идентификатор из частей для отображения.
    
    Args:
        node_type: Тип узла
        node_id: Идентификатор узла
        
    Returns:
        str: Отформатированная строка вида "ТИП#ID"
    """
    return format_display_id(NodeIdentifier(node_type, node_id))


def parse_display_id(display: str) -> Optional[NodeIdentifier]:
    """
    Разбирает отформатированный идентификатор обратно в структуру.
    
    Args:
        display: Строка вида "ТИП#ID"
        
    Returns:
        Optional[NodeIdentifier]: Структурированный идентификатор или None
        
    Пример:
        >>> parse_display_id('COMPLEX#42')
        NodeIdentifier(...)
        
    Логирование:
        - debug: успешный разбор
        - warning: ошибки формата
    """
    from utils.logger import get_logger
    log = get_logger(__name__)
    
    try:
        type_str, id_str = display.split('#', 1)
        # Приводим к нижнему регистру для поиска в Enum
        node_type = NodeType(type_str.lower())
        node_id = int(id_str)
        
        identifier = NodeIdentifier(node_type, node_id)
        log.debug(f"🔍 parse_display_id: {display} → {identifier}")
        return identifier
        
    except (ValueError, AttributeError) as e:
        log.warning(f"⚠️ parse_display_id: неверный формат '{display}': {e}")
        return None