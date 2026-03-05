# client/src/ui/tree/tree_menu.py
"""
Модуль для контекстного меню дерева
"""
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import QPoint, Slot, Qt
from PySide6.QtGui import QAction
from functools import partial

from src.ui.tree_model import NodeType


class TreeMenuMixin:
    """
    Миксин для контекстного меню дерева
    """
    
    @Slot(QPoint)
    def _show_context_menu(self, position: QPoint):
        """Показать контекстное меню для узла"""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        node = self.model._get_node(index)
        if not node:
            return
        
        menu = QMenu()
        
        # Определяем тип узла для текста меню
        node_type_display = {
            NodeType.COMPLEX: "комплекс",
            NodeType.BUILDING: "корпус",
            NodeType.FLOOR: "этаж",
            NodeType.ROOM: "помещение"
        }.get(node.node_type, "объект")
        
        # Пункт обновления узла
        refresh_action = QAction(f"🔄 Обновить {node_type_display}", menu)
        refresh_action.triggered.connect(partial(self._refresh_node, index, False))
        menu.addAction(refresh_action)
        
        # Показываем меню
        menu.exec(self.tree_view.viewport().mapToGlobal(position))