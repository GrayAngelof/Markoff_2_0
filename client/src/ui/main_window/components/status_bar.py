# client/src/ui/main_window/components/status_bar.py
"""
Модуль строки статуса главного окна.
Отображает текущее состояние приложения и соединения с сервером.
"""
from PySide6.QtWidgets import QStatusBar, QLabel
from PySide6.QtCore import QTimer
from typing import Optional

from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class StatusBar:
    """
    Компонент строки статуса.
    
    Предоставляет:
    - Отображение сообщений о процессе
    - Постоянный индикатор соединения
    - Таймер для автоматического скрытия сообщений
    """
    
    # ===== Константы =====
    _DEFAULT_MESSAGE = "Готов к работе"
    """Сообщение по умолчанию"""
    
    _CONNECTION_CHECKING = "⚪ Соединение..."
    """Текст индикатора соединения при проверке"""
    
    _CONNECTION_ONLINE = "✅ Сервер доступен"
    """Текст индикатора при успешном соединении"""
    
    _CONNECTION_OFFLINE = "❌ Сервер недоступен"
    """Текст индикатора при отсутствии соединения"""
    
    _ONLINE_STYLE = "color: green;"
    """Стиль для статуса онлайн"""
    
    _OFFLINE_STYLE = "color: red;"
    """Стиль для статуса офлайн"""
    
    _MESSAGE_TIMEOUT_MS = 3000
    """Время отображения временных сообщений в миллисекундах"""
    
    def __init__(self, parent_window) -> None:
        """
        Инициализирует строку статуса.
        
        Args:
            parent_window: Родительское окно (MainWindow)
        """
        self._parent = parent_window
        self._status_bar: Optional[QStatusBar] = None
        self._connection_label: Optional[QLabel] = None
        self._message_timer: Optional[QTimer] = None
        
        self._create_status_bar()
        self._setup_message_timer()
        
        log.debug("StatusBar: инициализирована")
    
    # ===== Приватные методы =====
    
    def _create_status_bar(self) -> None:
        """Создаёт и настраивает строку статуса."""
        self._status_bar = QStatusBar()
        self._parent.setStatusBar(self._status_bar)
        self._status_bar.showMessage(self._DEFAULT_MESSAGE)
        
        self._create_connection_indicator()
        
        log.debug("StatusBar: строка статуса создана")
    
    def _create_connection_indicator(self) -> None:
        """Создаёт постоянный индикатор соединения."""
        self._connection_label = QLabel(self._CONNECTION_CHECKING)
        if self._status_bar:
            self._status_bar.addPermanentWidget(self._connection_label)
        
        log.debug("StatusBar: индикатор соединения создан")
    
    def _setup_message_timer(self) -> None:
        """Настраивает таймер для автоматического скрытия сообщений."""
        self._message_timer = QTimer()
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._clear_temporary_message)
        
        log.debug("StatusBar: таймер сообщений настроен")
    
    def _clear_temporary_message(self) -> None:
        """Очищает временное сообщение и возвращает стандартное."""
        if self._status_bar:
            self._status_bar.showMessage(self._DEFAULT_MESSAGE)
        log.debug("StatusBar: временное сообщение очищено")
    
    # ===== Геттеры =====
    
    @property
    def status_bar(self) -> QStatusBar:
        """Возвращает виджет строки статуса."""
        if self._status_bar is None:
            raise ValueError("Status bar не инициализирован")
        return self._status_bar
    
    @property
    def connection_label(self) -> QLabel:
        """Возвращает метку индикатора соединения."""
        if self._connection_label is None:
            raise ValueError("Connection label не инициализирован")
        return self._connection_label
    
    # ===== Публичные методы =====
    
    def show_message(self, message: str, timeout: int = 0) -> None:
        """
        Показывает сообщение в строке статуса.
        
        Args:
            message: Текст сообщения
            timeout: Время отображения в мс (0 - постоянно)
        """
        if self._status_bar:
            self._status_bar.showMessage(message, timeout)
        log.debug(f"StatusBar: показано сообщение '{message}'")
    
    def show_temporary_message(self, message: str) -> None:
        """
        Показывает временное сообщение (на 3 секунды).
        
        Args:
            message: Текст сообщения
        """
        if self._status_bar:
            self._status_bar.showMessage(message, self._MESSAGE_TIMEOUT_MS)
        log.debug(f"StatusBar: показано временное сообщение '{message}'")
    
    def set_connection_online(self) -> None:
        """Устанавливает индикатор соединения в состояние 'онлайн'."""
        if self._connection_label:
            self._connection_label.setText(self._CONNECTION_ONLINE)
            self._connection_label.setStyleSheet(self._ONLINE_STYLE)
        log.debug("StatusBar: соединение ONLINE")
    
    def set_connection_offline(self) -> None:
        """Устанавливает индикатор соединения в состояние 'офлайн'."""
        if self._connection_label:
            self._connection_label.setText(self._CONNECTION_OFFLINE)
            self._connection_label.setStyleSheet(self._OFFLINE_STYLE)
        log.debug("StatusBar: соединение OFFLINE")
    
    def set_connection_checking(self) -> None:
        """Устанавливает индикатор соединения в состояние 'проверка'."""
        if self._connection_label:
            self._connection_label.setText(self._CONNECTION_CHECKING)
            self._connection_label.setStyleSheet("")
        log.debug("StatusBar: проверка соединения")
    
    def clear(self) -> None:
        """Очищает строку статуса до состояния по умолчанию."""
        if self._status_bar:
            self._status_bar.showMessage(self._DEFAULT_MESSAGE)
        self.set_connection_checking()
        log.debug("StatusBar: очищена")