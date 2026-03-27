# client/src/controllers/connection_controller.py
"""
ConnectionController — управление статусом соединения.

Debounce: эмитит события только при реальном изменении статуса.
"""

from typing import Optional
from src.core import EventBus
from src.core.types import Event
from src.core.events import ConnectionChanged
from src.controllers.base import BaseController
from utils.logger import get_logger

log = get_logger(__name__)


class ConnectionController(BaseController):
    """
    Контроллер соединения.
    
    Отслеживает статус соединения с сервером.
    Эмитит события ТОЛЬКО при реальном изменении статуса.
    
    Используемые события:
        - ConnectionChanged (входящее) — от ConnectionService
    """
    
    def __init__(
        self,
        bus: EventBus
    ):
        """
        Инициализирует контроллер соединения.
        
        Args:
            bus: Шина событий
        """
        log.info("Инициализация ConnectionController")
        super().__init__(bus)
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")
        
        self._is_online: Optional[bool] = None  # None = статус еще не известен
        self._initial_status_received = False
        
        # Подписка на изменение статуса соединения
        self._subscribe(ConnectionChanged, self._on_connection_changed)

        log.system("ConnectionController инициализирован")
    
    def _on_connection_changed(self, event: Event[ConnectionChanged]) -> None:
        """
        Обрабатывает изменение статуса соединения.
        
        Сохраняет статус. Статус используется другими компонентами
        через метод is_online().
        
        Args:
            event: Событие изменения соединения
        """
        new_status = event.data.is_online
        error = getattr(event.data, 'error', None)
        
        log.debug(f"Получено ConnectionChanged: online={new_status}, error={error}")
        
        # Первый статус — сохраняем
        if not self._initial_status_received:
            self._initial_status_received = True
            self._is_online = new_status
            log.info(f"Начальный статус соединения: {'ONLINE' if new_status else 'OFFLINE'}")
            return
        
        # Проверяем, изменился ли статус
        if self._is_online == new_status:
            log.debug(f"Статус соединения не изменился: {'ONLINE' if new_status else 'OFFLINE'}")
            return
        
        # Статус изменился
        old_status = self._is_online
        self._is_online = new_status
        
        log.info(f"Соединение изменилось: {'ONLINE' if old_status else 'OFFLINE'} -> "
                 f"{'ONLINE' if new_status else 'OFFLINE'}")
    
    # ===== Публичные методы =====
    
    def is_online(self) -> Optional[bool]:
        """
        Возвращает текущий статус соединения.
        
        Returns:
            Optional[bool]: True если онлайн, False если офлайн, None если неизвестно
        """
        return self._is_online
    
    def is_initialized(self) -> bool:
        """
        Возвращает True, если первый статус уже получен.
        
        Returns:
            bool: True если статус известен
        """
        return self._initial_status_received