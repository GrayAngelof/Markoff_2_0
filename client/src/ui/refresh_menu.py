# client/src/ui/refresh_menu.py
"""
Выпадающее меню для выбора типа обновления данных
Поддерживает три уровня:
- Текущий узел (F5)
- Видимые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal, Slot, Qt


class RefreshMenu(QMenu):
    """
    Меню выбора типа обновления
    
    Сигналы:
        refresh_current: обновить текущий выбранный узел
        refresh_visible: обновить все раскрытые узлы
        full_reset: полная перезагрузка
    """
    
    refresh_current = Signal()
    refresh_visible = Signal()
    full_reset = Signal()
    
    def __init__(self, parent=None):
        """Инициализация меню"""
        super().__init__("Обновить", parent)
        
        # Пункт "Обновить текущий узел"
        current_action = QAction("🔄 Обновить текущий узел", self)
        current_action.setShortcut(QKeySequence("F5"))
        current_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        current_action.setStatusTip("Обновить только выбранный узел и его содержимое")
        current_action.triggered.connect(self.refresh_current.emit)
        self.addAction(current_action)
        
        # Пункт "Обновить видимые узлы"
        visible_action = QAction("🔄 Обновить видимые узлы", self)
        visible_action.setShortcut(QKeySequence("Ctrl+F5"))
        visible_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        visible_action.setStatusTip("Обновить все раскрытые в данный момент узлы")
        visible_action.triggered.connect(self.refresh_visible.emit)
        self.addAction(visible_action)
        
        # Разделитель
        self.addSeparator()
        
        # Пункт "Полная перезагрузка"
        reset_action = QAction("🔄 Полная перезагрузка", self)
        reset_action.setShortcut(QKeySequence("Ctrl+Shift+F5"))
        reset_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        reset_action.setStatusTip("Очистить весь кэш и загрузить всё заново")
        reset_action.triggered.connect(self.full_reset.emit)
        self.addAction(reset_action)
        
        # Добавляем подсказки
        current_action.setToolTip("Обновить только текущий узел (F5)")
        visible_action.setToolTip("Обновить все раскрытые узлы (Ctrl+F5)")
        reset_action.setToolTip("Полная перезагрузка (Ctrl+Shift+F5)")
        
        print("✅ RefreshMenu: создано")