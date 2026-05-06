# client/src/ui/handlers/details_handler.py
"""
Обработчик событий панели деталей (UI слой).

Подписывается на NodeDetailsLoaded и обновляет DetailsPanel.
"""

# ===== ИМПОРТЫ =====
from src.core.event_bus import EventBus
from src.core.events.definitions import NodeDetailsLoaded, ShowDetailsPanel
from src.ui.details.panel import DetailsPanel
from src.view_models.details import DetailsViewModel, HeaderViewModel, InfoGridItem
from utils.logger import get_logger


log = get_logger(__name__)


class DetailsUiHandler:
    """
    Обработчик событий панели деталей.
    """

    def __init__(self, bus: EventBus, panel: DetailsPanel) -> None:
        log.system("DetailsUiHandler инициализация")
        self._bus = bus
        self._panel = panel
        self._subscriptions = []
        log.system("DetailsUiHandler инициализирован")

    def start(self) -> None:
        log.info("Запуск DetailsUiHandler")
        sub = self._bus.subscribe(NodeDetailsLoaded, self._on_details_loaded)
        self._subscriptions.append(sub)
        log.success("DetailsUiHandler запущен")

    def cleanup(self) -> None:
        log.info("Очистка DetailsUiHandler")
        for sub in self._subscriptions:
            sub()
        self._subscriptions.clear()
        log.success("DetailsUiHandler очищен")

    def _on_details_loaded(self, event: NodeDetailsLoaded) -> None:
        """Обновляет панель деталей, преобразуя IDetailsViewModel в DetailsViewModel."""
        node = event.node
        proto = event.view_model  # IDetailsViewModel

        log.info(f"Детали загружены для {node.node_type.value}#{node.node_id}")

        # Преобразуем протокол в DetailsViewModel
        header = HeaderViewModel(
            title=proto.header_title,
            subtitle=proto.header_subtitle,
            status_name=proto.header_status_name,
        )
        grid = [InfoGridItem(label, value) for label, value in proto.grid_items]
        vm = DetailsViewModel(header=header, grid=grid)

        self._panel.update_content(vm, node)
        self._bus.emit(ShowDetailsPanel())