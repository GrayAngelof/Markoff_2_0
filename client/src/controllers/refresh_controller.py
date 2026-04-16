# client/src/controllers/refresh_controller.py
"""
RefreshController — управление обновлением данных.

Поддерживает три режима:
- current: обновить текущий узел
- visible: обновить все раскрытые узлы
- full: полная перезагрузка (очистка кэша + сворачивание дерева)

Состояние (выбранный узел, раскрытые узлы) получает через события от TreeController.
"""

# ===== ИМПОРТЫ =====
from typing import Optional, Set

from src.core import EventBus
from src.core.events.definitions import (
    CollapseAllRequested,
    CurrentSelectionChanged,
    ExpandedNodesChanged,
    RefreshRequested,
)
from src.core.types import NodeIdentifier
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

        self._loader = loader

        # Состояние (обновляется через события)
        self._current_selection: Optional[NodeIdentifier] = None
        self._expanded_nodes: Set[NodeIdentifier] = set()

        # Подписки
        self._subscribe(RefreshRequested, self._on_refresh_requested)
        self._subscribe(CurrentSelectionChanged, self._on_selection_changed)
        self._subscribe(ExpandedNodesChanged, self._on_expanded_nodes_changed)

        log.success("RefreshController создан")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ СОСТОЯНИЯ ----
    def _on_selection_changed(self, event: CurrentSelectionChanged) -> None:
        """Обновляет текущий выбранный узел."""
        self._current_selection = event.selection
        if event.selection:
            log.debug(f"Текущий выбор: {event.selection.node_type.value}#{event.selection.node_id}")
        else:
            log.debug("Текущий выбор: None")

    def _on_expanded_nodes_changed(self, event: ExpandedNodesChanged) -> None:
        """Обновляет список раскрытых узлов."""
        self._expanded_nodes = event.expanded_nodes.copy()
        log.debug(f"Раскрыто узлов: {len(self._expanded_nodes)}")

    # ---- ОБРАБОТЧИКИ ЗАПРОСОВ ОБНОВЛЕНИЯ ----
    def _on_refresh_requested(self, refresh_data: RefreshRequested) -> None:
        """
        Обрабатывает запрос на обновление.

        Поддерживает режимы: 'current', 'visible', 'full'.
        """
        mode = refresh_data.mode

        log.info(f"Запрос обновления: режим {mode}")

        try:
            if mode == "current":
                self._handle_current_refresh()
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
    def _handle_current_refresh(self) -> None:
        """Обновляет текущий выбранный узел."""
        if not self._current_selection:
            log.warning("Нет текущего выбранного узла для обновления")
            return

        node = self._current_selection
        node_display = f"{node.node_type.value}#{node.node_id}"
        log.info(f"Обновление узла: {node_display}")

        self._loader.reload_node(node.node_type, node.node_id)

        log.info(f"Узел {node_display} обновлён")

    def _handle_visible_refresh(self) -> None:
        """Обновляет все раскрытые узлы."""
        if not self._expanded_nodes:
            log.warning("Нет раскрытых узлов для обновления")
            return

        count = len(self._expanded_nodes)
        log.info(f"Обновление {count} раскрытых узлов")

        for node in self._expanded_nodes:
            self._loader.reload_node(node.node_type, node.node_id)

        log.info(f"Обновлено {count} раскрытых узлов")

    def _handle_full_refresh(self) -> None:
        """Выполняет полную перезагрузку всех данных."""
        log.info("Полное обновление всех данных")

        # 1. Очищаем кэш
        self._loader.clear_cache()
        log.cache("Кэш очищен")

        # 2. Эмитим запрос на сворачивание всех узлов
        self._bus.emit(CollapseAllRequested())
        log.info("Отправлен запрос на сворачивание всех узлов")

        # 3. Загружаем комплексы заново
        complexes = self._loader.load_complexes()

        log.info(f"Полное обновление завершено: загружено {len(complexes)} комплексов")