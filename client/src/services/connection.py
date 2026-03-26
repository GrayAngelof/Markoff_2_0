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
        log.system("EventBus инициализирован")
        self._api = api
        self._interval = interval_ms / 1000
        self._is_online: Optional[bool] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._stop_event = threading.Event()
    
        log.system(f"ConnectionService инициализирован")  
        
    def start(self) -> None:
        """Запускает периодическую проверку (один поток)."""
        if self._running:
            log.debug("ConnectionService уже запущен")
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        log.api(f"ConnectionService запущен (интервал={self._interval:.1f}с)")
    
    def stop(self) -> None:
        """Останавливает периодическую проверку."""
        if not self._running:
            log.debug("ConnectionService уже остановлен")
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._thread:
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                log.warning("Таймаут остановки потока ConnectionService")
        
        log.api("ConnectionService остановлен")
    
    def force_check(self) -> None:
        """Принудительная проверка."""
        log.debug("Принудительная проверка соединения")
        self._check()
    
    def _run(self) -> None:
        """Основной цикл — один поток на весь сервис."""
        log.debug(f"Поток ConnectionService запущен, интервал={self._interval:.1f}с")
        
        while self._running:
            self._check()
            self._stop_event.wait(self._interval)
        
        log.success("Поток ConnectionService завершён")
    
    def _check(self) -> None:
        """Внутренняя проверка. Генерирует событие при изменении статуса."""
        try:
            online = self._api.check_connection()
        except Exception as e:
            online = False
            log.debug(f"Ошибка проверки соединения: {e}")
        
        if online != self._is_online:
            self._is_online = online
            status = "ONLINE" if online else "OFFLINE"
            
            # Важное событие изменения статуса - используем API категорию с INFO
            log.api(f"Статус соединения изменён: {status}")
            
            self._bus.emit(ConnectionChanged(is_online=online))
        else:
            # Периодические проверки без изменений - только DEBUG
            if self._is_online is not None:
                log.debug(f"Проверка соединения: {self._is_online}")