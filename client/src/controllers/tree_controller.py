# client/src/controllers/tree_controller.py
"""
TreeController — управление деревом объектов.

Единственное место, где хранится состояние:
- текущий выбранный узел
- список раскрытых узлов
"""

from typing import Optional, Set
from core import EventBus
from core.types import Event, NodeIdentifier, NodeType
from core.events import (
    NodeSelected, NodeExpanded, NodeCollapsed,
    NodeDetailsLoaded, ChildrenLoaded,
    CurrentSelectionChanged, ExpandedNodesChanged
)
from services import DataLoader, ContextService
from controllers.base import BaseController
from utils.logger import get_logger

log = get_logger(__name__)


class TreeController(BaseController):
    """
    Контроллер дерева объектов.
    
    Отвечает за:
    - Обработку выбора узла
    - Обработку раскрытия/сворачивания
    - Загрузку деталей и детей
    - Хранение состояния (текущий выбор, раскрытые узлы)
    - Эмиссию событий для UI
    """
    
    def __init__(
        self,
        bus: EventBus,
        loader: DataLoader,
        context_service: ContextService
    ):
        """
        Инициализирует контроллер дерева.
        
        Args:
            bus: Шина событий
            loader: Загрузчик данных
            context_service: Сервис контекста
        """
        super().__init__(bus)
        self._loader = loader
        self._context_service = context_service
        
        # Состояние (единственный источник правды)
        self._current_selection: Optional[NodeIdentifier] = None
        self._expanded_nodes: Set[NodeIdentifier] = set()
        
        # Подписки
        self._subscribe(NodeSelected, self._on_node_selected)
        self._subscribe(NodeExpanded, self._on_node_expanded)
        self._subscribe(NodeCollapsed, self._on_node_collapsed)
        
        log.info("TreeController initialized")
    
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        """
        Обрабатывает выбор узла.
        
        1. Сохраняет текущий выбор
        2. Загружает детали узла
        3. Собирает контекст (имена родителей)
        4. Эмитит событие для UI
        
        Args:
            event: Событие выбора узла
        """
        node = event.data.node
        log.info(f"Node selected: {node.node_type.value}#{node.node_id}")
        
        # 1. Сохраняем состояние
        old_selection = self._current_selection
        self._current_selection = node
        
        # 2. Эмитим изменение выбора
        if old_selection != node:
            self._bus.emit(CurrentSelectionChanged(selection=node))
        
        # 3. Загружаем детали
        try:
            details = self._loader.load_details(node.node_type, node.node_id)
            if details is None:
                log.warning(f"No details for {node.node_type.value}#{node.node_id}")
                return
            
            # 4. Собираем контекст
            context = self._context_service.get_context(node)
            
            # 5. Эмитим событие для UI
            self._bus.emit(NodeDetailsLoaded(
                node=node,
                payload=details,
                context=context
            ))
            
            log.debug(f"Details loaded for {node.node_type.value}#{node.node_id}")
            
        except Exception as e:
            self._emit_error(node, e)
    
    def _on_node_expanded(self, event: Event[NodeExpanded]) -> None:
        """
        Обрабатывает раскрытие узла.
        
        1. Сохраняет в список раскрытых
        2. Загружает детей
        3. Эмитит событие для UI
        
        Args:
            event: Событие раскрытия узла
        """
        node = event.data.node
        log.info(f"Node expanded: {node.node_type.value}#{node.node_id}")
        
        # 1. Сохраняем состояние
        was_expanded = node in self._expanded_nodes
        self._expanded_nodes.add(node)
        
        # 2. Эмитим изменение списка раскрытых
        if not was_expanded:
            self._bus.emit(ExpandedNodesChanged(
                expanded_nodes=self._expanded_nodes.copy()
            ))
        
        # 3. Определяем тип детей
        child_type = self._get_child_type(node.node_type)
        if not child_type:
            log.debug(f"Node {node.node_type.value}#{node.node_id} cannot have children")
            return
        
        # 4. Загружаем детей
        try:
            children = self._loader.load_children(
                node.node_type,
                node.node_id,
                child_type
            )
            
            # 5. Эмитим событие для UI
            self._bus.emit(ChildrenLoaded(
                parent=node,
                children=children
            ))
            
            log.debug(f"Loaded {len(children)} children for {node.node_type.value}#{node.node_id}")
            
        except Exception as e:
            self._emit_error(node, e)
    
    def _on_node_collapsed(self, event: Event[NodeCollapsed]) -> None:
        """
        Обрабатывает сворачивание узла.
        
        1. Удаляет из списка раскрытых
        2. Эмитит изменение
        
        Args:
            event: Событие сворачивания узла
        """
        node = event.data.node
        log.info(f"Node collapsed: {node.node_type.value}#{node.node_id}")
        
        # 1. Обновляем состояние
        was_expanded = node in self._expanded_nodes
        self._expanded_nodes.discard(node)
        
        # 2. Эмитим изменение
        if was_expanded:
            self._bus.emit(ExpandedNodesChanged(
                expanded_nodes=self._expanded_nodes.copy()
            ))
        
        # 3. Эмитим событие о сворачивании (опционально)
        # Можно добавить событие, если нужно
        # self._bus.emit(NodeCollapsedChanged(node=node))
    
    def _get_child_type(self, parent_type: NodeType) -> Optional[NodeType]:
        """
        Определяет тип детей по типу родителя.
        
        Args:
            parent_type: Тип родителя
            
        Returns:
            Optional[NodeType]: Тип детей или None
        """
        mapping = {
            NodeType.COMPLEX: NodeType.BUILDING,
            NodeType.BUILDING: NodeType.FLOOR,
            NodeType.FLOOR: NodeType.ROOM,
        }
        return mapping.get(parent_type)
    
    # ===== Публичные методы =====
    
    def get_current_selection(self) -> Optional[NodeIdentifier]:
        """
        Возвращает текущий выбранный узел.
        
        Returns:
            Optional[NodeIdentifier]: Выбранный узел или None
        """
        return self._current_selection
    
    def get_expanded_nodes(self) -> Set[NodeIdentifier]:
        """
        Возвращает копию списка раскрытых узлов.
        
        Returns:
            Set[NodeIdentifier]: Раскрытые узлы
        """
        return self._expanded_nodes.copy()
    
    def is_expanded(self, node: NodeIdentifier) -> bool:
        """
        Проверяет, раскрыт ли узел.
        
        Args:
            node: Идентификатор узла
            
        Returns:
            bool: True если раскрыт
        """
        return node in self._expanded_nodes