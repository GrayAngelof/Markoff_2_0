# client/src/core/events/definitions.py
"""
Все события приложения.

ПРАВИЛО: События не наследуются. Каждый тип события уникален.
Причина: обработчики подписываются на конкретный тип,
наследование нарушает ожидания.

Для передачи данных разного типа используется Generic[T].
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, List, Optional, Set, TypeVar

from src.core.types.event_structures import EventData
from src.core.types.nodes import NodeIdentifier, NodeType


# ===== ТИПЫ =====
T = TypeVar('T')


class DataLoadedKind(str, Enum):
    """Тип загруженных данных."""

    CHILDREN = "children"   # список детей (ленивая загрузка)
    DETAILS = "details"     # детальная информация об объекте


# ===== СОБЫТИЯ =====
# ---- UI события (пользовательские действия) ----
@dataclass(frozen=True, slots=True)
class NodeSelected(EventData, Generic[T]):
    """Пользователь выбрал узел в дереве."""

    node: NodeIdentifier
    payload: Optional[T] = None  # данные узла, если уже загружены


@dataclass(frozen=True, slots=True)
class NodeExpanded(EventData):
    """Пользователь раскрыл узел в дереве."""

    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class NodeCollapsed(EventData):
    """Пользователь свернул узел в дереве."""

    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class CollapseAllRequested(EventData):
    """Запрос на сворачивание всех узлов дерева."""


@dataclass(frozen=True, slots=True)
class CurrentSelectionChanged(EventData):
    """Изменился текущий выбранный узел."""

    selection: Optional[NodeIdentifier]


@dataclass(frozen=True, slots=True)
class ExpandedNodesChanged(EventData):
    """Изменился список раскрытых узлов."""

    expanded_nodes: Set[NodeIdentifier]


@dataclass(frozen=True, slots=True)
class TabChanged(EventData):
    """Пользователь переключил вкладку в панели деталей."""

    tab_index: int


# ---- Команды (запросы на действие) ----
@dataclass(frozen=True, slots=True)
class RefreshRequested(EventData):
    """
    Запрос на обновление данных (F5, Ctrl+F5, Ctrl+Shift+F5).

    mode:
        - 'current' — обновить текущий выбранный узел
        - 'visible' — обновить все раскрытые узлы
        - 'full' — полная перезагрузка всех данных
    """

    mode: str
    node: Optional[NodeIdentifier] = None  # для mode='current'


@dataclass(frozen=True, slots=True)
class ShowDetailsPanel(EventData):
    """Показать панель деталей (скрыть заглушку)."""


# ---- События данных (результаты загрузки) ----
@dataclass(frozen=True, slots=True)
class DataLoaded(EventData, Generic[T]):
    """
    Данные загружены (из кэша или API).

    Attributes:
        node_type: Тип узла
        node_id: ID узла
        payload: Загруженные данные (DTO или список DTO)
        count: Количество загруженных элементов (для списков)
        kind: Тип загруженных данных (CHILDREN или DETAILS)
    """

    node_type: NodeType
    node_id: int
    payload: T
    count: int = 1
    kind: DataLoadedKind = DataLoadedKind.DETAILS


@dataclass(frozen=True, slots=True)
class DataError(EventData):
    """Ошибка при загрузке данных."""

    node_type: str
    node_id: int
    error: str


@dataclass(frozen=True, slots=True)
class DataInvalidated(EventData):
    """Данные помечены как устаревшие (требуют перезагрузки)."""

    node_type: NodeType
    node_id: int
    count: int = 1
    reason: Optional[str] = None


# ---- События деталей (структурированные данные для UI) ----
@dataclass(frozen=True, slots=True)
class ChildrenLoaded(EventData, Generic[T]):
    """Дочерние элементы узла загружены."""

    parent: NodeIdentifier
    children: List[T]


@dataclass(frozen=True, slots=True)
class NodeDetailsLoaded(EventData, Generic[T]):
    """Детальная информация об узле загружена."""

    node: NodeIdentifier
    payload: T
    context: dict  # имена родителей для отображения иерархии


# ---- Системные события (инфраструктура) ----
@dataclass(frozen=True, slots=True)
class ConnectionChanged(EventData):
    """Статус соединения с сервером изменился."""

    is_online: bool
    error: Optional[str] = None