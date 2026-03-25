# client/src/ui/tree/model.py
"""
Модель дерева для Qt. Наследует QAbstractItemModel.
Предоставляет данные из TreeNode для отображения в QTreeView.
"""

from typing import List, Optional, Any, Union, Dict, Tuple
from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QFont, QBrush, QColor

from src.core.types import NodeType
from src.ui.tree.node import TreeNode
from src.models.room import Room

from utils.logger import get_logger

log = get_logger(__name__)


# Тип для индекса (Qt может передавать QModelIndex или QPersistentModelIndex)
ModelIndex = Union[QModelIndex, QPersistentModelIndex]


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
    
    # Цвета для разных типов узлов
    _COLOR_COMPLEX = QColor(0, 70, 130)      # темно-синий
    _COLOR_BUILDING = QColor(0, 100, 0)      # темно-зеленый
    _COLOR_FLOOR = QColor(100, 100, 100)     # серый
    _COLOR_ROOM_FREE = QColor(50, 150, 50)   # зеленый
    _COLOR_ROOM_OCCUPIED = QColor(200, 50, 50)  # красный
    _COLOR_DEFAULT = QColor(0, 0, 0)         # черный
    
    def __init__(self, root_nodes: Optional[List[TreeNode]] = None):
        """
        Инициализирует модель дерева.
        
        Args:
            root_nodes: Список корневых узлов (комплексов)
        """
        super().__init__()
        self._root_nodes = root_nodes or []
        
        # Кэш узлов для быстрого доступа по типу и ID
        self._node_cache: Dict[Tuple[NodeType, int], TreeNode] = {}
        
        # Кэшируем корневые узлы
        for node in self._root_nodes:
            self._node_cache[(node.node_type, node.id)] = node
            self._cache_children(node)
        
        log.data(f"TreeModel создана с {len(self._root_nodes)} корневыми узлами")
        if log.is_debug_enabled():
            for i, node in enumerate(self._root_nodes):
                log.debug(f"  root_nodes[{i}]: type={node.type}, id={node.id}, name='{node.name}'")

    def _cache_children(self, node: TreeNode) -> None:
        """Рекурсивно кэширует всех детей узла."""
        for child in node.children:
            self._node_cache[(child.node_type, child.id)] = child
            self._cache_children(child)

    def get_node_by_id(self, node_type: NodeType, node_id: int) -> Optional[TreeNode]:
        """
        Возвращает узел по типу и ID из кэша.
        
        Args:
            node_type: Тип узла
            node_id: ID узла
            
        Returns:
            Optional[TreeNode]: Найденный узел или None
        """
        return self._node_cache.get((node_type, node_id))

    # ===== Публичные методы для управления данными =====
    
    def set_root_nodes(self, nodes: List[TreeNode]) -> None:
        """
        Полная замена корневых узлов (полная перезагрузка дерева).
        
        Args:
            nodes: Новые корневые узлы
        """
        log.data(f"Замена корневых узлов: {len(nodes)} узлов")
        
        if log.is_debug_enabled():
            for i, node in enumerate(nodes):
                log.debug(f"  узлы[{i}]: type={node.type}, id={node.id}, name='{node.name}'")
        
        self.beginResetModel()
        self._root_nodes = nodes
        # Обновляем кэш
        self._node_cache.clear()
        for node in self._root_nodes:
            self._node_cache[(node.node_type, node.id)] = node
            self._cache_children(node)
        self.endResetModel()
        
        log.data(f"Модель дерева обновлена: {len(self._root_nodes)} корневых узлов")
    
    def insert_children(self, parent_node: TreeNode, children: List[TreeNode]) -> None:
        """
        Вставляет дочерние узлы в модель.
        
        Args:
            parent_node: Родительский узел
            children: Список дочерних узлов для вставки
        """
#        log.info(f"insert_children: parent={parent_node.type}#{parent_node.id} ({parent_node.name})")
#        for i, child in enumerate(children):
#            log.debug(f"insert_children: child[{i}]: {child.type}#{child.id} ({child.name}), parent={child.parent.type if child.parent else 'None'}")

#        if not children:
#            log.debug("insert_children: пустой список, ничего не делаем")
#            return
        
        parent_display = f"{parent_node.type}#{parent_node.id}"
        log.data(f"Вставка {len(children)} детей в узел {parent_display}")
        
        # Находим индекс родителя
        parent_index = self._get_index(parent_node)
        if not parent_index.isValid():
            log.error(f"Не найден индекс родителя {parent_display}")
            return
        
        # Определяем позицию вставки (в конец)
        first_row = parent_node.child_count()
        last_row = first_row + len(children) - 1
        
        log.debug(f"  позиция вставки: rows {first_row}..{last_row}")
        
        # Сигнализируем Qt о начале вставки
        self.beginInsertRows(parent_index, first_row, last_row)
        
        # Добавляем детей в узел
        parent_node.add_children(children)
        
        # Добавляем детей в кэш
        for child in children:
            self._node_cache[(child.node_type, child.id)] = child
            self._cache_children(child)
        
        # Сигнализируем Qt о завершении вставки
        self.endInsertRows()
        
        log.data(f"Вставлено {len(children)} детей в узел {parent_display}")
    
    def remove_children(self, parent_node: TreeNode, row: int, count: int) -> None:
        """
        Удаляет дочерние узлы из модели.
        
        Args:
            parent_node: Родительский узел
            row: Начальная строка для удаления
            count: Количество удаляемых узлов
        """
        if count == 0:
            return
        
        parent_display = f"{parent_node.type}#{parent_node.id}"
        log.data(f"Удаление {count} детей из узла {parent_display}, начальная строка={row}")
        
        # Находим индекс родителя
        parent_index = self._get_index(parent_node)
        if not parent_index.isValid():
            log.error(f"Не найден индекс родителя {parent_display}")
            return
        
        # Проверяем границы
        if row < 0 or row + count > parent_node.child_count():
            log.error(f"Неверные границы удаления: row={row}, count={count}, total={parent_node.child_count()}")
            return
        
        # Получаем удаляемых детей для очистки кэша
        removed_children = parent_node.children[row:row + count]
        
        # Сигнализируем Qt о начале удаления
        self.beginRemoveRows(parent_index, row, row + count - 1)
        
        # Удаляем детей из узла
        for _ in range(count):
            if row < len(parent_node._children):
                del parent_node._children[row]
        
        # Удаляем детей из кэша
        for child in removed_children:
            self._node_cache.pop((child.node_type, child.id), None)
        
        # Сигнализируем Qt о завершении удаления
        self.endRemoveRows()
        
        log.data(f"Удалено {count} детей из узла {parent_display}")
    
    def node_changed(self, node: TreeNode) -> None:
        """
        Уведомляет модель об изменении данных узла.
        
        Args:
            node: Узел, данные которого изменились
        """
        index = self._get_index(node)
        if index.isValid():
            log.debug(f"Узел изменён: {node.type}#{node.id}")
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
    
    # ===== Методы QAbstractItemModel =====
    
    def index(self, row: int, column: int, parent: ModelIndex = QModelIndex()) -> QModelIndex:
        """
        Создает индекс для элемента.
        
        Args:
            row: Строка (позиция среди siblings)
            column: Колонка (всегда 0 для дерева)
            parent: Родительский индекс
            
        Returns:
            QModelIndex: Индекс элемента или пустой индекс
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        # Для корневого уровня (нет родителя)
        if not parent.isValid():
            if 0 <= row < len(self._root_nodes):
                child_node = self._root_nodes[row]
#                log.debug(f"index: корневой уровень row={row} -> {child_node.type}#{child_node.id}")
                return self.createIndex(row, column, child_node)
            return QModelIndex()
        
        # Для не корневого уровня
        parent_node = self._get_node(parent)
        if parent_node is None:
            return QModelIndex()
        
        child_node = parent_node.child_at(row)
        if child_node is None:
            return QModelIndex()
        
#        log.debug(f"index: создан индекс для {child_node.type}#{child_node.id}")
        return self.createIndex(row, column, child_node)
    
    def parent(self, index: ModelIndex) -> QModelIndex: # type: ignore
        """
        Возвращает родительский индекс.
        
        Args:
            index: Индекс элемента
            
        Returns:
            QModelIndex: Родительский индекс или пустой индекс
        """
        if not index.isValid():
            return QModelIndex()
        
        child_node = self._get_node(index)
        if child_node is None:
            return QModelIndex()
        
        parent_node = child_node.parent
        if parent_node is None:
#            log.debug(f"parent: {child_node.type}#{child_node.id} -> ROOT")
            return QModelIndex()
        
#        log.debug(f"parent: {child_node.type}#{child_node.id} -> {parent_node.type}#{parent_node.id}")
        return self.createIndex(parent_node.row(), 0, parent_node)
    
    def rowCount(self, parent: ModelIndex = QModelIndex()) -> int:
        """
        Возвращает количество строк (детей) для родителя.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            int: Количество дочерних элементов
        """
        parent_node = self._get_node(parent)
        if parent_node is None:
            count = len(self._root_nodes)
#            log.debug(f"rowCount: ROOT -> {count}")
            return count
        count = parent_node.child_count()
        
#        if log.is_debug_enabled():
#            log.debug(f"rowCount: {parent_node.type}#{parent_node.id} -> {count}")
        return count
    
    def columnCount(self, parent: ModelIndex = QModelIndex()) -> int:
        """
        Возвращает количество колонок.
        
        Args:
            parent: Родительский индекс (не используется)
            
        Returns:
            int: Всегда 1 (одна колонка)
        """
        return 1
    
    def data(self, index: ModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """
        Возвращает данные для отображения.
        
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
        
        if role == Qt.ItemDataRole.DisplayRole:
#            log.debug(f"DisplayRole: '{node.name}' ({node.type}#{node.id})")
            return node.name
        
        elif role == Qt.ItemDataRole.FontRole:
            return self._get_font(node)
        
        elif role == Qt.ItemDataRole.ForegroundRole:
            return self._get_color(node)
        
        elif role == self.ItemIdRole:
            return node.id
        
        elif role == self.ItemTypeRole:
            return node.type
        
        elif role == self.ItemDataRole:
            return node.data
        
        return None
    
    def flags(self, index: ModelIndex) -> Qt.ItemFlag:
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
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Optional[str]:
        """
        Возвращает заголовок для колонки.
        
        Args:
            section: Номер колонки
            orientation: Ориентация
            role: Роль данных
            
        Returns:
            Optional[str]: Заголовок или None
        """
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return "Объекты"
        return None
    
    def hasChildren(self, parent: ModelIndex = QModelIndex()) -> bool:
        """Определяет, может ли узел иметь дочерние элементы."""
        parent_node = self._get_node(parent)
        
        if parent_node is None:
            return len(self._root_nodes) > 0
        
        return parent_node.has_children

    # ===== Вспомогательные методы =====
    
    def _get_node(self, index: ModelIndex) -> Optional[TreeNode]:
        """
        Получает узел из индекса.
        
        Args:
            index: Индекс элемента
            
        Returns:
            Optional[TreeNode]: Узел или None
        """
        if index.isValid():
            node = index.internalPointer()
            if isinstance(node, TreeNode):
                return node
        return None
    
    def _get_index(self, node: TreeNode) -> QModelIndex:
        """
        Находит QModelIndex для TreeNode.
        
        Args:
            node: Узел дерева
            
        Returns:
            QModelIndex: Индекс узла или пустой индекс
        """
        log.debug(f"_get_index: ищем {node.type}#{node.id}, parent={node.parent.type if node.parent else 'None'}")
        
        if node.parent is None:
            # Корневой узел
            try:
                row = self._root_nodes.index(node)
                log.debug(f"_get_index: корневой узел {node.type}#{node.id}, row={row}")
                return self.createIndex(row, 0, node)
            except ValueError:
                log.error(f"_get_index: корневой узел {node.type}#{node.id} не найден в _root_nodes")
                if log.is_debug_enabled():
                    root_ids = [f"{n.type}#{n.id}" for n in self._root_nodes]
                    log.debug(f"_get_index: _root_nodes ids = {root_ids}")
                return QModelIndex()
        else:
            # Некорневой узел
            row = node.row()
            log.debug(f"_get_index: некорневой узел {node.type}#{node.id}, row={row}, parent={node.parent.type}#{node.parent.id}")
            return self.createIndex(row, 0, node)
    
    def _get_font(self, node: TreeNode) -> QFont:
        """
        Возвращает шрифт для узла.
        
        Args:
            node: Узел дерева
            
        Returns:
            QFont: Настроенный шрифт
        """
        font = QFont()
        if node.type == 'complex' or node.type == 'building':
            font.setBold(True)
        return font
    
    def _get_color(self, node: TreeNode) -> QBrush:
        """
        Возвращает цвет для узла.
        
        Args:
            node: Узел дерева
            
        Returns:
            QBrush: Цвет для отображения
        """
        if node.type == 'complex':
            return QBrush(self._COLOR_COMPLEX)
        elif node.type == 'building':
            return QBrush(self._COLOR_BUILDING)
        elif node.type == 'floor':
            return QBrush(self._COLOR_FLOOR)
        elif node.type == 'room' and isinstance(node.data, Room):
            if node.data.status_code == 'free':
                return QBrush(self._COLOR_ROOM_FREE)
            elif node.data.status_code == 'occupied':
                return QBrush(self._COLOR_ROOM_OCCUPIED)
        return QBrush(self._COLOR_DEFAULT)