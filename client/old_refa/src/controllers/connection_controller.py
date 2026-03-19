# client/src/controllers/connection_controller.py
"""
Контроллер статуса соединения.
Обновляет UI при изменении статуса соединения с сервером.
"""
from typing import Dict, Any

from src.core.event_bus import EventBus
from src.core.events import SystemEvents
from src.controllers.base import BaseController

from utils.logger import get_logger


class ConnectionController(BaseController):
    """
    Контроллер статуса соединения.
    
    Логика:
    - При изменении статуса соединения → обновить индикаторы в UI
    - При потере соединения → заблокировать действия, требующие сети
    - При восстановлении → разблокировать
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Инициализирует контроллер соединения.
        
        Args:
            event_bus: Шина событий
        """
        super().__init__(event_bus)
        
        self._is_online = True  # по умолчанию считаем, что онлайн
        
        # Подписка на события соединения
        self._subscribe(SystemEvents.CONNECTION_CHANGED, self._on_connection_changed)
        
        self._logger.info("ConnectionController инициализирован")
    
    def _on_connection_changed(self, event: Dict[str, Any]) -> None:
        """
        Изменился статус соединения.
        
        Event data: {
            'is_online': bool,
            'timestamp': str (optional)
        }
        """
        is_online = event['data']['is_online']
        
        if is_online == self._is_online:
            return  # статус не изменился
        
        self._is_online = is_online
        status = "ONLINE" if is_online else "OFFLINE"
        self._logger.info(f"Статус соединения: {status}")
        
        # Генерируем события для UI
        if is_online:
            self._on_online()
        else:
            self._on_offline()
    
    def _on_online(self) -> None:
        """Соединение восстановлено."""
        self._bus.emit('ui.connection_online', {}, source='connection_controller')
        
        # Можно также разблокировать элементы UI через события
        self._bus.emit('ui.enable_network_actions', {}, source='connection_controller')
    
    def _on_offline(self) -> None:
        """Соединение потеряно."""
        self._bus.emit('ui.connection_offline', {}, source='connection_controller')
        
        # Блокируем действия, требующие сети
        self._bus.emit('ui.disable_network_actions', {}, source='connection_controller')
    
    def is_online(self) -> bool:
        """Возвращает текущий статус соединения."""
        return self._is_online