# client/src/ui/tree/tree_view.py
"""
Виджет дерева объектов.
Генерирует события при действиях пользователя.
"""
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import Signal, QModelIndex, Qt

from src.ui.tree_model.tree_node import TreeNode  # правильный импорт
from src.ui.tree_model.tree_model import TreeModel  # <-- ИСПРАВЛЕНО: импортируем модель
from src.ui.tree.tree_selection import TreeSelectionUtils

from utils.logger import get_logger

log = get_logger(__name__)


class TreeView(QTreeView):
    """
    Виджет дерева.
    
    Сигналы:
        item_selected: выбран элемент (тип, ID, данные, контекст)
    """
    
    item_selected = Signal(str, int, object, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._bus = None  # будет установлен извне
        
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setAlternatingRowColors(True)
        
        # Подключаем сигналы
        self.expanded.connect(self._on_expanded)
        self.collapsed.connect(self._on_collapsed)
        
        log.debug("TreeView инициализирован")
    
    def set_event_bus(self, bus):
        """Устанавливает шину событий."""
        self._bus = bus
    
    def set_model(self, model: TreeModel):  # <-- ИСПРАВЛЕНО: типизация
        """Устанавливает модель дерева."""
        super().setModel(model)
        log.debug("Модель установлена")
    
    def _on_expanded(self, index):
        """Узел раскрыт."""
        node = index.internalPointer()
        if self._bus and node and isinstance(node, TreeNode):
            self._bus.emit('ui.node_expanded', {
                'node_type': node.node_type,
                'node_id': node.get_id()
            }, source='tree_view')
            log.debug(f"Раскрыт узел {node.node_type}#{node.get_id()}")
    
    def _on_collapsed(self, index):
        """Узел свёрнут."""
        node = index.internalPointer()
        if self._bus and node and isinstance(node, TreeNode):
            self._bus.emit('ui.node_collapsed', {
                'node_type': node.node_type,
                'node_id': node.get_id()
            }, source='tree_view')
    
    def selectionChanged(self, selected, deselected):
        """Выделение изменилось."""
        super().selectionChanged(selected, deselected)
        
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            node = index.internalPointer()
            if node and isinstance(node, TreeNode):
                # Собираем контекст (будет заполнен контроллером)
                context = {}
                self.item_selected.emit(
                    node.node_type.value,
                    node.get_id(),
                    node.data,
                    context
                )
                log.debug(f"Выбран узел {node.node_type}#{node.get_id()}")

