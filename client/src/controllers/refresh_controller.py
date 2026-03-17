# client/src/controllers/refresh_controller.py
"""
Контроллер обновления данных.
Обрабатывает горячие клавиши и меню обновления.
"""
from typing import Dict, Any, Optional

from src.core.event_bus import EventBus
from src.core.events import HotkeyEvents, UIEvents
from src.controllers.base import BaseController
from src.data.entity_types import NodeType

from utils.logger import get_logger


class RefreshController(BaseController):
    """
    Контроллер обновления.
    
    Логика:
    - F5 → обновить текущий узел
    - Ctrl+F5 → обновить все раскрытые узлы
    - Ctrl+Shift+F5 → полная перезагрузка
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Инициализирует контроллер обновления.
        
        Args:
            event_bus: Шина событий
        """
        super().__init__(event_bus)
        
        # Подписки на горячие клавиши
        self._subscribe(HotkeyEvents.REFRESH_CURRENT, self._on_refresh_current)
        self._subscribe(HotkeyEvents.REFRESH_VISIBLE, self._on_refresh_visible)
        self._subscribe(HotkeyEvents.FULL_RESET, self._on_full_reset)
        
        self._logger.info("RefreshController инициализирован")
    
    def _on_refresh_current(self, event: Dict[str, Any]) -> None:
        """
        F5 - обновить текущий узел.
        Запрашиваем текущий выбранный узел и отправляем запрос на обновление.
        """
        self._logger.info("Горячая клавиша F5: обновление текущего узла")
        
        # Запрашиваем текущий выбранный узел
        # Ответ придёт через sys.current_selection, но мы не подписаны на него
        # Поэтому просто отправляем команду с просьбой определить текущий узел
        self._bus.emit(UIEvents.GET_SELECTED_NODE, {}, source='refresh_controller')
        
        # В реальности, tree_controller должен ответить на этот запрос
        # и инициировать обновление. Но для простоты можно сделать так:
        self._bus.emit(UIEvents.REFRESH_REQUESTED, {
            'mode': 'current'
        }, source='refresh_controller')
    
    def _on_refresh_visible(self, event: Dict[str, Any]) -> None:
        """
        Ctrl+F5 - обновить все раскрытые узлы.
        """
        self._logger.info("Горячая клавиша Ctrl+F5: обновление раскрытых узлов")
        
        # Запрашиваем список раскрытых узлов
        self._bus.emit(UIEvents.GET_EXPANDED_NODES, {}, source='refresh_controller')
        
        # Отправляем команду на обновление
        self._bus.emit(UIEvents.REFRESH_REQUESTED, {
            'mode': 'visible'
        }, source='refresh_controller')
    
    def _on_full_reset(self, event: Dict[str, Any]) -> None:
        """
        Ctrl+Shift+F5 - полная перезагрузка.
        """
        self._logger.info("Горячая клавиша Ctrl+Shift+F5: полная перезагрузка")
        
        # Сначала запрашиваем подтверждение (через UI)
        self._bus.emit('ui.show_confirmation', {
            'title': 'Полная перезагрузка',
            'message': 'Вы уверены, что хотите перезагрузить все данные?',
            'callback_event': UIEvents.REFRESH_REQUESTED,
            'callback_data': {'mode': 'full'}
        }, source='refresh_controller')