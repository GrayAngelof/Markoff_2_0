# client/src/ui/refresh_menu.py
"""
Меню выбора типа обновления для дерева объектов
Содержит три пункта:
- Обновить текущий узел (F5)
- Обновить все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction


class RefreshMenu(QMenu):
    """
    Выпадающее меню для выбора типа обновления
    
    Сигналы:
        refresh_current: обновить текущий узел
        refresh_visible: обновить все раскрытые узлы
        full_reset: полная перезагрузка
    """
    
    refresh_current = Signal()
    refresh_visible = Signal()
    full_reset = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Обновить", parent)
        
        # Создаём пункты меню
        self._create_actions()
        
        # Добавляем в меню
        self.addAction(self.current_action)
        self.addAction(self.visible_action)
        self.addSeparator()
        self.addAction(self.reset_action)
        
        # Добавляем подсказки
        self.current_action.setToolTip("Обновить только выбранный узел (F5)")
        self.visible_action.setToolTip("Обновить все раскрытые узлы (Ctrl+F5)")
        self.reset_action.setToolTip("Полная перезагрузка всех данных (Ctrl+Shift+F5)")
        
        print("✅ RefreshMenu: создано")
    
    def _create_actions(self):
        """Создание действий меню"""
        # Обновить текущий
        self.current_action = QAction("🔄 Обновить текущий узел", self)
        self.current_action.setShortcut("F5")
        self.current_action.triggered.connect(self.refresh_current.emit)
        
        # Обновить все раскрытые
        self.visible_action = QAction("🔄 Обновить все раскрытые", self)
        self.visible_action.setShortcut("Ctrl+F5")
        self.visible_action.triggered.connect(self.refresh_visible.emit)
        
        # Полная перезагрузка
        self.reset_action = QAction("🔄 Полная перезагрузка", self)
        self.reset_action.setShortcut("Ctrl+Shift+F5")
        self.reset_action.triggered.connect(self.full_reset.emit)