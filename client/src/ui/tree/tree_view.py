# client/src/ui/tree/tree_view.py
"""
Основной класс дерева объектов
Объединяет все миксины и базовый класс
"""
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex, QPoint, QTimer, QItemSelection
from PySide6.QtWidgets import QWidget

from src.core.api_client import ApiClient
from src.core.cache import DataCache
from src.ui.tree.base_tree import TreeViewBase
from src.ui.tree.tree_selection import TreeSelectionMixin
from src.ui.tree.tree_loader import TreeLoaderMixin
from src.ui.tree.tree_updater import TreeUpdaterMixin
from src.ui.tree.tree_menu import TreeMenuMixin
from src.ui.tree_model import NodeType


class TreeView(
    TreeViewBase,
    TreeSelectionMixin,
    TreeLoaderMixin,
    TreeUpdaterMixin,
    TreeMenuMixin
):
    """
    Виджет дерева объектов с ленивой загрузкой
    
    Сигналы:
        item_selected: испускается при выборе элемента в дереве
        data_loading: начало загрузки данных для узла
        data_loaded: завершение загрузки
        data_error: ошибка загрузки
    """
    
    # Сигналы
    item_selected = Signal(str, int, object, dict)  # type, id, data, context
    data_loading = Signal(str, int)                  # тип узла, id
    data_loaded = Signal(str, int)                   # тип узла, id
    data_error = Signal(str, int, str)                # тип узла, id, сообщение
    
    def __init__(self, parent=None):
        """Инициализация виджета дерева"""
        # Сначала инициализируем базовый класс
        super().__init__(parent)
        
        # Создаём клиент API и кэш
        self.api_client = ApiClient()
        self.cache = DataCache()
        
        # Передаём кэш в модель
        self.set_cache(self.cache)
        
        # Флаг для блокировки обработки выделения во время загрузки
        self._loading_details = False
        
        # Подключаем сигналы дерева
        self._connect_tree_signals()
        
        # Загружаем комплексы
        self.load_complexes()
        
        print("✅ TreeView: инициализирован")
    
    def _connect_tree_signals(self):
        """Подключение сигналов дерева"""
        selection_model = self.tree_view.selectionModel()
        selection_model.selectionChanged.connect(self._on_selection_changed)
        self.tree_view.expanded.connect(self._on_node_expanded)
        self.tree_view.collapsed.connect(self._on_node_collapsed)
        
        # Включаем контекстное меню
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # Подключаем сигналы модели
        self.model.data_loading.connect(self._on_model_data_loading)
        self.model.data_loaded.connect(self._on_model_data_loaded)
        self.model.data_error.connect(self._on_model_data_error)
    
    # ===== Обработчики сигналов =====
    
    @Slot(QModelIndex)
    def _on_node_expanded(self, index: QModelIndex):
        """Обработчик раскрытия узла - ленивая загрузка"""
        node = self.model._get_node(index)
        if not node:
            return
        
        # Сохраняем состояние раскрытого узла
        self.cache.mark_expanded(node.node_type.value, node.get_id())
        
        # Проверяем через модель, есть ли у узла дети
        has_children = self.model.hasChildren(index)
        
        # Если дети ещё не загружены и могут быть - загружаем
        if not node.loaded and has_children:
            print(f"🔍 TreeView: раскрыт узел {node.node_type.value} #{node.get_id()}, загружаем детей")
            self._load_children(index)
    
    @Slot(QModelIndex)
    def _on_node_collapsed(self, index: QModelIndex):
        """Обработчик сворачивания узла"""
        node = self.model._get_node(index)
        if node:
            self.cache.mark_collapsed(node.node_type.value, node.get_id())
            print(f"📂 TreeView: свёрнут узел {node.node_type.value} #{node.get_id()}")
    
    @Slot(QItemSelection, QItemSelection)
    def _on_selection_changed(self, selected, deselected):
        """Обработчик изменения выбора в дереве"""
        # Если идёт загрузка деталей - игнорируем временные выделения
        if self._loading_details:
            return
        
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            node = self.model._get_node(index)
            if node:
                item_type = node.node_type.value
                item_id = node.get_id()
                item_data = node.data
                context = self._get_context_for_node(node)
                
                # Отправляем сигнал с контекстом
                self.item_selected.emit(item_type, item_id, item_data, context)
                
                # Загружаем детали
                self._load_details_if_needed(item_type, item_id, index, context)
                
                print(f"🔹 TreeView: выбран {item_type} #{item_id}")
    
    @Slot(NodeType, int)
    def _on_model_data_loading(self, node_type: NodeType, node_id: int):
        """Обработчик начала загрузки данных в модели"""
        self.data_loading.emit(node_type.value, node_id)
    
    @Slot(NodeType, int)
    def _on_model_data_loaded(self, node_type: NodeType, node_id: int):
        """Обработчик завершения загрузки данных"""
        self.data_loaded.emit(node_type.value, node_id)
    
    @Slot(NodeType, int, str)
    def _on_model_data_error(self, node_type: NodeType, node_id: int, error: str):
        """Обработчик ошибки загрузки"""
        self.data_error.emit(node_type.value, node_id, error)