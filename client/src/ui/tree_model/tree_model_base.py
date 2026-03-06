# client/src/ui/tree_model/tree_model_base.py
"""
Базовый абстрактный класс для модели дерева.
Наследуется от QAbstractItemModel и определяет базовый интерфейс
для работы с иерархическими данными в Qt.
"""
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QFont, QBrush, QColor
from typing import Optional, Any

from src.ui.tree_model.node_types import NodeType
from src.ui.tree_model.tree_node import TreeNode
from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class TreeModelBase(QAbstractItemModel):
    """
    Абстрактный базовый класс для модели дерева.
    
    Предоставляет:
    - Виртуальный корневой узел (_root_node)
    - Базовые методы QAbstractItemModel (index, parent, rowCount, columnCount)
    - Кастомные роли для данных (ItemIdRole, ItemTypeRole, ItemDataRole)
    - Сигналы для отслеживания загрузки данных
    - Методы для получения узла из индекса
    
    Наследники должны реализовать:
    - data() - получение данных для отображения
    - flags() - флаги элементов
    - hasChildren() - проверка наличия детей
    - Методы управления данными (set_complexes, add_children, update_children)
    """
    
    # ===== Кастомные роли для данных =====
    ItemIdRole = Qt.UserRole + 1
    """Роль для получения ID объекта"""
    
    ItemTypeRole = Qt.UserRole + 2
    """Роль для получения типа объекта (NodeType)"""
    
    ItemDataRole = Qt.UserRole + 3
    """Роль для получения сырых данных (модель)"""
    
    # ===== Сигналы =====
    data_loading = Signal(NodeType, int)
    """Сигнал начала загрузки данных для узла (тип, ID)"""
    
    data_loaded = Signal(NodeType, int)
    """Сигнал завершения загрузки данных для узла (тип, ID)"""
    
    data_error = Signal(NodeType, int, str)
    """Сигнал ошибки загрузки данных (тип, ID, сообщение)"""
    
    # ===== Константы для стилей =====
    _FONT_SIZE_COMPLEX_BOOST = 1
    """Увеличение размера шрифта для комплексов"""
    
    _COLOR_COMPLEX = QColor(0, 70, 130)
    """Цвет текста для комплексов (тёмно-синий)"""
    
    _COLOR_BUILDING = QColor(0, 100, 0)
    """Цвет текста для корпусов (тёмно-зелёный)"""
    
    _COLOR_FLOOR = QColor(100, 100, 100)
    """Цвет текста для этажей (серый)"""
    
    _COLOR_ROOM_OCCUPIED = QColor(200, 50, 50)
    """Цвет текста для занятых помещений (красный)"""
    
    _COLOR_ROOM_FREE = QColor(50, 150, 50)
    """Цвет текста для свободных помещений (зелёный)"""
    
    _COLOR_DEFAULT = QColor(0, 0, 0)
    """Цвет текста по умолчанию (чёрный)"""
    
    def __init__(self, parent=None) -> None:
        """
        Инициализирует базовую модель дерева.
        
        Args:
            parent: Родительский объект
        """
        super().__init__(parent)
        
        # Виртуальный корневой узел (не отображается)
        self._root_node = TreeNode(None, None)
        
        log.debug("TreeModelBase: инициализирован")
    
    # ===== Базовые методы QAbstractItemModel =====
    
    def index(self, row: int, column: int, 
              parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """
        Создаёт индекс для элемента по строке и колонке.
        
        Args:
            row: Строка (позиция среди siblings)
            column: Колонка (всегда 0 для дерева)
            parent: Родительский индекс
            
        Returns:
            QModelIndex: Индекс элемента или пустой индекс
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
        Возвращает родительский индекс для данного индекса.
        
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
        if parent_node is None or parent_node == self._root_node:
            return QModelIndex()
        
        return self.createIndex(parent_node.row(), 0, parent_node)
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Возвращает количество строк (дочерних элементов) для родителя.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            int: Количество дочерних элементов
        """
        parent_node = self._get_node(parent)
        if parent_node is None:
            return 0
        return parent_node.child_count()
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Возвращает количество колонок.
        
        Args:
            parent: Родительский индекс (не используется)
            
        Returns:
            int: Всегда 1 (одна колонка)
        """
        return 1
    
    def headerData(self, section: int, orientation: Qt.Orientation, 
                   role: int = Qt.DisplayRole) -> Optional[str]:
        """
        Возвращает заголовок для колонки.
        
        Args:
            section: Номер колонки
            orientation: Ориентация
            role: Роль данных
            
        Returns:
            Optional[str]: Заголовок или None
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Объекты"
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Возвращает флаги элемента.
        
        Args:
            index: Индекс элемента
            
        Returns:
            Qt.ItemFlags: Флаги элемента
        """
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    # ===== Вспомогательные методы =====
    
    def _get_node(self, index: QModelIndex) -> Optional[TreeNode]:
        """
        Получает узел из индекса.
        
        Args:
            index: Индекс элемента
            
        Returns:
            Optional[TreeNode]: Узел или корневой узел
        """
        if index.isValid():
            node = index.internalPointer()
            if isinstance(node, TreeNode):
                return node
        return self._root_node
    
    def _index_of_node(self, node: TreeNode) -> QModelIndex:
        """
        Создаёт QModelIndex для узла.
        
        Args:
            node: Узел
            
        Returns:
            QModelIndex: Индекс узла или пустой индекс
        """
        if node is None or node == self._root_node:
            return QModelIndex()
        return self.createIndex(node.row(), 0, node)
    
    # ===== Виртуальные методы для переопределения =====
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Возвращает данные для отображения.
        Должен быть переопределён в наследнике.
        
        Args:
            index: Индекс элемента
            role: Роль данных
            
        Returns:
            Any: Данные для указанной роли
        """
        raise NotImplementedError("Метод data должен быть реализован в наследнике")
    
    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        """
        Проверяет, может ли узел иметь дочерние элементы.
        Должен быть переопределён в наследнике.
        
        Args:
            parent: Родительский индекс
            
        Returns:
            bool: True если узел может иметь детей
        """
        raise NotImplementedError("Метод hasChildren должен быть реализован в наследнике")