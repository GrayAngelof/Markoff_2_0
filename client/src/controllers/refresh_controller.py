# client/src/controllers/refresh_controller.py
"""
RefreshController — управление обновлением данных.

Без состояния — получает всё через события.
"""

from typing import Optional, Set
from src.core import EventBus
from src.core.types import Event, NodeIdentifier
from src.core.events import (
    RefreshRequested, CurrentSelectionChanged, ExpandedNodesChanged,
    NodeReloaded, VisibleNodesReloaded, FullReloadCompleted
)
from src.services import DataLoader
from src.controllers.base import BaseController
from utils.logger import get_logger

log = get_logger(__name__)


class RefreshController(BaseController):
    """
    Контроллер обновления данных.
    
    НЕ хранит состояние — получает его через события:
    - CurrentSelectionChanged — текущий выбранный узел
    - ExpandedNodesChanged — список раскрытых узлов
    
    Поддерживает три режима:
    - current: обновить текущий узел
    - visible: обновить все раскрытые узлы
    - full: полная перезагрузка
    """
    
    def __init__(
        self,
        bus: EventBus,
        loader: DataLoader
    ):
        """
        Инициализирует контроллер обновления.
        
        Args:
            bus: Шина событий
            loader: Загрузчик данных
        """
        super().__init__(bus)
        self._loader = loader
        
        # Состояние получаем из событий
        self._current_selection: Optional[NodeIdentifier] = None
        self._expanded_nodes: Set[NodeIdentifier] = set()
        
        # Сохраняем bound methods как атрибуты (сильные ссылки)
        self._bound_on_refresh_requested = self._on_refresh_requested
        self._bound_on_selection_changed = self._on_selection_changed
        self._bound_on_expanded_changed = self._on_expanded_changed
        
        # Подписки (LINK категория)
        log.link("Подписка на RefreshRequested, CurrentSelectionChanged, ExpandedNodesChanged")
        self._subscribe(RefreshRequested, self._bound_on_refresh_requested)
        self._subscribe(CurrentSelectionChanged, self._bound_on_selection_changed)
        self._subscribe(ExpandedNodesChanged, self._bound_on_expanded_changed)
        
        log.system("RefreshController инициализирован")
    
    def _on_selection_changed(self, event: Event[CurrentSelectionChanged]) -> None:
        """
        Обновляет текущий выбранный узел.
        
        Args:
            event: Событие изменения выбора
        """
        self._current_selection = event.data.selection
        if self._current_selection:
            log.debug(f"Текущий выбор: {self._current_selection.node_type.value}#{self._current_selection.node_id}")
        else:
            log.debug("Текущий выбор: None")
    
    def _on_expanded_changed(self, event: Event[ExpandedNodesChanged]) -> None:
        """
        Обновляет список раскрытых узлов.
        
        Args:
            event: Событие изменения списка раскрытых
        """
        self._expanded_nodes = event.data.expanded_nodes
        log.debug(f"Раскрыто узлов: {len(self._expanded_nodes)}")
    
    def _on_refresh_requested(self, event: Event[RefreshRequested]) -> None:
        """
        Обрабатывает запрос на обновление.
        
        Args:
            event: Событие запроса обновления
        """
        mode = event.data.mode
        node = event.data.node
        
        log.info(f"Запрос обновления: режим {mode}")
        if node:
            log.debug(f"Целевой узел: {node.node_type.value}#{node.node_id}")
        
        try:
            if mode == "current":
                self._handle_current_refresh(node)
            elif mode == "visible":
                self._handle_visible_refresh()
            elif mode == "full":
                self._handle_full_refresh()
            else:
                log.warning(f"Неизвестный режим обновления: {mode}")
                
        except Exception as e:
            log.error(f"Ошибка при обновлении: {e}")
            if node:
                self._emit_error(node, e)
            elif self._current_selection:
                self._emit_error(self._current_selection, e)
    
    def _handle_current_refresh(self, node: Optional[NodeIdentifier]) -> None:
        """
        Обновляет текущий выбранный узел.
        
        Args:
            node: Узел для обновления (из события или из состояния)
        """
        target = node or self._current_selection
        
        if not target:
            log.warning("Нет текущего выбранного узла для обновления")
            return
        
        node_display = f"{target.node_type.value}#{target.node_id}"
        log.info(f"Обновление узла: {node_display}")
        
        # Инвалидируем и перезагружаем
        self._loader.reload_node(target.node_type, target.node_id)
        
        # Эмитим событие об успешном обновлении
        self._bus.emit(NodeReloaded(node=target))
        log.info(f"Узел {node_display} обновлен")
    
    def _handle_visible_refresh(self) -> None:
        """Обновляет все раскрытые узлы."""
        if not self._expanded_nodes:
            log.warning("Нет раскрытых узлов для обновления")
            return
        
        count = len(self._expanded_nodes)
        log.info(f"Обновление {count} раскрытых узлов")
        
        if log.is_debug_enabled():
            for node in self._expanded_nodes:
                log.debug(f"  → {node.node_type.value}#{node.node_id}")
        
        for node in self._expanded_nodes:
            self._loader.reload_branch(node.node_type, node.node_id)
        
        self._bus.emit(VisibleNodesReloaded(count=count))
        log.info(f"Обновлено {count} раскрытых узлов")
    
    def _handle_full_refresh(self) -> None:
        """Выполняет полную перезагрузку всех данных."""
        log.info("Полное обновление всех данных")
        
        # Очищаем кэш
        self._loader.clear_cache()
        log.cache("Кэш очищен")
        
        # Загружаем комплексы
        complexes = self._loader.load_complexes()
        
        # Эмитим событие о завершении
        self._bus.emit(FullReloadCompleted(count=len(complexes)))
        
        log.info(f"Полное обновление завершено: загружено {len(complexes)} комплексов")
    
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