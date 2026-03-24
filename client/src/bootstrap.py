"""
Инициализация всех компонентов приложения.
Собирает вместе Core, Models, Data, Services, Controllers и передает в UI.
"""
from typing import Optional

from PySide6.QtWidgets import QApplication

from src.core import EventBus
from src.core.events import NodeSelected, NodeExpanded, NodeCollapsed, RefreshRequested

from src.data import EntityGraph
from src.data import (
    ComplexRepository,
    BuildingRepository,
    FloorRepository,
    RoomRepository,
    CounterpartyRepository,
    ResponsiblePersonRepository,
)

from src.services import ApiClient, DataLoader, ConnectionService, ContextService

from src.controllers import (
    TreeController,
    DetailsController,
    RefreshController,
    ConnectionController,
)

from src.ui.main_window import MainWindow

from utils.logger import get_logger

log = get_logger(__name__)


class ApplicationBootstrap:
    """
    Загрузчик всех компонентов приложения.
    
    Отвечает за:
    - Создание экземпляров всех слоев
    - Настройку зависимостей (DI)
    - Передачу зависимостей в UI
    """
    
    def __init__(self, app: QApplication):
        """
        Инициализирует все компоненты приложения.
        
        Args:
            app: Экземпляр QApplication
        """
        log.info("=" * 60)
        log.info("🚀 Запуск инициализации компонентов")
        log.info("=" * 60)
        
        self._app = app
        
        # Инициализация слоев по порядку
        self._init_core()
        self._init_data()
        self._init_services()
        self._init_controllers()
        self._init_ui()
        
        log.success("✅ Все компоненты инициализированы")
        log.info("=" * 60)
    
    # ===== Инициализация слоев =====
    
    def _init_core(self) -> None:
        """Инициализация ядра."""
        log.info("📡 Инициализация Core...")
        
        self._bus = EventBus()
        self._bus.set_debug(True)  # Включаем отладку для разработки
        
        log.success("  ✅ EventBus создан")
    
    def _init_data(self) -> None:
        """Инициализация слоя данных."""
        log.info("💾 Инициализация Data слоя...")
        
        # Граф сущностей
        self._graph = EntityGraph(self._bus)
        
        # Репозитории
        self._complex_repo = ComplexRepository(self._graph)
        self._building_repo = BuildingRepository(self._graph)
        self._floor_repo = FloorRepository(self._graph)
        self._room_repo = RoomRepository(self._graph)
        self._counterparty_repo = CounterpartyRepository(self._graph)
        self._responsible_person_repo = ResponsiblePersonRepository(self._graph)
        
        log.success("  ✅ EntityGraph и репозитории созданы")
        log.debug(f"    • ComplexRepository: {self._complex_repo}")
        log.debug(f"    • BuildingRepository: {self._building_repo}")
        log.debug(f"    • FloorRepository: {self._floor_repo}")
        log.debug(f"    • RoomRepository: {self._room_repo}")
        log.debug(f"    • CounterpartyRepository: {self._counterparty_repo}")
        log.debug(f"    • ResponsiblePersonRepository: {self._responsible_person_repo}")
    
    def _init_services(self) -> None:
        """Инициализация сервисного слоя."""
        log.info("🔧 Инициализация Services...")
        
        # API клиент
        self._api = ApiClient()
        log.debug(f"  • ApiClient: {self._api}")
        
        # DataLoader
        self._loader = DataLoader(self._bus, self._api, self._graph)
        log.debug(f"  • DataLoader: {self._loader}")
        
        # ContextService
        self._context_service = ContextService(
            self._complex_repo,
            self._building_repo,
            self._floor_repo,
            self._room_repo,
            self._counterparty_repo,
            self._responsible_person_repo
        )
        log.debug(f"  • ContextService: {self._context_service}")
        
        # ConnectionService
        self._connection_service = ConnectionService(self._bus, self._api)
        log.debug(f"  • ConnectionService: {self._connection_service}")
        
        log.success("  ✅ Services инициализированы")
    
    def _init_controllers(self) -> None:
        """Инициализация контроллеров."""
        log.info("🎮 Инициализация Controllers...")
        
        # TreeController
        self._tree_controller = TreeController(
            self._bus,
            self._loader,
            self._context_service
        )
        log.debug(f"  • TreeController: {self._tree_controller}")
        
        # DetailsController
        self._details_controller = DetailsController(
            self._bus,
            self._loader
        )
        log.debug(f"  • DetailsController: {self._details_controller}")
        
        # RefreshController
        self._refresh_controller = RefreshController(
            self._bus,
            self._loader
        )
        log.debug(f"  • RefreshController: {self._refresh_controller}")
        
        # ConnectionController
        self._connection_controller = ConnectionController(self._bus)
        log.debug(f"  • ConnectionController: {self._connection_controller}")
        
        log.success("  ✅ Controllers инициализированы")
    
    def _init_ui(self) -> None:
        """Инициализация UI."""
        log.info("🖥️ Инициализация UI...")
        
        # Создаем главное окно
        self._window = MainWindow()
        
        # TODO: Передаем зависимости в UI (после того как UI будет готов)
        # self._window.set_event_bus(self._bus)
        # self._window.set_tree_controller(self._tree_controller)
        # self._window.set_details_controller(self._details_controller)
        
        log.success("  ✅ MainWindow создана")
    
    # ===== Публичные методы =====
    
    def get_window(self) -> MainWindow:
        """Возвращает главное окно."""
        return self._window
    
    def get_bus(self) -> EventBus:
        """Возвращает шину событий (для отладки)."""
        return self._bus
    
    def cleanup(self) -> None:
        """Очистка ресурсов перед завершением."""
        log.info("🧹 Очистка ресурсов...")
        
        # Останавливаем сервисы
        self._connection_service.stop()
        
        # Очищаем контроллеры
        self._tree_controller.cleanup()
        self._details_controller.cleanup()
        self._refresh_controller.cleanup()
        self._connection_controller.cleanup()
        
        # Очищаем граф
        self._graph.clear()
        
        log.success("  ✅ Ресурсы очищены")