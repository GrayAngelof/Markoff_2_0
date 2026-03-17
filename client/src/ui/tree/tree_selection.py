# client/src/ui/tree/tree_selection.py
"""
Модуль для работы с выделением узлов и контекстом иерархии.
В новой архитектуре предоставляет только утилитные функции.
"""
from typing import Optional, Dict, Any, Tuple
from PySide6.QtCore import QModelIndex

from src.ui.tree_model.tree_node import TreeNode
from src.ui.tree_model import NodeType

from utils.logger import get_logger
log = get_logger(__name__)


class TreeSelectionUtils:
    """
    Утилиты для работы с выделением узлов дерева.
    
    Предоставляет статические методы для:
    - Получения информации о выделенном узле
    - Сбора контекста из родительских узлов
    """
    
    @staticmethod
    def get_selected_node_info(index: QModelIndex) -> Optional[Tuple[str, int, Any]]:
        """
        Получает информацию о выбранном узле по индексу.
        
        Args:
            index: Индекс выбранного узла
            
        Returns:
            Кортеж (тип_узла, идентификатор, данные) или None
        """
        if not index.isValid():
            return None
        
        node = index.internalPointer()
        if not node or not isinstance(node, TreeNode):
            return None
        
        return (node.node_type.value, node.get_id(), node.data)
    
    @staticmethod
    def get_context_for_node(node: TreeNode, graph=None, loader=None) -> Dict[str, Any]:
        """
        Собирает контекст из родительских узлов.
        
        Args:
            node: Узел, для которого собирается контекст
            graph: Граф сущностей (опционально, для загрузки владельцев)
            loader: Загрузчик данных (опционально, для загрузки владельцев)
            
        Returns:
            Словарь с контекстом:
            {
                'complex_name': str или None,
                'building_name': str или None,
                'floor_num': int или None,
                'owner_name': str или None
            }
        """
        context: Dict[str, Any] = {
            'complex_name': None,
            'building_name': None,
            'floor_num': None,
            'owner_name': None
        }
        
        current_node = node
        while current_node is not None:
            # Проверяем тип текущего узла и извлекаем соответствующую информацию
            if current_node.node_type == NodeType.COMPLEX and current_node.data:
                context['complex_name'] = current_node.data.name
                
            elif current_node.node_type == NodeType.BUILDING and current_node.data:
                context['building_name'] = current_node.data.name
                
                # Если есть graph и loader, можно загрузить владельца
                if graph and loader and hasattr(current_node.data, 'owner_id'):
                    owner_id = current_node.data.owner_id
                    if owner_id:
                        owner = loader.load_counterparty(owner_id)
                        if owner:
                            context['owner_name'] = owner.short_name
                            
            elif current_node.node_type == NodeType.FLOOR and current_node.data:
                context['floor_num'] = current_node.data.number
            
            # Переходим к родителю
            current_node = current_node.parent
        
        return context
    
    @staticmethod
    def find_node_by_id(model, node_type: NodeType, node_id: int) -> Optional[QModelIndex]:
        """
        Находит индекс узла по типу и идентификатору.
        
        Args:
            model: Модель дерева
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            QModelIndex или None, если узел не найден
        """
        if hasattr(model, 'get_index_by_id'):
            return model.get_index_by_id(node_type, node_id)
        
        log.warning("Модель не поддерживает get_index_by_id")
        return QModelIndex()
    
    @staticmethod
    def collect_ancestors_info(node: TreeNode) -> Dict[str, Any]:
        """
        Собирает информацию о всех предках узла.
        
        Args:
            node: Узел дерева
            
        Returns:
            Словарь с информацией о предках
        """
        ancestors = []
        current = node.parent
        
        while current:
            ancestors.append({
                'type': current.node_type.value,
                'id': current.get_id(),
                'name': str(current.data) if current.data else None
            })
            current = current.parent
        
        return {
            'node_type': node.node_type.value,
            'node_id': node.get_id(),
            'ancestors': ancestors
        }