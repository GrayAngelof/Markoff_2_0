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

from src.core.types.nodes import NodeType, NodeIdentifier
from src.core.types.event_structures import EventData

# Импорты моделей для типизации событий
from src.models import Building, Counterparty, ResponsiblePerson

T = TypeVar('T')


# ============================================================================
# UI ФАКТЫ (пользовательские действия)
# ============================================================================

@dataclass(frozen=True, slots=True)
class NodeSelected(EventData, Generic[T]):
    """
    Пользователь выбрал узел в дереве.
    
    Используется:
    - TreeController: сохраняет текущий выбранный узел
    - DetailsController: инициирует загрузку деталей
    """
    node: NodeIdentifier
    payload: Optional[T] = None  # данные узла, если уже загружены


@dataclass(frozen=True, slots=True)
class NodeExpanded(EventData):
    """
    Пользователь раскрыл узел в дереве.
    
    Используется:
    - TreeController: загружает дочерние элементы узла
    """
    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class NodeCollapsed(EventData):
    """
    Пользователь свернул узел в дереве.
    
    Используется:
    - TreeController: обновляет отображение узлов
    """
    node: NodeIdentifier


@dataclass(frozen=True, slots=True)
class TabChanged(EventData):
    """
    Пользователь переключил вкладку в панели деталей.
    
    Используется:
    - DetailsController: загружает данные для выбранной вкладки (ленивая загрузка)
    """
    tab_index: int


# ============================================================================
# КОМАНДЫ (запросы на действие)
# ============================================================================

@dataclass(frozen=True, slots=True)
class RefreshRequested(EventData):
    """
    Запрос на обновление данных (F5, Ctrl+F5, Ctrl+Shift+F5).
    
    mode:
    - 'current' — обновить текущий выбранный узел
    - 'visible' — обновить все раскрытые узлы
    - 'full' — полная перезагрузка всех данных
    
    Используется:
    - RefreshController: инициирует перезагрузку данных
    """
    mode: str  # 'current', 'visible', 'full'
    node: Optional[NodeIdentifier] = None  # для mode='current'

@dataclass(frozen=True, slots=True)
class ShowDetailsPanel(EventData):
    """
    Показать панель деталей (скрыть заглушку).
    
    Используется:
    - CentralWidget: переключает видимость PlaceholderWidget → DetailsPanel
    """
    pass


# ============================================================================
# СОБЫТИЯ ДАННЫХ (результаты загрузки)
# ============================================================================

@dataclass(frozen=True, slots=True)
class DataLoaded(EventData, Generic[T]):
    """
    Данные загружены (из кэша или API).
    
    Используется:
    - TreeController: получает детей узла
    - DetailsController: получает детали узла
    """
    node_type: str
    node_id: int
    payload: T
    count: int = 1


@dataclass(frozen=True, slots=True)
class DataError(EventData):
    """
    Ошибка при загрузке данных.
    
    Используется:
    - Контроллеры: логируют ошибку, показывают уведомление
    """
    node_type: str
    node_id: int
    error: str


@dataclass(frozen=True, slots=True)
class DataInvalidated(EventData):
    """
    Данные помечены как устаревшие (требуют перезагрузки).
    
    Используется:
    - TreeController: помечает узлы для перезагрузки при следующем раскрытии
    - DetailsController: обновляет кэш, перезагружает при необходимости
    """
    node_type: NodeType
    node_id: int
    count: int = 1
    reason: Optional[str] = None


# ============================================================================
# СОБЫТИЯ ДЕТАЛЕЙ (структурированные данные для UI)
# ============================================================================

@dataclass(frozen=True, slots=True)
class ChildrenLoaded(EventData, Generic[T]):
    """
    Дочерние элементы узла загружены.
    
    Используется:
    - TreeModel: добавляет дочерние узлы в дерево
    """
    parent: NodeIdentifier
    children: List[T]


@dataclass(frozen=True, slots=True)
class NodeDetailsLoaded(EventData, Generic[T]):
    """
    Детальная информация об узле загружена.
    
    Используется:
    - DetailsPanel: отображает информацию в панели деталей
    """
    node: NodeIdentifier
    payload: T
    context: dict  # имена родителей для отображения иерархии


# ============================================================================
# СИСТЕМНЫЕ СОБЫТИЯ (инфраструктура)
# ============================================================================

@dataclass(frozen=True, slots=True)
class ConnectionChanged(EventData):
    """
    Статус соединения с сервером изменился.
    
    Используется:
    - StatusBar: обновляет индикатор соединения
    - Toolbar: обновляет состояние кнопок
    - ConnectionController: управляет доступностью сетевых действий
    """
    is_online: bool
    error: Optional[str] = None