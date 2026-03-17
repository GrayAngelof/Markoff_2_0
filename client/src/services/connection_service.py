# client/src/services/connection_service.py
"""
Сервис мониторинга соединения с бэкендом.
Периодически проверяет доступность сервера и генерирует события.
"""
from PySide6.QtCore import QTimer, QObject
from typing import Optional

from src.core.event_bus import EventBus
from src.core.events import SystemEvents
from src.services.api_client import ApiClient

from utils.logger import get_logger


log = get_logger(__name__)


class ConnectionService(QObject):
    """
    Сервис мониторинга соединения.
    
    Периодически проверяет доступность бэкенда и генерирует
    событие sys.connection_changed при изменении статуса.
    """
    
    def __init__(self, event_bus: EventBus, api_client: ApiClient, 
                 check_interval_ms: int = 30000) -> None:
        """
        Инициализирует сервис соединения.
        
        Args:
            event_bus: Шина событий
            api_client: HTTP-клиент
            check_interval_ms: Интервал проверки в миллисекундах
        """
        super().__init__()
        
        self._bus = event_bus
        self._api = api_client
        self._is_online: Optional[bool] = None
        self._check_interval = check_interval_ms
        
        # Таймер для периодической проверки
        self._timer = QTimer()
        self._timer.timeout.connect(self._check_connection)
        self._timer.start(check_interval_ms)
        
        # Первая проверка через секунду
        QTimer.singleShot(1000, self._check_connection)
        
        log.info(f"ConnectionService инициализирован (интервал={check_interval_ms}мс)")
    
    def _check_connection(self) -> None:
        """Проверяет соединение и генерирует событие при изменении."""
        try:
            online = self._api.check_connection()
            
            if online != self._is_online:
                self._is_online = online
                status = "ONLINE" if online else "OFFLINE"
                log.info(f"Статус соединения изменился: {status}")
                
                self._bus.emit(SystemEvents.CONNECTION_CHANGED, {
                    'is_online': online,
                    'timestamp': self._get_timestamp()
                }, source='connection_service')
                
        except Exception as e:
            log.error(f"Ошибка при проверке соединения: {e}")
            
            if self._is_online != False:
                self._is_online = False
                self._bus.emit(SystemEvents.CONNECTION_CHANGED, {
                    'is_online': False,
                    'error': str(e),
                    'timestamp': self._get_timestamp()
                }, source='connection_service')
    
    def _get_timestamp(self) -> str:
        """Возвращает временную метку для события."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def force_check(self) -> None:
        """Принудительно запускает проверку соединения."""
        log.debug("Принудительная проверка соединения")
        self._check_connection()
    
    def get_status(self) -> Optional[bool]:
        """
        Возвращает текущий статус соединения.
        
        Returns:
            True если онлайн, False если офлайн, None если ещё не проверяли
        """
        return self._is_online
    
    def stop(self) -> None:
        """Останавливает периодическую проверку."""
        self._timer.stop()
        log.info("ConnectionService остановлен")
    
    def start(self) -> None:
        """Запускает периодическую проверку."""
        self._timer.start(self._check_interval)
        log.info("ConnectionService запущен")