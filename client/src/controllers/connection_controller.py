# client/src/controllers/connection_controller.py
"""
ConnectionController — управление статусом соединения.

Debounce: эмитит события только при реальном изменении статуса.
"""

from typing import Optional
from core import EventBus
from core.types import Event
from core.events import ConnectionChanged, NetworkActionsEnabled, NetworkActionsDisabled
from controllers.base import BaseController
from utils.logger import get_logger

log = get_logger(__name__)


class ConnectionController(BaseController):
    """
    Контроллер соединения.
    
    Отслеживает статус соединения с сервером.
    Эмитит события ТОЛЬКО при реальном изменении статуса.
    """
    
    def __init__(self, bus: EventBus):
        """
        Инициализирует контроллер соединения.
        
        Args:
            bus: Шина событий
        """
        super().__init__(bus)
        
        # None = ещё не проверяли
        self._is_online: Optional[bool] = None
        
        # Подписки
        self._subscribe(ConnectionChanged, self._on_connection_changed)
        
        log.info("ConnectionController initialized")
    
    def _on_connection_changed(self, event: Event[ConnectionChanged]) -> None:
        """
        Обрабатывает изменение статуса соединения.
        
        Эмитит события только при реальном изменении.
        
        Args:
            event: Событие изменения соединения
        """
        new_status = event.data.is_online
        
        # Проверяем, изменился ли статус
        if self._is_online == new_status:
            log.debug(f"Connection status unchanged: {'online' if new_status else 'offline'}")
            return
        
        # Статус изменился
        old_status = self._is_online
        self._is_online = new_status
        
        log.info(f"Connection changed: {'online' if old_status else 'offline'} -> "
                 f"{'online' if new_status else 'offline'}")
        
        if new_status:
            self._bus.emit(NetworkActionsEnabled())
        else:
            self._bus.emit(NetworkActionsDisabled())
    
    # ===== Публичные методы =====
    
    def is_online(self) -> Optional[bool]:
        """
        Возвращает текущий статус соединения.
        
        Returns:
            Optional[bool]: True если онлайн, False если офлайн, None если неизвестно
        """
        return self._is_online