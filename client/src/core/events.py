# client/src/core/events.py
"""
ЦЕНТРАЛИЗОВАННЫЙ РЕЕСТР ВСЕХ СОБЫТИЙ ПРИЛОЖЕНИЯ.

Это ЕДИНСТВЕННОЕ место, где определяются строковые константы событий.
Никаких магических строк в коде! Все события импортируются отсюда.

Категории событий:
- UI Events: команды от пользовательского интерфейса
- System Events: факты о состоянии системы
- Hotkey Events: горячие клавиши
- Projection Events: события от слоя проекций
- Custom Events: все остальные события приложения

Правила:
1. Каждое событие должно быть задокументировано с форматом данных
2. Группировка по категориям для удобства навигации
3. ALL_EVENTS словарь для отладки и автоматизации
"""
from typing import Dict, Any

from utils.logger import get_logger

# Создаём логгер для этого модуля
log = get_logger(__name__)


class UIEvents:
    """
    События, инициируемые пользовательским интерфейсом (команды).
    
    Формат данных для всех событий:
    {
        'node_type': str или NodeType,  # Тип узла
        'node_id': int,                  # ID узла
        'data': Any,                      # Дополнительные данные (опционально)
        'source': str                      # Источник события (заполняется автоматически)
    }
    """
    
    # === Дерево объектов ===
    NODE_SELECTED = 'ui.node_selected'
    """
    Пользователь выбрал узел в дереве.
    
    Data: {
        'node_type': NodeType,  # Тип выбранного узла
        'node_id': int,          # ID выбранного узла
        'data': object,          # Данные узла (могут быть неполными)
        'context': dict          # Контекст (имена родителей)
    }
    """
    
    NODE_EXPANDED = 'ui.node_expanded'
    """
    Пользователь раскрыл узел (показал детей).
    
    Data: {
        'node_type': NodeType,
        'node_id': int
    }
    """
    
    NODE_COLLAPSED = 'ui.node_collapsed'
    """
    Пользователь свернул узел (скрыл детей).
    
    Data: {
        'node_type': NodeType,
        'node_id': int
    }
    """
    
    # === Обновление данных ===
    REFRESH_REQUESTED = 'ui.refresh_requested'
    """
    Запрос на обновление данных.
    
    Data: {
        'mode': 'current' | 'visible' | 'full',  # Режим обновления
        'node_type': NodeType,                     # Для mode='current'
        'node_id': int                              # Для mode='current'
    }
    """
    
    # === Панель деталей ===
    TAB_CHANGED = 'ui.tab_changed'
    """
    Пользователь переключил вкладку в панели деталей.
    
    Data: {
        'tab_index': int,
        'tab_name': str
    }
    """
    
    # === Запросы состояния ===
    GET_SELECTED_NODE = 'ui.get_selected_node'
    """
    Запрос текущего выбранного узла.
    Ответ придёт через SystemEvents.CURRENT_SELECTION
    
    Data: {}  # без данных
    """
    
    GET_EXPANDED_NODES = 'ui.get_expanded_nodes'
    """
    Запрос списка раскрытых узлов.
    Ответ придёт через SystemEvents.EXPANDED_NODES
    
    Data: {}  # без данных
    """


class SystemEvents:
    """
    Системные события (факты о состоянии системы).
    На эти события можно реагировать, но нельзя их инициировать напрямую.
    """
    
    # === Загрузка данных ===
    DATA_LOADING = 'sys.data_loading'
    """
    Началась загрузка данных.
    
    Data: {
        'node_type': NodeType,      # Тип загружаемого узла
        'node_id': int,              # ID загружаемого узла
        'parent_type': NodeType,     # Тип родителя
        'parent_id': int,             # ID родителя
        'timestamp': float            # Время начала
    }
    """
    
    DATA_LOADED = 'sys.data_loaded'
    """
    Данные успешно загружены.
    
    Data: {
        'node_type': NodeType,
        'node_id': int,
        'data': list | object,        # Загруженные данные
        'parent_type': NodeType,      # Тип родителя
        'parent_id': int,              # ID родителя
        'count': int,                  # Количество элементов
        'is_detail': bool,             # Детальные данные?
        'duration_ms': float            # Время загрузки в мс
    }
    """
    
    DATA_ERROR = 'sys.data_error'
    """
    Ошибка загрузки данных.
    
    Data: {
        'node_type': NodeType,
        'node_id': int,
        'error': str,                   # Текст ошибки
        'parent_type': NodeType,        # Тип родителя
        'parent_id': int,                # ID родителя
        'timestamp': float                # Время ошибки
    }
    """
    
    # === Соединение ===
    CONNECTION_CHANGED = 'sys.connection_changed'
    """
    Изменилось состояние соединения с сервером.
    
    Data: {
        'is_online': bool,
        'was_online': bool,              # Предыдущее состояние
        'timestamp': str,                 # Время изменения
        'error': str                       # Если был offline - причина
    }
    """
    
    # === Кэш и данные ===
    CACHE_UPDATED = 'sys.cache_updated'
    """
    Кэш обновлён (данные изменились).
    
    Data: {
        'entity_type': str,
        'entity_id': int,
        'count': int,                      # Новое количество
        'timestamp': float
    }
    """
    
    # === Ответы на запросы ===
    CURRENT_SELECTION = 'sys.current_selection'
    """
    Ответ на запрос текущего выбранного узла.
    
    Data: {
        'node_type': NodeType,
        'node_id': int,
        'data': object                      # Данные узла
    }
    """
    
    EXPANDED_NODES = 'sys.expanded_nodes'
    """
    Ответ на запрос раскрытых узлов.
    
    Data: {
        'nodes': list[tuple(NodeType, int)]  # Список раскрытых узлов
    }
    """


class HotkeyEvents:
    """
    События горячих клавиш.
    Отдельная категория, чтобы можно было легко менять привязки.
    """
    
    REFRESH_CURRENT = 'hotkey.f5'
    """F5 - обновить текущий узел. Data: {}"""
    
    REFRESH_VISIBLE = 'hotkey.ctrl_f5'
    """Ctrl+F5 - обновить все раскрытые узлы. Data: {}"""
    
    FULL_RESET = 'hotkey.ctrl_shift_f5'
    """Ctrl+Shift+F5 - полная перезагрузка. Data: {}"""


class ProjectionEvents:
    """
    События от слоя проекций.
    Оповещают об обновлении структур данных для отображения.
    """
    
    TREE_UPDATED = 'projection.tree_updated'
    """
    Дерево объектов обновлено (перестроено).
    
    Data: {
        'tree': list[TreeNode],          # Корневые узлы дерева
        'timestamp': float,               # Время перестроения
        'reason': str                      # Причина (debounce/forced)
    }
    """
    
    DETAILS_UPDATED = 'projection.details_updated'
    """
    Детальная информация обновлена.
    
    Data: {
        'node_type': NodeType,
        'node_id': int,
        'data': object,
        'context': dict
    }
    """


class CustomEvents:
    """
    Пользовательские события приложения.
    Собирает все строковые события, которые не вошли в другие категории.
    """
    
    # === Владельцы и контрагенты ===
    BUILDING_OWNER_LOADED = 'custom.building_owner_loaded'
    """
    Загружена информация о владельце корпуса.
    
    Data: {
        'building_id': int,
        'owner': Counterparty,
        'responsible_persons': list[ResponsiblePerson],
        'context': dict
    }
    """
    
    NODE_DETAILS_LOADED = 'custom.node_details_loaded'
    """
    Загружены детали узла.
    
    Data: {
        'node_type': NodeType,
        'node_id': int,
        'data': object,
        'context': dict
    }
    """
    
    # === UI уведомления ===
    SHOW_ERROR = 'custom.show_error'
    """
    Показать диалог с ошибкой.
    
    Data: {
        'title': str,
        'message': str,
        'details': str (опционально)
    }
    """
    
    SHOW_CONFIRMATION = 'custom.show_confirmation'
    """
    Показать диалог подтверждения.
    
    Data: {
        'title': str,
        'message': str,
        'callback_event': str,      # Событие при подтверждении
        'callback_data': dict         # Данные для callback
    }
    """
    
    SHOW_MESSAGE = 'custom.show_message'
    """
    Показать временное сообщение в статус-баре.
    
    Data: {
        'message': str,
        'duration_ms': int            # Время показа (опционально)
    }
    """


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

log.success(f"✅ Events module initialized with {len(ALL_EVENTS)} event types")
log.debug(f"📋 Events by category:")
log.debug(f"  • UI Events: {len([e for e in ALL_EVENTS if e.startswith('ui.')])}")
log.debug(f"  • System Events: {len([e for e in ALL_EVENTS if e.startswith('sys.')])}")
log.debug(f"  • Hotkey Events: {len([e for e in ALL_EVENTS if e.startswith('hotkey.')])}")
log.debug(f"  • Projection Events: {len([e for e in ALL_EVENTS if e.startswith('projection.')])}")
log.debug(f"  • Custom Events: {len([e for e in ALL_EVENTS if e.startswith('custom.')])}")