# client/src/controllers/connection_controller.py
"""
ConnectionController — управление статусом соединения.

Debounce: эмитит события только при реальном изменении статуса.
"""

from typing import Optional
from src.core import EventBus
from src.core.types import Event
from src.core.events import ConnectionChanged, NetworkActionsEnabled, NetworkActionsDisabled
from src.controllers.base import BaseController
from utils.logger import get_logger

log = get_logger(__name__)


class ConnectionController(BaseController):
    """
    Контроллер соединения.
    
    Отслеживает статус соединения с сервером.
    Эмитит события ТОЛЬКО при реальном изменении статуса.
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
        super().__init__(bus)
        
        # SYSTEM - конкретный компонент приложения
        self._is_online: Optional[bool] = None  # None = статус еще не известен
        self._initial_status_received = False
        
        # Сохраняем bound method как атрибут (сильная ссылка)
        self._bound_on_connection_changed = self._on_connection_changed
        
        # Подписки - LINK категория
        log.link("Подписка на ConnectionChanged")
        self._subscribe(ConnectionChanged, self._bound_on_connection_changed)

        log.system("ConnectionController инициализирован")
    
    def _on_connection_changed(self, event: Event[ConnectionChanged]) -> None:
        """
        Обрабатывает изменение статуса соединения.
        
        Эмитит события только при реальном изменении.
        
        Args:
            event: Событие изменения соединения
        """
        new_status = event.data.is_online
        error = getattr(event.data, 'error', None)
        
        # DEBUG - детальная информация о полученном событии
        log.debug(f"Получено ConnectionChanged: online={new_status}, error={error}")
        
        # Первый статус — сохраняем без эмиссии дополнительных событий
        if not self._initial_status_received:
            self._initial_status_received = True
            self._is_online = new_status
            
            # INFO - важное событие инициализации
            log.info(f"Начальный статус соединения: {'ONLINE' if new_status else 'OFFLINE'}")
            return
        
        # Проверяем, изменился ли статус
        if self._is_online == new_status:
            log.debug(f"Статус соединения не изменился: {'ONLINE' if new_status else 'OFFLINE'}")
            return
        
        # Статус изменился
        old_status = self._is_online
        self._is_online = new_status
        
        # INFO - важное изменение состояния
        log.info(f"Соединение изменилось: {'ONLINE' if old_status else 'OFFLINE'} -> "
                 f"{'ONLINE' if new_status else 'OFFLINE'}")
        
        if new_status:
            # API - действия, связанные с сетью
            log.api("Эмит: NetworkActionsEnabled")
            self._bus.emit(NetworkActionsEnabled())
        else:
            log.api("Эмит: NetworkActionsDisabled")
            self._bus.emit(NetworkActionsDisabled())
    
    # ===== Публичные методы =====
    
    def is_online(self) -> Optional[bool]:
        """
        Возвращает текущий статус соединения.
        
        Returns:
            Optional[bool]: True если онлайн, False если офлайн, None если неизвестно
        """
        # DEBUG - запрос статуса (отладочная информация)
        log.debug(f"Запрос статуса соединения: {self._is_online}")
        return self._is_online
    
    def is_initialized(self) -> bool:
        """
        Возвращает True, если первый статус уже получен.
        
        Returns:
            bool: True если статус известен
        """
        return self._initial_status_received