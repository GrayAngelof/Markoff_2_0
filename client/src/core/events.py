# client/src/core/events.py
"""
Константы типов событий для всего приложения.
Централизованное хранение всех типов событий обеспечивает:
- Единообразие имён
- Автодополнение в IDE
- Предотвращение опечаток
- Документирование всех возможных событий

События делятся на три логические группы:
- UI Events (команды от пользовательского интерфейса)
- System Events (факты о состоянии системы)
- Hotkey Events (горячие клавиши)
- Projection Events (события от слоя проекций)

Формат: категория.действие (например, ui.node_selected)
"""
from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class UIEvents:
    """
    События, инициируемые пользовательским интерфейсом (команды).
    Эти события говорят системе: "пользователь хочет сделать X".
    """
    
    # === Дерево объектов ===
    NODE_SELECTED = 'ui.node_selected'
    """Пользователь выбрал узел в дереве. data: {'node_type': str, 'node_id': int, 'data': object}"""
    
    NODE_EXPANDED = 'ui.node_expanded'
    """Пользователь раскрыл узел. data: {'node_type': str, 'node_id': int}"""
    
    NODE_COLLAPSED = 'ui.node_collapsed'
    """Пользователь свернул узел. data: {'node_type': str, 'node_id': int}"""
    
    # === Обновление данных ===
    REFRESH_REQUESTED = 'ui.refresh_requested'
    """Запрос на обновление данных. data: {'mode': 'current'|'visible'|'full'}"""
    
    # === Панель деталей ===
    TAB_CHANGED = 'ui.tab_changed'
    """Пользователь переключил вкладку. data: {'tab_index': int}"""
    
    # === Запросы состояния ===
    GET_SELECTED_NODE = 'ui.get_selected_node'
    """Запрос текущего выбранного узла. Ответ придёт через sys.current_selection"""
    
    GET_EXPANDED_NODES = 'ui.get_expanded_nodes'
    """Запрос списка раскрытых узлов. Ответ придёт через sys.expanded_nodes"""


class SystemEvents:
    """
    Системные события (факты).
    Эти события говорят: "произошло событие X". На них можно реагировать.
    """
    
    # === Загрузка данных ===
    DATA_LOADING = 'sys.data_loading'
    """Началась загрузка данных. data: {'node_type': str, 'node_id': int, 'parent_type': str, 'parent_id': int}"""
    
    DATA_LOADED = 'sys.data_loaded'
    """Данные успешно загружены. data: {'node_type': str, 'node_id': int, 'data': list|object, 'is_detail': bool}"""
    
    DATA_ERROR = 'sys.data_error'
    """Ошибка загрузки данных. data: {'node_type': str, 'node_id': int, 'error': str}"""
    
    # === Соединение ===
    CONNECTION_CHANGED = 'sys.connection_changed'
    """Изменилось состояние соединения. data: {'is_online': bool}"""
    
    # === Кэш и данные ===
    CACHE_UPDATED = 'sys.cache_updated'
    """Кэш обновлён. data: {'entity_type': str, 'count': int}"""
    
    # === Состояние ===
    CURRENT_SELECTION = 'sys.current_selection'
    """Ответ на запрос выбранного узла. data: {'node_type': str, 'node_id': int, 'data': object}"""
    
    EXPANDED_NODES = 'sys.expanded_nodes'
    """Ответ на запрос раскрытых узлов. data: {'nodes': list[tuple(str, int)]}"""


class HotkeyEvents:
    """
    События горячих клавиш.
    Отдельная категория, чтобы можно было легко менять привязки.
    """
    
    REFRESH_CURRENT = 'hotkey.f5'
    """F5 - обновить текущий узел"""
    
    REFRESH_VISIBLE = 'hotkey.ctrl_f5'
    """Ctrl+F5 - обновить все раскрытые узлы"""
    
    FULL_RESET = 'hotkey.ctrl_shift_f5'
    """Ctrl+Shift+F5 - полная перезагрузка"""


class ProjectionEvents:
    """
    События от слоя проекций.
    Оповещают об обновлении структур данных для отображения.
    """
    
    TREE_UPDATED = 'projection.tree_updated'
    """Дерево объектов обновлено. data: {'tree': list[TreeNode]}"""
    
    DETAILS_UPDATED = 'projection.details_updated'
    """Детальная информация обновлена. data: {'node_type': str, 'node_id': int, 'data': object}"""


# Для удобства импорта можно собрать все события в один словарь
ALL_EVENTS = {
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
}

log.debug(f"Events module initialized with {len(ALL_EVENTS)} event types")