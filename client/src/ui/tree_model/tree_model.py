# client/src/ui/tree_model/tree_model.py
"""
Конкретная реализация модели дерева.
Объединяет все миксины и базовый класс для создания полноценной модели
с поддержкой индексации и управления данными.

В новой архитектуре модель получает данные от проекции через события,
а не управляет данными напрямую.
"""
from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QFont, QBrush, QColor
from typing import Any, Optional, Union

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.ui.tree_model.tree_model_base import TreeModelBase
from src.ui.tree_model.tree_model_index import TreeModelIndexMixin
from src.models.room import Room
from utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModel(
    TreeModelBase,
    TreeModelIndexMixin,
):
    """
    Полноценная модель дерева объектов.
    
    В новой архитектуре модель ТОЛЬКО отображает данные,
    получая готовое дерево от проекции через события.
    
    Объединяет функциональность:
    - Базовые методы QAbstractItemModel (TreeModelBase)
    - Индексация узлов для быстрого доступа (TreeModelIndexMixin)
    
    НЕ содержит:
    - Логики загрузки данных (перенесена в DataLoader)
    - Управления кэшем (перенесено в EntityGraph)
    - Миксинов управления данными (TreeModelDataMixin больше не используется)
    
    Предоставляет:
    - Отображение иерархии комплексов, корпусов, этажей и помещений
    - Кастомные роли для доступа к данным узлов
    - Сигналы для отслеживания загрузки (унаследованы)
    """
    
    def __init__(self, projection=None, parent=None) -> None:
        """
        Инициализирует модель дерева.
        
        Args:
            projection: Проекция дерева (для подписки на обновления)
            parent: Родительский объект
        """
        # Инициализация базовых классов
        super().__init__(parent)
        
        self._projection = projection
        self._subscriptions = []
        
        # Если есть проекция, подписываемся на её обновления
        if projection:
            self._subscribe_to_projection()
        
        log.debug("TreeModel: инициализирована (реактивная версия)")
    
    def _subscribe_to_projection(self) -> None:
        """Подписывается на обновления проекции."""
        if self._projection and hasattr(self._projection, '_bus'):
            unsubscribe = self._projection._bus.subscribe(
                'projection.tree_updated', 
                self._on_tree_updated
            )
            self._subscriptions.append(unsubscribe)
            log.debug("TreeModel: подписана на обновления проекции")
        else:
            log.warning("TreeModel: не удалось подписаться на проекцию - отсутствует _bus")
    
    def _on_tree_updated(self, event: dict) -> None:
        """
        Получает новое дерево от проекции и обновляет модель.
        
        Args:
            event: Событие с данными:
                {
                    'data': {
                        'tree': List[TreeNode] - корневые узлы дерева
                    }
                }
        """
        log.debug("TreeModel: получено обновление от проекции")
        
        self.beginResetModel()
        
        # Очищаем текущее дерево
        self._root_node.remove_all_children()
        self._clear_index()
        
        # Получаем корневые узлы из проекции
        root_nodes = event['data'].get('tree', [])
        
        # Добавляем их как детей корневого узла модели
        for node in root_nodes:
            self._root_node.append_child(node)
            self._add_to_index(node)
        
        self.endResetModel()
        
        log.info(f"TreeModel: обновлена, загружено {len(root_nodes)} корневых узлов")
    
    def cleanup(self) -> None:
        """Отписывается от всех событий и очищает ресурсы."""
        for unsubscribe in self._subscriptions:
            unsubscribe()
        self._subscriptions.clear()
        log.debug("TreeModel: очищена")
    
    # ===== Переопределение методов QAbstractItemModel =====
    
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) -> Any:
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
        if node is None or node == self._root_node:
            return None
        
        # Обработка различных ролей
        if role == Qt.ItemDataRole.DisplayRole:
            return node.get_display_text()
        
        elif role == Qt.ItemDataRole.FontRole:
            return self._get_node_font(node)
        
        elif role == Qt.ItemDataRole.ForegroundRole:
            return self._get_node_color(node)
        
        elif role == self.ItemIdRole:
            return node.get_id()
        
        elif role == self.ItemTypeRole:
            return node.node_type.value
        
        elif role == self.ItemDataRole:
            return node.data
        
        return None
    
    def hasChildren(self, parent: Union[QModelIndex, QPersistentModelIndex] = QModelIndex()) -> bool:
        """
        Определяет, может ли узел иметь дочерние элементы.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            bool: True если узел имеет детей
        """
        parent_node = self._get_node(parent)
        
        # Корневой узел
        if parent_node is None or parent_node == self._root_node:
            return self._root_node.child_count() > 0
        
        # Проверяем наличие детей у узла
        return parent_node.child_count() > 0
    
    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]) -> Qt.ItemFlag:
        """
        Возвращает флаги элемента.
        
        Args:
            index: Индекс элемента
            
        Returns:
            Qt.ItemFlag: Флаги элемента
        """
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
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
        elif room.status_code == 'reserved':
            return QBrush(QColor(255, 165, 0))  # оранжевый для зарезервированных
        elif room.status_code == 'maintenance':
            return QBrush(QColor(128, 128, 128))  # серый для ремонта
        
        return QBrush(self._COLOR_DEFAULT)
    
    # ===== Методы для обратной совместимости (deprecated) =====
    
    def set_complexes(self, complexes: list) -> None:
        """
        Устаревший метод. В новой архитектуре данные приходят через проекцию.
        
        Args:
            complexes: Список комплексов (игнорируется)
        """
        log.warning("TreeModel.set_complexes() устарел. Данные должны приходить через проекцию.")
        # Ничего не делаем, просто логируем предупреждение
    
    def add_children(self, parent_index, children_data, child_type) -> None:
        """
        Устаревший метод. В новой архитектуре данные приходят через проекцию.
        """
        log.warning("TreeModel.add_children() устарел. Данные должны приходить через проекцию.")
    
    def update_children(self, parent_index, children_data, child_type) -> None:
        """
        Устаревший метод. В новой архитектуре данные приходят через проекцию.
        """
        log.warning("TreeModel.update_children() устарел. Данные должны приходить через проекцию.")