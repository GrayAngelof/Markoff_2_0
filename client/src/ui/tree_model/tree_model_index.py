# client/src/ui/tree_model/tree_model_index.py
"""
Миксин для работы с индексацией узлов дерева.
Предоставляет быстрый доступ к узлам по их типу и идентификатору.
"""
from typing import Optional, Dict

from PySide6.QtCore import QModelIndex

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModelIndexMixin:
    """
    Миксин для индексации узлов дерева.
    
    Предоставляет:
    - Словарь _node_index для быстрого доступа к узлам по ключу
    - Метод _make_key для создания ключа из типа и ID
    - Метод get_node_by_id для получения узла по типу и ID
    - Метод get_index_by_id для получения QModelIndex по типу и ID
    
    Требует наличия в классе:
    - _root_node: TreeNode - корневой узел
    - _index_of_node: метод для получения индекса из узла
    """
    
    def __init__(self, *args, **kwargs):
        """
        Инициализирует миксин индексации.
        Создаёт пустой словарь для индексации узлов.
        """
        super().__init__(*args, **kwargs)
        
        # Словарь для быстрого доступа к узлам по ключу
        self._node_index: Dict[str, TreeNode] = {}
        
        log.debug("TreeModelIndexMixin: инициализирован")
    
    # ===== Приватные методы =====
    
    def _make_key(self, node_type: NodeType, node_id: int) -> str:
        """
        Создаёт ключ для доступа к узлу в индексе.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            str: Ключ в формате "тип:id"
        """
        return f"{node_type.value}:{node_id}"
    
    def _add_to_index(self, node: TreeNode) -> None:
        """
        Добавляет узел в индекс.
        
        Args:
            node: Узел для добавления
        """
        key = self._make_key(node.node_type, node.get_id())
        self._node_index[key] = node
        log.debug(f"Узел добавлен в индекс: {key}")
    
    def _remove_from_index(self, node: TreeNode) -> None:
        """
        Удаляет узел из индекса.
        
        Args:
            node: Узел для удаления
        """
        key = self._make_key(node.node_type, node.get_id())
        if key in self._node_index:
            del self._node_index[key]
            log.debug(f"Узел удалён из индекса: {key}")
    
    def _clear_index(self) -> None:
        """Очищает индекс узлов."""
        self._node_index.clear()
        log.debug("Индекс узлов очищен")
    
    # ===== Публичные методы =====
    
    def get_node_by_id(self, node_type: NodeType, node_id: int) -> Optional[TreeNode]:
        """
        Получает узел по типу и идентификатору.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            Optional[TreeNode]: Узел или None, если не найден
        """
        key = self._make_key(node_type, node_id)
        node = self._node_index.get(key)
        
        if node is None:
            log.debug(f"Узел не найден в индексе: {key}")
        else:
            log.debug(f"Узел найден в индексе: {key}")
        
        return node
    
    def get_index_by_id(self, node_type: NodeType, node_id: int) -> QModelIndex:
        """
        Получает QModelIndex для узла по типу и идентификатору.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            QModelIndex: Индекс узла или пустой индекс
        """
        node = self.get_node_by_id(node_type, node_id)
        if node:
            return self._index_of_node(node)
        return QModelIndex()
    
    def has_node(self, node_type: NodeType, node_id: int) -> bool:
        """
        Проверяет, существует ли узел с указанными типом и ID.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            bool: True если узел существует
        """
        key = self._make_key(node_type, node_id)
        return key in self._node_index