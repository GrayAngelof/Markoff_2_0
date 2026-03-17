# client/src/ui/main_window/components/toolbar.py
"""
Модуль панели инструментов главного окна.
Содержит кнопку обновления с меню, индикатор статуса и счётчик объектов.
"""
from PySide6.QtWidgets import QToolBar, QPushButton
from PySide6.QtCore import QSize, Signal, QObject
from PySide6.QtGui import QAction
from typing import Optional

from src.ui.refresh_menu import RefreshMenu
from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ToolbarSignals(QObject):
    """Сигналы для панели инструментов."""
    
    refresh_current = Signal()
    """Сигнал обновления текущего узла"""
    
    refresh_visible = Signal()
    """Сигнал обновления всех раскрытых узлов"""
    
    full_reset = Signal()
    """Сигнал полной перезагрузки"""


class Toolbar:
    """
    Компонент панели инструментов.
    
    Предоставляет:
    - Кнопку с меню для трёх уровней обновления
    - Индикатор статуса подключения
    - Счётчик объектов в кэше
    """
    
    # ===== Константы =====
    _ICON_SIZE = 16
    """Размер иконок в пикселях"""
    
    _TOOLBAR_NAME = "Панель инструментов"
    """Название панели инструментов"""
    
    _REFRESH_BUTTON_TEXT = "🔄 Обновить"
    """Текст кнопки обновления"""
    
    _REFRESH_BUTTON_TOOLTIP = "Выберите тип обновления (F5 - меню)"
    """Подсказка для кнопки обновления"""
    
    _STATUS_CHECKING = "⚪ Проверка..."
    """Текст при проверке статуса"""
    
    _COUNTER_DEFAULT = "📊 Объектов: -"
    """Текст счётчика по умолчанию"""
    
    def __init__(self, parent_window) -> None:
        """
        Инициализирует панель инструментов.
        
        Args:
            parent_window: Родительское окно (MainWindow)
        """
        self._parent = parent_window
        self._toolbar: Optional[QToolBar] = None
        self._refresh_menu: Optional[RefreshMenu] = None
        self._status_action: Optional[QAction] = None
        self._counter_action: Optional[QAction] = None
        
        self.signals = ToolbarSignals()
        
        self._create_toolbar()
        
        log.debug("Toolbar: инициализирован")
    
    # ===== Приватные методы =====
    
    def _create_toolbar(self) -> None:
        """Создаёт и настраивает панель инструментов."""
        self._toolbar = QToolBar(self._TOOLBAR_NAME, self._parent)
        self._toolbar.setMovable(False)
        self._toolbar.setIconSize(QSize(self._ICON_SIZE, self._ICON_SIZE))
        self._parent.addToolBar(self._toolbar)
        
        self._create_refresh_button()
        self._create_status_indicator()
        self._create_counter()
        
        log.debug("Toolbar: панель инструментов создана")
    
    def _create_refresh_button(self) -> None:
        """Создаёт кнопку обновления с выпадающим меню."""
        if self._toolbar is None:
            log.error("Toolbar не инициализирован")
            return
        
        # Создаём меню обновления
        self._refresh_menu = RefreshMenu(self._parent)
        
        # Подключаем сигналы меню
        if self._refresh_menu:
            self._refresh_menu.refresh_current.connect(self.signals.refresh_current)
            self._refresh_menu.refresh_visible.connect(self.signals.refresh_visible)
            self._refresh_menu.full_reset.connect(self.signals.full_reset)
        
        # Создаём кнопку
        refresh_button = QPushButton(self._REFRESH_BUTTON_TEXT)
        if self._refresh_menu:
            refresh_button.setMenu(self._refresh_menu)
        refresh_button.setToolTip(self._REFRESH_BUTTON_TOOLTIP)
        
        self._toolbar.addWidget(refresh_button)
        self._toolbar.addSeparator()
        
        log.debug("Toolbar: кнопка обновления создана")
    
    def _create_status_indicator(self) -> None:
        """Создаёт индикатор статуса подключения."""
        if self._toolbar is None:
            log.error("Toolbar не инициализирован")
            return
        
        self._status_action = QAction(self._STATUS_CHECKING, self._parent)
        self._status_action.setEnabled(False)
        self._toolbar.addAction(self._status_action)
        
        log.debug("Toolbar: индикатор статуса создан")
    
    def _create_counter(self) -> None:
        """Создаёт счётчик объектов."""
        if self._toolbar is None:
            log.error("Toolbar не инициализирован")
            return
        
        self._counter_action = QAction(self._COUNTER_DEFAULT, self._parent)
        self._counter_action.setEnabled(False)
        self._toolbar.addAction(self._counter_action)
        
        log.debug("Toolbar: счётчик объектов создан")
    
    # ===== Геттеры =====
    
    @property
    def toolbar(self) -> QToolBar:
        """
        Возвращает виджет панели инструментов.
        
        Returns:
            QToolBar: Панель инструментов
            
        Raises:
            ValueError: Если панель инструментов не инициализирована
        """
        if self._toolbar is None:
            raise ValueError("Toolbar не инициализирован")
        return self._toolbar
    
    @property
    def refresh_menu(self) -> RefreshMenu:
        """
        Возвращает меню обновления.
        
        Returns:
            RefreshMenu: Меню обновления
            
        Raises:
            ValueError: Если меню обновления не инициализировано
        """
        if self._refresh_menu is None:
            raise ValueError("Refresh menu не инициализирован")
        return self._refresh_menu
    
    @property
    def status_action(self) -> QAction:
        """
        Возвращает действие индикатора статуса.
        
        Returns:
            QAction: Действие индикатора статуса
            
        Raises:
            ValueError: Если действие статуса не инициализировано
        """
        if self._status_action is None:
            raise ValueError("Status action не инициализирован")
        return self._status_action
    
    @property
    def counter_action(self) -> QAction:
        """
        Возвращает действие счётчика объектов.
        
        Returns:
            QAction: Действие счётчика объектов
            
        Raises:
            ValueError: Если действие счётчика не инициализировано
        """
        if self._counter_action is None:
            raise ValueError("Counter action не инициализирован")
        return self._counter_action
    
    # ===== Публичные методы =====
    
    def set_status_online(self) -> None:
        """Устанавливает статус 'Онлайн'."""
        if self._status_action:
            self._status_action.setText("✅ Онлайн")
        log.debug("Toolbar: статус изменён на ONLINE")
    
    def set_status_offline(self) -> None:
        """Устанавливает статус 'Офлайн'."""
        if self._status_action:
            self._status_action.setText("❌ Офлайн")
        log.debug("Toolbar: статус изменён на OFFLINE")
    
    def set_status_checking(self) -> None:
        """Устанавливает статус 'Проверка...'."""
        if self._status_action:
            self._status_action.setText(self._STATUS_CHECKING)
        log.debug("Toolbar: статус изменён на CHECKING")
    
    def update_counter(self, count: int) -> None:
        """
        Обновляет счётчик объектов.
        
        Args:
            count: Количество объектов в кэше
        """
        if self._counter_action:
            self._counter_action.setText(f"📊 В кэше: {count} объектов")
        log.debug(f"Toolbar: счётчик обновлён: {count}")