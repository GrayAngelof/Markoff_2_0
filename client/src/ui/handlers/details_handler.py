# client/src/ui/handlers/details_handler.py
"""
Обработчик событий панели деталей (UI слой).

Подписывается на NodeDetailsLoaded и обновляет DetailsPanel.
"""

# ===== ИМПОРТЫ =====
from src.core import EventBus
from src.core.events.definitions import NodeDetailsLoaded, ShowDetailsPanel
from src.ui.details.panel import DetailsPanel
from src.view_models.details import DetailsViewModel
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class DetailsUiHandler:
    """
    Обработчик событий панели деталей.

    Отвечает за:
    - Подписку на NodeDetailsLoaded
    - Обновление DetailsPanel (шапка, сетка)
    - Эмиссию ShowDetailsPanel для переключения с заглушки на панель
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, panel: DetailsPanel) -> None:
        """Инициализирует обработчик."""
        log.system("DetailsUiHandler инициализация")
        self._bus = bus
        self._panel = panel
        self._subscriptions = []
        log.system("DetailsUiHandler инициализирован")

    def start(self) -> None:
        """Подписывается на события."""
        log.info("Запуск DetailsUiHandler")
        sub = self._bus.subscribe(NodeDetailsLoaded, self._on_details_loaded)
        self._subscriptions.append(sub)
        log.success("DetailsUiHandler запущен")

    def cleanup(self) -> None:
        """Отписывается от событий."""
        log.info("Очистка DetailsUiHandler")
        for sub in self._subscriptions:
            sub()
        self._subscriptions.clear()
        log.success("DetailsUiHandler очищен")

    # ---- ОБРАБОТЧИКИ СОБЫТИЙ ----
    def _on_details_loaded(self, event: NodeDetailsLoaded) -> None:
        """Обновляет панель деталей при получении ViewModel."""
        node = event.node
        vm = event.view_model

        log.info(f"Детали загружены для {node.node_type.value}#{node.node_id}")

        if not isinstance(vm, DetailsViewModel):
            log.error(f"Ожидался DetailsViewModel, получен {type(vm).__name__}")
            return

        self._panel.update_content(vm, node)
        self._bus.emit(ShowDetailsPanel())