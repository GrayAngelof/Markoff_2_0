# client/src/controllers/tree_controller.py
"""
TreeController — управление деревом объектов.

Единственное место, где хранится состояние:
- текущий выбранный узел
- список раскрытых узлов
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
    - Инициирование первой загрузки комплексов
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
        log.info("🌳 TreeController: инициализация")
        
        super().__init__(bus)
        self._loader = loader
        self._context_service = context_service
        self._app_window = None  # будет установлен позже
        
        # Состояние (единственный источник правды)
        self._current_selection: Optional[NodeIdentifier] = None
        self._expanded_nodes: Set[NodeIdentifier] = set()
        
        # Подписки
        log.debug("🔧 Подписка на события...")
        self._subscribe(NodeSelected, self._on_node_selected)
        self._subscribe(NodeExpanded, self._on_node_expanded)
        self._subscribe(NodeCollapsed, self._on_node_collapsed)
        self._subscribe(DataLoaded, self._on_data_loaded)
        
        log.success("✅ TreeController инициализирован")
    
    def set_app_window(self, app_window):
        """Устанавливает ссылку на фасад окна (для подмены панелей)."""
        self._app_window = app_window
        log.debug(f"🔗 TreeController: app_window установлен ({app_window})")
    
    def load_root_nodes(self) -> None:
        """
        Загружает корневые узлы (комплексы) при старте приложения.
        Вызывается после инициализации всех компонентов.
        """
        log.info("🏢 TreeController.load_root_nodes: начальная загрузка комплексов")
        
        # Проверяем, есть ли комплексы в графе
        log.debug("🔍 Проверка кэша: _loader._graph.get_all(NodeType.COMPLEX)")
        try:
            complexes = self._loader._graph.get_all(NodeType.COMPLEX)
            log.debug(f"📊 get_all вернул: {len(complexes)} комплексов")
        except Exception as e:
            log.error(f"❌ Ошибка при проверке кэша: {e}")
            raise
        
        if complexes:
            log.cache(f"💾 Комплексы уже загружены: {len(complexes)} шт.")
            self._on_complexes_loaded(complexes)
        else:
            log.info("📡 Комплексов нет в кэше, загружаем через DataLoader")
            try:
                # Загружаем комплексы
                log.debug("🚀 Вызов _loader.load_complexes()")
                complexes = self._loader.load_complexes()
                log.data(f"📦 Загружено комплексов: {len(complexes)}")
                if complexes:
                    for c in complexes:
                        log.debug(f"   - Комплекс #{c.id}: {c.name} (корпусов: {c.buildings_count})")
                # После загрузки придет DataLoaded, и будет вызван _on_data_loaded
            except Exception as e:
                log.error(f"❌ Ошибка загрузки комплексов: {e}")
                import traceback
                log.error(traceback.format_exc())
    
    def _on_data_loaded(self, event: Event[DataLoaded]) -> None:
        """
        Обрабатывает событие загрузки данных.
        Если загружены комплексы — создает дерево.
        """
        log.debug(f"📢 _on_data_loaded: node_type={event.data.node_type}, node_id={event.data.node_id}, count={event.data.count}")
        
        node_type = event.data.node_type
        node_id = event.data.node_id
        payload = event.data.payload
        
        # Если загружены комплексы (node_type = "complex" и node_id = 0)
        if node_type == "complex" and node_id == 0:
            log.info("🎯 Получены комплексы, создаем TreeView")
            log.debug(f"📦 payload type: {type(payload)}, length: {len(payload) if hasattr(payload, '__len__') else '?'}")
            self._on_complexes_loaded(payload)
        else:
            log.debug(f"⏭️ Событие не для корневых комплексов: {node_type}#{node_id}")
    
    def _on_complexes_loaded(self, complexes: List[Any]) -> None:
        """
        Создает TreeView и подменяет левую панель после загрузки комплексов.
        
        Args:
            complexes: Список загруженных комплексов
        """
        log.info(f"🌳 _on_complexes_loaded: создание TreeView с {len(complexes)} комплексами")
        
        if self._app_window is None:
            log.error("❌ AppWindow не установлен в TreeController")
            return
        
        # Логируем полученные комплексы
        for i, c in enumerate(complexes):
            log.debug(f"   [{i}] Комплекс #{c.id}: {c.name} (корпусов: {c.buildings_count})")
        
        # TODO: здесь будет создание TreeView и передача данных
        log.info("🖼️ TODO: Создание реального TreeView (пока заглушка)")
        
        # Временная заглушка — позже здесь будет реальный TreeView
        # from src.ui.tree.view import TreeView
        # tree_view = TreeView()
        # tree_view.set_complexes(complexes)
        # self._app_window.set_left_panel(tree_view)
        
        # Пока просто эмитим событие, что дерево готово
        log.debug("📢 Эмитим ExpandedNodesChanged")
        self._bus.emit(ExpandedNodesChanged(expanded_nodes=self._expanded_nodes.copy()))
        log.success("✅ Обработка комплексов завершена")
    
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
        log.info(f"🖱️ Node selected: {node.node_type.value}#{node.node_id}")
        
        # 1. Сохраняем состояние
        old_selection = self._current_selection
        self._current_selection = node
        log.debug(f"   Старый выбор: {old_selection.node_type.value if old_selection else 'None'} -> Новый: {node.node_type.value}#{node.node_id}")
        
        # 2. Эмитим изменение выбора
        if old_selection != node:
            log.debug("📢 Эмитим CurrentSelectionChanged")
            self._bus.emit(CurrentSelectionChanged(selection=node))
        
        # 3. Загружаем детали
        try:
            log.debug(f"🚀 Загрузка деталей для {node.node_type.value}#{node.node_id}")
            details = self._loader.load_details(node.node_type, node.node_id)
            if details is None:
                log.warning(f"⚠️ Нет деталей для {node.node_type.value}#{node.node_id}")
                return
            
            log.data(f"📦 Детали загружены: {type(details).__name__}#{details.id if hasattr(details, 'id') else '?'}")
            
            # 4. Собираем контекст
            log.debug(f"🔍 Сбор контекста для {node.node_type.value}#{node.node_id}")
            context = self._context_service.get_context(node)
            log.debug(f"   Контекст: {context}")
            
            # 5. Эмитим событие для UI
            log.debug(f"📢 Эмитим NodeDetailsLoaded для {node.node_type.value}#{node.node_id}")
            self._bus.emit(NodeDetailsLoaded(
                node=node,
                payload=details,
                context=context
            ))
            
            log.success(f"✅ Детали для {node.node_type.value}#{node.node_id} обработаны")
            
        except Exception as e:
            log.error(f"❌ Ошибка загрузки деталей: {e}")
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
        log.info(f"📂 Node expanded: {node.node_type.value}#{node.node_id}")
        
        # 1. Сохраняем состояние
        was_expanded = node in self._expanded_nodes
        self._expanded_nodes.add(node)
        log.debug(f"   Раскрытых узлов: {len(self._expanded_nodes)}")
        
        # 2. Эмитим изменение списка раскрытых
        if not was_expanded:
            log.debug("📢 Эмитим ExpandedNodesChanged")
            self._bus.emit(ExpandedNodesChanged(
                expanded_nodes=self._expanded_nodes.copy()
            ))
        
        # 3. Определяем тип детей
        child_type = self._get_child_type(node.node_type)
        if not child_type:
            log.debug(f"   Узел {node.node_type.value}#{node.node_id} не может иметь детей")
            return
        
        log.debug(f"   Тип детей: {child_type.value}")
        
        # 4. Загружаем детей
        try:
            log.debug(f"🚀 Загрузка детей для {node.node_type.value}#{node.node_id}")
            children = self._loader.load_children(
                node.node_type,
                node.node_id,
                child_type
            )
            
            log.data(f"📦 Загружено {len(children)} детей типа {child_type.value}")
            if children and len(children) <= 5:
                for i, child in enumerate(children):
                    log.debug(f"   [{i}] {type(child).__name__}#{getattr(child, 'id', '?')}")
            
            # 5. Эмитим событие для UI
            log.debug(f"📢 Эмитим ChildrenLoaded для {node.node_type.value}#{node.node_id}")
            self._bus.emit(ChildrenLoaded(
                parent=node,
                children=children
            ))
            
            log.success(f"✅ Загружено {len(children)} детей для {node.node_type.value}#{node.node_id}")
            
        except Exception as e:
            log.error(f"❌ Ошибка загрузки детей: {e}")
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
        log.info(f"📁 Node collapsed: {node.node_type.value}#{node.node_id}")
        
        # 1. Обновляем состояние
        was_expanded = node in self._expanded_nodes
        self._expanded_nodes.discard(node)
        log.debug(f"   Раскрытых узлов: {len(self._expanded_nodes)}")
        
        # 2. Эмитим изменение
        if was_expanded:
            log.debug("📢 Эмитим ExpandedNodesChanged")
            self._bus.emit(ExpandedNodesChanged(
                expanded_nodes=self._expanded_nodes.copy()
            ))
    
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
        result = mapping.get(parent_type)
        log.debug(f"🔍 get_child_type({parent_type.value}) -> {result.value if result else 'None'}")
        return result
    
    # ===== Публичные методы =====
    
    def get_current_selection(self) -> Optional[NodeIdentifier]:
        """
        Возвращает текущий выбранный узел.
        
        Returns:
            Optional[NodeIdentifier]: Выбранный узел или None
        """
        log.debug(f"🔍 get_current_selection -> {self._current_selection.node_type.value if self._current_selection else 'None'}#{self._current_selection.node_id if self._current_selection else '?'}")
        return self._current_selection
    
    def get_expanded_nodes(self) -> Set[NodeIdentifier]:
        """
        Возвращает копию списка раскрытых узлов.
        
        Returns:
            Set[NodeIdentifier]: Раскрытые узлы
        """
        log.debug(f"🔍 get_expanded_nodes -> {len(self._expanded_nodes)} узлов")
        return self._expanded_nodes.copy()
    
    def is_expanded(self, node: NodeIdentifier) -> bool:
        """
        Проверяет, раскрыт ли узел.
        
        Args:
            node: Идентификатор узла
            
        Returns:
            bool: True если раскрыт
        """
        result = node in self._expanded_nodes
        log.debug(f"🔍 is_expanded({node.node_type.value}#{node.node_id}) -> {result}")
        return result