# client/src/ui/main_window/status_bar.py
"""
Строка состояния приложения Markoff 2.0.
Отображает статус соединения с потокобезопасностью через сигналы Qt.
"""

from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtCore import Signal, QObject, QTimer

from src.core import EventBus
from src.core.events import ConnectionChanged

from utils.logger import get_logger

log = get_logger(__name__)


class StatusBarSignals(QObject):
    """Сигналы для StatusBar (для межпотокового взаимодействия)."""
    connection_status_changed = Signal(bool, str)  # is_online, error_message


class StatusBar(QStatusBar):
    """
    Строка состояния приложения.
    
    Содержит:
    - Левая часть: временные сообщения
    - Правая часть: индикатор соединения
    
    Подписывается на события:
    - ConnectionChanged — обновляет индикатор (потокобезопасно через сигналы)
    """
    
    def __init__(self, bus: EventBus):
        super().__init__()
        
        self._bus = bus
        self._signals = StatusBarSignals()
        self._message_timer = QTimer()
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._clear_message)
        
        self._create_connection_indicator()
        
        # Стартовое сообщение
        self.showMessage("Готов к работе")
        
        # Подключаем сигнал к слоту (в главном потоке)
        self._signals.connection_status_changed.connect(self._update_connection_status)
        
        # Подписываемся на события
        self._subscribe_to_events()
        
        log.debug("StatusBar создан")
    
    def _create_connection_indicator(self) -> None:
        """Создает индикатор соединения."""
        self._connection_label = QLabel("⚪ Проверка...")
        self.addPermanentWidget(self._connection_label)
    
    def _subscribe_to_events(self) -> None:
        """Подписывается на события."""
        self._bus.subscribe(ConnectionChanged, self._on_connection_changed)
        log.debug("StatusBar подписан на ConnectionChanged")
    
    def _on_connection_changed(self, event) -> None:
        """
        Обработчик события (может вызываться из любого потока).
        Эмитит сигнал для безопасного обновления UI.
        """
        is_online = event.data.is_online
        error = event.data.error if hasattr(event.data, 'error') else None
        error_msg = error if error else ("Сервер недоступен" if not is_online else "")
        
        # Эмитим сигнал (потокобезопасно)
        self._signals.connection_status_changed.emit(is_online, error_msg)
    
    def _update_connection_status(self, is_online: bool, error_msg: str) -> None:
        """
        Обновляет UI (вызывается в главном потоке).
        
        Args:
            is_online: True если соединение установлено
            error_msg: Сообщение об ошибке (если есть)
        """
        if is_online:
            self._connection_label.setText("✅ Онлайн")
            self._connection_label.setStyleSheet("color: green;")
            self.showTemporaryMessage("✅ Соединение с сервером установлено")
            log.debug("Статус: Онлайн")
        else:
            self._connection_label.setText("❌ Офлайн")
            self._connection_label.setStyleSheet("color: red;")
            msg = f"❌ {error_msg}" if error_msg else "❌ Сервер недоступен"
            self.showTemporaryMessage(msg)
            log.debug("Статус: Офлайн")
    
    def showTemporaryMessage(self, message: str, timeout_ms: int = 3000) -> None:
        """Показывает временное сообщение."""
        self.showMessage(message, timeout_ms)
        self._message_timer.start(timeout_ms)
    
    def _clear_message(self) -> None:
        """Очищает временное сообщение."""
        self.showMessage("Готов к работе")
    
    def cleanup(self) -> None:
        """Очищает ресурсы перед закрытием."""
        self._message_timer.stop()
        log.debug("StatusBar очищен")