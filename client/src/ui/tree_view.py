# client/src/ui/tree_view.py
"""
Компонент дерева объектов с поддержкой ленивой загрузки и кэширования
Отображает иерархию: Комплексы → Корпуса → Этажи → Помещения
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QLabel,
    QProgressBar, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex, QPoint, QTimer
from PySide6.QtGui import QAction
from typing import Optional, List, Dict, Any, Tuple

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
        Загрузка дочерних элементов для узла (первоначальная загрузка)
        
        Args:
            parent_index: индекс родительского узла
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
    
    def refresh_current(self):
        """
        Обновить текущий выбранный узел, сохраняя его и детей
        """
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            print("⚠️ TreeView: нет выбранного узла для обновления")
            return
        
        index = indexes[0]
        self._refresh_node(index)
    
    def refresh_visible(self):
        """
        Обновить все раскрытые узлы, сохраняя структуру дерева и выделение
        """
        expanded = self.cache.get_expanded_nodes()
        if not expanded:
            print("ℹ️ TreeView: нет раскрытых узлов для обновления")
            return
        
        # Запоминаем текущий выбранный узел
        current_selection = self.get_selected_node_info()
        selected_type = None
        selected_id = None
        if current_selection:
            selected_type, selected_id, _ = current_selection
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
            QTimer.singleShot(100, lambda: self._restore_selection_safe(selected_type, selected_id))
    
    def full_reset(self):
        """
        Полная перезагрузка (очистка кэша и перезагрузка комплексов)
        """
        print("🔄 TreeView: полная перезагрузка")
        
        # Очищаем кэш
        self.cache.clear()
        
        # Перезагружаем комплексы
        self.load_complexes()
    
    def _refresh_node(self, index: QModelIndex, use_cache: bool = False):
        """
        Обновить конкретный узел
        
        Args:
            index: индекс узла для обновления
            use_cache: использовать ли кэш (True) или принудительно с сервера (False)
        """
        node = self.model._get_node(index)
        if not node:
            return
        
        node_type = node.node_type
        node_id = node.get_id()
        
        # Определяем параметры для обновления
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
        
        # Если не используем кэш - удаляем его
        if not use_cache:
            self.cache.remove(cache_key)
        
        try:
            # Загружаем данные (из кэша или с сервера)
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
            print(f"❌ TreeView: ошибка обновления {node_type.value} #{node_id}: {e}")
            self.data_error.emit(node_type.value, node_id, str(e))
    
    def _restore_selection_safe(self, node_type: str, node_id: int):
        """
        Безопасное восстановление выделения с поиском узла по ID
        """
        try:
            # Получаем свежий индекс через модель
            index = self.model.get_index_by_id(NodeType(node_type), node_id)
            
            if index.isValid():
                # Проверяем, что узел действительно существует
                node = self.model._get_node(index)
                if node and node.get_id() == node_id:
                    # Устанавливаем выделение
                    self.tree_view.setCurrentIndex(index)
                    # Испускаем сигнал для обновления правой панели
                    self.item_selected.emit(node_type, node_id)
                    print(f"🔹 TreeView: восстановлено выделение {node_type} #{node_id}")
                    return
            
            # Если не нашли - пробуем найти родителя
            print(f"⚠️ TreeView: узел {node_type} #{node_id} не найден, ищем родителя")
            self._restore_parent_selection(node_type, node_id)
            
        except Exception as e:
            print(f"❌ Ошибка при восстановлении выделения: {e}")
            import traceback
            traceback.print_exc()
    
    def _restore_parent_selection(self, node_type: str, node_id: int):
        """Восстановить родительский узел, если не удалось найти целевой"""
        try:
            # Определяем родительский тип
            parent_type = None
            if node_type == NodeType.ROOM.value:
                parent_type = NodeType.FLOOR
            elif node_type == NodeType.FLOOR.value:
                parent_type = NodeType.BUILDING
            elif node_type == NodeType.BUILDING.value:
                parent_type = NodeType.COMPLEX
            else:
                return
            
            # Ищем первый доступный узел родительского типа
            if parent_type == NodeType.COMPLEX:
                index = self.model.index(0, 0)
                if index.isValid():
                    self.tree_view.setCurrentIndex(index)
                    node = self.model._get_node(index)
                    if node:
                        self.item_selected.emit(NodeType.COMPLEX.value, node.get_id())
                        print(f"🔹 TreeView: выбран комплекс #{node.get_id()} как запасной вариант")
                        
        except Exception as e:
            print(f"❌ Ошибка при восстановлении родителя: {e}")
    
    # ===== Обработчики сигналов =====
    
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
    
    def _on_node_collapsed(self, index: QModelIndex):
        """Обработчик сворачивания узла"""
        node = self.model._get_node(index)
        if node:
            self.cache.mark_collapsed(node.node_type.value, node.get_id())
            print(f"📂 TreeView: свёрнут узел {node.node_type.value} #{node.get_id()}")
    
    def _on_selection_changed(self, selected, deselected):
        """Обработчик изменения выбора в дереве"""
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
        """Показать контекстное меню для узла"""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        node = self.model._get_node(index)
        if not node:
            return
        
        menu = QMenu()
        
        # Пункт обновления узла
        refresh_action = QAction(f"Обновить {node.node_type.value}", menu)
        refresh_action.triggered.connect(lambda: self._refresh_node(index, use_cache=False))
        menu.addAction(refresh_action)
        
        # Показываем меню
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
    
    # ===== Публичные методы =====
    
    def show_loading(self, show: bool = True):
        """Показать/скрыть индикатор загрузки в заголовке"""
        if show:
            self.loading_bar.show()
            self.title_label.setText("Объекты (загрузка...)")
        else:
            self.loading_bar.hide()
        
        self.loading_bar.repaint()
    
    def _show_error(self, title: str, message: str):
        """Показать сообщение об ошибке"""
        QMessageBox.warning(self, title, message)
    
    def get_selected_node_info(self) -> Optional[Tuple[str, int, Any]]:
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
        """Выбрать узел по типу и ID"""
        index = self.model.get_index_by_id(NodeType(node_type), node_id)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            return True
        return False