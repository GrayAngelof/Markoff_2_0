# client/src/core/events.py
"""
Все события приложения.

ПРАВИЛО: События не наследуются. Каждый тип события уникален.
Причина: обработчики подписываются на конкретный тип,
наследование нарушает ожидания.

Для передачи данных разного типа используйте Generic[T].
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
from .types.nodes import NodeType
from core.types import NodeIdentifier
from core.types.event_structures import EventData

T = TypeVar('T')


# === UI ФАКТЫ ===
@dataclass(frozen=True, slots=True)
class NodeSelected(EventData, Generic[T]):
    """Пользователь выбрал узел."""
    node: NodeIdentifier
    payload: Optional[T] = None


@dataclass(frozen=True, slots=True)
class NodeExpanded(EventData):
    """Узел раскрыт."""
    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class NodeCollapsed(EventData):
    """Узел свёрнут."""
    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class TabChanged(EventData):
    """Переключена вкладка."""
    tab_index: int


# === СИСТЕМНЫЕ ФАКТЫ ===
@dataclass(frozen=True, slots=True)
class DataLoading(EventData):
    """Началась загрузка данных."""
    node_type: str
    node_id: int
    parent_type: Optional[str] = None
    parent_id: Optional[int] = None


@dataclass(frozen=True, slots=True)
class DataLoaded(EventData, Generic[T]):
    """Данные загружены."""
    node_type: str
    node_id: int
    payload: T
    count: int = 1

@dataclass(frozen=True, slots=True)
class DataInvalidated(EventData):
    """Данные помечены как невалидные."""
    node_type: NodeType
    node_id: int
    count: int = 1
    reason: Optional[str] = None


@dataclass(frozen=True, slots=True)
class DataError(EventData):
    """Ошибка загрузки данных."""
    node_type: str
    node_id: int
    error: str


@dataclass(frozen=True, slots=True)
class ConnectionChanged(EventData):
    """Изменился статус соединения."""
    is_online: bool


# === КОМАНДЫ (запросы на действие) ===
@dataclass(frozen=True, slots=True)
class RefreshRequested(EventData):
    """Запрос на обновление."""
    mode: str  # 'current', 'visible', 'full'
    node: Optional[NodeIdentifier] = None