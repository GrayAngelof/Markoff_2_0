# client/src/ui/tree_view.py
"""
Компонент дерева объектов с поддержкой ленивой загрузки и кэширования
Отображает иерархию: Комплексы → Корпуса → Этажи → Помещения
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QLabel,
    QProgressBar, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex, QPoint, QTimer, QItemSelection
from PySide6.QtGui import QAction
from typing import Optional, List, Dict, Any, Tuple
from functools import partial

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
    item_selected = Signal(str, int, object, dict)  # type, id, data, context
    data_loading = Signal(str, int)                  # тип узла, id
    data_loaded = Signal(str, int)                   # тип узла, id
    data_error = Signal(str, int, str)                # тип узла, id, сообщение
    
    def __init__(self, parent=None):
        """Инициализация виджета дерева"""
        super().__init__(parent)
        
        # Создаём клиент API и кэш
        self.api_client = ApiClient()
        self.cache = DataCache()
        
        # Флаг для блокировки обработки выделения во время загрузки
        self._loading_details = False
        
        # Настройка UI
        self._setup_ui()
        
        # Подключаем сигналы модели
        self._connect_model_signals()
        
        # Загружаем комплексы
        self.load_complexes()
        
        print("✅ TreeView: инициализирован")
    
    # ===== Инициализация UI =====
    
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
        
        # Индикатор загрузки
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
        
        if self.layout():
            self.layout().addLayout(header_layout)
    
    def _connect_model_signals(self):
        """Подключение сигналов модели"""
        self.model.data_loading.connect(self._on_model_data_loading)
        self.model.data_loaded.connect(self._on_model_data_loaded)
        self.model.data_error.connect(self._on_model_data_error)
    
    # ===== Вспомогательные методы =====
    
    def _get_context_for_node(self, node) -> dict:
        """
        Собрать контекст из родительских узлов
        
        Returns:
            dict: словарь с именами родительских узлов
                  {'complex_name': str, 'building_name': str, 'floor_num': int}
        """
        context = {
            'complex_name': None,
            'building_name': None,
            'floor_num': None
        }
        
        current = node
        while current:
            if current.node_type == NodeType.COMPLEX and current.data:
                context['complex_name'] = current.data.name
            elif current.node_type == NodeType.BUILDING and current.data:
                context['building_name'] = current.data.name
            elif current.node_type == NodeType.FLOOR and current.data:
                context['floor_num'] = current.data.number
            current = current.parent
        
        return context
    
    @Slot()
    def _reset_loading_flag(self):
        """Сбросить флаг загрузки деталей"""
        self._loading_details = False
    
    @Slot(str, int, object, dict)
    def _emit_updated_selection(self, item_type: str, item_id: int, item_data, context: dict):
        """Отправить обновлённые данные в DetailsPanel"""
        self.item_selected.emit(item_type, item_id, item_data, context)
    
    # ===== Загрузка данных =====
    
    @Slot()
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
    
    @Slot(QModelIndex)
    def _load_children(self, parent_index: QModelIndex):
        """
        Загрузка дочерних элементов для узла (первоначальная загрузка)
        """
        node = self.model._get_node(parent_index)
        if not node:
            return
        
        # Проверяем через модель, есть ли у узла дети
        has_children = self.model.hasChildren(parent_index)
        
        # Если уже загружено или не может иметь детей - выходим
        if node.loaded or not has_children:
            return

        # Определяем, что и как загружать
        node_type = node.node_type
        node_id = node.get_id()
        
        # Формируем ключ для кэша и функцию загрузки
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
            return
        
        # Сигнализируем о начале загрузки
        self.data_loading.emit(node_type.value, node_id)
        
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
            
            self.data_loaded.emit(node_type.value, node_id)
            
        except Exception as e:
            print(f"❌ TreeView: ошибка загрузки {child_type.value}: {e}")
            self.data_error.emit(node_type.value, node_id, str(e))
    
    # ===== Методы обновления данных =====
    
    @Slot()
    def refresh_current(self):
        """Обновить текущий выбранный узел"""
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            print("⚠️ TreeView: нет выбранного узла для обновления")
            return
        
        index = indexes[0]
        node = self.model._get_node(index)
        if not node:
            return
        
        node_type = node.node_type.value
        node_id = node.get_id()
        context = self._get_context_for_node(node)
        
        print(f"🔄 TreeView: обновление узла {node_type} #{node_id}")
        
        # Определяем параметры для обновления
        if node.node_type == NodeType.COMPLEX:
            cache_key = f"complex:{node_id}:buildings"
            load_func = self.api_client.get_buildings
            child_type = NodeType.BUILDING
        elif node.node_type == NodeType.BUILDING:
            cache_key = f"building:{node_id}:floors"
            load_func = self.api_client.get_floors
            child_type = NodeType.FLOOR
        elif node.node_type == NodeType.FLOOR:
            cache_key = f"floor:{node_id}:rooms"
            load_func = self.api_client.get_rooms
            child_type = NodeType.ROOM
        else:
            return
        
        # Блокируем сигналы на время обновления
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            # Удаляем кэш детей
            self.cache.remove(cache_key)
            
            # Загружаем свежие данные
            children = load_func(node_id)
            
            if children is not None:
                # Обновляем детей в модели
                self.model.update_children(index, children, child_type)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
            
            print(f"✅ TreeView: узел {node_type} #{node_id} обновлён")
            
        except Exception as e:
            print(f"❌ TreeView: ошибка обновления {node_type} #{node_id}: {e}")
            self.data_error.emit(node_type, node_id, str(e))
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение
        QTimer.singleShot(100, lambda: self._restore_selection_safe(node_type, node_id, context))
    
    @Slot()
    def refresh_visible(self):
        """Обновить все раскрытые узлы"""
        expanded = self.cache.get_expanded_nodes()
        if not expanded:
            print("ℹ️ TreeView: нет раскрытых узлов для обновления")
            return
        
        # Запоминаем текущий выбранный узел
        current_selection = self.get_selected_node_info()
        selected_type = None
        selected_id = None
        selected_context = None
        
        if current_selection:
            selected_type, selected_id, selected_data = current_selection
            # Находим узел чтобы получить контекст
            index = self.model.get_index_by_id(NodeType(selected_type), selected_id)
            if index.isValid():
                node = self.model._get_node(index)
                if node:
                    selected_context = self._get_context_for_node(node)
            print(f"🔍 Будет восстановлен узел: {selected_type} #{selected_id}")
        
        print(f"🔄 TreeView: обновление {len(expanded)} раскрытых узлов")
        
        # Блокируем сигналы на время обновления
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            for node_type, node_id in expanded:
                index = self.model.get_index_by_id(NodeType(node_type), node_id)
                if index.isValid():
                    self._refresh_node(index, use_cache=False)
            
            print(f"✅ TreeView: обновление {len(expanded)} узлов завершено")
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение, если оно было
        if selected_type and selected_id:
            # Даём время на завершение обновления
            QTimer.singleShot(100, 
                lambda: self._restore_selection_safe(selected_type, selected_id, selected_context))
    
    @Slot()
    def full_reset(self):
        """Полная перезагрузка (очистка кэша и перезагрузка комплексов)"""
        print("🔄 TreeView: полная перезагрузка")
        
        # Очищаем кэш
        self.cache.clear()
        
        # Перезагружаем комплексы
        self.load_complexes()
    
    @Slot(QModelIndex, bool)
    def _refresh_node(self, index: QModelIndex, use_cache: bool = False):
        """Обновить конкретный узел"""
        node = self.model._get_node(index)
        if not node:
            return
        
        node_type = node.node_type.value
        node_id = node.get_id()
        
        # Определяем параметры для обновления
        if node.node_type == NodeType.COMPLEX:
            cache_key = f"complex:{node_id}:buildings"
            load_func = self.api_client.get_buildings
            child_type = NodeType.BUILDING
        elif node.node_type == NodeType.BUILDING:
            cache_key = f"building:{node_id}:floors"
            load_func = self.api_client.get_floors
            child_type = NodeType.FLOOR
        elif node.node_type == NodeType.FLOOR:
            cache_key = f"floor:{node_id}:rooms"
            load_func = self.api_client.get_rooms
            child_type = NodeType.ROOM
        else:
            return
        
        # Если не используем кэш - удаляем его
        if not use_cache:
            self.cache.remove(cache_key)
        
        try:
            # Загружаем данные
            if use_cache:
                children = self.cache.get(cache_key)
                if children is None:
                    children = load_func(node_id)
                    self.cache.set(cache_key, children)
            else:
                children = load_func(node_id)
                self.cache.set(cache_key, children)
            
            # Обновляем детей в модели
            if children is not None:
                self.model.update_children(index, children, child_type)
            
        except Exception as e:
            print(f"❌ TreeView: ошибка обновления {node_type} #{node_id}: {e}")
            self.data_error.emit(node_type, node_id, str(e))
    
    @Slot(str, int, dict)
    def _restore_selection_safe(self, node_type: str, node_id: int, context: dict = None):
        """Безопасное восстановление выделения с поиском узла по ID"""
        try:
            index = self.model.get_index_by_id(NodeType(node_type), node_id)
            
            if index.isValid():
                node = self.model._get_node(index)
                if node and node.get_id() == node_id:
                    self.tree_view.setCurrentIndex(index)
                    # Передаём данные в сигнале с контекстом
                    if context is None:
                        context = self._get_context_for_node(node)
                    self.item_selected.emit(node_type, node_id, node.data, context)
                    print(f"🔹 TreeView: восстановлено выделение {node_type} #{node_id}")
                    return
            
            print(f"⚠️ TreeView: узел {node_type} #{node_id} не найден, ищем родителя")
            self._restore_parent_selection(node_type, node_id)
            
        except Exception as e:
            print(f"❌ Ошибка при восстановлении выделения: {e}")
            import traceback
            traceback.print_exc()
    
    @Slot(str, int)
    def _restore_parent_selection(self, node_type: str, node_id: int):
        """Восстановить родительский узел, если не удалось найти целевой"""
        try:
            parent_type = None
            if node_type == NodeType.ROOM.value:
                parent_type = NodeType.FLOOR
            elif node_type == NodeType.FLOOR.value:
                parent_type = NodeType.BUILDING
            elif node_type == NodeType.BUILDING.value:
                parent_type = NodeType.COMPLEX
            else:
                return
            
            if parent_type == NodeType.COMPLEX:
                index = self.model.index(0, 0)
                if index.isValid():
                    self.tree_view.setCurrentIndex(index)
                    node = self.model._get_node(index)
                    if node:
                        context = self._get_context_for_node(node)
                        self.item_selected.emit(NodeType.COMPLEX.value, node.get_id(), node.data, context)
                        print(f"🔹 TreeView: выбран комплекс #{node.get_id()} как запасной вариант")
                        
        except Exception as e:
            print(f"❌ Ошибка при восстановлении родителя: {e}")
    
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
    
    @Slot(str, int, QModelIndex, dict)
    def _load_details_if_needed(self, item_type: str, item_id: int, index: QModelIndex, context: dict):
        """Загрузить детальные данные, если их нет в текущем объекте"""
        # Устанавливаем флаг загрузки
        self._loading_details = True
        
        try:
            node = self.model._get_node(index)
            if not node:
                return
            
            item_data = node.data
            
            if item_type == 'complex' and isinstance(item_data, Complex):
                if item_data.address is None and item_data.description is None:
                    print(f"🔍 Загружаем детали комплекса #{item_id}")
                    detailed = self.api_client.get_complex_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        # Отправляем обновлённые данные с тем же контекстом
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
            
            elif item_type == 'building' and isinstance(item_data, Building):
                if item_data.description is None and item_data.address is None:
                    print(f"🔍 Загружаем детали корпуса #{item_id}")
                    detailed = self.api_client.get_building_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
            
            elif item_type == 'floor' and isinstance(item_data, Floor):
                if item_data.description is None:
                    print(f"🔍 Загружаем детали этажа #{item_id}")
                    detailed = self.api_client.get_floor_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
            
            elif item_type == 'room' and isinstance(item_data, Room):
                if item_data.area is None or item_data.status_code is None:
                    print(f"🔍 Загружаем детали помещения #{item_id}")
                    detailed = self.api_client.get_room_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
        finally:
            # Сбрасываем флаг через небольшую задержку
            QTimer.singleShot(100, self._reset_loading_flag)
    
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
    
    # ===== Контекстное меню =====
    
    @Slot(QPoint)
    def _show_context_menu(self, position: QPoint):
        """Показать контекстное меню для узла"""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        node = self.model._get_node(index)
        if not node:
            return
        
        menu = QMenu()
        
        # Определяем тип узла для текста меню
        node_type_display = {
            NodeType.COMPLEX: "комплекс",
            NodeType.BUILDING: "корпус",
            NodeType.FLOOR: "этаж",
            NodeType.ROOM: "помещение"
        }.get(node.node_type, "объект")
        
        # Пункт обновления узла
        refresh_action = QAction(f"🔄 Обновить {node_type_display}", menu)
        refresh_action.triggered.connect(partial(self._refresh_node, index, False))
        menu.addAction(refresh_action)
        
        # Показываем меню
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
    
    # ===== Публичные методы =====
    
    @Slot(bool)
    def show_loading(self, show: bool = True):
        """Показать/скрыть индикатор загрузки в заголовке"""
        if show:
            self.loading_bar.show()
            self.title_label.setText("Объекты (загрузка...)")
        else:
            self.loading_bar.hide()
            self.title_label.setText("Объекты")
        
        self.loading_bar.repaint()
    
    def _show_error(self, title: str, message: str):
        """Показать сообщение об ошибке"""
        QMessageBox.warning(self, title, message)
    
    def get_selected_node_info(self) -> Optional[Tuple[str, int, Any]]:
        """Получить информацию о выбранном узле"""
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return None
        
        index = indexes[0]
        node = self.model._get_node(index)
        if node:
            return (node.node_type.value, node.get_id(), node.data)
        
        return None
    
    def select_node(self, node_type: str, node_id: int) -> bool:
        """Выбрать узел по типу и ID"""
        index = self.model.get_index_by_id(NodeType(node_type), node_id)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            return True
        return False