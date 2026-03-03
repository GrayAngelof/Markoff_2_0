# client/src/ui/tree_view.py
"""
Компонент дерева объектов с поддержкой ленивой загрузки и кэширования
Отображает иерархию: Комплексы → Корпуса → Этажи → Помещения
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QLabel,
    QProgressBar, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex, QPoint
from PySide6.QtGui import QAction
from typing import Optional, List, Dict, Any

from src.core.api_client import ApiClient
from src.core.cache import DataCache
from src.ui.tree_model import TreeModel, NodeType
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class TreeView(QWidget):
    """
    Виджет дерева объектов с ленивой загрузкой
    
    Сигналы:
        item_selected: испускается при выборе элемента в дереве
        data_loading: начало загрузки данных для узла
        data_loaded: завершение загрузки
        data_error: ошибка загрузки
    """
    
    # Сигналы
    item_selected = Signal(str, int)  # type, id
    data_loading = Signal(str, int)   # тип узла, id
    data_loaded = Signal(str, int)    # тип узла, id
    data_error = Signal(str, int, str) # тип узла, id, сообщение
    
    def __init__(self, parent=None):
        """Инициализация виджета дерева"""
        super().__init__(parent)
        
        # Создаём клиент API и кэш
        self.api_client = ApiClient()
        self.cache = DataCache()
        
        # Словарь для отслеживания раскрытых узлов
        self._expanded_nodes: Dict[str, bool] = {}
        
        # Настройка UI
        self._setup_ui()
        
        # Подключаем сигналы модели
        self._connect_model_signals()
        
        # Загружаем комплексы
        self.load_complexes()
        
        print("✅ TreeView: инициализирован")
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок с индикатором загрузки
        self._setup_header()
        
        # Создаём модель дерева и передаём ей кэш
        self.model = TreeModel()
        self.model.set_cache(self.cache)
        
        # Создаём само дерево
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setExpandsOnDoubleClick(True)
        
        # Устанавливаем модель
        self.tree_view.setModel(self.model)
        
        # Подключаем сигналы дерева
        selection_model = self.tree_view.selectionModel()
        selection_model.selectionChanged.connect(self._on_selection_changed)
        self.tree_view.expanded.connect(self._on_node_expanded)
        self.tree_view.collapsed.connect(self._on_node_collapsed)
        
        # Включаем контекстное меню
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # Стили для дерева
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: white;
                border: none;
                outline: none;
            }
            QTreeView::item {
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeView::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QTreeView::item:hover {
                background-color: #f5f5f5;
            }
            QTreeView::item:selected:!active {
                background-color: #f0f0f0;
            }
        """)
        
        layout.addWidget(self.tree_view)
    
    def _setup_header(self):
        """Создание заголовка с индикатором загрузки"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        self.title_label = QLabel("Объекты")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #c0c0c0;
            }
        """)
        
        # Индикатор загрузки (прогресс-бар)
        self.loading_bar = QProgressBar()
        self.loading_bar.setMaximum(0)
        self.loading_bar.setMinimum(0)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        self.loading_bar.hide()
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.loading_bar)
        
        # Находим основной layout и добавляем заголовок в начало
        if self.layout():
            self.layout().addLayout(header_layout)
    
    def _connect_model_signals(self):
        """Подключение сигналов модели"""
        self.model.data_loading.connect(self._on_model_data_loading)
        self.model.data_loaded.connect(self._on_model_data_loaded)
        self.model.data_error.connect(self._on_model_data_error)
    
    # ===== Загрузка данных =====
    
    def load_complexes(self):
        """Загрузка комплексов (корневые узлы)"""
        self.show_loading(True)
        
        try:
            # Проверяем кэш
            cached = self.cache.get("complexes:all")
            if cached:
                print("📦 TreeView: комплексы загружены из кэша")
                complexes = cached
            else:
                # Загружаем с сервера
                complexes = self.api_client.get_complexes()
                # Сохраняем в кэш
                self.cache.set("complexes:all", complexes)
                print("🌐 TreeView: комплексы загружены с сервера")
            
            # Обновляем модель
            self.model.set_complexes(complexes)
            
            # Обновляем заголовок
            self.title_label.setText(f"Объекты ({len(complexes)})")
            
        except Exception as e:
            self._show_error("Ошибка загрузки комплексов", str(e))
            
        finally:
            self.show_loading(False)
    
    def _load_children(self, parent_index: QModelIndex):
        """
        Загрузка дочерних элементов для узла
        
        Args:
            parent_index: индекс родительского узла
        """
        node = self.model._get_node(parent_index)
        if not node or node.loaded or node.loading:
            return
        
        # Отмечаем начало загрузки
        self.model.node_loading(parent_index)
        
        # Определяем, что и как загружать
        node_type = node.node_type
        node_id = node.get_id()
        
        # Формируем ключ для кэша
        if node_type == NodeType.COMPLEX:
            cache_key = f"complex:{node_id}:buildings"
            load_func = self.api_client.get_buildings
            child_type = NodeType.BUILDING
        elif node_type == NodeType.BUILDING:
            cache_key = f"building:{node_id}:floors"
            load_func = self.api_client.get_floors
            child_type = NodeType.FLOOR
        elif node_type == NodeType.FLOOR:
            cache_key = f"floor:{node_id}:rooms"
            load_func = self.api_client.get_rooms
            child_type = NodeType.ROOM
        else:
            self.model.node_loaded(parent_index)
            return
        
        try:
            # Проверяем кэш
            children = self.cache.get(cache_key)
            
            if children is not None:
                print(f"📦 TreeView: {child_type.value} загружены из кэша для {node_type.value} #{node_id}")
            else:
                # Загружаем с сервера
                print(f"🌐 TreeView: загрузка {child_type.value} для {node_type.value} #{node_id}")
                children = load_func(node_id)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
            
            # Добавляем в модель
            if children:
                self.model.add_children(parent_index, children, child_type)
            
            self.model.node_loaded(parent_index)
            
        except Exception as e:
            print(f"❌ TreeView: ошибка загрузки {child_type.value}: {e}")
            self.model.node_error(parent_index, str(e))
            self._show_error(
                f"Ошибка загрузки {child_type.value}",
                f"Не удалось загрузить данные: {str(e)}"
            )
    
    # ===== Обработчики сигналов =====
    
    def _on_node_expanded(self, index: QModelIndex):
        """
        Обработчик раскрытия узла
        Реализует ленивую загрузку
        """
        node = self.model._get_node(index)
        if not node:
            return
        
        # Сохраняем состояние раскрытого узла
        key = f"{node.node_type.value}:{node.get_id()}"
        self._expanded_nodes[key] = True
        # Убедимся, что метод mark_expanded существует и вызывается с правильными аргументами
        if hasattr(self.cache, 'mark_expanded'):
            self.cache.mark_expanded(node.node_type.value, node.get_id())
        
        # Если дети ещё не загружены - загружаем
        if not node.loaded and not node.loading:
            print(f"🔍 TreeView: раскрыт узел {node.node_type.value} #{node.get_id()}, загружаем детей")
            self._load_children(index)
    
    def _on_node_collapsed(self, index: QModelIndex):
        """
        Обработчик сворачивания узла
        """
        node = self.model._get_node(index)
        if node:
            key = f"{node.node_type.value}:{node.get_id()}"
            self._expanded_nodes.pop(key, None)
            if hasattr(self.cache, 'mark_collapsed'):
                self.cache.mark_collapsed(node.node_type.value, node.get_id())
            print(f"📂 TreeView: свёрнут узел {node.node_type.value} #{node.get_id()}")
    
    def _on_selection_changed(self, selected, deselected):
        """
        Обработчик изменения выбора в дереве
        """
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            node = self.model._get_node(index)
            if node:
                item_type = node.node_type.value
                item_id = node.get_id()
                print(f"🔹 TreeView: выбран {item_type} #{item_id}")
                self.item_selected.emit(item_type, item_id)
    
    def _on_model_data_loading(self, node_type: NodeType, node_id: int):
        """Обработчик начала загрузки данных в модели"""
        self.data_loading.emit(node_type.value, node_id)
    
    def _on_model_data_loaded(self, node_type: NodeType, node_id: int):
        """Обработчик завершения загрузки данных"""
        self.data_loaded.emit(node_type.value, node_id)
    
    def _on_model_data_error(self, node_type: NodeType, node_id: int, error: str):
        """Обработчик ошибки загрузки"""
        self.data_error.emit(node_type.value, node_id, error)
    
    # ===== Контекстное меню =====
    
    def _show_context_menu(self, position: QPoint):
        """
        Показать контекстное меню для узла
        """
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        node = self.model._get_node(index)
        if not node:
            return
        
        menu = QMenu()
        
        # Пункт обновления узла
        refresh_action = QAction(f"🔄 Обновить {node.node_type.value}", menu)
        refresh_action.triggered.connect(lambda: self._refresh_node(index))
        menu.addAction(refresh_action)
        
        # Показываем меню
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
    
    def _refresh_node(self, index: QModelIndex):
        """
        Обновить конкретный узел (с инвалидацией кэша)
        """
        node = self.model._get_node(index)
        if not node:
            return
        
        print(f"🔄 TreeView: обновление узла {node.node_type.value} #{node.get_id()}")
        
        # Инвалидируем кэш для этой ветки
        self.cache.invalidate_branch(node.node_type.value, node.get_id())
        
        # Очищаем детей в модели
        self.model.clear_children(index)
        
        # Если узел раскрыт - загружаем заново
        if self.tree_view.isExpanded(index):
            self._load_children(index)
    
    # ===== Публичные методы для обновления =====
    
    def refresh_current(self):
        """
        Обновить текущий выбранный узел
        """
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            self._refresh_node(indexes[0])
        else:
            print("⚠️ TreeView: нет выбранного узла для обновления")
    
    def refresh_visible(self):
        """
        Обновить все раскрытые узлы
        """
        expanded = self.cache.get_expanded_nodes()
        if not expanded:
            print("ℹ️ TreeView: нет раскрытых узлов для обновления")
            return
        
        print(f"🔄 TreeView: обновление {len(expanded)} раскрытых узлов")
        
        # Инвалидируем все раскрытые ветки
        self.cache.invalidate_visible(expanded)
        
        # Для каждого раскрытого узла очищаем детей и перезагружаем
        for node_type, node_id in expanded:
            index = self.model.get_index_by_id(NodeType(node_type), node_id)
            if index.isValid():
                self.model.clear_children(index)
                self._load_children(index)
    
    def full_reset(self):
        """
        Полная перезагрузка (очистка кэша и перезагрузка комплексов)
        """
        print("🔄 TreeView: полная перезагрузка")
        
        # Очищаем кэш
        self.cache.clear()
        
        # Перезагружаем комплексы
        self.load_complexes()
    
    # ===== Вспомогательные методы =====
    
    def show_loading(self, show: bool = True):
        """
        Показать/скрыть индикатор загрузки в заголовке
        """
        if show:
            self.loading_bar.show()
            self.title_label.setText("Объекты (загрузка...)")
        else:
            self.loading_bar.hide()
            # Количество комплексов обновится при загрузке
        
        self.loading_bar.repaint()
    
    def _show_error(self, title: str, message: str):
        """
        Показать сообщение об ошибке
        """
        QMessageBox.warning(self, title, message)
    
    def get_selected_node_info(self) -> Optional[tuple]:
        """
        Получить информацию о выбранном узле
        Returns: (тип, id, данные) или None
        """
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return None
        
        index = indexes[0]
        node = self.model._get_node(index)
        if node:
            return (node.node_type.value, node.get_id(), node.data)
        
        return None
    
    def select_node(self, node_type: str, node_id: int) -> bool:
        """
        Выбрать узел по типу и ID
        """
        index = self.model.get_index_by_id(NodeType(node_type), node_id)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            return True
        return False