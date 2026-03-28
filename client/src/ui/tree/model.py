# client/src/ui/tree/model.py
"""
Модель дерева для Qt.

Наследует QAbstractItemModel. Предоставляет данные из TreeNode для отображения в QTreeView.
Не знает о загрузке данных и EventBus.
"""

# ===== ИМПОРТЫ =====
from typing import Any, Dict, Final, List, Optional, Tuple, Union, Final

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QBrush, QColor, QFont

from src.core.types import NodeType
from src.models.room import Room
from src.ui.tree.node import TreeNode
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)

# Тип для индекса (Qt может передавать QModelIndex или QPersistentModelIndex)
ModelIndex = Union[QModelIndex, QPersistentModelIndex]


# ===== КЛАСС =====
class TreeModel(QAbstractItemModel):
    """
    Модель дерева для QTreeView.

    Предоставляет данные из TreeNode для отображения.
    Не знает о загрузке данных и EventBus.

    Кастомные роли:
    - ItemIdRole: ID узла
    - ItemTypeRole: тип узла (complex, building, floor, room)
    - ItemDataRole: исходные данные (модель)
    """

    # Кастомные роли для доступа к данным
    ItemIdRole = Qt.ItemDataRole.UserRole + 1
    ItemTypeRole = Qt.ItemDataRole.UserRole + 2
    ItemDataRole = Qt.ItemDataRole.UserRole + 3

    # Локальные константы — цвета для разных типов узлов
    _COLOR_COMPLEX: Final[QColor] = QColor(0, 70, 130)      # темно-синий
    _COLOR_BUILDING: Final[QColor] = QColor(0, 100, 0)      # темно-зеленый
    _COLOR_FLOOR: Final[QColor] = QColor(100, 100, 100)     # серый
    _COLOR_ROOM_FREE: Final[QColor] = QColor(50, 150, 50)   # зеленый
    _COLOR_ROOM_OCCUPIED: Final[QColor] = QColor(200, 50, 50)  # красный
    _COLOR_DEFAULT: Final[QColor] = QColor(0, 0, 0)         # черный

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, root_nodes: Optional[List[TreeNode]] = None) -> None:
        """Инициализирует модель дерева."""
        super().__init__()
        self._root_nodes = root_nodes or []

        # Кэш узлов для быстрого доступа по типу и ID
        self._node_cache: Dict[Tuple[NodeType, int], TreeNode] = {}

        for node in self._root_nodes:
            self._node_cache[(node.node_type, node.id)] = node
            self._cache_children(node)

        log.data(f"TreeModel создана с {len(self._root_nodes)} корневыми узлами")

    # ---- ПУБЛИЧНОЕ API ----
    def set_root_nodes(self, nodes: List[TreeNode]) -> None:
        """Полная замена корневых узлов (полная перезагрузка дерева)."""
        log.data(f"Замена корневых узлов: {len(nodes)} узлов")

        self.beginResetModel()
        self._root_nodes = nodes

        self._node_cache.clear()
        for node in self._root_nodes:
            self._node_cache[(node.node_type, node.id)] = node
            self._cache_children(node)

        self.endResetModel()

        log.data(f"Модель дерева обновлена: {len(self._root_nodes)} корневых узлов")

    def insert_children(self, parent_node: TreeNode, children: List[TreeNode]) -> None:
        """Вставляет дочерние узлы в модель."""
        parent_display = f"{parent_node.type}#{parent_node.id}"
        log.data(f"Вставка {len(children)} детей в узел {parent_display}")

        parent_index = self._get_index(parent_node)
        if not parent_index.isValid():
            log.error(f"Не найден индекс родителя {parent_display}")
            return

        first_row = parent_node.child_count()
        last_row = first_row + len(children) - 1

        self.beginInsertRows(parent_index, first_row, last_row)

        parent_node.add_children(children)

        for child in children:
            self._node_cache[(child.node_type, child.id)] = child
            self._cache_children(child)

        self.endInsertRows()

        log.data(f"Вставлено {len(children)} детей в узел {parent_display}")

    def remove_children(self, parent_node: TreeNode, row: int, count: int) -> None:
        """Удаляет дочерние узлы из модели."""
        if count == 0:
            return

        parent_display = f"{parent_node.type}#{parent_node.id}"
        log.data(f"Удаление {count} детей из узла {parent_display}, начальная строка={row}")

        parent_index = self._get_index(parent_node)
        if not parent_index.isValid():
            log.error(f"Не найден индекс родителя {parent_display}")
            return

        if row < 0 or row + count > parent_node.child_count():
            log.error(f"Неверные границы удаления: row={row}, count={count}, total={parent_node.child_count()}")
            return

        removed_children = parent_node.children[row:row + count]

        self.beginRemoveRows(parent_index, row, row + count - 1)

        for _ in range(count):
            if row < len(parent_node._children):
                del parent_node._children[row]

        for child in removed_children:
            self._node_cache.pop((child.node_type, child.id), None)

        self.endRemoveRows()

        log.data(f"Удалено {count} детей из узла {parent_display}")

    def node_changed(self, node: TreeNode) -> None:
        """Уведомляет модель об изменении данных узла."""
        index = self._get_index(node)
        if index.isValid():
            log.debug(f"Узел изменён: {node.type}#{node.id}")
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    def get_node_by_id(self, node_type: NodeType, node_id: int) -> Optional[TreeNode]:
        """Возвращает узел по типу и ID из кэша."""
        return self._node_cache.get((node_type, node_id))

    # ---- МЕТОДЫ QABSTRACTITEMMODEL ----
    def index(self, row: int, column: int, parent: ModelIndex = QModelIndex()) -> QModelIndex:
        """Создаёт индекс для элемента."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            if 0 <= row < len(self._root_nodes):
                child_node = self._root_nodes[row]
                return self.createIndex(row, column, child_node)
            return QModelIndex()

        parent_node = self._get_node(parent)
        if parent_node is None:
            return QModelIndex()

        child_node = parent_node.child_at(row)
        if child_node is None:
            return QModelIndex()

        return self.createIndex(row, column, child_node)

    def parent(self, index: ModelIndex) -> QModelIndex:  # type: ignore
        """Возвращает родительский индекс."""
        if not index.isValid():
            return QModelIndex()

        child_node = self._get_node(index)
        if child_node is None:
            return QModelIndex()

        parent_node = child_node.parent
        if parent_node is None:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: ModelIndex = QModelIndex()) -> int:
        """Возвращает количество строк (детей) для родителя."""
        parent_node = self._get_node(parent)
        if parent_node is None:
            return len(self._root_nodes)
        return parent_node.child_count()

    def columnCount(self, parent: ModelIndex = QModelIndex()) -> int:
        """Возвращает количество колонок (всегда 1)."""
        return 1

    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Возвращает данные для отображения."""
        if not index.isValid():
            return None

        node = self._get_node(index)
        if node is None:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return node.name
        if role == Qt.ItemDataRole.FontRole:
            return self._get_font(node)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_color(node)
        if role == self.ItemIdRole:
            return node.id
        if role == self.ItemTypeRole:
            return node.type
        if role == self.ItemDataRole:
            return node.data

        return None

    def flags(self, index: ModelIndex) -> Qt.ItemFlag:
        """Возвращает флаги элемента."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Optional[str]:
        """Возвращает заголовок для колонки."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return "Объекты"
        return None

    def hasChildren(self, parent: ModelIndex = QModelIndex()) -> bool:
        """Определяет, может ли узел иметь дочерние элементы."""
        parent_node = self._get_node(parent)
        if parent_node is None:
            return len(self._root_nodes) > 0
        return parent_node.has_children

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _cache_children(self, node: TreeNode) -> None:
        """Рекурсивно кэширует всех детей узла."""
        for child in node.children:
            self._node_cache[(child.node_type, child.id)] = child
            self._cache_children(child)

    def _get_node(self, index: ModelIndex) -> Optional[TreeNode]:
        """Получает узел из индекса."""
        if index.isValid():
            node = index.internalPointer()
            if isinstance(node, TreeNode):
                return node
        return None

    def _get_index(self, node: TreeNode) -> QModelIndex:
        """Находит QModelIndex для TreeNode."""
        if node.parent is None:
            try:
                row = self._root_nodes.index(node)
                return self.createIndex(row, 0, node)
            except ValueError:
                log.error(f"_get_index: корневой узел {node.type}#{node.id} не найден")
                return QModelIndex()
        else:
            row = node.row()
            return self.createIndex(row, 0, node)

    def _get_font(self, node: TreeNode) -> QFont:
        """Возвращает шрифт для узла."""
        font = QFont()
        if node.type == 'complex' or node.type == 'building':
            font.setBold(True)
        return font

    def _get_color(self, node: TreeNode) -> QBrush:
        """Возвращает цвет для узла."""
        if node.type == 'complex':
            return QBrush(self._COLOR_COMPLEX)
        if node.type == 'building':
            return QBrush(self._COLOR_BUILDING)
        if node.type == 'floor':
            return QBrush(self._COLOR_FLOOR)
        if node.type == 'room' and isinstance(node.data, Room):
            if node.data.status_code == 'free':
                return QBrush(self._COLOR_ROOM_FREE)
            if node.data.status_code == 'occupied':
                return QBrush(self._COLOR_ROOM_OCCUPIED)
        return QBrush(self._COLOR_DEFAULT)