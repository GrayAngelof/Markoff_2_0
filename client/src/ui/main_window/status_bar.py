# client/src/ui/main_window/status_bar.py
"""
Строка состояния приложения Markoff 2.0.

Отображает статус соединения с потокобезопасностью через сигналы Qt.
"""

# ===== ИМПОРТЫ =====
from typing import Final

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtWidgets import QLabel, QStatusBar

from src.core import EventBus
from src.core.events import ConnectionChanged
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАССЫ =====
class StatusBarSignals(QObject):
    """Сигналы для StatusBar (для межпотокового взаимодействия)."""

    connection_status_changed = Signal(bool, str)  # is_online, error_message


class StatusBar(QStatusBar):
    """
    Строка состояния приложения.

    Содержит:
    - Левая часть: временные сообщения
    - Правая часть: индикатор соединения

    Подписывается на события ConnectionChanged (потокобезопасно через сигналы).
    """

    # Локальные константы — тексты сообщений
    _STATUS_CHECKING: Final[str] = "Проверка..."
    _STATUS_ONLINE: Final[str] = "Онлайн"
    _STATUS_OFFLINE: Final[str] = "Офлайн"
    _MESSAGE_READY: Final[str] = "Готов к работе"
    _MESSAGE_ONLINE: Final[str] = "Соединение с сервером установлено"
    _MESSAGE_OFFLINE: Final[str] = "Сервер недоступен"

    # Локальные константы — цвета для индикатора
    _COLOR_ONLINE: Final[str] = "green"
    _COLOR_OFFLINE: Final[str] = "red"

    # Локальные константы — символы для индикатора
    _SYMBOL_CHECKING: Final[str] = "⚪"
    _SYMBOL_ONLINE: Final[str] = "✅"
    _SYMBOL_OFFLINE: Final[str] = "❌"

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus) -> None:
        """Инициализирует строку состояния."""
        log.info("Инициализация StatusBar")
        super().__init__()

        self._bus = bus
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

        self._signals = StatusBarSignals()
        self._message_timer = QTimer()
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._clear_message)

        self._create_connection_indicator()

        self.showMessage(self._MESSAGE_READY)

        self._signals.connection_status_changed.connect(self._update_connection_status)
        self._subscribe_to_events()

        log.system("StatusBar инициализирован")

    def cleanup(self) -> None:
        """Очищает ресурсы перед закрытием."""
        self._message_timer.stop()
        log.data("StatusBar очищен")

    # ---- ПУБЛИЧНОЕ API ----
    def showTemporaryMessage(self, message: str, timeout_ms: int = 3000) -> None:
        """Показывает временное сообщение."""
        self.showMessage(message, timeout_ms)
        self._message_timer.start(timeout_ms)
        log.debug(f"Временное сообщение: {message}")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _create_connection_indicator(self) -> None:
        """Создаёт индикатор соединения."""
        self._connection_label = QLabel(f"{self._SYMBOL_CHECKING} {self._STATUS_CHECKING}")
        self.addPermanentWidget(self._connection_label)

    def _subscribe_to_events(self) -> None:
        """Подписывается на события."""
        self._bus.subscribe(ConnectionChanged, self._on_connection_changed)
        log.link("Подписка на ConnectionChanged")

    def _on_connection_changed(self, event) -> None:
        """
        Обработчик события (может вызываться из любого потока).
        Эмитит сигнал для безопасного обновления UI.
        """
        is_online = event.data.is_online
        error = event.data.error if hasattr(event.data, 'error') else None
        error_msg = error if error else (self._MESSAGE_OFFLINE if not is_online else "")

        log.info(f"Получено ConnectionChanged: online={is_online}")

        self._signals.connection_status_changed.emit(is_online, error_msg)

    @Slot(bool, str)
    def _update_connection_status(self, is_online: bool, error_msg: str) -> None:
        """Обновляет UI (вызывается в главном потоке)."""
        if is_online:
            self._connection_label.setText(f"{self._SYMBOL_ONLINE} {self._STATUS_ONLINE}")
            self._connection_label.setStyleSheet(f"color: {self._COLOR_ONLINE};")
            self.showTemporaryMessage(self._MESSAGE_ONLINE)
            log.api("Статус изменён: Онлайн")
        else:
            self._connection_label.setText(f"{self._SYMBOL_OFFLINE} {self._STATUS_OFFLINE}")
            self._connection_label.setStyleSheet(f"color: {self._COLOR_OFFLINE};")
            msg = error_msg if error_msg else self._MESSAGE_OFFLINE
            self.showTemporaryMessage(msg)
            log.api(f"Статус изменён: Офлайн ({msg})")

    @Slot()
    def _clear_message(self) -> None:
        """Очищает временное сообщение."""
        self.showMessage(self._MESSAGE_READY)
        log.debug("Временное сообщение очищено")