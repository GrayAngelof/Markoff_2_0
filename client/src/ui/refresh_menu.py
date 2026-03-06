# client/src/ui/refresh_menu.py
"""
Меню выбора типа обновления для дерева объектов.
Содержит три пункта с соответствующими горячими клавишами:
- Обновить текущий узел (F5)
- Обновить все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction
from typing import Optional

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class RefreshMenu(QMenu):
    """
    Выпадающее меню для выбора типа обновления данных.
    
    Предоставляет три действия:
    - refresh_current: обновление текущего выбранного узла
    - refresh_visible: обновление всех раскрытых узлов
    - full_reset: полная перезагрузка всех данных
    
    Каждое действие имеет свою горячую клавишу и всплывающую подсказку.
    """
    
    # ===== Сигналы =====
    refresh_current = Signal()
    """Сигнал обновления текущего узла"""
    
    refresh_visible = Signal()
    """Сигнал обновления всех раскрытых узлов"""
    
    full_reset = Signal()
    """Сигнал полной перезагрузки"""
    
    # ===== Константы =====
    _MENU_TITLE = "Обновить"
    """Заголовок меню"""
    
    # Тексты действий
    _ACTION_CURRENT_TEXT = "🔄 Обновить текущий узел"
    """Текст действия обновления текущего узла"""
    
    _ACTION_VISIBLE_TEXT = "🔄 Обновить все раскрытые"
    """Текст действия обновления всех раскрытых узлов"""
    
    _ACTION_RESET_TEXT = "🔄 Полная перезагрузка"
    """Текст действия полной перезагрузки"""
    
    # Подсказки
    _ACTION_CURRENT_TOOLTIP = "Обновить только выбранный узел (F5)"
    """Подсказка для обновления текущего узла"""
    
    _ACTION_VISIBLE_TOOLTIP = "Обновить все раскрытые узлы (Ctrl+F5)"
    """Подсказка для обновления всех раскрытых узлов"""
    
    _ACTION_RESET_TOOLTIP = "Полная перезагрузка всех данных (Ctrl+Shift+F5)"
    """Подсказка для полной перезагрузки"""
    
    # Горячие клавиши
    _SHORTCUT_CURRENT = "F5"
    """Горячая клавиша для обновления текущего узла"""
    
    _SHORTCUT_VISIBLE = "Ctrl+F5"
    """Горячая клавиша для обновления всех раскрытых узлов"""
    
    _SHORTCUT_RESET = "Ctrl+Shift+F5"
    """Горячая клавиша для полной перезагрузки"""
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует меню обновления.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(self._MENU_TITLE, parent)
        
        # Создание действий
        self._create_actions()
        
        # Добавление действий в меню
        self._populate_menu()
        
        log.success("RefreshMenu: создано")
    
    # ===== Приватные методы =====
    
    def _create_actions(self) -> None:
        """Создаёт все действия для меню."""
        self._create_current_action()
        self._create_visible_action()
        self._create_reset_action()
        
        log.debug("RefreshMenu: все действия созданы")
    
    def _create_current_action(self) -> None:
        """Создаёт действие для обновления текущего узла."""
        self._current_action = QAction(self._ACTION_CURRENT_TEXT, self)
        self._current_action.setShortcut(self._SHORTCUT_CURRENT)
        self._current_action.setToolTip(self._ACTION_CURRENT_TOOLTIP)
        self._current_action.triggered.connect(self.refresh_current.emit)
        
        log.debug("RefreshMenu: действие 'текущий узел' создано")
    
    def _create_visible_action(self) -> None:
        """Создаёт действие для обновления всех раскрытых узлов."""
        self._visible_action = QAction(self._ACTION_VISIBLE_TEXT, self)
        self._visible_action.setShortcut(self._SHORTCUT_VISIBLE)
        self._visible_action.setToolTip(self._ACTION_VISIBLE_TOOLTIP)
        self._visible_action.triggered.connect(self.refresh_visible.emit)
        
        log.debug("RefreshMenu: действие 'все раскрытые' создано")
    
    def _create_reset_action(self) -> None:
        """Создаёт действие для полной перезагрузки."""
        self._reset_action = QAction(self._ACTION_RESET_TEXT, self)
        self._reset_action.setShortcut(self._SHORTCUT_RESET)
        self._reset_action.setToolTip(self._ACTION_RESET_TOOLTIP)
        self._reset_action.triggered.connect(self.full_reset.emit)
        
        log.debug("RefreshMenu: действие 'полная перезагрузка' создано")
    
    def _populate_menu(self) -> None:
        """Заполняет меню созданными действиями."""
        self.addAction(self._current_action)
        self.addAction(self._visible_action)
        self.addSeparator()
        self.addAction(self._reset_action)
        
        log.debug("RefreshMenu: меню заполнено")
    
    # ===== Геттеры =====
    
    @property
    def current_action(self) -> QAction:
        """Возвращает действие обновления текущего узла."""
        return self._current_action
    
    @property
    def visible_action(self) -> QAction:
        """Возвращает действие обновления всех раскрытых узлов."""
        return self._visible_action
    
    @property
    def reset_action(self) -> QAction:
        """Возвращает действие полной перезагрузки."""
        return self._reset_action
    
    # ===== Публичные методы =====
    
    def set_actions_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает все действия меню.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._current_action.setEnabled(enabled)
        self._visible_action.setEnabled(enabled)
        self._reset_action.setEnabled(enabled)
        
        status = "включены" if enabled else "отключены"
        log.debug(f"RefreshMenu: все действия {status}")
    
    def set_current_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает действие обновления текущего узла.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._current_action.setEnabled(enabled)
        log.debug(f"RefreshMenu: действие 'текущий узел' {'включено' if enabled else 'отключено'}")
    
    def set_visible_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает действие обновления всех раскрытых узлов.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._visible_action.setEnabled(enabled)
        log.debug(f"RefreshMenu: действие 'все раскрытые' {'включено' if enabled else 'отключено'}")
    
    def set_reset_enabled(self, enabled: bool = True) -> None:
        """
        Включает или отключает действие полной перезагрузки.
        
        Args:
            enabled: True - включить, False - отключить
        """
        self._reset_action.setEnabled(enabled)
        log.debug(f"RefreshMenu: действие 'полная перезагрузка' {'включено' if enabled else 'отключено'}")