# client/src/controllers/tree_controller.py
"""
TreeController — управление деревом объектов.

Единственное место, где хранится состояние:
- текущий выбранный узел
- список раскрытых узлов

Загрузка детей: только через DataLoader → DataLoaded → проекция → модель
"""

from typing import Optional, Set, List, Any
from src.core import EventBus
from src.core.types import Event, NodeIdentifier, NodeType
from src.core.events import (
    NodeSelected, NodeExpanded, NodeCollapsed,
    NodeDetailsLoaded, ChildrenLoaded,
    CurrentSelectionChanged, ExpandedNodesChanged,
    DataLoaded, DataError
)
from src.services import DataLoader, ContextService
from src.controllers.base import BaseController
from src.projections.tree import TreeProjection
from src.ui.app_window import AppWindow
from src.ui.tree.view import TreeView
from src.ui.tree.model import TreeModel

from utils.logger import get_logger

log = get_logger(__name__)


class TreeController(BaseController):
    """
    Контроллер дерева объектов.
    
    Отвечает за:
    - Обработку выбора узла
    - Обработку раскрытия/сворачивания
    - Хранение состояния (текущий выбор, раскрытые узлы)
    - Инициирование загрузки (но не вставку!)
    - Создание TreeView и подмену левой панели
    
    Принцип работы:
    - Раскрытие узла → вызывает DataLoader.load_children() (только загрузка)
    - Загруженные данные приходят через DataLoaded
    - DataLoaded → проекция создает TreeNode → модель вставляет
    - Единый поток данных: загрузка → событие → создание → вставка
    """
    
    def __init__(
        self,
        bus: EventBus,
        loader: DataLoader,
        context_service: ContextService,
        tree_projection: TreeProjection
    ):
        super().__init__(bus)
        self._loader = loader
        self._context_service = context_service
        self._tree_projection = tree_projection
        self._app_window: Optional[AppWindow] = None
        self._tree_model: Optional[TreeModel] = None
        self._tree_view: Optional[TreeView] = None
        
        # Состояние (единственный источник правды)
        self._current_selection: Optional[NodeIdentifier] = None
        self._expanded_nodes: Set[NodeIdentifier] = set()
        
        # Сохраняем bound methods как атрибуты (сильные ссылки)
        self._bound_on_node_selected = self._on_node_selected
        self._bound_on_node_expanded = self._on_node_expanded
        self._bound_on_node_collapsed = self._on_node_collapsed
        self._bound_on_data_loaded = self._on_data_loaded
        
        # Подписки
        log.link("Подписка на события дерева")
        self._subscribe(NodeSelected, self._bound_on_node_selected)
        self._subscribe(NodeExpanded, self._bound_on_node_expanded)
        self._subscribe(NodeCollapsed, self._bound_on_node_collapsed)
        self._subscribe(DataLoaded, self._bound_on_data_loaded)
        
        log.system("TreeController инициализирован")
    
    def set_app_window(self, app_window: AppWindow) -> None:
        """Устанавливает ссылку на фасад окна (для подмены панелей)."""
        self._app_window = app_window
        log.debug("AppWindow установлен")
    
    # ===== Загрузка корневых узлов =====
    
    def load_root_nodes(self) -> None:
        """
        Загружает корневые узлы (комплексы) при старте приложения.
        """
        complexes = self._loader._graph.get_all(NodeType.COMPLEX)
        
        if complexes:
            log.cache(f"load_root_nodes: Комплексы уже загружены: {len(complexes)} шт.")
            self._on_complexes_loaded(complexes)
        else:
            log.api("load_root_nodes: Загрузка комплексов через API")
            complexes = self._loader.load_complexes()
            log.data(f"load_root_nodes: Загружено комплексов: {len(complexes)}")
            for c in complexes:
                log.debug(f"load_root_nodes: Комплекс #{c.id}: {c.name} (корпусов: {c.buildings_count})")
    
    def _on_data_loaded(self, event: Event[DataLoaded]) -> None:
        """
        ЕДИНСТВЕННОЕ МЕСТО, где создаются и вставляются узлы.
        
        Обрабатывает:
        - Загрузку комплексов → создание TreeView
        - Загрузку детей → создание TreeNode и вставка в модель
        """
        node_type = event.data.node_type
        node_id = event.data.node_id
        payload = event.data.payload
        
        log.debug(f"_on_data_loaded: {node_type}#{node_id}, count={event.data.count}")
        
        # Корневые узлы (комплексы)
        if node_type == "complex" and node_id == 0:
            log.info("_on_data_loaded: Получены комплексы, создаем TreeView")
            self._on_complexes_loaded(payload)
            return
        
        # Дети узла
        log.info(f"_on_data_loaded: Получены дети для {node_type}#{node_id}")
        
        if self._tree_model is None:
            log.error("_on_data_loaded: TreeModel не инициализирован")
            return
        
        # Находим родительский узел
        parent_identifier = NodeIdentifier(NodeType(node_type), node_id)
        parent_node = self._find_tree_node(parent_identifier)
        
        if parent_node is None:
            log.error(f"_on_data_loaded: Родительский узел {node_type}#{node_id} не найден")
            return
        
        log.debug(f"_on_data_loaded: Родитель {parent_node.type}#{parent_node.id}, детей сейчас: {parent_node.child_count()}")
        
        # Если дети уже есть — выходим (защита от дублирования)
        if parent_node.child_count() > 0:
            log.debug(f"_on_data_loaded: Дети уже загружены, пропускаем")
            return
        
        # Определяем тип детей
        child_type = self._get_child_type(NodeType(node_type))
        if not child_type:
            log.warning(f"_on_data_loaded: Неизвестный тип детей для {node_type}")
            return
        
        # Проекция создает TreeNode
        log.debug(f"_on_data_loaded: Вызов проекции для создания узлов типа {child_type.value}")
        children_nodes = self._tree_projection.build_children_from_payload(
            payload=payload,
            child_type=child_type,
            parent_node=parent_node
        )
        
        # Модель вставляет узлы
        if children_nodes:
            self._tree_model.insert_children(parent_node, children_nodes)
            log.success(f"_on_data_loaded: Вставлено {len(children_nodes)} детей")
        else:
            log.debug(f"_on_data_loaded: Нет детей для вставки")
            parent_node._has_children = False
    
    def _on_complexes_loaded(self, complexes: List[Any]) -> None:
        """
        Создает TreeView после загрузки комплексов.
        """
        if self._app_window is None:
            log.error("_on_complexes_loaded: AppWindow не установлен")
            return
        
        for c in complexes:
            log.debug(f"_on_complexes_loaded: Комплекс #{c.id}: {c.name} (корпусов: {c.buildings_count})")
        
        # Строим корневые узлы через проекцию
        root_nodes = self._tree_projection.get_root_nodes()
        log.debug(f"_on_complexes_loaded: Построено корневых узлов: {len(root_nodes)}")
        
        # Получаем TreeView из AppWindow
        tree_view = self._app_window.get_tree_view()
        
        # Создаем TreeModel и устанавливаем
        self._tree_model = TreeModel(root_nodes)
        tree_view.setModel(self._tree_model)
        tree_view.set_event_bus(self._bus)
        
        log.system(f"_on_complexes_loaded: TreeView обновлен с {len(root_nodes)} корневыми узлами")
    
    # ===== Обработка событий от UI =====
    
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        """Обрабатывает выбор узла."""
        node = event.data.node
        log.info(f"_on_node_selected: Выбран {node.node_type.value}#{node.node_id}")
        
        old_selection = self._current_selection
        self._current_selection = node
        
        if old_selection != node:
            self._bus.emit(CurrentSelectionChanged(selection=node))
        
        try:
            details = self._loader.load_details(node.node_type, node.node_id)
            if details is None:
                log.warning(f"_on_node_selected: Нет деталей для {node.node_type.value}#{node.node_id}")
                return
            
            context = self._context_service.get_context(node)
            self._bus.emit(NodeDetailsLoaded(
                node=node,
                payload=details,
                context=context
            ))
            log.data(f"_on_node_selected: Детали загружены")
            
        except Exception as e:
            log.error(f"_on_node_selected: Ошибка: {e}")
            self._emit_error(node, e)
    
    def _on_node_expanded(self, event: Event[NodeExpanded]) -> None:
        """
        ТОЛЬКО инициирует загрузку детей.
        Вставка происходит через _on_data_loaded.
        """
        node = event.data.node
        log.info(f"_on_node_expanded: Раскрыт {node.node_type.value}#{node.node_id}")
        
        # Сохраняем состояние
        was_expanded = node in self._expanded_nodes
        self._expanded_nodes.add(node)
        
        if not was_expanded:
            self._bus.emit(ExpandedNodesChanged(
                expanded_nodes=self._expanded_nodes.copy()
            ))
        
        # Проверяем, есть ли уже дети (чтобы не загружать повторно)
        if self._tree_model is not None:
            parent_node = self._find_tree_node(node)
            if parent_node and parent_node.child_count() > 0:
                log.debug(f"_on_node_expanded: Дети уже загружены (уже {parent_node.child_count()} детей)")
                return
        
        # Определяем тип детей
        child_type = self._get_child_type(node.node_type)
        if not child_type:
            log.debug(f"_on_node_expanded: Узел не может иметь детей")
            return
        
        # ТОЛЬКО ЗАГРУЗКА — данные придут через DataLoaded
        log.debug(f"_on_node_expanded: Инициируем загрузку детей типа {child_type.value}")
        self._loader.load_children(node.node_type, node.node_id, child_type)
    
    def _on_node_collapsed(self, event: Event[NodeCollapsed]) -> None:
        """Обрабатывает сворачивание узла."""
        node = event.data.node
        log.info(f"_on_node_collapsed: Свернут {node.node_type.value}#{node.node_id}")
        
        was_expanded = node in self._expanded_nodes
        self._expanded_nodes.discard(node)
        
        if was_expanded:
            self._bus.emit(ExpandedNodesChanged(
                expanded_nodes=self._expanded_nodes.copy()
            ))
    
    def _get_child_type(self, parent_type: NodeType) -> Optional[NodeType]:
        """Определяет тип детей по типу родителя."""
        mapping = {
            NodeType.COMPLEX: NodeType.BUILDING,
            NodeType.BUILDING: NodeType.FLOOR,
            NodeType.FLOOR: NodeType.ROOM,
        }
        return mapping.get(parent_type)
    
    def _find_tree_node(self, identifier: NodeIdentifier) -> Optional[Any]:
        """Находит TreeNode в дереве по NodeIdentifier."""
        if self._tree_model is None:
            return None
        
        # Используем кэш модели для быстрого поиска
        return self._tree_model.get_node_by_id(identifier.node_type, identifier.node_id)
    
    # ===== Публичные методы =====
    
    def get_current_selection(self) -> Optional[NodeIdentifier]:
        return self._current_selection
    
    def get_expanded_nodes(self) -> Set[NodeIdentifier]:
        return self._expanded_nodes.copy()
    
    def is_expanded(self, node: NodeIdentifier) -> bool:
        return node in self._expanded_nodes