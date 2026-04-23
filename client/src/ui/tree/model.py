# client/src/ui/tree/model.py
"""
Модель дерева для Qt.

Наследует QAbstractItemModel. Предоставляет данные из TreeNode для отображения в QTreeView.
Не знает о загрузке данных, EventBus и бизнес-логике.
"""

# ===== ИМПОРТЫ =====
from typing import Any, Dict, List, Optional, Tuple, Union

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QFont

from src.core.types import NodeType
from src.projections.tree_node import TreeNode
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)
ModelIndex = Union[QModelIndex, QPersistentModelIndex]


# ===== КЛАСС =====
class TreeModel(QAbstractItemModel):
    """
    Модель дерева для QTreeView.

    Никакой бизнес-логики, только отображение TreeNode.
    """

    # Кастомные роли для доступа к данным
    ItemIdRole = Qt.ItemDataRole.UserRole + 1
    ItemTypeRole = Qt.ItemDataRole.UserRole + 2
    ItemDataRole = Qt.ItemDataRole.UserRole + 3

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, root_nodes: Optional[List[TreeNode]] = None) -> None:
        super().__init__()
        self._root_nodes = root_nodes or []
        self._node_cache: Dict[Tuple[NodeType, int], TreeNode] = {}

        for node in self._root_nodes:
            self._cache_node(node)

        log.data(f"TreeModel создана с {len(self._root_nodes)} корневыми узлами")

    # ---- ПУБЛИЧНОЕ API ----
    def set_root_nodes(self, nodes: List[TreeNode]) -> None:
        """Полная замена корневых узлов."""
        log.data(f"Замена корневых узлов: {len(nodes)}")
        self.beginResetModel()
        self._root_nodes = nodes
        self._node_cache.clear()
        for node in self._root_nodes:
            self._cache_node(node)
        self.endResetModel()

    def insert_children(self, parent_node: TreeNode, children: List[TreeNode]) -> None:
        """Вставляет дочерние узлы в модель."""
        log.debug(f"insert_children: parent={parent_node.type}#{parent_node.id}, children={len(children)}")

        # Проверяем, есть ли родитель в кэше
        cached_parent = self._node_cache.get((parent_node.node_type, parent_node.id))
        if cached_parent is None:
            log.error(f"Родитель {parent_node.type}#{parent_node.id} не найден в кэше")
            return

        parent_index = self._get_index(cached_parent)
        if not parent_index.isValid():
            log.error(f"Родитель {parent_node.type}#{parent_node.id} не найден в модели")
            return

        first_row = cached_parent.child_count()
        last_row = first_row + len(children) - 1

        self.beginInsertRows(parent_index, first_row, last_row)
        cached_parent.add_children(children)
        for child in children:
            self._cache_node(child)
        self.endInsertRows()

        log.debug(f"Вставлено {len(children)} детей в {parent_node.type}#{parent_node.id}")

    def remove_children(self, parent_node: TreeNode, row: int, count: int) -> None:
        """Удаляет дочерние узлы."""
        if count == 0:
            return

        cached_parent = self._node_cache.get((parent_node.node_type, parent_node.id))
        if cached_parent is None:
            log.error(f"Родитель {parent_node.type}#{parent_node.id} не найден в кэше")
            return

        parent_index = self._get_index(cached_parent)
        if not parent_index.isValid():
            log.error(f"Родитель {parent_node.type}#{parent_node.id} не найден в модели")
            return

        self.beginRemoveRows(parent_index, row, row + count - 1)
        for _ in range(count):
            if row < len(cached_parent._children):
                removed = cached_parent._children.pop(row)
                self._node_cache.pop((removed.node_type, removed.id), None)
        self.endRemoveRows()

    def node_changed(self, node: TreeNode) -> None:
        """Уведомляет об изменении данных узла."""
        cached_node = self._node_cache.get((node.node_type, node.id))
        if cached_node is None:
            log.warning(f"Узел {node.type}#{node.id} не найден в кэше для обновления")
            return

        index = self._get_index(cached_node)
        if index.isValid():
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    def get_node_by_id(self, node_type: NodeType, node_id: int) -> Optional[TreeNode]:
        """Возвращает узел из кэша по типу и ID."""
        return self._node_cache.get((node_type, node_id))

    def get_all_cached_nodes(self) -> List[Tuple[NodeType, int]]:
        """Возвращает список всех ключей в кэше (для отладки)."""
        return list(self._node_cache.keys())

    # ---- РЕАЛИЗАЦИЯ QABSTRACTITEMMODEL ----
    def index(self, row: int, column: int, parent: ModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            if 0 <= row < len(self._root_nodes):
                return self.createIndex(row, column, self._root_nodes[row])
            return QModelIndex()

        parent_node = self._get_node(parent)
        if parent_node is None:
            return QModelIndex()

        child = parent_node.child_at(row)
        if child is None:
            return QModelIndex()

        return self.createIndex(row, column, child)

    def parent(self, index: ModelIndex) -> QModelIndex:  # type: ignore[override]
        if not index.isValid():
            return QModelIndex()

        child_node = self._get_node(index)
        if child_node is None or child_node.parent is None:
            return QModelIndex()

        return self.createIndex(child_node.parent.row(), 0, child_node.parent)

    def rowCount(self, parent: ModelIndex = QModelIndex()) -> int:
        parent_node = self._get_node(parent)
        if parent_node is None:
            return len(self._root_nodes)
        return parent_node.child_count()

    def columnCount(self, parent: ModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        node = self._get_node(index)
        if node is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return node.name
        if role == self.ItemIdRole:
            return node.id
        if role == self.ItemTypeRole:
            return node.type
        if role == self.ItemDataRole:
            return node.data
        return None

    def flags(self, index: ModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Optional[str]:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return "Объекты"
        return None

    def hasChildren(self, parent: ModelIndex = QModelIndex()) -> bool:
        parent_node = self._get_node(parent)
        if parent_node is None:
            return len(self._root_nodes) > 0
        return parent_node.has_children

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _cache_node(self, node: TreeNode) -> None:
        """Рекурсивно кэширует узел и всех его детей."""
        key = (node.node_type, node.id)
        self._node_cache[key] = node
        log.debug(f"Кэширован {key} -> '{node.name}'")

        for child in node.children:
            self._cache_node(child)

    def _get_node(self, index: ModelIndex) -> Optional[TreeNode]:
        """Возвращает TreeNode из internalPointer индекса."""
        if index.isValid():
            node = index.internalPointer()
            if isinstance(node, TreeNode):
                return node
        return None

    def _get_index(self, node: TreeNode) -> QModelIndex:
        """
        Возвращает QModelIndex для узла.

        Для корневых узлов: ищет позицию в _root_nodes.
        Для дочерних: создаёт индекс с row = позиция в родителе.
        """
        if node.parent is None:
            try:
                row = self._root_nodes.index(node)
                return self.createIndex(row, 0, node)
            except ValueError:
                log.error(f"Корневой узел {node.type}#{node.id} не найден в _root_nodes")
                return QModelIndex()
        else:
            return self.createIndex(node.row(), 0, node)