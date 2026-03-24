# client/src/core/events.py
"""
Все события приложения.

ПРАВИЛО: События не наследуются. Каждый тип события уникален.
Причина: обработчики подписываются на конкретный тип,
наследование нарушает ожидания.

Для передачи данных разного типа используйте Generic[T].
"""

from dataclasses import dataclass, field
from typing import Generic, TypeVar, Optional, List, Set, Any
from .types.nodes import NodeType
from src.core.types import NodeIdentifier
from src.core.types.event_structures import EventData

# Импорты моделей для типизации событий
from src.models import Building, Counterparty, ResponsiblePerson

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
class NodeCollapsedChanged(EventData):
    """Узел свёрнут (событие изменения состояния)."""
    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class TabChanged(EventData):
    """Переключена вкладка."""
    tab_index: int


# === СОБЫТИЯ СОСТОЯНИЯ (для контроллеров) ===
@dataclass(frozen=True, slots=True)
class CurrentSelectionChanged(EventData):
    """Изменился текущий выбранный узел."""
    selection: Optional[NodeIdentifier]


@dataclass(frozen=True, slots=True)
class ExpandedNodesChanged(EventData):
    """Изменился список раскрытых узлов."""
    expanded_nodes: Set[NodeIdentifier]


# === СОБЫТИЯ ДЕТАЛЕЙ ===
@dataclass(frozen=True, slots=True)
class NodeDetailsLoaded(EventData, Generic[T]):
    """Детальная информация о узле загружена."""
    node: NodeIdentifier
    payload: T
    context: dict  # имена родителей


@dataclass(frozen=True, slots=True)
class ChildrenLoaded(EventData, Generic[T]):
    """Дети узла загружены."""
    parent: NodeIdentifier
    children: List[T]


@dataclass(frozen=True, slots=True)
class BuildingDetailsLoaded(EventData):
    """Загружены детали корпуса с владельцем и контактами."""
    building: Building
    owner: Optional[Counterparty] = None
    responsible_persons: List[ResponsiblePerson] = field(default_factory=list)


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

# ===== События соединения =====
@dataclass(frozen=True, slots=True)
class ConnectionChanged(EventData):
    """Статус соединения изменился."""
    is_online: bool
    error: Optional[str] = None


# === СОБЫТИЯ ОБНОВЛЕНИЯ ===
@dataclass(frozen=True, slots=True)
class NodeReloaded(EventData):
    """Узел перезагружен."""
    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class VisibleNodesReloaded(EventData):
    """Все раскрытые узлы перезагружены."""
    count: int


@dataclass(frozen=True, slots=True)
class FullReloadCompleted(EventData):
    """Полная перезагрузка завершена."""
    count: int  # количество загруженных комплексов


# === СОБЫТИЯ СОЕДИНЕНИЯ ===
@dataclass(frozen=True, slots=True)
class NetworkActionsEnabled(EventData):
    """Сетевые действия разрешены (онлайн)."""
    pass


@dataclass(frozen=True, slots=True)
class NetworkActionsDisabled(EventData):
    """Сетевые действия запрещены (офлайн)."""
    pass


# === КОМАНДЫ (запросы на действие) ===
@dataclass(frozen=True, slots=True)
class RefreshRequested(EventData):
    """Запрос на обновление."""
    mode: str  # 'current', 'visible', 'full'
    node: Optional[NodeIdentifier] = None