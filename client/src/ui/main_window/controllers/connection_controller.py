# client/src/ui/main_window/controllers/connection_controller.py
"""
Контроллер проверки соединения с сервером.
Периодически проверяет доступность бекенда и обновляет статус.
"""
from PySide6.QtCore import QObject, QTimer, Slot

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ConnectionController(QObject):
    """
    Контроллер проверки соединения.
    
    Периодически проверяет доступность сервера и обновляет
    индикаторы статуса в панели инструментов и строке статуса.
    """
    
    # ===== Константы =====
    _CHECK_INTERVAL_MS = 30000
    """Интервал проверки соединения в миллисекундах (30 секунд)"""
    
    _INITIAL_CHECK_DELAY_MS = 1000
    """Задержка перед первой проверкой в миллисекундах"""
    
    def __init__(self, tree_view, toolbar, status_bar) -> None:
        """
        Инициализирует контроллер соединения.
        
        Args:
            tree_view: Виджет дерева (TreeView) для доступа к API
            toolbar: Панель инструментов (Toolbar)
            status_bar: Строка статуса (StatusBar)
        """
        super().__init__()
        
        self._tree_view = tree_view
        self._toolbar = toolbar
        self._status_bar = status_bar
        self._timer: QTimer = QTimer()
        
        self._setup_timer()
        
        log.debug("ConnectionController: инициализирован")
    
    # ===== Приватные методы =====
    
    def _setup_timer(self) -> None:
        """Настраивает таймер для периодической проверки."""
        self._timer.timeout.connect(self.check_connection)
        self._timer.start(self._CHECK_INTERVAL_MS)
        
        # Первая проверка с задержкой
        QTimer.singleShot(self._INITIAL_CHECK_DELAY_MS, self.check_connection)
        
        log.debug("ConnectionController: таймер настроен")
    
    def _is_connected(self) -> bool:
        """
        Проверяет доступность сервера.
        
        Returns:
            bool: True если сервер доступен
        """
        try:
            if hasattr(self._tree_view.api_client, 'check_connection'):
                return self._tree_view.api_client.check_connection()
            else:
                info = self._tree_view.api_client.get_server_info()
                return bool(info and 'message' in info)
        except Exception as error:
            log.debug(f"ConnectionController: ошибка при проверке: {error}")
            return False
    
    # ===== Публичные слоты =====
    
    @Slot()
    def check_connection(self) -> None:
        """Проверяет соединение и обновляет индикаторы."""
        if self._is_connected():
            self._toolbar.set_status_online()
            self._status_bar.set_connection_online()
            log.debug("ConnectionController: сервер доступен")
        else:
            self._toolbar.set_status_offline()
            self._status_bar.set_connection_offline()
            log.debug("ConnectionController: сервер недоступен")
    
    @Slot()
    def stop_checking(self) -> None:
        """Останавливает периодическую проверку."""
        self._timer.stop()
        log.debug("ConnectionController: проверка остановлена")