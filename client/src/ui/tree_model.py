# client/src/ui/tree_model.py
"""
Универсальная модель дерева для отображения иерархии объектов
Поддерживает все типы узлов: Complex, Building, Floor, Room
Работает в связке с системой кэширования DataCache
"""
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QFont, QBrush, QColor
from typing import Optional, List, Any, Union
from enum import Enum

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class NodeType(Enum):
    """Типы узлов дерева"""
    COMPLEX = "complex"
    BUILDING = "building"
    FLOOR = "floor"
    ROOM = "room"


class TreeNode:
    """
    Узел дерева, содержит данные и связи с родителем/детьми
    
    Атрибуты:
        data: модель данных (Complex, Building, Floor или Room)
        node_type: тип узла (NodeType)
        parent: родительский узел (или None для корня)
        children: список дочерних узлов
        loaded: флаг, загружены ли дочерние элементы
        loading: флаг, идёт ли загрузка (для индикатора)
    """
    
    def __init__(self, data: Any, node_type: NodeType, parent: Optional['TreeNode'] = None):
        self.data = data
        self.node_type = node_type
        self.parent = parent
        self.children: List['TreeNode'] = []
        self.loaded = False
        self.loading = False
    
    def append_child(self, child: 'TreeNode'):
        """Добавить дочерний узел"""
        self.children.append(child)
    
    def remove_children(self):
        """Удалить всех детей"""
        self.children.clear()
        self.loaded = False
    
    def child_at(self, row: int) -> Optional['TreeNode']:
        """Получить ребёнка по индексу"""
        if 0 <= row < len(self.children):
            return self.children[row]
        return None
    
    def row(self) -> int:
        """Индекс этого узла в родителе"""
        if self.parent:
            return self.parent.children.index(self)
        return 0
    
    def child_count(self) -> int:
        """Количество детей"""
        return len(self.children)
    
    def has_children(self) -> bool:
        """Есть ли дети (для отображения стрелочки)"""
        if self.node_type == NodeType.ROOM:
            return False  # У комнат нет детей
        # Для остальных типов дети могут быть, даже если ещё не загружены
        return True
    
    def get_display_text(self) -> str:
        """
        Получить текст для отображения в дереве
        Для каждого типа узла своё форматирование
        """
        if self.node_type == NodeType.COMPLEX and isinstance(self.data, Complex):
            return self.data.display_name()
        
        elif self.node_type == NodeType.BUILDING and isinstance(self.data, Building):
            if self.data.floors_count > 0:
                return f"{self.data.name} ({self.data.floors_count})"
            return self.data.name
        
        elif self.node_type == NodeType.FLOOR and isinstance(self.data, Floor):
            # Специальная обработка для подвалов и цоколя
            if self.data.number < 0:
                floor_text = f"Подвал {abs(self.data.number)}"
            elif self.data.number == 0:
                floor_text = "Цокольный этаж"
            else:
                floor_text = f"Этаж {self.data.number}"
            
            if self.data.rooms_count > 0:
                return f"{floor_text} ({self.data.rooms_count})"
            return floor_text
        
        elif self.node_type == NodeType.ROOM and isinstance(self.data, Room):
            return self.data.number
        
        return "???"
    
    def get_id(self) -> int:
        """Получить ID узла"""
        if hasattr(self.data, 'id'):
            return self.data.id
        return -1
    
    def __repr__(self):
        return f"TreeNode({self.node_type.value}, id={self.get_id()}, loaded={self.loaded})"


class TreeModel(QAbstractItemModel):
    """
    Модель данных для дерева объектов
    
    Сигналы:
        data_loading: испускается при начале загрузки данных для узла
        data_loaded: испускается после загрузки данных
        data_error: испускается при ошибке загрузки
    """
    
    # Кастомные роли для данных
    ItemIdRole = Qt.UserRole + 1      # ID объекта
    ItemTypeRole = Qt.UserRole + 2    # Тип объекта (NodeType)
    ItemDataRole = Qt.UserRole + 3    # Сырые данные (модель)
    ItemLoadingRole = Qt.UserRole + 4 # Флаг загрузки
    
    # Сигналы
    data_loading = Signal(NodeType, int)  # началась загрузка узла
    data_loaded = Signal(NodeType, int)   # данные загружены
    data_error = Signal(NodeType, int, str)  # ошибка загрузки
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Корневой узел (виртуальный, не отображается)
        self._root_node = TreeNode(None, None)
        # Словарь для быстрого доступа к узлам по ID
        self._node_index: dict[str, TreeNode] = {}
        self._cache = None  # будет установлен извне
    
    def set_cache(self, cache):
        """Установить систему кэширования"""
        self._cache = cache
    
    # ===== Базовые методы QAbstractItemModel =====
    
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """
        Создаёт индекс для элемента по строке и колонке
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        parent_node = self._get_node(parent)
        if parent_node is None:
            return QModelIndex()
        
        child_node = parent_node.child_at(row)
        if child_node is None:
            return QModelIndex()
        
        return self.createIndex(row, column, child_node)
    
    def parent(self, index: QModelIndex) -> QModelIndex:
        """
        Возвращает родительский индекс для данного индекса
        """
        if not index.isValid():
            return QModelIndex()
        
        child_node = self._get_node(index)
        if child_node is None:
            return QModelIndex()
        
        parent_node = child_node.parent
        if parent_node is None or parent_node == self._root_node:
            return QModelIndex()
        
        return self.createIndex(parent_node.row(), 0, parent_node)
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Количество строк (дочерних элементов) для родителя
        """
        parent_node = self._get_node(parent)
        if parent_node is None:
            return 0
        return parent_node.child_count()
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """В дереве всегда одна колонка"""
        return 1
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """
        Возвращает данные для отображения
        """
        if not index.isValid():
            return None
        
        node = self._get_node(index)
        if node is None:
            return None
        
        if role == Qt.DisplayRole:
            return node.get_display_text()
        
        elif role == Qt.FontRole:
            # Разные шрифты для разных типов узлов
            font = QFont()
            if node.node_type == NodeType.COMPLEX:
                font.setBold(True)
                font.setPointSize(font.pointSize() + 1)
            elif node.node_type == NodeType.BUILDING:
                font.setBold(True)
            return font
        
        elif role == Qt.ForegroundRole:
            # Цвет текста в зависимости от типа и статуса
            if node.node_type == NodeType.COMPLEX:
                return QBrush(QColor(0, 70, 130))  # Тёмно-синий
            elif node.node_type == NodeType.BUILDING:
                return QBrush(QColor(0, 100, 0))  # Тёмно-зелёный
            elif node.node_type == NodeType.FLOOR:
                return QBrush(QColor(100, 100, 100))  # Серый
            elif node.node_type == NodeType.ROOM and isinstance(node.data, Room):
                # Для комнат цвет зависит от статуса
                if node.data.status_code == 'occupied':
                    return QBrush(QColor(200, 50, 50))  # Красный для занятых
                elif node.data.status_code == 'free':
                    return QBrush(QColor(50, 150, 50))  # Зелёный для свободных
            return QBrush(QColor(0, 0, 0))  # Чёрный по умолчанию
        
        elif role == Qt.FontRole and node.loading:
            # Для загружающихся узлов - курсив
            font = QFont()
            font.setItalic(True)
            return font
        
        elif role == self.ItemIdRole:
            return node.get_id()
        
        elif role == self.ItemTypeRole:
            return node.node_type.value
        
        elif role == self.ItemDataRole:
            return node.data
        
        elif role == self.ItemLoadingRole:
            return node.loading
        
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Флаги элемента (можно выбирать, но нельзя редактировать)"""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """Заголовок для колонки"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Объекты"
        return None
    
    # ===== Вспомогательные методы =====
    
    def _get_node(self, index: QModelIndex) -> Optional[TreeNode]:
        """Получить узел из индекса"""
        if index.isValid():
            node = index.internalPointer()
            if isinstance(node, TreeNode):
                return node
        return self._root_node
    
    def _make_key(self, node_type: NodeType, node_id: int) -> str:
        """Создать ключ для индекса узлов"""
        return f"{node_type.value}:{node_id}"
    
    def _index_of_node(self, node: TreeNode) -> QModelIndex:
        """Создать QModelIndex для узла"""
        if node is None or node == self._root_node:
            return QModelIndex()
        return self.createIndex(node.row(), 0, node)
    
    # ===== Методы для управления данными =====
    
    def set_complexes(self, complexes: List[Complex]):
        """
        Установить список комплексов (корневые узлы)
        Вызывается при инициализации и полной перезагрузке
        """
        self.beginResetModel()
        
        # Очищаем всё
        self._root_node.children.clear()
        self._node_index.clear()
        
        # Создаём узлы для комплексов
        for complex_data in complexes:
            node = TreeNode(complex_data, NodeType.COMPLEX, self._root_node)
            self._root_node.append_child(node)
            
            # Сохраняем в индекс для быстрого доступа
            key = self._make_key(NodeType.COMPLEX, complex_data.id)
            self._node_index[key] = node
        
        self.endResetModel()
        
        print(f"✅ TreeModel: загружено {len(complexes)} комплексов")
    
    def add_children(self, parent_index: QModelIndex, children_data: List[Any], child_type: NodeType):
        """
        Добавить дочерние узлы к родительскому
        
        Args:
            parent_index: индекс родительского узла
            children_data: список данных для дочерних узлов
            child_type: тип дочерних узлов
        """
        parent_node = self._get_node(parent_index)
        if parent_node is None or parent_node == self._root_node:
            print(f"❌ TreeModel: попытка добавить детей к несуществующему родителю")
            return
        
        # Начинаем вставку
        first_row = parent_node.child_count()
        last_row = first_row + len(children_data) - 1
        
        self.beginInsertRows(parent_index, first_row, last_row)
        
        # Создаём и добавляем дочерние узлы
        for data in children_data:
            child_node = TreeNode(data, child_type, parent_node)
            parent_node.append_child(child_node)
            
            # Сохраняем в индекс
            key = self._make_key(child_type, data.id)
            self._node_index[key] = child_node
        
        # Помечаем, что дети загружены
        parent_node.loaded = True
        parent_node.loading = False
        
        self.endInsertRows()
        
        print(f"✅ TreeModel: добавлено {len(children_data)} {child_type.value} к {parent_node.node_type.value} #{parent_node.get_id()}")
    
    def clear_children(self, parent_index: QModelIndex):
        """
        Очистить дочерние узлы родителя
        
        Args:
            parent_index: индекс родительского узла
        """
        parent_node = self._get_node(parent_index)
        if parent_node is None or parent_node == self._root_node:
            return
        
        if parent_node.child_count() == 0:
            return
        
        self.beginRemoveRows(parent_index, 0, parent_node.child_count() - 1)
        
        # Удаляем из индекса
        for child in parent_node.children:
            key = self._make_key(child.node_type, child.get_id())
            self._node_index.pop(key, None)
        
        parent_node.remove_children()
        self.endRemoveRows()
        
        print(f"🔄 TreeModel: очищены дети {parent_node.node_type.value} #{parent_node.get_id()}")
    
    def node_loading(self, node_index: QModelIndex):
        """
        Отметить узел как загружающийся
        Вызывается перед началом загрузки данных
        """
        node = self._get_node(node_index)
        if node and not node.loading:
            node.loading = True
            # Обновляем отображение (покажет курсив или индикатор)
            self.dataChanged.emit(node_index, node_index, [Qt.FontRole])
            self.data_loading.emit(node.node_type, node.get_id())
    
    def node_loaded(self, node_index: QModelIndex):
        """
        Отметить узел как загруженный
        Вызывается после успешной загрузки
        """
        node = self._get_node(node_index)
        if node:
            node.loading = False
            self.dataChanged.emit(node_index, node_index, [Qt.FontRole])
            self.data_loaded.emit(node.node_type, node.get_id())
    
    def node_error(self, node_index: QModelIndex, error_msg: str):
        """
        Отметить ошибку загрузки узла
        """
        node = self._get_node(node_index)
        if node:
            node.loading = False
            self.dataChanged.emit(node_index, node_index, [Qt.FontRole])
            self.data_error.emit(node.node_type, node.get_id(), error_msg)
    
    def get_node_by_id(self, node_type: NodeType, node_id: int) -> Optional[TreeNode]:
        """
        Получить узел по типу и ID
        """
        key = self._make_key(node_type, node_id)
        return self._node_index.get(key)
    
    def get_index_by_id(self, node_type: NodeType, node_id: int) -> QModelIndex:
        """
        Получить индекс по типу и ID
        """
        node = self.get_node_by_id(node_type, node_id)
        if node:
            return self._index_of_node(node)
        return QModelIndex()
    
    def get_all_expanded_nodes(self) -> List[tuple]:
        """
        Получить список всех раскрытых узлов (для обновления)
        Должен вызываться из TreeView, который отслеживает состояние
        """
        # Этот метод будет заполнен в TreeView, так как только View знает,
        # какие узлы раскрыты
        return []
    
    def reset(self):
        """Полный сброс модели"""
        self.beginResetModel()
        self._root_node.children.clear()
        self._node_index.clear()
        self.endResetModel()
        print("🔄 TreeModel: полный сброс")