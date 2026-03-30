# client/src/controllers/refresh_controller.py
"""
RefreshController — управление обновлением данных.

Поддерживает три режима:
- current: обновить текущий узел
- visible: обновить все раскрытые узлы
- full: полная перезагрузка

Состояние (выбранный узел, раскрытые узлы) получает через сеттеры от TreeController.
"""

# ===== ИМПОРТЫ =====
from typing import Optional, Set

from src.core import EventBus
from src.core.events.definitions import DataError, DataInvalidated, DataLoaded, RefreshRequested
from src.core.types import NodeIdentifier  # Убран Event
from src.controllers.base import BaseController
from src.services import DataLoader
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class RefreshController(BaseController):
    """Контроллер обновления данных."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, loader: DataLoader) -> None:
        """Инициализирует контроллер обновления."""
        super().__init__(bus)
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

        self._loader = loader

        # Состояние (устанавливается извне через сеттеры)
        self._current_selection: Optional[NodeIdentifier] = None
        self._expanded_nodes: Set[NodeIdentifier] = set()

        self._subscribe(RefreshRequested, self._on_refresh_requested)

        log.success("RefreshController создан")

    # ---- ПУБЛИЧНОЕ API ----
    def set_current_selection(self, selection: Optional[NodeIdentifier]) -> None:
        """Устанавливает текущий выбранный узел."""
        self._current_selection = selection
        if selection:
            log.debug(f"Текущий выбор: {selection.node_type.value}#{selection.node_id}")
        else:
            log.debug("Текущий выбор: None")

    def set_expanded_nodes(self, expanded_nodes: Set[NodeIdentifier]) -> None:
        """Устанавливает список раскрытых узлов."""
        self._expanded_nodes = expanded_nodes
        log.debug(f"Раскрыто узлов: {len(self._expanded_nodes)}")

    def get_current_selection(self) -> Optional[NodeIdentifier]:
        """Возвращает текущий выбранный узел."""
        return self._current_selection

    def get_expanded_nodes(self) -> Set[NodeIdentifier]:
        """Возвращает копию списка раскрытых узлов."""
        return self._expanded_nodes.copy()

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_refresh_requested(self, refresh_data: RefreshRequested) -> None:  # Изменено: принимает RefreshRequested
        """
        Обрабатывает запрос на обновление.

        Поддерживает режимы: 'current', 'visible', 'full'.
        """
        mode = refresh_data.mode  # Прямой доступ к атрибутам
        node = refresh_data.node

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
            self._emit_error(None, e, {'mode': mode})

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _handle_current_refresh(self, node: Optional[NodeIdentifier]) -> None:
        """Обновляет текущий выбранный узел."""
        target = node or self._current_selection

        if not target:
            log.warning("Нет текущего выбранного узла для обновления")
            return

        node_display = f"{target.node_type.value}#{target.node_id}"
        log.info(f"Обновление узла: {node_display}")

        self._loader.reload_node(target.node_type, target.node_id)

        log.info(f"Узел {node_display} обновлён")

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

        log.info(f"Обновлено {count} раскрытых узлов")

    def _handle_full_refresh(self) -> None:
        """Выполняет полную перезагрузку всех данных."""
        log.info("Полное обновление всех данных")

        self._loader.clear_cache()
        log.cache("Кэш очищен")

        complexes = self._loader.load_complexes()

        log.info(f"Полное обновление завершено: загружено {len(complexes)} комплексов")