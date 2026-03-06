# client/src/ui/tree/tree_view.py
"""
Основной класс дерева объектов.
Объединяет все миксины и базовый класс для создания иерархического дерева
с поддержкой ленивой загрузки, кэширования и контекстного меню.
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

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeView(
    TreeViewBase,
    TreeSelectionMixin,
    TreeLoaderMixin,
    TreeUpdaterMixin,
    TreeMenuMixin
):
    """
    Виджет дерева объектов с поддержкой ленивой загрузки и кэширования.
    
    Предоставляет древовидное представление иерархии:
    Комплексы → Корпуса → Этажи → Помещения.
    
    Сигналы:
        item_selected: испускается при выборе элемента в дереве
        data_loading: начало загрузки данных для узла
        data_loaded: завершение загрузки данных
        data_error: ошибка загрузки данных
    """
    
    # ===== Сигналы =====
    item_selected = Signal(str, int, object, dict)
    """Сигнал выбора элемента (тип, идентификатор, данные, контекст)"""
    
    data_loading = Signal(str, int)
    """Сигнал начала загрузки данных для узла (тип, идентификатор)"""
    
    data_loaded = Signal(str, int)
    """Сигнал завершения загрузки данных для узла (тип, идентификатор)"""
    
    data_error = Signal(str, int, str)
    """Сигнал ошибки загрузки данных (тип, идентификатор, сообщение)"""
    
    # ===== Константы =====
    _LOADING_FLAG_RESET_DELAY_MS = 100
    """Задержка сброса флага загрузки в миллисекундах"""
    
    def __init__(self, parent: QWidget = None) -> None:
        """
        Инициализирует виджет дерева.
        
        Args:
            parent: Родительский виджет
        """
        # Инициализация базового класса
        super().__init__(parent)
        
        # Инициализация компонентов
        self._init_components()
        
        # Настройка сигналов
        self._connect_tree_signals()
        
        # Загрузка начальных данных
        self.load_complexes()
        
        log.success("TreeView: инициализирован")
    
    # ===== Приватные методы инициализации =====
    
    def _init_components(self) -> None:
        """
        Инициализация внутренних компонентов.
        Создаёт клиент API, кэш и устанавливает флаги состояния.
        """
        # Клиент для работы с API
        self._api_client = ApiClient()
        
        # Система кэширования данных
        self._cache = DataCache()
        
        # Передаём кэш в модель
        self.set_cache(self._cache)
        
        # Флаг блокировки обработки выделения во время загрузки
        self._is_loading_details = False
    
    def _connect_tree_signals(self) -> None:
        """
        Подключает сигналы дерева и модели к соответствующим обработчикам.
        """
        # Сигналы выделения
        selection_model = self.tree_view.selectionModel()
        selection_model.selectionChanged.connect(self._on_selection_changed)
        
        # Сигналы раскрытия/сворачивания узлов
        self.tree_view.expanded.connect(self._on_node_expanded)
        self.tree_view.collapsed.connect(self._on_node_collapsed)
        
        # Контекстное меню
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # Сигналы модели
        self.model.data_loading.connect(self._on_model_data_loading)
        self.model.data_loaded.connect(self._on_model_data_loaded)
        self.model.data_error.connect(self._on_model_data_error)
    
    # ===== Геттеры =====
    
    @property
    def api_client(self) -> ApiClient:
        """Возвращает клиент API."""
        return self._api_client
    
    @property
    def cache(self) -> DataCache:
        """Возвращает систему кэширования."""
        return self._cache
    
    @property
    def is_loading_details(self) -> bool:
        """
        Возвращает состояние загрузки деталей.
        
        Returns:
            True, если выполняется загрузка детальных данных
        """
        return self._is_loading_details
    
    # ===== Управление флагами =====
    
    def _set_loading_flag(self, value: bool) -> None:
        """
        Устанавливает флаг загрузки деталей.
        
        Args:
            value: Новое значение флага
        """
        self._is_loading_details = value
    
    @Slot()
    def _reset_loading_flag(self) -> None:
        """Сбрасывает флаг загрузки деталей."""
        self._set_loading_flag(False)
        log.debug("TreeView: флаг загрузки сброшен")
    
    # ===== Обработчики сигналов модели =====
    
    @Slot(NodeType, int)
    def _on_model_data_loading(self, node_type: NodeType, node_id: int) -> None:
        """
        Обрабатывает начало загрузки данных в модели.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self.data_loading.emit(node_type.value, node_id)
        log.debug(f"Модель начала загрузку {node_type.value} #{node_id}")
    
    @Slot(NodeType, int)
    def _on_model_data_loaded(self, node_type: NodeType, node_id: int) -> None:
        """
        Обрабатывает завершение загрузки данных в модели.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        self.data_loaded.emit(node_type.value, node_id)
        log.debug(f"Модель завершила загрузку {node_type.value} #{node_id}")
    
    @Slot(NodeType, int, str)
    def _on_model_data_error(self, node_type: NodeType, node_id: int, error: str) -> None:
        """
        Обрабатывает ошибку загрузки данных в модели.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        self.data_error.emit(node_type.value, node_id, error)
        log.error(f"Ошибка загрузки {node_type.value} #{node_id}: {error}")
    
    # ===== Обработчики сигналов дерева =====
    
    @Slot(QModelIndex)
    def _on_node_expanded(self, index: QModelIndex) -> None:
        """
        Обрабатывает раскрытие узла для ленивой загрузки дочерних элементов.
        
        Args:
            index: Индекс раскрываемого узла
        """
        node = self.model._get_node(index)
        if not node:
            log.warning("TreeView: попытка раскрыть несуществующий узел")
            return
        
        # Сохраняем состояние раскрытого узла в кэше
        self._cache.mark_expanded(node.node_type.value, node.get_id())
        
        # Проверяем наличие дочерних элементов
        has_children = self.model.hasChildren(index)
        
        # Загружаем детей, если они ещё не загружены
        if not node.loaded and has_children:
            log.info(f"Раскрыт узел {node.node_type.value} #{node.get_id()}, загрузка детей")
            self._load_children(index)
    
    @Slot(QModelIndex)
    def _on_node_collapsed(self, index: QModelIndex) -> None:
        """
        Обрабатывает сворачивание узла.
        
        Args:
            index: Индекс сворачиваемого узла
        """
        node = self.model._get_node(index)
        if node:
            self._cache.mark_collapsed(node.node_type.value, node.get_id())
            log.debug(f"Свёрнут узел {node.node_type.value} #{node.get_id()}")
    
    @Slot(QItemSelection, QItemSelection)
    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        """
        Обрабатывает изменение выделения в дереве.
        
        Args:
            selected: Новые выбранные индексы
            deselected: Индексы, с которых снято выделение
        """
        # Игнорируем временные выделения во время загрузки
        if self._is_loading_details:
            log.debug("TreeView: выделение проигнорировано (идёт загрузка)")
            return
        
        indexes = selected.indexes()
        if not indexes:
            return
        
        index = indexes[0]
        node = self.model._get_node(index)
        if not node:
            return
        
        # Получаем данные выбранного узла
        item_type = node.node_type.value
        item_id = node.get_id()
        item_data = node.data
        context = self._get_context_for_node(node)
        
        # Отправляем сигнал с контекстом
        self.item_selected.emit(item_type, item_id, item_data, context)
        
        # Загружаем детальные данные при необходимости
        self._load_details_if_needed(item_type, item_id, index, context)
        
        log.info(f"Выбран {item_type} #{item_id}")