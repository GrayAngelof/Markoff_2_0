# client/src/services/connection.py
"""
ConnectionService — мониторинг соединения.
ОДИН ПОТОК с циклом, без утечек.
"""

import threading
import time
from typing import Optional

from src.core import EventBus
from src.core.events import ConnectionChanged
from src.services.api_client import ApiClient
from utils.logger import get_logger

log = get_logger(__name__)


class ConnectionService:
    """Сервис периодической проверки доступности сервера."""
    
    def __init__(self, bus: EventBus, api: ApiClient, interval_ms: int = 600000):
        self._bus = bus
        self._api = api
        self._interval = interval_ms / 1000
        self._is_online: Optional[bool] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_event = threading.Event()
    
    def start(self) -> None:
        """Запускает периодическую проверку (один поток)."""
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        log.info(f"ConnectionService started (interval={self._interval}s)")
    
    def stop(self) -> None:
        """Останавливает периодическую проверку."""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        log.info("ConnectionService stopped")
    
    def force_check(self) -> None:
        """Принудительная проверка."""
        self._check()
    
    def _run(self) -> None:
        """Основной цикл — один поток на весь сервис."""
        while self._running:
            self._check()
            self._stop_event.wait(self._interval)
    
    def _check(self) -> None:
        """Внутренняя проверка. Генерирует событие при изменении статуса."""
        try:
            online = self._api.check_connection()
        except Exception:
            online = False
        
        if online != self._is_online:
            self._is_online = online
            status = "ONLINE" if online else "OFFLINE"
            log.info(f"Connection status changed: {status}")
            self._bus.emit(ConnectionChanged(is_online=online))