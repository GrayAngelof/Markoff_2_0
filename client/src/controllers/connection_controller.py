# client/src/controllers/connection_controller.py
"""
ConnectionController — управление статусом соединения.

Отслеживает статус соединения с сервером.
Эмитит события только при реальном изменении статуса (debounce).
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from src.core.event_bus import EventBus
from src.core.events.definitions import ConnectionChanged
from .base import BaseController
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class ConnectionController(BaseController):
    """
    Контроллер соединения.

    Отслеживает статус соединения с сервером.
    Эмитит события только при реальном изменении статуса.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus) -> None:
        """Инициализирует контроллер соединения."""
        log.info("Инициализация ConnectionController")
        super().__init__(bus)
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

        self._is_online: Optional[bool] = None  # None = статус ещё не известен
        self._initial_status_received = False

        self._subscribe(ConnectionChanged, self._on_connection_changed)

        log.system("ConnectionController инициализирован")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_connection_changed(self, data: ConnectionChanged) -> None:  # Изменено: data вместо event
        """
        Обрабатывает изменение статуса соединения.

        Сохраняет статус и логирует только при реальном изменении.
        """
        new_status = data.is_online  # Изменено: data.is_online вместо event.data.is_online
        error = getattr(data, 'error', None)

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

        log.info(
            f"Соединение изменилось: {'ONLINE' if old_status else 'OFFLINE'} -> "
            f"{'ONLINE' if new_status else 'OFFLINE'}"
        )

    # ---- ПУБЛИЧНОЕ API ----
    def is_online(self) -> Optional[bool]:
        """Возвращает текущий статус соединения."""
        return self._is_online

    def is_initialized(self) -> bool:
        """Возвращает True, если первый статус уже получен."""
        return self._initial_status_received