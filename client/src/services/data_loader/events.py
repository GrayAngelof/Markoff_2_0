# client/src/services/data_loader/events.py
"""
Обработчик событий для DataLoader.
Подписывается на UI-события и вызывает соответствующие методы NodeLoader.
"""
from typing import Dict, Any, List, Callable

from src.core.event_bus import EventBus
from src.core.events import UIEvents, SystemEvents
from src.services.data_loader.loader import NodeLoader
from src.services.data_loader.utils import LoaderUtils
from src.data.entity_types import NodeType

from utils.logger import get_logger


log = get_logger(__name__)


class EventHandler:
    """
    Обработчик событий для DataLoader.
    
    Отвечает за:
    - Подписку на события
    - Преобразование данных событий
    - Вызов методов NodeLoader
    - Генерацию системных событий
    
    Не содержит бизнес-логики загрузки.
    """
    
    def __init__(self, event_bus: EventBus, loader: NodeLoader, utils: LoaderUtils) -> None:
        """
        Инициализирует обработчик событий.
        
        Args:
            event_bus: Шина событий
            loader: Загрузчик узлов
            utils: Утилиты
        """
        self._bus = event_bus
        self._loader = loader
        self._utils = utils
        
        self._subscriptions: List[Callable] = []
        
        self._setup_subscriptions()
        
        log.debug("EventHandler инициализирован")
    
    def _setup_subscriptions(self) -> None:
        """Настраивает подписки на события."""
        self._subscribe(UIEvents.NODE_EXPANDED, self._on_node_expanded)
        self._subscribe(UIEvents.REFRESH_REQUESTED, self._on_refresh_requested)
        
        # Можно добавить другие подписки
        log.debug(f"EventHandler: настроено {len(self._subscriptions)} подписок")
    
    def _subscribe(self, event_type: str, callback: Callable) -> None:
        """Подписывается на событие с сохранением для отписки."""
        unsubscribe = self._bus.subscribe(event_type, callback)
        self._subscriptions.append(unsubscribe)
    
    def cleanup(self) -> None:
        """Отписывается от всех событий."""
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()
        log.debug("EventHandler: отписался от всех событий")
    
    # ===== Обработчики событий =====
    
    def _on_node_expanded(self, event: Dict[str, Any]) -> None:
        """
        Обрабатывает раскрытие узла.
        
        Event data: {
            'node_type': NodeType,
            'node_id': int
        }
        """
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        
        log.debug(f"Получено событие раскрытия {node_type}#{node_id}")
        
        # Определяем тип детей
        child_type = self._utils.get_child_type(node_type)
        if not child_type:
            log.debug(f"Тип {node_type} не может иметь детей")
            return
        
        # Сигнализируем о начале загрузки
        self._bus.emit(SystemEvents.DATA_LOADING, {
            'node_type': child_type,
            'parent_type': node_type,
            'parent_id': node_id
        }, source='data_loader')
        
        try:
            # Загружаем детей
            children = self._loader.load_children(node_type, node_id, child_type)
            
            # Сигнализируем об успехе
            self._bus.emit(SystemEvents.DATA_LOADED, {
                'node_type': child_type,
                'parent_type': node_type,
                'parent_id': node_id,
                'data': children,
                'count': len(children)
            }, source='data_loader')
            
        except Exception as e:
            log.error(f"Ошибка загрузки детей: {e}")
            self._bus.emit(SystemEvents.DATA_ERROR, {
                'node_type': child_type,
                'parent_type': node_type,
                'parent_id': node_id,
                'error': str(e)
            }, source='data_loader')
    
    def _on_refresh_requested(self, event: Dict[str, Any]) -> None:
        """
        Обрабатывает запрос на обновление.
        
        Event data: {
            'mode': 'current' | 'visible' | 'full',
            'node_type': NodeType (optional for current),
            'node_id': int (optional for current)
        }
        """
        mode = event['data'].get('mode', 'current')
        log.info(f"Получен запрос на обновление (mode={mode})")
        
        if mode == 'full':
            self._handle_full_refresh()
        elif mode == 'current':
            self._handle_current_refresh(event['data'])
        elif mode == 'visible':
            # visible обрабатывается контроллером, так как требует состояния UI
            pass
    
    def _handle_full_refresh(self) -> None:
        """Обрабатывает полную перезагрузку."""
        log.info("Начало полной перезагрузки")
        
        self._bus.emit(SystemEvents.DATA_LOADING, {
            'node_type': 'system',
            'node_id': None
        }, source='data_loader')
        
        try:
            # Загружаем комплексы
            complexes = self._loader.load_complexes()
            
            self._bus.emit(SystemEvents.DATA_LOADED, {
                'node_type': NodeType.COMPLEX,
                'parent_type': None,
                'parent_id': None,
                'data': complexes,
                'count': len(complexes)
            }, source='data_loader')
            
            log.success("Полная перезагрузка завершена")
            
        except Exception as e:
            log.error(f"Ошибка полной перезагрузки: {e}")
            self._bus.emit(SystemEvents.DATA_ERROR, {
                'node_type': 'system',
                'node_id': None,
                'error': str(e)
            }, source='data_loader')
    
    def _handle_current_refresh(self, data: Dict[str, Any]) -> None:
        """
        Обрабатывает обновление текущего узла.
        
        Args:
            data: Данные события с node_type и node_id
        """
        node_type = data.get('node_type')
        node_id = data.get('node_id')
        
        if not node_type or not node_id:
            log.warning("Недостаточно данных для обновления текущего узла")
            return
        
        log.info(f"Обновление текущего узла {node_type}#{node_id}")
        
        try:
            self._loader.reload_node(node_type, node_id)
        except Exception as e:
            log.error(f"Ошибка обновления узла: {e}")