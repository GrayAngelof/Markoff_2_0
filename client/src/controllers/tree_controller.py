# client/src/controllers/tree_controller.py
"""
TreeController — управление деревом объектов.

Единственное место, где хранится состояние:
- текущий выбранный узел
- список раскрытых узлов

Загрузка детей: только через DataLoader → DataLoaded → проекция → модель
"""

# ===== ИМПОРТЫ =====
from typing import Any, List, Optional, Set

from src.core import EventBus
from src.core.events import (
    ChildrenLoaded,
    DataError,
    DataLoaded,
    NodeCollapsed,
    NodeDetailsLoaded,
    NodeExpanded,
    NodeSelected,
)
from src.core.types import Event, NodeIdentifier, NodeType
from src.controllers.base import BaseController
from src.projections.tree import TreeProjection
from src.services import ContextService, DataLoader
from src.ui.app_window import AppWindow
from src.ui.tree.model import TreeModel
from src.ui.tree.view import TreeView
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
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
    - Раскрытие узла → вызывает DataLoader.load_children()
    - Загруженные данные приходят через DataLoaded
    - DataLoaded → проекция создает TreeNode → модель вставляет
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        bus: EventBus,
        loader: DataLoader,
        context_service: ContextService,
        tree_projection: TreeProjection,
    ) -> None:
        """Инициализирует контроллер дерева."""
        log.info("Инициализация TreeController")
        super().__init__(bus)
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

        self._loader = loader
        self._context_service = context_service
        self._tree_projection = tree_projection
        self._app_window: Optional[AppWindow] = None
        self._tree_model: Optional[TreeModel] = None
        self._tree_view: Optional[TreeView] = None

        # Состояние (единственный источник правды)
        self._current_selection: Optional[NodeIdentifier] = None
        self._expanded_nodes: Set[NodeIdentifier] = set()

        # Подписки
        self._subscribe(NodeSelected, self._on_node_selected)
        self._subscribe(NodeExpanded, self._on_node_expanded)
        self._subscribe(NodeCollapsed, self._on_node_collapsed)
        self._subscribe(DataLoaded, self._on_data_loaded)

        log.system("TreeController инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def set_app_window(self, app_window: AppWindow) -> None:
        """Устанавливает ссылку на фасад окна (для подмены панелей)."""
        self._app_window = app_window
        log.link("Связь с AppWindow установлена")

    def load_root_nodes(self) -> None:
        """Загружает корневые узлы (комплексы) при старте приложения."""
        complexes = self._loader._graph.get_all(NodeType.COMPLEX)

        if complexes:
            log.cache(f"Комплексы уже загружены: {len(complexes)} шт.")
            self._on_complexes_loaded(complexes)
        else:
            log.api("Загрузка комплексов через API")
            complexes = self._loader.load_complexes()
            log.data(f"Загружено комплексов: {len(complexes)}")

    def get_current_selection(self) -> Optional[NodeIdentifier]:
        """Возвращает текущий выбранный узел."""
        return self._current_selection

    def get_expanded_nodes(self) -> Set[NodeIdentifier]:
        """Возвращает копию списка раскрытых узлов."""
        return self._expanded_nodes.copy()

    def is_expanded(self, node: NodeIdentifier) -> bool:
        """Проверяет, раскрыт ли узел."""
        return node in self._expanded_nodes

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_data_loaded(self, event: Event[DataLoaded]) -> None:
        """
        ЕДИНСТВЕННОЕ МЕСТО, где создаются и вставляются узлы.

        Обрабатывает:
        - Загрузку комплексов → создание TreeView
        - Загрузку детей → создание TreeNode и вставка в модель
        """
        data = event.data

        # 1. Обработка комплексов (корневые узлы)
        node_type_str = data.node_type if isinstance(data.node_type, str) else data.node_type.value
        if node_type_str == "complex" and data.node_id == 0:
            log.info("Получены комплексы, создаем TreeView")
            self._on_complexes_loaded(data.payload)
            return

        # 2. Определяем, что это: дети или детали
        is_details = not isinstance(data.payload, list)

        if is_details:
            # Детальные данные обрабатываются в DetailsController
            log.debug(f"_on_data_loaded: детальные данные для {data.node_type}#{data.node_id}, пропускаем")
            return

        # 3. Обработка загрузки детей
        log.info(f"Получены дети для {data.node_type}#{data.node_id}, {data.count} шт")

        if self._tree_model is None:
            log.error("TreeModel не инициализирован")
            return

        parent_type = NodeType(data.node_type) if isinstance(data.node_type, str) else data.node_type
        parent_identifier = NodeIdentifier(parent_type, data.node_id)
        parent_node = self._find_tree_node(parent_identifier)

        if parent_node is None:
            log.error(f"Родительский узел {data.node_type}#{data.node_id} не найден")
            return

        # Защита от дублирования
        if parent_node.child_count() > 0:
            log.info(f"_on_data_loaded: Дети уже загружены, пропускаем")
            return

        child_type = self._get_child_type(parent_type)
        if not child_type:
            log.warning(f"Неизвестный тип детей для {data.node_type}")
            return

        children_nodes = self._tree_projection.build_children_from_payload(
            payload=data.payload,
            child_type=child_type,
            parent_node=parent_node,
        )

        if children_nodes:
            self._tree_model.insert_children(parent_node, children_nodes)
            log.success(f"Вставлено {len(children_nodes)} детей")

            self._bus.emit(ChildrenLoaded(
                parent=parent_identifier,
                children=children_nodes,
            ))
        else:
            log.warning(f"Нет детей для вставки")

    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        """
        Обрабатывает выбор узла.

        Состояние хранится здесь, не дублируется в событиях.
        """
        node = event.data.node
        log.info(f"Выбран {node.node_type.value}#{node.node_id}")

        self._current_selection = node

        try:
            details = self._loader.load_details(node.node_type, node.node_id)
            if details is None:
                log.warning(f"Нет деталей для {node.node_type.value}#{node.node_id}")
                return

            context = self._context_service.get_context(node)
            self._bus.emit(NodeDetailsLoaded(
                node=node,
                payload=details,
                context=context,
            ))
            log.data(f"Детали загружены")

        except Exception as e:
            log.error(f"Ошибка: {e}")
            self._emit_error(node, e)

    def _on_node_expanded(self, event: Event[NodeExpanded]) -> None:
        """
        ТОЛЬКО инициирует загрузку детей.
        Вставка происходит через _on_data_loaded.
        """
        node = event.data.node
        log.info(f"Раскрыт {node.node_type.value}#{node.node_id}")

        self._expanded_nodes.add(node)

        # Проверяем, есть ли уже дети (чтобы не загружать повторно)
        if self._tree_model is not None:
            parent_node = self._find_tree_node(node)
            if parent_node and parent_node.child_count() > 0:
                log.info(f"Дети уже загружены ({parent_node.child_count()} детей)")
                return

        child_type = self._get_child_type(node.node_type)
        if not child_type:
            log.info(f"Узел не может иметь детей")
            return

        # ТОЛЬКО ЗАГРУЗКА — данные придут через DataLoaded
        self._loader.load_children(node.node_type, node.node_id, child_type)

    def _on_node_collapsed(self, event: Event[NodeCollapsed]) -> None:
        """Обрабатывает сворачивание узла."""
        node = event.data.node
        log.info(f"Свернут {node.node_type.value}#{node.node_id}")
        self._expanded_nodes.discard(node)

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _on_complexes_loaded(self, complexes: List[Any]) -> None:
        """Создает TreeView после загрузки комплексов."""
        if self._app_window is None:
            log.error("AppWindow не установлен")
            return

        root_nodes = self._tree_projection.get_root_nodes()
        tree_view = self._app_window.get_tree_view()

        self._tree_model = TreeModel(root_nodes)
        tree_view.setModel(self._tree_model)
        tree_view.set_event_bus(self._bus)

        log.system(f"TreeView обновлен с {len(root_nodes)} корневыми узлами")

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
        return self._tree_model.get_node_by_id(identifier.node_type, identifier.node_id)