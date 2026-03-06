# client/src/ui/tree_model/tree_model.py
"""
Конкретная реализация модели дерева.
Объединяет все миксины и базовый класс для создания полноценной модели
с поддержкой индексации и управления данными.
"""
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QFont, QBrush
from typing import Any, Optional

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.ui.tree_model.tree_model_base import TreeModelBase
from src.ui.tree_model.tree_model_index import TreeModelIndexMixin
from src.ui.tree_model.tree_model_data import TreeModelDataMixin
from src.models.room import Room
from src.core.cache import DataCache
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModel(
    TreeModelBase,
    TreeModelIndexMixin,
    TreeModelDataMixin
):
    """
    Полноценная модель дерева объектов.
    
    Объединяет функциональность:
    - Базовые методы QAbstractItemModel (TreeModelBase)
    - Индексация узлов для быстрого доступа (TreeModelIndexMixin)
    - Управление данными (TreeModelDataMixin)
    
    Предоставляет:
    - Отображение иерархии комплексов, корпусов, этажей и помещений
    - Кастомные роли для доступа к данным узлов
    - Сигналы для отслеживания загрузки
    - Работу с системой кэширования
    """
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует модель дерева.
        
        Args:
            parent: Родительский объект
        """
        # Инициализация базовых классов
        super().__init__(parent)
        
        # Система кэширования (будет установлена извне)
        self._cache: Optional[DataCache] = None
        
        log.debug("TreeModel: инициализирована")
    
    # ===== Публичные методы =====
    
    def set_cache(self, cache: DataCache) -> None:
        """
        Устанавливает систему кэширования.
        
        Args:
            cache: Система кэширования данных
        """
        self._cache = cache
        log.debug("TreeModel: кэш установлен")
    
    # ===== Переопределение методов QAbstractItemModel =====
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Возвращает данные для отображения элемента.
        
        Args:
            index: Индекс элемента
            role: Роль данных
            
        Returns:
            Any: Данные для указанной роли или None
        """
        if not index.isValid():
            return None
        
        node = self._get_node(index)
        if node is None:
            return None
        
        # Обработка различных ролей
        if role == Qt.DisplayRole:
            return node.get_display_text()
        
        elif role == Qt.FontRole:
            return self._get_node_font(node)
        
        elif role == Qt.ForegroundRole:
            return self._get_node_color(node)
        
        elif role == self.ItemIdRole:
            return node.get_id()
        
        elif role == self.ItemTypeRole:
            return node.node_type.value
        
        elif role == self.ItemDataRole:
            return node.data
        
        return None
    
    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        """
        Определяет, может ли узел иметь дочерние элементы.
        
        Критерий: узел имеет детей ТОЛЬКО если счётчик в скобках > 0.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            bool: True если узел может иметь детей
        """
        parent_node = self._get_node(parent)
        
        # Корневой узел
        if parent_node is None or parent_node == self._root_node:
            return self._root_node.child_count() > 0
        
        # Комнаты никогда не имеют детей
        if parent_node.node_type == NodeType.ROOM:
            return False
        
        # Для остальных типов проверяем соответствующий счётчик
        return self._check_node_has_children(parent_node)
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_node_font(self, node: TreeNode) -> QFont:
        """
        Возвращает шрифт для узла в зависимости от его типа.
        
        Args:
            node: Узел дерева
            
        Returns:
            QFont: Настроенный шрифт
        """
        font = QFont()
        
        if node.node_type == NodeType.COMPLEX:
            font.setBold(True)
            font.setPointSize(font.pointSize() + self._FONT_SIZE_COMPLEX_BOOST)
        elif node.node_type == NodeType.BUILDING:
            font.setBold(True)
        
        return font
    
    def _get_node_color(self, node: TreeNode) -> QBrush:
        """
        Возвращает цвет для узла в зависимости от его типа и статуса.
        
        Args:
            node: Узел дерева
            
        Returns:
            QBrush: Цвет для отображения
        """
        if node.node_type == NodeType.COMPLEX:
            return QBrush(self._COLOR_COMPLEX)
        
        elif node.node_type == NodeType.BUILDING:
            return QBrush(self._COLOR_BUILDING)
        
        elif node.node_type == NodeType.FLOOR:
            return QBrush(self._COLOR_FLOOR)
        
        elif node.node_type == NodeType.ROOM and isinstance(node.data, Room):
            return self._get_room_color(node.data)
        
        return QBrush(self._COLOR_DEFAULT)
    
    def _get_room_color(self, room: Room) -> QBrush:
        """
        Возвращает цвет для помещения в зависимости от его статуса.
        
        Args:
            room: Данные помещения
            
        Returns:
            QBrush: Цвет для отображения
        """
        if room.status_code == 'occupied':
            return QBrush(self._COLOR_ROOM_OCCUPIED)
        elif room.status_code == 'free':
            return QBrush(self._COLOR_ROOM_FREE)
        
        return QBrush(self._COLOR_DEFAULT)
    
    def _check_node_has_children(self, node: TreeNode) -> bool:
        """
        Проверяет, может ли узел иметь детей на основе его данных.
        
        Args:
            node: Узел для проверки
            
        Returns:
            bool: True если узел может иметь детей
        """
        if node.node_type == NodeType.COMPLEX:
            if hasattr(node.data, 'buildings_count'):
                return node.data.buildings_count > 0
        
        elif node.node_type == NodeType.BUILDING:
            if hasattr(node.data, 'floors_count'):
                return node.data.floors_count > 0
        
        elif node.node_type == NodeType.FLOOR:
            if hasattr(node.data, 'rooms_count'):
                return node.data.rooms_count > 0
        
        return False