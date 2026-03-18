# client/src/ui/tree/tree_view.py
"""
Виджет дерева объектов.
Генерирует события при действиях пользователя через EventBus.
"""
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import QModelIndex, Qt, Slot

from src.ui.tree_model.tree_node import TreeNode
from src.ui.tree_model.tree_model import TreeModel

from utils.logger import get_logger

log = get_logger(__name__)


class TreeView(QTreeView):
    """
    Виджет дерева.
    
    Генерирует события через EventBus:
    - ui.node_expanded - при раскрытии узла
    - ui.node_collapsed - при сворачивании узла
    - ui.node_selected - при выборе узла
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._bus = None  # будет установлен извне
        
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setAlternatingRowColors(True)
        
        # Подключаем сигналы Qt (только для получения событий от Qt)
        self.expanded.connect(self._on_expanded)
        self.collapsed.connect(self._on_collapsed)
        
        log.debug("TreeView инициализирован")
    
    def set_event_bus(self, bus):
        """Устанавливает шину событий."""
        self._bus = bus
    
    def set_model(self, model: TreeModel):
        """Устанавливает модель дерева."""
        super().setModel(model)
        log.debug("Модель установлена")
    
    @Slot(QModelIndex)
    def _on_expanded(self, index):
        """Узел раскрыт - генерируем событие."""
        node = index.internalPointer()
        if self._bus and node and isinstance(node, TreeNode):
            self._bus.emit('ui.node_expanded', {
                'node_type': node.node_type,
                'node_id': node.get_id()
            }, source='tree_view')
            log.debug(f"Раскрыт узел {node.node_type}#{node.get_id()}")
    
    @Slot(QModelIndex)
    def _on_collapsed(self, index):
        """Узел свёрнут - генерируем событие."""
        node = index.internalPointer()
        if self._bus and node and isinstance(node, TreeNode):
            self._bus.emit('ui.node_collapsed', {
                'node_type': node.node_type,
                'node_id': node.get_id()
            }, source='tree_view')
    
    def selectionChanged(self, selected, deselected):
        """Выделение изменилось - генерируем событие."""
        super().selectionChanged(selected, deselected)
        
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            node = index.internalPointer()
            if node and isinstance(node, TreeNode) and self._bus:
                # ИСПРАВЛЕНО: генерируем событие через EventBus
                self._bus.emit('ui.node_selected', {
                    'node_type': node.node_type,
                    'node_id': node.get_id(),
                    'data': node.data
                }, source='tree_view')
                log.debug(f"Выбран узел {node.node_type}#{node.get_id()}")