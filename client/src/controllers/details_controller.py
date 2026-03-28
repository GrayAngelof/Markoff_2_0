# client/src/controllers/details_controller.py
"""
DetailsController — управление панелью детальной информации.

Ответственность:
- Координация отображения панели деталей при выборе узла
- Эмиссия события ShowDetailsPanel для переключения заглушки → панель
- Загрузка данных через DataLoader
- Отправка данных в DetailsPanel через события

Поток данных:
1. Пользователь выбирает узел в дереве
2. TreeView эмитит NodeSelected
3. DetailsController получает NodeSelected
4. Эмитит ShowDetailsPanel (AppWindow → CentralWidget переключает видимость)
5. Загружает данные через DataLoader
6. Отправляет View Models в DetailsPanel через события
"""

# ===== ИМПОРТЫ =====
from typing import Any, Optional

from src.core import EventBus
from src.core.events import NodeDetailsLoaded, NodeSelected, ShowDetailsPanel
from src.core.types import Event
from src.core.types.nodes import NodeIdentifier, NodeType
from src.controllers.base import BaseController
from src.services.data_loader import DataLoader
from src.ui.details.panel import DetailsPanel
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsController(BaseController):
    """
    Контроллер панели деталей.

    Управляет показом панели деталей, загрузкой данных
    и отправкой данных в DetailsPanel.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, loader: DataLoader) -> None:
        """Инициализирует контроллер панели деталей."""
        log.info("Инициализация DetailsController")
        super().__init__(bus)
        log.system(f"EventBus инициализирован: id={id(self._bus)}, debug={self._bus._debug}")

        self._loader = loader
        self._details_panel: Optional[DetailsPanel] = None
        self._current_node: Optional[NodeIdentifier] = None

        self._subscribe(NodeSelected, self._on_node_selected)

        log.success("DetailsController инициализирован")

    def cleanup(self) -> None:
        """Очищает ресурсы перед завершением."""
        self._details_panel = None
        self._current_node = None
        super().cleanup()
        log.debug("DetailsController: ресурсы очищены")

    # ---- ПУБЛИЧНОЕ API ----
    def set_details_panel(self, panel: DetailsPanel) -> None:
        """Устанавливает DetailsPanel для управления."""
        self._details_panel = panel
        log.link("DetailsController: DetailsPanel установлен")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_node_selected(self, event: Event[NodeSelected]) -> None:
        """
        Обрабатывает выбор узла в дереве.

        Эмитит ShowDetailsPanel и инициирует загрузку данных узла.
        """
        node = event.data.node
        self._current_node = node

        log.info(f"DetailsController: выбран узел {node.node_type.value}#{node.node_id}")

        self._bus.emit(ShowDetailsPanel())
        self._load_node_details(node)

    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _load_node_details(self, node: NodeIdentifier) -> None:
        """
        Загружает детальную информацию о узле.

        При успехе — отправляет данные в DetailsPanel.
        При ошибке — показывает сообщение об ошибке.
        """
        log.info(f"DetailsController: загрузка деталей для {node.node_type.value}#{node.node_id}")

        try:
            details = self._loader.load_details(node.node_type, node.node_id)

            if details is None:
                log.warning(f"DetailsController: данные для {node.node_type.value}#{node.node_id} не найдены")
                self._show_error(node, "Данные не найдены")
                return

            log.success(f"DetailsController: данные загружены для {node.node_type.value}#{node.node_id}")
            log.debug(f"DetailsController: тип данных = {type(details).__name__}")

            self._send_details_to_panel(node, details)

        except Exception as e:
            log.error(f"DetailsController: ошибка загрузки {node.node_type.value}#{node.node_id}: {e}")
            self._show_error(node, str(e))

    def _send_details_to_panel(self, node: NodeIdentifier, details: Any) -> None:
        """Отправляет данные в DetailsPanel через событие NodeDetailsLoaded."""
        self._bus.emit(NodeDetailsLoaded(
            node=node,
            payload=details,
            context={},
        ))
        log.debug(f"DetailsController: NodeDetailsLoaded отправлен для {node.node_type.value}#{node.node_id}")

    def _show_error(self, node: NodeIdentifier, error_message: str) -> None:
        """Показывает ошибку в DetailsPanel."""
        # TODO: Создать событие ShowError и обработать в DetailsPanel
        log.error(f"DetailsController: ошибка для {node.node_type.value}#{node.node_id}: {error_message}")