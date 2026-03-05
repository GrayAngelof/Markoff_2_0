# client/src/ui/tree/tree_selection.py
"""
Модуль для работы с выделением узлов и контекстом иерархии
"""
from PySide6.QtCore import QModelIndex, Slot, Qt
from typing import Optional, Dict, Any, Tuple

from src.ui.tree_model import NodeType, TreeNode


class TreeSelectionMixin:
    """
    Миксин для работы с выделением узлов и контекстом
    """
    
    def _get_context_for_node(self, node: TreeNode) -> Dict[str, Any]:
        """
        Собрать контекст из родительских узлов
        
        Returns:
            dict: словарь с именами родительских узлов
                  {'complex_name': str, 'building_name': str, 'floor_num': int}
        """
        context = {
            'complex_name': None,
            'building_name': None,
            'floor_num': None
        }
        
        current = node
        while current:
            if current.node_type == NodeType.COMPLEX and current.data:
                context['complex_name'] = current.data.name
            elif current.node_type == NodeType.BUILDING and current.data:
                context['building_name'] = current.data.name
            elif current.node_type == NodeType.FLOOR and current.data:
                context['floor_num'] = current.data.number
            current = current.parent
        
        return context
    
    def get_selected_node_info(self) -> Optional[Tuple[str, int, Any]]:
        """Получить информацию о выбранном узле"""
        if not hasattr(self, 'tree_view') or not hasattr(self, 'model'):
            return None
        
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return None
        
        index = indexes[0]
        node = self.model._get_node(index)
        if node:
            return (node.node_type.value, node.get_id(), node.data)
        
        return None
    
    def select_node(self, node_type: str, node_id: int) -> bool:
        """Выбрать узел по типу и ID"""
        if not hasattr(self, 'model') or not hasattr(self, 'tree_view'):
            return False
        
        index = self.model.get_index_by_id(NodeType(node_type), node_id)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            return True
        return False
    
    @Slot(str, int, dict)
    def _restore_selection_safe(self, node_type: str, node_id: int, context: dict = None):
        """Безопасное восстановление выделения с поиском узла по ID"""
        try:
            index = self.model.get_index_by_id(NodeType(node_type), node_id)
            
            if index.isValid():
                node = self.model._get_node(index)
                if node and node.get_id() == node_id:
                    self.tree_view.setCurrentIndex(index)
                    # Передаём данные в сигнале с контекстом
                    if context is None:
                        context = self._get_context_for_node(node)
                    
                    if hasattr(self, 'item_selected'):
                        self.item_selected.emit(node_type, node_id, node.data, context)
                    
                    print(f"🔹 TreeView: восстановлено выделение {node_type} #{node_id}")
                    return
            
            print(f"⚠️ TreeView: узел {node_type} #{node_id} не найден, ищем родителя")
            self._restore_parent_selection(node_type, node_id)
            
        except Exception as e:
            print(f"❌ Ошибка при восстановлении выделения: {e}")
            import traceback
            traceback.print_exc()
    
    @Slot(str, int)
    def _restore_parent_selection(self, node_type: str, node_id: int):
        """Восстановить родительский узел, если не удалось найти целевой"""
        try:
            parent_type = None
            if node_type == NodeType.ROOM.value:
                parent_type = NodeType.FLOOR
            elif node_type == NodeType.FLOOR.value:
                parent_type = NodeType.BUILDING
            elif node_type == NodeType.BUILDING.value:
                parent_type = NodeType.COMPLEX
            else:
                return
            
            if parent_type == NodeType.COMPLEX:
                index = self.model.index(0, 0)
                if index.isValid():
                    self.tree_view.setCurrentIndex(index)
                    node = self.model._get_node(index)
                    if node:
                        context = self._get_context_for_node(node)
                        
                        if hasattr(self, 'item_selected'):
                            self.item_selected.emit(
                                NodeType.COMPLEX.value, 
                                node.get_id(), 
                                node.data, 
                                context
                            )
                        
                        print(f"🔹 TreeView: выбран комплекс #{node.get_id()} как запасной вариант")
                        
        except Exception as e:
            print(f"❌ Ошибка при восстановлении родителя: {e}")