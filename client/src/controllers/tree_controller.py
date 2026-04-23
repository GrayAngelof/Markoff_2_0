# client/src/controllers/tree_controller.py
"""
TreeController — управление деревом объектов.

Единственное место, где хранится состояние:
- список раскрытых узлов

Загрузка детей: только через DataLoader → эмит ChildrenLoaded.
Никакой работы с UI (TreeModel/TreeView/AppWindow) здесь нет.
Выбор узла НЕ отслеживается — это ответственность DetailsController.
"""

# ===== ИМПОРТЫ =====
from typing import List, Optional, Set

from src.core import EventBus
from src.core.events.definitions import (
    ChildrenLoaded,
    CollapseAllRequested,
    DataLoaded,
    DataLoadedKind,
    ExpandedNodesChanged,
    NodeCollapsed,
    NodeExpanded,
)
from src.core.types import NodeIdentifier, NodeType, ROOT_NODE
from .base import BaseController
from src.projections.tree import TreeProjection
from src.services import DataLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class TreeController(BaseController):
    """
    Контроллер дерева объектов.

    Отвечает за:
    - Обработку раскрытия/сворачивания узлов
    - Хранение состояния раскрытых узлов
    - Инициирование загрузки детей через DataLoader
    - Эмиссию событий ChildrenLoaded, ExpandedNodesChanged

    НЕ отвечает за:
    - Выбор узла (это DetailsController)
    - Создание или обновление TreeModel/TreeView
    - Прямую работу с UI
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        bus: EventBus,
        loader: DataLoader,
        tree_projection: TreeProjection,
    ) -> None:
        """Инициализирует контроллер дерева."""
        log.system("TreeController инициализация")
        super().__init__(bus)

        self._loader = loader
        self._tree_projection = tree_projection

        # Состояние (единственный источник правды для раскрытых узлов)
        self._expanded_nodes: Set[NodeIdentifier] = set()

        # Подписки
        self._subscribe(NodeExpanded, self._on_node_expanded)
        self._subscribe(NodeCollapsed, self._on_node_collapsed)
        self._subscribe(DataLoaded, self._on_data_loaded)
        self._subscribe(CollapseAllRequested, self._on_collapse_all_requested)

        log.system("TreeController инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def load_root_nodes(self) -> None:
        """Загружает корневые узлы (комплексы) при старте приложения."""
        complexes = self._loader.load_complexes_tree()
        if complexes:
            log.data(f"Загружено комплексов: {len(complexes)}")
            self._on_complexes_loaded(complexes)
        else:
            log.warning("Не удалось загрузить комплексы")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_collapse_all_requested(self, _event: CollapseAllRequested) -> None:
        """Обрабатывает запрос на сворачивание всех узлов."""
        log.info("Сворачивание всех узлов дерева")
        self._expanded_nodes.clear()
        self._emit_expanded_nodes_changed()

    def _on_data_loaded(self, event: DataLoaded) -> None:
        """
        Обрабатывает загруженные данные (от DataLoader).

        Для детей (kind=CHILDREN) создаёт TreeNode через проекцию
        и эмитит ChildrenLoaded.
        Для деталей (kind=DETAILS) ничего не делает.
        """
        # Комплексы обрабатываются отдельно в _on_complexes_loaded
        if event.node_type == NodeType.COMPLEX and event.node_id == 0:
            return

        # Детальные данные пропускаем
        if event.kind == DataLoadedKind.DETAILS:
            log.debug(f"Детальные данные для {event.node_type.value}#{event.node_id}, пропускаем")
            return

        # Обработка загрузки детей (kind == CHILDREN)
        if event.kind == DataLoadedKind.CHILDREN:
            log.info(f"Получены дети для {event.node_type.value}#{event.node_id}, {event.count} шт")

            child_type = self._get_child_type(event.node_type)
            if not child_type:
                log.warning(f"Неизвестный тип детей для {event.node_type.value}")
                return

            children_nodes = self._tree_projection.build_children_from_payload(
                payload=event.payload,
                child_type=child_type,
            )

            if children_nodes:
                parent_id = NodeIdentifier(event.node_type, event.node_id)
                self._bus.emit(ChildrenLoaded(
                    parent=parent_id,
                    children=children_nodes,
                ))
                log.success(f"Отправлены дети для {parent_id}: {len(children_nodes)} узлов")
            else:
                log.warning("Нет детей для вставки")

    def _on_node_expanded(self, event: NodeExpanded) -> None:
        """
        Инициирует загрузку детей при раскрытии узла.

        В зависимости от типа узла вызывает соответствующий метод DataLoader.
        """
        node = event.node
        log.info(f"Раскрыт {node.node_type.value}#{node.node_id}")

        self._expanded_nodes.add(node)
        self._emit_expanded_nodes_changed()

        # Диспетчеризация по типу родителя
        if node.node_type == NodeType.COMPLEX:
            self._loader.load_buildings_tree(node.node_id)
        elif node.node_type == NodeType.BUILDING:
            self._loader.load_floors_tree(node.node_id)
        elif node.node_type == NodeType.FLOOR:
            self._loader.load_rooms_tree(node.node_id)
        else:
            log.debug(f"Узел {node.node_type.value} не может иметь детей")

    def _on_node_collapsed(self, event: NodeCollapsed) -> None:
        """Обрабатывает сворачивание узла."""
        node = event.node
        log.info(f"Свернут {node.node_type.value}#{node.node_id}")

        if node in self._expanded_nodes:
            self._expanded_nodes.discard(node)
            self._emit_expanded_nodes_changed()

    # ---- ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ЭМИССИИ СОСТОЯНИЯ ----
    def _emit_expanded_nodes_changed(self) -> None:
        """Эмитит событие об изменении списка раскрытых узлов."""
        self._bus.emit(ExpandedNodesChanged(expanded_nodes=self._expanded_nodes.copy()))
        log.debug(f"Эмиттирован ExpandedNodesChanged: {len(self._expanded_nodes)} узлов")

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _on_complexes_loaded(self, complexes: List) -> None:
        """
        Обрабатывает загруженные комплексы: создаёт корневые узлы
        и эмитит ChildrenLoaded с ROOT_NODE.
        """
        root_nodes = self._tree_projection.get_root_nodes()
        log.debug(f"Создано корневых узлов: {len(root_nodes)}")

        self._bus.emit(ChildrenLoaded(
            parent=ROOT_NODE,
            children=root_nodes,
        ))
        log.success("Отправлены корневые узлы (ROOT_NODE)")

    @staticmethod
    def _get_child_type(parent_type: NodeType) -> Optional[NodeType]:
        """Определяет тип детей по типу родителя."""
        mapping = {
            NodeType.COMPLEX: NodeType.BUILDING,
            NodeType.BUILDING: NodeType.FLOOR,
            NodeType.FLOOR: NodeType.ROOM,
        }
        return mapping.get(parent_type)