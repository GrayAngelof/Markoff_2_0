# client/src/ui/main_window/shortcuts.py
"""
Модуль управления горячими клавишами главного окна.
Определяет сочетания клавиш для основных действий.
"""
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class ShortcutSignals(QObject):
    """Сигналы для горячих клавиш."""
    
    refresh_current = Signal()
    """Сигнал обновления текущего узла (F5)"""
    
    refresh_visible = Signal()
    """Сигнал обновления всех раскрытых узлов (Ctrl+F5)"""
    
    full_reset = Signal()
    """Сигнал полной перезагрузки (Ctrl+Shift+F5)"""


class ShortcutManager:
    """
    Менеджер горячих клавиш.
    
    Определяет и обрабатывает сочетания клавиш:
    - F5: обновить текущий узел
    - Ctrl+F5: обновить все раскрытые узлы
    - Ctrl+Shift+F5: полная перезагрузка
    """
    
    # ===== Константы =====
    _SHORTCUTS = {
        'refresh_current': QKeySequence.Refresh,  # F5
        'refresh_visible': QKeySequence(Qt.CTRL | Qt.Key_F5),
        'full_reset': QKeySequence(Qt.CTRL | Qt.SHIFT | Qt.Key_F5),
    }
    """Словарь сочетаний клавиш"""
    
    def __init__(self, parent: QMainWindow) -> None:
        """
        Инициализирует менеджер горячих клавиш.
        
        Args:
            parent: Родительское окно (MainWindow)
        """
        self._parent = parent
        self._actions = {}
        self.signals = ShortcutSignals()
        
        self._create_shortcuts()
        
        log.debug("ShortcutManager: инициализирован")
    
    # ===== Приватные методы =====
    
    def _create_shortcuts(self) -> None:
        """Создаёт все горячие клавиши."""
        self._create_refresh_current()
        self._create_refresh_visible()
        self._create_full_reset()
        
        log.debug("ShortcutManager: все горячие клавиши созданы")
    
    def _create_refresh_current(self) -> None:
        """Создаёт горячую клавишу F5 (обновить текущий узел)."""
        action = QAction(self._parent)
        action.setShortcut(self._SHORTCUTS['refresh_current'])
        action.triggered.connect(self.signals.refresh_current)
        self._parent.addAction(action)
        self._actions['refresh_current'] = action
        
        log.debug("ShortcutManager: создана клавиша F5")
    
    def _create_refresh_visible(self) -> None:
        """Создаёт горячую клавишу Ctrl+F5 (обновить все раскрытые)."""
        action = QAction(self._parent)
        action.setShortcut(self._SHORTCUTS['refresh_visible'])
        action.triggered.connect(self.signals.refresh_visible)
        self._parent.addAction(action)
        self._actions['refresh_visible'] = action
        
        log.debug("ShortcutManager: создана клавиша Ctrl+F5")
    
    def _create_full_reset(self) -> None:
        """Создаёт горячую клавишу Ctrl+Shift+F5 (полная перезагрузка)."""
        action = QAction(self._parent)
        action.setShortcut(self._SHORTCUTS['full_reset'])
        action.triggered.connect(self.signals.full_reset)
        self._parent.addAction(action)
        self._actions['full_reset'] = action
        
        log.debug("ShortcutManager: создана клавиша Ctrl+Shift+F5")
    
    # ===== Геттеры =====
    
    @property
    def actions(self) -> dict:
        """Возвращает словарь созданных действий."""
        return self._actions.copy()
    
    # ===== Публичные методы =====
    
    def enable_all(self) -> None:
        """Включает все горячие клавиши."""
        for action in self._actions.values():
            action.setEnabled(True)
        log.debug("ShortcutManager: все клавиши включены")
    
    def disable_all(self) -> None:
        """Отключает все горячие клавиши."""
        for action in self._actions.values():
            action.setEnabled(False)
        log.debug("ShortcutManager: все клавиши отключены")