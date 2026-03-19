# client/src/core/event_constants.py
"""
КОНСТАНТЫ СОБЫТИЙ.

ЕДИНСТВЕННОЕ место определения строковых констант событий.
Все события в приложении должны импортироваться отсюда.

Категории:
- UI: команды от пользовательского интерфейса
- SYSTEM: факты о состоянии системы
- HOTKEY: горячие клавиши
- PROJECTION: события от слоя проекций
- CUSTOM: пользовательские события
"""
from typing import Dict


class UIEvents:
    """События пользовательского интерфейса (команды)."""
    
    NODE_SELECTED = 'ui.node_selected'
    """Пользователь выбрал узел. Data: NodeSelectedEvent"""
    
    NODE_EXPANDED = 'ui.node_expanded'
    """Пользователь раскрыл узел. Data: NodeExpandedEvent"""
    
    NODE_COLLAPSED = 'ui.node_collapsed'
    """Пользователь свернул узел. Data: NodeCollapsedEvent"""
    
    REFRESH_REQUESTED = 'ui.refresh_requested'
    """Запрос на обновление. Data: RefreshRequestedEvent"""
    
    TAB_CHANGED = 'ui.tab_changed'
    """Переключение вкладки. Data: TabChangedEvent"""
    
    GET_SELECTED_NODE = 'ui.get_selected_node'
    """Запрос текущего узла. Data: EmptyEvent"""
    
    GET_EXPANDED_NODES = 'ui.get_expanded_nodes'
    """Запрос раскрытых узлов. Data: EmptyEvent"""


class SystemEvents:
    """Системные события (факты)."""
    
    DATA_LOADING = 'sys.data_loading'
    """Начало загрузки данных. Data: DataLoadingEvent"""
    
    DATA_LOADED = 'sys.data_loaded'
    """Завершение загрузки. Data: DataLoadedEvent"""
    
    DATA_ERROR = 'sys.data_error'
    """Ошибка загрузки. Data: DataErrorEvent"""
    
    CONNECTION_CHANGED = 'sys.connection_changed'
    """Изменение соединения. Data: ConnectionChangedEvent"""
    
    CACHE_UPDATED = 'sys.cache_updated'
    """Обновление кэша. Data: CacheUpdatedEvent"""
    
    CURRENT_SELECTION = 'sys.current_selection'
    """Ответ на запрос выбранного узла. Data: CurrentSelectionEvent"""
    
    EXPANDED_NODES = 'sys.expanded_nodes'
    """Ответ на запрос раскрытых узлов. Data: ExpandedNodesEvent"""


class HotkeyEvents:
    """События горячих клавиш."""
    
    REFRESH_CURRENT = 'hotkey.f5'
    """F5 - обновить текущий узел. Data: EmptyEvent"""
    
    REFRESH_VISIBLE = 'hotkey.ctrl_f5'
    """Ctrl+F5 - обновить раскрытые узлы. Data: EmptyEvent"""
    
    FULL_RESET = 'hotkey.ctrl_shift_f5'
    """Ctrl+Shift+F5 - полная перезагрузка. Data: EmptyEvent"""


class ProjectionEvents:
    """События от слоя проекций."""
    
    TREE_UPDATED = 'projection.tree_updated'
    """Дерево обновлено. Data: TreeUpdatedEvent"""
    
    DETAILS_UPDATED = 'projection.details_updated'
    """Детали обновлены. Data: DetailsUpdatedEvent"""


class CustomEvents:
    """Пользовательские события."""
    
    BUILDING_OWNER_LOADED = 'custom.building_owner_loaded'
    """Владелец корпуса загружен. Data: BuildingOwnerLoadedEvent"""
    
    NODE_DETAILS_LOADED = 'custom.node_details_loaded'
    """Детали узла загружены. Data: NodeDetailsLoadedEvent"""
    
    SHOW_ERROR = 'custom.show_error'
    """Показать ошибку. Data: ShowErrorEvent"""
    
    SHOW_CONFIRMATION = 'custom.show_confirmation'
    """Показать подтверждение. Data: ShowConfirmationEvent"""
    
    SHOW_MESSAGE = 'custom.show_message'
    """Показать сообщение. Data: ShowMessageEvent"""


# Для удобства импорта собираем все события в один словарь
ALL_EVENTS: Dict[str, str] = {
    # UI Events
    'ui.node_selected': UIEvents.NODE_SELECTED,
    'ui.node_expanded': UIEvents.NODE_EXPANDED,
    'ui.node_collapsed': UIEvents.NODE_COLLAPSED,
    'ui.refresh_requested': UIEvents.REFRESH_REQUESTED,
    'ui.tab_changed': UIEvents.TAB_CHANGED,
    'ui.get_selected_node': UIEvents.GET_SELECTED_NODE,
    'ui.get_expanded_nodes': UIEvents.GET_EXPANDED_NODES,
    
    # System Events
    'sys.data_loading': SystemEvents.DATA_LOADING,
    'sys.data_loaded': SystemEvents.DATA_LOADED,
    'sys.data_error': SystemEvents.DATA_ERROR,
    'sys.connection_changed': SystemEvents.CONNECTION_CHANGED,
    'sys.cache_updated': SystemEvents.CACHE_UPDATED,
    'sys.current_selection': SystemEvents.CURRENT_SELECTION,
    'sys.expanded_nodes': SystemEvents.EXPANDED_NODES,
    
    # Hotkey Events
    'hotkey.f5': HotkeyEvents.REFRESH_CURRENT,
    'hotkey.ctrl_f5': HotkeyEvents.REFRESH_VISIBLE,
    'hotkey.ctrl_shift_f5': HotkeyEvents.FULL_RESET,
    
    # Projection Events
    'projection.tree_updated': ProjectionEvents.TREE_UPDATED,
    'projection.details_updated': ProjectionEvents.DETAILS_UPDATED,
    
    # Custom Events
    'custom.building_owner_loaded': CustomEvents.BUILDING_OWNER_LOADED,
    'custom.node_details_loaded': CustomEvents.NODE_DETAILS_LOADED,
    'custom.show_error': CustomEvents.SHOW_ERROR,
    'custom.show_confirmation': CustomEvents.SHOW_CONFIRMATION,
    'custom.show_message': CustomEvents.SHOW_MESSAGE,
}

# Логируем загрузку
from utils.logger import get_logger
log = get_logger(__name__)
log.success(f"✅ event_constants.py загружен: {len(ALL_EVENTS)} событий")